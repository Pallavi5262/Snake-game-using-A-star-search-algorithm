import pygame
import random
import math

pygame.init()

white = (255, 255, 255)  # snake body
red = (255, 0, 0)  # lifeline
purple = (128, 0, 128)  # snake head
black = (0, 0, 0)  # screen
green = (0, 255, 0)  # food
blue = (0, 0, 255)  # path color

cell_size = 30
screen_width = 900
screen_height = 600
cols = screen_width // cell_size
rows = screen_height // cell_size
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Snake game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 55)


def text_screen(text, color, x, y):
    screen_text = font.render(text, True, color)
    screen.blit(screen_text, [x, y])


def plot_snake(screen, head_color, body_color, snk_list, cell_size):
    for i, (x, y) in enumerate(snk_list):
        if i == len(snk_list) - 1:
            pygame.draw.rect(screen, head_color, [x * cell_size, y * cell_size, cell_size, cell_size])
        else:
            pygame.draw.rect(screen, body_color, [x * cell_size, y * cell_size, cell_size, cell_size])


def heart(sur, col, x, y, s):
    pygame.draw.circle(sur, red, (x * s + s // 2, y * s + s // 2), s // 2)


def perfect_sq(n):
    return int(math.sqrt(n)) ** 2 == n


def per_sq_pos(m_x, m_y):
    persq_x = [i for i in range(m_x) if perfect_sq(i)]
    persq_y = [i for i in range(m_y) if perfect_sq(i)]
    return random.choice(persq_x), random.choice(persq_y)

    def collision(x1, y1, x2, y2):
        return (x1, y1) == (x2, y2)


def reset_snake():
    return cols // 2, rows // 2, 0, 0, [], 1


def handle_game_over(lifeline):
    if lifeline > 0:
        lifeline -= 1
        return reset_snake(), lifeline
    return True, lifeline


def update_snpos(snake_x, snake_y, velocity_x, velocity_y):
    return snake_x + velocity_x, snake_y + velocity_y


def update_screen(score, lifeline, food_x, food_y, heart_x, heart_y, snk_list, path):
    screen.fill(black)
    heart(screen, red, heart_x, heart_y, cell_size)

    text_screen(f"Score: {score * 2}", white, 5, 5)
    text_screen(f"Lifelines: {lifeline}", white, screen_width - 200, 5)

    pygame.draw.rect(screen, green, [food_x * cell_size, food_y * cell_size, cell_size, cell_size])

    heart(screen, red, heart_x, heart_y, cell_size)

    for (px, py) in path:
        pygame.draw.rect(screen, blue, [px * cell_size, py * cell_size, cell_size, cell_size])

    plot_snake(screen, purple, white, snk_list, cell_size)
    pygame.display.update()

    def a_star(start, goal, grid):
        open_list = []

    closed_list = set()
    parent = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    open_list.append(start)

    while open_list:
        current = min(open_list, key=lambda x: f_score[x])
        if current == goal:
            return reconstruct_path(parent, current)

        open_list.remove(current)
        closed_list.add(current)

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for direction in directions:
            neighbor = (current[0] + direction[0], current[1] + direction[1])

            if (0 <= neighbor[0] < cols and 0 <= neighbor[1] < rows and
                    neighbor not in closed_list and grid[neighbor[1]][neighbor[0]] != 1):

                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                    parent[neighbor] = current
                    open_list.append(neighbor)

    return []


def heuristic(start, goal):
    return abs(start[0] - goal[0]) + abs(start[1] - goal[1])  # Manhattan distance


def reconstruct_path(parent, current):
    path = []
    while current in parent:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path  # Main Game Loop


def gameloop():
    exit_game = False
    game_over = False
    snake_x, snake_y, velocity_x, velocity_y, snk_list, snk_length = reset_snake()
    food_x, food_y = random.randint(0, cols - 1), random.randint(0, rows - 1)
    heart_x, heart_y = per_sq_pos(cols, rows)
    score, lifeline = 0, 0
    init_velocity, fps = 1, 10

    while not exit_game:
        if game_over:
            screen.fill(black)
            text_screen("Game Over! Press Enter To Restart", white, 100, 250)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    gameloop()
            continue

        grid = [[0 for _ in range(cols)] for _ in range(rows)]
        for (x, y) in snk_list:
            grid[y][x] = 1

        path = a_star((snake_x, snake_y), (heart_x, heart_y), grid)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and velocity_x == 0:
                    velocity_x, velocity_y = init_velocity, 0
                if event.key == pygame.K_LEFT and velocity_x == 0:
                    velocity_x, velocity_y = -init_velocity, 0
                if event.key == pygame.K_UP and velocity_y == 0:
                    velocity_x, velocity_y = 0, -init_velocity
                if event.key == pygame.K_DOWN and velocity_y == 0:
                    velocity_x, velocity_y = 0, init_velocity

        snake_x, snake_y = update_snpos(snake_x, snake_y, velocity_x, velocity_y)

        if collision(snake_x, snake_y, food_x, food_y):
            score += 1
            food_x, food_y = random.randint(0, cols - 1), random.randint(0, rows - 1)
            snk_length += 1

        if collision(snake_x, snake_y, heart_x, heart_y):
            if lifeline < 3:
                lifeline += 1
            heart_x, heart_y = random.randint(0, cols - 1), random.randint(0, rows - 1)

        if snake_x < 0 or snake_x >= cols or snake_y < 0 or snake_y >= rows:
            res, lifeline = handle_game_over(lifeline)
            if res is True:
                game_over = True
            else:
                snake_x, snake_y, velocity_x, velocity_y, snk_list, snk_length = res

        head = [snake_x, snake_y]
        snk_list.append(head)

        if len(snk_list) > snk_length:
            del snk_list[0]

        if head in snk_list[:-1]:
            res = handle_game_over(lifeline)
            if res is True:
                game_over = True
            else:
                snake_x, snake_y, velocity_x, velocity_y, snk_list, snk_length = res

        update_screen(score, lifeline, food_x, food_y, heart_x, heart_y, snk_list, path)
        clock.tick(fps)

    pygame.quit()
    quit()


gameloop()