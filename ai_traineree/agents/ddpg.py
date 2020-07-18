from ai_traineree.agents.utils import hard_update, soft_update
from ai_traineree.buffers import ReplayBuffer
from ai_traineree.networks import ActorBody, CriticBody
from ai_traineree.noise import GaussianNoise
from ai_traineree.types import AgentType

import numpy as np
import torch
from torch.optim import Adam
from torch.nn.functional import mse_loss
from typing import Any, Iterable, Tuple


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class DDPGAgent(AgentType):

    def __init__(self, state_dim: int, action_dim: int, hidden_layers: Iterable[int]=(128, 128),
                 actor_lr: float=2e-3, actor_lr_decay: float=0, critic_lr: float=2e-3, critic_lr_decay: float=0,
                 noise_scale: float=0.2, noise_sigma: float=0.1, clip: Tuple[int, int]=(-1, 1), config={}, device=None):
        super(DDPGAgent, self).__init__()
        self.device = device if device is not None else DEVICE

        # Reason sequence initiation.
        self.actor = ActorBody(state_dim, action_dim, hidden_layers=hidden_layers).to(self.device)
        self.critic = CriticBody(state_dim, action_dim, hidden_layers=hidden_layers).to(self.device)
        self.target_actor = ActorBody(state_dim, action_dim, hidden_layers=hidden_layers).to(self.device)
        self.target_critic = CriticBody(state_dim, action_dim, hidden_layers=hidden_layers).to(self.device)

        # Noise sequence initiation
        self.noise = GaussianNoise(shape=(action_dim,), mu=1e-8, sigma=noise_sigma, scale=noise_scale, device=device)

        # Target sequence initiation
        hard_update(self.target_actor, self.actor)
        hard_update(self.target_critic, self.critic)

        # Optimization sequence initiation.
        self.actor_optimizer = Adam(self.actor.parameters(), lr=actor_lr, weight_decay=actor_lr_decay)
        self.critic_optimizer = Adam(self.critic.parameters(), lr=critic_lr, weight_decay=critic_lr_decay)
        self.action_min = clip[0]
        self.action_max = clip[1]

        self.gamma: float = float(config.get('gamma', 0.99))
        self.tau: float = float(config.get('tau', 0.02))
        self.batch_size: int = int(config.get('batch_size', 64))
        self.buffer_size: int = int(config.get('buffer_size', int(1e6)))
        self.buffer = ReplayBuffer(self.batch_size, self.buffer_size)

        self.warm_up: int = int(config.get('warm_up', 0))
        self.update_every_iterations = 1
        self.number_updates = 1

        # Breath, my child.
        self.reset_agent()
        self.iteration = 0

    def reset_agent(self) -> None:
        self.actor.reset_parameters()
        self.critic.reset_parameters()
        self.target_actor.reset_parameters()
        self.target_critic.reset_parameters()

    def describe_agent(self) -> Tuple[Any, Any, Any, Any]:
        """
        Returns network's weights in order:
        Actor, TargetActor, Critic, TargetCritic
        """
        return (self.actor.state_dict(), self.target_actor.state_dict(), self.critic.state_dict(), self.target_critic())

    def step(self, state, action, reward, next_state, done):
        self.iteration += 1
        self.buffer.add(state, action, reward, next_state, done)

        if self.iteration < self.warm_up:
            return

        if len(self.buffer) > self.batch_size and (self.iteration % self.update_every_iterations) == 0:
            for _ in range(self.number_updates):
                batch = self.buffer.sample()
                self.learn(batch)

    def learn(self, samples):
        """update the critics and actors of all the agents """

        states, actions, rewards, next_states, dones = samples

        # critic loss
        next_actions = self.target_actor(next_states)
        Q_target_next = self.target_critic(next_states, next_actions)
        Q_target = rewards + (self.gamma * Q_target_next * (1 - dones))
        Q_expected = self.critic(states, actions)
        critic_loss = mse_loss(Q_expected, Q_target)

        # Minimize the loss
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        # torch.nn.utils.clip_grad_norm_(self.critic.parameters(), self.gradient_clip)
        self.critic_optimizer.step()
        self.last_loss = critic_loss.item()

        # Compute actor loss
        pred_actions = self.actor(states)
        actor_loss = -self.critic(states, pred_actions).mean()
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()

        soft_update(self.target_actor, self.actor, self.tau)
        soft_update(self.target_critic, self.critic, self.tau)

    def act(self, obs, noise: float=0.0):
        with torch.no_grad():
            obs = torch.tensor(obs.astype(np.float32)).to(self.device)
            action = self.actor(obs)
            action += noise*self.noise.sample()
            return torch.clamp(action, self.action_min, self.action_max).cpu().numpy().astype(np.float32)

    def target_act(self, obs, noise: float=0.0):
        with torch.no_grad():
            obs = torch.tensor(obs).to(self.device)
            action = self.target_actor(obs) + noise*self.noise.sample()
            return torch.clamp(action, self.action_min, self.action_max).cpu().numpy().astype(np.float32)