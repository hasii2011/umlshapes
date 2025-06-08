
from logging import Logger
from logging import getLogger

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.types.Common import AttachmentSide
from umlshapes.types.Common import LollipopCoordinates
from umlshapes.types.Common import Rectangle
from umlshapes.types.UmlPosition import UmlPosition


class LollipopInflator:
    """
    Expands the lollipop line for a relaxed hit capability
    """
    clsPreferences: UmlPreferences = UmlPreferences()

    def __init__(self):
        self.logger: Logger = getLogger(__name__)

    @classmethod
    def inflateLollipop(cls, attachmentSide: AttachmentSide, lollipopCoordinates: LollipopCoordinates) -> Rectangle:
        """
        Calculates a rectangle around the lollipop.
        TODO: perhaps include the ellipse at the end

        Args:
            attachmentSide:
            lollipopCoordinates:

        Returns:  The inflated rectangle

        """

        rectangle: Rectangle = Rectangle()

        startCoordinates:     UmlPosition = lollipopCoordinates.startCoordinates
        endCoordinates:       UmlPosition = lollipopCoordinates.endCoordinates
        hitAreaInflationRate: int         = LollipopInflator.clsPreferences.hitAreaInflationRate

        if attachmentSide == AttachmentSide.BOTTOM:

            rectangle.left   = startCoordinates.x - hitAreaInflationRate
            rectangle.right  = endCoordinates.x + hitAreaInflationRate
            rectangle.top    = startCoordinates.y
            rectangle.bottom = endCoordinates.y

        elif attachmentSide == AttachmentSide.TOP:

            rectangle.left   = startCoordinates.x - hitAreaInflationRate
            rectangle.right  = endCoordinates.x + hitAreaInflationRate
            rectangle.top    = endCoordinates.y
            rectangle.bottom = startCoordinates.y

        elif attachmentSide == AttachmentSide.RIGHT:

            rectangle.left   = startCoordinates.x
            rectangle.right  = endCoordinates.x
            rectangle.top    = startCoordinates.y - hitAreaInflationRate
            rectangle.bottom = endCoordinates.y + hitAreaInflationRate

        elif attachmentSide == AttachmentSide.LEFT:

            rectangle.left   = endCoordinates.x
            rectangle.right  = startCoordinates.x
            rectangle.top    = startCoordinates.y - hitAreaInflationRate
            rectangle.bottom = endCoordinates.y + hitAreaInflationRate

        return rectangle
