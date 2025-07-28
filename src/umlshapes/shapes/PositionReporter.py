
from typing import Protocol


class PositionReporter(Protocol):
    """
    My one and only use of a protocol class
    """
    def GetLabelPosition(self, idx: int):
        """

        Args:
            idx:    One of
                            NAME_IDX
                            SOURCE_CARDINALITY_IDX
                            DESTINATION_CARDINALITY_IDX

        Returns:    An x,y tuple
        """
        pass
