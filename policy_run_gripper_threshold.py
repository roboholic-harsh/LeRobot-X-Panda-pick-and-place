#!/usr/bin/env python3
import sys
import os
import json
import torch
import numpy as np
import cv2
from dataclasses import dataclass

# --- BRIDGE: Allow Conda to see ROS 2 ---
if "/opt/ros/humble/lib/python3.10/site-packages" not in sys.path:
    sys.path.append("/opt/ros/humble/lib/python3.10/site-packages")

import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

# --- LEROBOT IMPORTS ---
from lerobot.policies.act.modeling_act import ACTPolicy, ACTConfig
from lerobot.configs.types import FeatureType
from safetensors.torch import load_file

@dataclass
class DummyFeature:
    type: str
    shape: list

class LeRobotGazeboPilot(Node):
    def __init__(self, policy_path, dataset_stats_path):
        super().__init__('lerobot_pilot')
        
        self.device ="cpu"
        self.policy_path = policy_path
        self.stats_path = dataset_stats_path
        
        # --- JOINT ORDER (MATCHING YOUR DATASET) ---
        # Based on your ROS logs, your data was recorded in this scrambled order.
        self.scrambled_joint_names = [
            'panda_joint1', 'panda_joint2','panda_joint4', 
            'panda_joint5', 'panda_joint6', 'panda_joint7', 'panda_joint3', 
            'panda_finger_joint1', 'panda_finger_joint2'
        ]
        
        # --- LOAD STATS FOR UN-NORMALIZATION ---
        self.get_logger().info(f"📊 Loading stats from {self.stats_path}...")
        with open(self.stats_path, 'r') as f:
            stats = json.load(f)
            # Extract Action Mean and Std
            # Structure in stats.json is usually: "action": { "mean": [...], "std": [...] }
            # We convert them to torch tensors for fast math
            self.action_mean = torch.tensor(stats["action"]["mean"], device=self.device).squeeze()
            self.action_std = torch.tensor(stats["action"]["std"], device=self.device).squeeze()
            
        self.get_logger().info(f"✅ Stats Loaded. Mean: {self.action_mean[:2]}...")

        # --- LOAD POLICY ---
        self.get_logger().info(f"🧠 Loading Policy...")
        config_path = os.path.join(self.policy_path, "config.json")
        with open(config_path, "r") as f:
            config_dict = json.load(f)

        clean_config = self.hydrate_config(config_dict)
        cfg = ACTConfig(**clean_config)
        self.policy = ACTPolicy(cfg)
        
        model_file = os.path.join(self.policy_path, "model.safetensors")
        state_dict = load_file(model_file)
        self.policy.load_state_dict(state_dict)
        self.policy.to(self.device)
        self.policy.eval()
        self.get_logger().info("✅ Policy Ready!")

        # --- ROS SETUP ---
        self.bridge = CvBridge()
        self.arm_pub = self.create_publisher(JointTrajectory, '/panda_arm_controller/joint_trajectory', 10)
        self.gripper_pub = self.create_publisher(JointTrajectory, '/hand_controller/joint_trajectory', 10)
        
        self.create_subscription(Image, '/camera/overhead_camera/image_raw', self.world_cam_cb, 10)
        self.create_subscription(Image, '/camera/hand_camera/image_raw', self.gripper_cam_cb, 10)
        self.create_subscription(JointState, '/joint_states', self.joint_cb, 10)
        
        self.latest_world_img = None
        self.latest_gripper_img = None
        self.latest_joints = None
        
        self.timer = self.create_timer(0.1, self.control_step)

    def hydrate_config(self, config_dict):
        # (Standard hydration logic - Same as before)
        valid_args = {
            "n_obs_steps", "chunk_size", "n_action_steps", "normalization_mapping", 
            "vision_backbone", "pretrained_backbone_weights", "replace_final_stride_with_dilation",
            "pre_norm", "dim_model", "n_heads", "dim_feedforward", "feedforward_activation", 
            "n_encoder_layers", "n_decoder_layers", "use_vae", "latent_dim", "n_vae_encoder_layers", 
            "temporal_ensemble_coeff", "dropout", "kl_weight", "optimizer_lr", 
            "optimizer_weight_decay", "optimizer_lr_backbone", "input_features", "output_features"
        }
        new_config = {}
        for k, v in config_dict.items():
            if k not in valid_args: continue
            if k in ["input_features", "output_features"]:
                converted_features = {}
                for feature_name, feature_data in v.items():
                    str_type = feature_data["type"]
                    enum_type = FeatureType.VISUAL if str_type == "VISUAL" else \
                                FeatureType.STATE if str_type == "STATE" else \
                                FeatureType.ACTION if str_type == "ACTION" else str_type
                    converted_features[feature_name] = DummyFeature(type=enum_type, shape=feature_data["shape"])
                new_config[k] = converted_features
            else: new_config[k] = v
        return new_config

    def world_cam_cb(self, msg):
        try: self.latest_world_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except: pass

    def gripper_cam_cb(self, msg):
        try: self.latest_gripper_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except: pass

    def joint_cb(self, msg):
        name_to_pos = {n: p for n, p in zip(msg.name, msg.position)}
        ordered_pos = []
        try:
            # Sort input to match Training Order (Scrambled)
            for n in self.scrambled_joint_names:
                ordered_pos.append(name_to_pos.get(n, 0.0))
            self.latest_joints = np.array(ordered_pos, dtype=np.float32)
        except Exception:
            pass

    def control_step(self):
        if self.latest_world_img is None or self.latest_gripper_img is None or self.latest_joints is None:
            return

        # 1. Prepare Images (BGR -> RGB)
        def prep_image(img):
            img = cv2.resize(img, (640, 480))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # RGB Fix
            img = torch.from_numpy(img).float() / 255.0
            img = img.permute(2, 0, 1).unsqueeze(0)
            return img.to(self.device)

        # 2. Prepare State (Normalize Inputs manually if needed, but usually Policy handles inputs OK)
        # Note: Ideally we should normalize inputs too: (state - mean) / std.
        # But let's try raw first, as robust policies sometimes handle raw inputs better than raw outputs.
        # If robot fails to move correctly, we will add input normalization here.
        state = torch.from_numpy(self.latest_joints).float().unsqueeze(0).to(self.device)
        
        batch = {
            "observation.images.world": prep_image(self.latest_world_img),
            "observation.images.gripper": prep_image(self.latest_gripper_img),
            "observation.state": state
        }

        # 3. Inference
        with torch.no_grad():
            actions = self.policy.select_action(batch)
            
            # 4. CRITICAL: Un-Normalize Output
            # Action = (Predicted_Z_Score * Std) + Mean
            # This converts "0.64" back to "0.03" meters
            actions = (actions * self.action_std) + self.action_mean
            
            if actions.ndim == 2:
                 next_action = actions[0].cpu().numpy()
            elif actions.ndim == 3:
                 next_action = actions[0, 0].cpu().numpy()
            else: return

        # 5. Split (First 7=Arm, Last 2=Gripper)
        arm_cmd = next_action[:7]
        gripper_cmd = next_action[7:]

        # 6. Publish with Duration (Smooth Jitter)
        now = self.get_clock().now().to_msg()
        
        # Arm (Scrambled Order)
        arm_msg = JointTrajectory()
        # arm_msg.header.stamp = now
        # We use the scrambled names because 'arm_cmd' is in scrambled order!
        arm_msg.joint_names = self.scrambled_joint_names[:7] 
        p_arm = JointTrajectoryPoint()
        p_arm.positions = arm_cmd.tolist()
        # p_arm.time_from_start.sec = 0
        # p_arm.time_from_start.nanosec = 200000000 # 0.2s smoothing
        arm_msg.points = [p_arm]
        self.arm_pub.publish(arm_msg)

        # Gripper
        grip_msg = JointTrajectory()
        # grip_msg.header.stamp = now3
        grip_msg.joint_names = self.scrambled_joint_names[7:]
        p_grip = JointTrajectoryPoint()
        p_grip.positions = gripper_cmd.tolist()

        if p_grip.positions[1] > 0.032 and p_grip.positions[0] > 0.032:
            p_grip.positions[1] = 0.04
            p_grip.positions[0] = 0.04
        else:
            p_grip.positions[1] = 0.0
            p_grip.positions[0] = 0.0

        # p_grip.time_from_start.sec = 0
        # p_grip.time_from_start.nanosec = 500000000 # 0.5s smoothing
        grip_msg.points = [p_grip]
        self.gripper_pub.publish(grip_msg)
        
        print(f"Gripper (Physical): {gripper_cmd},  thr: {p_grip.positions}")

def main(args=None):
    rclpy.init(args=args)
    
    ##############################################################################################################################
    ##############################################################################################################################
    # 1. Path to your Model
    policy_path = os.path.expanduser("checkpoints_single_pose/020000/pretrained_model")
    # policy_path = os.path.expanduser("/home/roboholic_harsh/lerobot/runs/checkpoints_150_ep/075000/pretrained_model")
    
    # 2. Path to your Dataset Stats (REQUIRED for un-normalization)
    # This file is inside your dataset folder
    stats_path = os.path.expanduser("lerobot_10 single_position/lerobot_dataset_v3_final/meta/stats.json")
    
    node = LeRobotGazeboPilot(policy_path, stats_path)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()