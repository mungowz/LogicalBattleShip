from aima.logic import PropDefiniteKB, expr, pl_fc_entails
import random

class BattleshipGame:
    def __init__(self, size, human_ships, agent_ships):
        self.size = size  # Grid size
        self.human_ships = human_ships  # List of human ships, each represented by a list of tuples (cell positions occupied by the ship)
        self.agent_ships = agent_ships  # List of agent ships, each represented by a list of tuples (cell positions occupied by the ship)
        self.human_sunk = []
        self.agent_sunk = []
        self.agent = BattleshipAgent(size) # Agent instance
        self.human_grid_own = self.create_grid() # Human grid where one's pawns are placed
        self.human_grid_adv = self.create_grid() # Human grid where the moves made are memorized
        self.agent_grid_own = self.create_grid() # Agent grid where one's pawns are placed
        self.agent_grid_adv = self.create_grid() # Agent grid where the moves made are memorized
        self.human_hits = [] # List of boxes hit unsuccessfully
        self.human_misses = [] # List of boxes hit unsuccessfully

    def create_grid(self):
        grid = []
        for i in range(self.size):
            grid.append([])
            for _ in range(self.size):
                grid[i].append('*')
        return grid

    def print_grid(self, grid, turn):
        if turn == 'A':
            print("\033[32m   \033[0m" + "\033[32m \033[0m".join(f"\033[32m{i:2}\033[0m" for i in range(0, self.size)))
        else:
            print("   " + " ".join(f"{i:2}" for i in range(0, self.size)))
        for i in range(self.size):
            row_label = chr(65 + i)
            row_content = " ".join(f" {grid[i][j]}" for j in range(len(grid[0])))
            if turn == 'A':
                print(f"\033[32m{row_label}  {row_content}\033[0m")
            else:
                print(f"{row_label}  {row_content}")
        print('\n')

    def update_grid(self, turn):
        if turn == 'A':
            for cell in self.agent.hits:
                self.agent_grid_adv[cell[0]][cell[1]] = 'H'
            for cell in self.agent.misses:
                self.agent_grid_adv[cell[0]][cell[1]] = 'M'
        else:
            for cell in self.human_hits:
                self.human_grid_adv[cell[0]][cell[1]] = 'H'
            for cell in self.human_misses:
                self.human_grid_adv[cell[0]][cell[1]] = 'M'

    def check_hit(self, cell, ships):
        """Check if a cell hits a ship"""
        for ship in ships:
            if cell in ship:
                return "hit"
        return "miss"

    def update_sunk_adjiances(self, ship):
        '''Upgrade miss cells around sunk cells'''
        for cell in ship:
            adj = self.agent.get_adjacent_cells(cell)
            for cell in adj:
                if cell not in self.agent.misses and cell not in self.agent.hits:
                    self.agent.add_knowledge(cell, "sunk")
                    x, y = cell
                    self.agent_grid_adv[x][y] = 'M'

    def check_sunk(self, cell, turn):
        '''Check after a hit if the hit ship was also sunk'''
        if turn == 'A':
            for ship in self.human_ships:
                if ship not in self.human_sunk and all(cell in self.agent.hits for cell in ship):
                    self.human_sunk.append(ship)
                    print("\033[32msunk!\033[0m\n")
                    for cell in ship:
                        self.agent.kb.tell(expr(f'Sunk_{cell}'))
                        self.agent_grid_adv[cell[0]][cell[1]] = 'S'
                    self.update_sunk_adjiances(ship)
        else:
            for ship in self.agent_ships:
                if ship not in self.agent_sunk and all(cell in self.human_hits for cell in ship):
                    self.agent_sunk.append(ship)
                    print("Sunk!\n")
                    for cell in ship:
                        self.human_grid_adv[cell[0]][cell[1]] = 'S'

    def get_letter(self):
        while True:
            letter = input("Choose a letter between A and J: ").upper()
            if letter in 'ABCDEFGHIJ':
                return letter
            else:
                print("Invalid letter. Try again.")

    def get_number(self):
        while True:
            number = int(input("Choose a number between 0 and 9: "))
            if 0 <= number <= 9:
                return number
            else:
                print("Invalid number. Try again.")

    def human_next_move(self):
        x = self.get_letter()
        y = self.get_number()
        return (ord(x) - 65, y)

    def play(self):
        """Simulate the game"""
        for ship in self.human_ships:
            for i, j in ship:
                self.human_grid_own[i][j] = 'P'
        for ship in self.agent_ships:
            for i, j in ship:
                self.agent_grid_own[i][j] = 'P'

        self.agent.hits.append((7, 6))
        self.agent.hits.append((7, 7))
        self.agent_grid_adv[7][6] = 'H'
        self.agent_grid_adv[7][7] = 'H'
        self.agent.kb.tell(expr('Hit_(7, 7)'))
        self.agent.kb.tell(expr('Hit_(7, 6)'))

        turn = random.choice(['H', 'A'])

        while True:
            if (turn == 'A'):
                move = self.agent.choose_next_move()
                print(f"\033[32mAI tries: ({chr(65 + move[0])}, {move[1]})\033[0m")
                result = self.check_hit(move, self.human_ships)
                print(f"\033[32m{result}!\033[0m\n")
                self.agent.add_knowledge(move, result)
                self.update_grid(turn)
                self.check_sunk(move, turn)
                print("\033[32mUser own grid:\033[0m\n")
                self.print_grid(self.human_grid_own, turn)
                print("\033[32mAI opponent grid:\033[0m\n")
                self.print_grid(self.agent_grid_adv, turn)

                if len(self.agent.hits) == sum(len(ship) for ship in self.human_ships):
                    print("\033[32mAll ships sunk!\033[0m")
                    print("\033[32mAI won\033[0m!")
                    break
                turn = 'H'
            else:
                move = self.human_next_move()
                print(f"User tries: ({chr(65 + move[0])}, {move[1]})")
                result = self.check_hit(move, self.agent_ships)
                if result == 'hit':
                    self.human_hits.append(move)
                else:
                    self.human_misses.append(move)
                print(f"{result}!\n")
                self.update_grid(turn)
                self.check_sunk(move, turn)
                print("AI own grid:\n")
                self.print_grid(self.agent_grid_own, turn)
                print("User opponent grid:\n")
                self.print_grid(self.human_grid_adv, turn)

                if len(self.human_hits) == sum(len(ship) for ship in self.agent_ships):
                    print("All ships sunk!")
                    print("Human won!")
                    break
                turn = 'A'

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

