import pygame
import sys

# تنظیمات اولیه و مقادیر قابل تغییر
pygame.init()

# تنظیمات بازی
WINDOW_WIDTH, WINDOW_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
GAME_WIDTH = 1000
GAME_HEIGHT = 1200
control_panel_height = 200

# رنگ‌ها
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 102, 204)
GREEN = (0, 204, 102)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (169, 169, 169)

# تنظیمات توپ
ball_radius = 15
ball_speed = [8, 8]

# تنظیمات پدال
paddle_width = 200
paddle_height = 15
paddle_speed = 15

# تنظیمات بلوک‌ها
block_rows = 20
block_cols = 10
block_width = (GAME_WIDTH - 20) // block_cols - 10
block_height = 20
total_blocks_width = block_cols * (block_width + 10) - 10
blocks_offset_x = (GAME_WIDTH - total_blocks_width) // 2

# وضعیت بازی
move_left = False
move_right = False
game_over = False
game_won = False

# تنظیمات صفحه نمایش
game_x = (WINDOW_WIDTH - GAME_WIDTH) // 2
game_y = (WINDOW_HEIGHT - GAME_HEIGHT) // 2
control_panel_y = game_y + GAME_HEIGHT + 15
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Breakout Game")
clock = pygame.time.Clock()

# توابع کمکی

