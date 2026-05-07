<!-- App.svelte -->
<!-- App.svelte -->
<script>
  import ROSLIB from 'roslib';
  import PIDPanel from './PID_buttons.svelte';
  import SpeedChart from './Speed_chart.svelte';
  import { PIDPublisher, ros, targetPublisher } from '../lib/ROS';
  
  let isConnected = false;
  let targetSpeed = [0, 0, 0, 0];
  let pid_params = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
  let selectedWheel = 0;
  let kp = 0;
  let kd = 0;
  let ki = 0;
  let tolerance = 1;
  let timeWindowSeconds = 15;
 
  
  // New variable for wheel-specific target input
  let wheelTargetInput = 0;
  
  ros.on('connection', () => isConnected = true);
  ros.on('close', () => isConnected = false);
  
  // Function to handle wheel selection change
  function handleWheelSelection(event) {
    const wheel = Number(event.target.value);
    selectedWheel = wheel;
    console.log(`Wheel ${wheel} selected`);
    
    // Update wheelTargetInput with current value of selected wheel
    if (wheel === 0) {
      // All wheels - use first wheel's value or average
      wheelTargetInput = targetSpeed[0];
    } else {
      // Specific wheel - use its current value
      wheelTargetInput = targetSpeed[wheel - 1];
    }
    
    // Update PID if values exist
    if (kp !== 0 || kd !== 0 || ki !== 0) {
      publishPIDForSelectedWheel(kp, kd, ki);
    }
  }
  
  // Function to set target speed for selected wheel
  function setTargetForSelectedWheel() {
    const speed = parseFloat(wheelTargetInput);
    // Create new array with updated value(s)
    const newTarget = [...targetSpeed];
    
    if (selectedWheel === 0) {
      // Set all wheels to the same value
      for (let i = 0; i < 4; i++) {
        newTarget[i] = speed;
      }
      console.log(`Setting all wheels to target speed: ${speed}`);
    } else {
      // Set only the selected wheel
      const wheelIndex = selectedWheel - 1;
      newTarget[wheelIndex] = speed;
      console.log(`Setting wheel ${selectedWheel} to target speed: ${speed}`);
    }
    
    // Update local state
    targetSpeed = newTarget;
    
    // Publish to ROS
    publishTargetSpeed(newTarget);
  }
  
  // Function to publish target speed to ROS
  function publishTargetSpeed(newTargetArray) {
    if (!isConnected) {
      console.error('Cannot publish: ROS disconnected');
      return false;
    }
    
    try {
      const targetMessage = new ROSLIB.Message({
        layout: {
          dim: [{
            label: 'wheel_targets',
            size: 4,
            stride: 1
          }],
          data_offset: 0
        },
        data: newTargetArray.map(val => parseFloat(val))
      });
      
      targetPublisher.publish(targetMessage);
      console.log('Published target speeds to ROS:', newTargetArray);
      
      // Update the chart via event
      dispatch('targetupdate', { speed: newTargetArray });
      return true;
    } catch (error) {
      console.error('Error publishing target speed:', error);
      return false;
    }
  }
  
  // Handle target speed changes from chart
  function handleTargetChange(event) {
    targetSpeed = event.detail.speed;
    // Update wheelTargetInput to reflect changes
    if (selectedWheel === 0) {
      wheelTargetInput = targetSpeed[0];
    } else if (selectedWheel > 0) {
      wheelTargetInput = targetSpeed[selectedWheel - 1];
    }
  }
  
  function handleToleranceChange(event) {
    tolerance = event.detail.tolerance;
  }
  
  function handleTimeWindowChange(event) {
    timeWindowSeconds = event.detail.seconds;
  }
  
  function updateTimeWindow(seconds) {
    timeWindowSeconds = seconds;
  }
  
  // Rest of your PID functions remain the same...
  function publishPIDForSelectedWheel(kpVal, kdVal, kiVal) {
    kp = kpVal;
    kd = kdVal;
    ki = kiVal;
    
    switch(selectedWheel) {
      case 1:
        pid_params[0] = kp;
        pid_params[1] = ki;
        pid_params[2] = kd;
        break;
      case 2:
        pid_params[3] = kp;
        pid_params[4] = ki;
        pid_params[5] = kd;
        break;
      case 3:
        pid_params[6] = kp;
        pid_params[7] = ki;
        pid_params[8] = kd;
        break;
      case 4:
        pid_params[9] = kp;
        pid_params[10] = ki;
        pid_params[11] = kd;
        break;
      default:
        pid_params = [kp, ki, kd, kp, ki, kd, kp, ki, kd, kp, ki, kd];
        break;
    }
    
    const pidMessage = new ROSLIB.Message({
      layout: {
        dim: [{
          label: "pid_values",
          size: 12,
          stride: 1
        }],
        data_offset: 0
      },
      data: pid_params
    });
    
    console.log("Publishing PID array:", pid_params);
    PIDPublisher.publish(pidMessage);
  }
  
  function handlePIDChange(event) {
    const { type, value } = event.detail;
    const numValue = parseFloat(value);
    
    if (type === 'kp') kp = numValue;
    else if (type === 'ki') ki = numValue;
    else if (type === 'kd') kd = numValue;
    
    publishPIDForSelectedWheel(kp, kd, ki);
  }
  
  function handleApplyAll() {
    publishPIDForSelectedWheel(kp, kd, ki);
  }
  
  function handleReset() {
    kp = 0;
    ki = 0;
    kd = 0;
    publishPIDForSelectedWheel(0, 0, 0);
  }
  
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();
</script>


