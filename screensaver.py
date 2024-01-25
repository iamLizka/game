import pygame
import start
import _sqlite3

from start import *
from const import *


"""класс, отвечающий за отрисовку окна с управлением"""
def show_control():
    screen = pygame.display.set_mode(start.size)
    button_back = Button(30, 30, 130, 50, ("Назад", 45, 30))  # создание кнопки

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

        button_back.draw_button(screen, button_image)  # отрисовка кнопокки и надписи
        button_back.write(screen, 35)

        pygame.display.flip()

        if back: # если нажата кнопка назад
            running = False
            screensaver_game()
    pygame.quit()


"""класс, отвечающий за отрисовку окна с целью"""
def show_target():
    screen = pygame.display.set_mode(start.size)

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

    button_back = Button(30, 30, 130, 50, ("Назад", 45, 30))  # создание кнопки

    running = True
    back = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_back.pressed(event.pos):
                    back = True

        button_back.draw_button(screen, button_image)  # отрисовка кнопки и надписи
        button_back.write(screen, 35)

        pygame.display.flip()

        if back:  # если нажата кнопка назад
            running = False
            screensaver_game()
    pygame.quit()


"""получение данных о уровнях из бд"""
def open_file_levels(screen):
    db = _sqlite3.connect('data/data_levels.db')
    sql = db.cursor()
    count_levels = len(sql.execute("""SELECT level_name from Game""").fetchall())  # всего уровней в игре
    max_level = sql.execute("""SELECT id from Game where passed = 'no'""").fetchone()  # уровень, который сечас проходит игрок
    if max_level:  # если уровень, который сейчас проходит игрок, не последний, то задаем макс не пройденный уровень
        max_level = max_level[0]
    else:
        max_level = count_levels  # иначе последний уровень - это макс уровень
    x, y = 0, 20
    for i in range(count_levels):
        if i % 9 == 0:  # делим на 9, чтобы проверить заполнилась ли строка на экране
            x = 95
            y += 105
        if i + 1 <= int(max_level):  # если этот уровень уже пройден или сейчас проходится, то добавляем светлую картинку
            ButtonLevel(button_level_yes, max_level, x, y, i + 1)
        else:
            ButtonLevel(button_level_not, max_level, x, y, i + 1)  # если не пройден, то добавляем темную картинку
        x += 105


"""класс, отвечающий за отрисовку окна с уровнями"""
def show_levels():
    screen = pygame.display.set_mode(start.size)
    open_file_levels(screen)  # запускаем файл, для создния спрайтов кнопок с уровнями

    fon = pygame.transform.scale(fon_screensaver, (WIDTH_SCREEN, HEIGHT_SCREEN))  # фон
    screen.blit(fon, (0, 0))
    pygame.gfxdraw.box(screen, pygame.Rect(70, 100, 970, 550), (0, 0, 0, 70))  # полупрозрачный прямоугольник

    button_back = Button(30, 30, 130, 50, ("Назад", 45, 30))  # создание кнопки назад

    running = True  # флаг для основного цикла
    back = False  # флаг для выхода из окна
    playing = False  # флаг для запуска игры, при нажатии на кнопки

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_back.pressed(event.pos):
                    back = True
                for sprite in all_buttons_sprites:  # перебираем все спрайты кнопок и проверяем были ли они нажаты
                    if sprite.pressed(event.pos):
                        playing = True

        button_back.draw_button(screen, button_image)  # отрисовка кнопок и надписей
        button_back.write(screen, 35)
        all_buttons_sprites.draw(screen)
        for sprite in all_buttons_sprites:
            sprite.write(screen, 30)

        pygame.display.flip()

        if back:  # если нажата кнопка назад
            running = False
            screensaver_game()
        if playing:  # если нажата кнопка уровня
            running = False
            start.main()
    pygame.quit()


