import pygame
import random
import os


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60


WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
LIGHT_BROWN = (210, 180, 140)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GOLD = (255, 215, 0)
SKY_BLUE = (135, 206, 235)


BREAD_START_Y = 200
BREAD_HEIGHT = 100
BREAD_SPEED = 3
KNIFE_X = SCREEN_WIDTH // 2
MIN_SLICEABLE_WIDTH = 15
SLICE_GRAVITY = 0.25


HIGH_SCORE_FILE = "high_score.txt"


def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                return int(f.read())
        except (ValueError, FileNotFoundError):
            return 0
    return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, 'w') as f:
        f.write(str(score))


class Bread:
    def __init__(self):
        self.width = 300
        self.rect = pygame.Rect(-self.width, BREAD_START_Y, self.width, BREAD_HEIGHT)
        self.speed_x = BREAD_SPEED

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0

    def draw(self, surface):
        pygame.draw.rect(surface, BROWN, self.rect, border_radius=15)
        crust_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 20)
        pygame.draw.rect(surface, LIGHT_BROWN, crust_rect, border_top_left_radius=15, border_top_right_radius=15)

    def slice(self, slice_pos_x):
        if not self.rect.collidepoint(slice_pos_x, self.rect.centery):
            return None
        slice_width = self.rect.right - slice_pos_x
        remaining_width = self.rect.width - slice_width
        if remaining_width < MIN_SLICEABLE_WIDTH:
            return None
        new_slice = Slice(slice_pos_x, self.rect.y, slice_width, self.rect.height)
        self.rect.width = remaining_width
        return new_slice

class Slice:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed_y = random.uniform(-3, -1)
        self.speed_x = random.uniform(-1.5, 1.5)
        self.gravity = SLICE_GRAVITY
        self.rotation_speed = random.choice([-2, -1, 1, 2])
        self.angle = 0

        self.original_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(self.original_surface, BROWN, (0, 0, width, height), border_radius=15)
        crust_rect = pygame.Rect(0, 0, width, 20)
        pygame.draw.rect(self.original_surface, LIGHT_BROWN, crust_rect, border_top_left_radius=15, border_top_right_radius=15)

    def update(self):
        self.speed_y += self.gravity
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        self.angle += self.rotation_speed

    def draw(self, surface):
        rotated_surface = pygame.transform.rotate(self.original_surface, self.angle)
        new_rect = rotated_surface.get_rect(center=self.rect.center)
        surface.blit(rotated_surface, new_rect.topleft)

class Knife:
    def __init__(self, x_pos):
        self.x = x_pos
        self.height = SCREEN_HEIGHT
        self.is_slicing = False
        self.animation_timer = 0
        self.width = 10
        self.handle_height = 100

    def draw(self, surface):
        y_offset = 20 if self.is_slicing else 0
        blade_rect = pygame.Rect(self.x - self.width//2, 0 + y_offset, self.width, self.height)
        pygame.draw.rect(surface, GRAY, blade_rect)
        handle_rect = pygame.Rect(self.x - self.width, 0 + y_offset, self.width * 2, self.handle_height)
        pygame.draw.rect(surface, BLACK, handle_rect, border_top_left_radius=5, border_top_right_radius=5)

    def start_slice_animation(self):
        self.is_slicing = True
        self.animation_timer = 5

    def update(self):
        if self.is_slicing:
            self.animation_timer -= 1
            if self.animation_timer <= 0:
                self.is_slicing = False


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Ekmek Dilimleme Oyunu")
    clock = pygame.time.Clock()

    
    score_font = pygame.font.Font(None, 50)
    game_over_font = pygame.font.Font(None, 74)
    info_font = pygame.font.Font(None, 36)

    
    high_score = load_high_score()
    knife = Knife(KNIFE_X)

    def reset_game():
        return Bread(), [], 0, False

    bread, slices, score, game_over = reset_game()

    running = True
    while running:
       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if event.button == 1:
                    knife.start_slice_animation()
                    new_slice = bread.slice(KNIFE_X)
                    if new_slice:
                        slices.append(new_slice)
                        score += 1

            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    bread, slices, score, game_over = reset_game()

        
        if not game_over:
            bread.update()
            knife.update()
            for s in slices:
                s.update()
            slices = [s for s in slices if s.rect.top < SCREEN_HEIGHT]
            if bread.rect.width < MIN_SLICEABLE_WIDTH:
                game_over = True
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)

        
        screen.fill(SKY_BLUE)
        if not game_over:
            bread.draw(screen)
        for s in slices:
            s.draw(screen)
        knife.draw(screen)

        
        screen.blit(score_font.render(f"Dilim: {score}", True, BLACK), (10, 10))
        screen.blit(score_font.render(f"En Yüksek: {high_score}", True, GOLD), 
                    (SCREEN_WIDTH - 220, 10))

        
        if game_over:
            game_over_text = game_over_font.render("OYUN BİTTİ", True, RED)
            final_score_text = info_font.render(f"Toplam Dilim: {score}", True, BLACK)
            restart_text = info_font.render("Yeniden Başlamak İçin 'R' Tuşuna Basın", True, BLACK)
            screen.blit(game_over_text, (SCREEN_WIDTH/2 - game_over_text.get_width()/2, SCREEN_HEIGHT/2 - 50))
            screen.blit(final_score_text, (SCREEN_WIDTH/2 - final_score_text.get_width()/2, SCREEN_HEIGHT/2 + 20))
            screen.blit(restart_text, (SCREEN_WIDTH/2 - restart_text.get_width()/2, SCREEN_HEIGHT/2 + 60))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
