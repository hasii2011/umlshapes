
from typing import List

from dataclasses import dataclass


DEFAULT_X_WIGGLE_FACTOR: int = 10
DEFAULT_Y_WIGGLE_FACTOR: int = 10


@dataclass
class WiggleFactor:
    xFactor: int = DEFAULT_X_WIGGLE_FACTOR
    yFactor: int = DEFAULT_Y_WIGGLE_FACTOR

    @classmethod
    def deSerialize(cls, value: str) -> 'WiggleFactor':

        wiggleFactor: WiggleFactor = WiggleFactor()

        xy: List[str] = value.split(sep=',')

        assert len(xy) == 2, 'Incorrectly formatted position'
        assert value.replace(',', '', 1).isdigit(), 'String must be numeric'

        wiggleFactor.xFactor  = int(xy[0])
        wiggleFactor.yFactor = int(xy[1])

        return wiggleFactor

    def __str__(self):
        return f'{self.xFactor},{self.yFactor}'

    def __repr__(self):
        return self.__str__()
