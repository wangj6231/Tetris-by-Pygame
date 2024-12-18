import pygame
import random

pygame.init()
WIDTH, HEIGHT = 400, 600
CELL_SIZE = 30
COLUMNS, ROWS = 10, HEIGHT // CELL_SIZE

COLORS = {
    'background': (0, 0, 0),
    'grid': (30, 30, 30),
    'text': (200, 200, 200),
    'button_start': (0, 150, 0),
    'button_restart': (150, 100, 0),
    'border': (50, 50, 50)
}

PIECE_COLORS = [
    (0, 255, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 0), 
    (255, 100, 100),
    (100, 100, 255), 
    (255, 165, 0) 
]

SHAPES = [
    [[1, 1, 1, 1]],           # I
    [[1, 1], [1, 1]],         # O
    [[0, 1, 1], [1, 1, 0]],   # S
    [[1, 1, 0], [0, 1, 1]],   # Z
    [[1, 0, 0], [1, 1, 1]],   # L
    [[0, 0, 1], [1, 1, 1]],   # J
    [[0, 1, 0], [1, 1, 1]]    # T

]

INITIAL_MOVE_DELAY = 200
MOVE_REPEAT_DELAY = 50 

class Brick:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(PIECE_COLORS)
        self.x = COLUMNS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

class Tetris:
    def __init__(self):
        self.grid = [[0] * ROWS for _ in range(COLUMNS)]
        self.current_brick = Brick()
        self.next_brick = Brick()
        self.running = False
        self.score = 0
        self.high_score = self.load_high_score()
        self.last_move_time = {'left': 0, 'right': 0}
        self.key_press_time = {'left': 0, 'right': 0}

    def load_high_score(self):
        try:
            with open('tetris_high_score.txt', 'r') as file:
                return int(file.read())
        except:
            return 0

    def save_high_score(self):
        try:
            with open('tetris_high_score.txt', 'w') as file:
                file.write(str(self.high_score))
        except:
            pass

    def handle_movement(self, direction, current_time):
        key_state = pygame.key.get_pressed()
        dx = -1 if direction == 'left' else 1
        if (current_time - self.key_press_time[direction] >= INITIAL_MOVE_DELAY and
            current_time - self.last_move_time[direction] >= MOVE_REPEAT_DELAY):
            if self.move(dx, 0):
                self.last_move_time[direction] = current_time

    def is_valid_position(self, brick, offset_x=0, offset_y=0):
        for y, row in enumerate(brick.shape):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = brick.x + x + offset_x
                    grid_y = brick.y + y + offset_y
                    if (grid_x < 0 or grid_x >= COLUMNS or 
                        grid_y >= ROWS or 
                        (grid_y >= 0 and self.grid[grid_x][grid_y])):
                        return False
        return True

    def lock_brick(self):
        for y, row in enumerate(self.current_brick.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_brick.x + x][self.current_brick.y + y] = self.current_brick.color

    def clear_lines(self):
        cleared_lines = 0
        for y in range(ROWS):
            if all(self.grid[x][y] for x in range(COLUMNS)):
                cleared_lines += 1
                for move_y in range(y, 0, -1):
                    for x in range(COLUMNS):
                        self.grid[x][move_y] = self.grid[x][move_y - 1]
                for x in range(COLUMNS):
                    self.grid[x][0] = 0
        
        self.score += cleared_lines ** 2 * 10
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def spawn_brick(self):
        self.current_brick = self.next_brick
        self.next_brick = Brick()
        if not self.is_valid_position(self.current_brick):
            self.running = False

    def move(self, dx, dy):
        if self.is_valid_position(self.current_brick, dx, dy):
            self.current_brick.x += dx
            self.current_brick.y += dy
            return True
        elif dy:
            self.lock_brick()
            self.clear_lines()
            self.spawn_brick()
        return False

    def rotate_brick(self):
        original_shape = self.current_brick.shape[:]
        self.current_brick.rotate()
        if not self.is_valid_position(self.current_brick):
            self.current_brick.shape = original_shape

