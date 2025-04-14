
from typing import List
from typing import NewType

from dataclasses import dataclass

from umlshapes.types.Common import NOT_SET_INT


@dataclass
class UmlSize:
    """
    A size construct
    """
    width:  int = NOT_SET_INT
    height: int = NOT_SET_INT

    def __str__(self):
        return f'{self.width},{self.height}'

    def __repr__(self):
        return self.__str__()


UmlSizes = NewType('UmlSizes', List[UmlSize])
