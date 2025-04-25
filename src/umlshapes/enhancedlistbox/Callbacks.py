
from typing import Callable

from umlshapes.enhancedlistbox.CallbackAnswer import CallbackAnswer
from umlshapes.enhancedlistbox.DownCallbackData import DownCallbackData
from umlshapes.enhancedlistbox.UpCallbackData import UpCallbackData

AddCallback    = Callable[[],    CallbackAnswer]    # Consumer provided eventHandler;  Expects no parameters; Returns a CallbackAnswer
EditCallback   = Callable[[int], CallbackAnswer]    # Consumer provided eventHandler;  Expects the list box selection #; Returns a CallbackAnswer
RemoveCallback = Callable[[int], None]              # Consumer provided eventHandler;  Expects the list box selection #; Returns a CallbackAnswer
UpCallback     = Callable[[int], UpCallbackData]
DownCallback   = Callable[[int], DownCallbackData]
