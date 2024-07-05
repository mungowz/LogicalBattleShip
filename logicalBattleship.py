from battleshipGame import *

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