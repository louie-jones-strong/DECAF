from typing import TypeVar, Optional
import os
import platform
import typing


# region console input
def FilePicker(label:str, folderPath:str) -> str:
	files = os.listdir(folderPath)
	choice = OptionPicker(label, files)

	return os.path.join(folderPath, choice)

def NumPicker(label:str, minVal:int, maxVal:int) -> int:

	if minVal > maxVal:
		raise Exception("Min value is greater than max value")
	elif minVal == maxVal:
		return minVal

	if label is None or len(label) == 0:
		label = "Pick"

	userInput = input(f"{label}({minVal}-{maxVal}):")

	choice = None

	while True:
		choice = int(userInput)

		if minVal >= 0 and choice <= maxVal:
			break
		else:
			userInput = input("Invalid Please Pick Again:")

	return choice

def BoolPicker(label:str) -> bool:
	if label is None or len(label) == 0:
		label = "Pick"

	userInput = input(f"{label}(True/False):")

	choice:Optional[bool] = None

	while True:
		userInput = userInput.lower()

		if userInput == "true" or userInput == "t":
			choice = True
			break
		elif userInput == "false" or userInput == "f":
			choice = False
			break
		else:
			userInput = input("Invalid Please Pick Again:")

	return choice


T = TypeVar("T")
def OptionPicker(label:str, options:typing.List[T]) -> T:
	if len(options) == 0:
		raise Exception("No options to pick from")
	elif len(options) == 1:
		return options[0]


	for i in range(len(options)):
		print(f"  {i+1}:{options[i]}")

	choice = NumPicker(label, 1, len(options))
	choice -= 1

	return options[choice]

def StrPicker(label:str) -> str:
	if label is None or len(label) == 0:
		label = "Enter String"

	userInput = input(f"{label}:")

	choice = None
	while True:
		choice = userInput

		if len(choice) > 0:
			break
		else:
			userInput = input("Invalid Please Pick Again:")

	return userInput


# endregion


# region keyboard input

def IsKeyPressed(key:str) -> bool:

	# check if os is linux
	if platform.system() == "Linux":
		return False

	import keyboard
	return keyboard.is_pressed(key)

# endregion