from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Turtlesim Node
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim'
        ),
        # 2. Go To Pose Action Server
        Node(
            package='my_turtle',
            executable='go_to_pose_server',
            name='go_to_pose_server'
        ),
        # 3. Reset Service
        Node(
            package='my_turtle',
            executable='reset_service',
            name='reset_service'
        ),
        # 4. Draw Square Action Server
        Node(
            package='my_turtle',
            executable='draw_square_server',
            name='draw_square_server'
        ),
    ])