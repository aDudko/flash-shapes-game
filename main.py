import pygame
import random
import sys
import os

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FONT = pygame.font.SysFont(None, 32)
BG_COLOR = (229, 229, 229)
FG_COLOR = (0, 0, 0)
BUTTON_COLOR = (0, 128, 128)
INPUT_BG = (230, 230, 230)

SHAPES = ['circle', 'diamond', 'oval', 'rectangle', 'square', 'triangle']
CELL_SIZE = 100

def resource_path(relative_path):
    """ Получает путь к файлу """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

ASSETS_PATH = resource_path(os.path.join("assets", "shapes"))

# --- Window initialization (important before loading images) ---
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
correct_answers = 0
incorrect_answers = 0
pygame.display.set_caption(f"FlashShapes: {correct_answers}/{incorrect_answers}")
clock = pygame.time.Clock()

# --- Uploading images ---
shape_images = {}
for shape in SHAPES:
    path = os.path.join(ASSETS_PATH, f"{shape}.png")
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, (CELL_SIZE, CELL_SIZE))
        shape_images[shape] = img


# --- Utils ---
def draw_text(surface, text, pos, color=FG_COLOR):
    text_surf = FONT.render(text, True, color)
    surface.blit(text_surf, pos)


def draw_button(surface, rect, text):
    pygame.draw.rect(surface, BUTTON_COLOR, rect)
    text_surf = FONT.render(text, True, FG_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)


def draw_input_box(surface, rect, text):
    pygame.draw.rect(surface, INPUT_BG, rect)
    pygame.draw.rect(surface, FG_COLOR, rect, 2)
    draw_text(surface, text, (rect.x + 5, rect.y + 5))


def draw_shape(surface, shape, pos):
    img = shape_images.get(shape)
    if img:
        rect = img.get_rect(center=pos)
        surface.blit(img, rect)


# --- States ---
mode = 'settings'
input_text = ''
display_time_ms = 1500
shape_to_count = random.choice(SHAPES)
shapes_on_screen = []

input_rect = pygame.Rect(300, 140, 200, 40)
cols_rect = pygame.Rect(300, 200, 90, 40)
rows_rect = pygame.Rect(410, 200, 90, 40)
start_btn = pygame.Rect(300, 260, 200, 40)
next_btn = pygame.Rect(300, 500, 200, 40)
continue_btn = pygame.Rect(300, 450, 200, 40)

cols_input = ''
rows_input = ''
preview_timer_started = False

GRID_COLS = 6
GRID_ROWS = 5


def generate_shapes_grid():
    generated = []
    total_width = GRID_COLS * CELL_SIZE
    total_height = GRID_ROWS * CELL_SIZE

    space_x = (WINDOW_WIDTH - total_width) // (GRID_COLS + 1)
    space_y = (WINDOW_HEIGHT - total_height) // (GRID_ROWS + 1)

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            shape = random.choice(SHAPES)
            x = space_x * (col + 1) + CELL_SIZE * col + CELL_SIZE // 2
            y = space_y * (row + 1) + CELL_SIZE * row + CELL_SIZE // 2
            generated.append((shape, (x, y)))
    return generated


# --- Basic loop ---
running = True
show_shapes = False
answer_text = ''

while running:
    screen.fill(BG_COLOR)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if mode == 'settings' and start_btn.collidepoint(event.pos):
                try:
                    shape_to_count = random.choice(SHAPES)
                    mode = 'preview'
                except:
                    pass
            elif mode == 'result' and next_btn.collidepoint(event.pos):
                input_text = ''
                answer_text = ''
                shape_to_count = random.choice(SHAPES)
                mode = 'preview'
            elif mode == 'preview' and continue_btn.collidepoint(event.pos):
                shapes_on_screen = generate_shapes_grid()
                mode = 'show'
                show_shapes = True
                pygame.time.set_timer(pygame.USEREVENT, display_time_ms, loops=1)
        elif event.type == pygame.KEYDOWN and mode == 'settings':
            if event.key == pygame.K_BACKSPACE:
                if rows_rect.collidepoint(pygame.mouse.get_pos()):
                    rows_input = rows_input[:-1]
                elif cols_rect.collidepoint(pygame.mouse.get_pos()):
                    cols_input = cols_input[:-1]
                else:
                    input_text = input_text[:-1]
            elif event.unicode.isdigit():
                if rows_rect.collidepoint(pygame.mouse.get_pos()):
                    rows_input += event.unicode
                elif cols_rect.collidepoint(pygame.mouse.get_pos()):
                    cols_input += event.unicode
                else:
                    input_text += event.unicode
        elif event.type == pygame.USEREVENT and mode == 'show':
            mode = 'answer'
        elif event.type == pygame.KEYDOWN and mode == 'answer':
            if event.key == pygame.K_RETURN:
                try:
                    user_answer = int(input_text)
                    correct = sum(1 for s in shapes_on_screen if s[0] == shape_to_count)
                    if user_answer == correct:
                        answer_text = "Correct!"
                        correct_answers += 1
                    else:
                        answer_text = f"Incorrect. It was: {correct}"
                        incorrect_answers += 1
                    pygame.display.set_caption(f"FlashShapes {correct_answers}/{incorrect_answers}")
                    mode = 'result'
                except:
                    answer_text = "Incorrect input"
                    mode = 'result'
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            elif event.unicode.isdigit():
                input_text += event.unicode
        elif event.type == pygame.KEYDOWN and mode == 'result':
            if event.key == pygame.K_RETURN:
                input_text = ''
                answer_text = ''
                shape_to_count = random.choice(SHAPES)
                mode = 'preview'

    # --- Render ---
    if mode == 'settings':
        draw_text(screen, "Display time (ms):", (300, 100))
        draw_input_box(screen, input_rect, input_text)
        draw_text(screen, "Grid (cols x rows):", (300, 180))
        draw_input_box(screen, cols_rect, cols_input)
        draw_input_box(screen, rows_rect, rows_input)
        draw_button(screen, start_btn, "Start")

    elif mode == 'preview' and input_text and cols_input and rows_input:
        display_time_ms = int(input_text)
        GRID_COLS = max(1, int(cols_input))
        GRID_ROWS = max(1, int(rows_input))
        draw_text(screen, "Remember the shape:", (290, 140))
        draw_shape(screen, shape_to_count, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        draw_button(screen, continue_btn, "Display field")
        input_text = ''

    elif mode == 'preview':
        draw_text(screen, "Remember the shape:", (290, 140))
        draw_shape(screen, shape_to_count, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        draw_button(screen, continue_btn, "Display field")

    elif mode == 'show':
        for shape, pos in shapes_on_screen:
            draw_shape(screen, shape, pos)

    elif mode == 'answer':
        draw_text(screen, f"How many figures: {shape_to_count}?", (260, 110))
        draw_shape(screen, shape_to_count, (WINDOW_WIDTH // 2, 230))
        draw_input_box(screen, input_rect, input_text)
        draw_text(screen, "Press Enter to answer", (270, 270))

    elif mode == 'result':
        draw_text(screen, answer_text, (300, 200))
        draw_button(screen, next_btn, "New attempt")

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
