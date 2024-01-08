import pygame
import os
import sys

from const import *

"""загрузка изображения"""
def load_image(name, size=None, colorkey=None):
    fullname = os.path.join('data', name)
    # проверяем существует ли такой файл
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    # при необходимости убираем фон
    if colorkey is not None:
        colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    if size:
        image = pygame.transform.scale(image, (size[0], size[1]))  # для листа с анимацией игрока
    # возврашаем изображение
    return image


"""загрузка уровня"""
def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


"""рисование всех предметов на карте уровня"""
def generate_level(level, player_image, ghost_image):
    player, ghost, x, y = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Wall('wall', x, y)
            elif level[y][x] == '.':
                Grass('grass', x, y)
            elif level[y][x] == '@':
                Grass('grass', x, y)
                player = Player(player_image, x, y)
            elif level[y][x] == '$':
                Grass('grass', x, y)
                ghost = Ghost(ghost_image, x, y)
    # вернем игрока, а также размер поля в клетках
    return player, ghost, x, y


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
def game_over(screen):
    text = "GAME OVER"
    font = pygame.font.Font(None, 130)
    string_rendered = font.render(text, 1, pygame.Color('red'))
    intro_rect = string_rendered.get_rect()
    intro_rect.x = 300
    intro_rect.y = 300
    screen.blit(string_rendered, intro_rect)


"""создание спрайта стены"""
class Wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(walls_sprites, all_sprites)
        image1 = blocks_images[tile_type]
        self.image = pygame.transform.scale(image1, (size_block, size_block))
        self.rect = self.image.get_rect().move(
            size_block * pos_x, size_block * pos_y)


