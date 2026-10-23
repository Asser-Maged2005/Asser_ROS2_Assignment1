import math
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from geometry_msgs.msg import Twist

try:
    from turtlesim_msgs.msg import Pose
except ImportError:
    from turtlesim.msg import Pose

# Custom interfaces
from my_turtle_interfaces.msg import Posetarget
from my_turtle_interfaces.srv import Setspeed
from my_turtle_interfaces.action import Gotopose


class GoToPoseServer(Node):
    def __init__(self):
        super().__init__('go_to_pose_server')

        # Allow callbacks to run concurrently to prevent while-loop deadlocks
        self.cb_group = ReentrantCallbackGroup()

        # Speed parameters
        self.declare_parameter('max_linear_speed', 2.0)
        self.declare_parameter('max_angular_speed', 2.0)

        self.current_pose = Pose()

        # Subscribe to turtlesim pose
        self.pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
            callback_group=self.cb_group
        )

        # Publisher for velocity commands
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # Service to change speed limits
        self.speed_srv = self.create_service(
            Setspeed,
            'set_speed',
            self.handle_set_speed,
            callback_group=self.cb_group
        )

        # Action server to drive turtle to pose
        self.action_server = ActionServer(
            self,
            Gotopose,
            'go_to_pose',
            self.execute_go_to_pose,
            callback_group=self.cb_group
        )

        self.get_logger().info('GoToPose Action & Parameter Server is ready!')

    def pose_callback(self, msg: Pose):
        """Updates internal pose state whenever turtlesim publishes new coordinates."""
        self.current_pose = msg

    def handle_set_speed(self, request, response):
        if request.max_linear <= 0 or request.max_angular <= 0:
            response.success = False
            response.message = "Speed limits must be positive numbers!"
            return response

        self.set_parameters([
            rclpy.parameter.Parameter('max_linear_speed', value=request.max_linear),
            rclpy.parameter.Parameter('max_angular_speed', value=request.max_angular)
        ])

        response.success = True
        response.message = f"New limits set: Linear={request.max_linear}, Angular={request.max_angular}"
        self.get_logger().info(response.message)
        return response

    def execute_go_to_pose(self, goal_handle):
        self.get_logger().info('Received a new GoToPose goal...')
        target = goal_handle.request.target
        feedback_msg = Gotopose.Feedback()

        rate = self.create_rate(10)

        while rclpy.ok():
            max_lin = self.get_parameter('max_linear_speed').value
            max_ang = self.get_parameter('max_angular_speed').value

            dx = target.x - self.current_pose.x
            dy = target.y - self.current_pose.y
            distance = math.hypot(dx, dy)

            feedback_msg.distance_remaining = distance
            goal_handle.publish_feedback(feedback_msg)

            cmd = Twist()

            # Phase 1: Navigate to target coordinate
            if distance > 0.1:
                target_angle = math.atan2(dy, dx)
                angle_error = target_angle - self.current_pose.theta
                angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))

                # FIX 1: Pivot first, then drive. Prevents wide arcs and endless orbiting.
                if abs(angle_error) > 0.1:
                    cmd.linear.x = 0.0
                else:
                    cmd.linear.x = min(1.5 * distance, max_lin)

                # FIX 2: Clamp angular velocity on both positive and negative limits
                cmd.angular.z = max(-max_ang, min(4.0 * angle_error, max_ang))
                self.cmd_pub.publish(cmd)

            # Phase 2: Align to final yaw angle
            else:
                yaw_error = target.yaw - self.current_pose.theta
                yaw_error = math.atan2(math.sin(yaw_error), math.cos(yaw_error))

                if abs(yaw_error) > 0.05:
                    cmd.linear.x = 0.0
                    cmd.angular.z = max(-max_ang, min(4.0 * yaw_error, max_ang))
                    self.cmd_pub.publish(cmd)
                else:
                    cmd.linear.x = 0.0
                    cmd.angular.z = 0.0
                    self.cmd_pub.publish(cmd)
                    break

            rate.sleep()

        goal_handle.succeed()
        result = Gotopose.Result()
        result.success = True
        self.get_logger().info('Turtle arrived at target pose!')
        return result


def main(args=None):
    rclpy.init(args=args)
    node = GoToPoseServer()
    
    # Threading prevents the rate.sleep() loop from blocking incoming pose_callbacks
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()