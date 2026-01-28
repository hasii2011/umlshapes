
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from umlmodel.Class import Class
from umlmodel.SDInstance import SDInstance

from umlshapes.lib.ogl import CONSTRAINT_ALIGNED_TOP
from umlshapes.lib.ogl import CompositeShape
from umlshapes.lib.ogl import Constraint

from umlshapes.UmlUtils import UmlUtils

from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.UmlDimensions import UmlDimensions

from umlshapes.sd.eventhandlers.UmlInstanceNameEventHandler import UmlInstanceNameEventHandler
from umlshapes.sd.eventhandlers.UmlSDLifeLineEventHandler import UmlSDLifeLineEventHandler

from umlshapes.sd.SDInstanceConstrainer import SDInstanceConstrainer
from umlshapes.sd.UmlInstanceName import UmlInstanceName
from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine
from umlshapes.types.UmlPosition import UmlPosition

MINIMUM_SD_LIFELINE_X: int = 20
MINIMUM_SD_LIFELINE_Y: int = 20

if TYPE_CHECKING:
    from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

ANONYMOUS: Class = Class(name='Anonymous')


class UmlSDInstance(CompositeShape, TopLeftMixin):

    def __init__(self, sdInstance: SDInstance, diagramFrame: 'SequenceDiagramFrame', umlPubSubEngine: IUmlPubSubEngine):

        self._sdInstance:      SDInstance       = sdInstance
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine
        self._preferences:     UmlPreferences   = UmlPreferences()
        self._modelClass:      Class            = ANONYMOUS

        instanceDimensions: UmlDimensions  = self._preferences.instanceDimensions

        super().__init__()
        TopLeftMixin.__init__(self, umlShape=self, width=instanceDimensions.width, height=instanceDimensions.height)

        self.SetCanvas(diagramFrame)

        self.logger: Logger = getLogger(__name__)

        constrainingShape: SDInstanceConstrainer = SDInstanceConstrainer(diagramFrame)
        instanceName:      UmlInstanceName       = UmlInstanceName(sdInstance=sdInstance, sequenceDiagramFrame=diagramFrame)
        lifeLine:          UmlSDLifeLine         = UmlSDLifeLine(sequenceDiagramFrame=diagramFrame, instanceName=instanceName, instanceConstrainer=constrainingShape)

        self._customizeConstrainedShapes(constrainingShape, instanceName, lifeLine)

        self.AddChild(constrainingShape)
        self.AddChild(instanceName)
        self.AddChild(lifeLine)

        constraint: Constraint = Constraint(CONSTRAINT_ALIGNED_TOP, constrainingShape, [instanceName, lifeLine])
        self.AddConstraint(constraint)
        self.Recompute()

        lifeLine.Show(True)

        # If we don't do this, the shapes will be able to move on their
        # own, instead of moving the composite
        constrainingShape.SetDraggable(False)
        instanceName.SetDraggable(False)
        lifeLine.SetDraggable(False)

        # If we don't do this the shape will take all left-clicks for itself
        constrainingShape.SetSensitivityFilter(0)

        self._setInstanceNameEventHandler(instanceName=instanceName)
        self._setLifeLineEventHandler(lifeLine=lifeLine)

        self._constrainingShape: SDInstanceConstrainer = constrainingShape
        self._instanceName:      UmlInstanceName       = instanceName
        self._lifeLine:          UmlSDLifeLine         = lifeLine

        self._initialMoveOccurred: bool = False
        from wx import CallAfter as wxCallAfter
        wxCallAfter(lifeLine.setLifeLineEnds)

    @property
    def umlFrame(self) -> 'SequenceDiagramFrame':
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: 'SequenceDiagramFrame'):
        self.SetCanvas(frame)

    @property
    def modelClass(self) -> Class:
        return self._modelClass

    @modelClass.setter
    def modelClass(self, modelClass: Class):
        self._modelClass = modelClass

    def Move(self, dc, x: int, y: int, display: bool = True):
        """
        Override Move so we can adjust x & instanceY to be the center of
        the shape

        Args:
            dc:
            x:
            y:
            display:

        """
        instanceY: int = self._preferences.instanceYPosition
        self.logger.debug(f'xy: ({x},{y})  {instanceY=}')

        currentX: int = x
        if self._initialMoveOccurred is True:
            oldX:    int = self.position.x
            deltaX:  int = abs(oldX - x)

            if deltaX > self._preferences.instanceMoveDampener:
                self.logger.debug(f'{oldX=} {deltaX=}')
                if currentX > oldX:
                    self.logger.debug(f'current x {currentX} is greater than old x {oldX}')
                    currentX = oldX + self._preferences.instanceMoveDampener
                else:
                    self.logger.debug(f'current x {currentX} is less than old x {oldX}')
                    currentX = oldX - self._preferences.instanceMoveDampener

        else:
            self._initialMoveOccurred = True

        centerX, centerY = self.computeCenterXY(position=UmlPosition(x=currentX, y=instanceY))

        if centerX <= 0:
            centerX = MINIMUM_SD_LIFELINE_X
        if centerY <= 0:
            centerY = MINIMUM_SD_LIFELINE_Y

        self.logger.debug(f'centerXY=({centerX},{centerY})')

        super().Move(dc=dc, x=centerX, y=centerY, display=display)

    def _customizeConstrainedShapes(self, constrainingShape: SDInstanceConstrainer, instanceName: UmlInstanceName, lifeLine: UmlSDLifeLine):
        """
        Sets appropriate colors and ensure the lifeline is displays
        Args:
            constrainingShape:
            instanceName:
            lifeLine:

        """
        lifeLine.MakeLineControlPoints(n=2)
        lifeLine.SetPen(UmlUtils.blackDashedPen())

        instanceName.SetPen(UmlUtils.blackSolidPen())
        instanceName.SetTextColour('Black')
        instanceName.attachLifeline(umlSDLifeLine=lifeLine, constrainer=constrainingShape)

    def _setInstanceNameEventHandler(self, instanceName: UmlInstanceName):
        """
        Custom event handler for the name shape
        Args:
            instanceName:

        """

        eventHandler: UmlInstanceNameEventHandler = UmlInstanceNameEventHandler(
            umlInstanceName=instanceName,
            sdInstance=self._sdInstance,
            previousEventHandler=instanceName.GetEventHandler()
        )

        instanceName.SetEventHandler(eventHandler)

    def _setLifeLineEventHandler(self, lifeLine: UmlSDLifeLine):
        """
        Custom event handle for the life line

        Args:
            lifeLine:

        """

        eventHandler: UmlSDLifeLineEventHandler = UmlSDLifeLineEventHandler(
            umlSDLifeLine=lifeLine,
            previousEventHandler=lifeLine.GetEventHandler()
        )
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        lifeLine.SetEventHandler(handler=eventHandler)
