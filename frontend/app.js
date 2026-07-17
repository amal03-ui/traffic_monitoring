// Global variables
let updateTimer = null;
let lastUpdateTime = 0;
let countdownInterval = null;
const updateInterval = 1000; // Update every 1 second to catch yellow phase
const serverUrl = 'http://127.0.0.1:5000/backend';

// Function to update traffic signals based on camera images
function updateSignals(forceUpdate = false) {
    console.log("Starting updateSignals...", { forceUpdate });
    const northFile = document.getElementById('northFile')?.files[0];
    const southFile = document.getElementById('southFile')?.files[0];
    const westFile = document.getElementById('westFile')?.files[0];
    const eastFile = document.getElementById('eastFile')?.files[0];

    const formData = new FormData();
    if (northFile) formData.append('north', northFile);
    if (southFile) formData.append('south', southFile);
    if (westFile) formData.append('west', westFile);
    if (eastFile) formData.append('east', eastFile);

    showLoading(true);

    console.log(`Sending fetch request to ${serverUrl}/process...`);
    fetch(`${serverUrl}/process`, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin'
    })
    .then(response => {
        console.log(`Response status: ${response.status}`);
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Received response:", data);
        processServerResponse(data);
        
        lastUpdateTime = Date.now();
        showLoading(false);
        updateConnectionStatus(true);
        
        if (document.getElementById('auto-update')?.checked) {
            startAutoUpdate();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showLoading(false);
        showError(error.message);
        updateConnectionStatus(false);
    });
}

// Show or hide loading indicator
function showLoading(show) {
    const loadingElement = document.getElementById('loading');
    const errorElement = document.getElementById('error-message');
    if (loadingElement) loadingElement.style.display = show ? 'block' : 'none';
    if (errorElement) errorElement.style.display = 'none';
}

// Show error message
function showError(message) {
    const loadingElement = document.getElementById('loading');
    const errorElement = document.getElementById('error-message');
    if (loadingElement) loadingElement.style.display = 'none';
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
}

// Update connection status display
function updateConnectionStatus(connected) {
    const statusElem = document.getElementById('connection-status');
    if (statusElem) {
        statusElem.textContent = connected ? 'Connected' : 'Disconnected';
        statusElem.className = connected ? 'connected' : 'disconnected';
        console.log(`Connection status updated to: ${statusElem.textContent}`);
    }
}

// Process server response and update UI
function processServerResponse(data) {
    const signals = data.traffic_signals || {};
    console.log("Processing signals:", signals);
    
    Object.keys(signals).forEach(direction => {
        updateTrafficLight(direction, signals[direction]);
    });
    
    if (data.vehicle_counts) {
        Object.keys(data.vehicle_counts).forEach(direction => {
            const countElement = document.getElementById(`${direction}Count`);
            if (countElement) {
                countElement.textContent = data.vehicle_counts[direction];
            }
        });
    }
    
    if (data.timing_info) {
        const remainingTime = Math.round(data.timing_info.remaining_time || 0);
        startTimerCountdown(remainingTime, data.timing_info.current_green);
        updateVisitedStatus(data.timing_info.visited_roads);
        highlightCurrentGreen(data.timing_info.current_green);
    }
}

// Update traffic light display
function updateTrafficLight(direction, signal) {
    console.log(`Updating ${direction} to ${signal}`);
    const redLight = document.getElementById(`${direction}-red`);
    const yellowLight = document.getElementById(`${direction}-yellow`);
    const greenLight = document.getElementById(`${direction}-green`);
    const statusElement = document.getElementById(`${direction}-status`);

    if (!redLight || !yellowLight || !greenLight) {
        console.error(`Light elements not found for ${direction}`);
        return;
    }

    // Reset all lights to base class
    [redLight, yellowLight, greenLight].forEach(light => {
        light.className = 'light';
    });

    // Reset status text
    if (statusElement) {
        statusElement.textContent = '';
        statusElement.className = 'status';
    }

    // If signal is empty (neutral state), do not set any light or status
    if (!signal) {
        console.log(`No signal state for ${direction}, keeping lights off`);
        return;
    }

    // Apply the active signal
    const lightElement = document.getElementById(`${direction}-${signal}`);
    if (lightElement) {
        lightElement.className = `light ${signal} active`;
        console.log(`Activated ${direction}-${signal}, classes: ${lightElement.className}`);
    } else {
        console.error(`Light element not found for ${direction}-${signal}`);
    }
    
    if (statusElement) {
        statusElement.textContent = signal === 'green' ? 'GO' : signal === 'yellow' ? 'WAIT' : 'STOP';
        statusElement.className = 'status ' + signal;
    }
}

