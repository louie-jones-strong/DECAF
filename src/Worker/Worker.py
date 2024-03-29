import src.Worker.Agents.BaseAgent as BaseAgent
import src.Worker.Environments.BaseEnv as BaseEnv
import src.Common.Utils.SharedCoreTypes as SCT
import src.Worker.EnvRunner as EnvRunner
from src.Common.Enums.eAgentType import eAgentType
import src.Common.Utils.Metrics.Metrics as Metrics
import typing
import time
import logging
from src.Common.Utils.Config.ConfigurableClass import ConfigurableClass


class Worker(ConfigurableClass):
	"""
	Worker is responsible for collecting trajectories to fill the experience store.
	"""

	def __init__(self, eAgentType:eAgentType,
			envRunners:typing.List[EnvRunner.EnvRunner],
			isTrainingMode:bool) -> None:
		super().__init__()

		self.IsEvaluating = not isTrainingMode

		self.Envs = envRunners
		self.EpisodeCount = 0
		self.LastReward = 0
		self.TotalRewards = 0
		self.TotalCuratedReward = 0
		self.StartTime = 0.0
		self.TimeTook = 0.0

		self.Agent = BaseAgent.GetAgent(eAgentType, self.EnvConfig, isTrainingMode)

		self._ModelUpdateTime = time.time() + self.EnvConfig["SecsPerModelFetch"]

		self.Metrics = Metrics.Metrics()
		return

	def Run(self) -> None:
		"""
		Runs the worker's main loop.
		collecting observations from the envs and sending them to the agent, to get actions.
		then making the actions in the envs.
		"""
		self.StartTime = time.time()

		for i in range(len(self.Envs)):
			self.Envs[i].Reset()
		self.Agent.Reset()

		# get initial states from the environments
		stateList = [env.GetState() for env in self.Envs]
		envs = [env.Env for env in self.Envs]

		maxEpisodes = self.EnvConfig["MaxEpisodes"]

		# run the environments
		while self.EpisodeCount < maxEpisodes:

			# get actions from the agent
			with self.Metrics.Time("GetActions"):
				actions, actionValues, actionReasons = self._GetActions(stateList, envs)

			# make the chosen actions in the environments
			with self.Metrics.Time("StepEnvs"):
				stateList, envs, finishedEpisodes = self._StepEnvs(actions, actionValues, actionReasons)

			# increment the episode count by the number of episodes that have been completed in this step
			self.EpisodeCount += finishedEpisodes

			if finishedEpisodes > 0:
				avgRewards = self.TotalRewards / self.EpisodeCount
				avgTime = (time.time() - self.StartTime) / self.EpisodeCount

				avgCurated = self.TotalCuratedReward / self.EpisodeCount

				progressStr = f"{self.EpisodeCount} / {maxEpisodes}"
				logging.info(f"{progressStr}  avg:{avgRewards:.3f} avgCurated:{avgCurated:.3f} avgTime:{avgTime:.3f}")

			# If in evaluate mode then we only check for updates after an episode.
			# This is to ensure that the agent is consistent for the whole episode.
			if not self.IsEvaluating or finishedEpisodes > 0:
				self.CheckForUpdates()

		self.TimeTook = time.time() - self.StartTime
		return

	def _GetActions(self,
			stateList:typing.List[SCT.State],
			envs:typing.List[BaseEnv.BaseEnv]) -> \
				typing.Tuple[typing.List[SCT.Action], typing.List[SCT.ActionValues], typing.List[SCT.ActionReason]]:

		actions = []
		actionReasons = []
		actionValues_List = []

		for i in range(len(stateList)):
			with self.Metrics.Time("GetAction"):
				action, actionValues, actionReason = self.Agent.GetAction(stateList[i], envs[i])

			actions.append(action)
			actionReasons.append(actionReason)
			actionValues_List.append(actionValues)

		return actions, actionValues_List, actionReasons

	def _StepEnvs(self,
			actions:typing.List[SCT.Action],
			actionValues:typing.List[SCT.ActionValues],
			actionReasons) -> typing.Tuple[typing.List[SCT.State], typing.List[BaseEnv.BaseEnv], int]:
		"""
		Makes the chosen actions in the environments.

		Args:
			actions: list of actions to make in the environments.

		Returns:
			list of states after the actions have been made.
			count the number of episodes that have been completed, in this step.
		"""

		assert len(actions) == len(self.Envs), \
			f"the number of actions must match the number of envs. {len(actions)} != {len(self.Envs)}"


		stateList = []
		envs = []
		finishedEpisodes = 0
		for i in range(len(self.Envs)):

			state = self.Envs[i].State
			nextState, reward, terminated, truncated = self.Envs[i].Step(actions[i], actionValues[i], actionReasons[i])

			self.Agent.Remember(state, actions[i], reward, nextState, terminated, truncated)


			if terminated or truncated:
				finishedEpisodes += 1
				self.LastReward = self.Envs[i].TotalReward
				self.TotalRewards += self.LastReward

				self.TotalCuratedReward += self.Envs[i].TotalCuratedReward

				self.Envs[i].Reset()
				self.Agent.Reset()


		stateList = [env.GetState() for env in self.Envs]
		envs = [env.Env for env in self.Envs]

		return stateList, envs, finishedEpisodes


	def CheckForUpdates(self) -> None:
		"""
		Checks if the agent needs to update its models.
		This is based on the time since the last update.
		The time between updates is set in the config.
		"""

		if time.time() >= self._ModelUpdateTime:
			self.Agent.UpdateModels()

			self._ModelUpdateTime = time.time() + self.EnvConfig["SecsPerModelFetch"]
		return


	def Clear(self) -> None:
		self.EpisodeCount = 0
		self.LastReward = 0
		self.TotalRewards = 0
		self.TotalCuratedReward = 0
		self.StartTime = 0.0
		self.TimeTook = 0.0
		return