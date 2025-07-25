
from typing import Tuple

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx import DC
from wx import MemoryDC
from wx import RED

from wx.lib.ogl import FORMAT_CENTRE_HORIZ
from wx.lib.ogl import FORMAT_CENTRE_VERT
from wx.lib.ogl import RectangleShape

from pyutmodelv2.PyutActor import PyutActor

from umlshapes.UmlUtils import UmlUtils

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.mixins.ControlPointMixin import ControlPointMixin
from umlshapes.mixins.IDMixin import IDMixin
from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.types.UmlDimensions import UmlDimensions

from umlshapes.frames.UseCaseDiagramFrame import UseCaseDiagramFrame

MARGIN: int = 5
ACTOR_HEIGHT_ADJUSTMENT:    float = 0.8
ACTOR_HEAD_SIZE_ADJUSTMENT: float = 0.4
ARM_X_ADJUSTMENT:           float = 0.25
ARM_Y_ADJUSTMENT:           float = 0.15
BODY_START_ADJUSTMENT:      float = 0.2
NAME_Y_ADJUSTMENT:          float = 0.60


@dataclass
class HeadComputations:
    """
    Holds the results of the computations when drawing the Actor's head
    """
    centerX:   int = 0
    centerY:   int = 0
    adjustedY: int = 0


