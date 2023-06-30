from game import FlappyBirdAI
from model import Linear_QNet, QTrainer
import torch
import numpy as np
import argparse

class Test:
    def __init__(self):
        self.model = Linear_QNet(4, 256, 2)
        self.model.load_state_dict(torch.load(args.model))
        self.game = FlappyBirdAI()

    def get_state(self, game):
    
        state = [
                game.pipe_list[-1][0].topleft[0] - game.bird_rect.centerx, game.pipe_list[-1][0].topright[0] - game.bird_rect.centerx,
                game.bird_rect.centery - game.pipe_list[-1][1].midbottom[1],
                game.pipe_list[-1][0].midtop[1] - game.bird_rect.centery
            ]
        return np.array(state, dtype=int)


if __name__ == "__main__":

    parser = argparse.ArgumentParser() 
    parser.add_argument('-m','--model', type=str, default='model/model.pt')

    args = parser.parse_args()

    test = Test()
    start = False

    while True:
        if start == False:
            test.game.screen.blit(test.game.background, (0, 0))  
            test.game.screen.blit(test.game.message, test.game.game_over_rect)  
            start = test.game.check_key()
            test.game.update()
            
        else:
            state_old = test.get_state(test.game)

            final_move = [0, 0]
            state0 = torch.tensor(state_old, dtype=torch.float)
            prediction = test.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

            reward, done, score = test.game.play_step(final_move)

            if done:
                test.game.reset()
                start = False
