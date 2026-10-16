
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
        labelSize: UmlDimensions = size if size is not None else preferences.associationLabelSize

        super().__init__(
            label=label,
            size=labelSize,
            fontSize=preferences.associationTextFontSize,
            formatMode=preferences.associationLabelFormat
        )

