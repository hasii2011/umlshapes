
from typing import cast
from typing import Optional
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import MemoryDC

from umlmodel.SDExecution import SDExecution

from umlshapes.lib.ogl import CONTROL_POINT_VERTICAL
from umlshapes.lib.ogl import RectangleShape

from umlshapes.utils.ResourceUtils import ResourceUtils

from umlshapes.mixins.ControlPointMixin import ControlPointMixin
from umlshapes.mixins.IdentifierMixin import IdentifierMixin
from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.sd.SDLayoutEngine import SDLayoutEngine
from umlshapes.shapes.UmlControlPoint import UmlControlPoint

if TYPE_CHECKING:
    from umlshapes.lib.ogl import ControlPoint
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine

DEFAULT_EXECUTION_WIDTH: int = 14
DEFAULT_MIN_SPAN_HEIGHT: int = 40
HIT_TEST_TOLERANCE:      int = 4

EXECUTION_TOP_HANDLE_INDEX:    int = 0
EXECUTION_BOTTOM_HANDLE_INDEX: int = 1
TOP_CONTROL_POINT_INDEX:       int = EXECUTION_TOP_HANDLE_INDEX
BOTTOM_CONTROL_POINT_INDEX:    int = EXECUTION_BOTTOM_HANDLE_INDEX


