from typing import Any

import numpy as np
import src.Common.Utils.SharedCoreTypes as SCT
from numpy.typing import NDArray
from src.Common.Agents.BaseAgent import BaseAgent


class RandomAgent(BaseAgent):


	def GetAction(self, state:SCT.State) -> Any:
		super().GetAction(state)
		return self.ActionSpace.sample()


	def GetActionValues(self, state:SCT.State) -> NDArray[np.float32]:
		super().GetActionValues(state)

		actions = int(self.ActionSpace.n)
		return np.random.rand(actions).astype(np.float32)