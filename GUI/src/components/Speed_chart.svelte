<script>
  import { onMount, onDestroy } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  import { ros, speedSubscriber, targetSubscriber, targetPublisher } from "../lib/ROS";
  import ROSLIB from 'roslib';
  
  export let timeWindowSeconds = 15;
  export let targetSpeed = [10, 10, 10, 10]; // Array of 4 values
  export let tolerance = 1;
  export let isConnected = false;
  export let connectionStatus = 'Initializing...';
  export let errorMessage = '';
  export let isChartPaused = false; 
  export let selectedWheel=0;
  
  // UI input for single value
  let targetInput = 10;
  
  // Chart data
  let chart;
  let chartCanvas;
  let speedListener;
  let targetListener;
  let speedData1 = [];
  let speedData2 = [];
  let speedData3 = [];
  let speedData4 = [];
  let currentSpeeds = [0, 0, 0, 0];
  let timeLabels = [];
  let startTime = Date.now() / 1000;
  let firstMessageTime = null;
  let dataPoints = 0;
  let lastMessageTime = null;
  
  // Pause timing variables
  let pauseStartTime = null;
  let totalPauseDuration = 0;

  // Y-axis min/max values
  let yAxisMin = 0;
  let yAxisMax = 20;

  // Register Chart.js
  Chart.register(...registerables);
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  onMount(() => {
    console.log('Component mounted - initializing chart');
    initializeChart();
    setupROSConnection();
  });

  onDestroy(() => {
    console.log('Component destroying - cleaning up');
    if (speedListener) {
      speedSubscriber.unsubscribe(speedListener);
    }
    if (targetListener) {
      targetSubscriber.unsubscribe(targetListener);
    }
  });
  
  // Update targetInput when targetSpeed prop changes
  $: {
    if (targetSpeed && Array.isArray(targetSpeed) && targetSpeed.length === 4) {
      targetInput = targetSpeed[0]; // Use first value for input
    }
  }
  
  // Watch for chart pause changes
  $: {
    if (isChartPaused && pauseStartTime === null) {
      // Chart just got paused
      pauseStartTime = Date.now() / 1000;
      console.log('Chart PAUSED at time:', pauseStartTime);
    } else if (!isChartPaused && pauseStartTime !== null) {
      // Chart just got resumed
      const now = Date.now() / 1000;
      const pauseDuration = now - pauseStartTime;
      totalPauseDuration += pauseDuration;
      pauseStartTime = null;
      console.log('Chart RESUMED, pause duration:', pauseDuration, 'total pause:', totalPauseDuration);
    }
  }

  export function updateChartXAxis() {
    if (!chart) return;
    
    if (timeLabels.length === 0) {
      chart.options.scales.x.min = 0;
      chart.options.scales.x.max = timeWindowSeconds;
    } else {
      const currentTime = timeLabels[timeLabels.length - 1];
      
      if (currentTime < timeWindowSeconds) {
        chart.options.scales.x.min = 0;
        chart.options.scales.x.max = timeWindowSeconds;
      } else {
        chart.options.scales.x.min = currentTime - timeWindowSeconds;
        chart.options.scales.x.max = currentTime;
      }
    }
    
    chart.update('none');
  }
  
  export function calculateYAxisBounds() {
    // Get all speed data from all wheels
    const allSpeeds = [];
    
    // Add all data from wheel arrays
    for (let i = 0; i < speedData1.length; i++) {
      if (speedData1[i] !== undefined && !isNaN(speedData1[i])) allSpeeds.push(speedData1[i]);
      if (speedData2[i] !== undefined && !isNaN(speedData2[i])) allSpeeds.push(speedData2[i]);
      if (speedData3[i] !== undefined && !isNaN(speedData3[i])) allSpeeds.push(speedData3[i]);
      if (speedData4[i] !== undefined && !isNaN(speedData4[i])) allSpeeds.push(speedData4[i]);
    }
    
    if (allSpeeds.length === 0) {
      // Use average target speed for bounds
      const avgTarget = targetSpeed.reduce((a, b) => a + b, 0) / targetSpeed.length;
      yAxisMin = 0;
      yAxisMax = Math.max(avgTarget + tolerance + 5, 15);
      return;
    }
    
    const minSpeed = Math.min(...allSpeeds);
    const maxSpeed = Math.max(...allSpeeds);
    
    // Calculate with padding
    yAxisMin = Math.max(0, minSpeed - 5);
    yAxisMax = maxSpeed + 5;
    
    // Ensure there's always some height to the chart
    if (yAxisMax - yAxisMin < 10) {
      const center = (yAxisMax + yAxisMin) / 2;
      yAxisMin = center - 5;
      yAxisMax = center + 5;
    }
    
    // Round to nice numbers
    yAxisMin = Math.floor(yAxisMin);
    yAxisMax = Math.ceil(yAxisMax);
    
    console.log(`Y-axis bounds calculated: min=${yAxisMin}, max=${yAxisMax} from ${allSpeeds.length} data points`);
  }

  export function updateChartYAxis() {
    if (!chart) return;
    
    calculateYAxisBounds();
    
    // Update chart options
    chart.options.scales.y.min = yAxisMin;
    chart.options.scales.y.max = yAxisMax;
    
    // Force update
    chart.update('none');
  }

  function updateWheelVisibility() {
    if (!chart) return;
        const wheelDatasets = chart.data.datasets.slice(0, 4);
    if (selectedWheel === 0) {
      // Show all wheels
      wheelDatasets.forEach((dataset, index) => {
        dataset.hidden = false;
      });
    } else {
      // Show only selected wheel
      wheelDatasets.forEach((dataset, index) => {
        dataset.hidden = (index !== selectedWheel - 1);
      });
    }}

   export function initializeChart() {
    console.log('Initializing chart...');
    try {
      const ctx = chartCanvas.getContext('2d');
     
      const lineColor1 = '#00FFFF'; // Bright Cyan
      const lineColor2 = '#00FF00'; // Bright Lime Green
      const lineColor3 = '#FFFF00'; // Bright Yellow
      const lineColor4 = '#FF00FF'; // Bright Magenta

      chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: timeLabels,
          datasets: [
            {
              label: 'wheel 1',
              data: speedData1,
              borderColor: lineColor1, 
              backgroundColor: 'transparent', 
              tension: 0.3,
              fill: false, 
              pointRadius: 0,
              borderWidth: 3,
              hidden:false
            },
            {
              label: 'wheel 2',
              data: speedData2,
              borderColor: lineColor2,
              backgroundColor: 'transparent',
              tension: 0.3,
              fill: false, 
              pointRadius: 0,
              borderWidth: 3,
              hidden: false
            },
            {
              label: 'wheel 3',
              data: speedData3,
              borderColor: lineColor3,
              backgroundColor: 'transparent',
              tension: 0.3,
              fill: false, 
              pointRadius: 0,
              borderWidth: 3,
              hidden:false
            },
            {
              label: 'wheel 4',
              data: speedData4,
              borderColor: lineColor4,
              backgroundColor: 'transparent',
              tension: 0.3,
              fill: false,
              pointRadius: 0,
              borderWidth: 3,
              hidden:false
            },
            {
              label: 'Upper Bound',
              data: [],
              borderColor: 'rgba(220, 38, 38, 0.8)',
              backgroundColor: 'transparent',
              borderWidth: 2,
              borderDash: [5, 5],
              fill: false,
              pointRadius: 0,
              tension: 0
            },
            {
              label: 'Lower Bound',
              data: [],
              borderColor: 'rgba(239, 68, 68, 0.7)',
              backgroundColor: 'transparent',
              borderWidth: 2,
              borderDash: [5, 5],
              fill: false,
              pointRadius: 0,
              tension: 0
            }
            // Removed the 'Target' dataset but kept all calculations
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: { duration: 0 },
          scales: {
            x: {
              type: 'linear',
              display: true,
              title: { 
                display: true, 
                text: 'Time (seconds)',
                color: '#DC2626',
                font: { size: 14, weight: 'bold' }
              },
              ticks: { 
                callback: value => value.toFixed(1) + 's',
                maxTicksLimit: 10,
                color: '#B91C1C'
              },
              grid: {
                color: 'rgba(220, 38, 38, 0.15)'
              }
            },
            y: {
              type: 'linear',
              display: true,
              title: { 
                display: true, 
                text: 'Speed',
                color: '#DC2626',
                font: { size: 14, weight: 'bold' }
              },
              ticks: { 
                callback: value => value.toFixed(1),
                color: '#B91C1C'
              },
              min: yAxisMin,
              max: yAxisMax,
              grid: {
                color: 'rgba(220, 38, 38, 0.15)'
              }
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'top',
              labels: {
                usePointStyle: true,
                padding: 15,
                font: { size: 12, weight: '500' },
                color: '#DC2626',
                filter: function(legendItem, chartData) {
                  return legendItem.datasetIndex < 4;
                }
              }
            },
            tooltip: {
              mode: 'index',
              intersect: false,
              backgroundColor: 'rgba(0, 0, 0, 0.85)',
              titleColor: '#FCA5A5',
              bodyColor: '#fff',
              borderColor: '#DC2626',
              borderWidth: 1,
              callbacks: {
                label: function(context) {
                  if (context.datasetIndex < 4) {
                    return `${context.dataset.label}: ${context.parsed.y.toFixed(2)}`;
                  } else if (context.datasetIndex === 4) {
                    const avgTarget = targetSpeed.reduce((a, b) => a + b, 0) / targetSpeed.length;
                    return `Upper Bound: ${(avgTarget + tolerance).toFixed(2)}`;
                  } else if (context.datasetIndex === 5) {
                    const avgTarget = targetSpeed.reduce((a, b) => a + b, 0) / targetSpeed.length;
                    return `Lower Bound: ${(avgTarget - tolerance).toFixed(2)}`;
                  }
                  
                }
              }
            }
          },
          interaction: {
            intersect: false,
            mode: 'nearest'
          }
        }
      });
      
      updateBorderLines();
      updateWheelVisibility();
      console.log('Chart initialized successfully');
    } catch (error) {
      console.error('Error initializing chart:', error);
      errorMessage = 'Chart error: ' + error.message;
    }
  }

  function setupROSConnection() {
    console.log('=== DEBUG: setupROSConnection ===');
    console.log('ros object exists?', !!ros);
    
    if (!ros) {
      errorMessage = 'ROS object is undefined';
      console.error(errorMessage);
      return;
    }
    
    console.log('ROS connection status:', ros.isConnected);

    ros.on('connection', () => {
      console.log('Connected to ROS Bridge via shared connection');
      isConnected = true;
      connectionStatus = 'Connected to ROS Bridge';
      startTime = Date.now() / 1000;
      subscribeToTopics();
    });

    ros.on('error', (error) => {
      console.error('ROS connection error:', error);
      isConnected = false;
      connectionStatus = 'Connection error';
      errorMessage = 'ROS error: ' + error;
    });

    ros.on('close', () => {
      console.log('ROS connection closed');
      isConnected = false;
      connectionStatus = 'Disconnected from ROS';
    });

    if (ros.isConnected) {
      console.log('ROS already connected, subscribing immediately');
      isConnected = true;
      connectionStatus = 'Connected to ROS Bridge';
      startTime = Date.now() / 1000;
      subscribeToTopics();
    } else {
      console.log('Waiting for ROS connection...');
      connectionStatus = 'Connecting to ROS Bridge...';
    }
  }

   function updateBorderLines() {
    if (!chart || timeLabels.length === 0) return;
    const avgTarget = targetSpeed.reduce((a, b) => a + b, 0) / targetSpeed.length;
    const upperBoundValue = avgTarget + tolerance;
    const lowerBoundValue = avgTarget - tolerance;
    const upperBoundData = new Array(timeLabels.length).fill(upperBoundValue);
    const lowerBoundData = new Array(timeLabels.length).fill(lowerBoundValue);
    chart.data.datasets[4].data = upperBoundData;
    chart.data.datasets[5].data = lowerBoundData;
  }

  function toggleChartPause() {
    isChartPaused = !isChartPaused;
    console.log(`Chart ${isChartPaused ? 'paused' : 'resumed'}`);
    if (!isChartPaused) {
      if (lastMessageTime) {
        const now = Date.now() / 1000;
        const pauseDuration = now - lastMessageTime;
        if (firstMessageTime) {
          firstMessageTime += pauseDuration;
        }
      }
    }
  }

  function subscribeToTopics() {
    console.log('Subscribing to topics...');
    try {
      speedListener = speedSubscriber.subscribe((message) => {
        if (isChartPaused) {
          console.log('Chart is paused - ignoring new data');
          return;
        }
        if (message.data && Array.isArray(message.data) && message.data.length === 4) {
          currentSpeeds = message.data; 
          const now = Date.now() / 1000;
          lastMessageTime = now;
          if (firstMessageTime === null) {
            firstMessageTime = now;
          }
          
          const elapsedTime = (now - firstMessageTime) - totalPauseDuration;
          speedData1.push(currentSpeeds[0]);
          speedData2.push(currentSpeeds[1]);
          speedData3.push(currentSpeeds[2]);
          speedData4.push(currentSpeeds[3]);
          timeLabels.push(elapsedTime);
          dataPoints++;
          
          
          removeOldDataByTime(elapsedTime);
          updateBorderLines();
          updateChartYAxis(); 
          updateChartXAxis();
          updateWheelVisibility();
          
          if (chart) {
            chart.update('none');
          }
        } else {
          console.warn('Received unexpected data format:', message);
        }
      });
      
      
      targetListener = targetSubscriber.subscribe((message) => {        
        if (message.data && Array.isArray(message.data)) {
          targetSpeed = message.data.map(val => parseFloat(val));
          targetInput = targetSpeed[0];
          updateBorderLines();
          updateChartYAxis(); 
          updateChartXAxis();
          updateWheelVisibility();
          
          if (chart) {
            chart.update('none');
          }
        }
      });   
    } catch (error) {
      console.error('Error subscribing to topics:', error);
      errorMessage = 'Subscription error: ' + error.message;
    }
  }

  function removeOldDataByTime(currentTime) {
    const cutoffTime = currentTime - timeWindowSeconds;
    while (timeLabels.length > 0 && timeLabels[0] < cutoffTime) {
      timeLabels.shift();
      speedData1.shift();
      speedData2.shift();
      speedData3.shift();
      speedData4.shift();
    }
  }

  // Publish target speed as Float32MultiArray
  function publishTargetSpeed(newTargetArray) {
    console.log('DEBUG: Attempting to publish target speed:', newTargetArray);
    
    if (!isConnected) {
      errorMessage = 'Cannot publish: ROS disconnected';
      return false;
    }
    
    if (!targetPublisher) {
      errorMessage = 'Publisher not initialized';
      return false;
    }
    
    try {
      // Create Float32MultiArray message
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
      
      console.log(' Successfully published target speeds to ROS');
      errorMessage = '';
      return true;
      
    } catch (error) {
      console.error(' Error publishing target speed:', error);
      errorMessage = 'Publish error: ' + error.message;
      return false;
    }
  }
  export function updateTimeWindow(seconds) {
    console.log(`Updating time window to ${seconds} seconds`);
    timeWindowSeconds = seconds;
    
    if (timeLabels.length > 0) {
      const currentTime = timeLabels[timeLabels.length - 1];
      removeOldDataByTime(currentTime);
      updateBorderLines();
      updateChartYAxis(); 
      updateChartXAxis();
      updateWheelVisibility();
      
      if (chart) {
        chart.update('none');
      }
    }
    
    dispatch('timewindowchange', { seconds });
  }

  export function updateTargetSpeed(newTarget) {
    console.log('updateTargetSpeed called with:', newTarget);
    
    // Handle both single value and array
    let newTargetArray;
    if (Array.isArray(newTarget)) {
      newTargetArray = newTarget.map(val => parseFloat(val));
    } else {
      const val = parseFloat(newTarget);
      newTargetArray = [val, val, val, val];
    }
    targetInput = newTargetArray[0];
    targetSpeed = newTargetArray;
    
    // Publish to ROS
    if (publishTargetSpeed(newTargetArray)) {
      // Update chart
      updateBorderLines();
      updateChartYAxis();
      updateChartXAxis();
      updateWheelVisibility();
      
      if (chart) {
        chart.update('none');
      }
      
      dispatch('targetchange', { speed: newTargetArray });
    }
  }

  export function updateTolerance(newTolerance) {
    tolerance = parseFloat(newTolerance);
    console.log(`Tolerance set to: ±${tolerance}`);
    
    updateBorderLines();
    updateChartYAxis(); 
    updateChartXAxis();
    updateWheelVisibility();
    if (chart) {
      chart.update('none');
    }
    
    dispatch('tolerancechange', { tolerance });
  }
  
  // React to changes
  $: if (timeWindowSeconds !== undefined && chart) {
    updateTimeWindow(timeWindowSeconds);
  }
  
  $: if (tolerance !== undefined && chart) {
    updateTolerance(tolerance);
  }
