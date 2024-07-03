from aima.logic import *
import random


A, B, C, D, E, F, G, H, I, J = range(10)
AMOUNT = 0
SIZE = 1
GRID_SIZE = 10


def create_grid(GRID_SIZE):
    grid = []

    for i in range(GRID_SIZE):
        grid.append([])
        for j in range(GRID_SIZE):
            grid[i].append('*')
    
    return grid


def print_grid(grid):
    print('   ' + ' '.join(f'{i:2}' for i in range(0, len(grid))))

    for i in range(len(grid)):
        row_label = chr(65 + i)
        row_content = ' '.join(f' {grid[i][j]}' for j in range(len(grid[0])))
        print(f"{row_label}  {row_content}")
    print('\n')


def knowledge_base_definition(GRID_SIZE):
    kb = PropDefiniteKB()

    # U = Unknown  H = Hit  M = Miss  S = Sunk  E = Empty

    # Initialize all 10 x 10 grid as an empty grid
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            kb.tell(expr(f'U_{chr(65 + x)}{y}'))

    # A Miss is equal to Empty and viceversa, so this is a biconditional which can be written as 2 implications
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            kb.tell(expr(f'M_{chr(65 + x)}{y}==>E_{chr(65 + x)}{y}'))
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            kb.tell(expr(f'E_{chr(65 + x)}{y}==>M_{chr(65 + x)}{y}'))

    # Case when we have 1 Hit and 3 adjacent Misses (edges of the grid are excluded)
    for x in range(1, GRID_SIZE - 1):
        for y in range(1, GRID_SIZE - 1):
            kb.tell(expr(f'(H_{chr(65 + x)}{y} & M_{chr(65 + x)}{y - 1} & M_{chr(65 + x - 1)}{y} & M_{chr(65 + x + 1)}{y})==>H_{chr(65 + x)}{y + 1}'))
            kb.tell(expr(f'(H_{chr(65 + x)}{y} & M_{chr(65 + x)}{y + 1} & M_{chr(65 + x + 1)}{y} & M_{chr(65 + x - 1)}{y})==>H_{chr(65 + x)}{y - 1}'))
            kb.tell(expr(f'(H_{chr(65 + x)}{y} & M_{chr(65 + x - 1)}{y} & M_{chr(65 + x)}{y - 1} & M_{chr(65 + x)}{y + 1})==>H_{chr(65 + x + 1)}{y}'))
            kb.tell(expr(f'(H_{chr(65 + x)}{y} & M_{chr(65 + x + 1)}{y} & M_{chr(65 + x)}{y - 1} & M_{chr(65 + x)}{y + 1})==>H_{chr(65 + x - 1)}{y}'))

    # Case when we have 1 Hit and 2 adjacent Misses, on the left and right edge of the grid (G[0][0], G[0][N], G[M][0] and G[M][N])
    for x in range(1, GRID_SIZE - 1):
        kb.tell(expr(f'(H_{chr(65 + x)}0 & M_{chr(65 + x - 1)}0 & M_{chr(65 + x + 1)}0)==>H_{chr(65 + x)}1'))
        kb.tell(expr(f'(H_{chr(65 + x)}0 & M_{chr(65 + x)}1 & M_{chr(65 + x + 1)}0)==>H_{chr(65 + x - 1)}0'))
        kb.tell(expr(f'(H_{chr(65 + x)}0 & M_{chr(65 + x)}1 & M_{chr(65 + x - 1)}0)==>H_{chr(65 + x + 1)}0'))
        kb.tell(expr(f'(H_{chr(65 + x)}9 & M_{chr(65 + x - 1)}9 & M_{chr(65 + x + 1)}9)==>H_{chr(65 + x)}8'))
        kb.tell(expr(f'(H_{chr(65 + x)}9 & M_{chr(65 + x)}8 & M_{chr(65 + x + 1)}9)==>H_{chr(65 + x - 1)}9'))
        kb.tell(expr(f'(H_{chr(65 + x)}9 & M_{chr(65 + x)}8 & M_{chr(65 + x - 1)}9)==>H_{chr(65 + x + 1)}9'))

    # Case when we have 1 Hit and 2 adjacent Misses, on the lowest and highest edge of the grid (G[0][0], G[0][N], G[M][0] and G[M][N])
    for y in range(1, GRID_SIZE - 1):
        kb.tell(expr(f'(H_A{y} & M_A{y - 1} & M_A{y + 1})==>H_B{y}'))
        kb.tell(expr(f'(H_A{y} & M_B{y} & M_A{y + 1})==>H_B{y - 1}'))
        kb.tell(expr(f'(H_A{y} & M_B{y} & M_A{y - 1})==>H_B{y + 1}'))
        kb.tell(expr(f'(H_J{y} & M_J{y - 1} & M_J{y + 1})==>H_B{y}'))
        kb.tell(expr(f'(H_J{y} & M_I{y} & M_J{y + 1})==>H_J{y - 1}'))
        kb.tell(expr(f'(H_J{y} & M_I{y} & M_J{y - 1})==>H_J{y + 1}'))

    # Case for G[0][0], G[0][N], G[M][0] and G[M][N]
    kb.tell(expr(f'(H_A0 & M_A1)==>H_B0'))
    kb.tell(expr(f'(H_A0 & M_B0)==>H_A1'))
    kb.tell(expr(f'(H_J0 & M_I0)==>H_J1'))
    kb.tell(expr(f'(H_J0 & M_J1)==>H_I0'))
    kb.tell(expr(f'(H_A9 & M_A8)==>H_B9'))
    kb.tell(expr(f'(H_A9 & M_B9)==>H_A8'))
    kb.tell(expr(f'(H_J9 & M_I9)==>H_J8'))
    kb.tell(expr(f'(H_J9 & M_J8)==>H_I9'))
    
    # All adjacent cells around a Sunk cell are Empty
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if (x != 0):
                kb.tell(expr(f'(S_{chr(65 + x)}{y} & U_{chr(65 + x - 1)}{y})==>E_{chr(65 + x - 1)}{y}'))
            if (x != GRID_SIZE - 1):
                kb.tell(expr(f'(S_{chr(65 + x)}{y} & U_{chr(65 + x + 1)}{y})==>E_{chr(65 + x + 1)}{y}'))
            if (y != 0):
                kb.tell(expr(f'(S_{chr(65 + x)}{y} & U_{chr(65 + x)}{y - 1})==>E_{chr(65 + x)}{y - 1}'))
            if (y !=  GRID_SIZE - 1):
                kb.tell(expr(f'(S_{chr(65 + x)}{y} & U_{chr(65 + x)}{y + 1})==>E_{chr(65 + x)}{y + 1}'))
    
    # Case when there is 1 Miss and 2 adjacent Hits
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if x < GRID_SIZE - 3:
                kb.tell(expr(f'(M_{chr(65 + x)}{y}) & H_{chr(65 + x + 1)}{y} & H_{chr(65 + x + 2)}{y}==>H_{chr(65 + x + 3)}{y}'))
            if x > 3:
                kb.tell(expr(f'(M_{chr(65 + x)}{y}) & H_{chr(65 + x - 1)}{y} & H_{chr(65 + x - 2)}{y}==>H_{chr(65 + x - 3)}{y}'))
            if y < GRID_SIZE - 3:
                kb.tell(expr(f'(M_{chr(65 + x)}{y}) & H_{chr(65 + x)}{y + 1} & H_{chr(65 + x)}{y + 2}==>H_{chr(65 + x)}{y + 3}'))
            if y > 3:
                kb.tell(expr(f'(M_{chr(65 + x)}{y}) & H_{chr(65 + x)}{y - 1} & H_{chr(65 + x)}{y - 2}==>H_{chr(65 + x)}{y - 3}'))
    
    kb.tell(expr(f'(H_A0 & H_A1)==>H_A2'))
    kb.tell(expr(f'(H_A0 & H_B0)==>H_C0'))
    kb.tell(expr(f'(H_J0 & H_I0)==>H_H0'))
    kb.tell(expr(f'(H_J0 & H_J1)==>H_J2'))
    kb.tell(expr(f'(H_A9 & H_A8)==>H_A7'))
    kb.tell(expr(f'(H_A9 & H_B9)==>H_C9'))
    kb.tell(expr(f'(H_J9 & H_I9)==>H_H9'))
    kb.tell(expr(f'(H_J9 & M_J8)==>H_J7'))

    return kb


