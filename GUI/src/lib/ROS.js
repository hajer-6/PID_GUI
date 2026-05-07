// rosConnection.js
 import ROSLIB from 'roslib';

// Create ROS connection
export const ros = new ROSLIB.Ros({
  url: 'ws://localhost:9090'
});

// Connection events
ros.on('connection', () => console.log('ROS connected'));
ros.on('error', (error) => console.error('ROS error:', error));
ros.on('close', () => console.log('ROS disconnected'));

// PID Publishers
export const kpPublisher = new ROSLIB.Topic({
  ros,
  name: '/pid/kp',
  messageType: 'std_msgs/Float32'
});

export const kiPublisher = new ROSLIB.Topic({
  ros,
  name: '/pid/ki',
  messageType: 'std_msgs/Float32'
});

export const kdPublisher = new ROSLIB.Topic({
  ros,
  name: '/pid/kd',
  messageType: 'std_msgs/Float32'
});

export const PIDPublisher = new ROSLIB.Topic({
  ros,
  name: '/pid/PIDvalue',
  messageType: 'std_msgs/Float32MultiArray'
});

export const targetPublisher = new ROSLIB.Topic({
    ros,
    name: '/pid/target_speed',
    messageType: 'std_msgs/Float32MultiArray'
});

export const targetSubscriber = new ROSLIB.Topic({
  ros,
  name: '/pid/target_speed',
  messageType: 'std_msgs/Float32MultiArray'
});

// Chart Subscribers
export const speedSubscriber = new ROSLIB.Topic({
  ros,
  name: '/speed',
  messageType: 'std_msgs/Float32MultiArray'
});