def draw_button(rect, text, text_color, button_color):
    """ رسم دکمه‌ها """
    pygame.draw.rect(screen, button_color, rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, rect, 3, border_radius=10)
    font = pygame.font.SysFont(None, 40)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def show_message(message, button_text):
    """ نمایش پیغام‌های برد/باخت """
    message_rect = pygame.Rect((WINDOW_WIDTH - 600) // 2, (WINDOW_HEIGHT - 200) // 2, 600, 200)
    pygame.draw.rect(screen, DARK_GRAY, message_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, message_rect, 5, border_radius=10)

    font = pygame.font.SysFont(None, 100)
    text_surface = font.render(message, True, WHITE)
    text_rect = text_surface.get_rect(center=(message_rect.centerx, message_rect.top + 60))
    screen.blit(text_surface, text_rect)

    button_rect = pygame.Rect(message_rect.centerx - 200, message_rect.bottom - 80, 400, 50)
    draw_button(button_rect, button_text, BLACK, GREEN)

    return button_rect

def reset_game():
    """ ریست کردن بازی """
    global ball_pos, ball_speed, paddle_pos, blocks, game_over, game_won
    ball_pos = [GAME_WIDTH // 2, GAME_HEIGHT // 2]
    ball_speed = [8, 8]
    paddle_pos = [GAME_WIDTH // 2 - paddle_width // 2, GAME_HEIGHT - 30]
    blocks = [
        pygame.Rect(blocks_offset_x + col * (block_width + 10), 10 + row * (block_height + 10), block_width, block_height)
        for row in range(block_rows) for col in range(block_cols)
    ]
    game_over = False
    game_won = False

# تنظیمات اولیه بازی
ball_pos = [GAME_WIDTH // 2, GAME_HEIGHT // 2]
paddle_pos = [GAME_WIDTH // 2 - paddle_width // 2, GAME_HEIGHT - 30]
blocks = [
    pygame.Rect(blocks_offset_x + col * (block_width + 10), 10 + row * (block_height + 10), block_width, block_height)
    for row in range(block_rows) for col in range(block_cols)
]

# تابع برای چک کردن برخورد توپ با دیوارها
def check_ball_collision():
    """ بررسی برخورد توپ با دیوارها """
    global ball_speed, game_over
    if ball_pos[0] <= ball_radius or ball_pos[0] >= GAME_WIDTH - ball_radius:
        ball_speed[0] = -ball_speed[0]
    if ball_pos[1] <= ball_radius:
        ball_speed[1] = -ball_speed[1]
    if ball_pos[1] >= GAME_HEIGHT - ball_radius:
        game_over = True  # باخت

# تابع برای برخورد توپ با پدال
def check_paddle_collision():
    """ بررسی برخورد توپ با پدال """
    global ball_speed
    paddle_rect = pygame.Rect(paddle_pos[0], paddle_pos[1], paddle_width, paddle_height)
    if paddle_rect.colliderect(pygame.Rect(ball_pos[0] - ball_radius, ball_pos[1] - ball_radius, ball_radius * 2, ball_radius * 2)):
        ball_speed[1] = -ball_speed[1]
        # محاسبه سرعت توپ هنگام برخورد با پدال
        ball_speed[0] += (ball_pos[0] - (paddle_pos[0] + paddle_width / 2)) / paddle_width * 2

# تابع برای برخورد توپ با بلوک‌ها
def check_block_collision():
    """ بررسی برخورد توپ با بلوک‌ها """
    global ball_speed
    for block in blocks[:]:
        if pygame.Rect(block).colliderect(pygame.Rect(ball_pos[0] - ball_radius, ball_pos[1] - ball_radius, ball_radius * 2, ball_radius * 2)):
            blocks.remove(block)
            ball_speed[1] = -ball_speed[1]
            break

# حلقه اصلی بازی
running = True
while running:
    screen.fill(WHITE)

    game_rect = pygame.Rect(game_x, game_y, GAME_WIDTH, GAME_HEIGHT)
    pygame.draw.rect(screen, LIGHT_GRAY, game_rect)
    pygame.draw.rect(screen, DARK_GRAY, game_rect, 5)

    if not (game_over or game_won):
        control_panel_rect = pygame.Rect(game_x, control_panel_y, GAME_WIDTH, control_panel_height)
        pygame.draw.rect(screen, LIGHT_GRAY, control_panel_rect)
        pygame.draw.rect(screen, DARK_GRAY, control_panel_rect, 5)

        # فاصله بین دکمه‌ها (کاهش فاصله بین خود دکمه‌ها)
        button_width = 300
        button_height = 120
        button_spacing = 100  # فاصله بین دکمه‌ها از هم
        total_buttons_width = 2 * button_width + button_spacing  # مجموع عرض دکمه‌ها با فاصله
        left_button = pygame.Rect(game_x + (GAME_WIDTH - total_buttons_width) // 2, control_panel_y + (control_panel_height - button_height) // 2, button_width, button_height)
        right_button = pygame.Rect(left_button.right + button_spacing, control_panel_y + (control_panel_height - button_height) // 2, button_width, button_height)

        draw_button(left_button, "Left", WHITE, DARK_GRAY)
        draw_button(right_button, "Right", WHITE, DARK_GRAY)

    # دریافت ورودی‌ها
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_over or game_won:
                replay_button = show_message("Play Again?", "Replay")
                if replay_button.collidepoint(event.pos):
                    reset_game()
            if not (game_over or game_won):
                if left_button.collidepoint(event.pos):
                    move_left = True
                elif right_button.collidepoint(event.pos):
                    move_right = True
        elif event.type == pygame.MOUSEBUTTONUP:
            move_left = False
            move_right = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                move_left = True
            elif event.key == pygame.K_RIGHT:
                move_right = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                move_left = False
            elif event.key == pygame.K_RIGHT:
                move_right = False

    if game_over or game_won:
        message = "You Won!" if game_won else "Game Over!"
        replay_button = show_message(message, "Replay")
        pygame.display.flip()
        continue

    # حرکت پدال
    if move_left:
        paddle_pos[0] = max(paddle_pos[0] - paddle_speed, 0)
    if move_right:
        paddle_pos[0] = min(paddle_pos[0] + paddle_speed, GAME_WIDTH - paddle_width)

    # حرکت توپ
    ball_pos[0] += ball_speed[0]
    ball_pos[1] += ball_speed[1]

    # بررسی برخورد توپ با دیوارها، پدال و بلوک‌ها
    check_ball_collision()
    check_paddle_collision()
    check_block_collision()

    if not blocks:
        game_won = True

    # رسم بلوک‌ها
    for block in blocks:
        pygame.draw.rect(screen, GREEN, block.move(game_x, game_y))
        pygame.draw.rect(screen, WHITE, block.move(game_x, game_y), 2)

    # رسم پدال و توپ
    pygame.draw.rect(screen, BLUE, pygame.Rect(paddle_pos[0], paddle_pos[1], paddle_width, paddle_height).move(game_x, game_y), border_radius=10)
    pygame.draw.circle(screen, RED, (ball_pos[0] + game_x, ball_pos[1] + game_y), ball_radius)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
