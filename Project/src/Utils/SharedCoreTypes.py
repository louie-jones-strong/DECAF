import typing
from typing import Any, Optional, Union
from numpy.typing import NDArray
import numpy as np
from gymnasium.spaces import Discrete, Box

# single step
State = Union[NDArray[Any], int, typing.Tuple]
Action = int
Reward = Union[float, int]
Config = typing.Dict[str, Any]

StateSpace = Union[Discrete, Box]
ActionSpace = Discrete



# training batch
State_List = NDArray[Union[np.int_, np.float32]]
Action_List = NDArray[np.int_]
Reward_List = NDArray[Union[np.int_, np.float32]]





def JoinTuples(a:Optional[typing.Tuple], b:Optional[typing.Tuple]) -> typing.Tuple:
	joinedTuple:tuple = tuple()
	if a is not None:
		joinedTuple += a

	if b is not None:
		joinedTuple += b

	return joinedTuple
