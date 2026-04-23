
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import CallAfter as wxCallAfter

from umlmodel.SDInstance import SDInstance

from umlshapes.lib.ogl import CompositeShape
from umlshapes.lib.ogl import Constraint
from umlshapes.lib.ogl import CONSTRAINT_ALIGNED_TOP

from umlshapes.ResourceUtils import ResourceUtils

from umlshapes.mixins.ControlPointMixin import ControlPointMixin
from umlshapes.mixins.IdentifierMixin import IdentifierMixin
from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.sd.eventhandlers.UmlSDLifeLineEventHandler import UmlSDLifeLineEventHandler

from umlshapes.types.UmlDimensions import UmlDimensions

from umlshapes.sd.SDInstanceConstrainer import SDInstanceConstrainer
from umlshapes.sd.UmlInstanceName import UmlInstanceName
from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine


if TYPE_CHECKING:
    from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

OP_NONE: int = 0    # None of OP_CLICK_LEFT, OP_CLICK_RIGHT, OP_DRAG_LEFT, OP_DRAG_RIGHT

class UmlSDInstance(ControlPointMixin, IdentifierMixin, CompositeShape, TopLeftMixin):

    def __init__(self, sdInstance: SDInstance, diagramFrame: 'SequenceDiagramFrame', umlPubSubEngine: IUmlPubSubEngine):

        self._preferences:  UmlPreferences = UmlPreferences()

        self._sdInstance:      SDInstance       = sdInstance
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        instanceDimensions: UmlDimensions = self._preferences.instanceDimensions

        ControlPointMixin.__init__(self, shape=self)
        IdentifierMixin.__init__(self)
        CompositeShape.__init__(self)
        TopLeftMixin.__init__(self, umlShape=self, width=instanceDimensions.width, height=instanceDimensions.height)

        self.SetCanvas(diagramFrame)

        self.logger: Logger = getLogger(__name__)

        constrainingShape: SDInstanceConstrainer = SDInstanceConstrainer(diagramFrame)
        instanceName:      UmlInstanceName       = UmlInstanceName(sdInstance=sdInstance)
        sdLifeLine:        UmlSDLifeLine         = UmlSDLifeLine(
            instanceConstrainer=constrainingShape,
            instanceName=instanceName,
            sequenceDiagramFrame=diagramFrame
        )

        instanceName.SetPen(ResourceUtils.blackSolidPen())
        instanceName.SetTextColour('Black')

        self.AddChild(constrainingShape)
        self.AddChild(instanceName)
        self.AddChild(sdLifeLine)

        constraint: Constraint = Constraint(CONSTRAINT_ALIGNED_TOP, constrainingShape, [instanceName, sdLifeLine])
        self.AddConstraint(constraint)
        self.Recompute()

        # If we don't do this, the shapes will be able to move on their
        # own, instead of moving the composite
        constrainingShape.SetDraggable(False)
        instanceName.SetDraggable(False)
        sdLifeLine.SetDraggable(False)

        # If we don't do this the shape will take all left-clicks for itself
        constrainingShape.SetSensitivityFilter(OP_NONE)
        self.SetCentreResize(False)

        wxCallAfter(sdLifeLine.adjustLifeLineTopPosition)

        self._setEventHandlers(umlSDLifeLine=sdLifeLine)
        self._umlSDLifeLine: UmlSDLifeLine = sdLifeLine

    @property
    def umlFrame(self) -> 'SequenceDiagramFrame':
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: 'SequenceDiagramFrame'):
        self.SetCanvas(frame)

    @property
    def umlSDLifeLine(self) -> UmlSDLifeLine:
        return self._umlSDLifeLine

    def _setEventHandlers(self, umlSDLifeLine: UmlSDLifeLine):
        """
        Set the event handlers for the constrained shapes

        Args:
            umlSDLifeLine:

        """

        eventHandler: UmlSDLifeLineEventHandler = UmlSDLifeLineEventHandler(
            umlSDLifeLine=umlSDLifeLine,
            umlPubSubEngine=self._umlPubSubEngine,
            previousEventHandler=umlSDLifeLine.GetEventHandler()
        )
        umlSDLifeLine.SetEventHandler(eventHandler)

    def __str__(self) -> str:
        return f'UmlSDInstance: `{self.id}` {self._sdInstance.instanceName}'

    def __repr__(self) -> str:
        return self.__str__()