"""основная функция"""
def screensaver_game():
    global button_sound_image, volume_menu_pause, volume_game
    screen = pygame.display.set_mode(start.size)

    pygame.mixer.music.play(-1)  # запуск зацикленной фоновой мелодии
    pygame.mixer.music.set_volume(volume_menu_pause)  # установка громкости

    button_play = Button(360, 280, 390, 70, ("Играть", 480, 280))  # создание кнопок
    button_target = Button(360, 360, 390, 70, ("Цель", 495, 360))
    button_control = Button(360, 440, 390, 70, ("Управление", 415, 440))
    button_levels = Button(360, 520, 390, 70, ("Уровни", 470, 520))
    button_sound = Button(20, 20, 50, 45)

    running = True  # флаг для основного цикла
    game_starting = False  # флаг для отслеживания нажатия кнопки 'Играть'
    control = False  # флаг для отслеживания нажатия кнопки 'Управление'
    target = False  # флаг для отслеживания нажатия кнопки 'Цель'
    levels = False   # флаг для отслеживания нажатия кнопки 'Уровни'
    sound = True  # флаг для отслеживания включена ли громкость

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
                elif button_levels.pressed(event.pos):
                    levels = True
                elif button_sound.pressed(event.pos):
                    if sound:  # проверяем включена ли уже музыка
                        button_sound_image = button_sound_off_image
                        sound = False
                        volume_game, volume_menu_pause = 0, 0  # изменение громкости
                    else:
                        button_sound_image = button_sound_on_image
                        sound = True
                        volume_game, volume_menu_pause = 1, 0.3  # изменение громкости
                    pygame.mixer.music.set_volume(volume_menu_pause)  # устанока громкости

        fon = pygame.transform.scale(fon_screensaver, (WIDTH_SCREEN, HEIGHT_SCREEN))
        screen.blit(fon, (0, 0))

        font = pygame.font.SysFont("cambria", 70)  # отрисовка названия игры
        string_rendered = font.render(NAME_GAME, 1, pygame.Color(COLOR_FONT))
        intro_rect = string_rendered.get_rect()
        intro_rect.x = 160
        intro_rect.y = 110
        screen.blit(string_rendered, intro_rect)

        # отрисовка кнопок и надписей
        button_play.draw_button(screen, button_image)
        button_play.write(screen, 45)
        button_control.draw_button(screen, button_image)
        button_control.write(screen, 45)
        button_target.draw_button(screen, button_image)
        button_target.write(screen, 45)
        button_levels.draw_button(screen, button_image)
        button_levels.write(screen, 45)
        button_sound.draw_button(screen, button_sound_image)


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
        elif levels:  # если нажата кнопка уровни
            running = False
            show_levels()

    pygame.quit()


"""создание спрайта кнопки с уровнями"""
class ButtonLevel(pygame.sprite.Sprite):
    def __init__(self, image, current_level, pos_x, pos_y, text):
        super().__init__(all_buttons_sprites)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.num_level = text
        self.current_level = current_level

    # отрисовка надписи на кнопке
    def write(self, screen, size_font):
        font = pygame.font.SysFont("comicsansms", size_font)
        string_rendered = font.render(str(self.num_level), 1, pygame.Color(COLOR_FONT))
        intro_rect = string_rendered.get_rect()
        stepx, stepy = 30, 20
        if self.num_level >= 10:
            stepx -= 5
        intro_rect.x = self.rect.x + stepx
        intro_rect.y = self.rect.y + stepy
        screen.blit(string_rendered, intro_rect)  # отрисовка номера уровня

    # нажатие кнопки
    def pressed(self, mouse):
        if self.rect.x <= mouse[0] <= self.rect.x + self.rect.w and\
                self.rect.y <= mouse[1] <= self.rect.y + self.rect.h:
            # если кнопка была нажата кнопка с пройденным уровнем, то перезаписываем нынешний уровень в файле
            if self.num_level <= int(self.current_level):
                with open("data/number_last_level.txt", "w", encoding='utf8') as f:
                    f.write(str(self.num_level))
                return True


"""класс кнопки"""
class Button:
    def __init__(self, x, y, width, height, data_text=None):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.color = COLOR_FONT
        if data_text:
            self.text = data_text[0]
            self.text_x, self.text_y = data_text[1], data_text[2]


    # отрисовка кнопки
    def draw_button(self, screen, image, blackout=None):
        button = pygame.transform.scale(image, (self.width, self.height))
        screen.blit(button, (self.x, self.y))
        if blackout:  # если передан цвет, используем его
            pygame.gfxdraw.box(screen, pygame.Rect(self.x, self.y, self.width, self.height), (255, 255, 255, 60))
            self.color = ("#363430")

    # отрисовка надписи
    def write(self, screen, size_font):
        font = pygame.font.SysFont("comicsansms", size_font)
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
fon_screensaver = start.load_image("fon.jpg")
button_up_dawn_image = start.load_image("button_up_dawn.jpg", (180, 120), -1)
button_esc_image = start.load_image("button_esc_image.jpg", (60, 60), -1)
button_r_image = start.load_image("button_r_image.jpg", (60, 60), -1)
button_ctrl_image = start.load_image("button_ctrl_image.jpg", (90, 60), -1)
button_c_image = start.load_image("button_c_image.jpg", (60, 60), -1)
button_sound_on_image = start.load_image("button_sound_on.png", (50, 45), -1)
button_sound_off_image = start.load_image("button_sound_off.png", (50, 45), -1)
button_level_yes = start.load_image("grass_button_yes.jpg", (80, 80))
button_level_not = start.load_image("grass_button_not.jpg", (80, 80))
button_image = start.blocks_images["wall"]

button_sound_image = button_sound_on_image
volume_menu_pause = 0.3  # громкость во время паузы и в маню
volume_game = 0.7  # основная громкость

all_buttons_sprites = pygame.sprite.Group()  # создание группы спрайтов для кнопок с уровнями

pygame.init()