</script>

<div class="speed-chart-container">
  {#if errorMessage}
    <div class="error-message">
      <span class="error-icon"></span>
      {errorMessage}
    </div>
  {/if}
  
  <div class="chart-control-buttons">
    <button 
      class="control-button {isChartPaused ? 'resume-button' : 'pause-button'}" 
      on:click={toggleChartPause}>
      {isChartPaused ? '▶ Start Chart' : '⏸ Stop Chart'}
    </button>
    
   
    
    <div class="target-control">
  <button on:click={() => updateTolerance(tolerance)} class="tolerance-button">
    Set Tolerance
  </button>
  <input 
    type="number" 
    step="0.5" 
    min="0" 
    bind:value={tolerance}
    class="target-input"
    placeholder="Tolerance"
  />
</div>
</div>
  
  <div class="chart-wrapper">
    <canvas bind:this={chartCanvas}></canvas>
  </div>
  
  
</div>

<style>
  

  .speed-chart-container {
    width: 100%;
    height: 100%;
    position: relative;
    background: linear-gradient(135deg, rgba(20, 0, 0, 0.9) 0%, rgba(40, 0, 0, 0.8) 100%);
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 4px 20px rgba(220, 38, 38, 0.3);
    border: 1px solid rgba(220, 38, 38, 0.2);
    display: flex;
    flex-direction: column;
  }
  
  .chart-control-buttons {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
    align-items: center;
    flex-wrap: wrap;
  }
  
  .control-button {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    font-weight: 500;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .tolerance-button {
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.4);
}

.tolerance-button:hover {
  background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.5);
}
  
  .pause-button {
    background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%);
    color: white;
    box-shadow: 0 2px 8px rgba(220, 38, 38, 0.4);
  }
  
  .pause-button:hover {
    background: linear-gradient(135deg, #B91C1C 0%, #991B1B 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.5);
  }
  
  .resume-button {
    background: linear-gradient(135deg, #16A34A 0%, #15803D 100%);
    color: white;
    box-shadow: 0 2px 8px rgba(22, 163, 74, 0.4);
  }
  
  .resume-button:hover {
    background: linear-gradient(135deg, #15803D 0%, #166534 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(22, 163, 74, 0.5);
  }
  
  
  .target-control {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-left: auto;
  }
  
  .target-input {
    width: 100px;
    padding: 8px 12px;
    background: rgba(69, 10, 10, 0.6);
    border: 1px solid rgba(220, 38, 38, 0.3);
    border-radius: 6px;
    color: white;
    font-size: 14px;
    text-align: center;
  }
  
  .target-input:focus {
    outline: none;
    border-color: #DC2626;
    box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.2);
  }
  
  .chart-wrapper {
    flex: 1;
    min-height: 0;
    position: relative;
  }
  
  canvas {
    width: 100% !important;
    height: 100% !important;
    display: block;
  }
  
  .error-message {
    background: linear-gradient(135deg, rgba(127, 29, 29, 0.9) 0%, rgba(69, 10, 10, 0.9) 100%);
    color: #FCA5A5;
    padding: 12px 16px;
    border-radius: 6px;
    margin-bottom: 15px;
    border: 1px solid rgba(220, 38, 38, 0.5);
    font-weight: 500;
    box-shadow: 0 2px 8px rgba(127, 29, 29, 0.3);
    display: flex;
    align-items: center;
    gap: 8px;
  }
  

  @media (max-width: 768px) {
    .chart-control-buttons {
      flex-direction: column;
      align-items: stretch;
    }
    
    .target-control {
      margin-left: 0;
      justify-content: center;
    }
    
  }
</style>