class UmlSDExecution(ControlPointMixin, IdentifierMixin, RectangleShape, TopLeftMixin):
    """
    Represents an Execution Specification (Execution Occurrence / Focus of Control)
    drawn as a narrow vertical rectangular overlay on a Sequence Diagram lifeline
    per the OMG UML standard specification.
    """

    def __init__(
        self,
        lifeLine: 'UmlSDLifeLine',
        startY: int = 0,
        endY: int = 0,
        nestingLevel: int = 0,
        sdExecution: Optional[SDExecution] = None
    ):

        self.logger: Logger = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()
        self._layoutEngine: SDLayoutEngine = SDLayoutEngine()

        self._lifeLine: 'UmlSDLifeLine' = lifeLine

        if sdExecution is not None:
            self._sdExecution: SDExecution = sdExecution
            if self._sdExecution.endTime - self._sdExecution.startTime < self._preferences.timeStepHeight:
                self._sdExecution.endTime = self._sdExecution.startTime + self._preferences.timeStepHeight
        else:
            calculatedEndY: int = max(startY + self._preferences.timeStepHeight, endY)
            self._sdExecution = SDExecution(
                instance=lifeLine.sdInstance,
                startTime=startY,
                endTime=calculatedEndY,
                nestingLevel=nestingLevel
            )

        width:  int = self._preferences.executionWidth
        height: int = self._sdExecution.endTime - self._sdExecution.startTime

        ControlPointMixin.__init__(self, shape=self)
        IdentifierMixin.__init__(self)
        RectangleShape.__init__(self, w=width, h=height)
        TopLeftMixin.__init__(self, umlShape=self, width=width, height=height)

        self.SetCanvas(lifeLine.GetCanvas())
        self.SetBrush(ResourceUtils.backGroundBrush())
        self.SetPen(ResourceUtils.blackSolidPen())
        self.SetCentreResize(False)

        self.recomputeGeometry()

        umlFrame: Optional['UmlFrame'] = cast(Optional['UmlFrame'], lifeLine.GetCanvas())
        if umlFrame is not None:
            if hasattr(umlFrame, 'umlPubSubEngine'):
                from umlshapes.sd.eventhandlers.UmlSDExecutionEventHandler import UmlSDExecutionEventHandler

                eventHandler: UmlSDExecutionEventHandler = UmlSDExecutionEventHandler(
                    umlSDExecution=self,
                    umlPubSubEngine=umlFrame.umlPubSubEngine,
                    previousEventHandler=self.GetEventHandler()
                )
                self.SetEventHandler(eventHandler)

    @property
    def lifeLine(self) -> 'UmlSDLifeLine':
        return self._lifeLine

    @property
    def sdExecution(self) -> SDExecution:
        return self._sdExecution

    @sdExecution.setter
    def sdExecution(self, sdExecution: SDExecution):

        self._sdExecution = sdExecution
        if self._sdExecution.endTime - self._sdExecution.startTime < self._preferences.timeStepHeight:
            self._sdExecution.endTime = self._sdExecution.startTime + self._preferences.timeStepHeight

        self.recomputeGeometry()

    @property
    def startY(self) -> int:
        return self._sdExecution.startTime

    @startY.setter
    def startY(self, newStartY: int):
        self._sdExecution.startTime = newStartY
        if self._sdExecution.endTime - self._sdExecution.startTime < self._preferences.timeStepHeight:
            self._sdExecution.endTime = self._sdExecution.startTime + self._preferences.timeStepHeight
        self.recomputeGeometry()

    @property
    def endY(self) -> int:
        return self._sdExecution.endTime

    @endY.setter
    def endY(self, newEndY: int):
        self._sdExecution.endTime = max(self._sdExecution.startTime + self._preferences.timeStepHeight, newEndY)
        self.recomputeGeometry()

    @property
    def nestingLevel(self) -> int:
        return self._sdExecution.nestingLevel

    @nestingLevel.setter
    def nestingLevel(self, newLevel: int):

        self._sdExecution.nestingLevel = newLevel
        self.recomputeGeometry()

    def recomputeGeometry(self):
        """
        Recompute center X, center Y, width, and height based on lifeline position
        and nesting offset, updating the underlying OGL shape geometry.
        """
        lifeLineX: int = round(self._lifeLine.GetX())
        centerX:   int
        centerY:   int
        width:     int
        height:    int

        centerX, centerY, width, height = self._layoutEngine.computeExecutionBounds(
            lifeLineX=lifeLineX,
            startY=self._sdExecution.startTime,
            endY=self._sdExecution.endTime,
            nestingLevel=self._sdExecution.nestingLevel
        )

        self.SetX(centerX)
        self.SetY(centerY)
        self.SetSize(width, height)

    def MakeControlPoints(self):
        """
        Create top and bottom vertical sizing handles for adjusting execution duration.
        """
        from umlshapes.frames.UmlFrame import UmlFrame

        self._controlPoints = []

        halfHeight: float = self.GetHeight() / 2.0
        centerX: float = self.GetX()
        centerY: float = self.GetY()

        umlFrame: 'UmlFrame' = cast('UmlFrame', self.GetCanvas())
        umlControlPointSize: int = self._preferences.controlPointSize

        topControlPoint: UmlControlPoint = UmlControlPoint(
            umlFrame=umlFrame,
            shape=self,
            size=umlControlPointSize,
            xOffSet=0.0,
            yOffSet=-halfHeight,
            controlPointType=CONTROL_POINT_VERTICAL
        )
        topControlPoint.SetX(centerX)
        topControlPoint.SetY(centerY - halfHeight)
        topControlPoint.SetParent(self)
        self.GetChildren().append(topControlPoint)
        umlFrame.AddShape(topControlPoint)
        self._controlPoints.append(topControlPoint)
        self._addEventHandler(umlControlPoint=topControlPoint)

        bottomControlPoint: UmlControlPoint = UmlControlPoint(
            umlFrame=umlFrame,
            shape=self,
            size=umlControlPointSize,
            xOffSet=0.0,
            yOffSet=halfHeight,
            controlPointType=CONTROL_POINT_VERTICAL
        )
        bottomControlPoint.SetX(centerX)
        bottomControlPoint.SetY(centerY + halfHeight)
        bottomControlPoint.SetParent(self)
        self.GetChildren().append(bottomControlPoint)
        umlFrame.AddShape(bottomControlPoint)
        self._controlPoints.append(bottomControlPoint)
        self._addEventHandler(umlControlPoint=bottomControlPoint)

    def GetControlPoints(self) -> list['ControlPoint']:
        return self._controlPoints

    def ResetControlPoints(self, _dc: Optional[MemoryDC] = None):
        """
        Reposition control points to current top and bottom bounds.
        """
        if len(self._controlPoints) >= 2:
            halfHeight: float = self.GetHeight() / 2.0
            centerX: float = self.GetX()
            centerY: float = self.GetY()

            topControlPoint: UmlControlPoint = cast(UmlControlPoint, self._controlPoints[EXECUTION_TOP_HANDLE_INDEX])
            topControlPoint.xOffset = 0.0
            topControlPoint.yOffset = -halfHeight
            topControlPoint.SetX(centerX)
            topControlPoint.SetY(centerY - halfHeight)

            bottomControlPoint: UmlControlPoint = cast(UmlControlPoint, self._controlPoints[EXECUTION_BOTTOM_HANDLE_INDEX])
            bottomControlPoint.xOffset = 0.0
            bottomControlPoint.yOffset = halfHeight
            bottomControlPoint.SetX(centerX)
            bottomControlPoint.SetY(centerY + halfHeight)

    def HitTest(self, x: float, y: float) -> tuple[int, float] | bool:
        """
        Hit test providing exact execution box coverage with comfortable padding.
        """
        halfWidth: float = (self.GetWidth() / 2.0) + HIT_TEST_TOLERANCE
        halfHeight: float = self.GetHeight() / 2.0

        left: float = self.GetX() - halfWidth
        right: float = self.GetX() + halfWidth
        top: float = self.GetY() - halfHeight
        bottom: float = self.GetY() + halfHeight

        if (left <= x <= right) and (top <= y <= bottom):
            return 0, abs(x - self.GetX())
        return False

    def OnDraw(self, dc: MemoryDC):
        """
        Draw the execution specification bar with a white opaque fill to occlude the
        underlying dashed lifeline, highlighting in red dashed pen when selected.
        """
        if self.AncestorSelected() is True or self.Selected() is True:
            self.SetPen(ResourceUtils.redDashedPen())
        else:
            self.SetPen(ResourceUtils.blackSolidPen())

        self.SetBrush(ResourceUtils.backGroundBrush())
        super().OnDraw(dc)

    def __str__(self) -> str:
        return f'UmlSDExecution(id={self.id}, modelId={self._sdExecution.id}, startY={self.startY}, endY={self.endY}, nestingLevel={self.nestingLevel})'

    def __repr__(self) -> str:
        return self.__str__()
