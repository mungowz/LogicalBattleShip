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

        U = Unknown  H = Hit  M = Miss  S = Sunk  E = Empty                                                   
                                                                                                                 M M    M H M
        Handle case where I have two adjacent hits, on the flanks of the two hits I will have two misses (e.g.:  H H    M H M )
                                                                                                                 M M  
        '''                                                                                                        
        for x in range(self.size):
            for y in range(self.size):
                '''Handles a miss in the upper left corner in case of two adjacent horizontal misses'''
                if  x + 1 >= 0 and x + 1 < self.size and y + 1 >= 0 and y + 1 < self.size:
                    self.kb.tell(expr(f"(Hit_({x + 1}, {y}) & Hit_({x + 1}, {y + 1}))==>Miss_({x}, {y})"))
                '''Handles a miss in the upper right corner in case of two adjacent horizontal misses'''
                if  x + 1 >= 0 and x + 1 < self.size and y - 1 >= 0 and y - 1 < self.size:
                    self.kb.tell(expr(f"(Hit_({x + 1}, {y}) & Hit_({x + 1}, {y - 1}))==>Miss_({x}, {y})"))
                '''Handles a miss in the lower right corner in case of two adjacent horizontal misses'''
                if  x - 1 >= 0 and x - 1 < self.size and y - 1 >= 0 and y - 1 < self.size:
                    self.kb.tell(expr(f"(Hit_({x - 1}, {y}) & Hit_({x - 1}, {y - 1}))==>Miss_({x}, {y})"))
                '''Handles a miss in the lower left corner in case of two adjacent horizontal misses'''
                if  x - 1 >= 0 and x - 1 < self.size and y + 1 >= 0 and y + 1 < self.size:
                    self.kb.tell(expr(f"(Hit_({x - 1}, {y}) & Hit_({x - 1}, {y + 1}))==>Miss_({x}, {y})"))
                '''Handles a miss in the upper left corner in case of two adjacent vertical misses'''
                if  x + 1 >= 0 and x + 1 < self.size and y + 1 >= 0 and y + 1 < self.size:
                    self.kb.tell(expr(f"(Hit_({x + 1}, {y + 1}) & Hit_({x}, {y + 1}))==>Miss_({x}, {y})"))
                '''Handles a miss in the upper right corner in case of two adjacent vertical misses'''
                if  x + 1 >= 0 and x + 1 < self.size and y - 1 >= 0 and y - 1 < self.size:
                    self.kb.tell(expr(f"(Hit_({x}, {y - 1}) & Hit_({x + 1}, {y - 1}))==>Miss_({x}, {y})"))
                '''Handles a miss in the lower right corner in case of two adjacent vertical misses'''
                if  x - 1 >= 0 and x - 1 < self.size and y - 1 >= 0 and y - 1 < self.size:
                    self.kb.tell(expr(f"(Hit_({x}, {y - 1}) & Hit_({x - 1}, {y - 1}))==>Miss_({x}, {y})"))
                '''Handles a miss in the lower left corner in case of two adjacent vertical misses'''
                if  x - 1 >= 0 and x - 1 < self.size and y + 1 >= 0 and y + 1 < self.size:
                    self.kb.tell(expr(f"(Hit_({x}, {y + 1}) & Hit_({x - 1}, {y + 1}))==>Miss_({x}, {y})"))
        
        # Initialize all 10 x 10 grid as an empty grid
        for x in range(self.size):
            for y in range(self.size):
                self.kb.tell(expr(f'Unknown_{x}{y}'))

        # A Miss is equal to Empty and viceversa, so this is a biconditional which can be written as 2 implications
        for x in range(self.size):
            for y in range(self.size):
                self.kb.tell(expr(f'Miss_{x}{y}==>Empty_{x}{y}'))
        for x in range(self.size):
            for y in range(self.size):
                self.kb.tell(expr(f'Empty_{x}{y}==>Miss_{x}{y}'))

        # Case when we have 1 Hit and 3 adjacent Misses (edges of the grid are excluded)
        for x in range(1, self.size - 1):
            for y in range(1, self.size - 1):
                self.kb.tell(expr(f'(Hit_{x}{y} & Miss_{x}{y - 1} & Miss_{x - 1}{y} & Miss_{x + 1}{y})==>Hit_{x}{y + 1}'))
                self.kb.tell(expr(f'(Hit_{x}{y} & Miss_{x}{y + 1} & Miss_{x + 1}{y} & Miss_{x - 1}{y})==>Hit_{x}{y - 1}'))
                self.kb.tell(expr(f'(Hit_{x}{y} & Miss_{x - 1}{y} & Miss_{x}{y - 1} & Miss_{x}{y + 1})==>Hit_{x + 1}{y}'))
                self.kb.tell(expr(f'(Hit_{x}{y} & Miss_{x + 1}{y} & Miss_{x}{y - 1} & Miss_{x}{y + 1})==>Hit_{x - 1}{y}'))

        # Case when we have 1 Hit and 2 adjacent Misses, on the left and right edge of the grid (G[0][0], G[0][N], G[M][0] and G[M][N] are excluded)
        for x in range(1, self.size - 1):
            self.kb.tell(expr(f'(Hit_{x}0 & Miss_{x - 1}0 & Miss_{x + 1}0)==>Hit_{x}1'))
            self.kb.tell(expr(f'(Hit_{x}0 & Miss_{x}1 & Miss_{x + 1}0)==>Hit_{x - 1}0'))
            self.kb.tell(expr(f'(Hit_{x}0 & Miss_{x}1 & Miss_{x - 1}0)==>Hit_{x + 1}0'))
            self.kb.tell(expr(f'(Hit_{x}9 & Miss_{x - 1}9 & Miss_{x + 1}9)==>Hit_{x}8'))
            self.kb.tell(expr(f'(Hit_{x}9 & Miss_{x}8 & Miss_{x + 1}9)==>Hit_{x - 1}9'))
            self.kb.tell(expr(f'(Hit_{x}9 & Miss_{x}8 & Miss_{x - 1}9)==>Hit_{x + 1}9'))

        # Case when we have 1 Hit and 2 adjacent Misses, on the lowest and highest edge of the grid (G[0][0], G[0][N], G[M][0] and G[M][N] are excluded)
        for y in range(1, self.size - 1):
            self.kb.tell(expr(f'(Hit_0{y} & Miss_0{y - 1} & Miss_0{y + 1})==>Hit_1{y}'))
            self.kb.tell(expr(f'(Hit_0{y} & Miss_1{y} & Miss_0{y + 1})==>Hit_1{y - 1}'))
            self.kb.tell(expr(f'(Hit_0{y} & Miss_1{y} & Miss_0{y - 1})==>Hit_1{y + 1}'))
            self.kb.tell(expr(f'(Hit_9{y} & Miss_9{y - 1} & Miss_9{y + 1})==>Hit_1{y}'))
            self.kb.tell(expr(f'(Hit_9{y} & Miss_8{y} & Miss_9{y + 1})==>Hit_9{y - 1}'))
            self.kb.tell(expr(f'(Hit_9{y} & Miss_8{y} & Miss_9{y - 1})==>Hit_9{y + 1}'))

        # Case for G[0][0], G[0][N], G[M][0] and G[M][N]
        self.kb.tell(expr(f'(Hit_00 & Miss_01)==>Hit_10'))
        self.kb.tell(expr(f'(Hit_00 & Miss_10)==>Hit_01'))
        self.kb.tell(expr(f'(Hit_90 & Miss_80)==>Hit_91'))
        self.kb.tell(expr(f'(Hit_90 & Miss_91)==>Hit_80'))
        self.kb.tell(expr(f'(Hit_09 & Miss_08)==>Hit_19'))
        self.kb.tell(expr(f'(Hit_09 & Miss_19)==>Hit_08'))
        self.kb.tell(expr(f'(Hit_99 & Miss_89)==>Hit_98'))
        self.kb.tell(expr(f'(Hit_99 & Miss_98)==>Hit_89'))

        # All adjacent cells around a Sunk cell are Empty
        for x in range(self.size):
            for y in range(self.size):
                if (x != 0):
                    self.kb.tell(expr(f'(Sunk_{x}{y} & Unknown_{x - 1}{y})==>Empty_{x - 1}{y}'))
                if (x != self.size - 1):
                    self.kb.tell(expr(f'(Sunk_{x}{y} & Unknown_{x + 1}{y})==>Empty_{x + 1}{y}'))
                if (y != 0):
                    self.kb.tell(expr(f'(Sunk_{x}{y} & Unknown_{x}{y - 1})==>Empty_{x}{y - 1}'))
                if (y !=  self.size - 1):
                    self.kb.tell(expr(f'(Sunk_{x}{y} & Unknown_{x}{y + 1})==>Empty_{x}{y + 1}')) 
    #if I have two adjacent hit, cells that are adjacent to these two, but in different rows o columns from them, are miss (IMPLEMENT

    def add_knowledge(self, cell, result):
        """Adds knowledge to KB based on stroke result"""
        if result == 'hit':
            self.hits.append(cell)
            self.kb.tell(expr(f'Hit_{cell}'))
        elif result == 'miss':
            self.misses.append(cell)
            self.kb.tell(expr(f'Miss_{cell}'))
        else:
            self.kb.tell(expr(f"Sunk_{cell}"))

    def get_adjacent_cells(self, cell):
        """Returns the boxes adjacent to a given cell"""
        x, y = cell
        adjacent = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
        return [(i, j) for i, j in adjacent if 0 <= i < self.size and 0 <= j < self.size]

    def make_inferenced_move(self, cell):
        x, y = cell
        move = (x - 1, y)
        if x != 0 and pl_fc_entails(self.kb, expr(f'Hit_{x - 1}{y}')) and move not in self.hits and move not in self.misses:
            return move
        move = (x + 1, y)
        if x != (self.size - 1) and pl_fc_entails(self.kb, expr(f'Hit_{x + 1}{y}')) and move not in self.hits and move not in self.misses:
            return move
        move = (x, y - 1)
        if y != 0 and pl_fc_entails(self.kb, expr(f'Hit_{x}{y - 1}')) and move not in self.hits and move not in self.misses:
            return move
        move = (x, y + 1)
        if y != (self.size - 1) and pl_fc_entails(self.kb, expr(f'Hit_{x}{y + 1}')) and move not in self.hits and move not in self.misses:
            return move
        return (-1, -1)

    def choose_next_move(self):
        """Chooses the next move based on current knowledge base"""
        for cell in self.hits:
            inference = self.make_inferenced_move(cell)
            if inference != (-1, -1):
                return inference

        for cell in self.hits:
            for adj in self.get_adjacent_cells(cell):
                if adj not in self.hits and adj not in self.misses :
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