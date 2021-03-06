import gym
import logging
from typing import Optional

from ai_traineree.env_runner import EnvRunner
from ai_traineree.types import AgentType, Hyperparameters
from ai_traineree.tasks import GymTask


class SageMakerExecutor:

    _logger = logging.getLogger("SageMakerExecutor")

    def __init__(self, env_name, agent_name: str, hyperparameters: Optional[Hyperparameters] = None):
        self._logger.info("Initiating SageMakerExecutor with env_name '%s' and agent '%s'", env_name, agent_name)

        env = gym.make(env_name)
        self.task = GymTask(env, env_name)
        agent = None
        if agent_name.upper() == "DQN":
            from ai_traineree.agents.dqn import DQNAgent
            agent = DQNAgent
        elif agent_name.upper() == "PPO":
            from ai_traineree.agents.ppo import PPOAgent
            agent = PPOAgent
        elif agent_name.upper() == "DDPG":
            from ai_traineree.agents.ddpg import DDPGAgent
            agent = DDPGAgent
        else:
            self._logger.warning("No agent provided. You're given a PPO agent.")
            from ai_traineree.agents.ppo import PPOAgent
            agent = PPOAgent

        self.max_iterations = int(hyperparameters.get("max_iterations", 10000))
        self.max_episodes = int(hyperparameters.get("max_episodes", 1000))
        self.log_every = int(hyperparameters.get("log_every", 10))
        self.score_goal = int(hyperparameters.get("score_goal", 100))

        self.eps_start: float = float(hyperparameters.get('eps_start', 1.0))
        self.eps_end: float = float(hyperparameters.get('eps_end', 0.02))
        self.eps_decay: float = float(hyperparameters.get('eps_decay', 0.995))

        self.agent: AgentType = agent(self.task.state_size, self.task.action_size, config=hyperparameters)

        self.env_runner = EnvRunner(self.task, self.agent, max_iterations=self.max_iterations)

    def run(self) -> None:
        self._logger.info("Running model '%s' for env '%s'", self.agent.name, self.task.name)
        self.env_runner.run(
            reward_goal=self.score_goal, max_episodes=self.max_episodes,
            eps_start=self.eps_start, eps_end=self.eps_end, eps_decay=self.eps_decay,
            log_every=self.log_every,
        )

    def save_results(self, path):
        self._logger.info("Saving the model to path %s", path)
        self.agent.save_state(path)