"""создание спрайта травы"""
class Grass(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(grass_sprites, all_sprites)
        image1 = blocks_images[tile_type]
        self.image = pygame.transform.scale(image1, (size_block, size_block))
        self.rect = self.image.get_rect().move(
            size_block * pos_x, size_block * pos_y)


"""создание спрайта игрока"""
class Player(pygame.sprite.Sprite):
    def __init__(self, player_image, pos_x, pos_y):
        super().__init__(player_sprite)
        self.image = player_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = size_block * pos_x
        self.rect.y = size_block * pos_y

        # индексы в списки с анимацией относительно направления движения игрока
        self.animation_right = [13, 14, 15]
        self.animation_left = [9, 10, 11]
        self.animation_up = [5, 6, 7]
        self.animation_down = [1, 2, 3]

    # координаты игрока
    def get_coords(self):
        return self.rect.x, self.rect.y

    # меняем изображение игрока относительно его движения
    def animation(self, sheet, move):
        if move == "D":
            self.change_image(sheet[self.animation_down[0]])
            self.animation_down.append(self.animation_down[0])
            self.animation_down.pop(0)
        elif move == "U":
            self.change_image(sheet[self.animation_up[0]])
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
    def update(self, step):
        self.rect = self.rect.move(step[0], step[1])  # сначала перемещаем игрока
        if pygame.sprite.spritecollideany(self, walls_sprites):  # если игрок касается стен, то перемещаем его обратно
            self.rect = self.rect.move(-step[0], -step[1])
        if pygame.sprite.spritecollideany(self, ghost_sprites):  # если игрок сталкивается с призраком, то игра окончена
            return True


"""создание спрайта призрака"""
class Ghost(pygame.sprite.Sprite):
    def __init__(self, ghost_image, pos_x, pos_y):
        super().__init__(ghost_sprites)
        self.image = ghost_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = size_block * pos_x
        self.rect.y = size_block * pos_y

        # индексы в списки с анимацией относительно направления движения призрака
        self.animation_right = [6, 7, 8]
        self.animation_left = [3, 4, 5]
        self.animation_up = [9, 10, 11]
        self.animation_down = [0, 1, 2]

    # меняем изображение призрака относительно его движения
    def animation(self, sheet, move):
        if move == "D":
            self.change_image(sheet[self.animation_down[0]])
            self.animation_down.append(self.animation_down[0])
            self.animation_down.pop(0)
        elif move == "U":
            self.change_image(sheet[self.animation_up[0]])
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
    def update(self, target, old, coord_block, step_player, full_screen):
        if full_screen:
            width_screen, height_screen = (pygame.display.Info().current_w, pygame.display.Info().current_h)
            distance_left_right = 300
            distance_up_down = 250
        else:
            width_screen, height_screen = WIDTH_SCREEN, HEIGHT_SCREEN
            distance_left_right = 250
            distance_up_down = 200

        # если игрок находиться в левой части экрана и движеться влево,
        # то проверяем где находится блок стены с координатами (0, 0)
        if target.rect.x <= distance_left_right and step_player[0] < 0:

            if coord_block[0][0] != 0:  # если координата х блока не равна 0, то делаем смещение для всех объектов
                self.dx = old[0] - target.rect.x
                # возвращаем игрока на старые координаты, чтобы не было ускорения во время движения всех объектов
                player.update((-step_player[0], -step_player[1]))

            elif coord_block[0][0] == 0:  # если координата х блока равна 0, то смщение не делаем
                self.dx = 0

        # если игрок находиться в правой части экрана и движеться вправо,
        # то проверяем где находится блок стены с координатами (WIDTH_SCREEN - size_block, HEIGHT_SCREEN - size_block),
        # т.е. самого правого нижнего блока
        elif target.rect.x >= width_screen - distance_left_right and step_player[0] > 0:
            print(coord_block[1][0], width_screen - size_block)
            # если координата х блока не равна (WIDTH_SCREEN - size_block), то делаем смещение для всех объектов
            if coord_block[1][0] >= width_screen - size_block:
                self.dx = old[0] - target.rect.x
                # возвращаем игрока на старые координаты, чтобы не было ускорения во время движения всех объектов
                player.update((-step_player[0], -step_player[1]))

            # если координата х блока равна (WIDTH_SCREEN - size_block), то смщение не делаем
            elif coord_block[1][0] < width_screen - size_block:
                self.dx = 0

        # если игрок находиться в верхней части экрана и движеться вверх,
        # то проверяем где находится блок стены с координатами (0, 0)
        elif target.rect.y <= distance_up_down and step_player[1] < 0:

            if coord_block[0][1] != 0:  # если координата у блока не равна 0, то делаем смещение для всех объектов
                self.dy = old[1] - target.rect.y
                # возвращаем игрока на старые координаты, чтобы не было ускорения во время движения всех объектов
                player.update((-step_player[0], -step_player[1]))

            elif coord_block[0][1] == 0:  # если координата у блока равна 0, то смщение не делаем
                self.dy = 0

        # если игрок находиться в нижней части экрана и движеться вниз,
        # то проверяем где находится блок стены с координатами (WIDTH_SCREEN - size_block, HEIGHT_SCREEN - size_block),
        # т.е. самого правого нижнего блока
        elif target.rect.y >= height_screen - distance_up_down and step_player[1] > 0:

            # если координата у блока не равна (HEIGHT_SCREEN - size_block), то делаем смещение для всех объектов
            if coord_block[1][1] >= height_screen - size_block:
                self.dy = old[1] - target.rect.y
                # возвращаем игрока на старые координаты, чтобы не было ускорения во время движения всех объектов
                player.update((-step_player[0], -step_player[1]))

            # если координата у блока равна (HEIGHT_SCREEN - size_block), то смщение не делаем
            elif coord_block[1][1] < height_screen - size_block:
                self.dy = 0
        else:
            self.dx = 0
            self.dy = 0


"""основная функция"""
def main():
    pygame.init()
    size = WIDTH_SCREEN, HEIGHT_SCREEN
    screen = pygame.display.set_mode(size)

    step, move = None, None

    running = True  # флаг для основного цикла
    moving_player = False  # флаг для движения игрока
    game_overing = False  # флаг для окончания игры
    full_screen = False  # флаг для полноэкранного режима
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if full_screen:
                        pygame.display.set_mode(size)
                        full_screen = False
                    else:
                        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        full_screen = True
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
                moving_player = False
                player.change_image(frames_player[0])

        screen.fill((0, 0, 0))

        old_coords = player.get_coords()  # координаты игрока перед ходом

        if moving_player:
            if player.update(step):  # если игра окончена, то показываем заставку
                game_overing = True
            # передаем в метод анимации игрока список с изображениями(анимация сама) и направление движения
            player.animation(frames_player, move)

            # координаты левого верхнего блока карты и правого нижнего блока
            coords_block = [camera.get_coord_block(all_sprites.sprites()[0]),
                              camera.get_coord_block(all_sprites.sprites()[-1])]

            # обновляем положение камеры, передавая ей игрока, старые координаты игрока координаты блоков и смещение иг.
            camera.update(player, old_coords, coords_block, step, full_screen)

            for sprite in all_sprites:  # обновление координат всех спрайтов
                camera.apply(sprite)

            for sprite in ghost_sprites:  # обновление координат всех призраков
                camera.apply(sprite)

        # отрисовка всех объектов
        all_sprites.draw(screen)
        player_sprite.draw(screen)
        ghost_sprites.draw(screen)

        if game_overing:
            game_over(screen)

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


#  словарь с изображениями стены и травы
blocks_images = {"wall": load_image("wall.png"),
                 "grass": load_image("grass.png")}

# создание групп спрайтов
all_sprites = pygame.sprite.Group()
grass_sprites = pygame.sprite.Group()
walls_sprites = pygame.sprite.Group()
ghost_sprites = pygame.sprite.Group()
player_sprite = pygame.sprite.Group()


frames_player = cut_sheet(load_image("player.png", (160, 160), -1), 4, 4)  # список с анимацией игрока
frames_ghost = cut_sheet(load_image("ghost.png", (130, 150), -1), 3, 4)  # список с анимацией призрака
# здесь получаем игрока и размеры поля в клетках
player, ghost, level_x, level_y = generate_level(load_level("level_2.txt"), frames_player[0], frames_ghost[0])
camera = Camera()

clock = pygame.time.Clock()
FPS = 15

if __name__ == "__main__":
    main()