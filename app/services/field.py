import json
import random

from collections import defaultdict

from loguru import logger


DIRECTIONS = [
    (-1, 0), (1, 0), (0, -1), (0, 1),
    (-1, -1), (-1, 1), (1, -1), (1, 1)
]


class FieldService():
    def __init__(
        self,
        start: tuple[int, int],
        mines: int = 10,
        height: int = 9,
        width: int = 9,
    ) -> None:
        self.height = height
        self.width = width
        self.mines = []
        self.create_field(start, mines)
        self.opened = [start]
        self.flagged = set()

    def create_field(self, start: tuple[int, int], mines: int) -> None:
        field_size = self.height * self.width
        if mines >= field_size:
            raise Exception
        
        potential_mine_positions = range(field_size)
        forbidden_positions = self.calculate_forbidden_positions(start)
        potential_mine_positions = list(set(potential_mine_positions) - set(forbidden_positions))
        mine_positions = random.choices(potential_mine_positions, k=mines)
        
        mines = [9 if i in mine_positions else 0 for i, _ in enumerate(range(field_size))]
        for i, cell in enumerate(mines):
            row = i // self.height
            column = i % self.width
            if cell == 9:
                self.mines.append((row, column))
                continue
            
            mine_count = 0
            for change in DIRECTIONS:
                neighbour_row, neighbour_column = (row + change[0], column + change[1])
                if neighbour_row < 0 or neighbour_row >= self.height or neighbour_column < 0 or neighbour_column >= self.width:
                    continue
                if mines[self.calculate_flat_index((neighbour_row, neighbour_column))] == 9:
                    mine_count += 1   
            mines[i] = mine_count
        
        self.field = [mines[row * self.width : (row + 1) * self.width] for row in range(self.height)]
    
    def calculate_forbidden_positions(self, start: tuple[int, int]) -> list[tuple[int, int]]:
        forbidden_positions = [self.calculate_flat_index(start)]
        
        for change in DIRECTIONS:
            row, column = start[0] + change[0], start[1] + change[1]
            if row < 0 or row >= self.height or column < 0 or column >= self.width:
                continue
            
            forbidden_positions.append(self.calculate_flat_index((row, column)))
        
        return forbidden_positions
    
    def calculate_flat_index(self, coordinates: tuple[int, int]) -> int:
        return coordinates[0] * self.width + coordinates[1]

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
    
    def check_cell(self, coordinates: tuple[int, int]) -> str:
        cell = self.field[coordinates[0]][coordinates[1]]
        if cell == 9:
            return json.dumps({
                "status": "game_over",
                "cells": {
                    "oops": [coordinates],
                    "mine": self.mines
                }
            })
        
        if cell > 0:
            return json.dumps({
                "status": "okay",
                "cells": {
                    f"open{cell}": [coordinates],
                }
            })
        
        return json.dumps({
                "status": "okay",
                "cells": self.get_neighbouring_cells(coordinates)
            })

    def get_neighbouring_cells(self, coordinates: tuple[int, int], visited: set | None = None, collected: dict[str, list[tuple[int, int]]] | None = None) -> dict[str, list[tuple[int, int]]]:
        if visited is None:
            visited = set()
        if collected is None:
            collected = defaultdict(list)
        
        if coordinates in visited:
            return collected

        row, column = coordinates
        if row < 0 or row >= self.height or column < 0 or column >= self.width:
            return collected

        visited.add(coordinates)
        
        value = self.field[row][column]
        if value > 0:
            collected[f"open{value}"].append(coordinates)
            return collected
        
        collected["empty"].append(coordinates)

        for change in DIRECTIONS:
            neighbor = (row + change[0], column + change[1])
            self.get_neighbouring_cells(neighbor, visited, collected)

        return collected
    
    def flag_cell(self, coordinates: tuple[int, int], remove_flag: bool = False) -> None:
        if remove_flag:
            self.flagged.discard(coordinates)
        else:
            self.flagged.add(coordinates)
        logger.debug(f"Flagged cells are now: {self.flagged}")
            

if __name__ == "__main__":
    field_service = FieldService(start=(1, 0))
    field_service.print_field()
