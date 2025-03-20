import pygame
import random

# 初始化Pygame
pygame.init()

# 颜色定义
COLORS = [
    (0, 0, 0),  # 背景色
    (255, 0, 0),  # 红色
    (0, 150, 0),  # 绿色
    (0, 0, 255),  # 蓝色
    (255, 120, 0),  # 橙色
    (255, 255, 0),  # 黄色
    (180, 0, 255),  # 紫色
    (0, 220, 220)  # 青色
]
GAME_BG = (30, 30, 30)  # 游戏区背景
MENU_BG = (60, 60, 60)  # 菜单区背景

# 修正后的方块形状（S/Z型镜面对称）
SHAPES = [
    # I型
    [
        [(-2, 0), (-1, 0), (0, 0), (1, 0)],
        [(0, -2), (0, -1), (0, 0), (0, 1)],
        [(-2, 0), (-1, 0), (0, 0), (1, 0)],
        [(0, -2), (0, -1), (0, 0), (0, 1)]
    ],
    # O型
    [
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)]
    ],
    # T型
    [
        [(-1, 0), (0, 0), (1, 0), (0, 1)],
        [(0, 1), (0, 0), (0, -1), (1, 0)],
        [(-1, 0), (0, 0), (1, 0), (0, -1)],
        [(0, -1), (0, 0), (0, 1), (-1, 0)]
    ],
    # L型
    [
        [(-1, 0), (0, 0), (1, 0), (1, 1)],
        [(0, 1), (0, 0), (0, -1), (1, -1)],
        [(-1, -1), (-1, 0), (0, 0), (1, 0)],
        [(-1, 1), (0, 1), (0, 0), (0, -1)]
    ],
    # J型
    [
        [(-1, 0), (0, 0), (1, 0), (-1, 1)],
        [(0, 1), (0, 0), (0, -1), (-1, -1)],
        [(1, -1), (1, 0), (0, 0), (-1, 0)],
        [(0, -1), (0, 0), (0, 1), (1, 1)]
    ],
    # S型（修正）
    [
        # [(-1, 0), (0, 0), (0, 1), (1, 1)],
        # [(0, -1), (0, 0), (1, 0), (1, 1)],
        # [(-1, -1), (0, -1), (0, 0), (1, 0)],
        # [(-1, 0), (-1, 1), (0, 0), (0, -1)]
        [(-1, 0), (0, 0), (0, 1), (1, 1)],
        [(0, 1), (0, 0), (1, 0), (1, -1)],
        [(-1, 0), (0, 0), (0, 1), (1, 1)],
        [(0, 1), (0, 0), (1, 0), (1, -1)],
    ],
    # Z型（修正）
    [
        [(-1, 1), (0, 1), (0, 0), (1, 0)],
        [(1, 1), (1, 0), (0, 0), (0, -1)],
        [(-1, 1), (0, 1), (0, 0), (1, 0)],
        [(1, 1), (1, 0), (0, 0), (0, -1)],
    ]
]

SHAPE_COLORS = [1, 2, 3, 4, 5, 6, 7]

# 游戏常量
GRID_WIDTH = 20
GRID_HEIGHT = 20
BORDER = 2
FPS = 60
MENU_WIDTH = 200  # 固定菜单宽度

# 初始化全屏
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()

# 动态计算方块尺寸
BLOCK_SIZE = min(
    (WINDOW_WIDTH - MENU_WIDTH) // GRID_WIDTH,
    WINDOW_HEIGHT // GRID_HEIGHT
)
GAME_AREA_WIDTH = BLOCK_SIZE * GRID_WIDTH

pygame.display.set_caption("俄罗斯方块")
clock = pygame.time.Clock()


class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.rotation = 0
        self.color = SHAPE_COLORS[shape]


def check_collision(grid, piece, dx=0, dy=0, dr=0):
    """检查碰撞"""
    new_rotation = (piece.rotation + dr) % 4
    shape_rot = SHAPES[piece.shape][new_rotation]
    new_x = piece.x + dx
    new_y = piece.y + dy
    for (bx, by) in shape_rot:
        x = new_x + bx
        y = new_y + by
        if x < 0 or x >= GRID_WIDTH:
            return True
        if y >= GRID_HEIGHT:
            return True
        if y >= 0 and grid[y][x] != 0:
            return True
    return False


def fix_piece(grid, piece):
    """固定方块并返回是否游戏结束"""
    shape = SHAPES[piece.shape][piece.rotation]
    game_over = False
    for (bx, by) in shape:
        x = piece.x + bx
        y = piece.y + by
        if y < 0:  # 新增游戏结束判断
            game_over = True
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            grid[y][x] = piece.color
    return game_over


def clear_lines(grid):
    """消除满行"""
    lines_cleared = 0
    y = GRID_HEIGHT - 1
    while y >= 0:
        if all(cell != 0 for cell in grid[y]):
            del grid[y]
            grid.insert(0, [0] * GRID_WIDTH)
            lines_cleared += 1
        else:
            y -= 1
    return lines_cleared


