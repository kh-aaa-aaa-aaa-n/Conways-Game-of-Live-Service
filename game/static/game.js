let socket = null;

function connectWebSocket() {
    socket = new WebSocket("ws://" + window.location.host + "/ws/game/");
    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.action === "update_grid") {
            updateGrid(data.grid);
        }
    };
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
    socket.send(JSON.stringify({
        action: "toggle",
        x: x,
        y: y
    }));
}

// Start the game simulation loop
function startGame() {
    socket.send(JSON.stringify({
        action: "start_game"
    }));
}

// Establish WebSocket connection when the page loads
connectWebSocket();
