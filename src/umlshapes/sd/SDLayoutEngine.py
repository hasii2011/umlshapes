from dataclasses import replace
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.sd.SDFragmentBounds import SDFragmentBounds
from umlshapes.sd.SDLayoutParameters import SDLayoutParameters

if TYPE_CHECKING:
    from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine


class SDLayoutEngine:
    """
    Computes coordinates for Sequence Diagram participants and message timeSteps.
    Provides deterministic layout for interactive diagrams and auto-generation.

    Initialization:
        Always instantiates with layout parameters initialized from preferences.
        If a caller requires a customized parameter set, they should:
          1. Retrieve a copy of the current parameters via the `parameters` getter,
             modify the desired fields, and reassign it via the setter; OR
          2. Construct a new SDLayoutParameters instance and assign it via the `parameters` setter.
    """

    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        self._preferences: UmlPreferences     = UmlPreferences()
        self._parameters:  SDLayoutParameters = SDLayoutParameters(
            timeStepHeight=self._preferences.timeStepHeight,
            reflexiveMessageWidth=self._preferences.reflexiveMessageWidth,
            executionWidth=self._preferences.executionWidth,
            executionShiftDelta=self._preferences.executionShiftDelta,
            fragmentPadding=self._preferences.fragmentPadding
        )

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

    def computeTimeStepY(self, headerBottomY: int, timeStepIndex: int) -> int:
        """
        Compute the vertical Y coordinate for a given message timeStep index.
        """
        return headerBottomY + self._parameters.topPadding + (timeStepIndex * self._parameters.timeStepHeight)

    def computeNearestTimeStepIndex(self, headerBottomY: int, targetY: int) -> int:
        """
        Compute the nearest timeStep index for a given raw Y coordinate.
        """
        relativeY: int = targetY - (headerBottomY + self._parameters.topPadding)
        if relativeY < 0:
            return 0
        timeStepIndex: int = round(relativeY / self._parameters.timeStepHeight)
        return timeStepIndex

    def computeNearestTimeStepY(self, headerBottomY: int, targetY: int) -> int:
        """
        Snap an arbitrary Y coordinate to the nearest valid timeStep Y.
        """
        timeStepIndex: int = self.computeNearestTimeStepIndex(headerBottomY=headerBottomY, targetY=targetY)
        return self.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=timeStepIndex)

    def computeExecutionX(self, lifeLineX: int, nestingLevel: int = 0) -> int:
        """
        Compute horizontal center X coordinate for an activation bar on a lifeline.
        Nesting level 0 is centered directly on the lifeline; nested levels are shifted right.
        """
        shiftDelta: int = self._parameters.executionShiftDelta
        return lifeLineX + (nestingLevel * shiftDelta)

    def computeExecutionBounds(
        self,
        lifeLineX: int,
        startY: int,
        endY: int,
        nestingLevel: int = 0
    ) -> tuple[int, int, int, int]:
        """
        Compute (centerX, centerY, width, height) for an activation bar.
        Height is constrained to at least one timeStepHeight.
        """
        centerX: int = self.computeExecutionX(lifeLineX=lifeLineX, nestingLevel=nestingLevel)
        centerY: int = (startY + endY) // 2
        width: int = self._parameters.executionWidth
        height: int = max(self._parameters.timeStepHeight, endY - startY)
        return centerX, centerY, width, height

    def computeLifelineHeight(self, totalTimeSteps: int) -> int:
        """
        Compute the required lifeline height to accommodate totalTimeSteps message levels.
        """
        initialHeight: int = self._preferences.initialLifeLineLength
        neededHeight: int = self._parameters.topPadding + ((totalTimeSteps + 1) * self._parameters.timeStepHeight) + self._parameters.bottomPadding
        return max(initialHeight, neededHeight)

    def computeFragmentBounds(
        self,
        lifeLines: list['UmlSDLifeLine'],
        startY: int,
        endY: int
    ) -> SDFragmentBounds:
        """
        Compute the bounding box (SDFragmentBounds) for a combined fragment.

        The horizontal span extends from the leftmost to the rightmost participant
        lifelines, expanded on each side by `fragmentPadding`. The vertical span is
        bounded by `startY` and `endY`, constrained to at least one `timeStepHeight`.
        Coordinates are centered per wxOGL / RectangleShape conventions.

        Args:
            lifeLines: Participant lifelines covered by the combined fragment.
            startY:    Top vertical coordinate (typically snapped to a timeStep).
            endY:      Bottom vertical coordinate (typically snapped to a timeStep).

        Returns:
            SDFragmentBounds: Dataclass containing centerX, centerY, width, and height.
        """
        if len(lifeLines) == 0:
            return SDFragmentBounds(
                centerX=0,
                centerY=(startY + endY) // 2,
                width=0,
                height=max(self._parameters.timeStepHeight, endY - startY)
            )

        padding: int = self._parameters.fragmentPadding
        xPositions: list[int] = [round(lifeLine.GetX()) for lifeLine in lifeLines]
        minX: int = min(xPositions) - padding
        maxX: int = max(xPositions) + padding

        width: int = maxX - minX
        centerX: int = (minX + maxX) // 2

        height: int = max(self._parameters.timeStepHeight, endY - startY)
        centerY: int = (startY + endY) // 2

        return SDFragmentBounds(
            centerX=centerX,
            centerY=centerY,
            width=width,
            height=height
        )

    def snapFragmentToTimeSteps(self, headerBottomY: int, startY: int, endY: int) -> tuple[int, int]:
        """
        Snap top and bottom Y coordinates of a fragment to the nearest discrete time steps.
        Ensures endY is at least one timeStep below startY.
        """
        snappedStartY: int = self.computeNearestTimeStepY(headerBottomY=headerBottomY, targetY=startY)
        snappedEndY: int = self.computeNearestTimeStepY(headerBottomY=headerBottomY, targetY=endY)

        if snappedEndY <= snappedStartY:
            snappedEndY = snappedStartY + self._parameters.timeStepHeight

        return snappedStartY, snappedEndY
