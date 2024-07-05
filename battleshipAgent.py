from aima.logic import PropDefiniteKB, expr, pl_fc_entails
import random

class BattleshipAgent:
    def __init__(self, size):
        self.size = size  # Grid size
        self.kb = PropDefiniteKB()  # Knowledge base
        self.hits = []  # List of successfully hit boxes
        self.misses = []  # List of boxes hit unsuccessfully
        self.knowledge_base_definition()

    def knowledge_base_definition(self):
        '''
        Defines the agent's knowledge base by codifying game rules and strategies
        '''
        # H = Hit  M = Miss  S = Sunk  
        #                                                                                                          M M    M H M
        # Handle case where there are two adjacent hits, on the flanks of the two hits will be two misses (e.g.:   H H    M H M )
        #                                                                                                          M M  
                                                                                          
        for x in range(self.size):
            for y in range(self.size):
                if 0 < x < self.size and 0 < y < self.size:
                    # Handles a miss in the upper left corner in case of two adjacent horizontal misses
                    self.kb.tell(expr(f"(Hit_({x + 1}, {y}) & Hit_({x + 1}, {y + 1}))==>Miss_({x}, {y})"))
                    # Handles a miss in the upper right corner in case of two adjacent horizontal misses
                    self.kb.tell(expr(f"(Hit_({x + 1}, {y}) & Hit_({x + 1}, {y - 1}))==>Miss_({x}, {y})"))
                    # Handles a miss in the lower right corner in case of two adjacent horizontal misses
                    self.kb.tell(expr(f"(Hit_({x - 1}, {y}) & Hit_({x - 1}, {y - 1}))==>Miss_({x}, {y})"))
                    # Handles a miss in the lower left corner in case of two adjacent horizontal misses
                    self.kb.tell(expr(f"(Hit_({x - 1}, {y}) & Hit_({x - 1}, {y + 1}))==>Miss_({x}, {y})"))
                    # Handles a miss in the upper left corner in case of two adjacent vertical misses
                    self.kb.tell(expr(f"(Hit_({x}, {y + 1}) & Hit_({x + 1}, {y + 1}))==>Miss_({x}, {y})"))
                    # Handles a miss in the upper right corner in case of two adjacent vertical misses
                    self.kb.tell(expr(f"(Hit_({x}, {y - 1}) & Hit_({x + 1}, {y - 1}))==>Miss_({x}, {y})"))
                    # Handles a miss in the lower right corner in case of two adjacent vertical misses
                    self.kb.tell(expr(f"(Hit_({x}, {y - 1}) & Hit_({x - 1}, {y - 1}))==>Miss_({x}, {y})"))
                    # Handles a miss in the lower left corner in case of two adjacent vertical misses
                    self.kb.tell(expr(f"(Hit_({x}, {y + 1}) & Hit_({x - 1}, {y + 1}))==>Miss_({x}, {y})"))

        # Handle previous case in the corners of the grid
        self.kb.tell(expr(f"(Hit_(0, 0) & Hit_(0, 1))==>Miss_(1, 0)"))
        self.kb.tell(expr(f"(Hit_(0, 0) & Hit_(1, 0))==>Miss_(0, 1)"))
        self.kb.tell(expr(f"(Hit_(0, 9) & Hit_(0, 8))==>Miss_(1, 9)"))
        self.kb.tell(expr(f"(Hit_(0, 9) & Hit_(1, 9))==>Miss_(0, 8)"))
        self.kb.tell(expr(f"(Hit_(9, 0) & Hit_(9, 1))==>Miss_(8, 0)"))
        self.kb.tell(expr(f"(Hit_(9, 0) & Hit_(8, 0))==>Miss_(9, 1)"))
        self.kb.tell(expr(f"(Hit_(9, 9) & Hit_(9, 8))==>Miss_(8, 9)"))
        self.kb.tell(expr(f"(Hit_(9, 9) & Hit_(8, 9))==>Miss_(9, 8)"))

        # Case when there are one hit and three adjacent misses (edges of the grid are excluded)
        for x in range(1, self.size - 1):
            for y in range(1, self.size - 1):
                self.kb.tell(expr(f"(Hit_({x}, {y}) & Miss_({x}, {y - 1}) & Miss_({x - 1}, {y}) & Miss_({x + 1}, {y}))==>Hit_({x}, {y + 1})"))
                self.kb.tell(expr(f"(Hit_({x}, {y}) & Miss_({x}, {y + 1}) & Miss_({x + 1}, {y}) & Miss_({x - 1}, {y}))==>Hit_({x}, {y - 1})"))
                self.kb.tell(expr(f"(Hit_({x}, {y}) & Miss_({x - 1}, {y}) & Miss_({x}, {y - 1}) & Miss_({x}, {y + 1}))==>Hit_({x + 1}, {y})"))
                self.kb.tell(expr(f"(Hit_({x}, {y}) & Miss_({x + 1}, {y}) & Miss_({x}, {y - 1}) & Miss_({x}, {y + 1}))==>Hit_({x - 1}, {y})"))

        # Case when there are one hit and two adjacent misses, on the left and right edge of the grid (corners of the grid are excluded)
        for x in range(1, self.size - 1):
            self.kb.tell(expr(f"(Hit_({x}, 0) & Miss_({x - 1}, 0) & Miss_({x + 1}, 0))==>Hit_({x}, 1)"))
            self.kb.tell(expr(f"(Hit_({x}, 0) & Miss_({x}, 1) & Miss_({x + 1}, 0))==>Hit_({x - 1}, 0)"))
            self.kb.tell(expr(f"(Hit_({x}, 0) & Miss_({x}, 1) & Miss_({x - 1}, 0))==>Hit_({x + 1}, 0)"))
            self.kb.tell(expr(f"(Hit_({x}, 9) & Miss_({x - 1}, 9) & Miss_({x + 1}, 9))==>Hit_({x}, 8)"))
            self.kb.tell(expr(f"(Hit_({x}, 9) & Miss_({x}, 8) & Miss_({x + 1}, 9))==>Hit_({x - 1}, 9)"))
            self.kb.tell(expr(f"(Hit_({x}, 9) & Miss_({x}, 8) & Miss_({x - 1}, 9))==>Hit_({x + 1}, 9)"))

        # Case when there are one hit and two adjacent misses, on the lowest and highest edge of the grid (corners of the grid are excluded)
        for y in range(1, self.size - 1):
            self.kb.tell(expr(f"(Hit_(0, {y}) & Miss_(0, {y - 1}) & Miss_(0, {y + 1}))==>Hit_(1, {y})"))
            self.kb.tell(expr(f"(Hit_(0, {y}) & Miss_(1, {y}) & Miss_(0, {y + 1}))==>Hit_(1, {y - 1})"))
            self.kb.tell(expr(f"(Hit_(0, {y}) & Miss_(1, {y}) & Miss_(0, {y - 1}))==>Hit_(1, {y + 1})"))
            self.kb.tell(expr(f"(Hit_(9, {y}) & Miss_(9, {y - 1}) & Miss_(9, {y + 1}))==>Hit_(1, {y})"))
            self.kb.tell(expr(f"(Hit_(9, {y}) & Miss_(8, {y}) & Miss_(9, {y + 1}))==>Hit_(9, {y - 1})"))
            self.kb.tell(expr(f"(Hit_(9, {y}) & Miss_(8, {y}) & Miss_(9, {y - 1}))==>Hit_(9, {y + 1})"))

        # Case which involve corners of the grid (G[0][0], G[0][N], G[M][0] and G[M][N])
        self.kb.tell(expr(f"(Hit_(0, 0) & Miss_(0, 1))==>Hit_(1, 0)"))
        self.kb.tell(expr(f"(Hit_(0, 0) & Miss_(1, 0))==>Hit_(0, 1)"))
        self.kb.tell(expr(f"(Hit_(9, 0) & Miss_(8, 0))==>Hit_(9, 1)"))
        self.kb.tell(expr(f"(Hit_(9, 0) & Miss_(9, 1))==>Hit_(8, 0)"))
        self.kb.tell(expr(f"(Hit_(0, 9) & Miss_(0, 8))==>Hit_(1, 9)"))
        self.kb.tell(expr(f"(Hit_(0, 9) & Miss_(1, 9))==>Hit_(0, 8)"))
        self.kb.tell(expr(f"(Hit_(9, 9) & Miss_(8, 9))==>Hit_(9, 8)"))
        self.kb.tell(expr(f"(Hit_(9, 9) & Miss_(9, 8))==>Hit_(8, 9)"))

        #                    |M|
        # Hendles cases as: M| |M in the central cell there is a miss to infer
        #                    |M|
        for x in range(self.size):
            for y in range(self.size):
                if 0 < x < self.size and 0 < y < self.size and 0 < x < self.size and 0 < y < self.size:
                    self.kb.tell(expr(f"(Miss_({x - 1}, {y}) & Miss_({x + 1}, {y}) & Miss_({x}, {y - 1}) & Miss_({x}, {y + 1}))==>Miss_({x}, {y})"))

    def add_knowledge(self, cell, result):
        """Adds knowledge to KB based on stroke result"""
        if result == "hit":
            self.hits.append(cell)
            self.kb.tell(expr(f"Hit_{cell}"))
        elif result == "miss":
            self.misses.append(cell)
            self.kb.tell(expr(f"Miss_{cell}"))
        else:
            self.kb.tell(expr(f"Sunk_{cell}"))

    def get_adjacent_cells(self, cell):
        """Returns the boxes adjacent to a given cell"""
        x, y = cell
        adjacent = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
        return [(i, j) for i, j in adjacent if 0 <= i < self.size and 0 <= j < self.size]
    
    def check_globally(self):
        for x in range(self.size):
            for y in range(self.size):
                cell = (x, y)
                if cell not in self.hits and cell not in self.misses:
                    if pl_fc_entails(self.kb, expr(f"Hit_{cell}")):
                        print(f"\033[32mInferred ({chr(65 + x)}, {y}) as hit\033[0m")
                        return cell
                    if pl_fc_entails(self.kb, expr(f"Miss_{cell}")):
                        print(f"\033[32mInferred ({chr(65 + x)}, {y}) as miss\033[0m")
                        self.add_knowledge(cell, "miss")
        return()

    def choose_next_move(self):
        """Chooses the next move based on current knowledge base"""
        for cell in self.hits:
            for adj in self.get_adjacent_cells(cell):
                if adj not in self.hits and adj not in self.misses:
                    if pl_fc_entails(self.kb, expr(f"Miss_{adj}")):
                        print(f"\033[32mInferred ({chr(65 + adj[0])}, {adj[1]}) as miss\033[0m")
                        self.add_knowledge(adj, "miss")
                    else:
                        return adj
                
        # If there are no recent hits, choose a random cell
        while True:
            move = (random.randint(0, self.size-1), random.randint(0, self.size-1))
            if move not in self.hits and move not in self.misses:
                return move