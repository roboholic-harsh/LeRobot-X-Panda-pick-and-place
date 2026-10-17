# automatic_pnp

A ROS 2 motion planning and pick-and-place execution package for the Franka Emika Panda manipulator using MoveIt 2.

## 📌 Overview

`automatic_pnp` serves as the high-level task planner and trajectory execution engine. It interfaces with perception topics (from `tf_detector`) to retrieve 3D world coordinates of objects on the table, computes collision-free trajectories via MoveIt 2's Cartesian planning pipeline and inverse kinematics, and actuates the parallel gripper.

---

## 🚀 Key Nodes

### 1. `pnp.py` (Base Trajectory Pick & Place)
- Subscribes to `/block_coordinates_tf` (`geometry_msgs/msg/Point`).
- Performs pre-grasp approach ($Z = 0.35\text{ m}$), Cartesian descent to object height ($Z = \text{point.z} + 0.10\text{ m}$), grasps using `/hand_controller/follow_joint_trajectory`, lifts the object, transports it to the dustbin ($X=0.0, Y=0.5, Z=0.5$), releases, and returns home.

```bash
ros2 run automatic_pnp pnp
```

### 2. `clear_table.py` (Robust Table Cleaner)
- An enhanced cleaning node with real-time TCP arrival verification via `tf2_ros` transform lookup (`panda_link8` vs. target pose).
- Prevents early drop failures by validating that the gripper has physically arrived at the destination before opening.

```bash
ros2 run automatic_pnp clear_table
```

### 3. `automated_sorting.py` & `automated_sorting2.py` (Priority Color Sorting)
- Subscribes to color-segregated coordinate topics:
  - `/red_block_coords`
  - `/blue_block_coords`
  - `/green_block_coords`
- Enforces strict priority sorting: **Red** $\rightarrow$ **Blue** $\rightarrow$ **Green**.
- Places sorted blocks into designated bin locations:
  - **Red Bin**: $X=0.0, Y=0.5, Z=0.5$ (Left)
  - **Blue Bin**: $X=0.0, Y=-0.5, Z=0.5$ (Right)
  - **Green Bin**: $X=-0.5, Y=0.0, Z=0.5$ (Rear)

```bash
ros2 run automatic_pnp automated_sorting
```

---

## 📡 Interfaces & Topics

### Subscriptions
| Topic | Type | Description |
|---|---|---|
| `/block_coordinates_tf` | `geometry_msgs/msg/Point` | 3D coordinates of target block in world frame |
| `/red_block_coords` | `geometry_msgs/msg/Point` | 3D coordinates of detected red block |
| `/blue_block_coords` | `geometry_msgs/msg/Point` | 3D coordinates of detected blue block |
| `/green_block_coords` | `geometry_msgs/msg/Point` | 3D coordinates of detected green block |

### Action Clients & Service Clients
| Client / Service | Type | Purpose |
|---|---|---|
| `move_action` | `moveit_msgs/action/MoveGroup` | High-level arm joint motion |
| `execute_trajectory` | `moveit_msgs/action/ExecuteTrajectory` | Execution of calculated trajectories |
| `compute_cartesian_path` | `moveit_msgs/srv/GetCartesianPath` | Linear end-effector Cartesian motion |
| `compute_ik` | `moveit_msgs/srv/GetPositionIK` | Inverse kinematics solver |
| `/hand_controller/follow_joint_trajectory` | `control_msgs/action/FollowJointTrajectory` | Franka finger gripper control (open: 0.036m, close: 0.00m) |

