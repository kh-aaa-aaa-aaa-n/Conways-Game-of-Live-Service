document.addEventListener('DOMContentLoaded', () => {
    // for admins
    const gridElement = document.getElementById('grid');
    const startButton = document.getElementById('start-button'); 
    const stopButton = document.getElementById('stop-button');   
    const clearButton = document.getElementById('clear-button'); 
    const statusDisplay = document.getElementById('simulation-status');

    // Save/Load Elements (may be null for guests)
    const saveNameInput = document.getElementById('save-name-input');
    const saveStateButton = document.getElementById('save-state-button');
    const loadStateSelect = document.getElementById('load-state-select');
    const loadStateButton = document.getElementById('load-state-button');
    const refreshSavesButton = document.getElementById('refresh-saves-button');
    const saveLoadFeedback = document.getElementById('save-load-feedback');

    let socket; // WebSocket connection
    let gridSize = 20; // Default grid size 
    let isSimulationRunning = false; // Track simulation state

    //Grid Functions 
    function initializeGrid() {
        if (!gridElement) {
            console.error("Grid element not found!");
            return;
        }
        gridElement.innerHTML = ''; // Clear previous grid
        gridElement.style.setProperty('--grid-size', gridSize);
        gridElement.style.gridTemplateColumns = `repeat(${gridSize}, 25px)`;
        gridElement.style.gridTemplateRows = `repeat(${gridSize}, 25px)`;

        for (let i = 0; i < gridSize; i++) {
            for (let j = 0; j < gridSize; j++) {
                const cell = document.createElement('div');
                cell.classList.add('cell');
                cell.dataset.row = i;
                cell.dataset.col = j;

                cell.addEventListener('click', () => toggleCell(cell));
                gridElement.appendChild(cell);
            }
        }
        console.log("Grid initialized.");
        updateStatusDisplay(); // Update status on init
    }

    function toggleCell(cell) {
        const row = cell.dataset.row;
        const col = cell.dataset.col;
        const isAlive = cell.classList.toggle('alive'); 
        console.log(`Cell [${row}, ${col}] toggled. Now: ${isAlive ? 'Alive' : 'Dead'}`);

        // Send the state change to the server via WebSocket
        sendWebSocketMessage({
            action: 'toggle_cell',
            row: parseInt(row),
            col: parseInt(col),
            state: isAlive
        });
    }

    function updateGridFromServer(newGrid) {
        if (!gridElement) return;
        console.log("Updating grid from server data...");
        const cells = gridElement.querySelectorAll('.cell');
        cells.forEach(cell => {
            try {
                 const row = parseInt(cell.dataset.row);
                 const col = parseInt(cell.dataset.col);
                 if (newGrid && newGrid[row] && newGrid[row][col] !== undefined) {
                     if (newGrid[row][col]) { // Check for truthy value (e.g., 1)
                         cell.classList.add('alive');
                     } else {
                         cell.classList.remove('alive');
                     }
                 } else {
                     // Handle case where cell data might be missing (e.g., grid resize?)
                     cell.classList.remove('alive'); // Default to dead if unsure
                 }
            } catch (e) {
                 console.error("Error updating cell:", cell.dataset.row, cell.dataset.col, e);
            }

        });
        console.log("Grid display updated.");
    }

    // --- WebSocket Functions ---
    function setupWebSocket() {
        // Ensure only one WebSocket connection is attempted
        if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
             console.log("WebSocket connection already exists or is connecting.");
             return;
        }

        const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsURL = wsProtocol + window.location.host + '/ws/game/'; // Matches routing.py

        console.log("Attempting WebSocket connection to:", wsURL);
        try {
            socket = new WebSocket(wsURL);
        } catch (error) {
             console.error("Failed to create WebSocket:", error);
             showFeedback("Failed to connect to the game server.", true);
             return; // Stop if WebSocket creation fails
        }


        socket.onopen = () => {
            console.log("WebSocket connection established.");
            // Request initial state and saved states list (if applicable)
            sendWebSocketMessage({ action: 'get_initial_state' });
            if (loadStateSelect) { // Check if save/load controls exist (implies user logged in)
                requestSavedStates();
            }
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("WebSocket message received:", data);

                switch (data.type) {
                    case 'grid_update':
                    case 'initial_state':
                        if (data.grid) {
                            updateGridFromServer(data.grid);
                        } else {
                            console.warn("Received grid update/initial state without grid data:", data);
                        }
                        break;
                    case 'connection_established':
                        console.log("Server confirmed connection:", data.message);
                        break;
                    case 'simulation_started':
                        isSimulationRunning = true;
                        updateStatusDisplay();
                        showFeedback("Simulation started.");
                        break;
                    case 'simulation_stopped':
                        isSimulationRunning = false;
                        updateStatusDisplay();
                        showFeedback("Simulation paused.");
                        break;
                     case 'grid_cleared':
                        isSimulationRunning = false; // Clearing implies stopping
                        updateStatusDisplay();
                        showFeedback("Grid reset.");
                        break;
                    case 'saved_states_list':
                        if (data.states) {
                            populateLoadSelect(data.states);
                        }
                        break;
                    case 'save_success':
                        showFeedback(data.message || "State saved successfully.");
                        if (saveNameInput) saveNameInput.value = ''; // Clear input on success
                        break;
                    case 'load_success':
                        showFeedback(data.message || "State loaded successfully.");
                        isSimulationRunning = false; // Loading implies stopping simulation
                        updateStatusDisplay();
                        break;
                    case 'error':
                        console.error("Server error:", data.message);
                        showFeedback(`Error: ${data.message}`, true); // Show error in feedback area
                        break;
                    default:
                        console.warn("Received unknown message type:", data.type, data);
                }
            } catch (error) {
                console.error("Error parsing WebSocket message or processing data:", error);
                console.error("Received data:", event.data);
            }
        };

        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
            showFeedback("WebSocket connection error. Check console.", true);
            isSimulationRunning = false; // Assume simulation stops on error
            updateStatusDisplay();
        };

        socket.onclose = (event) => {
            console.log("WebSocket connection closed.", event.code, event.reason);
            showFeedback(`Connection closed: ${event.reason || 'No reason given'}` , !event.wasClean);
            socket = null; 
            isSimulationRunning = false; 
            updateStatusDisplay();
        };
    }

    function sendWebSocketMessage(message) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            try {
                 socket.send(JSON.stringify(message));
                 console.log("Sent message:", message);
            } catch (error) {
                 console.error("Error sending WebSocket message:", error);
            }

        } else {
            console.warn("WebSocket not connected. Cannot send message:", message);
            showFeedback("Not connected to game server.", true);
        }
    }

    // --- Control Button Functions ---
    function setupControlButtons() {
        // Admin Controls
        if (startButton) {
             startButton.addEventListener('click', () => sendWebSocketMessage({ action: 'start_simulation' }));
        }
        if (stopButton) {
             stopButton.addEventListener('click', () => sendWebSocketMessage({ action: 'stop_simulation' }));
        }
        if (clearButton) {
             clearButton.addEventListener('click', () => sendWebSocketMessage({ action: 'clear_grid' }));
        }

        // Save/Load Controls (check existence as they depend on login)
        if (saveStateButton && saveNameInput) {
            saveStateButton.addEventListener('click', () => {
                const saveName = saveNameInput.value.trim();
                if (!saveName) {
                    showFeedback("Please enter a name for your save.", true);
                    return;
                }
                sendWebSocketMessage({ action: 'save_state', name: saveName });
            });
        }

        if (loadStateButton && loadStateSelect) {
            loadStateButton.addEventListener('click', () => {
                const selectedId = loadStateSelect.value;
                if (!selectedId) {
                    showFeedback("Please select a state to load.", true);
                    return;
                }
                sendWebSocketMessage({ action: 'load_state', save_id: selectedId }); 
            });
        }

        if (refreshSavesButton) {
            refreshSavesButton.addEventListener('click', requestSavedStates);
        }
    }

    function updateStatusDisplay() {
        if (statusDisplay) {
            statusDisplay.textContent = `Status: ${isSimulationRunning ? 'Running' : 'Paused'}`;
            statusDisplay.style.color = isSimulationRunning ? 'green' : 'orange';

            if (startButton) startButton.disabled = isSimulationRunning;
            if (stopButton) stopButton.disabled = !isSimulationRunning;
        }
    }

    function showFeedback(message, isError = false) {
        if (saveLoadFeedback) {
            saveLoadFeedback.textContent = message;
            saveLoadFeedback.className = isError ? 'feedback-error' : 'feedback-success'; 
            setTimeout(() => {
                 if (saveLoadFeedback.textContent === message) {
                      saveLoadFeedback.textContent = '';
                      saveLoadFeedback.className = '';
                 }
            }, 5000); 
        } else {
             console.log(`Feedback (${isError ? 'Error' : 'Info'}): ${message}`);
        }
    }

    function requestSavedStates() {
        if (loadStateSelect) {
             console.log("Requesting saved states list...");
             sendWebSocketMessage({ action: 'get_saved_states' });
        }
    }

    function populateLoadSelect(states) {
        if (!loadStateSelect) return; 

        const previouslySelected = loadStateSelect.value;

        while (loadStateSelect.options.length > 1) {
            loadStateSelect.remove(1);
        }

        if (states && Array.isArray(states)) {
             states.forEach(state => {
                 if (state.id && state.name) { 
                     const option = document.createElement('option');
                     option.value = state.id;
                     option.textContent = state.name; 
                     loadStateSelect.appendChild(option);
                 }
             });
        } else {
             console.warn("Received invalid or empty states list:", states);
        }


        if (previouslySelected) {
            loadStateSelect.value = previouslySelected;
        }
    }


    initializeGrid(); 
    setupWebSocket(); 
    setupControlButtons(); 

}); 