# 如何使用 Pygame 開發簡單的俄羅斯方塊

## 環境準備

首先，確保你已經安裝了 Pygame。

```bash
pip install pygame
```

## 遊戲的基本結構

俄羅斯方塊遊戲可以分為以下幾個核心部分：

1. **遊戲窗口**：創建視覺介面。
2. **方塊邏輯**：生成與控制俄羅斯方塊。
3. **遊戲網格**：管理固定方塊的位置和碰撞檢測。
4. **得分系統**：計算玩家的得分並顯示。
5. **渲染功能**：將遊戲元素畫在屏幕上。
6. **輸入控制**：處理玩家的鍵盤輸入。
7. **高分榜**：顯示最高分數。
8. **資料庫**：儲存用戶資料和高分。

## 實現細節

### 1. 設置遊戲窗口與參數

首先，我們需要定義一些基本參數，如窗口尺寸、網格單元大小，以及顏色。

```python
import pygame
import random
import sqlite3

pygame.init()

# 基本參數
WIDTH, HEIGHT = 400, 760
CELL_SIZE = 30
COLUMNS, ROWS = 10, HEIGHT // CELL_SIZE

# 顏色定義
COLORS = {
    'background': (0, 0, 0),
    'grid': (30, 30, 30),
    'text': (200, 200, 200),
    'button_start': (0, 150, 0),
    'button_restart': (150, 100, 0),
    'border': (50, 50, 50)
}
```

### 2. 定義俄羅斯方塊的形狀與顏色

俄羅斯方塊由不同形狀的方塊組成，我們可以用二維數組表示它們：

```python
# 方塊形狀
SHAPES = [
    [[1, 1, 1, 1]],           # I
    [[1, 1], [1, 1]],         # O
    [[0, 1, 1], [1, 1, 0]],   # S
    [[1, 1, 0], [0, 1, 1]],   # Z
    [[1, 0, 0], [1, 1, 1]],   # L
    [[0, 0, 1], [1, 1, 1]],   # J
    [[0, 1, 0], [1, 1, 1]]    # T
]

# 方塊顏色
PIECE_COLORS = [
    (0, 255, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 0),
    (255, 100, 100),
    (100, 100, 255),
    (255, 165, 0)
]
```

### 3. 創建遊戲對象類

俄羅斯方塊的運行依賴於兩個主要類別：

1. **Brick 類**：負責單個方塊的生成與旋轉。
2. **Tetris 類**：負責遊戲網格、碰撞檢測、得分計算等。

```python
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

    def load_high_score(self):
        conn = sqlite3.connect('tetris.db')
        cursor = conn.cursor()
        cursor.execute('SELECT high_score FROM users WHERE username = ?', (self.player_name,))
        high_score = cursor.fetchone()[0]
        conn.close()
        return high_score

    def save_high_score(self):
        conn = sqlite3.connect('tetris.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET high_score = ? WHERE username = ?', (self.high_score, self.player_name))
        conn.commit()
        conn.close()

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
```

### 4. 繪製遊戲畫面

使用 Pygame 的繪圖功能來渲染遊戲網格、方塊和分數框。

```python
class Renderer:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game

    def draw_grid(self):
        for x in range(COLUMNS):
            for y in range(ROWS):
                color = self.game.grid[x][y] if self.game.grid[x][y] else COLORS['grid']
                pygame.draw.rect(self.screen, color,
                                 pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def render(self):
        self.screen.fill(COLORS['background'])
        self.draw_grid()
        pygame.display.flip()
```

### 5. 主遊戲循環

實現遊戲的主循環，處理事件、更新狀態並渲染畫面。

```python
def main():
    init_db()
    screen = pygame.display.set_mode((WIDTH + 150, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    game = Tetris("Player")
    renderer = Renderer(screen, game)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        if game.running:
            game.move(0, 1)

        renderer.render()
        clock.tick(60)

if __name__ == "__main__":
    main()
```

### 6. 高分榜

顯示最高分數。

```python
def get_high_scores(limit=10):
    conn = sqlite3.connect('tetris.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, high_score FROM users ORDER BY high_score DESC LIMIT ?', (limit,))
    high_scores = cursor.fetchall()
    conn.close()
    return high_scores

class Renderer:
    # ...existing code...

    def draw_high_scores(self):
        high_scores = get_high_scores()
        font = pygame.font.SysFont("Arial", 20)
        title_surface = font.render("High Scores", True, COLORS['text'])
        self.screen.blit(title_surface, (WIDTH + 10, 350))

        for i, (username, score) in enumerate(high_scores):
            score_text = font.render(f"{i + 1}. {username}: {score}", True, COLORS['text'])
            self.screen.blit(score_text, (WIDTH + 10, 380 + i * 30))

    def render(self):
        self.screen.fill(COLORS['background'])
        self.draw_grid()
        # ...existing code...
        self.draw_high_scores()
        pygame.display.flip()
```

### 7. 資料庫初始化

初始化資料庫，儲存用戶資料和高分。

```python
def init_db():
    conn = sqlite3.connect('tetris.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        high_score INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()
```

## 資料庫介紹

在這個專案中，我們使用 SQLite 資料庫來儲存用戶資料和高分。SQLite 是一個輕量級的資料庫，適合用於小型應用程式。以下是資料庫的初始化和使用方法：

1. **初始化資料庫**：在程式開始時，呼叫 `init_db` 函數來創建資料庫和表格。
2. **註冊用戶**：使用 `register_user` 函數來新增用戶資料。
3. **用戶登入**：使用 `login_user` 函數來驗證用戶身份。
4. **儲存高分**：在遊戲結束時，使用 `save_high_score` 函數來更新用戶的最高分數。
5. **獲取高分榜**：使用 `get_high_scores` 函數來獲取最高分數的用戶列表。

## 改進建議

1. **增加聲音效果**：為方塊移動、旋轉和消除增加音效。
2. **增加難度曲線**：隨著遊戲進行，逐漸提高方塊下落的速度。
3. **高分榜**：保存最高分數，讓玩家可以挑戰自己或他人。
4. **自適應屏幕大小**：允許遊戲適應不同分辨率的屏幕。

## 總結

通過本教學，你學會了如何用 Pygame 開發一個基礎的俄羅斯方塊遊戲。我們使用了 Pygame 的繪圖與事件處理功能來構建遊戲邏輯與視覺效果，並展示了如何管理遊戲狀態。如果你有更多創意，可以進一步擴展這個遊戲，例如增加特別道具、多人對戰模式等。

## 開源資源

如果你希望直接查看完整的代碼或進一步學習，請參考以下開源資源：

- **GitHub 開源代碼** - [Tetris by Pygame](https://github.com/wangj6231/Tetris-by-Pygame)
  此代碼庫包含完整的俄羅斯方塊遊戲實現，包括多種進階功能，適合作為學習和改進的基礎。

