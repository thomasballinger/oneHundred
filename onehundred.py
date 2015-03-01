import sys

import numpy
import pygame

from pygame.locals import *

# board size
SQUARE_SIZE = 30
BOARD_SIZE = 10
GAP = 2
MARGINX = 50
TOP_MARGIN = 100
BOTTOM_MARGIN = 30
WINWIDTH = SQUARE_SIZE * BOARD_SIZE + MARGINX * 2 + GAP * (BOARD_SIZE + 2)
WINHEIGHT = SQUARE_SIZE * BOARD_SIZE + TOP_MARGIN + GAP * (BOARD_SIZE + 2) + BOTTOM_MARGIN

# colors
BACKGROUND = (255, 165, 0)  # orange
GREEN = (0, 255, 0)
DGREEN = (50, 205, 50)  # lime green
PURPLE = (153, 50, 204)  # dark orchid
RED = (255, 0, 0)
FILLED = (64, 224, 208)  # turquoise
EMPTY = (192, 192, 192)  # light grey
WHITE = (248, 248, 255)
BLACK = (0, 0, 0)
TEXTCOLOR = BLACK

cols = [
    [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK],
    [BLACK, WHITE, WHITE, WHITE, WHITE, WHITE, WHITE, WHITE, WHITE, BLACK],
    [BLACK, WHITE, DGREEN, BLACK, DGREEN, BLACK, DGREEN, BLACK, WHITE, BLACK],
    [BLACK, WHITE, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, WHITE, BLACK],
    [BLACK, WHITE, WHITE, WHITE, WHITE, WHITE, WHITE, WHITE, WHITE, BLACK],
    [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK],
    [WHITE, WHITE, WHITE, BLACK, BLACK, BLACK, BLACK, WHITE, WHITE, WHITE],
    [WHITE, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, WHITE],
    [BLACK, WHITE, BLACK, WHITE, BLACK, WHITE, BLACK, WHITE, BLACK, BLACK],
    [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK]]

FPS = 60


def main():
    global WIN, FPSCLOCK

    pygame.init()

    FONT = pygame.font.Font('freesansbold.ttf', 20)

    WIN = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    FPSCLOCK = pygame.time.Clock()

    pygame.display.set_caption('100')

    board = init_board(BOARD_SIZE)

    mousex = None
    mousey = None

    score = 0

    while True:
        WIN.fill(BACKGROUND)
        draw_board(board)

        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouse_clicked = True
            elif event.type == KEYDOWN and event.key == K_RETURN:
                if len(next_possible_moves(board)) == 0:
                    score = 0
                    board = init_board(BOARD_SIZE)
                    draw_board(board)
                    boxx, boxy = None, None

        boxx, boxy = get_box_at_pixel(board, mousex, mousey)

        if boxx is not None and boxy is not None:

            if score == 0:
                if mouse_clicked:
                    score += 1
                    board[boxx, boxy] = score

            if score != 0 and board[boxx, boxy] == 0:
                lastx, lasty = which(board, score)
                if (boxx, boxy) in next_possible_moves(board):
                    draw_highlighted_box(boxx, boxy, GREEN)
                    if mouse_clicked:
                        score += 1
                        board[boxx, boxy] = score
                else:
                    draw_highlighted_box(boxx, boxy, RED)

        if len(next_possible_moves(board)) == 0:
            if score < 100:
                end_of_game = FONT.render('Game over, your score is ' + str(score), True, TEXTCOLOR)
            else:
                end_of_game = FONT.render('You won', True, TEXTCOLOR)

            WIN.blit(end_of_game, (MARGINX, 30))
            WIN.blit(FONT.render('Press Enter to start again', True, TEXTCOLOR), (MARGINX, 60))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


# functions

def spots(m):
    """Generates pairs of locations and contents of numpy array m"""
    for i in xrange(m.shape[0]):
        for j in xrange(m.shape[1]):
            yield (i, j), m[i, j]


def which(m, val):
    """Returns first (i, j) index at where val is found

    m is a matrix
    val is a value
    """
    for (i, j), contents in spots(m):
        if contents == val:
            return (i, j)
    return (None, None)


def init_board(dim):
    """initialize board"""
    return numpy.zeros(shape=(dim, dim), dtype=numpy.int)


def draw_board(board):
    """draws board"""
    for (i, j), contents in spots(board):
        col = EMPTY if contents == 0 else contents
        left, top = left_top_coords_of_box(i, j)
        pygame.draw.rect(WIN, col, (left, top, SQUARE_SIZE, SQUARE_SIZE))
        pygame.draw.rect(WIN, BLACK, (left, top, SQUARE_SIZE, SQUARE_SIZE), 1)
    if numpy.amax(board) > 0:
        boxx, boxy = which(board, numpy.amax(board))
        left, top = left_top_coords_of_box(boxx, boxy)
        pygame.draw.rect(WIN, GREEN, (left, top, SQUARE_SIZE, SQUARE_SIZE), 1)


def left_top_coords_of_box(boxx, boxy):
    """Returns pixel coordinates given board coordinates"""
    left = MARGINX + (boxx + 1) * GAP + boxx * SQUARE_SIZE  # boxx * (SQUARE_SIZE + GAP) + MARGINX + GAP
    top = TOP_MARGIN + (boxy + 1) * GAP + boxy * SQUARE_SIZE  # boxy * (SQUARE_SIZE + GAP) + TOP_MARGIN + GAP
    return(left, top)


def get_box_at_pixel(board, x, y):
    """Returns board coordinates given pixel coordinates"""
    rects = (((i, j), pygame.Rect(*left_top_coords_of_box(i, j) +
                                  (SQUARE_SIZE, SQUARE_SIZE)))
             for i in xrange(BOARD_SIZE)
             for j in xrange(BOARD_SIZE))
    for (boxx, boxy), box_rect in rects:
        if box_rect.collidepoint(x, y):
            return(boxx, boxy)
    return(None, None)


def draw_highlighted_box(boxx, boxy, col):
    left, top = left_top_coords_of_box(boxx, boxy)
    pygame.draw.rect(WIN, col, (left, top, SQUARE_SIZE, SQUARE_SIZE), 5)


def manhattan_dist(box1, box2):
    """Returns manhattan distance between two boxes on the board

    box1, box2 are tuples of (x, y) coordinates"""
    return abs(box1[0]-box2[0]) + abs(box1[1]-box2[1])


def next_possible_moves(board):
    boxx, boxy = which(board, numpy.amax(board))
    deltas = [(3, 0), (0, 3), (-3, 0), (0, -3),
              (-2, 2), (2, 2), (2, -2), (-2, -2)]
    return [(x, y) for x, y in [(boxx+dx, boxy+dy) for dx, dy in deltas]
            if x in xrange(BOARD_SIZE) and y in xrange(BOARD_SIZE) and
            board[x, y] == 0]


if __name__ == '__main__':
    main()
