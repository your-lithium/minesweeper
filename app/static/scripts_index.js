document.getElementById('rows').addEventListener('input', function() {
    document.getElementById('rowsNumber').value = this.value;
});
document.getElementById('columns').addEventListener('input', function() {
    document.getElementById('columnsNumber').value = this.value;
});
document.getElementById('mines').addEventListener('input', function() {
    document.getElementById('minesNumber').value = this.value;
});

document.getElementById('rowsNumber').addEventListener('input', function() {
    document.getElementById('rows').value = this.value;
});
document.getElementById('columnsNumber').addEventListener('input', function() {
    document.getElementById('columns').value = this.value;
});
document.getElementById('minesNumber').addEventListener('input', function() {
    document.getElementById('mines').value = this.value;
});

document.getElementById('custom').addEventListener('submit', function(event) {
    const rows = parseInt(document.getElementById('rows').value);
    const columns = parseInt(document.getElementById('columns').value);
    const mines = parseInt(document.getElementById('mines').value);

    const totalCells = rows * columns;
    const minMines = Math.floor(totalCells * 0.1);
    const maxMines = Math.floor(totalCells * 0.35);

    if (mines < minMines || mines > maxMines) {
        event.preventDefault();
        alert(`The number of mines must be between ${minMines} and ${maxMines}.`);
    }
});
