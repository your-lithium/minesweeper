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


class CellCollection(RootModel):
    root: dict[str, list[Cell]]


class GameResponse(BaseModel):
    status: str
    cells: CellCollection
