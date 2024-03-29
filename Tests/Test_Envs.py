import unittest
import os
import src.Worker.Worker as Worker
import src.Common.Store.ExperienceStore.EsBase as EsBase
from src.Common.Enums.eAgentType import eAgentType
import src.Worker.EnvRunner as EnvRunner
import src.Worker.Environments.BaseEnv as BaseEnv
import src.Common.Utils.Config.ConfigManager as ConfigManager


class Test_Envs(unittest.TestCase):

	ConfigRoot = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Config')
	EnvsRoot = os.path.join(ConfigRoot, 'Envs')
	MaxEpisodesOverride = 1
	MaxStepsOverride = 10
	AgentType = eAgentType.Random

	def test_Envs(self):
		configManager = ConfigManager.ConfigManager()
		configList = os.listdir(self.EnvsRoot)

		for config in configList:
			configManager.Setup(config)

			configPath = os.path.join(self.EnvsRoot, config)
			# check is a file
			self.assertTrue(os.path.isfile(configPath), 'Config is not a file')

			# check is a json file
			self.assertTrue(config.endswith('.json'), 'Config is not a json file')


			# modify the config to use a smaller number of episodes and steps
			configManager.EnvConfig["MaxEpisodes"] = self.MaxEpisodesOverride
			configManager.EnvConfig["MaxSteps"] = self.MaxStepsOverride
			configManager.EnvConfig["NumEnvsPerWorker"] = 2

			envRunners = []

			env = BaseEnv.GetEnv(configManager.EnvConfig, render=False)
			experienceStore = EsBase.EsBase()
			runner = EnvRunner.EnvRunner(env, configManager.EnvConfig["MaxSteps"], experienceStore)
			envRunners.append(runner)
			worker = Worker.Worker(self.AgentType, envRunners, True)

			worker.Run()



		return
