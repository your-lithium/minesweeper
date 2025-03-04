import random
from typing import Generator

from app.schemas import Cell, CellCollection, GameResponse

DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]


class FieldService:
    def __init__(
        self,
        start: Cell,
        n_mines: int = 10,
        height: int = 9,
        width: int = 9,
    ) -> None:
        """Initialises the field with the requested parameters.

        Args:
            start (Cell): The cell clicked first.
            n_mines (int, optional): Number of mines in the game. Defaults to 10.
            height (int, optional): Height of the game field. Defaults to 9.
            width (int, optional): Width of the game field. Defaults to 9.
        """
        self.height = height
        self.width = width

        self.mines: set[Cell] = set()
        self.field: list[list[int]] = []
        self.create_field(start, n_mines)

        self.opened: set[Cell] = {start}
        self.flagged: set[Cell] = set()

    def __str__(self) -> str:
        """Used for debugging field creation, prints the field.

        Returns:
            str: The string representation of the field.
        """
        result = ""
        for row in self.field:
            for cell_value in row:
                if cell_value == 9:
                    result += "¤ "
                elif cell_value == 0:
                    result += "· "
                else:
                    result += f"{cell_value} "
            result += "\n"
        return result.strip()

    def calculate_flat_index(self, cell: Cell) -> int:
        """Helper function for calculating one-dimensional (flat) index of a cell from a two-dimensional one.

        Args:
            cell (Cell): The cell (containing its two-dimensional coordinates) to calculate the flat index for.

        Returns:
            int: The flat (one-dimensional) index of the cell.
        """
        return cell.row * self.width + cell.column

    def get_cell_neighbours(self, cell: Cell) -> Generator[Cell, None, None]:
        """Helper function for finding valid neighbours of a cell.

        Args:
            cell (Cell): The cell to find the neighbours for.

        Yields:
            Generator[Cell, None, None]: The valid neighbours of the cell.
        """
        for change in DIRECTIONS:
            neighbour_cell = cell.add(change)
            if not (
                neighbour_cell.row < 0
                or neighbour_cell.row >= self.height
                or neighbour_cell.column < 0
                or neighbour_cell.column >= self.width
            ):
                yield neighbour_cell

    def create_field(self, start: Cell, n_mines: int) -> None:
        """Creates the field — operates on the assumption the starting cell has no mines in or around it.

        Args:
            start (Cell): The empty starting cell.
            n_mines (int): The number of mines to populate the field with.

        Raises:
            ValueError: In case there are too many mined cells (more than 35% of the total amount).
            ValueError: In case there are too little mined cells (less than 10% of the total amount).
        """
        field_size = self.height * self.width
        if n_mines > field_size * 0.35:
            raise ValueError("There should be at most 35% mined cells. Try to go for 20%, it's ideal.")
        elif n_mines < field_size * 0.1:
            raise ValueError("There should be at least 10% mined cells. Try to go for 20%, it's ideal.")

        forbidden_mine_positions = self.calculate_forbidden_mine_positions(start)
        potential_mine_positions = list(set(range(field_size)) - set(forbidden_mine_positions))
        mine_positions = random.sample(potential_mine_positions, k=n_mines)

        flat_field = [9 if i in mine_positions else 0 for i in range(field_size)]
        for i, cell_value in enumerate(flat_field):
            row = i // self.width
            column = i % self.width
            if cell_value == 9:
                self.mines.add(Cell(row=row, column=column))
                continue

            neighbour_mine_count = 0
            cell = Cell(row=row, column=column)
            for neighbour in self.get_cell_neighbours(cell=cell):
                if flat_field[self.calculate_flat_index(neighbour)] == 9:
                    neighbour_mine_count += 1
            flat_field[i] = neighbour_mine_count

        self.field = [flat_field[row * self.width : (row + 1) * self.width] for row in range(self.height)]  # noqa: E203

    def calculate_forbidden_mine_positions(self, start: Cell) -> list[int]:
        """Calculates the positions that can't be mined (those all around the starting cell).

        Args:
            start (Cell): The starting cell.

        Returns:
            list[int]: The positions (flat-indexed) that can't contain mines.
        """
        forbidden_mine_positions = [self.calculate_flat_index(start)]

        for neighbour in self.get_cell_neighbours(cell=start):
            forbidden_mine_positions.append(self.calculate_flat_index(cell=neighbour))

        return forbidden_mine_positions

    def check_cell(self, cell: Cell) -> GameResponse:
        """Check a cell — find out what value it has and how that affects the game as a whole.

        Args:
            cell (Cell): The cell to check.

        Returns:
            GameResponse: The result of a check.
        """
        cell_value = self.field[cell.row][cell.column]

        if cell_value == 9:
            response = GameResponse(status="game_over", cells={"oops": [cell], "mine": list(self.mines)})
        elif cell_value > 0:
            self.opened.add(cell)
            response = GameResponse(
                status="okay",
                cells={
                    f"open{cell_value}": [cell],
                },
            )
        else:
            opened_area = self.flood_neighbouring_cells(cell)
            if opened_area:
                self.opened.update(opened_area.cells)
                response = GameResponse(status="okay", cells=opened_area)

        return response.model_dump()

    def check_neighbouring_cells(self, cell: Cell) -> GameResponse | None:
        """Check neighbours of a cell. A cell can't be checked if there's less flagged
        neighbours compared to the actual cell value.

        Args:
            cell (Cell): The cell whose neighbours to check.

        Returns:
            GameResponse | None: The result of a check or no result if a cell couldn't be checked.
        """
        cell_value = self.field[cell.row][cell.column]
        flagged_neighbours = 0
        neighbouring_cells = []
        failed_neighbour_check = None

        for neighbour in self.get_cell_neighbours(cell=cell):
            if neighbour in self.flagged:
                flagged_neighbours += 1
                continue

            neighbour_check = self.check_cell(cell=neighbour)
            if neighbour_check["status"] == "game_over" and not failed_neighbour_check:
                failed_neighbour_check = neighbour_check
            neighbouring_cells.append(neighbour_check["cells"])

        if flagged_neighbours < cell_value:
            return None
        elif failed_neighbour_check:
            return failed_neighbour_check

        merged_opened_cells: CellCollection | dict[str, list[Cell]] = {}
        for d in neighbouring_cells:
            for key, value in d.items():
                if key in merged_opened_cells:
                    merged_opened_cells[key] += value
                else:
                    merged_opened_cells[key] = value

        result = GameResponse(status="okay", cells=merged_opened_cells)
        return result.model_dump()

    def flood_neighbouring_cells(
        self,
        cell: Cell,
        collected: CellCollection | None = None,
    ) -> CellCollection | None:
        """Performs a recursive flood fill check of the cells, starting from one of them.
        The starting cell is always empty. Stops when finding a non-empty border.

        Args:
            cell (Cell): The cell to check. On the first run, always empty.
            collected (CellCollection | None, optional):
                The cells collected, with their corresponding values.
                Defaults to None on the first run.

        Returns:
            CellCollection | None:
                The resulting cell collection, if all cells have been visited.
                None, if there are still potentially cells to check.
        """
        if collected is None:
            collected = CellCollection()

        if cell in collected.cells:
            return None

        cell_value = self.field[cell.row][cell.column]
        if cell_value > 0:
            collected[f"open{cell_value}"].append(cell)
            return None

        collected["empty"].append(cell)

        for neighbour in self.get_cell_neighbours(cell=cell):
            self.flood_neighbouring_cells(cell=neighbour, collected=collected)

        return collected

    def flag_cell(self, cell: Cell, remove_flag: bool = False) -> None:
        """Flag or unflag a single cell.

        Args:
            cell (Cell): The cell to flag
            remove_flag (bool, optional): Whether to remove the flag or not. Defaults to False.
        """
        if remove_flag:
            self.flagged.discard(cell)
        else:
            self.flagged.add(cell)

    def check_win(self) -> bool:
        """Check if all conditions for winning have been met already.

        Returns:
            bool: Whether all conditions have been met.
        """
        if len(self.mines) + len(self.opened) == self.width * self.height and self.mines.isdisjoint(self.opened):
            return True
        return False


if __name__ == "__main__":
    field_service = FieldService(start=Cell(row=1, column=0))
    print(field_service)
