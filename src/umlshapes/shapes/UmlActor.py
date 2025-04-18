
from typing import Tuple

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx import Point

from pyutmodelv2.PyutActor import PyutActor
from wx.lib.ogl import DrawnShape
from wx.lib.ogl import ShapeCanvas

from umlshapes.UmlUtils import UmlUtils
from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlRect import UmlRect

MARGIN: int = 10

ACTOR_HEIGHT_ADJUSTMENT: float = 0.8
BODY_START_ADJUSTMENT:   float = 0.57
BODY_END_ADJUSTMENT:     float = 0.3
ARM_POSITION_ADJUSTMENT: float = 0.1


@dataclass
class HeadComputations:
    """
    Holds the results of the computations when drawing the Actor's head
    """
    centerX:   int = 0
    centerY:   int = 0
    adjustedY: int = 0


class UmlActor(DrawnShape):
    """
    We have to make this a 2 step creation class so it will work
    when we deserialize this class in untanglePyut
    """

    def __init__(self, pyutActor: PyutActor = None, size: UmlDimensions = None):
        """
        Need the position upon creation because of how DrawnShape's work

        Args:
            pyutActor:
            size:
        """

        self.logger:       Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()
        if pyutActor is None:
            self._pyutActor: PyutActor = PyutActor()
        else:
            self._pyutActor = pyutActor

        if size is None:
            self._useCaseSize: UmlDimensions = self._preferences.actorSize
        else:
            self._useCaseSize = size

        super().__init__()

    @property
    def pyutActor(self) -> PyutActor:
        return self._pyutActor

    @pyutActor.setter
    def pyutActor(self, value: PyutActor):
        self._pyutActor = value

    def Create(self, umlPosition: UmlPosition):
        """

        Args:
            umlPosition:

        """
        self.SetX(umlPosition.x)
        self.SetY(umlPosition.y)
        self.SetWidth(self._useCaseSize.width)
        self.SetHeight(self._useCaseSize.height)

        self.SetDrawnBrush(UmlUtils.backGroundBrush(), isFill=True)

        self._drawActor(umlPosition=umlPosition)
        # Make sure to call CalculateSize when all drawing is done
        self.CalculateSize()

    def OnDraw(self, dc):

        width:  int = round(self.GetWidth())
        height: int = round(self.GetHeight())
        x: int = round(self.GetX())
        y: int = round(self.GetY())
        dc.SetClippingRegion(x, y, width, height)

        super().OnDraw(dc=dc)

        dc.DestroyClippingRegion()

    def _drawActor(self, umlPosition: UmlPosition):

        width:       int = self.GetWidth()
        height:      int = self.GetHeight()

        # Our sweet actor size
        actorWidth:   int = width
        actorHeight:  int = round(ACTOR_HEIGHT_ADJUSTMENT * (height - 2.0 * MARGIN))  # 80 % of total height
        actorMinSize: int = min(actorHeight, actorWidth)

        hc: HeadComputations = self._drawActorHead(actorMinSize=actorMinSize, height=height, width=width, x=umlPosition.x, y=umlPosition.y)

        x, y = self._drawBodyAndArms(actorMinSize=actorMinSize,
                                     actorHeight=actorHeight,
                                     actorWidth=actorWidth, centerX=hc.centerX, y=umlPosition.y)

        self._drawActorFeet(actorHeight, actorWidth, x, y)

        self._drawBuddyName(actorHeight=actorHeight, centerY=hc.centerY, height=height, x=x)

    def _drawActorHead(self, actorMinSize: int, height: int, width: int, x: int, y: int) -> HeadComputations:
        """
        Draw our actor head;
        Args:
            height:
            actorMinSize:
            width:
            x:
            y:

        Returns:  The center coordinates (centerX, centerY) and the adjusted y position
        """
        centerX: int = x + width // 2
        centerY: int = y + height // 2

        x = round(centerX - 0.2 * actorMinSize)
        adjustedY = y + MARGIN

        percentageOfMinSize: int = round(0.4 * actorMinSize)
        umlRect: UmlRect = UmlRect(left=x,
                                   top=adjustedY,
                                   width=percentageOfMinSize,
                                   height=percentageOfMinSize)

        # self.DrawEllipse(x, y, percentageOfMinSize, percentageOfMinSize)
        self.DrawEllipse(rect=UmlRect.toRectTuple(umlRect=umlRect))

        # return centerX, centerY, adjustY
        return HeadComputations(
            centerX=centerX,
            centerY=centerY,
            adjustedY=adjustedY
        )

    def _drawBodyAndArms(self, actorMinSize: int, actorHeight, actorWidth, centerX, y: int) -> Tuple[int, int]:
        """
        Draw body and arms
        Args:
            actorMinSize:
            actorHeight:
            actorWidth:
            centerX:
            y:

        Returns: Updated x, y positions as a tuple
        """
        x: int = centerX
        y += round(BODY_START_ADJUSTMENT * actorMinSize)
        #
        # Draw body trunk
        #
        pt1: Point = Point(x=x, y=y)
        pt2: Point = Point(x=x, y=y + round(BODY_END_ADJUSTMENT * actorHeight))

        self.DrawLine(pt1=pt1, pt2=pt2)
        #
        # Draw flailing arms
        #
        pt3: Point = Point(
            x=round(x - 0.25 * actorWidth),
            y=round(y + (ARM_POSITION_ADJUSTMENT * actorHeight))
        )
        pt4: Point = Point(
            x=round(x + 0.25 * actorWidth),
            y=round(y + (ARM_POSITION_ADJUSTMENT * actorHeight))
        )
        self.DrawLine(pt1=pt3, pt2=pt4)

        return x, y

    def _drawActorFeet(self, actorHeight: int, actorWidth: int, x: int, y: int):
        """

        Args:
            actorHeight:
            actorWidth:
            x:
            y:
        """
        actorFeetPercentage: int = round(0.3 * actorHeight)
        y += round(actorFeetPercentage)

        pt1: Point = Point(x=x, y=y)
        pt2: Point = Point(x=x - round(0.25 * actorWidth), y=y + actorFeetPercentage)

        pt3: Point = Point(x=x + round(0.25 * actorWidth), y=y + actorFeetPercentage)

        # self.DrawLine(x, y, x - round(0.25 * actorWidth), y + actorFeetPercentage)
        # self.DrawLine(x, y, x + round(0.25 * actorWidth), y + actorFeetPercentage)
        self.DrawLine(pt1=pt1, pt2=pt2)
        self.DrawLine(pt1=pt1, pt2=pt3)

    def _drawBuddyName(self, actorHeight: int, centerY: int, height: int, x: int):
        """

        Args:
            actorHeight:
            centerY:
            height:
            x:

        """

        # textWidth, textHeight = dc.GetTextExtent(self.pyutActor.name)
        canvas: ShapeCanvas = self.GetCanvas()
        textWidth, textHeight = canvas.GetTextExtent(self.pyutActor.name)

        adjustedX: int = round(x - 0.5 * textWidth)
        y:         int = round(centerY + 0.5 * height - MARGIN - 0.1 * actorHeight)

        pt: Point = Point(x=adjustedX, y=y)

        self.SetDrawnFont(UmlUtils.defaultFont())
        self.DrawText(self.pyutActor.name, pt=pt)
