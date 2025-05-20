
from typing_extensions import Protocol


class PositionReporter(Protocol):

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
