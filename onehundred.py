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
                 name, square_size, board_size, gap, marginx, top_margin,
                 bottom_margin):
        """Grid display with Pygame, with customizable behavior via callabacks

        - on_box_click(x, y) is called when the user clicks a box
        - on_box_hover(x, y) is called when the user hovers over a box,
          and should return the color to highlight the box or None
        - on_return() is called when the user hits return
        """
        self.on_box_click = on_box_click
        self.on_box_hover = on_box_hover
        self.on_return = on_return

        self.background = background
        self.name = name

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
        pygame.display.set_caption(self.name)

    def render(self, board, msg=''):
        """Update display with background image color or EMPTY

        board is a numpy array of ints.
        Each grid square will be painted EMPTY if board value is 0,
        else painted with self.background"""
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

        if msg:
            self.message(msg)

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
        for (i, j), turn in spots(board):
            color = EMPTY if turn == 0 else self.background[i][j]
            left, top = self.left_top_coords_of_box(i, j)
            pygame.draw.rect(self.win, color, (left, top, self.square_size, self.square_size))
            pygame.draw.rect(self.win, BLACK, (left, top, self.square_size, self.square_size), 1)
        if numpy.amax(board) > 0:
            boxx, boxy = which(board, numpy.amax(board))
            left, top = self.left_top_coords_of_box(boxx, boxy)
            pygame.draw.rect(self.win, GREEN, (left, top, self.square_size, self.square_size), 1)

    def message(self, msg):
        """Displays up to three lines of text"""
        for i, line in enumerate(msg.split('\n')):
            text = self.font.render(line, True, TEXTCOLOR)
            self.win.blit(text, (self.marginx, (i + 1) * 30))


class Game(object):
    def __init__(self, board_size):
        self.board_size = board_size
        self.reset()

    def reset(self):
        self.score = 0
        self.board = init_board(self.board_size)

    def try_make_move(self, boxx, boxy):
        """Try to select a box as a move"""
        try:
            self.make_move(boxx, boxy)
        except ValueError:
            pass

    def make_move(self, boxx, boxy):
        """Make a move, or raise ValueError if move is illegal"""
        if self.board[boxx, boxy] != 0:
            raise ValueError("Illegal move")
        if self.score == 0:
            self.score += 1
            self.board[boxx, boxy] = self.score
        elif self.board[boxx, boxy] == 0:
            lastx, lasty = which(self.board, self.score)
            if (boxx, boxy) in self.next_possible_moves():
                self.score += 1
                self.board[boxx, boxy] = self.score

    def is_valid(self, boxx, boxy):
        """Returns True if this move would be valid"""
        if self.score == 0:
            return True
        lastx, lasty = which(self.board, self.score)
        if self.board[boxx, boxy] != 0:
            return False
        if (boxx, boxy) in self.next_possible_moves():
            return True
        else:
            return False

    def is_full(self, boxx, boxy):
        """Returns True if this box is open"""
        if self.board[boxx, boxy] != 0:
            return False

    def next_possible_moves(self):
        boxx, boxy = which(self.board, numpy.amax(self.board))
        deltas = [(3, 0), (0, 3), (-3, 0), (0, -3),
                  (-2, 2), (2, 2), (2, -2), (-2, -2)]
        return [(x, y) for x, y in [(boxx+dx, boxy+dy) for dx, dy in deltas]
                if x in xrange(self.board.shape[0]) and y in xrange(self.board.shape[1]) and
                self.board[x, y] == 0]

    def won(self):
        return self.score == 100

    def lost(self):
        return len(self.next_possible_moves()) == 0 and not self.won()

    def __str__(self):
        return str(self.board)


def main():
    board_size = 10
    game = Game(board_size)

    def box_color(boxx, boxy):
        """Returns the highlight color of a box, or None if not highlighted"""
        if game.is_full(boxx, boxy):
            return None
        return GREEN if game.is_valid(boxx, boxy) else RED

    def reset_if_game_over():
        """If there are no possible moves, reset the game"""
        if game.won() or game.lost():
            game.reset()

    display = Display(on_box_click=game.try_make_move,
                      on_box_hover=box_color,
                      on_return=reset_if_game_over,
                      background=HACKERSCHOOL,
                      name='100',
                      square_size=30,
                      board_size=board_size,
                      gap=2,
                      marginx=10,
                      top_margin=100,
                      bottom_margin=30)

    start_again = '\nPress Enter to start again'
    while True:
        if game.lost():
            msg = 'Game over, your score is ' + str(game.score) + start_again
        elif game.won():
            msg = 'You won' + start_again
        else:
            msg = ''
        display.render(game.board, msg)

        display.fps_clock.tick(FPS)


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


def game_with_move(game, x, y):
    g = Game(game.board_size)
    g.score = game.score
    g.board = game.board.copy()
    g.make_move(x, y)
    return g


def solve(game):
    """Returns a list of moves which would win, or None if impossible"""
    if game.won():
        return []
    moves = game.next_possible_moves()
    import random
    random.shuffle(moves)
    for move in moves:
        print game, game.score, move
        result = solve(game_with_move(game, *move))
        if result is not None:
            return [move] + result
    return None


if __name__ == '__main__':
    print solve(Game(10))
    main()