def make_random_move(human_grid_own, last_hit, GRID_SIZE):
    x = random.randint(0, GRID_SIZE - 1)
    y = random.randint(0, GRID_SIZE - 1)

    if human_grid_own[x][y] == 'P':
        score = 'H'
        last_hit = 0
    else:     
        score = 'M'
    return score, x, y, last_hit


def make_inferenced_move(agent_grid_adv, kb, x, y, GRID_SIZE):
    score = 'H'
    if x != 0 and pl_fc_entails(kb, expr(f'H_{chr(65 + x - 1)}{y}')) and agent_grid_adv[x - 1][y] != 'H':
        x = x - 1
    elif x != (GRID_SIZE - 1) and pl_fc_entails(kb, expr(f'H_{chr(65 + x + 1)}{y}')) and agent_grid_adv[x + 1][y] != 'H':
        x = x + 1
    elif y != 0 and pl_fc_entails(kb, expr(f'H_{chr(65 + x)}{y - 1}')) and agent_grid_adv[x][y - 1] != 'H':
        y = y - 1
    elif y != (GRID_SIZE - 1) and pl_fc_entails(kb, expr(f'H_{chr(65 + x)}{y + 1}')) and agent_grid_adv[x][y + 1] != 'H':
        y = y + 1
    else:
         score = 'M'
    return score, x, y 


