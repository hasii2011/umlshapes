
from typing import List

from dataclasses import dataclass


@dataclass
class DeltaXY:
    """
    Hold the difference between a label and its associated end point;
    """
    deltaX: int = 0
    deltaY: int = 0

    @classmethod
    def deSerialize(cls, value: str) -> 'DeltaXY':

        deltaXY: DeltaXY = DeltaXY()

        deltaXDeltaY: List[str] = value.split(sep=',')

        assert len(deltaXDeltaY) == 2, 'Incorrectly formatted delta x,y'
        assert value.replace(',', '', 1).isdigit(), 'String must be numeric'

        deltaXY.deltaX  = int(deltaXDeltaY[0])
        deltaXY.deltaY = int(deltaXDeltaY[1])

        return deltaXY

    def __str__(self):
        return f'{self.deltaX},{self.deltaY}'

    def __repr__(self):
        return self.__str__()