class Renderer:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.start_button_rect = pygame.Rect(WIDTH + 20, HEIGHT // 2 + 50, 100, 40)
        self.restart_button_rect = pygame.Rect(WIDTH + 20, HEIGHT // 2 + 120, 100, 40)
        self.preview_pos = (WIDTH + 25, 50)
        self.score_pos = (WIDTH + 25, 200)
        self.high_score_pos = (WIDTH + 25, 280)

    def draw_grid(self):
        pygame.draw.rect(self.screen, COLORS['border'], 
                        pygame.Rect(0, 0, COLUMNS * CELL_SIZE, ROWS * CELL_SIZE), 2)
        
        for x in range(COLUMNS):
            for y in range(ROWS):
                color = self.game.grid[x][y] if self.game.grid[x][y] else COLORS['grid']
                pygame.draw.rect(self.screen, color, 
                    pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, COLORS['border'], 
                    pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    def draw_score_box(self, pos, label, value):
        font = pygame.font.SysFont("Arial", 20)
        box_width, box_height = 120, 60
        
        box_rect = pygame.Rect(pos[0], pos[1], box_width, box_height)
        pygame.draw.rect(self.screen, COLORS['grid'], box_rect)
        pygame.draw.rect(self.screen, COLORS['border'], box_rect, 1)
        
        label_text = font.render(label, True, COLORS['text'])
        value_text = font.render(str(value), True, COLORS['text'])
        self.screen.blit(label_text, (pos[0] + 10, pos[1] + 10))
        self.screen.blit(value_text, (pos[0] + 10, pos[1] + 35))

    def draw_preview_box(self):
        font = pygame.font.SysFont("Arial", 20)
        next_text = font.render("Next:", True, COLORS['text'])
        self.screen.blit(next_text, (self.preview_pos[0], self.preview_pos[1] - 30))

        preview_size = 4 * CELL_SIZE
        preview_rect = pygame.Rect(self.preview_pos[0], self.preview_pos[1], 
                                 preview_size, preview_size)
        pygame.draw.rect(self.screen, COLORS['grid'], preview_rect)
        pygame.draw.rect(self.screen, COLORS['border'], preview_rect, 1)

        brick = self.game.next_brick
        brick_width = len(brick.shape[0]) * CELL_SIZE
        brick_height = len(brick.shape) * CELL_SIZE
        
        start_x = self.preview_pos[0] + (preview_size - brick_width) // 2
        start_y = self.preview_pos[1] + (preview_size - brick_height) // 2

        for y, row in enumerate(brick.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, brick.color,
                        pygame.Rect(start_x + x * CELL_SIZE, start_y + y * CELL_SIZE, 
                                  CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, COLORS['border'],
                        pygame.Rect(start_x + x * CELL_SIZE, start_y + y * CELL_SIZE, 
                                  CELL_SIZE, CELL_SIZE), 1)

    def draw_buttons(self):
        font = pygame.font.SysFont("Arial", 20)
        
        pygame.draw.rect(self.screen, COLORS['button_start'], self.start_button_rect)
        start_text = font.render("START", True, COLORS['text'])
        self.screen.blit(start_text, (self.start_button_rect.x + 20, 
                                     self.start_button_rect.y + 10))

        pygame.draw.rect(self.screen, COLORS['button_restart'], self.restart_button_rect)
        restart_text = font.render("RESTART", True, COLORS['text'])
        self.screen.blit(restart_text, (self.restart_button_rect.x + 5, 
                                      self.restart_button_rect.y + 10))

    def render(self):
        self.screen.fill(COLORS['background'])
        self.draw_grid()
        
        if self.game.running:
            for y, row in enumerate(self.game.current_brick.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, self.game.current_brick.color,
                            pygame.Rect((self.game.current_brick.x + x) * CELL_SIZE,
                                      (self.game.current_brick.y + y) * CELL_SIZE,
                                      CELL_SIZE, CELL_SIZE))
                        pygame.draw.rect(self.screen, COLORS['border'],
                            pygame.Rect((self.game.current_brick.x + x) * CELL_SIZE,
                                      (self.game.current_brick.y + y) * CELL_SIZE,
                                      CELL_SIZE, CELL_SIZE), 1)
            
            self.draw_preview_box()

        self.draw_buttons()
        self.draw_score_box(self.score_pos, "Score:", self.game.score)
        self.draw_score_box(self.high_score_pos, "High Score:", self.game.high_score)
        pygame.display.flip()

def main():
    screen = pygame.display.set_mode((WIDTH + 150, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    game = Tetris()
    renderer = Renderer(screen, game)

    normal_drop_time = 500
    fast_drop_time = 50
    drop_time = normal_drop_time
    last_drop = pygame.time.get_ticks()

    while True:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.save_high_score()
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN and game.running:
                if event.key == pygame.K_LEFT:
                    game.key_press_time['left'] = current_time
                    game.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game.key_press_time['right'] = current_time
                    game.move(1, 0)
                elif event.key == pygame.K_UP:
                    game.rotate_brick()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    game.key_press_time['left'] = 0
                elif event.key == pygame.K_RIGHT:
                    game.key_press_time['right'] = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if renderer.start_button_rect.collidepoint(mouse_pos) and not game.running:
                    game = Tetris()
                    renderer = Renderer(screen, game)
                    game.running = True
                elif renderer.restart_button_rect.collidepoint(mouse_pos):
                    game = Tetris()
                    renderer = Renderer(screen, game)
                    game.running = True

        if game.running:
            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_LEFT] and game.key_press_time['left']:
                game.handle_movement('left', current_time)
            if keys[pygame.K_RIGHT] and game.key_press_time['right']:
                game.handle_movement('right', current_time)
            
            drop_time = fast_drop_time if keys[pygame.K_DOWN] else normal_drop_time
            if current_time - last_drop > drop_time:
                game.move(0, 1)
                last_drop = current_time

        renderer.render()
        clock.tick(60)

if __name__ == "__main__":
    main()