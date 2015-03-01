import sys

import numpy
import pygame

from pygame.locals import *

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

HACKERSCHOOL = [
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


class Display(object):
    def __init__(self, on_box_click, on_box_hover, on_return, background,
                 square_size, board_size, gap, marginx, top_margin,
                 bottom_margin):
        """

        - on_box_click(x, y) is called when the user clicks a box
        - on_box_hover(x, y) is called when the user hovers over a box,
          and should return the color to highlight the box or None
        - on_return() is called when the user hits return
        """
        self.on_box_click = on_box_click
        self.on_box_hover = on_box_hover
        self.on_return = on_return

        self.background = background

        self.square_size = square_size
        self.board_size = board_size
        self.gap = gap
        self.marginx = marginx
        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        self.current_box = None

        self.setup()

    @property
    def winwidth(self):
        return (self.square_size * self.board_size + self.marginx * 2 +
                self.gap * (self.board_size + 2))

    @property
    def winheight(self):
        return (self.square_size * self.board_size + self.top_margin +
                self.gap * (self.board_size + 2) + self.bottom_margin)

    def setup(self):
        pygame.init()
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.win = pygame.display.set_mode((self.winwidth, self.winheight))
        self.fps_clock = pygame.time.Clock()
        pygame.display.set_caption('100')

    def render(self, board):
        """"""
        self.win.fill(BACKGROUND)
        self.draw_board(board)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
                boxx, boxy = self.get_box_at_pixel(board, mousex, mousey)
                if boxx is not None and boxy is not None:
                    self.current_box = (boxx, boxy)
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                boxx, boxy = self.get_box_at_pixel(board, mousex, mousey)
                if boxx is not None and boxy is not None:
                    self.current_box = (boxx, boxy)
                    self.on_box_click(boxx, boxy)
            elif event.type == KEYDOWN and event.key == K_RETURN:
                self.on_return()

        if self.current_box:
            color = self.on_box_hover(*self.current_box)
            if color:
                self.draw_highlighted_box(*self.current_box + (color,))
        pygame.display.update()

    def get_box_at_pixel(self, board, x, y):
        """Returns board coordinates given pixel coordinates"""
        rects = (((i, j), pygame.Rect(*self.left_top_coords_of_box(i, j) +
                                      (self.square_size, self.square_size)))
                 for i in xrange(self.board_size)
                 for j in xrange(self.board_size))
        for (boxx, boxy), box_rect in rects:
            if box_rect.collidepoint(x, y):
                return(boxx, boxy)
        return(None, None)

    def draw_highlighted_box(self, boxx, boxy, col):
        left, top = self.left_top_coords_of_box(boxx, boxy)
        pygame.draw.rect(self.win, col, (left, top, self.square_size, self.square_size), 5)

    def left_top_coords_of_box(self, boxx, boxy):
        """Returns pixel coordinates given board coordinates"""
        left = self.marginx + (boxx + 1) * self.gap + boxx * self.square_size  # boxx * (SQUARE_SIZE + GAP) + MARGINX + GAP
        top = self.top_margin + (boxy + 1) * self.gap + boxy * self.square_size  # boxy * (SQUARE_SIZE + GAP) + TOP_MARGIN + GAP
        return(left, top)

    def draw_board(self, board):
        """draws board"""
        for (i, j), contents in spots(board):
            color = EMPTY if contents == 0 else self.background[i][j]
            left, top = self.left_top_coords_of_box(i, j)
            pygame.draw.rect(self.win, color, (left, top, self.square_size, self.square_size))
            pygame.draw.rect(self.win, BLACK, (left, top, self.square_size, self.square_size), 1)
        if numpy.amax(board) > 0:
            boxx, boxy = which(board, numpy.amax(board))
            left, top = self.left_top_coords_of_box(boxx, boxy)
            pygame.draw.rect(self.win, GREEN, (left, top, self.square_size, self.square_size), 1)

    def message(self, msg):
        text = FONT.render(msg, True, TEXTCOLOR)
        WIN.blit(text, (MARGINX, 30))


class Game(object):
    def __init__(self, board_size):
        self.board_size = board_size
        self.reset()

    def reset(self):
        self.score = 0
        self.board = init_board(self.board_size)


def main():
    board_size = 10
    game = Game(board_size)

    def on_return():
        if len(next_possible_moves(game.board)) == 0:
            game.reset()
            game.score = 0

    def on_box_click(boxx, boxy):
        if game.score == 0:
            game.score += 1
            game.board[boxx, boxy] = game.score
        elif game.board[boxx, boxy] == 0:
            lastx, lasty = which(game.board, game.score)
            if (boxx, boxy) in next_possible_moves(game.board):
                game.score += 1
                game.board[boxx, boxy] = game.score

    def on_box_hover(boxx, boxy):
        if game.score == 0:
            return GREEN
        lastx, lasty = which(game.board, game.score)
        if game.board[boxx, boxy] != 0:
            return None
        if (boxx, boxy) in next_possible_moves(game.board):
            return GREEN
        else:
            return RED

    display = Display(on_box_click=on_box_click,
                      on_box_hover=on_box_hover,
                      on_return=on_return,
                      background=HACKERSCHOOL,
                      square_size=30,
                      board_size=board_size,
                      gap=2,
                      marginx=10,
                      top_margin=100,
                      bottom_margin=30)

    while True:
        display.render(game.board)

        if len(next_possible_moves(game.board)) == 0:
            if game.score < 100:
                display.message('Game over, your score is ' + str(game.score))
            else:
                display.message('You won')

        display.fps_clock.tick(FPS)


#WIN.blit(FONT.render('Press Enter to start again', True, TEXTCOLOR), (MARGINX, 60))
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


def manhattan_dist(box1, box2):
    """Returns manhattan distance between two boxes on the board

    box1, box2 are tuples of (x, y) coordinates"""
    return abs(box1[0]-box2[0]) + abs(box1[1]-box2[1])


def next_possible_moves(board):
    boxx, boxy = which(board, numpy.amax(board))
    deltas = [(3, 0), (0, 3), (-3, 0), (0, -3),
              (-2, 2), (2, 2), (2, -2), (-2, -2)]
    return [(x, y) for x, y in [(boxx+dx, boxy+dy) for dx, dy in deltas]
            if x in xrange(board.shape[0]) and y in xrange(board.shape[1]) and
            board[x, y] == 0]


if __name__ == '__main__':
    main()
