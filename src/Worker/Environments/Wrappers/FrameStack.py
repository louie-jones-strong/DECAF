# code was modified from
# https://github.com/openai/baselines/blob/master/baselines/src.Common/atari_wrappers.py


from typing import Any, SupportsFloat, TYPE_CHECKING
import src.Common.Utils.SharedCoreTypes as SCT
from numpy.typing import NDArray

# other file dependencies
import gymnasium as gym
from collections import deque
from gymnasium import spaces
import numpy as np
import typing


class FrameStack(gym.Wrapper):
	def __init__(self, env:gym.Env, k:int):
		gym.Wrapper.__init__(self, env)
		self.k = k
		self.frames:typing.Deque[SCT.State] = deque([], maxlen=k)

		shape = env.observation_space.shape

		dtype = env.observation_space.dtype
		assert dtype == np.uint8 or dtype == np.float32, \
			f'FrameStack requires uint8 or float32 observations. but was: {dtype}'

		if TYPE_CHECKING:
			assert isinstance(dtype, (np.uint8, np.float32)), \
				f'FrameStack requires uint8 or float32 observations. but was: {dtype}'

		self.observation_space = spaces.Box(
			low=0,
			high=255,
			shape=(SCT.JoinTuples(shape, (k,))),
			dtype=dtype)
		return

	def reset(self, **kwargs:Any) -> typing.Tuple[NDArray[Any], typing.Dict[str, Any]]:
		state, info = self.env.reset(**kwargs)
		for _ in range(self.k):
			self.frames.append(state)
		return self._get_ob(), info

	def step(self, action:SCT.Action) -> typing.Tuple[NDArray[Any], SupportsFloat, bool, bool, typing.Dict[str, Any]]:
		nextState, reward, terminated, truncated, info = self.env.step(action)
		self.frames.append(nextState)
		return self._get_ob(), reward, terminated, truncated, info

	def _get_ob(self) -> NDArray[Any]:
		assert len(self.frames) == self.k

		stackedFrames = np.array(self.frames)
		stackedFrames = np.swapaxes(stackedFrames, 0, 2)
		return stackedFrames
