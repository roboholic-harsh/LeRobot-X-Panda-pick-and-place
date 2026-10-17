# cube_spawner

A ROS 2 simulation utility package for dynamically spawning manipulation objects and managing full system bringup in Ignition Gazebo.

## 📌 Overview

`cube_spawner` manages:
1. Dynamic creation of physical objects (SDF models) into the running Ignition Gazebo simulation via `ros_gz_sim create`.
2. Master system bringup orchestration (`bringup.launch.py`) that coordinates Gazebo, controller initialization, and MoveIt 2.

---

## 🚀 Key Scripts & Executables

### 1. `timely_spawner.py` (`spawn_block`)
- Spawns a $4\text{ cm}$ red cube at the exact **trained single position**:
  - $X = 0.45\text{ m}$
  - $Y = 0.15\text{ m}$
  - $Z = 0.121\text{ m}$
- Automatically runs periodically (every 40s) or can be executed as a one-shot command.

```bash
ros2 run cube_spawner spawn_block
```

### 2. `spawn_colored.py` (`spawn_colored`)
- Batch spawns a set of colored cubes (3 Red, 3 Blue, 3 Green) across randomized table positions ($X \in [0.35, 0.65]$, $Y \in [-0.30, 0.30]$, $Z = 0.121$).
- Used for color-sorting experiments.

```bash
ros2 run cube_spawner spawn_colored
```

### 3. `spawner.py`
- General purpose spawner with randomized coordinates across table boundaries.

---

## 📂 Launch Files

### `bringup.launch.py` (Master Environment Bringup)
Orchestrates the entire simulation environment:
- Loads `franka_moveit_config/launch/gazebo.launch.py` (Ignition Gazebo + Panda Robot + Dual Camera bridges).
- Starts `move_group.launch.py` with `use_sim_time:=true`.
- Forces `/move_group` ROS parameters to maintain time synchronization with simulation time.

```bash
ros2 launch cube_spawner bringup.launch.py
```

### `coloured_spawner_world.launch.py`
Launches Gazebo and invokes `spawn_colored` with a 5-second timer delay to populate the table with colored sorting blocks.

```bash
ros2 launch cube_spawner coloured_spawner_world.launch.py
```

