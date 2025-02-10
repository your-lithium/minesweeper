import random
from collections import defaultdict

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

    def create_field(self, start: Cell, n_mines: int) -> None:
        field_size = self.height * self.width
        if n_mines >= field_size:
            raise Exception

        potential_mine_positions = list(range(field_size))
        forbidden_positions = self.calculate_forbidden_positions(start)
        potential_mine_positions = list(set(potential_mine_positions) - set(forbidden_positions))
        mine_positions = random.choices(potential_mine_positions, k=n_mines)

        mines = [9 if i in mine_positions else 0 for i in range(field_size)]
        for i, cell in enumerate(mines):
            row = i // self.height
            column = i % self.width
            if cell == 9:
                self.mines.add(Cell(row=row, column=column))
                continue

            mine_count = 0
            for change in DIRECTIONS:
                neighbour = Cell(row=row + change[0], column=column + change[1])
                if (
                    neighbour.row < 0
                    or neighbour.row >= self.height
                    or neighbour.column < 0
                    or neighbour.column >= self.width
                ):
                    continue
                if mines[self.calculate_flat_index(neighbour)] == 9:
                    mine_count += 1
            mines[i] = mine_count

        self.field = [mines[row * self.width : (row + 1) * self.width] for row in range(self.height)]  # noqa: E203

    def calculate_forbidden_positions(self, start: Cell) -> list[int]:
        forbidden_positions = [self.calculate_flat_index(start)]

        for change in DIRECTIONS:
            neighbour = Cell(row=start.row + change[0], column=start.column + change[1])
            if (
                neighbour.row < 0
                or neighbour.row >= self.height
                or neighbour.column < 0
                or neighbour.column >= self.width
            ):
                continue

            forbidden_positions.append(self.calculate_flat_index(neighbour))

        return forbidden_positions

    def calculate_flat_index(self, coordinates: Cell) -> int:
        return coordinates.row * self.width + coordinates.column

    def print_field(self) -> None:
        for row in self.field:
            for cell in row:
                if cell == 9:
                    print("¤", end=" ")
                elif cell == 0:
                    print("·", end=" ")
                else:
                    print(cell, end=" ")
            print()

    def check_neighbouring_cells(self, coordinates: Cell) -> GameResponse:
        neighbouring_cells = []
        for change in DIRECTIONS:
            neighbour_cell = Cell(row=coordinates.row + change[0], column=coordinates.column + change[1])
            if (
                neighbour_cell in self.mines
                or neighbour_cell.row < 0
                or neighbour_cell.row >= self.height
                or neighbour_cell.column < 0
                or neighbour_cell.column >= self.width
            ):
                continue

            neighbour_check = self.check_cell(neighbour_cell)
            if neighbour_check["status"] == "game_over":
                return neighbour_check
            neighbouring_cells.append(neighbour_check["cells"])

        merged_cells: dict[str, str | dict[str, list[Cell]]] = {}
        for d in neighbouring_cells:
            for key, value in d.items():
                if key in merged_cells:
                    merged_cells[key] += value
                else:
                    merged_cells[key] = value

        result = GameResponse(status="okay", cells=merged_cells)
        return result.model_dump()

    def check_cell(self, coordinates: Cell) -> GameResponse:
        cell_value = self.field[coordinates.row][coordinates.column]

        if cell_value == 9:
            response = GameResponse(status="game_over", cells={"oops": [coordinates], "mine": list(self.mines)})
        elif cell_value > 0:
            self.opened.add(coordinates)
            response = GameResponse(
                status="okay",
                cells={
                    f"open{cell_value}": [coordinates],
                },
            )
        else:
            opened_area = self.get_neighbouring_cells(coordinates)
            self.opened.update(coordinates for cell_type in opened_area.values() for coordinates in cell_type)
            response = GameResponse(status="okay", cells=opened_area)

        return response.model_dump()

    def get_neighbouring_cells(
        self,
        coordinates: Cell,
        visited: set[Cell] | None = None,
        collected: CellCollection | defaultdict[str, list[Cell]] | None = None,
    ) -> CellCollection | defaultdict[str, list[Cell]]:
        if visited is None:
            visited = set()
        if collected is None:
            collected = defaultdict(list)

        if coordinates in visited:
            return collected

        if (
            coordinates.row < 0
            or coordinates.row >= self.height
            or coordinates.column < 0
            or coordinates.column >= self.width
        ):
            return collected

        visited.add(coordinates)

        value = self.field[coordinates.row][coordinates.column]
        if value > 0:
            collected[f"open{value}"].append(coordinates)
            return collected

        collected["empty"].append(coordinates)

        for change in DIRECTIONS:
            neighbour = Cell(row=coordinates.row + change[0], column=coordinates.column + change[1])
            self.get_neighbouring_cells(neighbour, visited, collected)

        return collected

    def flag_cell(self, coordinates: Cell, remove_flag: bool = False) -> None:
        if remove_flag:
            self.flagged.discard(coordinates)
        else:
            self.flagged.add(coordinates)

    def check_win(self) -> bool:
        if len(self.mines) + len(self.opened) == self.width * self.height and self.mines.isdisjoint(self.opened):
            return True
        return False


if __name__ == "__main__":
    field_service = FieldService(start=Cell(row=1, column=0))
    field_service.print_field()
