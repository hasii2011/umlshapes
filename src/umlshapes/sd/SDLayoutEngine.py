from dataclasses import replace

from logging import Logger
from logging import getLogger

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.sd.SDLayoutParameters import SDLayoutParameters


class SDLayoutEngine:
    """
    Computes coordinates for Sequence Diagram participants and message timeSteps.
    Provides deterministic layout for interactive diagrams and auto-generation.

    Initialization:
        Always instantiates with default layout parameters (SDLayoutParameters).
        If a caller requires a customized parameter set, they should:
          1. Retrieve a copy of the current parameters via the `parameters` getter,
             modify the desired fields, and reassign it via the setter; OR
          2. Construct a new SDLayoutParameters instance and assign it via the `parameters` setter.
    """

    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        self._parameters:  SDLayoutParameters = SDLayoutParameters()
        self._preferences: UmlPreferences     = UmlPreferences()

    @property
    def parameters(self) -> SDLayoutParameters:
        """
        Returns a copy of the layout parameters.

        Direct mutations to the returned instance will not affect this engine;
        any modifications must be submitted via the parameter's setter.
        """
        return replace(self._parameters)

    @parameters.setter
    def parameters(self, parameters: SDLayoutParameters):
        """
        Update the layout parameters for this engine.

        Args:
            parameters: The new SDLayoutParameters to use for layout calculations.
        """
        self._parameters = replace(parameters)

    def computeColumnX(self, columnIndex: int) -> int:
        """
        Compute horizontal center X coordinate for a given participant column index.
        """
        return self._parameters.startX + (columnIndex * self._parameters.columnSpacing)

    def computeSlotY(self, headerBottomY: int, slotIndex: int) -> int:
        """
        Compute the vertical Y coordinate for a given message slot index.
        """
        return headerBottomY + self._parameters.topPadding + (slotIndex * self._parameters.slotHeight)

    def computeNearestSlotIndex(self, headerBottomY: int, targetY: int) -> int:
        """
        Compute the nearest slot index for a given raw Y coordinate.
        """
        relativeY: int = targetY - (headerBottomY + self._parameters.topPadding)
        if relativeY < 0:
            return 0
        slotIndex: int = round(relativeY / self._parameters.slotHeight)
        return slotIndex

    def computeNearestSlotY(self, headerBottomY: int, targetY: int) -> int:
        """
        Snap an arbitrary Y coordinate to the nearest valid slot Y.
        """
        slotIndex: int = self.computeNearestSlotIndex(headerBottomY=headerBottomY, targetY=targetY)
        return self.computeSlotY(headerBottomY=headerBottomY, slotIndex=slotIndex)

    def computeLifelineHeight(self, totalSlots: int) -> int:
        """
        Compute the required lifeline height to accommodate totalSlots message levels.
        """
        initialHeight: int = self._preferences.initialLifeLineLength
        neededHeight: int = self._parameters.topPadding + ((totalSlots + 1) * self._parameters.slotHeight) + self._parameters.bottomPadding
        return max(initialHeight, neededHeight)
