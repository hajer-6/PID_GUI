<!-- PIDPanel.svelte -->
<script>
  import { ros, kdPublisher, kiPublisher, kpPublisher, PIDPublisher } from "../lib/ROS";
  import ROSLIB from 'roslib';

  export let kp = 0;
  export let ki = 0;
  export let kd = 0;
  export let isConnected = false;
  export let logMessages = [];
  export let selectedWheel=0;



  
  export function publishPID() {
    try {
      
      const multiArrayMsg = new ROSLIB.Message({
        layout: {
          dim: [
            {
              label: "pid_values",
              size: 12,
              stride: 1
            }
          ],
          data_offset: 0
        },
        data: [kp, ki, kd, kp, ki, kd, kp, ki, kd, kp, ki, kd]
      });
      
      PIDPublisher.publish(multiArrayMsg);
    } catch (error) {
      logMessages.push(`Error publishing PID: ${error.message}`);
    }
  }

  export function resetPID() {
    kp = 0;
    ki = 0;
    kd = 0;
    logMessages.push('PID values reset to 0');
    
    publishPID()
  }

  // Custom event dispatchers
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

   function handleInputChange(type, value) {
    const numValue = parseFloat(value);
    
    // Update local value
    if (type === 'kp') kp = numValue;
    else if (type === 'ki') ki = numValue;
    else if (type === 'kd') kd = numValue;
    
    // Dispatch event to parent
    dispatch(type + 'change', { 
      type: type,
      value: numValue
    });
  }

  function handleApplyAll() {
    dispatch('applyall');
    handleInputChange('kp', kp);
    handleInputChange('ki', ki);
    handleInputChange('kd', kd);
  }

  function handleReset() {
    // Reset local values
    kp = 0;
    ki = 0;
    kd = 0;
    
    // Dispatch event to parent
    dispatch('reset');
  }
</script>

<div class="pid-panel">
  <div class="panel-header">
    <div class="status-indicator">
      <div class="status-dot {isConnected ? 'connected' : 'disconnected'}"></div>
      <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
    </div>

  </div>

  <div class="pid-controls">
    <div class="control-row">
      <div class="control-group">
        <label for="kp">Kp</label>
        <input 
          id="kp" 
          type="number" 
          step="0.01" 
          bind:value={kp}
          class="control-input">
        
      </div>
    </div>
    
    <div class="control-row">
      <div class="control-group">
        <label for="ki">Ki </label>
        <input 
          id="ki" 
          type="number" 
          step="0.01" 
          bind:value={ki}
          class="control-input">
        
      </div>
    </div>
    
    <div class="control-row">
      <div class="control-group">
        <label for="kd">Kd </label>
        <input 
          id="kd" 
          type="number" 
          step="0.01" 
          bind:value={kd}
          class="control-input">
       
      </div>
    </div>
  </div>

  <div class="pid-actions">
    <button on:click={handleApplyAll} class="btn-action btn-apply">
      
      Apply to {selectedWheel === 0 ? 'All Wheels' : `Wheel ${selectedWheel}`}
    </button>
    
    <button on:click={handleReset} class="btn-action btn-reset">
      Reset {selectedWheel === 0 ? 'All' : `Wheel ${selectedWheel}`}
    </button>
  </div>
  
 
</div>