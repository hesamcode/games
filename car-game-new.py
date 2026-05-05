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

# متغیرهای ماشین
car_radius = 50
car_max_speed = 12
car_acceleration = 0.4
car_friction = 0.04
car_angle = 0
car_velocity_x = 0
car_velocity_y = 0

# جوی‌استیک
joystick_center = (WIDTH // 2, HEIGHT - 300)
joystick_radius = 160
joystick_handle_radius = 70
joystick_active = False
joystick_x = joystick_center[0]
joystick_y = joystick_center[1]

# تصویر ماشین
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

# متغیرهای طراحی پیست
drawing = False
track_points = []
track_thickness = 150
track_border_thickness = 20
game_started = False
MIN_DISTANCE = 5

clock = pygame.time.Clock()
running = True

# تابع بررسی اینکه آیا ماشین روی جاده پیست هست یا نه
def is_on_track(x, y):
    if not track_points:
        return True
    for i in range(len(track_points) - 1):
        p1, p2 = track_points[i], track_points[i + 1]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            continue
        t = max(0, min(1, ((x - p1[0]) * dx + (y - p1[1]) * dy) / length_sq))
        proj_x = p1[0] + t * dx
        proj_y = p1[1] + t * dy
        dist = math.hypot(x - proj_x, y - proj_y)
        if dist <= track_thickness / 2:
            return True
    return False

# پیدا کردن نزدیک‌ترین نقطه روی پیست
def find_closest_point_on_track(x, y):
    if not track_points:
        return (x, y)  # اصلاح برای لیست خالی
    closest_dist = float('inf')
    closest_point = track_points[0]
    for i in range(len(track_points) - 1):
        p1, p2 = track_points[i], track_points[i + 1]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            continue
        t = max(0, min(1, ((x - p1[0]) * dx + (y - p1[1]) * dy) / length_sq))
        proj_x = p1[0] + t * dx
        proj_y = p1[1] + t * dy
        dist = math.hypot(x - proj_x, y - proj_y)
        if dist < closest_dist:
            closest_dist = dist
            closest_point = (proj_x, proj_y)
    return closest_point

# تابع مدیریت برخورد
def handle_collision(new_x, new_y, old_x, old_y):
    velocity = pygame.math.Vector2(car_velocity_x, car_velocity_y)
    if velocity.length() == 0 or is_on_track(new_x, new_y):
        return new_x, new_y, car_velocity_x, car_velocity_y

    closest_x, closest_y = find_closest_point_on_track(new_x, new_y)
    normal = pygame.math.Vector2(new_x - closest_x, new_y - closest_y).normalize()

    velocity_tangent = velocity - velocity.project(normal)
    velocity_normal = velocity.project(normal)
    new_velocity = velocity_tangent * 0.95 - velocity_normal * 0.3

    correction_factor = car_radius * 0.1
    while not is_on_track(new_x, new_y):
        new_x -= normal.x * correction_factor
        new_y -= normal.y * correction_factor

    return new_x, new_y, new_velocity.x, new_velocity.y

# تنظیم موقعیت اولیه ماشین
car_x, car_y = WIDTH // 2, HEIGHT // 2

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_started:
            drawing = True
            track_points.append(pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEMOTION and drawing:
            new_point = pygame.mouse.get_pos()
            if not track_points or math.hypot(new_point[0] - track_points[-1][0], new_point[1] - track_points[-1][1]) > MIN_DISTANCE:
                track_points.append(new_point)
        elif event.type == pygame.MOUSEBUTTONUP and not game_started:
            drawing = False
            if len(track_points) > 1:
                first_point = track_points[0]
                last_point = track_points[-1]
                if math.hypot(first_point[0] - last_point[0], first_point[1] - last_point[1]) > 10:
                    track_points.append(first_point)
                car_x, car_y = track_points[0]
                game_started = True
        elif game_started:
            if event.type == pygame.MOUSEBUTTONDOWN:
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

    if game_started:
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
        if speed > car_max_speed:  # اصلاح typo
            car_velocity_x = car_velocity_x * car_max_speed / speed
            car_velocity_y = car_velocity_y * car_max_speed / speed

        new_car_x = car_x + car_velocity_x
        new_car_y = car_y + car_velocity_y
        car_x, car_y, car_velocity_x, car_velocity_y = handle_collision(new_car_x, new_car_y, car_x, car_y)

    # رسم صفحه
    screen.fill(WHITE)

    if not game_started:
        if len(track_points) > 1:
            pygame.draw.lines(screen, DARK_GRAY, False, track_points, track_border_thickness)
    else:
        if len(track_points) > 1:
            pygame.draw.lines(screen, LIGHT_GRAY, True, track_points, track_thickness)
            pygame.draw.lines(screen, DARK_GRAY, True, track_points, track_border_thickness)

        shadow_rect = shadow_image.get_rect(center=(int(car_x + 10), int(car_y + 10)))
        screen.blit(shadow_image, shadow_rect)

        rotated_car = pygame.transform.rotate(car_image_original, -car_angle)
        car_rect = rotated_car.get_rect(center=(int(car_x), int(car_y)))
        screen.blit(rotated_car, car_rect)

        pygame.draw.circle(screen, GRAY, joystick_center, joystick_radius, 5)
        pygame.draw.circle(screen, RED, (int(joystick_x), int(joystick_y)), joystick_handle_radius)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
