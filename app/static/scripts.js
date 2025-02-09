const websocket = new WebSocket("ws://localhost:8000/ws/play/");
let firstClick = true;

function getGameSettings() {
    let table = document.querySelector("table");
    let rows = parseInt(table.classList.value.match(/rows(\d+)/)[1]);
    let columns = parseInt(table.classList.value.match(/columns(\d+)/)[1]);
    let mines = parseInt(table.classList.value.match(/mines(\d+)/)[1]);

    return { rows, columns, mines };
};

function processCellClick(event) {
    let cell = event.target;
    let row = parseInt(cell.getAttribute("data-row"), 10);
    let column = parseInt(cell.getAttribute("data-column"), 10);
    
    if (firstClick) {
        console.log("Starting the game...")
        let settings = getGameSettings();

        websocket.send(JSON.stringify({
            type: "start",
            start: [row, column],
            mines: settings.mines,
            height: settings.rows,
            width: settings.columns
        }));
        firstClick = false;
    } else {
        websocket.send(JSON.stringify({
            type: "click",
            cell: [row, column]
        }));
    }
};

function processCellDoubleClick(event) {
    let cell = event.target;
    let row = parseInt(cell.getAttribute("data-row"), 10);
    let column = parseInt(cell.getAttribute("data-column"), 10);
    
    websocket.send(JSON.stringify({
        type: "check_neighbours",
        cell: [row, column]
    }));
};

function processCellRightClick(event) {
    event.preventDefault();

    if (!firstClick) {
        let cell = event.target;
        let row = parseInt(cell.getAttribute("data-row"), 10);
        let column = parseInt(cell.getAttribute("data-column"), 10);

        if (cell.classList.contains("closed")) {
            websocket.send(JSON.stringify({
                type: "flag",
                cell: [row, column]
            }));
            cell.classList.remove("closed");
            cell.classList.add("flag");
            cell.removeAttribute("onclick");
        } else if (cell.classList.contains("flag")) {
            websocket.send(JSON.stringify({
                type: "remove_flag",
                cell: [row, column]
            }));
            cell.classList.remove("flag");
            cell.classList.add("closed");
            cell.setAttribute("onclick", "processCellClick(event)");
        };
    };
};

function updateClass(cells, cell_class) {
    cells.forEach(([row, column]) => {
        let cell = document.querySelector(`.cell.closed[data-row="${row}"][data-column="${column}"]`);
        if (cell) {
            cell.classList.remove("closed");
            cell.classList.add(cell_class);
            cell.removeAttribute("onclick");
            cell.removeAttribute("oncontextmenu");
            if (cell_class !== "empty") {
                cell.addEventListener("dblclick", processCellDoubleClick);
            } else {
                cell.disabled = true;
            }
        }
    });
};

function updateBoard(cells) {
    Object.entries(cells).forEach(([cellClass, cellList]) => {
        updateClass(cellList, cellClass);
    });
};

websocket.onmessage = function(event) {
    let message = JSON.parse(event.data);
    console.log("Received result", message);
    
    if (message.status === "game_over") {
        updateBoard(message.cells);
        alert("Game Over!");
        websocket.close(1000, "Game Over");
    } else {
        updateBoard(message.cells);
    }
};
