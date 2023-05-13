import os
import typing
from collections import deque
from typing import Optional

import numpy as np
import src.DataManager.DataColumnTypes as DCT
import src.DataManager.MarkovModel as MarkovModel
import src.DataManager.ReplayBuffer as ReplayBuffer
import src.Utils.SharedCoreTypes as SCT
import src.Utils.Singleton as Singleton
from src.Environments.BaseEnv import BaseEnv
from numpy.typing import NDArray


class DataManager(Singleton.Singleton):

	def Setup(self, config:SCT.Config, env:BaseEnv) -> None:
		self.LoadConfig(config)
		self._Env = env

		# transition accumulator
		stateTupleType = typing.Tuple[SCT.State, SCT.Action, SCT.Reward, SCT.State, bool, bool]
		self._TransitionAccumulator: typing.Deque[stateTupleType] = deque()
		self._QValueAccumulator:SCT.Reward = 0

		self._ReplayBuffer = ReplayBuffer.ReplayBuffer(self._Config["ReplayBufferMaxSize"], self._Env)
		self._MarkovModel = MarkovModel.MarkovModel(int(self._Env.ActionSpace.n))

		return

	def LoadConfig(self, config:SCT.Config) -> None:
		self._Config = config

		self._Config["ReplayBufferMaxSize"] = 100000
		self._Config["TransitionAccumulatorSize"] = 1000
		self._Config["QFuncGamma"] = 0.99

		return

	def Save(self, path:str) -> None:
		self._EmptyAccumulator()

		self._ReplayBuffer.Save(os.path.join(path, "ReplayBuffer"))
		self._MarkovModel.Save(os.path.join(path, "MarkovModel"))
		return

	def Load(self, path:str) -> None:
		self._ReplayBuffer.Load(os.path.join(path, "ReplayBuffer"))
		self._MarkovModel.Load(os.path.join(path, "MarkovModel"))
		return




# region Calls from Env Runner

	def EnvRemember(self,
			state:SCT.State,
			action:SCT.Action,
			reward:SCT.Reward,
			nextState:SCT.State,
			terminated:bool,
			truncated:bool) -> None:

		# self._MarkovModel.Remember(state, action, reward, nextState, terminated, truncated)

		# add transition to the transition accumulator
		transition = (state, action, reward, nextState, terminated, truncated)
		self._QValueAccumulator += reward * (self._Config["QFuncGamma"] ** len(self._TransitionAccumulator))
		self._TransitionAccumulator.append(transition)


		# if transition accumulator is full, remove the oldest
		# transition and add it to the replay buffer
		if len(self._TransitionAccumulator) > self._Config["TransitionAccumulatorSize"]:
			self._PopAccumulator()

		assert len(self._TransitionAccumulator) <= self._Config["TransitionAccumulatorSize"], \
			f"Transition accumulator has size of: {len(self._TransitionAccumulator)}"

		return

	def EnvReset(self) -> None:

		# empty transition accumulator into the replay buffer
		self._EmptyAccumulator()
		return

# endregion

	def _EmptyAccumulator(self) -> None:
		while len(self._TransitionAccumulator) > 0:
			self._PopAccumulator()


		epsilon = 0.1 ** 9
		assert len(self._TransitionAccumulator) == 0, \
			f"Transition accumulator not empty, has size of: {len(self._TransitionAccumulator)}"

		assert abs(self._QValueAccumulator) <= epsilon, \
			f"Q value accumulator not empty, has value of: {self._QValueAccumulator}, {epsilon}"

		self._QValueAccumulator = 0
		return

	def _PopAccumulator(self) -> None:
		oldest = self._TransitionAccumulator.popleft()

		# unpack transition
		state, action, reward, nextState, terminated, truncated = oldest
		qValue = self._QValueAccumulator

		# self._MarkovModel.OnEmptyTransAcc(state, action, reward, nextState, terminated, truncated, qValue)

		# add to the replay buffer
		self._ReplayBuffer.Add(state, action, reward, nextState, terminated, truncated, futureReward=qValue)

		# update the q value accumulator
		self._QValueAccumulator -= reward
		self._QValueAccumulator *= (1/self._Config["QFuncGamma"])
		return





# region data sampling

	def GetColumns(self, columns:typing.List[DCT.DataColumnTypes]) -> typing.List[NDArray]:
		columnsData = self._ReplayBuffer.SampleAll()

		columnsData = DCT.FilterColumns(columns, columnsData)
		return columnsData

	def _JoinColumnsData(self, columnsData):

		output = []
		for i in range(len(columnsData[0])):
			joinedRow = [columnsData[j][i] for j in range(len(columnsData))]
			output.append(np.array(joinedRow))

		output = np.array(output)
		return output

	def GetXYData(self,
			xColumns:typing.List[DCT.DataColumnTypes],
			yColumns:typing.List[DCT.DataColumnTypes]
			) -> typing.Tuple[typing.List[NDArray], typing.List[NDArray]]:

		joinedColumns = xColumns + yColumns
		joinedColumnsData = self.GetColumns(joinedColumns)

		xColumnsData = joinedColumnsData[:len(xColumns)]
		yColumnsData = joinedColumnsData[len(xColumns):]

		# # join x columns
		# if len(xColumnsData) > 1:
		# 	xColumnsData = self._JoinColumnsData(xColumnsData)
		# else:
		# 	xColumnsData = xColumnsData[0]

		# if len(yColumnsData) > 1:
		# 	yColumnsData = self._JoinColumnsData(yColumnsData)
		# else:
		# 	yColumnsData = yColumnsData[0]

		return xColumnsData, yColumnsData




	def GetSampleIndexs(self, batchSize:int,
			priorityKey:Optional[str] = None,
			priorityScale:float = 1.0) -> typing.Tuple[NDArray[np.int_], NDArray[np.float32]]:

		return self._ReplayBuffer.GetSampleIndexs(batchSize, priorityKey, priorityScale)

	def SampleArrays(self,
			arrays,
			batchSize:int,
			priorityKey:Optional[str] = None,
			priorityScale:float = 1.0):

		indexs, priorities = self.GetSampleIndexs(batchSize, priorityKey, priorityScale)

		sampledArrays = []
		for array in arrays:
			sampledArrays.append(array[indexs])

		return indexs, priorities, sampledArrays


# endregion