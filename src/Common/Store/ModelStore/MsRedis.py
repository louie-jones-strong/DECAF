import src.Common.Store.ModelStore.MsBase as MsBase
import redis
import numpy as np
import tensorflow as tf
import logging

class MsRedis(MsBase.MsBase):

	def __init__(self) -> None:
		super().__init__()

		# connect to the model store
		self.RedisClient = redis.Redis(host="model-store", port=5002, db=0)
		return

	def HasModel(self, modelKey:str) -> bool:
		numExist = self.RedisClient.exists(modelKey)
		return numExist > 0

	def FetchNewestWeights(self, modelKey:str, model:tf.keras.models.Model) -> bool:
		try:

			flatWeightBytes = self.RedisClient.get(modelKey)
			if flatWeightBytes is None:
				return False

			flatWeights = np.frombuffer(flatWeightBytes, dtype=np.float32)

			currentWeights = model.get_weights()

			newWeights = []
			idx = 0
			for layer in currentWeights:
				shape = layer.shape
				count = np.prod(shape)
				layerWeights = flatWeights[idx:idx+count]
				layerWeights = layerWeights.reshape(shape)
				idx += count
				newWeights.append(layerWeights)

			model.set_weights(newWeights)
		except Exception as e:
			logging.exception("Failed to fetch weights from model store", exc_info=e)
			return False

		return True

	def PushModel(self, modelKey:str, model:tf.keras.models.Model) -> None:

		weights = model.get_weights()
		flatWeights = np.concatenate([w.flatten() for w in weights])

		flatWeightBytes = flatWeights.tobytes()
		self.RedisClient.set(modelKey, flatWeightBytes)
		return
