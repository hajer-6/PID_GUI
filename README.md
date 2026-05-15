# ROS-GUI: Web Interface for Robot Control

A modern web-based graphical user interface built with **Svelte** and **Vite** that communicates with ROS2 through **ROS Bridge**. This project provides an intuitive dashboard for monitoring and controlling robots in real-time.

## Project Overview

This application serves as a bridge between your ROS2-powered robots  and a web browser interface. It allows you to:
- Monitor robot telemetry and sensor data
- Send control commands to your robot
- Visualize real-time robot states
- Interact with ROS topics, services, and parameters through a clean GUI


### Prerequisites

- **Node.js** 
- **ROS2**
- **ROS Bridge Server** 
- **Svelte (Vite version)** - automatically set up below

<img width="794" height="490" alt="Screenshot 2026-05-15 170050" src="https://github.com/user-attachments/assets/c857201b-6359-487b-8dd7-720a4ed07d82" />

---

## 🛠 Installation & Setup

### Step 1: Install Node.js and npm

Download and install Node.js from [nodejs.org](https://nodejs.org/en)

Verify installation:
```bash
node --version
npm --version
```

### Step2:Create svelte project
```
npm create vite@latest
```
When prompted:
    Project name: Enter a lowercase name (e.g., ros-gui)
    Select framework: Choose Svelte
    Select variant: Choose JavaScript
    Use vite 8 beta: Select no
    Install with npm and start now: Select yes

    cd your-project-name
    npm install

### Step 3: Install ROS Bridge Server
  ```
  sudo apt install ros-jazzy-rosbridge-server
```
### step4: Run
```
 ros2 launch rosbridge_server rosbridge_websocket_launch.xml
  cd gui
  npm install
  npm run dev
```
Click the "Network" link in the terminal output to open the application in your browser.

