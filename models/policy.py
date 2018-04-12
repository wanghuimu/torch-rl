import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable

class Policy(nn.Module):
    def __init__(self, obs_space, action_space, activation='tanh'):
        super().__init__()

        if activation == 'tanh':
            self.activation = F.tanh
        elif activation == 'relu':
            self.activation = F.relu
        elif activation == 'sigmoid':
            self.activation = F.sigmoid

        self.fc1 = nn.Linear(obs_space.shape[1], 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, action_space.n)

    def forward(self, x):
        x = self.fc1(x)
        x = self.activation(x)
        x = self.fc2(x)
        x = self.activation(x)
        x = self.fc3(x)
        return x

    def select_action(self, x):
        raw_dist = self.forward(x)
        dist = F.softmax(raw_dist, dim=1)
        action = dist.multinomial()
        return action.data
    
    def get_loss(self, x, action, advantage):
        raw_dist = self.forward(x)
        log_dist = F.log_softmax(raw_dist, dim=1)
        dist = F.softmax(raw_dist, dim=1)
        entropy = -(log_dist * dist).sum(dim=1).mean()
        action_log_prob = log_dist.gather(1, action)
        action_loss = - (action_log_prob * advantage).mean()
        # print("entropy: {:.5f}".format(entropy.data[0]))
        # print("action loss: {:.5f}".format(action_loss.data[0]))
        return action_loss - 0.01 * entropy