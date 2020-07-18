from ai_traineree.tasks import GymTask
import numpy as np
import pylab as plt
import gym

from ai_traineree.types import TaskType
from ai_traineree.agents.dqn import DQNAgent
from examples import interact_episode, run_env

import matplotlib
matplotlib.use('TkAgg')


env_name = 'LunarLander-v2'
env = gym.make(env_name)

task: TaskType = GymTask(env, env_name)
config = {'batch_size': 64}
agent = DQNAgent(task.state_size, task.action_size)

interact_episode(task, agent, 0, render=True)
scores = run_env(task, agent, 50, 20000, eps_start=1.0, eps_end=0.05, eps_decay=0.9999)
interact_episode(task, agent, 0, render=True)

# plot the scores
fig = plt.figure()
ax = fig.add_subplot(111)
plt.plot(np.arange(len(scores)), scores)
plt.ylabel('Score')
plt.xlabel('Episode #')
plt.savefig(f'{env_name}.png', dpi=120)
plt.show()