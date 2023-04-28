import enum
import os
import json
from Utils.PathHelper import GetRootPath


class AgentMode(enum.Enum):
	Train = 0
	Play = 1



def GetAgent(agentName):
	from . import RandomAgent, DQNAgent, HumanAgent, MonteCarloAgent
	lookUp = {
		"Random": RandomAgent.RandomAgent,
		"DQN": DQNAgent.DQNAgent,
		"Human": HumanAgent.HumanAgent,
		"MonteCarlo": MonteCarloAgent.MonteCarloAgent,
	}

	if agentName not in lookUp:
		raise Exception(f"Agent \"{agentName}\" not found in {lookUp}")
		return None

	return lookUp[agentName]




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

	def Remember(self, state, action, reward, nextState, done):
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