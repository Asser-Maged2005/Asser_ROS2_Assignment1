# Asser_ROS2_Assignment1

ROS2 assignment developed by **Asser Maged**, **Osama Mohamed**, & **Youssef Mahmoud**.

### Team Members
* **Asser Maged** - 9478
* **Osama Mohammed** - 9686
* **Youssef Mahmoud** - 9385

---

## Getting Started

> **Note:** The directory paths below assume your workspace is at `~/ROSpractice`. Please adjust if your workspace is saved elsewhere.

### Launch Instructions

#### Terminal 1: Launching the Nodes
```bash
cd ~/ROSpractice
source install/setup.bash
ros2 launch my_turtle turtle_lab.launch.py
```

#### Terminal 2: Sending the Action Goal
```bash
cd ~/ROSpractice
source install/setup.bash
ros2 action send_goal /draw_square my_turtle_interfaces/action/Gotopose "{target: {x: 3.0, y: 3.0, yaw: 0.0}}" --feedback
```

---

## Rosbag Operations

### Record
To record all topics during the run, use:
```bash
ros2 bag record -a -o square_run_bag
```

### Replay
To replay the data, first reset the turtle environment and then play the bag:
```bash
ros2 service call /reset_turtle std_srvs/srv/Empty {}
ros2 bag play square_run_bag
```
