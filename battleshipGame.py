from battleshipAgent import *

class BattleshipGame:
    def __init__(self, size, human_ships, agent_ships):
        self.size = size  # Grid size
        self.human_ships = human_ships  # List of human ships, each represented by a list of tuples (cell positions occupied by the ship)
        self.agent_ships = agent_ships  # List of agent ships, each represented by a list of tuples (cell positions occupied by the ship)
        self.human_sunk = [] # List of user's sunk boxes
        self.agent_sunk = [] # List of agent's sunk boxes
        self.agent = BattleshipAgent(size) # Agent instance
        self.human_grid_own = self.create_grid() # User grid where one's pawns are placed
        self.human_grid_adv = self.create_grid() # User grid where the moves made are memorized
        self.agent_grid_own = self.create_grid() # Agent grid where one's pawns are placed
        self.agent_grid_adv = self.create_grid() # Agent grid where the moves made are memorized
        self.human_hits = [] # List of boxes hit successfully by user
        self.human_misses = [] # List of boxes hit unsuccessfully by user

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
                if self.agent_grid_adv[cell[0]][cell[1]] != 'S':
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
            self.agent.add_knowledge(cell, "sunk")
            self.agent_grid_adv[cell[0]][cell[1]] = 'S'
            adj = self.agent.get_adjacent_cells(cell)
            for cell in adj:
                if cell not in self.agent.misses and cell not in self.agent.hits:
                    self.agent.add_knowledge(cell, "miss")
                    x, y = cell
                    self.agent_grid_adv[x][y] = 'M'

    def check_sunk(self, cell, turn):
        '''Check after a hit if the hit ship was also sunk'''
        if turn == 'A':
            for ship in self.human_ships:
                if ship not in self.human_sunk and all(cell in self.agent.hits for cell in ship):
                    self.human_sunk.append(ship)
                    print("\033[32msunk!\033[0m\n")
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

        turn = random.choice(['H', 'A'])
        human_move_counter = agent_move_counter = 0

        while True:
            move = ()
            if (turn == 'A'):
                agent_move_counter += 1
                print(f"\033[32mAI turn: {agent_move_counter}\033[0m\n")
                if agent_move_counter % 10 == 0:
                    move = self.agent.check_globally()
                if move == ():
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
                    print("\033[32mAI won!\033[0m\n")
                    break
                turn = 'H'
            else:
                human_move_counter += 1
                print(f"AI turn: {human_move_counter}\n")
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