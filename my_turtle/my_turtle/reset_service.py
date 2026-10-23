import rclpy
from rclpy.node import Node
from std_srvs.srv import Empty

# Handle package name variations for turtlesim services
try:
    from turtlesim_msgs.srv import TeleportAbsolute, SetPen
except ImportError:
    from turtlesim.srv import TeleportAbsolute, SetPen


class ResetService(Node):
    def __init__(self):
        super().__init__('reset_service')

        # Create service clients
        self.clear_client = self.create_client(Empty, '/clear')
        self.teleport_client = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')

        # Expose custom /reset_turtle service
        self.reset_srv = self.create_service(Empty, 'reset_turtle', self.handle_reset)

        self.get_logger().info('Reset Service Node is Ready!')

    def handle_reset(self, request, response):
        self.get_logger().info('Resetting turtle pose without trailing lines...')

        # Step 1: Turn off the pen (off=1)
        if self.pen_client.wait_for_service(timeout_sec=1.0):
            pen_req = SetPen.Request()
            pen_req.off = 1
            self.pen_client.call_async(pen_req)

        # Step 2: Teleport back to starting center (5.544445, 5.544445, yaw=0.0)
        if self.teleport_client.wait_for_service(timeout_sec=1.0):
            teleport_req = TeleportAbsolute.Request()
            teleport_req.x = 5.544445
            teleport_req.y = 5.544445
            teleport_req.theta = 0.0
            self.teleport_client.call_async(teleport_req)

        # Step 3: Turn pen back on (off=0) with default white color
        if self.pen_client.wait_for_service(timeout_sec=1.0):
            pen_req = SetPen.Request()
            pen_req.r = 255
            pen_req.g = 255
            pen_req.b = 255
            pen_req.width = 2
            pen_req.off = 0
            self.pen_client.call_async(pen_req)

        # Step 4: Clear any lingering artifacts on screen
        if self.clear_client.wait_for_service(timeout_sec=1.0):
            clear_req = Empty.Request()
            self.clear_client.call_async(clear_req)

        return response


def main(args=None):
    rclpy.init(args=args)
    node = ResetService()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()