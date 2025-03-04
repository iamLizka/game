import pygame
import os
import sys
import random
import pygame.gfxdraw
import _sqlite3

import screensaver
from const import *
from screensaver import *


"""загрузка изображения"""
def load_image(name, size=None, colorkey=None):
    fullname = os.path.join('data', name)
    # проверяем существует ли такой файл
    if not os.path.isfile(fullname):
        # print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    # при необходимости убираем фон
    if colorkey is not None:
        colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    if size:
        image = pygame.transform.scale(image, (size[0], size[1]))
    # возврашаем изображение
    return image


"""загрузка уровня"""
def load_level(filename):
    filename = "data/levels/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


"""рисование всех предметов на карте уровня"""
def generate_level(level):
    player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Wall('wall', x, y)
            elif level[y][x] == '.' or level[y][x] == '_':
                Grass('grass', x, y)
            elif level[y][x] == "!":
                Portal('portal', x, y)
            elif level[y][x] == "@":
                Grass('grass', x, y)
                player = Player(frames_player[0], x, y)
    # возвращаем размер поля в клетках
    return player, x, y


"""разрезание листа с анимацией игрока"""
def cut_sheet(sheet, columns, rows):
    frames = []
    rect = pygame.Rect(40, 40, sheet.get_width() // columns, sheet.get_height() // rows)
    for j in range(rows):
        for i in range(columns):
            frame_location = (rect.w * i, rect.h * j)
            frames.append(sheet.subsurface(pygame.Rect(frame_location, rect.size)))
    # возвращаем список со всеми обрезанными изображениями
    return frames


"""заставка в конце игры"""
def show_game_over(screen, full_screen, player_won):
    stepx, stepy = 0, 0
    if full_screen:  # если включен полноэкранный режим, то делаем отступ
        stepx, stepy = STEP_SCREEN_X * 2, STEP_SCREEN_Y * 2
    if player_won:
        text = "  VICTORY"
    else:
        text = "GAME OVER"
    font = pygame.font.SysFont("comicsansms", 110)
    string_rendered = font.render(text, 1, pygame.Color('red'))
    intro_rect = string_rendered.get_rect()
    intro_rect.x = 240 + stepx
    intro_rect.y = 310 + stepy
    screen.blit(string_rendered, intro_rect)


"""заставка с уровнем"""
def show_numlevel(screen, full_screen, text):
    stepx, stepy = 0, 0
    if full_screen:  # если включен полноэкранный режим, то делаем отступ
        stepx, stepy = STEP_SCREEN_X * 2, STEP_SCREEN_Y * 2
    font = pygame.font.SysFont("comicsansms", 90)
    string_rendered = font.render(text, 1, pygame.Color(COLOR_FONT))
    intro_rect = string_rendered.get_rect()
    intro_rect.x = 390 + stepx
    intro_rect.y = 310 + stepy
    screen.blit(string_rendered, intro_rect)


"""определяем координаты пули и создаем ее"""
def attack(move_attack, bullet_image, player_coords):
    x = player_coords[0] + 15
    y = player_coords[1] + 20
    if player.get_count_bullets() > 0:  # если у игрока есть патроны, то создаем патрон
        sound_bullet.play()
        player.update_count_bullets(-1)
        Bullet(bullet_image, x, y, move_attack)


"""создание спрайта портала"""
class Portal(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(portal_sprite, all_sprites)
        image1 = blocks_images[tile_type]
        self.image = pygame.transform.scale(image1, (size_block, size_block))
        self.rect = self.image.get_rect().move(
            size_block * pos_x, size_block * pos_y)

    # для обновления координат объекта во время смены режима экрана
    def update_coords(self, step):
        self.rect = self.rect.move(step[0], step[1])


"""создание спрайта стены"""
class Wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(walls_sprites, all_sprites)
        image1 = blocks_images[tile_type]
        self.image = pygame.transform.scale(image1, (size_block, size_block))
        self.rect = self.image.get_rect().move(
            size_block * pos_x, size_block * pos_y)

    # для обновления координат объекта во время смены режима экрана
    def update_coords(self, step):
        self.rect = self.rect.move(step[0], step[1])


"""создание спрайта травы"""
class Grass(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(grass_sprites, all_sprites)
        image1 = blocks_images[tile_type]
        self.image = pygame.transform.scale(image1, (size_block, size_block))
        self.rect = self.image.get_rect().move(
            size_block * pos_x, size_block * pos_y)

    # для обновления координат объекта во время смены режима экрана
    def update_coords(self, step):
        self.rect = self.rect.move(step[0], step[1])


"""создание спрайта игрока"""
class Player(pygame.sprite.Sprite):
    def __init__(self, player_image, pos_x, pos_y):
        super().__init__(player_sprite, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = size_block * pos_x
        self.rect.y = size_block * pos_y
        self.count_money = 0
        self.count_lifes = 3
        self.count_bullets = 10

        # индексы в списке с анимацией относительно направления движения игрока
        self.animation_right = [9, 10, 11]
        self.animation_left = [6, 7, 8]
        self.animation_up = [3, 4, 5]
        self.animation_down = [0, 1, 2]

    # получение количества пуль у игрока
    def get_count_bullets(self):
        return self.count_bullets

    # изменение количества пуль у игрока
    def update_count_bullets(self, count):
        self.count_bullets += count

    # изменение количества денег у игрока
    def update_count_money(self, count):
        self.count_money += count

    # получение количества денег у игрока
    def get_count_money(self):
        return self.count_money

    # изменение количества жизней у игрока
    def update_count_lifes(self, count):
        self.count_lifes += count

    # получение количества жизней у игрока
    def get_count_lifes(self):
        return self.count_lifes

    # получение координат объекта в клетках
    def get_coords_in_blocks(self, fullscreen):
        if fullscreen:
            return self.rect.x // size_block - STEP_SCREEN_X, self.rect.y // size_block - STEP_SCREEN_Y
        return self.rect.x // size_block, self.rect.y // size_block

    # для обновления координат объекта во время смены режима экрана
    def update_coords(self, step):
        self.rect = self.rect.move(step[0], step[1])

    # координаты игрока
    def get_coords(self):
        return self.rect.x, self.rect.y

    # меняем изображение игрока относительно его движения
    def animation(self, sheet, move):
        if move == "D":
            self.change_image(sheet[self.animation_down[0]])  # ставим первую в списке анимаций изображение
            self.animation_down.append(self.animation_down[0])  # добавляем ее в конец списка
            self.animation_down.pop(0)  # удаляем первое изображение из списка
        elif move == "U":
            self.change_image(sheet[self.animation_up[0]])  # анологично
            self.animation_up.append(self.animation_up[0])
            self.animation_up.pop(0)
        elif move == "L":
            self.change_image(sheet[self.animation_left[0]])
            self.animation_left.append(self.animation_left[0])
            self.animation_left.pop(0)
        elif move == "R":
            self.change_image(sheet[self.animation_right[0]])
            self.animation_right.append(self.animation_right[0])
            self.animation_right.pop(0)

    # смена изображения игрока
    def change_image(self, image):
        self.image = image

    # изменение положения игрока на поле
    def update(self, step, necessary_count_money, timer):
        self.rect = self.rect.move(step[0], step[1])  # сначала перемещаем игрока
        if pygame.sprite.spritecollideany(self, walls_sprites):  # если игрок касается стен, то перемещаем его обратно
            self.rect = self.rect.move(-step[0], -step[1])
        if pygame.sprite.spritecollideany(self, ghost_sprites):  # если игрок сталкивается с призраком
            self.rect = self.rect.move(-step[0], -step[1])
            # проверяем прошло ли время после предыдущего касания с призраком
            if (pygame.time.get_ticks() - timer.get_timer()) // 1000 > 0.3:
                timer.new_timer()  # обнуляем таймер
                sound_wound.play()
                player.update_count_lifes(-1)  # забираем жизнь у игрока
                if player.get_count_money() >= 100:  # забираем деньги у игрока, только если они у него есть
                    player.update_count_money(-100)
                return "loss"  # возвращаем проигрыш

        # если игрок попал в партал
        if pygame.sprite.spritecollideany(self, portal_sprite):

            # если игрок попадает в портал, проверякм набрал ли он нужное количество денег
            if self.rect.x == portal_sprite.sprites()[0].rect.x and self.rect.y == portal_sprite.sprites()[0].rect.y:
                # self.rect = self.rect.move(-step[0], -step[1])
                if self.count_money >= necessary_count_money:  # если игрок набрал, он прошел уровень
                    update_level()
                    return "win"  # возвращаем победу

        if pygame.sprite.spritecollide(self, money_sprites, True):  # если игрок касается денег
            self.count_money += 100


"""создание спрайта призрака"""
class Ghost(pygame.sprite.Sprite):
    def __init__(self, ghost_image, pos_x, pos_y):
        super().__init__(ghost_sprites, all_sprites)
        self.image = ghost_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos_x
        self.rect.y = pos_y

        # индексы в списки с анимацией относительно направления движения призрака
        self.animation_right = [6, 7, 8]
        self.animation_left = [3, 4, 5]
        self.animation_up = [9, 10, 11]
        self.animation_down = [0, 1, 2]

        self.direction = None

    # получение координат объекта в клетках
    def get_coords_in_blocks(self, fullscreen):
        if fullscreen:
            return self.rect.x // size_block - STEP_SCREEN_X, self.rect.y // size_block - STEP_SCREEN_Y
        return self.rect.x // size_block, self.rect.y // size_block

    # для обновления координат объекта во время смены режима экрана
    def update_coords(self, step):
        self.rect = self.rect.move(step[0], step[1])

    # меняем изображение призрака относительно его движения
    def animation(self, sheet, move):
        if move == "D":
            self.change_image(sheet[self.animation_down[0]])  # ставим первую в списке анимаций изображение
            self.animation_down.append(self.animation_down[0])  # добавляем ее в конец списка
            self.animation_down.pop(0)  # удаляем первое изображение из списка
        elif move == "U":
            self.change_image(sheet[self.animation_up[0]])  # анологично
            self.animation_up.append(self.animation_up[0])
            self.animation_up.pop(0)
        elif move == "L":
            self.change_image(sheet[self.animation_left[0]])
            self.animation_left.append(self.animation_left[0])
            self.animation_left.pop(0)
        elif move == "R":
            self.change_image(sheet[self.animation_right[0]])
            self.animation_right.append(self.animation_right[0])
            self.animation_right.pop(0)

    # смена изображения призрака
    def change_image(self, image):
        self.image = image

    # определяем направление призрака
    def choice_direction(self):
        self.direction = random.choice(["R", "L", "U", "D"])
        if self.direction == "R":
            self.step = (STEP_GHOST, 0)
        elif self.direction == "L":
            self.step = (-STEP_GHOST, 0)
        elif self.direction == "U":
            self.step = (0, -STEP_GHOST)
        elif self.direction == "D":
            self.step = (0, STEP_GHOST)

    # изменение положения призрака на поле
    def update(self, timer):
        # флаг для работы выбора направления движения призрака,
        # если Folse значит направление выбрано, иначе продолжаем искать
        can = True
        while can:

            #  проверяем выбрано ли уже направление, если нет, то запускаем функцию для рандомного выбора
            if not self.direction:
                self.choice_direction()
            self.rect = self.rect.move(self.step[0], self.step[1])  # сначала перемещаем призрака

            # если призрак касается стен, то перемещаем его обратно
            if pygame.sprite.spritecollideany(self, walls_sprites):
                self.rect = self.rect.move(-self.step[0], -self.step[1])
                self.direction = None  # значит направление не подошло, повторяем все заново

            # если призрак сталкивается с игроком, перемещаем его обратно
            if pygame.sprite.spritecollideany(self, player_sprite):
                self.rect = self.rect.move(-self.step[0], -self.step[1])
                # проверяем прошло ли время после предыдущего касания с игроком
                if (pygame.time.get_ticks() - timer.get_timer()) // 1000 > 0.3:
                    timer.new_timer()  # обнуляем таймер
                    sound_wound.play()
                    player.update_count_lifes(-1)  # забираем жизнь у игрока
                    if player.get_count_money() >= 100:  # забираем деньги у игрока, только если они у него есть
                        player.update_count_money(-100)

                self.direction = None  # значит направление не подошло, повторяем все заново

            #  проверяем не сталкивается ли призрак с другими призраками, если да, то проделываеем все также
            for sprite in pygame.sprite.spritecollide(self, ghost_sprites, False):
                if sprite is not self:
                    self.rect = self.rect.move(-self.step[0], -self.step[1])
                    self.direction = None
            else:
                can = False  # значит направление выбрано
        return self.direction  # возвращаем направление движения


"""класс таймера для отсчета времени, когда игрок касается призрака"""
class Timer:
    def __init__(self):
        self.start_ticks = pygame.time.get_ticks()

    # получение текущего времени на таймере
    def get_timer(self):
        return self.start_ticks

    # обнуление таймера
    def new_timer(self):
        self.start_ticks = pygame.time.get_ticks()


"""класс камеры для ослеживания положения игрока на поле"""
class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # координаты передаваемого блока
    def get_coord_block(self, block):
        return block.rect.x, block.rect.y

    # сдвигаем объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционируем камеру относительно движения объекта
    def update(self, target, old, coord_block, step_player):
        self.dx, self.dy = 0, 0  # обнуляем смешение

        # если игрок находиться в левой части экрана и движеться влево,
        # то проверяем где находится блок стены с координатами (0, 0)
        if target.rect.x <= 300 and step_player[0] < 0:

            if coord_block[0][0] != 0:  # если координата х блока не равна 0, то делаем смещение для всех объектов
                self.dx = old[0] - target.rect.x

        # если игрок находиться в правой части экрана и движеться вправо,
        # то проверяем где находится блок стены с координатами (WIDTH_SCREEN - size_block, HEIGHT_SCREEN - size_block),
        # т.е. самого правого нижнего блока
        elif target.rect.x >= WIDTH_SCREEN - 300 and step_player[0] > 0:
            # если координата х блока не равна (WIDTH_SCREEN - size_block), то делаем смещение для всех объектов
            if coord_block[1][0] != WIDTH_SCREEN - size_block:
                self.dx = old[0] - target.rect.x

        # если игрок находиться в верхней части экрана и движеться вверх,
        # то проверяем где находится блок стены с координатами (0, 0)
        elif target.rect.y <= 250 and step_player[1] < 0:

            if coord_block[0][1] != 0:  # если координата у блока не равна 0, то делаем смещение для всех объектов
                self.dy = old[1] - target.rect.y

        # если игрок находиться в нижней части экрана и движеться вниз,
        # то проверяем где находится блок стены с координатами (WIDTH_SCREEN - size_block, HEIGHT_SCREEN - size_block),
        # т.е. самого правого нижнего блока
        elif target.rect.y >= HEIGHT_SCREEN - 250 and step_player[1] > 0:

            # если координата у блока не равна (HEIGHT_SCREEN - size_block), то делаем смещение для всех объектов
            if coord_block[1][1] != HEIGHT_SCREEN - size_block:
                self.dy = old[1] - target.rect.y

        else:
            self.dx = 0
            self.dy = 0


"""создание спрайта пули игрока"""
class Bullet(pygame.sprite.Sprite):
    def __init__(self, bullet_image, pos_x, pos_y, move):
        super().__init__(bullet_sprites, all_sprites)
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.find_step_bullet(move)

    # для обновления координат объекта во время смены режима экрана
    def update_coords(self, step):
        self.rect = self.rect.move(step[0], step[1])

    # определяем шаг пули, исходя из напраления движения
    def find_step_bullet(self, move_attack):
        if move_attack == "D":
            self.step = (0, SPEED_BULLET)
        elif move_attack == "U":
            self.step = (0, -SPEED_BULLET)
        elif move_attack == "R":
            self.step = (SPEED_BULLET, 0)
        elif move_attack == "L":
            self.step = (-SPEED_BULLET, 0)

    # изменение положения пули на поле
    def update(self):
        self.rect = self.rect.move(self.step[0], self.step[1])  # сначала перемещаем пулю
        if pygame.sprite.spritecollideany(self, walls_sprites):  # если пуля касается стен, то удаляем ее
            self.kill()

        # если пуля сталкивается с призраком, то удаляем призрака и пулю
        if pygame.sprite.spritecollide(self, ghost_sprites, True):
            self.kill()


"""создание спрайта денег"""
class Money(pygame.sprite.Sprite):
    def __init__(self, money_image, pos_x, pos_y):
        super().__init__(money_sprites, all_sprites)
        self.image = money_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos_x + 10
        self.rect.y = pos_y + 15

    # получение координат объекта в клетках
    def get_coords_in_blocks(self, fullscreen):
        if fullscreen:
            return (self.rect.x - 10) // size_block - STEP_SCREEN_X, (self.rect.y - 15) // size_block - STEP_SCREEN_Y
        return (self.rect.x - 10) // size_block, (self.rect.y - 15) // size_block

    # для обновления координат объекта во время смены режима экрана
    def update_coords(self, step):
        self.rect = self.rect.move(step[0], step[1])


"""функция проверяет можно ли делать деньги в этой клетке карты (если эта клетка - трава, то можно)"""
def create_money(level, money_image, pos_x, pos_y, full_screen):
    if full_screen:  # определяем смещение, относительно того вколючен ли полноэкранный режим или двигалась ли камера
        dx, dy = -STEP_SCREEN_X, -STEP_SCREEN_Y
    else:
        dx, dy = screen_offset()
    if level[pos_y][pos_x] == '.':
        # координаты игрока в клетках
        pos_player = player.get_coords_in_blocks(full_screen)
        # проверяем не стоит ли на этой клетке игрок
        # (+ 1 для того, чтобы проверить ситуацию, где игрок на двух клетках стоит)
        if (pos_x, pos_y) != [pos_player[0], pos_player[1]]:
        # перебираем все деньги и проверяем совпадает ли их координата с нынешней
            for money in money_sprites:
                if (pos_x, pos_y) == money.get_coords_in_blocks(full_screen):
                    return False
        Money(money_image, pos_x * size_block - dx, pos_y * size_block - dy)


"""функция проверяет можно ли создать призрака в этой клетке карты (если эта клетка - трава, то можно)"""
def create_ghost(level, ghost_image, pos_x, pos_y, full_screen):
    if full_screen:
        dx, dy = -STEP_SCREEN_X, -STEP_SCREEN_Y
    else:
        dx, dy = screen_offset()
    if level[pos_y][pos_x] == '.':
        # координаты игрока в клетках
        pos_player = player.get_coords_in_blocks(full_screen)
        # проверяем не стоит ли на этой клетке игрок и проверяем на 1 клетку вокруг него
        if (pos_x, pos_y) not in [(pos_player[0], pos_player[1]), (pos_player[0] + 1, pos_player[1]),
                                      (pos_player[0] - 1, pos_player[1]), (pos_player[0], pos_player[1] + 1),
                                      (pos_player[0], pos_player[1] - 1)]:
            # перебираем всех уже существующих призраков и проверяем совпадает ли их координата с нынешней
            for ghost in ghost_sprites:
                ghost_x_y = ghost.get_coords_in_blocks(full_screen)
                #  проверяем есть ли другие призраки в нашем блоке и блока сверху, снизу, справа, слева
                if (pos_x, pos_y) in [(ghost_x_y[0], ghost_x_y[1]), (ghost_x_y[0] + 1, ghost_x_y[1]),
                                      (ghost_x_y[0] - 1, ghost_x_y[1]), (ghost_x_y[0], ghost_x_y[1] + 1),
                                      (ghost_x_y[0], ghost_x_y[1] - 1)]:
                    return False
            Ghost(ghost_image, pos_x * size_block - dx, pos_y * size_block - dy)


"""разворачивает или сворачивает окно игры"""
def full_screen_mode(mode, levelx, levely):
    global STEP_SCREEN_X, STEP_SCREEN_Y
    #  сворачиваем экран
    if mode:
        display = (pygame.display.Info().current_w, pygame.display.Info().current_h)  # разрешение экрана пк
        block_coords = camera.get_coord_block(walls_sprites.sprites()[-1])  # координаты самого правого нижнего блока
        pygame.display.set_mode((WIDTH_SCREEN, HEIGHT_SCREEN))  # меняем размер окна

        # если игрок находился в левой части карты при развернутом экране и коордю. х < WIDTH_SCREEN // 2
        # (т.е. меньше половины свернутого экрана), тогда изменение по х = 0
        if WIDTH_SCREEN // 2 > player.rect.x and player.rect.x < display[0] // 2:
            dx = 0

        # если игрок находился в правой части карты при развернутом экране и
        # расстояние display[0] - player.rect.x (т.е. расстояние от игрока до правой стены карты) < WIDTH_SCREEN // 2
        elif WIDTH_SCREEN // 2 > display[0] - player.rect.x and player.rect.x > display[0] // 2:
            # из коорд. крайнего блока вычитаем оступ и ширину экраана и прибавляем размер блока
            dx = block_coords[0] - STEP_SCREEN_X - WIDTH_SCREEN + size_block

        # если игрок находился в левой части карты при развернутом экране и коордю. х > WIDTH_SCREEN // 2
        # (т.е. меньше половины свернутого экрана), тогда изменение по х = 0
        elif player.rect.x < display[0] // 2:
            # из коорд. х игрока вычитаем половину свернутого экрана, а дальше делим
            # и умножаем на size_block, чтобы dx нацело делилось на size_block
            dx = (player.rect.x - WIDTH_SCREEN // 2) // size_block * size_block

        # если игрок находился в правой части карты при развернутом экране и расстояние
        else:
            # из коорд.крайнего блока ширину экрана, а дальше делим
            # и умножаем на size_block, чтобы dx нацело делилось на size_block
            dx = (block_coords[0] - WIDTH_SCREEN) // size_block * size_block - size_block

        # дальше по такому же принципу только с координами y
        if HEIGHT_SCREEN // 2 > player.rect.y and player.rect.y < display[1] // 2:
            dy = 0
        elif HEIGHT_SCREEN // 2 > display[1] - player.rect.y and player.rect.y > display[1] // 2:
            dy = block_coords[1] - STEP_SCREEN_Y - HEIGHT_SCREEN + size_block
        elif player.rect.y < display[1] // 2:
            dy = 0
        else:
            dy = (block_coords[1] - HEIGHT_SCREEN) // size_block * size_block - size_block

        for sprite in all_sprites:
            sprite.update_coords((-(dx + STEP_SCREEN_X), -(dy + STEP_SCREEN_Y)))  # передаем в метод спрайта смещение
        return False  # возвращаем False, так как экран свернули

    # разворачиваем экран
    else:
        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # меняем размер окна
        x = pygame.display.Info().current_w  # ширина развернутого экрана
        y = pygame.display.Info().current_h  # высота развернутого экрана
        # отступ, чтобы карта была поцентру (вычитаем из развернутого экрана размер карты и делим на 2)
        STEP_SCREEN_X = (x - (levelx + 1) * size_block) // 2  # levelx + 1, тк отчет с 0
        STEP_SCREEN_Y = (y - (levely + 1) * size_block) // 2
        coords_1 = camera.get_coord_block(all_sprites.sprites()[0])  # коорд. самого левого вернего блока
        for sprite in all_sprites:
            sprite.update_coords((abs(coords_1[0]) + STEP_SCREEN_X, abs(coords_1[1]) + STEP_SCREEN_Y))
        return True  # возвращаем True, так как экран развернули


"""рисование в углу окна количества денег, жизней и патрон"""
def draw_results(screen, image_money, image_heart, count_hearts, max_count_money, full_screen):
    stepx, stepy = 0, 0  # оступ, зависит от развернуто ли окно или нет
    if full_screen:
        stepx, stepy = STEP_SCREEN_X * 3, STEP_SCREEN_Y

    # отрисовка полупрозрачного прямоугольника (в нем будет вся инфа)
    pygame.gfxdraw.box(screen, pygame.Rect(WIDTH_SCREEN - 180 + stepx, 20 + stepy, 160, 100), (0, 0, 0, 100))
    screen.blit(image_money, (WIDTH_SCREEN - 170 + stepx, 35 + stepy))  # отрисовка изображения купюры

    font = pygame.font.Font(None, 25)
    string_rendered = font.render(f"{str(player.get_count_money())}/{max_count_money}", 1, pygame.Color("#cccccc"))
    intro_rect = string_rendered.get_rect()
    intro_rect.x = WIDTH_SCREEN - 125 + stepx
    intro_rect.y = 35 + stepy
    screen.blit(string_rendered, intro_rect)  # отрисока количества денег игроока

    screen.blit(bullet_image_in_rect, (WIDTH_SCREEN - 170 + stepx, 55 + stepy))  # отрисовка изображения пули
    string_rendered = font.render(str(player.get_count_bullets()), 1, pygame.Color("#cccccc"))
    intro_rect = string_rendered.get_rect()
    intro_rect.x = WIDTH_SCREEN - 125 + stepx
    intro_rect.y = 63 + stepy
    screen.blit(string_rendered, intro_rect)  # отрисока количества патрон игроока

    step_heart = 0
    for _ in range(count_hearts):
        screen.blit(image_heart, (WIDTH_SCREEN - 170 + step_heart + stepx, 85 + stepy))  # отрисовка сердца
        step_heart += 30


"""создание кнопок во время паузы"""
def create_button_pause(full_screen, text):
    # данные для кнопок ( x, y, ширинаб высота, x и y для текста)
    list_data_buttons = {"Продолжить": [380, 380, 225, 60, 385, 385],
                         "Выход": [630, 380, 140, 60, 645, 385]}
    stepx, stepy = 0, 0  # оступ, зависит от развернуто ли окно или нет
    if full_screen:
        stepx, stepy = STEP_SCREEN_X * 1.9, STEP_SCREEN_Y
    but = list_data_buttons[text]
    return screensaver.Button(but[0] + stepx, but[1] + stepy, but[2], but[3], (text,  but[4] + stepx, but[5] + stepy))


"""отрисовка фона во время паузы (полупрозрачный прямоугольник)"""
def pause_in_game(screen, full_screen):
    stepx, stepy = 0, 0  # оступ, зависит от развернуто ли окно или нет
    if full_screen:
        stepx, stepy = STEP_SCREEN_X * 1.9, STEP_SCREEN_Y
    pygame.gfxdraw.box(screen, pygame.Rect(WIDTH_SCREEN // 2 - 200 + stepx, HEIGHT_SCREEN // 2 + stepy,
                                           430, 100), (0, 0, 0, 120))


"""обновляем все объекты на поле при запуске игры"""
def update_all():
    global level, level_x, camera, level_y, player

    with open("data/number_last_level.txt", "r", encoding='utf8') as f:  # открываем файл с номером текущего уровня
        num_level = int(f.read())

    # получаем из таблицы по номеру уровня имя файла, кол-ло призраков на поле и денег, которые игрок должен собрать
    db = _sqlite3.connect('data/data_levels.db')
    sql = db.cursor()
    data = sql.execute(f"""SELECT level_name, count_ghost, count_money FROM Game WHERE id == {num_level}""").fetchone()
    # имя файла, кол-во призраков на поле, кол-во денег, котое надо собрать
    level_name, max_count_ghost, need_max_count_money = data[0], data[1], data[2]
    db.close()

    for sprite in all_sprites:  # удаляем все объекты
        sprite.kill()

    level = load_level(level_name)  # загружаем уровень
    player, level_x, level_y = generate_level(level)  # получаем размеры поля и игрока
    camera = Camera()  # создаем камеру для слежки за игроком

    # создаем призраков и деньги
    while len(money_sprites) != MAX_COUNT_MONEY:
        create_money(level, money_image, random.randint(0, level_x), random.randint(0, level_y), False)
    while len(ghost_sprites) != max_count_ghost:
        create_ghost(level, frames_ghost[0], random.randint(0, level_x), random.randint(0, level_y), False)

    return max_count_ghost, need_max_count_money, num_level, level_x, level_y


"""если игрок находится не ровно на блоке, а посередине и при этом пытаеся двигаться, но ему мешает этот блок"""
def steping(level, move, necessary_count_money, full_screen, timer):
    # к примеру  # - стена; . - трава; @ - игрок
    #   #######
    #   #..@..#
    #   ####.##
    # если игрок находится на пол блока правее (на двух блоках одновременно) и пытается идти вниз, то не получится,
    # тк нижняя стена мешает
    # ниже я это обрабатываю, чтобы в таком случае игрок сначала сделал шаг вправо, встав ровно на блок над травой
    if full_screen:  # относительно того, включен ли полноэкранный режим, делаем смещение игрока
        dx, dy = -STEP_SCREEN_X, -STEP_SCREEN_Y  # просто отступ до начала карты
    else:
        dx, dy = screen_offset()  # если камера сдвинута

    # если игрок стоит, как в примере, проверяем есть ли под ним стена и если ли рядом с этой стеной трава и
    # насколько игрок вылез за пределы стена (надо на не больше половины блока)
    if move == "D" and level[(player.rect.y + dy) // size_block + 1][(player.rect.x + dx) // size_block + 1] in "_."\
            and level[(player.rect.y + dy) // size_block + 1][(player.rect.x + dx) // size_block] == "#"\
            and size_block // 2 <= player.rect.x + dx - (player.rect.x + dx) // size_block * size_block <= size_block:
        player.update((10, 0), necessary_count_money, timer)

    # если игрок стоит как в примере + 1 блок и немного праве
    elif move == "D" and level[(player.rect.y + dy) // size_block + 1][(player.rect.x + dx) // size_block] in "_."\
            and level[(player.rect.y + dy) // size_block + 1][(player.rect.x + dx) // size_block + 1] == "#"\
            and 0 < player.rect.x + dx - (player.rect.x + dx) // size_block * size_block <= size_block // 2:
        player.update((-10, 0), necessary_count_money, timer)

    # дальше те же действия, только меняем положение игрока
    elif move == "U" and level[(player.rect.y + dy) // size_block - 1][(player.rect.x + dx) // size_block + 1] in "_."\
            and level[(player.rect.y + dy) // size_block - 1][(player.rect.x + dx) // size_block] == "#"\
            and size_block // 2 <= player.rect.x + dx - (player.rect.x + dx) // size_block * size_block <= size_block:
        player.update((10, 0), necessary_count_money, timer)

    elif move == "U" and level[(player.rect.y + dy) // size_block - 1][(player.rect.x + dx) // size_block] in "_."\
            and level[(player.rect.y + dy) // size_block - 1][(player.rect.x + dx) // size_block + 1] == "#"\
            and 0 < player.rect.x + dx - (player.rect.x + dx) // size_block * size_block <= size_block // 2:
        player.update((-10, 0), necessary_count_money, timer)

    elif move == "R" and level[(player.rect.y + dy) // size_block + 1][(player.rect.x + dx) // size_block + 1] in "_." \
            and level[(player.rect.y + dy) // size_block][(player.rect.x + dx) // size_block + 1] == "#" \
            and size_block // 2 <= player.rect.y + dy - (player.rect.y + dy) // size_block * size_block <= size_block:
        player.update((0, 10), necessary_count_money, timer)

    elif move == "R" and level[(player.rect.y + dy) // size_block][(player.rect.x + dx) // size_block + 1] in "_." \
            and level[(player.rect.y + dy) // size_block + 1][(player.rect.x + dx) // size_block + 1] == "#" \
            and 0 < player.rect.y + dy - (player.rect.y + dy) // size_block * size_block <= size_block // 2:
        player.update((0, -10), necessary_count_money, timer)

    elif move == "L" and level[(player.rect.y + dy) // size_block + 1][(player.rect.x + dx) // size_block - 1] in "_." \
            and level[(player.rect.y + dy) // size_block][(player.rect.x + dx) // size_block - 1] == "#" \
            and size_block // 2 <= player.rect.y + dy - (player.rect.y + dy) // size_block * size_block <= size_block:
        player.update((0, 10), necessary_count_money, timer)

    elif move == "L" and level[(player.rect.y + dy) // size_block][(player.rect.x + dx) // size_block - 1] in "_." \
            and level[(player.rect.y + dy) // size_block + 1][(player.rect.x + dx) // size_block - 1] == "#" \
            and 0 < player.rect.y + dy - (player.rect.y + dy) // size_block * size_block <= size_block // 2:
        player.update((0, -10), necessary_count_money, timer)


"""получение смещения относительно того, в какой части карты находится игрок, если окно маленькое"""
def screen_offset():
    coords_block = camera.get_coord_block(walls_sprites.sprites()[-1])  # коорд. самого правого нижнего блока
    # из длины карты вычитаем длину до блока, коорд. которого меняюся, когда камера двигается
    dx = len(level[0]) * size_block - coords_block[0] - size_block
    dy = len(level) * size_block - coords_block[1] - size_block
    return dx, dy


"""обновление уровня"""
def update_level():
    with open("data/number_last_level.txt", "r+", encoding='utf8') as f:
        num_level = f.read()
        # проверяем есть ли в бд следующий уровень, если да - обновляем, если нет - оставляем текущий
        db = _sqlite3.connect('data/data_levels.db')
        sql = db.cursor()
        # отмечаем в бд, что уровень пройден и получаем следующий
        sql.execute(f"""UPDATE Game SET passed = 'yes' WHERE id = {int(num_level)}""")
        data = sql.execute(f"""SELECT level_name FROM Game WHERE id == {int(num_level) + 1}""").fetchone()
        db.commit()
        if data:  # если есть следующий уровень, то удаляем текущий из файла
            f.truncate(0)
            f.seek(0)
            f.write(str(int(num_level) + 1))  # обновляем файл, где записан текущий уровень


"""основная функция"""
def main():
    pygame.init()
    pygame.mixer.music.set_volume(screensaver.volume_game)  # устанавливаем громкость
    sound_game_over.set_volume(screensaver.volume_game)
    sound_win.set_volume(screensaver.volume_game)
    sound_bullet.set_volume(screensaver.volume_game)
    sound_wound.set_volume(screensaver.volume_game)

    screen = pygame.display.set_mode(size)

    timer = Timer()  # таймер для отслеживания времени, при столкновении игрока и призрака
    timer_bullets = Timer()  # таймер для пополнения патронов
    timer_game_over_show_level = Timer()  # таймер для отрисовка надписи в конце игры и уровня в начале

    # получаем кол-во прираков на поле, сколько денег нужно собрать, номер уровня и размеры поля
    max_count_ghost, necessary_count_money, num_level, levelx, levely = update_all()

    button_continue, button_back = None, None  # кнопки продолжения и выхода во время паузы
    step, move = None, "D"  # шаг и направление (направление по умолчанию значит куда полетит пуля в самом начале игры)

    running = True  # флаг для основного цикла
    moving_player = False  # флаг для обозначения движется ли игрока
    game_playing = True  # флаг для обозначения окончена ли игры
    full_screen = False  # флаг для обозначения развернуто ли окно игры
    game_over = False  # флаг для обозначения окончена ли игра
    pause = False  # флаг для обозначения включена ли пауза
    back = False  # флаг для обозначения выходим ли из игры
    player_won = False  # флаг для обозначения прошел ли игрок уровень
    showing_level = True  # флаг для обозначения идет ли отрисовка уровня (номер)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and pause:  # если пауза включена, отслеживаем нажатие на кнопки
                if button_continue.pressed(event.pos):
                    game_playing = True  # продолжаем игру
                    pause = False
                    pygame.mixer.music.set_volume(screensaver.volume_menu_pause)  # увеличиваем громкость
                elif button_back.pressed(event.pos):
                    pause = False
                    back = True  # выходим из игры
                    pygame.mixer.music.set_volume(screensaver.volume_menu_pause)  # уменьшаем громкость

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r and game_playing:
                    attack(move, bullet_image, player.get_coords())  # запускаем функцию по созданию пули

                if event.key == pygame.K_ESCAPE and not game_over:  # включение паузы
                    pygame.mixer.music.set_volume(screensaver.volume_menu_pause)  # уменьшаем громкость
                    game_playing = False  # останавливаем игру
                    pause = True  # вклучаем паузу
                    button_continue = create_button_pause(full_screen, "Продолжить")  # создание кнопок
                    button_back = create_button_pause(full_screen, "Выход")

                if pygame.key.get_pressed()[pygame.K_LCTRL] and pygame.key.get_pressed()[pygame.K_c]:
                    full_screen = full_screen_mode(full_screen, levelx, levely)  # передаем включен ли full_screen режим
                    if pause:
                        # заново создаем кнопки, потому что при вкл/выкл полноэкранного режима кнопки съехали
                        button_continue = create_button_pause(full_screen, "Продолжить")
                        button_back = create_button_pause(full_screen, "Выход")

                if event.key == pygame.K_RIGHT:
                    step, move = (STEP_PLAYER, 0), "R"
                    moving_player = True
                if event.key == pygame.K_LEFT:
                    step, move = (-STEP_PLAYER, 0), "L"
                    moving_player = True
                if event.key == pygame.K_UP:
                    step, move = (0, -STEP_PLAYER), "U"
                    moving_player = True
                if event.key == pygame.K_DOWN:
                    step, move = (0, STEP_PLAYER), "D"
                    moving_player = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT\
                        or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    moving_player = False
                    player.change_image(frames_player[0])

        screen.fill("#808080")

        if game_playing:

            old_coords = player.get_coords()  # координаты игрока перед ходом

            for sprite in bullet_sprites:  # обновление координат всех пуль
                sprite.update()

            for sprite in ghost_sprites:  # обновление координат всех призраков
                move_ghost = sprite.update(timer)
                sprite.animation(frames_ghost, move_ghost)  # анимация призрака

            if moving_player:
                if player.update(step, necessary_count_money, timer) == "win":  # значит игрок выиграл
                    # обнуляем таймер, чтобы пошел отсчет сколько отрисовывать заставку
                    timer_game_over_show_level = Timer()
                    game_playing = False  # игра оставливается
                    game_over = True  # начинается заставка в конце игры
                    player_won = True  # запускаются действия, если игрок выирал
                    sound_win.play()
                # если игрок пытается сдвинуться, надясь на середине блока
                steping(level, move, necessary_count_money, full_screen, timer)
                # передаем в метод анимации игрока список с изображениями(анимация сама) и направление движения
                player.animation(frames_player, move)

                # координаты левого верхнего блока карты и правого нижнего блока
                coords_block = [camera.get_coord_block(walls_sprites.sprites()[0]),
                                  camera.get_coord_block(walls_sprites.sprites()[-1])]

                # обновляем положение камеры, если выключен полноэкранный режим,
                # передавая ей игрока, старые координаты игрока координаты блоков и смещение иг.
                if not full_screen:
                    camera.update(player, old_coords, coords_block, step)

                for sprite in all_sprites:  # обновление координат всех спрайтов
                    camera.apply(sprite)

            # следим за кол-вом денег и призраков на поле, если что создаем новые
            while len(money_sprites) < MAX_COUNT_MONEY:
                create_money(level, money_image, random.randint(0, level_x), random.randint(0, level_y), full_screen)
            while len(ghost_sprites) < max_count_ghost:
                create_ghost(level, frames_ghost[0], random.randint(0, level_x),
                             random.randint(0, level_y), full_screen)

            if player.get_count_lifes() == 0:  # если жизни игрока закончились, он проиграл
                timer_game_over_show_level = Timer()  # обнуляем таймер, чтобы пошел отсчет отрисовки заставки
                game_playing = False  # игра останавливается
                game_over = True  # заставка в конце игры
                player_won = False  # запускаются действия, если игрок проиграл
                sound_game_over.play()

            # пополнение патрон каждые 3 сек, если их меньше 10
            if (pygame.time.get_ticks() - timer_bullets.get_timer()) // 1000 > 3 \
                    and player.get_count_bullets() < MAX_COUNT_BULLETS:
                timer_bullets.new_timer()
                player.update_count_bullets(1)

        # отрисовка всех объектов
        all_sprites.draw(screen)
        player_sprite.draw(screen)
        ghost_sprites.draw(screen)
        bullet_sprites.draw(screen)

        # отрисовка кол-ва денег, патрон, жизней игрока в углу экрана
        draw_results(screen, money_image_result, heart_image, player.get_count_lifes(),
                     necessary_count_money, full_screen)

        if pause:  # если пауза, то отрисовываем все кнопки
            pause_in_game(screen, full_screen)  # рисует полупрозрачный прямоугольник под кнопками
            button_continue.draw_button(screen, blocks_images["wall"], True)  # отвечает за продолжение игры
            button_continue.write(screen, 35)
            button_back.draw_button(screen, blocks_images["wall"], True)  # отвечает за выход
            button_back.write(screen, 35)

        elif game_over:  # надпись о конце игры
            if (pygame.time.get_ticks() - timer_game_over_show_level.get_timer()) // 1000 > 2:
                back = True  # если 2 сек прошло выдим из игры
            else:
                show_game_over(screen, full_screen, player_won)

        elif showing_level:  # надпись в начале игры (уровень)
            if (pygame.time.get_ticks() - timer_game_over_show_level.get_timer()) // 1000 > 1:
                showing_level = False  # если сек прошла убираем надпись с уровнем
            else:
                show_numlevel(screen, full_screen, f"LEVEL {num_level}")

        pygame.display.flip()
        clock.tick(FPS)
        if back:  # если игрок выходит из игры в главное меню или не игрок
            running = False
            screensaver.screensaver_game()

    pygame.quit()


size = WIDTH_SCREEN, HEIGHT_SCREEN

#  словарь с изображениями стены и травы
blocks_images = {"wall": load_image("wall.png", (size_block, size_block), -1),
                 "grass": load_image("grass.png", (size_block, size_block), -1),
                 "portal": load_image("portal.png", (size_block, size_block), -1)}

# создание групп спрайтов
all_sprites = pygame.sprite.Group()
grass_sprites = pygame.sprite.Group()
walls_sprites = pygame.sprite.Group()
ghost_sprites = pygame.sprite.Group()
player_sprite = pygame.sprite.Group()
bullet_sprites = pygame.sprite.Group()
money_sprites = pygame.sprite.Group()
portal_sprite = pygame.sprite.Group()

frames_player = cut_sheet(load_image("player.png", (120, 160), -1), 3, 4)  # список с анимацией игрока
frames_ghost = cut_sheet(load_image("ghost.png", (110, 150), -1), 3, 4)  # список с анимацией призрака

# загузка изображений
bullet_image = load_image("bullet.png", (10, 10), -1)
bullet_image_in_rect = load_image("bullet.png", (30, 30), -1)
money_image = load_image("money_50.jpg", (20, 10), -1)
money_image_result = load_image("money_50.jpg", (35, 15), -1)
heart_image = load_image("heart.png", (30, 30), -1)

STEP_SCREEN_X = 0  # отступ при развернутом экране
STEP_SCREEN_Y = 0

pygame.init()
pygame.display.set_caption(NAME_GAME)  # изменение названия игры
icon = pygame.image.load("data\icon.png")
pygame.display.set_icon(icon)  # изменение иконки игры

#  загрузка музыки и звуков
pygame.mixer.music.load("data\music\music_fon.mp3")
sound_game_over = pygame.mixer.Sound("data\music\music_gameover.mp3")
sound_win = pygame.mixer.Sound("data\music\music_win.mp3")
sound_bullet = pygame.mixer.Sound("data\music\sound_bullet.mp3")
sound_wound = pygame.mixer.Sound("data\music\sound_wound.mp3")

clock = pygame.time.Clock()
FPS = 15

if __name__ == "__main__":
    screensaver.screensaver_game()
