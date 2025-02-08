const websocket = new WebSocket("ws://localhost:8000/ws/play/");
let firstClick = true;

function getGameSettings() {
    let table = document.querySelector("table");
    let rows = parseInt(table.classList.value.match(/rows(\d+)/)[1]);
    let columns = parseInt(table.classList.value.match(/columns(\d+)/)[1]);
    let mines = parseInt(table.classList.value.match(/mines(\d+)/)[1]);

    return { rows, columns, mines };
};

function processCell(event) {
    let cell = event.target;
    let row = parseInt(cell.classList[2].replace("row", ""));
    let column = parseInt(cell.classList[3].replace("column", ""));
    
    if (firstClick) {
        console.log("Starting the game...")
        let settings = getGameSettings();

        websocket.send(JSON.stringify({
            start: [row, column],
            mines: settings.mines,
            height: settings.rows,
            width: settings.columns
        }));
        firstClick = false;
    } else {
        websocket.send(JSON.stringify([row, column]));
    }
};

function updateClass(cells, cell_class) {
    cells.forEach(([row, column]) => {
        let cell = document.querySelector(`.cell.closed.row${row}.column${column}`);
        if (cell) {
            cell.classList.remove("closed");
            cell.classList.add(cell_class);
            cell.disabled = true;
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
