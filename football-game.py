import pygame
import sys
import math

# مقداردهی اولیه Pygame
pygame.init()

# تنظیمات صفحه (تمام‌صفحه)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_width(), screen.get_height()
pygame.display.set_caption("FOOTBALL")

# رنگ‌ها
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# اندازه زمین
FIELD_WIDTH = int(WIDTH * 0.9)
FIELD_HEIGHT = int(HEIGHT * 0.6)
FIELD_X = (WIDTH - FIELD_WIDTH) // 2
FIELD_Y = (HEIGHT - FIELD_HEIGHT) // 2

# مختصات و اندازه‌ها
PLAYER_SIZE = 30
BALL_SIZE = 15
GOAL_WIDTH = 300
GOAL_HEIGHT = 50
GOAL_BAR_WIDTH = 15
player_red_x, player_red_y = FIELD_X + FIELD_WIDTH // 2, FIELD_Y + FIELD_HEIGHT - 50  # بازیکن قرمز
player_blue_x, player_blue_y = FIELD_X + FIELD_WIDTH // 2, FIELD_Y + 50  # بازیکن آبی
ball_x, ball_y = FIELD_X + FIELD_WIDTH // 2, FIELD_Y + FIELD_HEIGHT // 2
player_speed = 8
ball_speed_x, ball_speed_y = 0, 0
BALL_FRICTION = 0.98

# امتیازات
red_score = 0
blue_score = 0
font = pygame.font.SysFont(None, 36)

# جوی‌استیک قرمز (پایین)
JOYSTICK_RADIUS = 130
JOYSTICK_RED_X = WIDTH // 2
JOYSTICK_RED_Y = HEIGHT - 170
joystick_red_base = pygame.Rect(JOYSTICK_RED_X - JOYSTICK_RADIUS, JOYSTICK_RED_Y - JOYSTICK_RADIUS, JOYSTICK_RADIUS * 2, JOYSTICK_RADIUS * 2)
joystick_red_pos = [JOYSTICK_RED_X, JOYSTICK_RED_Y]
joystick_red_active = False
red_touch_id = None

# جوی‌استیک آبی (بالا)
JOYSTICK_BLUE_X = WIDTH // 2
JOYSTICK_BLUE_Y = 170
joystick_blue_base = pygame.Rect(JOYSTICK_BLUE_X - JOYSTICK_RADIUS, JOYSTICK_BLUE_Y - JOYSTICK_RADIUS, JOYSTICK_RADIUS * 2, JOYSTICK_RADIUS * 2)
joystick_blue_pos = [JOYSTICK_BLUE_X, JOYSTICK_BLUE_Y]
joystick_blue_active = False
blue_touch_id = None

# حلقه اصلی بازی
clock = pygame.time.Clock()
running = True