def make_adjacent_move(agent_grid_adv, human_grid_own, x, y, last_hit, h, k):
    if last_hit == 0 and (x == 0 or agent_grid_adv[x - 1][y] == 'M'):
        last_hit = 1
    if last_hit == 0 and x != 0:
        if human_grid_own[x - 1][y] != 'P':
            score = 'M'
            last_hit = 1
            h = - 1
            return score, x, y, last_hit, h, k
        else:
            score = 'H'
            last_hit = 0
            x = x - 1
            return score, x, y, last_hit, h, k

    if last_hit == 1 and (x == GRID_SIZE - 1 or agent_grid_adv[x + 1][y] == 'M'):
        last_hit = 2
    if last_hit == 1 and x != GRID_SIZE - 1:
        if human_grid_own[x + 1][y] != 'P':
            score = 'M'
            last_hit = 2
            h = 1
            return score, x, y, last_hit, h, k
        else:
            score = 'H'
            last_hit = 0
            x = x + 1
            return score, x, y, last_hit, h, k
        
    if last_hit == 2 and (y == 0 or agent_grid_adv[x][y - 1] == 'M'):
        last_hit = 3
    if last_hit == 2 and y != 0:
        if human_grid_own[x][y - 1] != 'P':
            score = 'M'
            last_hit = 3
            k = -1
            return score, x, y, last_hit, h, k
        else:
            score = 'H'
            last_hit = 0
            y = y - 1
            return score, x, y, last_hit, h, k
                
    if last_hit == 3 and (y == GRID_SIZE - 1 or agent_grid_adv[x - 1][y] == 'M'):
        last_hit = 4
    if last_hit == 3 and y != GRID_SIZE - 1:
        if human_grid_own[x][y + 1] != 'P':
            score = 'M'
            last_hit = 4
            k = 1
            return score, x, y, last_hit, h, k
        else:
            score = 'H'
            last_hit = 0
            x = y + 1
            return score, x, y, last_hit, h, k


def make_move(agent_grid_adv, human_grid_own, kb, score, x, y, last_hit, GRID_SIZE):
    h = k = 0
    if last_hit == 4:
        score, x, y, last_hit = make_random_move(human_grid_own, last_hit, GRID_SIZE)
    else:
        score, x, y  = make_inferenced_move(agent_grid_adv, kb, x, y, GRID_SIZE)
        if score == 'M':
            score, x, y, last_hit, h, k = make_adjacent_move(human_grid_own, x, y, last_hit, h, k)
        else:
            last_hit = 0

    print(f'Agent tries: x:{chr(65 + x + h)} y:{y + k}')
    if score == 'M':
        print('Miss!\n\n')
    else:
        print('Hit!\n\n')
        
    kb.tell(expr(f'{score}_{chr(65 + x + h)}{y + k}'))
    agent_grid_adv[x + h][y + k] = score
    
    return agent_grid_adv, kb, score, x, y, last_hit


human_grid_own = create_grid(GRID_SIZE)
human_grid_adv = create_grid(GRID_SIZE)
agent_grid_adv = create_grid(GRID_SIZE)

ships = {
    'Destroyer': (3, 3),
    'PatrolBoat': (4, 2)
}

human_pawns = {
    'Destroyer': ships['Destroyer'][AMOUNT],
    'PatrolBoat': ships['PatrolBoat'][AMOUNT]    
}

human_grid_own[A][0] = 'P'
human_grid_own[A][1] = 'P'
human_grid_own[A][2] = 'P'
human_grid_own[J][0] = 'P'
human_grid_own[J][1] = 'P'
human_grid_own[J][2] = 'P'
human_grid_own[E][5] = 'P'
human_grid_own[F][5] = 'P'
human_grid_own[G][5] = 'P'
human_grid_own[C][3] = 'P'
human_grid_own[C][4] = 'P'
human_grid_own[J][9] = 'P'
human_grid_own[I][9] = 'P'
human_grid_own[J][7] = 'P'
human_grid_own[I][7] = 'P'
human_grid_own[G][0] = 'P'
human_grid_own[G][1] = 'P'

agent_grid_own = human_grid_own.copy()
kb = knowledge_base_definition(GRID_SIZE)
score = 'X'
x = -1
y = -1
last_hit = 4

#agent_grid_adv[A][0] = 'H'
#agent_grid_adv[A][1] = 'H'
#kb.tell(expr('H_A0'))
#kb.tell(expr('H_A1'))

agent_grid_adv[C][3] = 'H'
kb.tell(expr('H_C3'))
x = C
y = 3
last_hit = 0
for _ in range(4):
    agent_grid_adv, kb, score, x, y, last_hit = make_move(agent_grid_adv, human_grid_own, kb, score, x, y, last_hit, GRID_SIZE)
    print(f'score:{score} x:{x} y:{y} last_hit:{last_hit}')
    print_grid(human_grid_own)
    print_grid(agent_grid_adv)