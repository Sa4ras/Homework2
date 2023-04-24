import torch
import torch.nn as nn
import torch.nn.functional as F

from utils.test_env import EnvTest
from core.deep_q_learning_torch import DQN
from q3_schedule import LinearExploration, LinearSchedule
import numpy as np
from configs.q4_linear import config
import logging


class Linear(DQN):
    """
    Implement Fully Connected with Torch
    """

    def initialize_models(self):
        """Creates the 2 separate networks (Q network and Target network). The input
        to these models will be an img_height * img_width image
        with channels = n_channels * self.config.state_history

        1. Set self.q_network to be a linear layer with num_actions as the output size
        2. Set self.target_network to be the same configuration self.q_network but initialized from scratch
        3. What is the input size of the model?

        Hints:
            1. Simply setting self.target_network = self.q_network is incorrect.
            2. Look up nn.Linear
        """
        # this information might be useful
        state_shape = self.env.state_shape()
        img_height, img_width, n_channels = state_shape
        num_actions = self.env.num_actions()

        ##############################################################
        ################ YOUR CODE HERE (3-4 lines) ##################
        num_of_input_features = img_height*img_width*n_channels*self.config.state_history
        self.q_network = nn.Linear(num_of_input_features, num_actions)
        self.target_network = nn.Linear(num_of_input_features, num_actions)
        ##############################################################
        ######################## END YOUR CODE #######################

    def get_q_values(self, state: torch.Tensor, network: str = "q_network"):
        """
        Returns Q values for all actions

        Args:
            state: (torch tensor)
                shape = (batch_size, img height, img width, nchannels x config.state_history)
            network: (str)
                The name of the network we want to use for the forward pass,
                either "q_network" or "target_network".

        Returns:
            out: (torch tensor) of shape = (batch_size, num_actions)

        Hint:
            1. Look up torch.flatten
            2. You can forward a tensor through a network by simply calling it (i.e. network(tensor))
        """
        out = None

        ##############################################################
        ################ YOUR CODE HERE - 3-5 lines ##################
        batch_size = state.shape[0]
        
        out = torch.Tensor([])
        for i in range(batch_size):
            input_tensor = torch.flatten(state[i,:,:,:])
            if network == 'q_network':
                if len(out) == 0:
                    out = self.q_network(input_tensor)
                else:
                    res = self.q_network(input_tensor)
                    out = torch.cat((out, res))            
            else:
                if len(out) == 0:
                    out = self.target_network(input_tensor)
                else:
                    res = self.target_network(input_tensor)
                    out = torch.cat((out, res))
        
        out = torch.reshape(out, shape=[batch_size, self.env.num_actions()])
        ##############################################################
        ######################## END YOUR CODE #######################

        return out

    def update_target(self):
        """
        update_target_op will be called periodically
        to copy Q network weights to target Q network

        Remember that in DQN, we maintain two identical Q networks with
        2 different sets of weights.

        Periodically, we need to update all the weights of the Q network
        and assign them with the values from the regular network.

        Hint:
            1. look up saving and loading pytorch models
        """

        ##############################################################
        ################### YOUR CODE HERE - 1-2 lines ###############
        torch.save(self.q_network,'./temp_model_weights.pt')
        self.target_network = torch.load('./temp_model_weights.pt')

        ##############################################################
        ######################## END YOUR CODE #######################

    def calc_loss(
        self,
        q_values: torch.Tensor,
        target_q_values: torch.Tensor,
        actions: torch.Tensor,
        rewards: torch.Tensor,
        done_mask: torch.Tensor,
    ) -> torch.Tensor:
        """
        Calculate the MSE loss of this step.
        The loss for an example is defined as:
            Q_samp(s) = r if done
                      = r + gamma * max_a' Q_target(s', a') if not done
            loss = (Q_samp(s) - Q(s, a))^2

        Args:
            q_values: (torch tensor) shape = (batch_size, num_actions)
                The Q-values that your current network estimates (i.e. Q(s, a') for all a')
            target_q_values: (torch tensor) shape = (batch_size, num_actions)
                The Target Q-values that your target network estimates (i.e. (i.e. Q_target(s', a') for all a')
            actions: (torch tensor) shape = (batch_size,)
                The actions that you actually took at each step (i.e. a)
            rewards: (torch tensor) shape = (batch_size,)
                The rewards that you actually got at each step (i.e. r)
            done_mask: (torch tensor) shape = (batch_size,)
                A boolean mask of examples where we reached the terminal state

        Hint:
            You may find the following functions useful
                - torch.max
                - torch.sum
                - torch.nn.functional.one_hot
                - torch.nn.functional.mse_loss
                - torch.bitwise_not
        """
        # you may need this variable
        num_actions = self.env.num_actions()
        gamma = self.config.gamma
        max_v = torch.max(target_q_values,dim=1).values
        q_samp = torch.where(done_mask,rewards,rewards+torch.mul(gamma,max_v))
        actions = torch.nn.functional.one_hot(actions.to(torch.int64), num_actions)
        q = torch.sum(torch.multiply(q_values,actions),dim=1)
        
        
        ##############################################################
        ##################### YOUR CODE HERE - 3-5 lines #############
        self.loss = torch.nn.functional.mse_loss(q_samp,q)
        print(self.loss)
        return self.loss
        ##############################################################
        ######################## END YOUR CODE #######################

    def add_optimizer(self):
        """
        Set self.optimizer to be an Adam optimizer optimizing only the self.q_network
        parameters

        Hint:
            - Look up torch.optim.Adam
            - What are the input to the optimizer's constructor?
            - The learning rate will be set following a LinearSchedule
              (implemented in q4), so you don't need to set it here.
        """
        ##############################################################
        #################### YOUR CODE HERE - 1 line #############
        self.optimizer = torch.optim.Adam(self.q_network.parameters())
        ##############################################################
        ######################## END YOUR CODE #######################


if __name__ == "__main__":
    logging.getLogger(
        "matplotlib.font_manager"
    ).disabled = True  # disable font manager warnings
    env = EnvTest((5, 5, 1))

    # exploration strategy
    exp_schedule = LinearExploration(
        env, config.eps_begin, config.eps_end, config.eps_nsteps
    )

    # learning rate schedule
    lr_schedule = LinearSchedule(config.lr_begin, config.lr_end, config.lr_nsteps)

    # train model
    model = Linear(env, config)
    model.run(exp_schedule, lr_schedule, run_idx=1)