// Update visited status indicators
function updateVisitedStatus(visitedRoads) {
    document.querySelectorAll('.visited-indicator').forEach(element => {
        element.classList.remove('visited');
    });
    
    if (Array.isArray(visitedRoads)) {
        visitedRoads.forEach(direction => {
            const indicator = document.getElementById(`${direction}-visited`);
            if (indicator) indicator.classList.add('visited');
        });
    }
}

// Highlight the current green road
function highlightCurrentGreen(currentGreen) {
    console.log(`Highlighting current green: ${currentGreen}`);
    document.querySelectorAll('.traffic-signal').forEach(element => {
        element.classList.remove('current-green');
    });
    
    if (currentGreen) {
        const greenSignal = Array.from(document.querySelectorAll('.traffic-signal'))
            .find(signal => signal.querySelector('h2')?.textContent.trim().toLowerCase() === currentGreen.toLowerCase());
        if (greenSignal) {
            greenSignal.classList.add('current-green');
            console.log(`Highlighted ${currentGreen} as current green`);
        } else {
            console.warn(`No traffic signal found for direction: ${currentGreen}`);
        }
    }
}

// Timer countdown functionality
function startTimerCountdown(startTime, currentGreen) {
    if (countdownInterval) {
        clearInterval(countdownInterval);
        countdownInterval = null;
    }
    
    document.querySelectorAll('.timer').forEach(timer => {
        timer.style.display = 'none';
    });
    
    if (!currentGreen) {
        console.warn("No current green road specified for timer");
        return;
    }

    const timerElement = document.querySelector(`#${currentGreen}-timer #timer`);
    const timerContainer = document.getElementById(`${currentGreen}-timer`);
    if (timerElement && timerContainer) {
        timerElement.textContent = startTime;
        timerContainer.style.display = 'block';
    } else {
        console.warn(`Timer element not found for direction: ${currentGreen}`);
        return;
    }
    
    countdownInterval = setInterval(() => {
        let currentTime = parseInt(timerElement.textContent || 0);
        if (currentTime > 0) {
            timerElement.textContent = currentTime - 1;
        } else {
            clearInterval(countdownInterval);
            countdownInterval = null;
            if (document.getElementById('auto-update')?.checked) {
                console.log("Timer expired, forcing update");
                updateSignals(true);
            }
        }
    }, 1000);
}

// Auto-update functionality
function startAutoUpdate() {
    if (updateTimer) {
        clearInterval(updateTimer);
        updateTimer = null;
    }
    
    const intervalInput = document.getElementById('update-interval');
    const interval = (parseInt(intervalInput?.value) || 5) * 1000; // Default to 5 seconds if invalid
    console.log(`Starting auto-update with interval: ${interval}ms`);
    updateTimer = setInterval(() => {
        if (document.getElementById('auto-update')?.checked) {
            console.log("Auto-update triggered");
            updateSignals();
        } else {
            clearInterval(updateTimer);
            updateTimer = null;
            console.log("Auto-update disabled");
        }
    }, interval);
}

// Toggle auto-update functionality
function toggleAutoUpdate() {
    const autoUpdateCheckbox = document.getElementById('auto-update');
    if (autoUpdateCheckbox?.checked) {
        startAutoUpdate();
    } else if (updateTimer) {
        clearInterval(updateTimer);
        updateTimer = null;
        console.log("Auto-update stopped");
    }
}

// Test server connection
function testServerConnection() {
    showLoading(true);
    console.log(`Testing server connection at ${serverUrl}/test`);
    
    fetch(`${serverUrl}/test`, {
        method: 'GET'
    })
    .then(response => {
        if (!response.ok) throw new Error(`Server responded with status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log("Server test response:", data);
        showLoading(false);
        updateConnectionStatus(true);
    })
    .catch(error => {
        console.error('Connection error:', error);
        showLoading(false);
        showError(`Server connection failed: ${error.message}`);
        updateConnectionStatus(false);
    });
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const autoUpdateCheckbox = document.getElementById('auto-update');
    const processButton = document.getElementById('process-images');
    if (autoUpdateCheckbox) {
        autoUpdateCheckbox.addEventListener('change', toggleAutoUpdate);
    }
    if (processButton) {
        processButton.addEventListener('click', updateSignals);
    }
    setTimeout(testServerConnection, 1000);
});