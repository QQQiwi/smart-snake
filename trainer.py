import torch
import random
import numpy as np
from collections import deque
from game_for_ai import SnakeGameAI, Direction, Point, GameParameters
from model import Linear_QNet, QTrainer
from get_stats import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        head = game.snake.body[0]
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)

        dir_l = game.snake.state == Direction.LEFT
        dir_r = game.snake.state == Direction.RIGHT
        dir_u = game.snake.state == Direction.UP
        dir_d = game.snake.state == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game.snake.is_dead(point_r)) or
            (dir_l and game.snake.is_dead(point_l)) or
            (dir_u and game.snake.is_dead(point_u)) or
            (dir_d and game.snake.is_dead(point_d)),

            # Danger right
            (dir_u and game.snake.is_dead(point_r)) or
            (dir_d and game.snake.is_dead(point_l)) or
            (dir_l and game.snake.is_dead(point_u)) or
            (dir_r and game.snake.is_dead(point_d)),

            # Danger left
            (dir_d and game.snake.is_dead(point_r)) or
            (dir_u and game.snake.is_dead(point_l)) or
            (dir_r and game.snake.is_dead(point_u)) or
            (dir_l and game.snake.is_dead(point_d)),

            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Food location
            game.food_position.x < game.snake.head.x,  # food left
            game.food_position.x > game.snake.head.x,  # food right
            game.food_position.y < game.snake.head.y,  # food up
            game.food_position.y > game.snake.head.y  # food down
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))  # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)  # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        # for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()

    load = True
    if load:
        agent.model.load_state_dict(torch.load('model/model_133.pth'))
        # agent.model.eval()

    epoch = 0
    while True:
        epoch += 1
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.game_iteration(final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot result
            game = SnakeGameAI()
            agent.n_games += 1
            agent.train_long_memory()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)

            if score > record:
                record = score
                agent.model.save(f'model_{agent.n_games}.pth')
                plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()