def new_piece():
    """生成新方块"""
    shape = random.randint(0, 6)
    x = GRID_WIDTH // 2 - 1
    y = -2
    piece = Piece(x, y, shape)
    if check_collision(grid, piece):
        return None
    return piece


def draw_grid(screen, grid):
    """绘制游戏区"""
    pygame.draw.rect(screen, GAME_BG, (0, 0, GAME_AREA_WIDTH, WINDOW_HEIGHT))
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = COLORS[grid[y][x]]
            rect = (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - BORDER, BLOCK_SIZE - BORDER)
            pygame.draw.rect(screen, color, rect)


def draw_piece(screen, piece):
    """绘制当前方块"""
    shape = SHAPES[piece.shape][piece.rotation]
    color = COLORS[piece.color]
    for (bx, by) in shape:
        x = piece.x + bx
        y = piece.y + by
        if y >= 0:
            rect = (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - BORDER, BLOCK_SIZE - BORDER)
            pygame.draw.rect(screen, color, rect)


def draw_menu(screen, score):
    """绘制菜单区"""
    pygame.draw.rect(screen, MENU_BG, (GAME_AREA_WIDTH, 0, MENU_WIDTH, WINDOW_HEIGHT))
    font = pygame.font.SysFont('arial', BLOCK_SIZE)
    # 分数显示
    text = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(text, (GAME_AREA_WIDTH + 20, BLOCK_SIZE))
    # 操作说明
    controls = [
        "Operation Instructions:",
        "←/→: Move left/right",
        "↑  : Rotate",
        "↓  : Speed up"
    ]
    for i, line in enumerate(controls):
        text = font.render(line, True, (200, 200, 200))
        screen.blit(text, (GAME_AREA_WIDTH + 20, BLOCK_SIZE * 3 + i * BLOCK_SIZE))


def get_line_reward_factor(lines):
    if lines == 4:
        return 200
    elif lines == 3:
        return 150
    elif lines == 2:
        return 120
    else:
        return 100


# 游戏初始化
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
current_piece = new_piece()
fall_speed = 800
speed_multiplier = 15  # 加速倍率
score = 0
game_over = False
running = True
fall_time = pygame.time.get_ticks()
restart_timer = 0  # 新增重启计时器

# 移动控制参数
move_delay = 200  # 首次移动延迟
move_interval = 100  # 连续移动间隔
last_move = {
    pygame.K_LEFT: 0,
    pygame.K_RIGHT: 0
}

# 主循环
while running:
    current_time = pygame.time.get_ticks()
    keys = pygame.key.get_pressed()

    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            running = False
        elif event.type == pygame.KEYDOWN and not game_over:
            # 处理旋转（只响应单次按键）
            if event.key == pygame.K_UP and current_piece:
                if not check_collision(grid, current_piece, dr=1):
                    current_piece.rotation = (current_piece.rotation + 1) % 4

    if not game_over and current_piece:
        # 处理连续左右移动
        for key in [pygame.K_LEFT, pygame.K_RIGHT]:
            if keys[key]:
                time_since_last = current_time - last_move[key]
                if time_since_last > move_delay or (last_move[key] != 0 and time_since_last > move_interval):
                    dx = -1 if key == pygame.K_LEFT else 1
                    if not check_collision(grid, current_piece, dx=dx):
                        current_piece.x += dx
                    last_move[key] = current_time
            else:
                last_move[key] = 0

        # 处理加速下落
        current_fall_speed = fall_speed // speed_multiplier if keys[pygame.K_DOWN] else fall_speed
        if current_time - fall_time >= current_fall_speed:
            if not check_collision(grid, current_piece, dy=1):
                current_piece.y += 1
                fall_time = current_time
            else:
                # 修复游戏结束判断逻辑
                game_over_flag = fix_piece(grid, current_piece)
                lines = clear_lines(grid)
                score += lines * get_line_reward_factor(lines)

                # 同时检测两种结束条件
                current_piece = new_piece()
                if game_over_flag or not current_piece:
                    game_over = True
                    restart_timer = current_time

                fall_time = current_time

    # 游戏结束处理
    if game_over:
        # 绘制结束画面
        screen.fill(GAME_BG)
        draw_grid(screen, grid)
        draw_menu(screen, score)

        # 游戏结束文字
        font = pygame.font.SysFont('arial', BLOCK_SIZE * 2)
        text = font.render('Game Over', True, (255, 0, 0))
        text_rect = text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        screen.blit(text, text_rect)

        # 3秒后显示重启提示
        if current_time - restart_timer > 3000:
            font = pygame.font.SysFont('arial', BLOCK_SIZE // 2)
            text = font.render('Press any button to restart', True, (255, 255, 255))
            text_rect = text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + BLOCK_SIZE * 2))
            screen.blit(text, text_rect)

            # 检测重启按键
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # 重置游戏状态
                    grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
                    current_piece = new_piece()
                    score = 0
                    game_over = False
                    fall_time = pygame.time.get_ticks()

    else:
        # 正常游戏绘制
        screen.fill(GAME_BG)
        draw_grid(screen, grid)
        if current_piece:
            draw_piece(screen, current_piece)
        draw_menu(screen, score)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()