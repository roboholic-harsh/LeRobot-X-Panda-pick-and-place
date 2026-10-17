# LeRobot Single-Position Demonstration Dataset

![Dual Camera Demonstration](../../assets/data_collection_dual_cam.gif)

*Synchronized dual-camera demonstration playback: Overhead View (Left) and Wrist/Gripper View (Right).*

---

## 📌 Dataset Overview

This dataset was recorded in Ignition Gazebo using the Franka Emika Panda robot. It provides expert demonstrations of picking a red block placed at a fixed single position on the table and depositing it into the dustbin.

- **Dataset Codebase Version:** LeRobot `v3.0`
- **Robot Type:** Franka Emika Panda (7-DOF Arm + 2-Finger Gripper)
- **Total Episodes:** 11 episodes
- **Total Frames:** 3,948 frames
- **FPS:** 30 Hz
- **Chunk Size:** 1,000 frames per chunk

---

## 🎥 Camera Perspectives & Media

| Stream | Resolution | Encoding | Path |
|---|---|---|---|
| **Overhead Camera** (`observation.images.world`) | $640 \times 480 \times 3$ | H.264 / MP4 | `lerobot_dataset_v3_final/videos/observation.images.world/chunk-000/file-000.mp4` |
| **Wrist/Gripper Camera** (`observation.images.gripper`) | $640 \times 480 \times 3$ | H.264 / MP4 | `lerobot_dataset_v3_final/videos/observation.images.gripper/chunk-000/file-000.mp4` |

### Visual Demonstrations
<p align="center">
  <img src="../../assets/data_collection_world.gif" width="48%" alt="Overhead Camera Demo" />
  <img src="../../assets/data_collection_gripper.gif" width="48%" alt="Wrist Camera Demo" />
</p>
<p align="center">
  <em>Left: Overhead Camera View &bull; Right: Eye-in-Hand Gripper Camera View</em>
</p>

---

## 📊 Features & Schema

From `lerobot_dataset_v3_final/meta/info.json`:

```json
{
  "observation.images.world": { "dtype": "video", "shape": [480, 640, 3] },
  "observation.images.gripper": { "dtype": "video", "shape": [480, 640, 3] },
  "observation.state": {
    "dtype": "float32",
    "shape": [9],
    "names": [
      "panda_joint1", "panda_joint2", "panda_joint4",
      "panda_joint5", "panda_joint6", "panda_joint7",
      "panda_joint3", "panda_finger_joint1", "panda_finger_joint2"
    ]
  },
  "action": {
    "dtype": "float32",
    "shape": [9],
    "names": [
      "panda_joint1", "panda_joint2", "panda_joint4",
      "panda_joint5", "panda_joint6", "panda_joint7",
      "panda_joint3", "panda_finger_joint1", "panda_finger_joint2"
    ]
  }
}
```

---

## 🎯 Target Pose & Coordinate Reference

- **Initial Cube Position:** $X = 0.45\text{ m}, Y = 0.15\text{ m}, Z = 0.121\text{ m}$
- **Target Bin Location:** $X = 0.0\text{ m}, Y = 0.5\text{ m}, Z = 0.5\text{ m}$
- **Normalization Stats:** Computed and stored in `lerobot_dataset_v3_final/meta/stats.json` for mean/std scaling.

