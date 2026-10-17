# panda_description

Robot description package containing URDF models, visual meshes, and collision models for the 7-DOF Franka Emika Panda manipulator and parallel gripper.

## 📌 Contents

- **`urdf/panda.urdf`**: Canonical kinematic description of the Franka Emika Panda arm (joints 1 to 7) and Panda Hand (finger joints 1 and 2).
- **`meshes/visual/`**: DAE (Collada) files representing high-fidelity visual representations of each robot link (`link0.dae` through `link7.dae`, `hand.dae`, `finger.dae`).
- **`meshes/collision/`**: STL collision geometries optimized for efficient collision-checking and ray-tracing physics in MoveIt 2 and Ignition Gazebo.

## 📄 Licensing

The URDF models and mesh assets were sourced from the `franka_ros` package by Franka Emika GmbH and adapted for ROS 2 and MoveIt 2 resources under the Apache-2.0 license.