class UmlActor(ControlPointMixin, RectangleShape, TopLeftMixin, IDMixin):

    def __init__(self, pyutActor: PyutActor = None, size: UmlDimensions = None):
        """

        Args:
            pyutActor:
            size:       An initial size that overrides the default
        """
        self.logger: Logger = getLogger(__name__)

        self._preferences: UmlPreferences = UmlPreferences()
        if pyutActor is None:
            self._pyutActor: PyutActor = PyutActor()
        else:
            self._pyutActor = pyutActor

        if size is None:
            actorSize: UmlDimensions = self._preferences.actorSize
        else:
            actorSize = size

        super().__init__(shape=self)
        RectangleShape.__init__(self, w=actorSize.width, h=actorSize.height)
        TopLeftMixin.__init__(self, umlShape=self, width=actorSize.width, height=actorSize.height)
        IDMixin.__init__(self, umlShape=self)

        self.SetFixedSize(actorSize.width, actorSize.height)
        self.SetDraggable(drag=True)
        self.SetCentreResize(False)
        self.SetMaintainAspectRatio(True)
        self.SetFormatMode(mode=FORMAT_CENTRE_HORIZ | FORMAT_CENTRE_VERT)

    @property
    def pyutActor(self) -> PyutActor:
        return self._pyutActor

    @pyutActor.setter
    def pyutActor(self, value: PyutActor):
        self._pyutActor = value

    @property
    def selected(self) -> bool:
        return self.Selected()

    @selected.setter
    def selected(self, select: bool):
        self.Select(select=select)

    @property
    def umlFrame(self) -> UseCaseDiagramFrame:
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: UseCaseDiagramFrame):
        self.SetCanvas(frame)

    # This is dangerous, accessing internal stuff
    # noinspection PyProtectedMember
    # noinspection SpellCheckingInspection
    def ResetControlPoints(self):
        """
        Reset the positions of the control points (for instance, when the
        shape's shape has changed).

        Actors only have 4 control points HORIZONTAL and VERTICAL
        Bad Code depends on indices

        REFERENCE:  The parent of this method that I am deeply overriding
        """
        self.ResetMandatoryControlPoints()

        if len(self._controlPoints) == 0:
            return

        maxX, maxY = self.GetBoundingBoxMax()
        minX, minY = self.GetBoundingBoxMin()

        # widthMin  = minX + UML_CONTROL_POINT_SIZE + 2
        # heightMin = minY + UML_CONTROL_POINT_SIZE + 2
        widthMin  = minX
        heightMin = minY

        # Offsets from the main object
        top = -heightMin / 2.0
        bottom = heightMin / 2.0 + (maxY - minY)
        left = -widthMin / 2.0
        right = widthMin / 2.0 + (maxX - minX)

        self._controlPoints[0]._xoffset = left
        self._controlPoints[0]._yoffset = top

        # self._controlPoints[0]._xoffset = 0
        # self._controlPoints[0]._yoffset = top

        self._controlPoints[1]._xoffset = right
        self._controlPoints[1]._yoffset = top

        # self._controlPoints[1]._xoffset = right
        # self._controlPoints[1]._yoffset = 0

        self._controlPoints[2]._xoffset = right
        self._controlPoints[2]._yoffset = bottom

        # self._controlPoints[2]._xoffset = 0
        # self._controlPoints[2]._yoffset = bottom

        self._controlPoints[3]._xoffset = left
        self._controlPoints[3]._yoffset = bottom

        # self._controlPoints[3]._xoffset = left
        # self._controlPoints[3]._yoffset = 0

    def OnDraw(self, dc: MemoryDC):
        """
        Don't call parent OnDraw;  Do not need the borders drawn

        x, y are the center of the shape
        Args:
            dc:
        """
        dc.SetBrush(UmlUtils.backGroundBrush())
        dc.SetFont(UmlUtils.defaultFont())
        # Gets the minimum bounding box for the shape
        width:  int = self.size.width
        height: int = self.size.height

        # Calculate the top and left of the shape
        x: int = round(self.GetX())
        y: int = round(self.GetY())
        # x: int = self.GetX()
        # y: int = self.GetY()

        leftX: int = x - (width // 2)
        topY:  int = y - (height // 2)

        # drawing is restricted in the specified region of the device
        dc.SetClippingRegion(leftX, topY, width, height)
        if self.Selected() is True:
            UmlUtils.drawSelectedRectangle(dc=dc, shape=self)

        self._drawActor(dc=dc, x=x, y=y, width=width, height=height)

        dc.DestroyClippingRegion()

    def _drawActor(self, dc: MemoryDC, x: int, y: int, width: int, height: int):

        # Our sweet actor size
        actorWidth:   int = width
        actorHeight:  int = round(ACTOR_HEIGHT_ADJUSTMENT * (height - 2.0 * MARGIN))  # % of total height
        actorMinSize: int = min(actorHeight, actorWidth)

        hc: HeadComputations = self._drawActorHead(dc=dc, actorMinSize=actorMinSize, height=height, x=x, y=y)
        x, y                 = self._drawBodyAndArms(dc=dc,
                                                     actorMinSize=actorMinSize,
                                                     actorHeight=actorHeight,
                                                     actorWidth=actorWidth,
                                                     centerX=hc.centerX,
                                                     y=hc.adjustedY
                                                     )
        self._drawActorFeet(dc, actorHeight, actorWidth, x, y)
        self._drawBuddyName(dc, actorHeight, hc.centerY,  height, x)

    def _drawActorHead(self, dc: DC, actorMinSize: int, height: int, x: int, y: int) -> HeadComputations:
        """
        Draw our actor head
        Args:
            dc:
            actorMinSize:
            height:
            x:
            y:

        Returns:  The center coordinates (centerX, centerY) and the adjusted y position
        """
        centerX:   int = x
        adjustedX: int = round(centerX - 0.2 * actorMinSize)
        adjustedY: int  = y - (height // 2) + MARGIN

        percentageOfMinSize: int = round(ACTOR_HEAD_SIZE_ADJUSTMENT * actorMinSize)
        centerY:             int = adjustedY + percentageOfMinSize

        dc.DrawEllipse(adjustedX, adjustedY, percentageOfMinSize, percentageOfMinSize)

        return HeadComputations(centerX=centerX,
                                centerY=centerY,
                                adjustedY=y
                                )

    def _drawBodyAndArms(self, dc: DC, actorMinSize: int, actorHeight, actorWidth, centerX, y: int) -> Tuple[int, int]:
        """
        Draw body and arms
        Args:
            dc:
            actorMinSize:
            actorHeight:
            actorWidth:
            centerX:
            y:

        Returns: Updated x, y positions as a tuple
        """
        bodyX: int = centerX
        bodyY: int = y - round(BODY_START_ADJUSTMENT * actorMinSize)

        dc.DrawLine(bodyX, bodyY, bodyX, bodyY + round(0.3 * actorHeight))

        # draw arms as a single left to right line
        x1: int = round(bodyX - ARM_X_ADJUSTMENT * actorWidth)
        y1: int = round(bodyY + ARM_Y_ADJUSTMENT * actorHeight)
        x2: int = round(bodyX + ARM_X_ADJUSTMENT * actorWidth)
        y2: int = round(bodyY + ARM_Y_ADJUSTMENT * actorHeight)

        dc.DrawLine(x1=x1, y1=y1, x2=x2, y2=y2)

        return bodyX, bodyY

    def _drawActorFeet(self, dc: DC, actorHeight: int, actorWidth: int, x: int, y: int):
        """

        Args:
            dc:
            actorHeight:
            actorWidth:
            x:
            y:
        """
        actorFeetPercentage: int = round(0.3 * actorHeight)
        y += round(actorFeetPercentage)

        dc.DrawLine(x, y, x - round(0.25 * actorWidth), y + actorFeetPercentage)
        dc.DrawLine(x, y, x + round(0.25 * actorWidth), y + actorFeetPercentage)

    def _drawBuddyName(self, dc: DC, actorHeight: int, centerY: int, height: int, x: int):
        """
        Args:
            dc:
            actorHeight:
            centerY:
            height:
            x:
        """

        textWidth, textHeight = dc.GetTextExtent(self.pyutActor.name)

        y = round(centerY + NAME_Y_ADJUSTMENT * height - MARGIN - 0.1 * actorHeight)

        if self.Selected() is True:
            dc.SetTextForeground(RED)

        dc.DrawText(self.pyutActor.name, round(x - 0.5 * textWidth), y)

    def __str__(self) -> str:
        return self.pyutActor.name

    def __repr__(self):

        strMe: str = f"[UmlActor - umlId: `{self.id} `modelId: '{self.pyutActor.id}']"
        return strMe
