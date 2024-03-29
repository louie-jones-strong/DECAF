import src.Common.Utils.ModelHelper as ModelHelper
from src.Common.Enums.eModelType import eModelType
import src.Common.Utils.Metrics.Metrics as Metrics
from src.Common.Utils.Config.ConfigurableClass import ConfigurableClass
import logging


class Model(ConfigurableClass):

	def __init__(self, modelType:eModelType):
		super().__init__()
		self.ModelConfig = self.Config["ModelConfigs"][modelType.name]

		self._ModelType = modelType

		self._ModelHelper = ModelHelper.ModelHelper()
		modelData = self._ModelHelper.BuildModel(self._ModelType)
		self._Model, self._InputColumns, self._OutputColumns, self._ModelConfig = modelData

		self.HasTrainedModel = False

		self._Metrics = Metrics.Metrics()

		self.UpdateModels()
		return

	def UpdateModels(self) -> None:
		self.HasTrainedModel = self._ModelHelper.FetchNewestWeights(self._ModelType, self._Model)
		logging.info(f"fetched newest weights ({self._ModelType}) {self.HasTrainedModel}")
		return

	def CanPredict(self) -> bool:
		return self.HasTrainedModel


	def Predict(self, x):
		preProcessedX = self._ModelHelper.PreProcessColumns(x, self._InputColumns)

		batchSize = min(len(x), self.ModelConfig["MaxDeploymentBatchSize"])
		rawY = self._Model.predict(preProcessedX, batch_size=batchSize, verbose=0)

		y = self._ModelHelper.PostProcessColumns(rawY, self._OutputColumns)

		return y, rawY
