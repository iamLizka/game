import start
from start import *

def screensaver_game():
    pygame.init()
    screen = pygame.display.set_mode(size)

    button = Button(350, 270, 410, 80, "Играть")

    running = True
    game_starting = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button.pressed(event.pos):
                    game_starting = True

        fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH_SCREEN, HEIGHT_SCREEN))
        screen.blit(fon, (0, 0))

        button.draw_button(screen)
        button.write(screen, 470, 290)

        pygame.display.flip()

        if game_starting:
            running = False
            start.main()
    pygame.quit()


class Button:
    def __init__(self, x, y, width, height, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw_button(self, screen):
        button = pygame.transform.scale(blocks_images["wall"], (self.width, self.height))
        screen.blit(button, (self.x, self.y))

    def write(self, screen, x, y):
        font = pygame.font.Font(None, 70)
        string_rendered = font.render(self.text, 1, pygame.Color("#cccccc"))
        intro_rect = string_rendered.get_rect()
        intro_rect.x = x
        intro_rect.y = y
        screen.blit(string_rendered, intro_rect)

    def pressed(self, mouse):
        if self.x <= mouse[0] <= self.x + self.width and self.y <= mouse[1] <= self.y + self.height:
            return True