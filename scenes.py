import pygame
from logic import W

pygame.font.init()
FONT = pygame.font.SysFont(None, 36)
SMALL = pygame.font.SysFont(None, 26)
TITLE = pygame.font.SysFont(None, 72)

def draw_text(screen, msg, font, color, pos):
    s = font.render(msg, True, color)
    screen.blit(s, s.get_rect(center=pos))

class Button:
    def __init__(self, label, y, action):
        self.label, self.action = label, action
        self.rect = pygame.Rect(0, 0, 280, 50)
        self.rect.center = (W // 2, y)

    def draw(self, screen):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (56, 189, 248) if hover else (51, 65, 85),
                         self.rect, border_radius=8)
        draw_text(screen, self.label, FONT, (255, 255, 255), self.rect.center)

    def clicked(self, e):
        return (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1
                and self.rect.collidepoint(e.pos))