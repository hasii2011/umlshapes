
from typing import List
from typing import NewType
from typing import Tuple

from dataclasses import dataclass


@dataclass
class UmlPosition:

    x: int = 0
    y: int = 0

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


UmlPositions = NewType('UmlPositions', List[UmlPosition])
