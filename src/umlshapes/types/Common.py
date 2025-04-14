
from typing import Union
from typing import cast

from pyutmodelv2.PyutNote import PyutNote
from pyutmodelv2.PyutText import PyutText

ModelObject = Union[PyutText, PyutNote, None]


NOT_SET_INT:     int   = cast(int, None)
