from game import FlappyBirdAI
from model import Linear_QNet, QTrainer
import torch
import numpy as np
import argparse

def get_state(game):
    
    state = [
            game.pipe_list[-1][0].topleft[0] - game.bird_rect.centerx, game.pipe_list[-1][0].topright[0] - game.bird_rect.centerx,
            game.bird_rect.centery - game.pipe_list[-1][1].midbottom[1],
            game.pipe_list[-1][0].midtop[1] - game.bird_rect.centery
        ]

    return np.array(state, dtype=int)

parser = argparse.ArgumentParser() 
parser.add_argument('-m','--model', type=str, default='model/model.pt')

args = parser.parse_args()

model = Linear_QNet(4, 256, 2)

model.load_state_dict(torch.load(args.model))

game = FlappyBirdAI()

start = False

while True:
    if start == False:
        game.screen.blit(game.background, (0, 0))  
        game.screen.blit(game.message, game.game_over_rect)  
        start = game.check_key()
        game.update()
        
    else:
        state_old = get_state(game)

        final_move = [0, 0]
        state0 = torch.tensor(state_old, dtype=torch.float)
        prediction = model(state0)
        move = torch.argmax(prediction).item()
        final_move[move] = 1

        reward, done, score = game.play_step(final_move)

        if done:
            game.reset()
            start = False