<div class="app">
  <!-- Header -->
  <header class="header">
    <div class="logo-section">
      <div class="logo">
        <span class="logo-text">M.I.A</span>
      </div>
      <h1>PID Tuning</h1>
    </div>

    <!-- Wheel Selection and Target Speed Controls -->
    <div class="wheel-controls">
      <div class="dropdown">
        <label for="wheel-select">Select Wheel</label>
        <select 
          id="wheel-select" 
          on:change={handleWheelSelection}
        >
          <option value="0">All wheels</option>
          <option value="1">Wheel 1</option>
          <option value="2">Wheel 2</option>
          <option value="3">Wheel 3</option>
          <option value="4">Wheel 4</option>
        </select>
      </div>
      
    
    </div>
    
    <div class="header-controls">
      <div class="top-controls">
        <!-- Time Window Control -->
        <div class="control-group">
          <label>Time Window (s)</label>
          <input 
            type="number" 
            step="1" 
            min="1" 
            max="60" 
            bind:value={timeWindowSeconds}
            on:change={() => updateTimeWindow(timeWindowSeconds)}
            class="control-input compact"
          />
        </div>
        <div class="target-speed-control">
        <label for="target-speed-input">
          {selectedWheel === 0 ? 'Target Speed (All)' : `Target Speed (Wheel ${selectedWheel})`}
        </label>
        <div class="target-input-group">
          <input 
            id="target-speed-input"
            type="number" 
            step="0.5"
            bind:value={wheelTargetInput}
            class="target-speed-input"
            placeholder="Enter speed"
          />
          <button 
            on:click={setTargetForSelectedWheel}
            class="set-target-btn"
          >
            Set
          </button>
        </div>
      </div>
        
        
      </div>
      <div class="status-indicator {isConnected ? 'connected' : 'disconnected'}">
        <div class="status-dot"></div>
        <span>{isConnected ? 'ROS Connected' : 'ROS Disconnected'}</span>
      </div>
    </div>
  </header>

  <!-- Main Chart Area -->
  <main class="chart-main-area">
    <div class="chart-wrapper">
      <SpeedChart 
        {isConnected}
        {targetSpeed}
        {tolerance}
        {timeWindowSeconds}
        {selectedWheel}
        on:targetchange={handleTargetChange}
        on:tolerancechange={handleToleranceChange}
        on:timewindowchange={handleTimeWindowChange}
      />
    </div>
    
  </main>

  <!-- PID Controls Section at Bottom -->
  <footer class="controls-footer">
    
    <div class="pid-controls-container">
      <PIDPanel 
        {isConnected} 
        {selectedWheel} 
        {kp} 
        {ki}
        {kd}
        on:kpchange={handlePIDChange}
        on:kichange={handlePIDChange}
        on:kdchange={handlePIDChange}
        on:applyall={handleApplyAll}
        on:reset={handleReset}
      />
    </div>
  </footer>
