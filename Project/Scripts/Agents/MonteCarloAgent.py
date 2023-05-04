#region typing dependencies
from typing import TYPE_CHECKING, Any, Optional, Type, TypeVar

import Utils.SharedCoreTypes as SCT

from numpy.typing import NDArray
from Environments.BaseEnv import BaseEnv
if TYPE_CHECKING:
	pass
# endregion

# other file dependencies
import Agents.BaseAgent as BaseAgent
import numpy as np


class MonteCarloAgent(BaseAgent.BaseAgent):

	def __init__(self, env:BaseEnv, envConfig:SCT.Config, mode:BaseAgent.AgentMode=BaseAgent.AgentMode.Train):
		super().__init__(env, envConfig, mode=mode)

		self._SubAgent = BaseAgent.GetAgent(self.Config["SubAgent"])(self.Env, envConfig, mode=mode)

		return

	def GetAction(self, state:SCT.State) -> SCT.Action:
		super().GetAction(state)
		actionValues = self.GetActionValues(state)
		return self._GetMaxValues(actionValues)

	def GetActionValues(self, state:SCT.State) -> NDArray[np.float32]:
		super().GetActionValues(state)

		return self._SearchActions(self.Env, state)

	def _SearchActions(self, env:BaseEnv, state:SCT.State, depth:int=0) -> NDArray[np.float32]:

		actionValues = self._SubAgent.GetActionValues(state)
		dicountFactor:float = self.Config["DiscountFactor"]

		if depth >= self.Config["MaxDepth"]:
			return actionValues * dicountFactor

		actionPrioList = np.argsort(actionValues)[::-1]

		for i in range(self.Config["TopActionCount"]):
			action = actionPrioList[i]

			# predict with markov model
			nextState, reward, terminated, truncated = self.DataManager._MarkovModel.Predict(state, action)

			# if not in markov model, simulate
			if terminated is None:

				envCopy = env.Clone()
				nextState, reward, terminated, truncated = envCopy.Step(action)

				actionValues[action] = reward

				if not (terminated or truncated):
					actionValues[action] += np.max(self._SearchActions(envCopy, nextState, depth=depth + 1))

				del envCopy

			else:
				actionValues[action] = reward

				if not terminated:
					actionValues[action] += np.max(self._SearchActions(env, nextState, depth=depth + 1))


		return actionValues * dicountFactor




	def Reset(self) -> None:
		super().Reset()
		self._SubAgent.Reset()
		return

	def Remember(self,
			state:SCT.State,
			action:SCT.Action,
			reward:SCT.Reward,
			nextState:SCT.State,
			terminated:bool,
			truncated:bool) -> None:

		super().Remember(state, action, reward, nextState, terminated, truncated)
		self._SubAgent.Remember(state, action, reward, nextState, terminated, truncated)
		return

	def Save(self, path:str) -> None:
		super().Save(path)
		self._SubAgent.Save(path)
		return

	def Load(self, path:str) -> None:
		super().Load(path)
		self._SubAgent.Load(path)
		return