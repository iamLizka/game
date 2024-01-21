import pygame
import start
from start import *
from const import *


"""класс, отвечающий за отрисовку окна с управлением"""
def show_control():
    screen = pygame.display.set_mode(size)

    button_back = Button(30, 30, 120, 45, "Назад", 50, 40)  # создание кнопки

    fon = pygame.transform.scale(fon_screensaver, (WIDTH_SCREEN, HEIGHT_SCREEN))
    screen.blit(fon, (0, 0))

    # отрисовка полупрозрачного прямоугольника
    rect_surface = pygame.Surface((610, 420), pygame.SRCALPHA)
    pygame.draw.rect(rect_surface, (60, 60, 60), rect_surface.get_rect(), 0, 20)
    rect_surface.set_alpha(170)
    screen.blit(rect_surface, (250, 180))

    font = pygame.font.Font(None, 25)  # шрифт

    screen.blit(button_up_dawn_image, (260, 190))  # отрисовка клавиш движения и соответсвующей надписи
    string_rendered = font.render("Ходьба", 1, pygame.Color(COLOR_FONT))
    intro_rect = string_rendered.get_rect()
    intro_rect.x = 455
    intro_rect.y = 280
    screen.blit(string_rendered, intro_rect)

    screen.blit(button_r_image, (330, 340))  # отрисовка клавиши, отвечающей за стрельбу, и соответсвующей надписи
    string_rendered = font.render("Режим стельбы", 1, pygame.Color(COLOR_FONT))
    intro_rect = string_rendered.get_rect()
    intro_rect.x = 455
    intro_rect.y = 360
    screen.blit(string_rendered, intro_rect)

    screen.blit(button_esc_image, (330, 420)) # отрисовка клавиши, отвечающей за паузу, и соответсвующей надписи
    string_rendered = font.render("Пауза", 1, pygame.Color(COLOR_FONT))
    intro_rect = string_rendered.get_rect()
    intro_rect.x = 455
    intro_rect.y = 440
    screen.blit(string_rendered, intro_rect)

    screen.blit(button_ctrl_image, (280, 500))  # отрисовка клавиш, отвечающих за вкл/выкл полноэкранного режима
    screen.blit(button_c_image, (370, 500))
    text_list = ["Включить/выключить полноэкранный режим", "(работает только в режиме игры)"]
    y = 510
    for text in text_list:  # отрисовка соответсвующей надписи
        string_rendered = font.render(text, 1, pygame.Color(COLOR_FONT))
        intro_rect = string_rendered.get_rect()
        intro_rect.x = 455
        intro_rect.y = y
        screen.blit(string_rendered, intro_rect)
        y += 20

    running = True
    back = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_back.pressed(event.pos):
                    back = True

        button_back.draw_button(screen)  # отрисовка кнопокки и надписи
        button_back.write(screen, 35)

        pygame.display.flip()

        if back: # если нажата кнопка назад
            running = False
            screensaver_game()
    pygame.quit()


"""класс, отвечающий за отрисовку окна с целью"""
def show_target():
    screen = pygame.display.set_mode(size)

    font = pygame.font.Font(None, 30)

    fon = pygame.transform.scale(fon_screensaver, (WIDTH_SCREEN, HEIGHT_SCREEN))
    screen.blit(fon, (0, 0))

    # отрисовка полупрозрачного прямоугольника
    rect_surface = pygame.Surface((630, 410), pygame.SRCALPHA)
    pygame.draw.rect(rect_surface, (60, 60, 60), rect_surface.get_rect(), 0, 20)
    rect_surface.set_alpha(160)
    screen.blit(rect_surface, (240, 190))

    y = 220
    for text in TEXT_TARGET:  # отрисовка текста
        string_rendered = font.render(text, 1, pygame.Color(COLOR_FONT))
        intro_rect = string_rendered.get_rect()
        intro_rect.x = 260
        intro_rect.y = y
        screen.blit(string_rendered, intro_rect)
        y += 30

    button_back = Button(30, 30, 120, 45, "Назад", 50, 40)  # создание кнопки

    running = True
    back = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_back.pressed(event.pos):
                    back = True

        button_back.draw_button(screen)  # отрисовка кнопки и надписи
        button_back.write(screen, 35)

        pygame.display.flip()

        if back:  # если нажата кнопка назад
            running = False
            screensaver_game()
    pygame.quit()


"""основная функция"""
def screensaver_game():
    screen = pygame.display.set_mode(size)

    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)

    # создание кнопок
    button_play = Button(350, 270, 410, 80, "Играть", 470, 290)
    button_control = Button(350, 450, 410, 80, "Управление", 410, 470)
    button_target = Button(350, 360, 410, 80, "Цель", 485, 380)

    running = True
    game_starting = False  # флаг для отслеживания нажатияя кнопки 'Играть'
    control = False  # флаг для отслеживания нажатияя кнопки 'Управление'
    target = False  # флаг для отслеживания нажатияя кнопки 'Цель'

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_play.pressed(event.pos):
                    game_starting = True
                elif button_control.pressed(event.pos):
                    control = True
                elif button_target.pressed(event.pos):
                    target = True


        fon = pygame.transform.scale(fon_screensaver, (WIDTH_SCREEN, HEIGHT_SCREEN))
        screen.blit(fon, (0, 0))

        # отрисовка кнопок и надписей
        button_play.draw_button(screen)
        button_play.write(screen, 70)
        button_control.draw_button(screen)
        button_control.write(screen, 70)
        button_target.draw_button(screen)
        button_target.write(screen, 70)

        pygame.display.flip()

        if game_starting:  # если нажата кпопка играть
            running = False
            pygame.mixer.pause()
            start.main()
        elif control:  # если нажата кнопка управление
            running = False
            show_control()
        elif target:  # если нажата кнопка цель
            running = False
            show_target()

    pygame.quit()


"""класс кнопки"""
class Button:
    def __init__(self, x, y, width, height, text, text_x, text_y):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.text = text
        self.text_x, self.text_y = text_x, text_y
        self.color = COLOR_FONT

    # отрисовка кнопки
    def draw_button(self, screen, blackout=None):
        button = pygame.transform.scale(blocks_images["wall"], (self.width, self.height))
        screen.blit(button, (self.x, self.y))
        if blackout: # если передан цвет, используем его
            pygame.gfxdraw.box(screen, pygame.Rect(self.x, self.y, self.width, self.height), (255, 255, 255, 60))
            self.color = ("#363430")

    # отрисовка надписи
    def write(self, screen, size_font):
        font = pygame.font.Font(None, size_font)
        string_rendered = font.render(self.text, 1, pygame.Color(self.color))
        intro_rect = string_rendered.get_rect()
        intro_rect.x = self.text_x
        intro_rect.y = self.text_y
        screen.blit(string_rendered, intro_rect)

    # нажатие кнопки
    def pressed(self, mouse):
        if self.x <= mouse[0] <= self.x + self.width and self.y <= mouse[1] <= self.y + self.height:
            return True


# загрузка изоображений
fon_screensaver = load_image("fon.jpg")
button_up_dawn_image = load_image("button_up_dawn.jpg", (180, 120), -1)
button_esc_image = load_image("button_esc_image.jpg", (60, 60), -1)
button_r_image = load_image("button_r_image.jpg", (60, 60), -1)
button_ctrl_image = load_image("button_ctrl_image.jpg", (90, 60), -1)
button_c_image = load_image("button_c_image.jpg", (60, 60), -1)

pygame.init()


