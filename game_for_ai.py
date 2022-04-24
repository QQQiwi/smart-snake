from game import *
import numpy as np


class SnakeAI(Snake):
    def move(self, action):
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.state)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # right turn r -> d -> l -> u
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # left turn r -> u -> l -> d

        self.state = new_dir

        x = self.head.x
        y = self.head.y
        if self.state == Direction.RIGHT:
            x += GameParameters.BLOCK_SIZE.value
        elif self.state == Direction.LEFT:
            x -= GameParameters.BLOCK_SIZE.value
        elif self.state == Direction.DOWN:
            y += GameParameters.BLOCK_SIZE.value
        elif self.state == Direction.UP:
            y -= GameParameters.BLOCK_SIZE.value

        self.head = Point(x, y)

    def is_dead(self, point=None):
        block_size = GameParameters.BLOCK_SIZE.value

        if point is None:
            point = self.head

        if point.x > GameParameters.SCREEN_WIDTH.value - block_size \
                or point.y > GameParameters.SCREEN_HEIGHT.value - block_size or point.y < 0 or point.x < 0:
            return True

        if point in self.body[1:]:
            return True

        return False


class SnakeGameAI(SnakeGame):
    frame_iteration = 0

    def __init__(self):
        super().__init__()
        self.snake = SnakeAI()
        self.frame_iteration = 0

    def game_iteration(self, action):
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self.snake.move(action)
        self.snake.body.insert(0, self.snake.head)

        reward = 0
        game_over = False
        if self.snake.is_dead() or self.frame_iteration > 100 * len(self.snake.body):
            game_over = True
            reward = -10
            return reward, game_over, self.snake.length

        if self.snake.head == self.food_position:
            self.snake.length += 1
            reward = 10
            self.place_food()
        else:
            self.snake.body.pop()

        self.update_window()
        self.game_clock.tick(GameParameters.SPEED.value)
        return reward, game_over, self.snake.length
