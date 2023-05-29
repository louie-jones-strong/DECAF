import enum
import json
import os
import random

import numpy as np
import src.DataManager.DataManager as DataManager
import src.Utils.Metrics.Logger as Logger
import src.Utils.SharedCoreTypes as SCT
from numpy.typing import NDArray
from src.Utils.PathHelper import GetRootPath
import src.Agents.ForwardModel as ForwardModel


class AgentMode(enum.Enum):
	Play = 0
	Train = 1
	Eval = 2


AgentList = ["Random", "DQN", "Human", "MonteCarlo", "Exploration"]
def GetAgent(agentName:str, envConfig:SCT.Config, mode:AgentMode, forwardModel:ForwardModel.ForwardModel) -> object:


	if agentName == "Random":
		from . import RandomAgent
		return RandomAgent.RandomAgent(envConfig, mode)

	elif agentName == "DQN":
		from . import DQNAgent
		return DQNAgent.DQNAgent(envConfig, mode)

	elif agentName == "Human":
		from . import HumanAgent
		return HumanAgent.HumanAgent(envConfig, mode)

	elif agentName == "MonteCarlo":
		from . import MonteCarloAgent
		return MonteCarloAgent.MonteCarloAgent(envConfig, mode, forwardModel)

	elif agentName == "Exploration":
		from . import ExplorationAgent
		return ExplorationAgent.ExplorationAgent(envConfig, mode)


	raise Exception(f"Agent \"{agentName}\" not found")





class BaseAgent:
	def __init__(self, envConfig:SCT.Config, mode:AgentMode):

		self.Mode = mode
		self.Name = self.__class__.__name__.replace("Agent", "")

		self.LoadConfig(envConfig)

		self.DataManager = DataManager.DataManager()
		self._Logger = Logger.Logger()

		self.StepNum = 0
		self.TotalStepNum = 0
		self.TotalRememberedStep = 0
		self.EpisodeNum = 0
		return

	def LoadConfig(self, envConfig:SCT.Config) -> None:
		self.Config = {}

		path = os.path.join(GetRootPath(), "Config", f"AgentConfig_{self.Name}.json")
		if os.path.exists(path):
			with open(path, "r") as f:
				self.Config = json.load(f)

		self.EnvConfig = envConfig.get("AgentConfig", {}).get(self.Name, None)

		print(f"""
Agent {self.Name}
Config: {self.Config}
EnvConfig: {self.EnvConfig}
""")
		return

	def Reset(self) -> None:
		self.StepNum = 0
		self.EpisodeNum += 1


		if self.Mode == AgentMode.Eval:
			self.Mode = AgentMode.Train
		elif self.Mode == AgentMode.Train:

			episodesBetweenEval = self.Config.get("EpisodesBetweenEval", -1)
			if episodesBetweenEval > 0 and self.EpisodeNum % episodesBetweenEval == 0:
				self.Mode = AgentMode.Eval
		return

	def Remember(self,
			state:SCT.State,
			action:SCT.Action,
			reward:SCT.Reward,
			nextState:SCT.State,
			terminated:bool,
			truncated:bool) -> None:

		self.TotalRememberedStep += 1
		return


	def GetAction(self, state:SCT.State) -> SCT.Action:
		self.StepNum += 1
		self.TotalStepNum += 1

		return 0

	def GetActionValues(self, state:SCT.State) -> NDArray[np.float32]:
		shape = SCT.JoinTuples(self.DataManager.ActionSpace.shape, None)
		return np.ones(shape, dtype=np.float32)

	def _GetMaxValues(self, values:NDArray[np.float32]) -> int:
		maxValue = np.max(values)
		maxValues = np.where(values == maxValue)[0]
		choice = random.choice(maxValues)
		return int(choice)


	def Save(self, path:str) -> None:
		return

	def Load(self, path:str) -> None:
		return
