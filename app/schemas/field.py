from typing import Sequence

from pydantic import BaseModel, ConfigDict, RootModel


class Cell(BaseModel):
    row: int
    column: int

    model_config = ConfigDict(frozen=True)

    @classmethod
    def from_sequence(cls, data: Sequence[int]):
        if len(data) != 2:
            raise ValueError(f"Expected a sequence of length 2, but got {len(data)}")
        return cls(row=data[0], column=data[1])

    def add(self, other: tuple[int, int]) -> "Cell":
        return Cell(row=self.row + other[0], column=self.column + other[1])


class CellCollection(RootModel):
    root: dict[str, list[Cell]] = {}

    @property
    def cells(self) -> list[Cell]:
        return [cell for cell_type in self.root.values() for cell in cell_type]

    def __getitem__(self, key: str) -> list[Cell]:
        if key not in self.root:
            self.root[key] = []
        return self.root[key]

    def __setitem__(self, key: str, value: list[Cell]):
        self.root[key] = value


class GameResponse(BaseModel):
    status: str
    cells: CellCollection
