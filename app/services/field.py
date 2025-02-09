import random

from collections import defaultdict


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
        
        self.mines = set()
        self.field = []
        self.create_field(start, mines)
        
        self.opened = {start}
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
                self.mines.add((row, column))
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
    
    def check_neighbouring_cells(self, coordinates: tuple[int, int]) -> dict[str, str | dict[str, list[tuple[int, int]]]]:
        neighbouring_cells = []
        for change in DIRECTIONS:
            row, column = coordinates[0] + change[0], coordinates[1] + change[1]
            neighbour_coordinates = (row, column)
            if neighbour_coordinates in self.mines or row < 0 or row >= self.height or column < 0 or column >= self.width:
                continue
            
            neighbour = self.check_cell(neighbour_coordinates)
            if neighbour["status"] == "game_over":
                return neighbour
            neighbouring_cells.append(neighbour["cells"])
        
        merged_cells = {}
        for d in neighbouring_cells:
            for key, value in d.items():
                if key in merged_cells:
                    merged_cells[key] += value
                else:
                    merged_cells[key] = value
        
        return {
            "status": "okay",
            "cells": merged_cells
        }            
    
    def check_cell(self, coordinates: tuple[int, int]) -> dict[str, str | dict[str, list[tuple[int, int]]]]:
        cell = self.field[coordinates[0]][coordinates[1]]
        if cell == 9:
            return {
                "status": "game_over",
                "cells": {
                    "oops": [coordinates],
                    "mine": list(self.mines)
                }
            }
        
        if cell > 0:
            self.opened.add(coordinates)
            return {
                "status": "okay",
                "cells": {
                    f"open{cell}": [coordinates],
                }
            }
        
        opened_area = self.get_neighbouring_cells(coordinates)
        self.opened.update(coordinates for cell_type in opened_area.values() for coordinates in cell_type)
        return {
                "status": "okay",
                "cells": opened_area
            }

    def get_neighbouring_cells(
        self,
        coordinates: tuple[int, int],
        visited: set | None = None,
        collected: dict[str, list[tuple[int, int]]] | None = None
    ) -> dict[str, list[tuple[int, int]]]:
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
    
    def check_win(self) -> bool:
        if len(self.mines) + len(self.opened) == self.width * self.height and self.mines.isdisjoint(self.opened):
            return True
        return False
            

if __name__ == "__main__":
    field_service = FieldService(start=(1, 0))
    field_service.print_field()
