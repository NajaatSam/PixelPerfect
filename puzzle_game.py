import sys
import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the screen and clock
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Image Puzzle")
clock = pygame.time.Clock()  # Clock for controlling frame rate

# Define colors
BACKGROUND_COLOR = (230, 230, 230)  # Light gray
TEXT_COLOR = (0, 0, 0)  # Black
BUTTON_COLOR = (100, 200, 100)  # Green
BUTTON_HOVER_COLOR = (150, 250, 150)  # Lighter Green

# Load and set up the font
font = pygame.font.Font(None, 36)  # Default font and size
small_font = pygame.font.Font(None, 28)

def draw_button(text, rect, active):
    pygame.draw.rect(screen, BUTTON_HOVER_COLOR if active else BUTTON_COLOR, rect)
    text_surf = small_font.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

preview_button = pygame.Rect(700, 10, 90, 30)  # Adjust size and position as needed

def setup_game():
    # Load background image and scale it
    background_image = pygame.image.load('office.jpeg')
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # For fade animation
    alpha_value = 255
    fading_out = True
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    rows, cols = 0, 0
    input_active = {'rows': False, 'cols': False}
    input_text = {'rows': '', 'cols': ''}
    buttons = {
        'rows': pygame.Rect(300, 200, 200, 50),
        'cols': pygame.Rect(300, 300, 200, 50),
        'start': pygame.Rect(350, 400, 100, 50)
    }
    while True:
        screen.blit(background_image, (0, 0))
        
        # Handle fade animation
        if fading_out:
            alpha_value -= 5
            if alpha_value <= 0:
                fading_out = False
                alpha_value = 0
        else:
            alpha_value += 5
            if alpha_value >= 255:
                fading_out = True
                alpha_value = 255
        fade_surface.set_alpha(alpha_value)
        screen.blit(fade_surface, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttons['rows'].collidepoint(event.pos):
                    input_active['rows'] = True
                    input_active['cols'] = False
                elif buttons['cols'].collidepoint(event.pos):
                    input_active['cols'] = True
                    input_active['rows'] = False
                elif buttons['start'].collidepoint(event.pos) and rows and cols:
                    return rows, cols
            elif event.type == pygame.KEYDOWN:
                if input_active['rows'] or input_active['cols']:
                    current = 'rows' if input_active['rows'] else 'cols'
                    if event.key == pygame.K_BACKSPACE:
                        input_text[current] = input_text[current][:-1]
                    elif event.key == pygame.K_RETURN:
                        if rows and cols:
                            return rows, cols
                    else:
                        input_text[current] += event.unicode
                        try:
                            if current == 'rows':
                                rows = int(input_text[current])
                            else:
                                cols = int(input_text[current])
                        except ValueError:
                            input_text[current] = input_text[current][:-1]

        draw_button(f"Rows: {input_text['rows']}", buttons['rows'], input_active['rows'])
        draw_button(f"Cols: {input_text['cols']}", buttons['cols'], input_active['cols'])
        if rows and cols:
            draw_button("Start", buttons['start'], True)

        pygame.display.flip()
        clock.tick(30)


def display_text(text):
    text_surface = font.render(text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text_surface, text_rect)

def load_image(image_path, rows, cols):
    image = pygame.image.load(image_path)
    image_width, image_height = image.get_size()
    piece_width = image_width // cols
    piece_height = image_height // rows
    pieces = []
    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(col * piece_width, row * piece_height, piece_width, piece_height)
            piece = image.subsurface(rect)
            scaled_piece = pygame.transform.scale(piece, (SCREEN_WIDTH // cols, SCREEN_HEIGHT // rows))
            pieces.append((scaled_piece, rect))  # Store original rect for checking solved state
    return pieces

def draw_pieces(pieces, rows, cols, positions):
    piece_width = SCREEN_WIDTH // cols
    piece_height = SCREEN_HEIGHT // rows
    for index in range(len(pieces)):
        piece, _ = pieces[positions[index]]
        x = (index % cols) * piece_width
        y = (index // cols) * piece_height
        if piece is not None:
            screen.blit(piece, (x, y))
        else:
            pygame.draw.rect(screen, BACKGROUND_COLOR, (x, y, piece_width, piece_height))

def display_expected_image(pieces, rows, cols):
    piece_width = SCREEN_WIDTH // cols
    piece_height = SCREEN_HEIGHT // rows
    for index, (piece, _) in enumerate(pieces[:-1]):
        row = index // cols
        col = index % cols
        x = col * piece_width
        y = row * piece_height
        screen.blit(piece, (x, y))
    pygame.display.flip()

def main():
    rows, cols = setup_game()
    
    pieces = load_image("office.jpeg", rows, cols)
    pieces[-1] = (None, pieces[-1][1])
    positions = list(range(len(pieces)))  # Initialize positions based on initial order

    display_expected_image(pieces, rows, cols)

    # Wait for a user action to continue
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

    # Shuffle the pieces, excluding the last one
    indices = positions[:-1]  # Get indices of all but the last (empty) space
    random.shuffle(indices)
    positions[:-1] = indices  # Shuffle the indices representing pieces' positions

    empty_index = len(pieces) - 1  # Find the initial empty slot

    solved = False
    running = True
    preview_mode = False  # Flag to toggle preview
    preview_button = pygame.Rect(700, 10, 90, 30)  # Define the position and size of the preview button
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if preview_button.collidepoint(event.pos):
                    preview_mode = not preview_mode  # Toggle the preview mode
                elif event.button == 1 and not solved and not preview_mode:
                    mx, my = event.pos
                    piece_index = (mx // (SCREEN_WIDTH // cols)) + ((my // (SCREEN_HEIGHT // rows)) * cols)
                    if piece_index < len(pieces) and piece_index != empty_index:
                        if (abs(piece_index - empty_index) == 1 and piece_index // cols == empty_index // cols) or \
                        (abs(piece_index - empty_index) == cols):
                            positions[piece_index], positions[empty_index] = positions[empty_index], positions[piece_index]
                            empty_index = piece_index
                            if positions == list(range(len(pieces))):
                                screen.fill(BACKGROUND_COLOR)
                                draw_pieces(pieces, rows, cols, positions)
                                pygame.display.flip()
                                display_text("Congratulations! You solved the puzzle!")

        screen.fill(BACKGROUND_COLOR)
        if preview_mode:
            display_expected_image(pieces, rows, cols)
        else:
            draw_pieces(pieces, rows, cols, positions)
        draw_button("Preview", preview_button, preview_mode)
        pygame.display.flip()
        clock.tick(60)  # Maintain 60 frames per second

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
