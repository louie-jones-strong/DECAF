import src.Common.Agents.BaseAgent as BaseAgent
import numpy as np
import src.Common.Utils.Metrics.Logger as Logger
import src.Common.Utils.SharedCoreTypes as SCT
from numpy.typing import NDArray
import src.Common.Utils.ConfigHelper as ConfigHelper
from src.Common.Enums.eAgentType import eAgentType
from src.Common.Enums.ePlayMode import ePlayMode
from gymnasium.spaces import Discrete, Box
import typing


class HardCodedAi(BaseAgent.BaseAgent):

	def __init__(self, envConfig:SCT.Config, isTrainingMode:bool):
		super().__init__(envConfig, isTrainingMode)
		return

	def Reset(self) -> None:
		super().Reset()
		return

	def Save(self, path:str) -> None:
		super().Save(path)
		return

	def Load(self, path:str) -> None:
		super().Load(path)
		return



	def Remember(self,
		state:SCT.State,
		action:SCT.Action,
		reward:SCT.Reward,
		nextState:SCT.State,
		terminated:bool,
		truncated:bool) -> None:

		super().Remember(state, action, reward, nextState, terminated, truncated)
		return


	def GetAction(self, state:SCT.State) -> typing.Tuple[SCT.Action, str]:
		super().GetAction(state)

		return 0, "HardCoded"