import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

class Test(Node):
    def __init__(self):
        super().__init__('test_sub')

        self.create_subscription(Float32, '/pid/kp', self.cb_kp, 10)
        self.create_subscription(Float32, '/pid/ki', self.cb_ki, 10)
        self.create_subscription(Float32, '/pid/kd', self.cb_kd, 10)
        self.create_subscription(String, '/pid/gains', self.cb_all, 10)

    def cb_kp(self, msg):
        print("Kp =", msg.data)

    def cb_ki(self, msg):
        print("Ki =", msg.data)

    def cb_kd(self, msg):
        print("Kd =", msg.data)

    def cb_all(self, msg):
        print("All =", msg.data)

rclpy.init()
node = Test()
rclpy.spin(node)
