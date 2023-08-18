import numpy as np
import src.Common.Utils.SharedCoreTypes as SCT
from numpy.typing import NDArray
import src.Worker.Agents.Models.ForwardModel as ForwardModel
import src.Worker.Agents.Models.ValueModel as ValueModel
import src.Worker.Agents.Models.PlayStyleModel as PlayStyleModel
import typing
from typing import Optional, Tuple
import math
import src.Worker.Agents.BaseAgent as BaseAgent
import src.Common.Utils.ConfigHelper as ConfigHelper


class TreeNode(ConfigHelper.ConfigurableClass):
	def __init__(self,
			state:SCT.State,
			episodeStep:int,
			done:bool,
			valueModel:ValueModel.ValueModel,
			playStyleModel:PlayStyleModel.PlayStyleModel,
			parent:Optional['TreeNode'] = None,
			actionIdxTaken:Optional[int] = None):

		self.LoadConfig()

		self.State = state

		self.ValueModelValue = None
		if valueModel.CanPredict():
			self.ValueModelValue = valueModel.Predict([state])

		self.PlayStyleModelValue = None
		if playStyleModel.CanPredict():
			self.PlayStyleModelValue = playStyleModel.Predict([state], [actionIdxTaken])[0]

		self.EpisodeStep = episodeStep
		self.Done = done

		self.TotalRewards:SCT.Reward = 0
		self.Counts = 0

		self.Parent = parent
		self.ActionIdxTaken = actionIdxTaken

		self.Children:Optional[typing.List['TreeNode']] = None

		return

	def Selection(self, exploreFactor:float) -> 'TreeNode':

		if self.Done:
			return self

		if self.Children is None:
			return self


		nodeScores = np.array([child.GetNodeScore(exploreFactor, self.Counts) for child in self.Children])

		# selectedIndex = np.argmax(nodeScores)
		selectedIndex = BaseAgent.BaseAgent._GetMaxValues(nodeScores)

		selectedNode = self.Children[selectedIndex]

		return selectedNode.Selection(exploreFactor)

	def Expand(self, actionList:SCT.Action_List,
			forwardModel:ForwardModel.ForwardModel,
			valueModel:ValueModel.ValueModel,
			playStyleModel:PlayStyleModel.PlayStyleModel) -> None:

		stateList = TreeNode.CloneState(self.State, len(actionList))

		nextStates, rewards, terminateds = forwardModel.Predict(stateList, actionList)


		self.Children = []
		for i in range(len(nextStates)):
			terminated = terminateds[i]
			expandedNode = TreeNode(
				nextStates[i],
				episodeStep=self.EpisodeStep + 1,
				done=terminated,
				valueModel=valueModel,
				playStyleModel=playStyleModel,
				parent=self,
				actionIdxTaken=i)

			if terminated:
				expandedNode.BackPropagate(rewards[i], counts=1)

			self.Children.append(expandedNode)

		return

	def BackPropagate(self, totalReward:SCT.Reward, counts:int) -> None:
		self.TotalRewards += totalReward
		self.Counts += counts

		if self.Parent is not None:
			self.Parent.BackPropagate(totalReward, counts)

		return

	def GetNodeScore(self, exploreFactor:float, parentCounts:int) -> float:
		# Unexplored nodes have maximum values so we favour exploration
		if self.Counts == 0:
			return float('inf')

		# if the node is done then we don't want to explore it further
		if self.Done:
			return float('-inf')

		# get this node's value
		rolloutRewards = self.TotalRewards / self.Counts

		predictedValue = 0
		if self.ValueModelValue is not None:
			predictedValue = self.ValueModelValue

		styleValue = 0
		if self.PlayStyleModelValue is not None:
			styleValue = self.PlayStyleModelValue

		nodeScoreConfig = self.Config["NodeScoreConfig"]

		nodeValue = 0
		nodeValue += rolloutRewards * nodeScoreConfig["RolloutRewardsMultiplier"]
		nodeValue += predictedValue * nodeScoreConfig["PredictedValueMultiplier"]
		nodeValue += styleValue * nodeScoreConfig["StyleValueMultiplier"]





		# get the explore value relative to the other children of our parent
		parentCounts = self.Counts
		if self.Parent is not None:
			parentCounts = self.Parent.Counts

		exploreValue = math.sqrt(math.log(parentCounts) / self.Counts)


		return nodeValue + exploreFactor * exploreValue

	def GetActionValues(self) -> Tuple[Optional[NDArray[np.float32]], Optional[NDArray[np.float32]]]:

		if self.Children is None:
			return None, None

		actionValues = np.zeros(len(self.Children), dtype=np.float32)
		valueModelValues = np.zeros(len(self.Children), dtype=np.float32)

		for i in range(len(self.Children)):
			child = self.Children[i]
			valueModelValues[i] = child.ValueModelValue

			if child.Counts > 0:
				actionValues[i] = child.TotalRewards / child.Counts

				if child.Done and actionValues[i] <= 0:
					actionValues[i] = -1_000
					continue

		return actionValues, valueModelValues

	def GetActionNode(self, action:SCT.Action) -> Optional['TreeNode']:
		for child in self.Children:
			if child.ActionTaken == action:
				return child

		return None

	def DetachParent(self) -> None:
		del self.Parent
		self.Parent = None
		self.ActionIdxTaken = None
		return

	def AllExplored(self) -> bool:

		if self.Children is None:
			return False

		for child in self.Children:
			if child.Counts == 0:
				return False

		return True

	@staticmethod
	def CloneState(state:SCT.State, count:int) -> SCT.State_List:

		if isinstance(state, int):
			return np.full(count, state, dtype=np.int_)


		currentState = state.reshape(1, -1)
		states = np.repeat(currentState, count, axis=0)
		return states

	def ToDict(self):
		data = {
			"State": self.State,
			"EpisodeStep": self.EpisodeStep,
			"Done": self.Done,
			"TotalRewards": self.TotalRewards,
			"Counts": self.Counts,
			"ActionIdxTaken": self.ActionIdxTaken,
			"ValueModelValue": self.ValueModelValue,
			"PlayStyleModelValue": self.PlayStyleModelValue
		}

		data["Children"] = None
		if self.Children is not None:
			data["Children"] = [child.ToDict() for child in self.Children]

		return data
