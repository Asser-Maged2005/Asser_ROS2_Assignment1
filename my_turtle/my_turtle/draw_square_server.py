import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, ActionClient
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from action_msgs.msg import GoalStatus
from std_srvs.srv import Empty

from my_turtle_interfaces.msg import Posetarget

try:
    from my_turtle_interfaces.action import Gotopose
except ImportError:
    from my_turtle_interfaces.action import GoToPose as Gotopose


class DrawSquareServer(Node):
    def __init__(self):
        super().__init__('draw_square_server')

        # Allow concurrent execution of sub-actions without deadlocking
        self.cb_group = ReentrantCallbackGroup()

        self.reset_client = self.create_client(
            Empty, 'reset_turtle', callback_group=self.cb_group)
            
        self.go_to_pose_client = ActionClient(
            self, Gotopose, 'go_to_pose', callback_group=self.cb_group)
            
        self.action_server = ActionServer(
            self, Gotopose, 'draw_square',
            execute_callback=self.execute_draw_square,
            callback_group=self.cb_group
        )

        self.get_logger().info('Draw Square Action Server Node is READY!')

    async def execute_draw_square(self, goal_handle):
        self.get_logger().info('Received goal: Drawing square...')

        # 1. Reset turtle
        if self.reset_client.wait_for_service(timeout_sec=3.0):
            await self.reset_client.call_async(Empty.Request())
            self.get_logger().info('Turtle reset completed.')

        # 2. Check go_to_pose availability
        if not self.go_to_pose_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('go_to_pose action server is NOT online!')
            goal_handle.abort()
            return Gotopose.Result(success=False)

        # 3. Corner positions starting from origin (5.54, 5.54) with side length 3.0
        side = 3.0
        x0, y0 = 5.544445, 5.544445

        corners = [
            (x0 + side, y0, 0.0),          # Corner 1: Right
            (x0 + side, y0 + side, 1.57),   # Corner 2: Top Right
            (x0, y0 + side, 3.14),          # Corner 3: Top Left
            (x0, y0, 0.0)                   # Corner 4: Back to Origin
        ]

        feedback = Gotopose.Feedback()

        for i, (cx, cy, cyaw) in enumerate(corners):
            self.get_logger().info(f'Navigating to Corner {i+1}/4: ({cx:.2f}, {cy:.2f})')

            goal_msg = Gotopose.Goal()
            goal_msg.target = Posetarget(x=cx, y=cy, yaw=cyaw)

            # Send sub-goal safely using await
            sub_handle = await self.go_to_pose_client.send_goal_async(goal_msg)
            if not sub_handle.accepted:
                self.get_logger().error(f'Corner {i+1} rejected!')
                goal_handle.abort()
                return Gotopose.Result(success=False)

            # Await execution
            res = await sub_handle.get_result_async()
            if res.status != GoalStatus.STATUS_SUCCEEDED:
                self.get_logger().error(f'Failed at corner {i+1}')
                goal_handle.abort()
                return Gotopose.Result(success=False)

            # Publish feedback
            feedback.distance_remaining = float(4 - (i + 1))
            goal_handle.publish_feedback(feedback)

        goal_handle.succeed()
        self.get_logger().info('Square pattern completed successfully!')
        return Gotopose.Result(success=True)


def main(args=None):
    rclpy.init(args=args)
    node = DrawSquareServer()
    
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