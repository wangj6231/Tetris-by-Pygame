import pygame
import random

pygame.init()
WIDTH, HEIGHT = 400, 760
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
    def __init__(self, player_name):
        self.player_name = player_name
        self.grid = [[0] * ROWS for _ in range(COLUMNS)]
        self.current_brick = Brick()
        self.next_brick = Brick()
        self.running = False
        self.score = 0
        self.high_score = self.load_high_score()
        self.last_move_time = {'left': 0, 'right': 0}
        self.key_press_time = {'left': 0, 'right': 0}
        self.game_over = False
        self.paused = False

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
            self.game_over = True

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

    def get_drop_position(self):
        drop_brick = Brick()
        drop_brick.shape = self.current_brick.shape
        drop_brick.color = self.current_brick.color
        drop_brick.x = self.current_brick.x
        drop_brick.y = self.current_brick.y

        while self.is_valid_position(drop_brick, 0, 1):
            drop_brick.y += 1
        
        return drop_brick

    def toggle_pause(self):
        self.paused = not self.paused

class Renderer:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.start_button_rect = pygame.Rect(WIDTH + 5, HEIGHT // 2 + 30, 100, 40)
        self.restart_button_rect = pygame.Rect(WIDTH + 5, HEIGHT // 2 + 100, 100, 40)
        self.pause_button_rect = pygame.Rect(WIDTH + 5, HEIGHT // 2 + 170, 100, 40)
        self.preview_pos = (WIDTH + 10, 80)
        self.score_pos = (WIDTH + 10, 210)
        self.high_score_pos = (WIDTH + 10, 290)
        self.hint_pos = (WIDTH + 10, HEIGHT // 2 + 240)
        self.controls_pos = (WIDTH + 10, HEIGHT // 2 + 280)
        self.player_name_pos = (WIDTH + 10, 10)

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

        self.draw_player_name()

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

        pygame.draw.rect(self.screen, COLORS['button_start'], self.pause_button_rect)
        pause_text = font.render("PAUSE", True, COLORS['text'])
        self.screen.blit(pause_text, (self.pause_button_rect.x + 20, 
                                     self.pause_button_rect.y + 10))

    def draw_game_over(self):
        font = pygame.font.SysFont("Arial", 40, bold=True)
        text = font.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text, text_rect)

    def draw_hint_box(self):
        font = pygame.font.SysFont("Arial", 16)
        hint_text = font.render("Press 'START' to begin", True, COLORS['text'])
        self.screen.blit(hint_text, (self.hint_pos[0], self.hint_pos[1]))

    def draw_controls_box(self):
        font = pygame.font.SysFont("Arial", 16)
        controls_text = [
            "Left : Move Left",
            "Right : Move Right",
            "Up : Rotate",
            "Down : Fast Drop",
            "P: Pause"
        ]
        for i, line in enumerate(controls_text):
            text = font.render(line, True, COLORS['text'])
            self.screen.blit(text, (self.controls_pos[0], self.controls_pos[1] + i * 20))

    def draw_player_name(self):
        font = pygame.font.SysFont("Arial", 20)
        name_text = font.render(f"Player: {self.game.player_name}", True, COLORS['text'])
        self.screen.blit(name_text, (self.preview_pos[0], self.preview_pos[1] - 60))

    def render(self):
        self.screen.fill(COLORS['background'])
        self.draw_grid()
        
        if self.game.running:
            drop_brick = self.game.get_drop_position()
            for y, row in enumerate(drop_brick.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, 
                                         (200, 200, 200),
                                         pygame.Rect((drop_brick.x + x) * CELL_SIZE, 
                                                     (drop_brick.y + y) * CELL_SIZE, 
                                                     CELL_SIZE, CELL_SIZE), 1)
            
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
        else:
            if self.game.game_over:
                self.draw_game_over()

        self.draw_score_box(self.score_pos, "Score", self.game.score)
        self.draw_score_box(self.high_score_pos, "High Score", self.game.high_score)
        self.draw_preview_box()
        self.draw_buttons()
        self.draw_hint_box()
        self.draw_controls_box()
        pygame.display.flip()

def draw_initial_screen(screen, input_box, player_name, active):
    screen.fill(COLORS['background'])
    font = pygame.font.SysFont("Arial", 40)
    text_surface = font.render("Enter your name:", True, COLORS['text'])
    screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2 - 100))
    
    color = COLORS['text'] if active else COLORS['grid']
    pygame.draw.rect(screen, color, input_box, 2)
    name_surface = font.render(player_name, True, (255, 255, 255))
    screen.blit(name_surface, (input_box.x + 5, input_box.y + 5))
    
    pygame.display.flip()

def main():
    screen = pygame.display.set_mode((WIDTH + 150, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    player_name = ""
    active = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        game = Tetris(player_name)
                        renderer = Renderer(screen, game)
                        game.running = True
                        game_loop(screen, clock, game, renderer)
                        return  # Exit the initial screen loop
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        player_name += event.unicode

        draw_initial_screen(screen, input_box, player_name, active)
        clock.tick(30)

def game_loop(screen, clock, game, renderer):
    normal_drop_time = 500
    fast_drop_time = 15
    drop_time = normal_drop_time
    last_drop = pygame.time.get_ticks()

    while True:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.save_high_score()
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game.toggle_pause()
                elif game.running and not game.paused:
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
                    game = Tetris(game.player_name)
                    renderer = Renderer(screen, game)
                    game.running = True
                elif renderer.restart_button_rect.collidepoint(mouse_pos):
                    game = Tetris(game.player_name)
                    renderer = Renderer(screen, game)
                    game.running = True
                elif renderer.pause_button_rect.collidepoint(mouse_pos) and game.running:
                    game.toggle_pause()

        if game.running and not game.paused:
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