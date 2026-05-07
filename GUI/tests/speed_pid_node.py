import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import time


class PIDController(Node):
    def __init__(self):
        super().__init__('pid_controller')
        
        # PID parameters (can be tuned via ROS parameters or topics)
        self.kp = 1.0
        self.ki = 0.1
        self.kd = 0.01
        
        # PID states
        self.prev_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()
        
        # Target speed (can be set via ROS topic)
        self.target_speed = 5.0
        
        # Subscriber for raw speed
        self.raw_speed_subscriber = self.create_subscription(
            Float32,
            '/raw_speed',
            self.raw_speed_callback,
            10
        )
        
        # Publisher for PID-controlled speed
        self.controlled_speed_publisher = self.create_publisher(
            Float32,
            '/speed',  # This is what the chart subscribes to
            10
        )
        
        # Publisher for target speed (optional, for monitoring)
        self.target_publisher = self.create_publisher(
            Float32,
            '/pid/target_speed',
            10
        )
        
        # Publisher for PID parameters (optional)
        self.pid_params_publisher = self.create_publisher(
            Float32,
            '/pid_params',
            10
        )
        
        # Subscription for target speed updates
        self.target_subscriber = self.create_subscription(
            Float32,
            '/set_target_speed',
            self.target_speed_callback,
            10
        )
        
        # Timer for publishing target speed
        self.target_timer = self.create_timer(1.0, self.publish_target_speed)
        
        self.get_logger().info('PID Controller started')

    def target_speed_callback(self, msg):
        """Update target speed when received"""
        self.target_speed = msg.data
        self.get_logger().info(f'Target speed updated to: {self.target_speed}')

    def publish_target_speed(self):
        """Publish current target speed for monitoring"""
        msg = Float32()
        msg.data = self.target_speed
        self.target_publisher.publish(msg)

    def raw_speed_callback(self, msg):
        """Process raw speed through PID controller"""
        current_speed = msg.data
        current_time = time.time()
        dt = current_time - self.last_time
        
        # Calculate error
        error = self.target_speed - current_speed
        
        # Calculate PID terms
        p_term = self.kp * error
        
        self.integral += error * dt
        i_term = self.ki * self.integral
        
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        d_term = self.kd * derivative
        
        # Calculate control output
        control_output = p_term + i_term + d_term
        
        # Apply control to speed (simple addition for simulation)
        controlled_speed = current_speed + control_output
        
        # Clamp the speed
        controlled_speed = max(0.0, min(controlled_speed, 50.0))
        
        # Update states
        self.prev_error = error
        self.last_time = current_time
        
        # Publish controlled speed
        output_msg = Float32()
        output_msg.data = controlled_speed
        self.controlled_speed_publisher.publish(output_msg)
        
        # Log PID info
        self.get_logger().info(
            f'Raw: {current_speed:.2f}, Target: {self.target_speed:.2f}, '
            f'Controlled: {controlled_speed:.2f}, '
            f'Error: {error:.2f}, P: {p_term:.2f}, I: {i_term:.2f}, D: {d_term:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)
    pid_controller = PIDController()
    
    try:
        rclpy.spin(pid_controller)
    except KeyboardInterrupt:
        pass
    
    pid_controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()