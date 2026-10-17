# franka_moveit_config

MoveIt 2 configuration and Ignition Gazebo simulation setup for the Franka Emika Panda robot with dual-camera perception.

## 📌 Overview

This package encapsulates the robot semantic definition (`panda.srdf`), controller configurations (`ros2_control`), kinematic solver settings, Gazebo physics world (`table_world.sdf`), and dual-camera sensor definitions (`camera.xacro`).

---

## 📷 Camera Setup (`config/camera.xacro`)

The simulation defines two cameras:
1. **Overhead Camera (Static World View)**:
   - Position: $X = 0.2\text{ m}, Y = 0.0\text{ m}, Z = 1.8\text{ m}$
   - Orientation: Pointing downward at the table ($RPY = [-\frac{\pi}{2}, \frac{\pi}{2}, 0]$)
   - Topic: `/camera/overhead_camera/image_raw`
2. **Hand/Wrist Camera (Eye-in-Hand)**:
   - Attached to link: `panda_hand`
   - Offset: $XYZ = [0.08, 0, 0.08]$, $RPY = [\pi, -2.35619, 0]$
   - Topic: `/camera/hand_camera/image_raw`

---

## 🚀 Controllers & Hardware Interface

Defined in `config/ros2_controllers.yaml`:
- **`joint_state_broadcaster`**: Publishes all arm and finger joint positions to `/joint_states`.
- **`panda_arm_controller`**: FollowJointTrajectory controller for `panda_joint1` through `panda_joint7`.
- **`hand_controller`**: FollowJointTrajectory controller for `panda_finger_joint1` and `panda_finger_joint2`.

Communication between Ignition Gazebo and ROS 2 is maintained via `ros_gz_bridge`.

---

## 📂 Launch Files

### `gazebo.launch.py`
Starts Ignition Gazebo with `table_world.sdf`, spawns the Panda robot model, launches `robot_state_publisher`, activates the controllers sequentially via process exit handlers, and bridges camera topics.

```bash
ros2 launch franka_moveit_config gazebo.launch.py
```

### `move_group.launch.py`
Launches the MoveIt 2 MoveGroup node, loading OMPL and Pilz cartesian planning pipelines, kinematics solvers, and execution capabilities.

```bash
ros2 launch franka_moveit_config move_group.launch.py use_sim_time:=true
```

### `moveit_rviz.launch.py`
Visualizes the robot state and trajectory planning interface in RViz2.

```bash
ros2 launch franka_moveit_config moveit_rviz.launch.py
```

