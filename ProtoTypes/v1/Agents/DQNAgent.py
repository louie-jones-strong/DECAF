from . import BaseAgent
import Utils.ReplayBuffer as ReplayBuffer
import tensorflow as tf
import numpy as np
import os

class DQNAgent(BaseAgent.BaseAgent):

	def __init__(self, env, envConfig, mode=BaseAgent.AgentMode.Train):
		super().__init__(env, envConfig, mode=mode)

		self.TransitionAcc = ReplayBuffer.TransitionAccumulator(1000)
		self.ReplayBuffer = ReplayBuffer.ReplayBuffer(self.Config["MaxBufferSize"], self.Env)


		self.RunModel = self.BuildModel()
		self.ExplorationRate = self.Config["MaxExplorationRate"]

		if self.Mode == BaseAgent.AgentMode.Train:
			self.TrainingModel = self.BuildModel()
			self.TrainingModel.set_weights(self.RunModel.get_weights())

			self.ExplorationAgent = BaseAgent.GetAgent(self.Config["ExplorationAgent"])(self.Env, envConfig)
			self.IsEval = True

		return

	def BuildModel(self):
		inputShape = self.Env.observation_space.shape
		outputNumber = self.Env.action_space.n


		model = tf.keras.models.Sequential()

		# input layer
		model.add(tf.keras.layers.Input(shape=inputShape))
		model.add(tf.keras.layers.Flatten())

		# hidden layers


		# output layer
		model.add(tf.keras.layers.Dense(outputNumber))

		lr = self.Config["LearningRate"]
		optimizer = tf.keras.optimizers.Adam(learning_rate=lr)

		# compile the network
		self.LossFunc = tf.keras.losses.Huber()
		model.compile(optimizer=optimizer, loss=self.LossFunc)

		return model




	def Reset(self):
		super().Reset()
		self.TransitionAcc.TransferToReplayBuffer(self.ReplayBuffer)
		self.TransitionAcc.Clear()

		self.ExplorationAgent.Reset()

		if self.IsEval:
			self.IsEval = False
		elif self.Mode == BaseAgent.AgentMode.Train:
			if self.EpisodeNum % self.Config["EpisodesBetweenEval"] == 0:
				self.IsEval = True

		return

	def Remember(self, state, action, reward, nextState, done):
		super().Remember(state, action, reward, nextState, done)
		self.TransitionAcc.Add(state, action, reward, nextState, done)
		return

	def Train(self):

		# check that we are in training mode
		if self.Mode != BaseAgent.AgentMode.Train:
			return

		if len(self.ReplayBuffer) < self.Config["MinBufferSize"]:
			return

		# samples from the replay buffer

		def GetSamples(bactchSize):
			indexs, states, actions, rewards, nextStates, dones, futureRewards, priorities = self.ReplayBuffer.Sample(batchSize)
			dones = tf.convert_to_tensor([float(done) for done in dones])


			return indexs, states, actions, rewards, nextStates, dones, futureRewards, priorities
		def CalTargetQs(states, actions, rewards, nextStates, dones, futureRewards):

			nextStatePredictedQ = self.RunModel.predict(nextStates, verbose=0)
			# get the max Q for the next state
			futureQ = np.max(nextStatePredictedQ, axis=1)


			# if the real future reward is not None, then check if it is better than the predicted
			if futureRewards is not None:
				futureQ = np.maximum(futureQ, futureRewards)

			# we should not add future reward if it is the last state
			futureQ *= (1-dones)

			# discount factor for future rewards
			gamma = self.Config["FutureRewardDiscount"]
			futureQ *= gamma


			# Calculate targets (bellman equation)
			targetQs = rewards + futureQ

			return targetQs
		def TrainWeights(targetQs, states, actions, priorities):
			# aplly gradient descent
			with tf.GradientTape() as tape:
				qValues = self.TrainingModel(states)

				actionMask = tf.keras.utils.to_categorical(actions, self.Env.action_space.n, dtype=np.float32)
				currentQ = tf.reduce_sum(tf.multiply(qValues, actionMask), axis=1)

				absError = abs(targetQs - currentQ)
				loss = self.LossFunc(targetQs, currentQ)
				# loss = tf.reduce_mean(loss * priorities)

			gradients = tape.gradient(loss, self.TrainingModel.trainable_variables)
			self.TrainingModel.optimizer.apply_gradients(zip(gradients, self.TrainingModel.trainable_variables))
			return loss, absError


		batchSize = self.Config["BatchSize"]
		indexs, states, actions, rewards, nextStates, dones, futureRewards, priorities = GetSamples(batchSize)
		targetQs = CalTargetQs(states, actions, rewards, nextStates, dones, futureRewards)
		loss, absError = TrainWeights(targetQs, states, actions, priorities)

		# update the priorities
		self.ReplayBuffer.UpdatePriorities(indexs, absError)


		# update the training network
		if self.TotalFrameNum % self.Config["FramesPerUpdateRunningNetwork"] == 0:
			self.RunModel.set_weights(self.TrainingModel.get_weights())
			print("=================update running network=================")
		return

	def GetActionValues(self, state):

		isExploreAction = False
		# if it is training mode
		if self.Mode == BaseAgent.AgentMode.Train and not self.IsEval:
			if np.random.random() < self.ExplorationRate:
				isExploreAction = True

			# decay exploration rate
			self.ExplorationRate -= self.Config["ExplorationDelta"]
			self.ExplorationRate = max(self.ExplorationRate, self.Config["MinExplorationRate"])


		# get action values from the network
		state = np.expand_dims(state, axis=0)
		actionValues = self.RunModel.predict(state, verbose=0)[0]
		# print(f"Action: {np.argmax(actionValues)} Value: {np.max(actionValues):.2f}")

		# get action values
		if isExploreAction:
			# get action values from the exploration agent
			actionValues = self.ExplorationAgent.GetActionValues(state)


		framesPerTrain = self.Config["FramesPerTrain"]
		if self.TotalFrameNum % framesPerTrain == 0:
			self.Train()


		return actionValues


	def Save(self, path):
		self.RunModel.save( os.path.join(path, "DqnModel.h5") )
		self.ReplayBuffer.Save( os.path.join(path, "ReplayBuffer") )
		return

	def Load(self, path):

		modelPath = os.path.join(path, "DqnModel.h5")
		if os.path.exists(modelPath):
			self.RunModel = tf.keras.models.load_model(modelPath)

			if self.Mode == BaseAgent.AgentMode.Train:
				self.TrainingModel.set_weights(self.RunModel.get_weights())


		self.ReplayBuffer.Load( os.path.join(path, "ReplayBuffer") )
		return