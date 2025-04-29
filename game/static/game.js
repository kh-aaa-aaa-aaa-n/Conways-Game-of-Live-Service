document.addEventListener('DOMContentLoaded', function() {
    const gridContainer = document.getElementById('grid');
    const rows = 50; // Grid dimensions
    const cols = 50;

    let socket = null;
    let timeoutActive = false;

    // --- WebSocket Connection ---
    function connectWebSocket() {
        const wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
        const wsURL = wsProtocol + window.location.host + "/ws/game/";
        console.log("Connecting to WebSocket:", wsURL);

        socket = new WebSocket(wsURL);

        socket.onopen = function(e) {
            console.log("WebSocket connection established");
            // socket.send(JSON.stringify({ action: "get_initial_state" }));
        };

        socket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            // console.log("WebSocket message received:", data); // Less verbose logging

            if (data.action === "update_grid") {
                updateGridFromServer(data.grid);
            } else if (data.type === "error") {
                console.error("Backend Error:", data.message);
                // Consider using a custom, styled modal for errors instead of alert
                alert("Error: " + data.message);
                if (data.message.includes("wait")) {
                    timeoutActive = true;
                }
            } else if (data.type === "timeout_end") {
                console.log("Timeout ended, interactions enabled.");
                timeoutActive = false;
            }
            // Handle other message types if needed
        };

        socket.onclose = function(event) {
            console.warn("WebSocket connection closed:", event);
            if (!event.wasClean) {
                 alert("WebSocket connection lost. Please refresh the page.");
            }
        };

        socket.onerror = function(error) {
            console.error("WebSocket Error:", error);
            alert("Failed to connect to the game server. Please check your connection and refresh.");
        };
    }

    // --- Update Grid Based on Server Data ---
    function updateGridFromServer(serverCells) {
        if (!Array.isArray(serverCells)) {
            console.error("Invalid grid data received:", serverCells);
            return;
        }
        const cellMap = new Map(serverCells.map(cell => [`${cell.x},${cell.y}`, cell.is_alive]));
        document.querySelectorAll(".cell").forEach(cell => {
            const isAlive = cellMap.get(`${cell.dataset.x},${cell.dataset.y}`);
            cell.classList.toggle("alive", isAlive === true);
        });
        // console.log("Grid updated from server data."); // Less verbose logging
    }

    // --- Handle Clicking a Cell ---
    function handleCellClick(event) {
        if (timeoutActive) {
            console.log("Timeout active, move ignored.");
            return;
        }
        const cell = event.target;
        if (cell.classList.contains('cell') && cell.dataset.x != null && cell.dataset.y != null) {
            const x = parseInt(cell.dataset.x, 10);
            const y = parseInt(cell.dataset.y, 10);
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({ action: "toggle_cell", x: x, y: y }));
            } else {
                console.warn("WebSocket not connected. Cannot toggle cell.");
                alert("Not connected to game server.");
            }
        }
    }

    // --- Create the Visual Grid Structure ---
    function createVisualGrid() {
        if (!gridContainer) { console.error("Grid container not found!"); return; }
        gridContainer.innerHTML = '';
        gridContainer.style.setProperty('--grid-rows', rows);
        gridContainer.style.setProperty('--grid-cols', cols);
        gridContainer.style.gridTemplateColumns = `repeat(${cols}, auto)`;
        gridContainer.style.gridTemplateRows = `repeat(${rows}, auto)`;

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                const cell = document.createElement('div');
                cell.classList.add('cell');
                cell.dataset.x = c;
                cell.dataset.y = r;
                gridContainer.appendChild(cell);
            }
        }
        // Ensure listener is added only once
        if (!gridContainer.hasAttribute('listener-added')) {
             gridContainer.addEventListener('click', handleCellClick);
             gridContainer.setAttribute('listener-added', 'true');
        }
        console.log(`Created visual grid (${rows}x${cols}).`);
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

        for (const [buttonId, action] of Object.entries(buttons)) {
            const btn = document.getElementById(buttonId);
            if (btn) {
                btn.addEventListener('click', () => sendControlAction(action));
            }
        }
    }

    // --- Modal Control Logic ---
    const purposeModal = document.getElementById('purpose-modal');
    const rulesModal = document.getElementById('rules-modal');
    const modalBackdrop = document.getElementById('modal-backdrop');
    const purposeBtn = document.getElementById('purpose-btn');
    const rulesBtn = document.getElementById('rules-btn');
    const closeBtns = document.querySelectorAll('.modal-close-btn');

    function openModal(modal) {
        if (modal) {
            modal.classList.add('modal-open');
            modalBackdrop.classList.add('modal-open');
            document.body.classList.add('modal-active'); // <<< ADD THIS CLASS TO BODY
        }
    }

    function closeModal(modal) {
        if (modal) {
            modal.classList.remove('modal-open');
            const anyModalOpen = document.querySelector('.modal.modal-open');
            if (!anyModalOpen) {
                 modalBackdrop.classList.remove('modal-open');
                 document.body.classList.remove('modal-active'); // <<< REMOVE THIS CLASS FROM BODY
            }
        }
    }

    if (purposeBtn && purposeModal) {
        purposeBtn.addEventListener('click', (e) => { e.stopPropagation(); openModal(purposeModal); });
    }
    if (rulesBtn && rulesModal) {
        rulesBtn.addEventListener('click', (e) => { e.stopPropagation(); openModal(rulesModal); });
    }
    closeBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const modalId = btn.getAttribute('data-modal-id');
            closeModal(document.getElementById(modalId));
        });
    });
    if (modalBackdrop) {
        modalBackdrop.addEventListener('click', () => {
             closeModal(document.querySelector('.modal.modal-open'));
        });
    }
     document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeModal(document.querySelector('.modal.modal-open'));
        }
    });
    // --- End Modal Control Logic ---


    // --- Initialize ---
    createVisualGrid();
    setupControlButtons();
    connectWebSocket();

}); // End of DOMContentLoaded wrapper