import enum
import os
import json
from Utils.PathHelper import GetRootPath


class AgentMode(enum.Enum):
	Train = 0
	Play = 1


AgentList = ["Random", "DQN", "Human", "MonteCarlo", "Exploration"]
def GetAgent(agentName):


	if agentName == "Random":
		from . import RandomAgent
		return RandomAgent.RandomAgent
	elif agentName == "DQN":
		from . import DQNAgent
		return DQNAgent.DQNAgent
	elif agentName == "Human":
		from . import HumanAgent
		return HumanAgent.HumanAgent
	elif agentName == "MonteCarlo":
		from . import MonteCarloAgent
		return MonteCarloAgent.MonteCarloAgent
	elif agentName == "Exploration":
		from . import ExplorationAgent
		return ExplorationAgent.ExplorationAgent

	raise Exception(f"Agent \"{agentName}\" not found")
	return





class BaseAgent:
	def __init__(self, env, envConfig, mode=AgentMode.Train):
		self.Env = env
		self.Mode = mode
		self.Name = self.__class__.__name__.replace("Agent", "")

		self.LoadConfig(envConfig)

		self.FrameNum = 0
		self.TotalFrameNum = 0
		self.TotalRememberedFrame = 0
		self.EpisodeNum = 0
		return

	def LoadConfig(self, envConfig):
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

	def Reset(self):
		self.FrameNum = 0
		self.EpisodeNum += 1
		return

	def Remember(self, state, action, reward, nextState, terminated, truncated):
		self.TotalRememberedFrame += 1
		return


	def GetAction(self, state):
		self.FrameNum += 1
		self.TotalFrameNum += 1

		actionValues = self.GetActionValues(state)
		if actionValues is not None:
			return actionValues.argmax()

		return None

	def GetActionValues(self, state):
		return None

	def Save(self, path):
		return

	def Load(self, path):
		return
