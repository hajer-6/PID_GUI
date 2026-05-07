import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray  
import random
import time

class SpeedPublisher(Node):
    def __init__(self):
        super().__init__('speed_publisher')
        # Change the message type to Float32MultiArray
        self.publisher_ = self.create_publisher(Float32MultiArray, '/speed', 10)
        self.timer = self.create_timer(0.1, self.publish_speed)
        # Initialize 4 different speed values
        self.speeds = [0.0, 0.0, 0.0, 0.0]
        self.get_logger().info('Speed array publisher started')

    def publish_speed(self):
        # Update each speed value independently
        for i in range(4):
            self.speeds[i] = self.speeds[i] + random.uniform(-1, 1)
            self.speeds[i] = max(0.0, min(self.speeds[i], 50))
        
        # Create Float32MultiArray message
        msg = Float32MultiArray()
        
        # Set the data field (this is a list of floats)
        msg.data = self.speeds
        self.publisher_.publish(msg)
        self.get_logger().info(f"Publishing speeds: {[f'{s:.2f}' for s in self.speeds]}")

def main(args=None):
    rclpy.init(args=args)
    node = SpeedPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()