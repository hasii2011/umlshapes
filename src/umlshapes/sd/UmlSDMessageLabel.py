
from typing import Optional

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.shapes.UmlBaseLabel import UmlBaseLabel
from umlshapes.types.UmlDimensions import UmlDimensions


class UmlSDMessageLabel(UmlBaseLabel):
    """
    Sequence Diagram Message Label.
    """

    def __init__(self, label: str = '', size: Optional[UmlDimensions] = None):
        """

        Args:
            label: The message text
            size:  Optional dimensions
        """
        preferences: UmlPreferences = UmlPreferences()

        super().__init__(
            label=label,
            size=size,
            fontSize=preferences.associationTextFontSize,
            formatMode=preferences.associationLabelFormat
        )

        self._proportionalOffset: float = 0.5
        self._fixedX:              int   = 0
        self._verticalOffset:      int   = 0

    @property
    def proportionalOffset(self) -> float:
        return self._proportionalOffset

    @proportionalOffset.setter
    def proportionalOffset(self, offset: float):
        self._proportionalOffset = offset

    @property
    def fixedX(self) -> int:
        return self._fixedX

    @fixedX.setter
    def fixedX(self, fixedX: int):
        self._fixedX = fixedX

    @property
    def verticalOffset(self) -> int:
        return self._verticalOffset

    @verticalOffset.setter
    def verticalOffset(self, offset: int):
        self._verticalOffset = offset

