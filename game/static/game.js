// Ensure DOM is fully loaded before running script
document.addEventListener('DOMContentLoaded', () => {
    const gridElement = document.getElementById('grid');
    let socket; // WebSocket connection
    const gridSize = 20; // Default grid size (can be adjusted)

    // --- Initialize Grid ---
    function initializeGrid() {
        gridElement.innerHTML = ''; // Clear previous grid
        gridElement.style.setProperty('--grid-size', gridSize); // Set CSS variable for grid dimensions
        gridElement.style.gridTemplateColumns = `repeat(${gridSize}, 25px)`; // Set grid columns
        gridElement.style.gridTemplateRows = `repeat(${gridSize}, 25px)`;    // Set grid rows

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
        console.log("Grid initialized with size:", gridSize);
    }

    // --- Toggle Cell State ---
    function toggleCell(cell) {
        const row = cell.dataset.row;
        const col = cell.dataset.col;
        const isAlive = cell.classList.toggle('alive');
        console.log(`Cell [${row}, ${col}] toggled. Now: ${isAlive ? 'Alive' : 'Dead'}`);

        // Send the state change to the server via WebSocket
        if (socket && socket.readyState === WebSocket.OPEN) {
             console.log("Sending state change:", { row, col, state: isAlive });
             socket.send(JSON.stringify({
                 action: 'toggle_cell',
                 row: parseInt(row),
                 col: parseInt(col),
                 state: isAlive
             }));
        } else {
             console.warn("WebSocket not connected. Cannot send toggle state.");
        }
    }

    // --- Update Grid from Server Data ---
    function updateGridFromServer(newGrid) {
         console.log("Received grid update from server:", newGrid);
         const cells = gridElement.querySelectorAll('.cell');
         cells.forEach(cell => {
             const row = parseInt(cell.dataset.row);
             const col = parseInt(cell.dataset.col);
             if (newGrid[row] && newGrid[row][col]) {
                 cell.classList.add('alive');
             } else {
                 cell.classList.remove('alive');
             }
         });
         console.log("Grid display updated based on server data.");
    }

    // --- Setup WebSocket Connection ---
    function setupWebSocket() {
        // Construct WebSocket URL dynamically
        const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsURL = wsProtocol + window.location.host + '/ws/game/'; // Ensure this matches your routing.py

        console.log("Attempting to connect WebSocket to:", wsURL);
        socket = new WebSocket(wsURL);

        socket.onopen = () => {
            console.log("WebSocket connection established.");
            // Request initial grid state upon connection
            if (socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({ action: 'get_initial_state' }));
                console.log("Requested initial grid state from server.");
            }
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("WebSocket message received:", data);

                if (data.type === 'grid_update' && data.grid) {
                    updateGridFromServer(data.grid);
                } else if (data.type === 'initial_state' && data.grid) {
                    console.log("Received initial state.");
                    updateGridFromServer(data.grid); // Update grid with initial state
                } else if (data.type === 'error') {
                    console.error("Server error:", data.message);
                    alert(`Server error: ${data.message}`);
                } else if (data.type === 'connection_established') { // Handle specific message type
                    console.log("Server confirmed connection.");
                } else {
                    console.warn("Received unknown message type or format:", data);
                }
            } catch (error) {
                console.error("Error parsing WebSocket message:", error);
                console.error("Received data:", event.data); // Log the raw data
            }
        };

        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
            alert("WebSocket connection error. Please check the server and console.");
        };

        socket.onclose = (event) => {
            console.log("WebSocket connection closed.", event.code, event.reason);
            // Optional: Attempt to reconnect or notify user
            // alert("WebSocket connection closed. You might need to refresh the page.");
        };
    }

    // --- Add Listeners for Control Buttons ---
    function setupControlButtons() {
        const buttons = {
            'start-button': 'start_simulation',
            'stop-button': 'stop_simulation',
            'clear-button': 'clear_grid'
        };

        function sendControlAction(action) {
             if (socket && socket.readyState === WebSocket.OPEN) {
                console.log(`Sending action: ${action}`);
                socket.send(JSON.stringify({ action: action }));
            } else {
                console.warn("WebSocket not connected. Cannot send action:", action);
                alert("Not connected to game server.");
            }
        }

        // Add listeners ONLY if control buttons exist
        for (const [buttonId, action] of Object.entries(buttons)) {
            const btn = document.getElementById(buttonId);
            if (btn) { // <<<--- CHECK IF BUTTON EXISTS
                // Remove previous listener if any, to prevent duplicates
                // A safer approach is to ensure setupControlButtons is called only once, or use named functions/flags
                // Check if listener already exists (simple flag method)
                if (!btn.hasAttribute('data-listener-added')) {
                    btn.addEventListener('click', () => sendControlAction(action));
                    btn.setAttribute('data-listener-added', 'true'); // Mark as added
                }
            } else {
                // Button not found (likely non-admin user), no warning needed here
                // console.warn(`Button with ID ${buttonId} not found.`);
            }
        }
    }


    // --- Main Initialization ---
    initializeGrid();     // Setup the visual grid first
    setupWebSocket();     // Establish WebSocket connection
    setupControlButtons();// Setup listeners for buttons (if they exist)

}); // End of DOMContentLoaded