import pygame
import math

# مقداردهی اولیه Pygame و تنظیمات اولیه
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Car Game")

# رنگ‌ها و متغیرهای ثابت
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (120, 120, 120)
LIGHT_GRAY = (200, 200, 200)
SHADOW = (50, 50, 50, 100)

# اندازه‌های بزرگ‌تر
car_radius = 50
car_x = WIDTH // 2
car_y = HEIGHT // 2 + 400
car_max_speed = 12
car_acceleration = 0.4
car_friction = 0.04
car_angle = 0
car_velocity_x = 0
car_velocity_y = 0

# مختصات پیست بیضی بزرگ‌تر
track_center_x = WIDTH // 2
track_center_y = HEIGHT // 2 - 200
track_a = 500
track_b = 700
track_thickness = 150
track_inner_a = track_a - track_thickness
track_inner_b = track_b - track_thickness
track_border_thickness = 20

# جوی‌استیک بزرگ‌تر
joystick_center = (WIDTH // 2, HEIGHT - 300)
joystick_radius = 160
joystick_handle_radius = 70
joystick_active = False
joystick_x = joystick_center[0]
joystick_y = joystick_center[1]

# تصویر ماشین با جزئیات بیشتر
car_image = pygame.Surface((car_radius * 2, car_radius * 2), pygame.SRCALPHA)
pygame.draw.rect(car_image, RED, (car_radius - 15, car_radius - 30, 30, 60))
pygame.draw.circle(car_image, BLACK, (car_radius - 15, car_radius - 30), 12)
pygame.draw.circle(car_image, BLACK, (car_radius + 15, car_radius - 30), 12)
pygame.draw.circle(car_image, BLACK, (car_radius - 15, car_radius + 30), 12)
pygame.draw.circle(car_image, BLACK, (car_radius + 15, car_radius + 30), 12)
car_image_original = car_image.copy()

# سایه ماشین
shadow_image = pygame.Surface((car_radius * 2, car_radius * 2), pygame.SRCALPHA)
pygame.draw.ellipse(shadow_image, SHADOW, (0, 0, car_radius * 2, car_radius * 2))

# حلقه اصلی بازی
clock = pygame.time.Clock()
running = True

def get_ellipse_value(x, y, a, b):
    return ((x - track_center_x) ** 2 / a ** 2 + (y - track_center_y) ** 2 / b ** 2)

def is_inside_track(x, y):
    outer_value = get_ellipse_value(x, y, track_a, track_b)
    inner_value = get_ellipse_value(x, y, track_inner_a, track_inner_b)
    return outer_value <= 1 and inner_value >= 1

def handle_collision(new_x, new_y, old_x, old_y):
    velocity = pygame.math.Vector2(car_velocity_x, car_velocity_y)
    if velocity.length() == 0:
        return old_x, old_y, 0, 0

    outer_value = get_ellipse_value(new_x, new_y, track_a, track_b)
    inner_value = get_ellipse_value(new_x, new_y, track_inner_a, track_inner_b)

    if outer_value > 1:
        dx = 2 * (new_x - track_center_x) / (track_a ** 2)
        dy = 2 * (new_y - track_center_y) / (track_b ** 2)
        normal = pygame.math.Vector2(dx, dy).normalize()
    elif inner_value < 1:
        dx = 2 * (new_x - track_center_x) / (track_inner_a ** 2)
        dy = 2 * (new_y - track_center_y) / (track_inner_b ** 2)
        normal = pygame.math.Vector2(dx, dy).normalize() * -1
    else:
        return new_x, new_y, car_velocity_x, car_velocity_y

    velocity_tangent = velocity - velocity.project(normal)
    velocity_normal = velocity.project(normal)
    new_velocity = velocity_tangent * 0.95 - velocity_normal * 0.3

    correction_factor = car_radius * 0.1
    while not is_inside_track(new_x, new_y):
        new_x -= normal.x * correction_factor
        new_y -= normal.y * correction_factor

    return new_x, new_y, new_velocity.x, new_velocity.y

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            distance = math.hypot(mx - joystick_center[0], my - joystick_center[1])
            if distance <= joystick_radius:
                joystick_active = True
        elif event.type == pygame.MOUSEBUTTONUP:
            joystick_active = False
            joystick_x = joystick_center[0]
            joystick_y = joystick_center[1]
        elif event.type == pygame.MOUSEMOTION and joystick_active:
            mx, my = pygame.mouse.get_pos()
            dx = mx - joystick_center[0]
            dy = my - joystick_center[1]
            distance = math.hypot(dx, dy)
            if distance > joystick_radius:
                angle = math.atan2(dy, dx)
                joystick_x = joystick_center[0] + math.cos(angle) * joystick_radius
                joystick_y = joystick_center[1] + math.sin(angle) * joystick_radius
            else:
                joystick_x = mx
                joystick_y = my

    # حرکت ماشین
    if joystick_active:
        dx = joystick_x - joystick_center[0]
        dy = joystick_y - joystick_center[1]
        distance = math.hypot(dx, dy)
        if distance > 0:
            angle = math.atan2(dy, dx)
            accel_factor = min(distance / joystick_radius, 1)
            car_velocity_x += math.cos(angle) * car_acceleration * accel_factor
            car_velocity_y += math.sin(angle) * car_acceleration * accel_factor
            target_angle = math.degrees(angle) - 90
            angle_diff = (target_angle - car_angle) % 360
            if angle_diff > 180:
                angle_diff -= 360
            car_angle += angle_diff * 0.15
    else:
        car_velocity_x *= (1 - car_friction)
        car_velocity_y *= (1 - car_friction)

    speed = math.hypot(car_velocity_x, car_velocity_y)
    if speed > car_max_speed:
        car_velocity_x = car_velocity_x * car_max_speed / speed
        car_velocity_y = car_velocity_y * car_max_speed / speed

    new_car_x = car_x + car_velocity_x
    new_car_y = car_y + car_velocity_y

    # مدیریت برخورد
    car_x, car_y, car_velocity_x, car_velocity_y = handle_collision(new_car_x, new_car_y, car_x, car_y)

    # رسم صفحه
    screen.fill(WHITE)

    # رسم پیست یک‌رنگ با نوار تیره در لبه‌های داخلی و خارجی
    pygame.draw.ellipse(screen, LIGHT_GRAY, (track_center_x - track_a, track_center_y - track_b, 
                                             track_a * 2, track_b * 2))  # پیست خاکستری روشن
    pygame.draw.ellipse(screen, WHITE, (track_center_x - track_inner_a, track_center_y - track_inner_b, 
                                        track_inner_a * 2, track_inner_b * 2))  # فضای داخلی سفید
    pygame.draw.ellipse(screen, DARK_GRAY, (track_center_x - track_a, track_center_y - track_b, 
                                            track_a * 2, track_b * 2), track_border_thickness)  # نوار تیره خارجی
    pygame.draw.ellipse(screen, DARK_GRAY, (track_center_x - track_inner_a, track_center_y - track_inner_b, 
                                            track_inner_a * 2, track_inner_b * 2), track_border_thickness)  # نوار تیره داخلی

    # رسم سایه ماشین
    shadow_rect = shadow_image.get_rect(center=(int(car_x + 10), int(car_y + 10)))
    screen.blit(shadow_image, shadow_rect)

    # رسم ماشین
    rotated_car = pygame.transform.rotate(car_image_original, -car_angle)
    car_rect = rotated_car.get_rect(center=(int(car_x), int(car_y)))
    screen.blit(rotated_car, car_rect)

    # رسم جوی‌استیک
    pygame.draw.circle(screen, GRAY, joystick_center, joystick_radius, 5)
    pygame.draw.circle(screen, RED, (int(joystick_x), int(joystick_y)), joystick_handle_radius)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
