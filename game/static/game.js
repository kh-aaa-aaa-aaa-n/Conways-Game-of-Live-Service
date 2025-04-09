let socket = null;
let timeoutActive = false;

function connectWebSocket() {
    const wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
    socket = new WebSocket(wsProtocol + window.location.host + "/ws/game/");
    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.action === "update_grid") {
            updateGrid(data.grid);
        }
        
        if (data.type === "error") {
            alert(data.message);
            if (data.message.includes("log in")) {
                window.location.href = "/login/";
            } else if (data.message.includes("wait")) {
                timeoutActive = true;
                disableCellInteractions(true);
            }
        }
        
        if (data.type === "timeout_end") {
            timeoutActive = false;
            disableCellInteractions(false);
        }
    };
    
    socket.onclose = function(event) {
        console.log("Connection closed. Redirecting to login.");
        window.location.href = "/login/";
    };
}

function updateGrid(cells) {
    const cellMap = new Map(cells.map(cell => [`${cell.x},${cell.y}`, cell]));
    document.querySelectorAll(".cell").forEach(cell => {
        const x = cell.dataset.x;
        const y = cell.dataset.y;
        const cellState = cellMap.get(`${x},${y}`);
        if (cellState && cellState.is_alive) {
            cell.classList.add("alive");
        } else {
            cell.classList.remove("alive");
        }
    });
}

// Toggle cell state (alive or dead) when clicked
function toggleCell(x, y, cell) {
    if (timeoutActive) {
        return;
    }

    socket.send(JSON.stringify({
        action: "toggle",
        x: x,
        y: y
    }));
}

// Disable or enable game board
function disableCellInteractions(disable) {
    const cells = document.querySelectorAll(".cell");
    cells.forEach(cell => {
        if (disable) {
            cell.removeEventListener("click", handleCellClick);
        } else {
            cell.addEventListener("click", handleCellClick);
        }
    });
}

function handleCellClick(event) {
    const cell = event.target;
    const x = cell.dataset.x;
    const y = cell.dataset.y;
    toggleCell(x, y, cell);
}

const grid = document.getElementById("grid");
for (let x = 0; x < 50; x++) {
    for (let y = 0; y < 50; y++) {
        const cell = document.createElement("div");
        cell.classList.add("cell");
        cell.dataset.x = x;
        cell.dataset.y = y;
        cell.addEventListener("click", () => toggleCell(x, y, cell));
        grid.appendChild(cell);
    }
}

// Establish WebSocket connection when the page loads
connectWebSocket();
