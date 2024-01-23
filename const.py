import pygame

WIDTH_SCREEN = 1120  # ширина окна
HEIGHT_SCREEN = 720  # высота окна

size_block = 40  # размер блока

STEP_PLAYER = 10  # скорость игрока
STEP_GHOST = 5  # скорость призрака

SPEED_BULLET = 20  # скорость пули

# смещение при развернутом окне, чтобы карта была по центру
STEP_SCREEN_X = 90
STEP_SCREEN_Y = 30

MAX_COUNT_MONEY = 7  # максимальное кол-во купюр на поле
MAX_COUNT_BULLETS = 10  # максимальное кол-во патрон у игрока
MAX_COUNT_GHOST = 20  # максимальное кол-во призраков

COLOR_FONT = "#cccccc"

NAME_GAME = "Maze Runner: Money Hunt"
# текст с целью игры
TEXT_TARGET = [" Цель игрока пройти лабиринт, набрав нужное количество",
              "денег, которые разбросаны по всей карте. При этом не",
              "попадаясь в руки к призракам, на расстоянии они",
              "безвредны, но каждое столкновение с ними забирает",
              "одну жизни игрока, а их всего три. Как только все жизни",
              "заканчиваются, игра окончена. У игрока есть возможность",
              "убить призрака, для этого достаточно одного выстрела.",
              "Патроны не бесконечные, но пополняюся каждые три",
              "секунды.",
              " Дойдя до конца лабиринта, игрок переходит на новый",
              "уровень, который будет сложнее предыдущего."]


