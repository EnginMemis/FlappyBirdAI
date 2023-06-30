import torch
import random
import numpy as np
import time
from collections import deque
from game import FlappyBirdAI
from model import Linear_QNet, QTrainer
import argparse

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(4, 256, 2)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        state = [
            game.pipe_list[-1][0].topleft[0] - game.bird_rect.centerx, game.pipe_list[-1][0].topright[0] - game.bird_rect.centerx,
            game.bird_rect.centery - game.pipe_list[-1][1].midbottom[1],
            game.pipe_list[-1][0].midtop[1] - game.bird_rect.centery
        ]
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            samples = random.sample(self.memory, BATCH_SIZE)
        else:
            samples = self.memory
        
        states, actions, rewards, next_states, dones = zip(*samples)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        final_move = [0, 0]
        state0 = torch.tensor(state, dtype=torch.float)
        prediction = self.model(state0)
        move = torch.argmax(prediction).item()
        final_move[move] = 1

        return final_move

def train(model_name):
    record = 0
    agent = Agent()

    if model_name != None:
        agent.model.load_state_dict(torch.load(model_name))

    game = FlappyBirdAI()
    while True:
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        agent.remember(state_old, final_move, reward, state_new, done)

        if done or score == 600:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print("Game:", agent.n_games, "Score:", score, "Record:", record)

if __name__ == "__main__":
    parser = argparse.ArgumentParser() 
    parser.add_argument('-m','--check_point', type=str, default=None)

    args = parser.parse_args()
    
    train(args.check_point)