def main():
    A, B, C, D, E, F, G, H, I, J = range(10)
    grid_size = 10
    human_ships = [
        # 4 PatrolBoat (2 cells) 
        [(B, 8), (C, 8)], 
        [(F, 8), (F, 9)],
        [(J, 4), (J, 5)],
        [(I, 9), (J, 9)],
        # 3 Destroyer (3 cells)
        [(H, 6), (H, 7), (H, 8)],
        [(C, 2), (D, 2), (E, 2)],
        [(J, 0), (J, 1), (J, 2)],
        # 2 Battleship (4 cells)
        [(C, 0), (D, 0), (E, 0), (F, 0)],
        [(E, 4), (E, 5), (E, 6), (E, 7)],
        # 1 Carrier (6 cells)
        [(A, 0), (A, 1), (A, 2), (A, 3), (A, 4), (A, 5)]
    ]
    agent_ships = [
        # 4 PatrolBoat (2 cells) 
        [(A, 0), (A, 1)], 
        [(C, 2), (C, 3)],
        [(E, 4), (E, 5)],
        [(I, 1), (J, 1)],
        # 3 Destroyer (3 cells)
        [(A, 7), (B, 7), (C, 7)],
        [(I, 3), (I, 4), (I, 5)],
        [(E, 0), (E, 1), (E, 2)],
        # 2 Battleship (4 cells)
        [(G, 2), (G, 3), (G, 4), (G, 5)],
        [(G, 7), (H, 7), (I, 7), (J, 7)],
        # 1 Carrier (6 cells)
        [(D, 9), (E, 9), (F, 9), (G, 9), (H, 9), (I, 9)]
    ]
    game = BattleshipGame(grid_size, human_ships, agent_ships)
    game.play()

if __name__ == "__main__":
    main()