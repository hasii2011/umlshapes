
from dataclasses import dataclass


@dataclass
class DeltaXY:
    """
    Hold the difference between a label and its associated end point;
    """
    deltaX: int = 0
    deltaY: int = 0
