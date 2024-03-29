import typing
import src.Common.Utils.SharedCoreTypes as SCT
from src.Common.Enums.eModelType import eModelType
import src.Worker.Agents.Models.Model as Model

class PlayStyleModel(Model.Model):
	def __init__(self, modelType:eModelType):
		super().__init__(modelType)
		return

	def Predict(self, states:SCT.State_List, actions:SCT.Action_List) -> typing.Tuple[SCT.Reward_List]:

		x = [states, actions]
		y, rawY = super().Predict(x)

		# get the prediction confidence
		# this is the second column of the output
		confidence = rawY[:,1]

		return confidence