</div>
<style>
  /* Reset and Base */
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  :global(body) {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #000000;
    color: #ffffff;
    height: 100vh;
    overflow: hidden;
  }
  
  /* App Container */
  .app {
    height: 100vh;
    display: flex;
    flex-direction: column;
    padding: 20px;
    gap: 10px;
    overflow: hidden;
    background: linear-gradient(135deg, #0a0a0a 0%, #1a0000 100%);
  }
  
  /* Header - Fixed Height */
  .header {
    flex-shrink: 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 20px;
    border-bottom: 1px solid #450a0a;
    background: linear-gradient(135deg, rgba(20, 0, 0, 0.9) 0%, rgba(40, 0, 0, 0.8) 100%);
    border-radius: 12px;
    padding: 1px;
    border: 1px solid rgba(220, 38, 38, 0.2);
  }
  
  .logo-section {
    display: flex;
    align-items: center;
    gap: 14px;
  }
  
  .logo {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #DC2626;
    font-weight: 600;
    font-size: 18px;
  }
  
  .logo-text {
    background: linear-gradient(135deg, #DC2626, #EF4444);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
  }
  
  h1 {
    font-size: 24px;
    font-weight: 600;
    color: #DC2626;
    text-shadow: 0 2px 4px rgba(220, 38, 38, 0.3);
  }
  .target-speed-control label {
    font-size: 12px;
    font-weight: 500;
    color: #EF4444;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    
  }
  
  .target-input-group {
    display: flex;
    gap: 8px;
  }
  
  .target-speed-input {
    flex: 1;
    padding: 10px 12px;
    background: rgba(69, 10, 10, 0.6);
    border: 1px solid rgba(220, 38, 38, 0.3);
    border-radius: 6px;
    color: #ffffff;
    font-size: 14px;
    width: 100px;
    height: 35px;
  }
  
  .target-speed-input:focus {
    outline: none;
    border-color: #DC2626;
    box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.2);
  }
  
  .set-target-btn {
    padding: 10px 16px;
    background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%);
    border: none;
    border-radius: 6px;
    color: white;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    height: 35px;
  }
  
  .set-target-btn:hover {
    background: linear-gradient(135deg, #B91C1C 0%, #991B1B 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
  }
  
  .header-controls {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 5px;
  }
  
  .top-controls {
    display: flex;
    gap: 16px;
    align-items: flex-end;
    flex-wrap: wrap;
  }
  .dropdown {
  position: relative;
  display: inline-block;
}


  .control-group {
    display: flex;
    flex-direction: column;
    
    min-width: 120px;
  }
  
  .control-group label {
    font-size: 12px;
    font-weight: 500;
    color: #EF4444;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  .control-input.compact {
    width: 100%;
    padding: 8px 12px;
    background: rgba(69, 10, 10, 0.6);
    border: 1px solid rgba(220, 38, 38, 0.3);
    border-radius: 6px;
    color: #ffffff;
    font-size: 14px;
  }
  
  .control-input.compact:focus {
    outline: none;
    border-color: #DC2626;
    box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.2);
  }
  
  .status-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 500;
    padding: 6px 12px;
    background: rgba(20, 0, 0, 0.6);
    border-radius: 20px;
    border: 1px solid rgba(220, 38, 38, 0.3);
  }
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  
  .status-indicator.connected .status-dot {
    background: #16A34A;
    box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.2);
  }
  
  .status-indicator.disconnected .status-dot {
    background: #DC2626;
    box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.2);
  }
  
  /* Main Chart Area - Takes Most Space */
  .chart-main-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow: hidden;
    position: relative;
  }
  
  .chart-wrapper {
    flex: 1;
    background: linear-gradient(135deg, rgba(20, 0, 0, 0.9) 0%, rgba(40, 0, 0, 0.8) 100%);
    border-radius: 12px;
    padding: 20px;
    min-height: 0;
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border: 1px solid rgba(220, 38, 38, 0.2);
    box-shadow: 0 4px 20px rgba(220, 38, 38, 0.2);
  }
  
  /* Ensure chart fills container properly */
  :global(.speed-chart-container) {
    flex: 1;
    min-height: 0;
    position: relative;
    width: 100%;
    height: 100%;
  }
  
  :global(.speed-chart-container canvas) {
    position: absolute;
    top: 0;
    left: 0;
    width: 100% !important;
    height: 100% !important;
    display: block;
  }
  
  /* Controls Footer - Fixed Height at Bottom */
  .controls-footer {
    flex-shrink: 0;
    display: grid;
    grid-template-columns: 3fr 2fr;
    gap:30px;
    height: 280px;
    z-index: 2;
  }
  
  .pid-controls-container {
    background: linear-gradient(135deg, rgba(20, 0, 0, 0.9) 0%, rgba(40, 0, 0, 0.8) 100%);
    border-radius: 12px;
    padding: 34px;
    border: 10px solid rgba(220, 38, 38, 0.2);
    width: 1240px;
    box-shadow: 0 4px 20px rgba(220, 38, 38, 0.2);
  }
  
  /* PID Panel Customization */
  :global(.pid-panel) {
    background: transparent;
    border: none;
    padding: 0;
    margin: 0;
  }
  .dropdown {
    display: flex;
    flex-direction: column;
    min-width: 140px;
  }
  
  .dropdown label {
    font-size: 12px;
    font-weight: 500;
    color: #EF4444;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
  }
  
  .dropdown select {
    width: 100%;
    padding: 10px 12px;
    background: rgba(69, 10, 10, 0.6);
    border: 1px solid rgba(220, 38, 38, 0.3);
    border-radius: 6px;
    color: #ffffff;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    appearance: none;
    background-repeat: no-repeat;
    background-position: right 12px center;
    background-size: 12px;
    padding-right: 32px;
  }
  
  .dropdown select:focus {
    outline: none;
    border-color: #DC2626;
    box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.2);
  }
  
  .dropdown select option {
    background: rgba(20, 0, 0, 0.95);
    color: white;
  }
  
  :global(.pid-controls) {
    display: grid;
    left: 200px;
    grid-template-columns: repeat(3,1fr);
    gap: 220px;
    margin-bottom: 3px;
    width: 3px;
  }
  
  :global(.control-group) {
    margin: 0;
  }
  
  :global(.control-group label) {
    color: #EF4444;
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 2px;
    display: block;
  }
  
  :global(.control-input) {
    width: 100;
    padding: 12px 16px;
    background: rgba(69, 10, 10, 0.6);
    border: 1px solid rgba(220, 38, 38, 0.3);
    border-radius: 8px;
    color: #ffffff;
    font-size: 16px;
    font-weight: 500;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
  }
  
  :global(.control-input:focus) {
    outline: none;
    border-color: #DC2626;
    box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.2);
  }
  
  :global(.pid-actions) {
    display: flex;
    gap: 8px;
    width: px;
    
  }
  
  :global(.btn-action) {
    flex: 1;
    padding: 15x 25px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 13x;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  :global(.btn-apply) {
    background: linear-gradient(135deg, #DC2626, #B91C1C);
    color: white;
  }
  
  :global(.btn-apply:hover) {
    background: linear-gradient(135deg, #B91C1C, #991B1B);
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(220, 38, 38, 0.3);
  }
  
  :global(.btn-reset) {
    background: rgba(69, 10, 10, 0.6);
    color: #ffffff;
    border: 1px solid rgba(220, 38, 38, 0.3);
  }
  
  :global(.btn-reset:hover) {
    background: rgba(127, 29, 29, 0.8);
    transform: translateY(-2px);
  }
  
  /* Responsive Design */
  @media (max-width: 1200px) {
    .controls-footer {
      grid-template-columns: 1fr;
      height: auto;
      gap: 11px;
    }
    
    .pid-controls-container {
      height: 320px;
    }
  }
  
  @media (max-width: 768px) {
    .app {
      padding: 16px;
      gap: 16px;
    }
    
    .header {
      flex-direction: column;
      align-items: stretch;
      gap: 12px;
      padding-bottom: 16px;
    }
    
    .logo-section {
      justify-content: center;
      text-align: center;
      flex-direction: column;
      gap: 8px;
    }
    
    .header-controls {
      align-items: stretch;
    }
    
    .top-controls {
      flex-wrap: wrap;
      justify-content: center;
      gap: 12px;
    }
    
    .control-input.compact {
      width: 100px;
    }
  
    
    :global(.pid-controls) {
      grid-template-columns: 1fr;
      gap: 16px;
    }
    
    :global(.pid-actions) {
      flex-direction: column;
    }
    
    .chart-wrapper {
      padding: 16px;
    }
    
    .pid-controls-container {
      padding: 20px;
    }
  }
</style>