import typing

import reverb
import src.Common.Agents.BaseAgent as BaseAgent
import src.Common.Environments.BaseEnv as BaseEnv
import src.Common.Utils.ConfigHelper as ConfigHelper
import src.Common.Utils.SharedCoreTypes as SCT
import src.Worker.EnvRunner as EnvRunner
from src.Common.Enums.AgentType import AgentType


class Worker:

	def __init__(self, envConfig:SCT.Config, agentType:AgentType, isTrainingMode:bool) -> None:
		self.Config = envConfig

		self.Agents = []
		self.Agents.append(BaseAgent.GetAgent(agentType, envConfig, isTrainingMode))

		experienceStore = reverb.Client(f'experience-store:{5001}')


		self.Envs = []
		for i in range(self.Config["NumEnvsPerWorker"]):
			env = BaseEnv.GetEnv(self.Config)

			runnner = EnvRunner.EnvRunner(env, self.Config["MaxSteps"], experienceStore)
			self.Envs.append(runnner)


		self.EpisodeCount = 0
		return

	def _GetActions(self, stateList):
		actions = []
		for i in range(len(stateList)):
			action = self.Agents[0].GetAction(stateList[i])
			actions.append(action)
		return actions

	def _StepEnvs(self, actions):

		stateList = []
		for i in range(len(self.Envs)):

			state, done = self.Envs[i].Step(actions[i])
			if done:
				maxEpisodes = self.Config["MaxEpisodes"]
				print(f"{self.EpisodeCount+1} / {maxEpisodes}")
				self.EpisodeCount += 1

			stateList.append(state)

		return stateList


	def Run(self) -> None:

		stateList = [env.GetState() for env in self.Envs]
		while self.EpisodeCount < self.Config["MaxEpisodes"]:

			# get agent action
			actions = self._GetActions(stateList)
			# step the envirements
			self._StepEnvs(actions)
		return