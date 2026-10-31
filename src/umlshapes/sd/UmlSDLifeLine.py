from typing import Optional
from typing import TYPE_CHECKING
from typing import cast

from logging import Logger
from logging import getLogger

from wx import MemoryDC
from wx import ClientDC

from umlmodel.SDInstance import SDInstance

from umlshapes.lib.ogl import RectangleShape

from umlshapes.utils.ResourceUtils import ResourceUtils

from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

from umlshapes.mixins.IdentifierMixin import IdentifierMixin
from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.sd.SDInstanceConstrainer import SDInstanceConstrainer
from umlshapes.sd.UmlSDExecution import UmlSDExecution
from umlshapes.sd.UmlInstanceName import UmlInstanceName
from umlshapes.sd.UmlSDMessage import UmlSDMessage
from umlshapes.sd.UmlSDMessage import UmlSDMessages

if TYPE_CHECKING:
    from umlshapes.sd.UmlSDInstance import UmlSDInstance

HIT_TEST_TOLERANCE: int = 15


class UmlSDLifeLine(IdentifierMixin, RectangleShape, TopLeftMixin):

    def __init__(self, instanceName: UmlInstanceName, instanceConstrainer: SDInstanceConstrainer):

        self.logger:       Logger         = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()

        width:  int = 1
        height: int = self._preferences.initialLifeLineLength

        IdentifierMixin.__init__(self)
        RectangleShape.__init__(self, w=width, h=height)
        TopLeftMixin.__init__(self, umlShape=self, width=width, height=height)

        self._umlInstanceName:     UmlInstanceName           = instanceName
        self._instanceConstrainer: SDInstanceConstrainer     = instanceConstrainer
        self._umlSDInstance:       Optional['UmlSDInstance'] = None
        self._executions:          list[UmlSDExecution]      = []

    @property
    def umlFrame(self) -> SequenceDiagramFrame:
        return self.GetCanvas()

    @property
    def umlInstanceName(self) -> UmlInstanceName:
        return self._umlInstanceName

    @property
    def sdInstance(self) -> SDInstance:
        return self._umlInstanceName.sdInstance

    @property
    def instanceConstrainer(self) -> SDInstanceConstrainer:
        return self._instanceConstrainer

    @property
    def umlSDInstance(self) -> 'UmlSDInstance':
        return cast('UmlSDInstance', self._umlSDInstance)

    @umlSDInstance.setter
    def umlSDInstance(self, instance: 'UmlSDInstance'):
        self._umlSDInstance = instance

    @property
    def messages(self) -> UmlSDMessages:
        return cast(UmlSDMessages, self._lines)

    @property
    def executions(self) -> list[UmlSDExecution]:
        return self._executions

    def HitTest(self, x: float, y: float) -> tuple[int, float] | bool:
        """
        Hit test for lifeline providing a comfortable click band (+/- 15px).
        """
        centerX: float = self.GetX()
        centerY: float = self.GetY()
        halfHeight: float = self.GetHeight() / 2.0

        top: float = centerY - halfHeight
        bottom: float = centerY + halfHeight

        if (abs(x - centerX) <= HIT_TEST_TOLERANCE) and (top <= y <= bottom):
            return 0, abs(x - centerX)

        return False

    def OnDraw(self, dc: MemoryDC):
        lineX: int = round(self.GetX())
        halfHeight: float = self.GetHeight() / 2.0
        topY: int = round(self.GetY() - halfHeight)
        bottomY: int = round(self.GetY() + halfHeight)

        if self.AncestorSelected() is True:
            dc.SetPen(ResourceUtils.redDashedPen())
        else:
            dc.SetPen(ResourceUtils.blackDashedPen())

        dc.DrawLine(lineX, topY, lineX, bottomY)

        for execution in self._executions:
            execution.OnDraw(dc)

    def addExecution(self, execution: UmlSDExecution):
        if execution not in self._executions:
            self._executions.append(execution)
            self._recalculateNestingLevels()
            self.recomputeExecutionsGeometry()

            diagramFrame: SequenceDiagramFrame = self.umlFrame
            if execution not in diagramFrame.umlDiagram.GetShapeList():
                execution.Show(True)
                diagramFrame.umlDiagram.AddShape(execution)

    def removeExecution(self, execution: UmlSDExecution):
        if execution in self._executions:
            self._executions.remove(execution)
            self._recalculateNestingLevels()
            self.recomputeExecutionsGeometry()

            diagramFrame: SequenceDiagramFrame = self.umlFrame
            if execution in diagramFrame.umlDiagram.GetShapeList():
                diagramFrame.umlDiagram.RemoveShape(execution)

    def getExecutionAtY(self, y: int) -> Optional[UmlSDExecution]:
        """
        Return the deepest nested execution bar covering the given Y coordinate, if any.
        """
        matching: list[UmlSDExecution] = []
        for execution in self._executions:
            if execution.startY <= y <= execution.endY:
                matching.append(execution)

        if len(matching) == 0:
            return None

        matching.sort(key=lambda a: a.nestingLevel, reverse=True)
        return matching[0]

    def recalculateNestingLevels(self):
        """
        Public method to sort executions by startY and recalculate nesting levels.
        """
        self._recalculateNestingLevels()

    def recomputeExecutionsGeometry(self):
        """
        Recompute geometry for all execution specification bars attached to this lifeline.
        """
        for execution in self._executions:
            execution.recomputeGeometry()
            execution.ResetControlPoints()

        dc: ClientDC = ClientDC(self.umlFrame)
        self.umlFrame.PrepareDC(dc)
        self.MoveLinks(dc)

    def adjustLifeLineTopPosition(self):

        self.logger.debug(f'------------------')

        umlInstanceName: UmlInstanceName = self._umlInstanceName
        instanceNameHeight: int = umlInstanceName.GetHeight()
        instanceNameWidth:  int = umlInstanceName.GetWidth()
        centerX:            int = umlInstanceName.GetX()
        centerY:            int = umlInstanceName.GetY()
        self.logger.debug(f'{instanceNameHeight=} {instanceNameWidth=} {centerX=} {centerY=}')

        instanceNameBottomY: int = centerY + (instanceNameHeight // 2)
        self.logger.debug(f'{instanceNameBottomY=}')

        lifeLineTopY: int = instanceNameBottomY + round(self.GetHeight() // 2)

        self.SetY(lifeLineTopY)
        self.logger.debug(f'------------------')

    def addMessage(self, umlSDMessage: UmlSDMessage, destinationLifeLine: Optional['UmlSDLifeLine'] = None):
        """
        Add a message linked to this lifeline.

        Args:
            umlSDMessage:        The message shape
            destinationLifeLine: The target lifeline for directed messages (None for lost/found messages)
        """
        if umlSDMessage.isFoundMessage:
            if umlSDMessage not in self._lines:
                self._lines.append(umlSDMessage)
            umlSDMessage.SetFrom(None)
            umlSDMessage.SetTo(self)
        elif umlSDMessage.isLostMessage or destinationLifeLine is None:
            if umlSDMessage not in self._lines:
                self._lines.append(umlSDMessage)
            umlSDMessage.SetFrom(self)
            umlSDMessage.SetTo(None)
        else:
            self.AddLine(line=umlSDMessage, other=destinationLifeLine)

    def _recalculateNestingLevels(self):
        """
        Sort executions by startY and recalculate nesting levels for overlapping intervals.
        """
        sortedActivations: list[UmlSDExecution] = sorted(self._executions, key=lambda a: a.startY)
        activeLevels: list[int] = []

        for execution in sortedActivations:
            placedLevel: Optional[int] = None
            for levelIdx, endY in enumerate(activeLevels):
                if endY <= execution.startY:
                    activeLevels[levelIdx] = execution.endY
                    placedLevel = levelIdx
                    break

            if placedLevel is None:
                placedLevel = len(activeLevels)
                activeLevels.append(execution.endY)

            execution.nestingLevel = placedLevel

    def __str__(self) -> str:
        return f'UmlSDLifeLine: {self.id}'

    def __repr__(self) -> str:
        return self.__str__()
