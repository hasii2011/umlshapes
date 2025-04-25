
from dataclasses import dataclass


@dataclass
class CallbackAnswer:
    """
    An eventHandler returns True if the value in item is to be placed in the listbox,
    A value of False indicates that the value of item is undefined
    """
    valid: bool = False
    item:  str  = ''
