from ai_traineree.agents.ppo import PPOAgent as Agent
from ai_traineree.tasks import GymTask
from ai_traineree.types import TaskType
from examples import interact_episode, run_env

import numpy as np
import pylab as plt
import gym


env_name = 'LunarLanderContinuous-v2'
env = gym.make(env_name)

task: TaskType = GymTask(env, env_name)
config = {
    'rollout_length': 30,
    'batch_size': 30,
    "optimization_epochs": 1,
    "ppo_ratio_clip": 0.2,
    "value_loss_weight": 2,
    "entropy_weight": 0.0005,
    "gamma": 0.98,
    "action_scale": 2,
    "max_grad_norm_actor": 2.0,
    "max_grad_norm_critic": 2.0,
    "critic_lr": 1e-3,
    "actor_lr": 1e-3,
}
agent = Agent(task.state_size, task.action_size, hidden_layers=(300, 300), config=config)

interact_episode(task, agent, 0, render=True)
scores = run_env(task, agent, 80, 4000)
agent.save_state(f"{env_name}_{agent.name}")
interact_episode(task, agent, 0, render=True)

# plot the scores
fig = plt.figure()
ax = fig.add_subplot(111)
plt.plot(np.arange(len(scores)), scores)
plt.ylabel('Score')
plt.xlabel('Episode #')
plt.savefig(f'{env_name}.png', dpi=120)
plt.show()