
from typing import List
from typing import NewType
from typing import Tuple

from dataclasses import dataclass

@dataclass
class UmlPoint:
    x: int = 0
    y: int = 0


@dataclass
class UmlPosition(UmlPoint):
    """
    Syntactic sugar to be able to reuse a UML Point
    """

    @classmethod
    def deSerialize(cls, value: str) -> 'UmlPosition':

        umlPosition: UmlPosition = UmlPosition()

        xy: List[str] = value.split(sep=',')

        assert len(xy) == 2, 'Incorrectly formatted position'
        assert value.replace(',', '', 1).isdigit(), 'String must be numeric'

        umlPosition.x  = int(xy[0])
        umlPosition.y = int(xy[1])

        return umlPosition

    @classmethod
    def tupleToOglPosition(cls, position: Tuple[int, int]) -> 'UmlPosition':
        """
        tuple[0] is the abscissa
        tuple[1] is the ordinate

        Args:
            position:  A position in Tuple format,

        Returns:  An OglPosition object
        """

        return UmlPosition(x=position[0], y=position[1])

    def __str__(self):
        return f'{self.x},{self.y}'

    def __repr__(self):
        return self.__str__()

UmlPositions = NewType('UmlPositions', List[UmlPosition])
