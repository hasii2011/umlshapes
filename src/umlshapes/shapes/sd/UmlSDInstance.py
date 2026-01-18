
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from umlmodel.SDInstance import SDInstance

from umlshapes.lib.ogl import CONSTRAINT_ALIGNED_TOP
from umlshapes.lib.ogl import CompositeShape
from umlshapes.lib.ogl import Constraint

from umlshapes.UmlUtils import UmlUtils

from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.types.UmlDimensions import UmlDimensions

from umlshapes.shapes.sd.UmlInstanceNameEventHandler import UmlInstanceNameEventHandler
from umlshapes.shapes.sd.UmlSDLifeLineEventHandler import UmlSDLifeLineEventHandler

from umlshapes.shapes.sd.SDInstanceConstrainer import SDInstanceConstrainer
from umlshapes.shapes.sd.UmlInstanceName import UmlInstanceName
from umlshapes.shapes.sd.UmlSDLifeLine import UmlSDLifeLine


if TYPE_CHECKING:
    from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame


class UmlSDInstance(CompositeShape, TopLeftMixin):

    def __init__(self, sdInstance: SDInstance, diagramFrame: 'SequenceDiagramFrame', umlPubSubEngine: IUmlPubSubEngine):

        self._sdInstance:      SDInstance       = sdInstance
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine
        self._preferences:     UmlPreferences   = UmlPreferences()

        instanceDimensions: UmlDimensions  = self._preferences.instanceDimensions

        super().__init__()
        TopLeftMixin.__init__(self, umlShape=self, width=instanceDimensions.width, height=instanceDimensions.height)

        self.SetCanvas(diagramFrame)

        self.logger:        Logger         = getLogger(__name__)

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

    @property
    def umlFrame(self) -> 'SequenceDiagramFrame':
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: 'SequenceDiagramFrame'):
        self.SetCanvas(frame)

    def connectInstanceNameToBottomOfContainer(self):

        instanceNameHeight: int = self._instanceName.GetHeight()
        self.logger.debug(f'{instanceNameHeight=}')

        startX: int = round(self._instanceName.GetX())
        startY: int = round(self._instanceName.GetY() + (instanceNameHeight // 2))
        self.logger.debug(f'x2y2: ({startX},{startY})')

        constrainerHeight: int = self._constrainingShape.GetHeight()
        endX: int = round(self._constrainingShape.GetX())
        endY: int = round(self._constrainingShape.GetY() + (constrainerHeight // 2))
        self.logger.debug(f'x1y1: ({endX},{endY})')

        self._lifeLine.SetEnds(
            x1=startX,
            y1=startY,
            x2=endX,
            y2=endY
        )

        self.logger.debug(f'------------------')

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
