# Asser_ROS2_Assignment1

ROS2 assignment developed by **Asser Maged**, **Osama Mohamed**, & **Youssef Mahmoud**.

### Team Members
- **Asser Maged** - 9478
- **Osama Mohammed** - 9686
- **Youssef Mahmoud** - 9385

---

## Getting Started

> **Note:** The directory paths below assume your workspace is at `~/ROSpractice`. Please adjust if your workspace is saved elsewhere.
> 
> **Important:** Always run these two lines when opening a new terminal before executing any commands below:
> ```bash
> cd ~/ROSpractice
> source install/setup.bash
> ```

### 1. Boot up the System
Run the master launch file in your **first terminal** to start Turtlesim and all background servers:
```bash
ros2 launch my_turtle turtle_lab.launch.py
```

---

## Usage Scenarios

Open a **second terminal** (remember to source it!) to trigger any of the following commands:

### Scenario A: Draw a Complete Square
Triggers the planner to draw a full 4-point square starting at the given coordinates.
```bash
ros2 action send_goal /draw_square my_turtle_interfaces/action/Gotopose "{target: {x: 3.0, y: 3.0, yaw: 0.0}}" --feedback
```

### Scenario B: Drive to a Single Custom Pose
Bypasses the square planner and drives the turtle to one specific point (e.g., x=8, y=8).
```bash
ros2 action send_goal /go_to_pose my_turtle_interfaces/action/Gotopose "{target: {x: 8.0, y: 8.0, yaw: 1.57}}" --feedback
```

### Scenario C: Reset the Turtle & Clear Screen
Instantly lifts the pen, teleports the turtle to the center, and wipes the drawn lines.
```bash
ros2 service call /reset_turtle std_srvs/srv/Empty {}
```

### Scenario D: Change the Max Speed limits
Updates the linear and angular speed limits on the fly without restarting the nodes.
```bash
ros2 service call /set_speed my_turtle_interfaces/srv/Setspeed "{max_linear: 4.0, max_angular: 4.0}"
```

### Scenario E: Lift or Customize the Pen
Directly call the Turtlesim pen service to change colors or lift the pen completely (`off: 1` lifts it, `off: 0` puts it down).
```bash
ros2 service call /turtle1/set_pen turtlesim/srv/SetPen "{r: 255, g: 0, b: 0, width: 3, off: 1}"
```

---

## Rosbag Operations (Bonus)

### Record a Run
To record all system topics (including velocity commands) during a run:
```bash
ros2 bag record -a -o square_run_bag
```

### Replay a Run
To prove autonomous playback, clear the screen and play the recorded bag file:
```bash
ros2 service call /reset_turtle std_srvs/srv/Empty {}
ros2 bag play square_run_bag
```
