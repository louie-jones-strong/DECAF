import os
import json
from src.Common.Utils.PathHelper import GetRootPath
import src.Common.Utils.SharedCoreTypes as SCT
from gymnasium.spaces import Discrete, Box
from typing import Union
import numpy as np


class ConfigurableClass:

	def LoadConfig(self, overrideConfig:SCT.Config) -> None:
		self.Config = LoadAndMergeConfig(self.__class__.__name__, overrideConfig)

		# get base config from base classes
		for b in self.__class__.__bases__:
			if issubclass(b, ConfigurableClass) and b != ConfigurableClass:
				self.Config = LoadAndMergeConfig(b.__name__, self.Config, allowJoining=True)

		return

def LoadAndMergeConfig(className:str, overrideConfig:SCT.Config, allowJoining:bool = False) -> SCT.Config:

	configPath = GetClassConfigPath(className)

	baseConfig = {}
	if os.path.exists(configPath):
		baseConfig = LoadConfig(configPath)

	if HasNoneBaseKeys(baseConfig, overrideConfig) and className in overrideConfig:
		overrideConfig = overrideConfig[className]

	baseConfig = MergeConfig(baseConfig, overrideConfig, allowJoining=allowJoining)

	return baseConfig


def GetClassConfigPath(className:str) -> str:
	configPath = os.path.join(GetRootPath(), "Config", f"{className}.json")

	return configPath


def LoadConfig(configPath:str) -> SCT.Config:

	if not os.path.exists(configPath):
		raise Exception(f"configPath {configPath} does not exist")

	if not os.path.isfile(configPath):
		raise Exception(f"configPath {configPath} is not a file")

	with open(configPath, "r") as f:
		config = json.load(f)

	return config





def MergeConfig(
		baseConfig:SCT.Config,
		overrideConfig:SCT.Config,
		allowJoining:bool = False) -> SCT.Config:

	for key, value in baseConfig.items():

		if key in overrideConfig:
			if isinstance(value, dict):
				MergeConfig(value, overrideConfig[key])
			elif isinstance(value, list):
				raise NotImplementedError()
			else:
				baseConfig[key] = overrideConfig[key]

	if allowJoining:
		for key, value in overrideConfig.items():
			if key not in baseConfig:
				baseConfig[key] = value



	return baseConfig

def HasNoneBaseKeys(baseConfig:SCT.Config, overrideConfig:SCT.Config) -> bool:
	hasNoneBaseKeys = False

	for key, value in overrideConfig.items():
		if key not in baseConfig:
			hasNoneBaseKeys = True
			break

	return hasNoneBaseKeys


def ConfigToDType(typeStr:str) -> np.dtype:

	if typeStr == "float32":
		return np.float32

	raise Exception(f"Unknown dtype: {typeStr}")

def ConfigToSpace(config:SCT.Config) -> Union[Discrete, Box]:

	if config["Type"] == "Discrete":
		space = Discrete(config["Shape"])
	elif config["Type"] == "Box":

		dType = ConfigToDType(config["Dtype"])

		low = np.array(config["Low"], dtype=dType)
		high = np.array(config["High"], dtype=dType)
		shape = tuple(config["Shape"])

		if low.shape != shape:
			low = np.full(shape, low, dtype=dType)

		if high.shape != shape:
			high = np.full(shape, high, dtype=dType)

		space = Box(low, high, shape, np.float32)

	return space