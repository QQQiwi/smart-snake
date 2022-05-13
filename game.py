from enum import Enum
import random
import pygame
from collections import namedtuple


DEFAULT_SPEED = 30

Point = namedtuple('Point', 'x, y')
pygame.init()


class Direction(Enum):
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4


class Colors(Enum):
    WHITE = (255, 255, 255)
    RED = (200, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 250, 154)
    # BLACK = (0, 0, 0)
    BLACK = (255, 255, 255)


class GameParameters(Enum):
    BLOCK_SIZE = 20
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720


class Snake:
    def __init__(self):
        self.state = Direction.RIGHT
        self.length = 0
        self.head = Point(GameParameters.SCREEN_WIDTH.value / 2, GameParameters.SCREEN_HEIGHT.value / 2)
        self.body = [self.head,
                     Point(self.head.x - GameParameters.BLOCK_SIZE.value, self.head.y),
                     Point(self.head.x - 2 * GameParameters.BLOCK_SIZE.value, self.head.y)]

    def move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.UP:
            y -= GameParameters.BLOCK_SIZE.value
        elif direction == Direction.DOWN:
            y += GameParameters.BLOCK_SIZE.value
        elif direction == Direction.RIGHT:
            x += GameParameters.BLOCK_SIZE.value
        elif direction == Direction.LEFT:
            x -= GameParameters.BLOCK_SIZE.value
        self.head = Point(x, y)

    def is_dead(self):
        block_size = GameParameters.BLOCK_SIZE.value

        if self.head.x > GameParameters.SCREEN_WIDTH.value - block_size \
                or self.head.y > GameParameters.SCREEN_HEIGHT.value - block_size or self.head.y < 0 or self.head.x < 0:
            return True

        if self.head in self.body[1:]:
            return True

        return False


class SnakeGame:
    def __init__(self):
        pygame.display.set_caption('Snake Game')
        self.screen_width = GameParameters.SCREEN_WIDTH.value
        self.screen_height = GameParameters.SCREEN_HEIGHT.value
        self.game_display = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.game_clock = pygame.time.Clock()
        self.snake = Snake()

        self.food_position = None
        self.place_food()

    def place_food(self):
        block_size = GameParameters.BLOCK_SIZE.value
        x = random.randint(0, (self.screen_width - block_size) // block_size) * block_size
        y = random.randint(0, (self.screen_height - block_size) // block_size) * block_size

        self.food_position = Point(x, y)
        if self.food_position in self.snake.body:
            self.place_food()

    def update_window(self):
        self.game_display.fill(Colors.BLACK.value)
        block_size = GameParameters.BLOCK_SIZE.value

        for body_element in self.snake.body:
            pygame.draw.rect(self.game_display,
                             Colors.BLUE.value,
                             pygame.Rect(body_element.x, body_element.y, block_size, block_size))

            pygame.draw.rect(self.game_display,
                             Colors.GREEN.value,
                             pygame.Rect(body_element.x+4, body_element.y+4, 12, 12))

        pygame.draw.rect(self.game_display,
                         Colors.RED.value,
                         pygame.Rect(self.food_position.x, self.food_position.y, block_size, block_size))

        pygame.display.flip()

    def game_iteration(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.snake.state != Direction.DOWN:
                    self.snake.state = Direction.UP
                elif event.key == pygame.K_DOWN and self.snake.state != Direction.UP:
                    self.snake.state = Direction.DOWN
                elif event.key == pygame.K_LEFT and self.snake.state != Direction.RIGHT:
                    self.snake.state = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.snake.state != Direction.LEFT:
                    self.snake.state = Direction.RIGHT

        self.snake.move(self.snake.state)
        self.snake.body.insert(0, self.snake.head)

        is_game_over = False
        if self.snake.is_dead():
            is_game_over = True
            return is_game_over, self.snake.length

        if self.snake.head == self.food_position:
            self.snake.length += 1
            self.place_food()
        else:
            self.snake.body.pop()

        self.update_window()
        self.game_clock.tick(DEFAULT_SPEED)
        return is_game_over, self.snake.length


if __name__ == '__main__':
    game = SnakeGame()
    while True:
        is_game_end, score = game.game_iteration()
        if is_game_end:
            break

    print('Score: ', score)
    pygame.quit()
