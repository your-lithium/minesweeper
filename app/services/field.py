import random
from collections import defaultdict
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
        self.height = height
        self.width = width

        self.mines: set[Cell] = set()
        self.field: list[list[int]] = []
        self.create_field(start, n_mines)

        self.opened: set[Cell] = {start}
        self.flagged: set[Cell] = set()

    def __str__(self):
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
        return cell.row * self.width + cell.column

    def get_cell_neighbours(self, cell: Cell) -> Generator[Cell, None, None]:
        for change in DIRECTIONS:
            neighbour_cell = cell.add(change)
            if (
                neighbour_cell.row < 0
                or neighbour_cell.row >= self.height
                or neighbour_cell.column < 0
                or neighbour_cell.column >= self.width
            ):
                continue
            yield neighbour_cell

    def create_field(self, start: Cell, n_mines: int) -> None:
        field_size = self.height * self.width
        if n_mines >= field_size:
            raise ValueError("There can't be as many mines as cells in a game")

        forbidden_mine_positions = self.calculate_forbidden_mine_positions(start)
        potential_mine_positions = list(set(range(field_size)) - set(forbidden_mine_positions))
        mine_positions = random.choices(potential_mine_positions, k=n_mines)

        flat_field = [9 if i in mine_positions else 0 for i in range(field_size)]
        for i, cell_value in enumerate(flat_field):
            row = i // self.height
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
        forbidden_mine_positions = [self.calculate_flat_index(start)]

        for neighbour in self.get_cell_neighbours(cell=start):
            forbidden_mine_positions.append(self.calculate_flat_index(cell=neighbour))

        return forbidden_mine_positions

    def check_cell(self, cell: Cell) -> GameResponse:
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
            opened_area = self.get_neighbouring_cells(cell)
            self.opened.update(coordinates for cell_type in opened_area.values() for coordinates in cell_type)
            response = GameResponse(status="okay", cells=opened_area)

        return response.model_dump()

    def check_neighbouring_cells(self, cell: Cell) -> GameResponse:
        neighbouring_cells = []
        for neighbour in self.get_cell_neighbours(cell=cell):
            if neighbour in self.flagged:
                continue

            neighbour_check = self.check_cell(cell=neighbour)
            if neighbour_check["status"] == "game_over":
                return neighbour_check
            neighbouring_cells.append(neighbour_check["cells"])

        merged_opened_cells: CellCollection | dict[str, list[Cell]] = {}
        for d in neighbouring_cells:
            for key, value in d.items():
                if key in merged_opened_cells:
                    merged_opened_cells[key] += value
                else:
                    merged_opened_cells[key] = value

        result = GameResponse(status="okay", cells=merged_opened_cells)
        return result.model_dump()

    def get_neighbouring_cells(
        self,
        cell: Cell,
        visited: set[Cell] | None = None,
        collected: CellCollection | defaultdict[str, list[Cell]] | None = None,
    ) -> CellCollection | defaultdict[str, list[Cell]]:
        if visited is None:
            visited = set()
        if collected is None:
            collected = defaultdict(list)

        if cell in visited:
            return collected

        visited.add(cell)

        cell_value = self.field[cell.row][cell.column]
        if cell_value > 0:
            collected[f"open{cell_value}"].append(cell)
            return collected

        collected["empty"].append(cell)

        for neighbour in self.get_cell_neighbours(cell=cell):
            self.get_neighbouring_cells(cell=neighbour, visited=visited, collected=collected)

        return collected

    def flag_cell(self, cell: Cell, remove_flag: bool = False) -> None:
        if remove_flag:
            self.flagged.discard(cell)
        else:
            self.flagged.add(cell)

    def check_win(self) -> bool:
        if len(self.mines) + len(self.opened) == self.width * self.height and self.mines.isdisjoint(self.opened):
            return True
        return False


if __name__ == "__main__":
    field_service = FieldService(start=Cell(row=1, column=0))
    print(field_service)