def keep_inside_field(x, y, size, speed_x=0, speed_y=0):
    """محدود کردن حرکت به داخل زمین"""
    x = max(FIELD_X + size, min(FIELD_X + FIELD_WIDTH - size, x))
    y = max(FIELD_Y + size, min(FIELD_Y + FIELD_HEIGHT - size, y))
    if x <= FIELD_X + size or x >= FIELD_X + FIELD_WIDTH - size:
        speed_x *= -0.8
    if y <= FIELD_Y + size or y >= FIELD_Y + FIELD_HEIGHT - size:
        speed_y *= -0.8
    return x, y, speed_x, speed_y

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.FINGERDOWN:
            mx, my = event.x * WIDTH, event.y * HEIGHT
            if joystick_red_base.collidepoint(mx, my) and red_touch_id is None:
                red_touch_id = event.finger_id
                joystick_red_active = True
            elif joystick_blue_base.collidepoint(mx, my) and blue_touch_id is None:
                blue_touch_id = event.finger_id
                joystick_blue_active = True
        elif event.type == pygame.FINGERUP:
            if event.finger_id == red_touch_id:
                joystick_red_active = False
                joystick_red_pos = [JOYSTICK_RED_X, JOYSTICK_RED_Y]
                red_touch_id = None
            elif event.finger_id == blue_touch_id:
                joystick_blue_active = False
                joystick_blue_pos = [JOYSTICK_BLUE_X, JOYSTICK_BLUE_Y]
                blue_touch_id = None
        elif event.type == pygame.FINGERMOTION:
            mx, my = event.x * WIDTH, event.y * HEIGHT
            if event.finger_id == red_touch_id and joystick_red_active:
                dx = mx - JOYSTICK_RED_X
                dy = my - JOYSTICK_RED_Y
                dist = math.sqrt(dx ** 2 + dy ** 2)
                if dist > JOYSTICK_RADIUS:
                    dx = dx * JOYSTICK_RADIUS / dist
                    dy = dy * JOYSTICK_RADIUS / dist
                joystick_red_pos = [JOYSTICK_RED_X + dx, JOYSTICK_RED_Y + dy]
            elif event.finger_id == blue_touch_id and joystick_blue_active:
                dx = mx - JOYSTICK_BLUE_X
                dy = my - JOYSTICK_BLUE_Y
                dist = math.sqrt(dx ** 2 + dy ** 2)
                if dist > JOYSTICK_RADIUS:
                    dx = dx * JOYSTICK_RADIUS / dist
                    dy = dy * JOYSTICK_RADIUS / dist
                joystick_blue_pos = [JOYSTICK_BLUE_X + dx, JOYSTICK_BLUE_Y + dy]

    # حرکت بازیکن قرمز با جوی‌استیک
    if joystick_red_active:
        dx = joystick_red_pos[0] - JOYSTICK_RED_X
        dy = joystick_red_pos[1] - JOYSTICK_RED_Y
        if abs(dx) > 10:
            player_red_x += player_speed * (dx / JOYSTICK_RADIUS)
        if abs(dy) > 10:
            player_red_y += player_speed * (dy / JOYSTICK_RADIUS)
    player_red_x, player_red_y, _, _ = keep_inside_field(player_red_x, player_red_y, PLAYER_SIZE)

    # حرکت بازیکن آبی با جوی‌استیک
    if joystick_blue_active:
        dx = joystick_blue_pos[0] - JOYSTICK_BLUE_X
        dy = joystick_blue_pos[1] - JOYSTICK_BLUE_Y
        if abs(dx) > 10:
            player_blue_x += player_speed * (dx / JOYSTICK_RADIUS)
        if abs(dy) > 10:
            player_blue_y += player_speed * (dy / JOYSTICK_RADIUS)
    player_blue_x, player_blue_y, _, _ = keep_inside_field(player_blue_x, player_blue_y, PLAYER_SIZE)

    # حرکت و کاهش سرعت توپ
    ball_x += ball_speed_x
    ball_y += ball_speed_y
    ball_speed_x *= BALL_FRICTION
    ball_speed_y *= BALL_FRICTION
    if abs(ball_speed_x) < 0.1 and abs(ball_speed_y) < 0.1:
        ball_speed_x, ball_speed_y = 0, 0
    ball_x, ball_y, ball_speed_x, ball_speed_y = keep_inside_field(ball_x, ball_y, BALL_SIZE, ball_speed_x, ball_speed_y)

    # برخورد بازیکن‌ها با توپ
    red_rect = pygame.Rect(player_red_x - PLAYER_SIZE, player_red_y - PLAYER_SIZE, PLAYER_SIZE * 2, PLAYER_SIZE * 2)
    blue_rect = pygame.Rect(player_blue_x - PLAYER_SIZE, player_blue_y - PLAYER_SIZE, PLAYER_SIZE * 2, PLAYER_SIZE * 2)
    ball_rect = pygame.Rect(ball_x - BALL_SIZE, ball_y - BALL_SIZE, BALL_SIZE * 2, BALL_SIZE * 2)
    
    if red_rect.colliderect(ball_rect):
        angle = math.atan2(ball_y - player_red_y, ball_x - player_red_x)
        ball_speed_x = 15 * math.cos(angle) * 0.9
        ball_speed_y = 15 * math.sin(angle) * 0.9
    if blue_rect.colliderect(ball_rect):
        angle = math.atan2(ball_y - player_blue_y, ball_x - player_blue_x)
        ball_speed_x = 15 * math.cos(angle) * 0.9
        ball_speed_y = 15 * math.sin(angle) * 0.9

    # تعریف تیرها و قسمت باز دروازه
    goal_top_left_bar = pygame.Rect(FIELD_X + FIELD_WIDTH // 2 - GOAL_WIDTH // 2, FIELD_Y, GOAL_BAR_WIDTH, GOAL_HEIGHT)
    goal_top_right_bar = pygame.Rect(FIELD_X + FIELD_WIDTH // 2 + GOAL_WIDTH // 2 - GOAL_BAR_WIDTH, FIELD_Y, GOAL_BAR_WIDTH, GOAL_HEIGHT)
    goal_bottom_left_bar = pygame.Rect(FIELD_X + FIELD_WIDTH // 2 - GOAL_WIDTH // 2, FIELD_Y + FIELD_HEIGHT - GOAL_HEIGHT, GOAL_BAR_WIDTH, GOAL_HEIGHT)
    goal_bottom_right_bar = pygame.Rect(FIELD_X + FIELD_WIDTH // 2 + GOAL_WIDTH // 2 - GOAL_BAR_WIDTH, FIELD_Y + FIELD_HEIGHT - GOAL_HEIGHT, GOAL_BAR_WIDTH, GOAL_HEIGHT)
    goal_top_open = pygame.Rect(FIELD_X + FIELD_WIDTH // 2 - GOAL_WIDTH // 2 + GOAL_BAR_WIDTH, FIELD_Y, GOAL_WIDTH - 2 * GOAL_BAR_WIDTH, GOAL_HEIGHT)
    goal_bottom_open = pygame.Rect(FIELD_X + FIELD_WIDTH // 2 - GOAL_WIDTH // 2 + GOAL_BAR_WIDTH, FIELD_Y + FIELD_HEIGHT - GOAL_HEIGHT, GOAL_WIDTH - 2 * GOAL_BAR_WIDTH, GOAL_HEIGHT)

    # چک کردن گل و برخورد با تیرها
    if goal_top_open.colliderect(ball_rect) and ball_speed_y < 0 and ball_y > FIELD_Y:
        red_score += 1
        ball_x, ball_y = FIELD_X + FIELD_WIDTH // 2, FIELD_Y + FIELD_HEIGHT // 2
        ball_speed_x, ball_speed_y = 0, 0
        player_red_x, player_red_y = FIELD_X + FIELD_WIDTH // 2, FIELD_Y + FIELD_HEIGHT - 50  # بازیکن قرمز
        player_blue_x, player_blue_y = FIELD_X + FIELD_WIDTH // 2, FIELD_Y + 50  # بازیکن آبی
    elif goal_bottom_open.colliderect(ball_rect) and ball_speed_y > 0 and ball_y < FIELD_Y + FIELD_HEIGHT - GOAL_HEIGHT:
        blue_score += 1
        ball_x, ball_y = FIELD_X + FIELD_WIDTH // 2, FIELD_Y + FIELD_HEIGHT // 2
        ball_speed_x, ball_speed_y = 0, 0
    elif goal_top_left_bar.colliderect(ball_rect) or goal_bottom_left_bar.colliderect(ball_rect):
        ball_speed_x = -abs(ball_speed_x) * 0.8
    elif goal_top_right_bar.colliderect(ball_rect) or goal_bottom_right_bar.colliderect(ball_rect):
        ball_speed_x = abs(ball_speed_x) * 0.8

    # رسم صفحه
    screen.fill(WHITE)

    # رسم زمین
    pygame.draw.rect(screen, WHITE, (FIELD_X, FIELD_Y, FIELD_WIDTH, FIELD_HEIGHT))
    pygame.draw.rect(screen, BLACK, (FIELD_X, FIELD_Y, FIELD_WIDTH, FIELD_HEIGHT), 10)
    pygame.draw.line(screen, BLACK, (FIELD_X + FIELD_WIDTH // 2, FIELD_Y), (FIELD_X + FIELD_WIDTH // 2, FIELD_Y + FIELD_HEIGHT), 5)
    pygame.draw.circle(screen, BLACK, (FIELD_X + FIELD_WIDTH // 2, FIELD_Y + FIELD_HEIGHT // 2), 150, 5)

    # رسم دروازه‌ها
    pygame.draw.rect(screen, BLACK, (FIELD_X + FIELD_WIDTH // 2 - GOAL_WIDTH // 2, FIELD_Y, GOAL_WIDTH, GOAL_HEIGHT))
    pygame.draw.rect(screen, BLUE, goal_top_left_bar)
    pygame.draw.rect(screen, BLUE, goal_top_right_bar)
    pygame.draw.line(screen, WHITE, (FIELD_X + FIELD_WIDTH // 2 - GOAL_WIDTH // 2 + GOAL_BAR_WIDTH, FIELD_Y + GOAL_HEIGHT), 
                     (FIELD_X + FIELD_WIDTH // 2 + GOAL_WIDTH // 2 - GOAL_BAR_WIDTH, FIELD_Y + GOAL_HEIGHT), 2)
    pygame.draw.rect(screen, BLACK, (FIELD_X + FIELD_WIDTH // 2 - GOAL_WIDTH // 2, FIELD_Y + FIELD_HEIGHT - GOAL_HEIGHT, GOAL_WIDTH, GOAL_HEIGHT))
    pygame.draw.rect(screen, RED, goal_bottom_left_bar)
    pygame.draw.rect(screen, RED, goal_bottom_right_bar)
    pygame.draw.line(screen, WHITE, (FIELD_X + FIELD_WIDTH // 2 - GOAL_WIDTH // 2 + GOAL_BAR_WIDTH, FIELD_Y + FIELD_HEIGHT - GOAL_HEIGHT), 
                     (FIELD_X + FIELD_WIDTH // 2 + GOAL_WIDTH // 2 - GOAL_BAR_WIDTH, FIELD_Y + FIELD_HEIGHT - GOAL_HEIGHT), 2)

    # رسم بازیکن‌ها و توپ
    pygame.draw.circle(screen, RED, (int(player_red_x), int(player_red_y)), PLAYER_SIZE)
    pygame.draw.circle(screen, BLUE, (int(player_blue_x), int(player_blue_y)), PLAYER_SIZE)
    pygame.draw.circle(screen, BLACK, (int(ball_x), int(ball_y)), BALL_SIZE)

    # رسم کادر امتیاز قرمز (بالا سمت چپ)
    red_box_border = pygame.Rect(FIELD_X - 2, FIELD_Y - 62, 84, 44)
    red_box = pygame.Rect(FIELD_X, FIELD_Y - 60, 80, 40)
    pygame.draw.rect(screen, BLACK, red_box_border, border_radius=100)
    pygame.draw.rect(screen, RED, red_box, border_radius=100)
    red_text = font.render(str(red_score), True, WHITE)
    screen.blit(red_text, (FIELD_X + 40 - red_text.get_width() // 2, FIELD_Y - 50))

    # رسم کادر امتیاز آبی (پایین سمت راست - برعکس)
    blue_box_surface = pygame.Surface((84, 44), pygame.SRCALPHA)  # سطح جداگانه برای کادر آبی
    pygame.draw.rect(blue_box_surface, BLACK, (0, 0, 84, 44), border_radius=100)  # کادر بیرونی
    pygame.draw.rect(blue_box_surface, BLUE, (2, 2, 80, 40), border_radius=100)  # کادر داخلی
    blue_text = font.render(str(blue_score), True, WHITE)
    blue_box_surface.blit(blue_text, (42 - blue_text.get_width() // 2, 22 - blue_text.get_height() // 2))  # متن در مرکز سطح
    blue_box_rotated = pygame.transform.rotate(blue_box_surface, 180)  # چرخاندن کل کادر
    screen.blit(blue_box_rotated, (FIELD_X + FIELD_WIDTH - 84, FIELD_Y + FIELD_HEIGHT + 20))  # قرار دادن در موقعیت

    # رسم جوی‌استیک‌ها
    pygame.draw.circle(screen, WHITE, (JOYSTICK_RED_X, JOYSTICK_RED_Y), JOYSTICK_RADIUS)
    pygame.draw.circle(screen, BLACK, (JOYSTICK_RED_X, JOYSTICK_RED_Y), JOYSTICK_RADIUS, 5)
    pygame.draw.circle(screen, RED, (int(joystick_red_pos[0]), int(joystick_red_pos[1])), JOYSTICK_RADIUS // 2)
    pygame.draw.circle(screen, WHITE, (JOYSTICK_BLUE_X, JOYSTICK_BLUE_Y), JOYSTICK_RADIUS)
    pygame.draw.circle(screen, BLACK, (JOYSTICK_BLUE_X, JOYSTICK_BLUE_Y), JOYSTICK_RADIUS, 5)
    pygame.draw.circle(screen, BLUE, (int(joystick_blue_pos[0]), int(joystick_blue_pos[1])), JOYSTICK_RADIUS // 2)

    # آپدیت صفحه
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
