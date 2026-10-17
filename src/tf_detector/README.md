# tf_detector

A ROS 2 computer vision and 3D spatial coordinate projection package for object detection in robotic manipulation.

## 📌 Overview

`tf_detector` bridges 2D camera images and 3D Cartesian coordinates. It processes color images from simulated overhead cameras, performs color segmentation (HSV masking), calculates bounding boxes and centroids, and uses pinhole camera model ray-casting against the table surface plane to compute precise 3D world coordinates via the `tf2_ros` transform tree.

---

## 🚀 Key Nodes

### 1. `detector.py` (Object & Red Cube Detector)
- Subscribes to:
  - `/camera/overhead_camera/camera_info` (`sensor_msgs/msg/CameraInfo`)
  - `/camera/overhead_camera/image_raw` (`sensor_msgs/msg/Image`)
- Detection Pipeline:
  1. Identifies the table contour using HSV thresholding to constrain the Region of Interest (ROI).
  2. Detects red cubes within the ROI using dual-band HSV thresholds ($H \in [0, 10] \cup [170, 180]$).
  3. Projects 2D pixels to 3D rays in the camera frame via `image_geometry.PinholeCameraModel`.
  4. Transforms rays into the `world` frame using `tf2_ros`.
  5. Computes ray-plane intersection at table object height ($Z = 0.12\text{ m}$).
  6. Identifies the top-right candidate and publishes to `/block_coordinates_tf` and `/block_marker_tf`.

```bash
ros2 run tf_detector detector
```

### 2. `colored_detector.py` / `colored_detector2.py` (Multi-Class Color Detector)
- Simultaneously detects Red, Blue, and Green blocks.
- Publishes segregated coordinate streams to:
  - `/red_block_coords` (`geometry_msgs/msg/Point`)
  - `/blue_block_coords` (`geometry_msgs/msg/Point`)
  - `/green_block_coords` (`geometry_msgs/msg/Point`)

```bash
ros2 run tf_detector colored_detector
```

---

## 📂 Launch Files

### `vision_system.launch.py`
Brings up the simulation environment via `cube_spawner/bringup.launch.py` and launches `detector.py` with visualization windows.

```bash
ros2 launch tf_detector vision_system.launch.py
```

### `sorting_system.launch.py`
Brings up the simulation with colored blocks and launches the multi-class color detector node.

```bash
ros2 launch tf_detector sorting_system.launch.py
```

