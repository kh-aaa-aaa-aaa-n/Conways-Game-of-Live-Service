document.addEventListener('DOMContentLoaded', function() {
    const gridContainer = document.getElementById('grid');
    const rows = 50; // Grid dimensions
    const cols = 50;

    let socket = null;
    let timeoutActive = false; // To handle potential move timeouts from backend

    if (!gridContainer) {
        console.error("Grid container ('#grid') not found!");
        return;
    }

    // --- WebSocket Connection ---
    function connectWebSocket() {
        // Use ws:// locally, wss:// if served over https
        const wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
        // Ensure the path matches game/routing.py
        const wsURL = wsProtocol + window.location.host + "/ws/game/";
        console.log("Connecting to WebSocket:", wsURL);

        socket = new WebSocket(wsURL);

        socket.onopen = function(e) {
            console.log("WebSocket connection established");
            // Optional: Request initial state from server?
            // socket.send(JSON.stringify({ action: "get_initial_state" }));
        };

        socket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            console.log("WebSocket message received:", data);

            if (data.action === "update_grid") {
                updateGridFromServer(data.grid);
            }

            if (data.type === "error") {
                alert("Error: " + data.message); // Show backend errors
                if (data.message.includes("log in")) {
                    // Redirect if backend indicates login is required
                    window.location.href = "{% url 'game:login' %}"; 
                                                                    
                } else if (data.message.includes("wait")) {
                    console.warn("Timeout active, interactions disabled.");
                    timeoutActive = true;
                    // Optional: Visually indicate timeout (e.g., disable buttons)
                }
            }

            if (data.type === "timeout_end") {
                console.log("Timeout ended, interactions enabled.");
                timeoutActive = false;
                 // Optional: Re-enable buttons etc.
            }
            // Add handlers for other potential message types from backend
        };

        socket.onclose = function(event) {
            console.warn("WebSocket connection closed:", event);
            // Avoid immediate redirect to prevent loops if connection fails instantly
            // Maybe show a message or attempt reconnect with delay
            alert("WebSocket connection lost. Please refresh or log in again.");
            // Consider redirecting only if close code indicates authentication issue
            // if (event.code === YOUR_AUTH_ERROR_CODE) {
            //    window.location.href = "{% url 'game:login' %}";
            // }
        };

        socket.onerror = function(error) {
            console.error("WebSocket Error:", error);
            alert("Failed to connect to the game server. Please check your connection and refresh.");
        };
    }

    // --- Update Grid Based on Server Data ---
    function updateGridFromServer(serverCells) {
        // Assume serverCells is an array ]
        // Or potentially a simpler format depending on your consumer
        const cellMap = new Map(serverCells.map(cell => [`${cell.x},${cell.y}`, cell.is_alive]));

        document.querySelectorAll(".cell").forEach(cell => {
            const x = cell.dataset.x;
            const y = cell.dataset.y;
            const isAlive = cellMap.get(`${x},${y}`); // Check if this cell is in the map and alive

            if (isAlive) { // Check for true, not just existence
                cell.classList.add("alive");
            } else {
                cell.classList.remove("alive");
            }
        });
        // console.log("Grid updated from server data.");
    }

    // --- Handle Clicking a Cell ---
    function handleCellClick(event) {
        if (timeoutActive) {
            console.log("Timeout active, move ignored.");
            return; // Ignore clicks if timeout is active
        }

        const cell = event.target;
        if (cell.classList.contains('cell') && cell.dataset.x && cell.dataset.y) {
            const x = parseInt(cell.dataset.x, 10);
            const y = parseInt(cell.dataset.y, 10);

            // Send toggle request via WebSocket if connected
            if (socket && socket.readyState === WebSocket.OPEN) {
                console.log(`Sending toggle for cell (${x}, ${y})`);
                socket.send(JSON.stringify({
                    action: "toggle", // Ensure consumer expects this action
                    x: x,
                    y: y
                }));
                 // Optional: Optimistic UI update (toggle locally immediately)
                 // cell.classList.toggle('alive');
                 // Note: Server response should confirm the actual state via updateGridFromServer
            } else {
                console.warn("WebSocket not connected. Cannot toggle cell.");
                alert("Not connected to game server. Please refresh.");
            }
        }
    }


    // --- Create the Visual Grid Structure ---
    function createVisualGrid() {
        gridContainer.innerHTML = ''; // Clear previous grid
        gridContainer.style.setProperty('--grid-rows', rows);
        gridContainer.style.setProperty('--grid-cols', cols);

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                const cell = document.createElement('div');
                cell.classList.add('cell');
                // Add data attributes for coordinates, essential for click handler
                cell.dataset.x = c; // x corresponds to column
                cell.dataset.y = r; // y corresponds to row
                gridContainer.appendChild(cell);
            }
        }
        console.log(`Created visual grid (${rows}x${cols}).`);
        // Add the single event listener to the container (event delegation)
        gridContainer.addEventListener('click', handleCellClick);
        console.log("Click listener added to grid container.");
    }

    // --- Add Listeners for Control Buttons ---
    document.getElementById('start-button')?.addEventListener('click', () => {
        console.log("Start button clicked (functionality not implemented)");
        // TODO: Send 'start' command if needed by backend logic
        // if (socket && socket.readyState === WebSocket.OPEN) { socket.send(JSON.stringify({ action: "start_simulation" })); }
    });

     document.getElementById('stop-button')?.addEventListener('click', () => {
        console.log("Stop button clicked (functionality not implemented)");
         // TODO: Send 'stop' command via WebSocket if needed
         // if (socket && socket.readyState === WebSocket.OPEN) { socket.send(JSON.stringify({ action: "stop_simulation" })); }
    });

     document.getElementById('clear-button')?.addEventListener('click', () => {
        console.log("Clear button clicked (functionality not implemented)");
         // TODO: Send 'clear' command via WebSocket
         // if (socket && socket.readyState === WebSocket.OPEN) { socket.send(JSON.stringify({ action: "clear_grid" })); }
         // TODO: Optionally clear grid visually immediately
         // document.querySelectorAll(".cell").forEach(cell => cell.classList.remove("alive"));
    });


    // --- Initialize ---
    createVisualGrid(); // Build the grid structure
    connectWebSocket(); // Connect to the server

}); // End of DOMContentLoaded