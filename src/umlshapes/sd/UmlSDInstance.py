
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import CallAfter as wxCallAfter

from umlmodel.SDInstance import SDInstance

from umlshapes.lib.ogl import CompositeShape
from umlshapes.lib.ogl import Constraint
from umlshapes.lib.ogl import CONSTRAINT_ALIGNED_TOP

from umlshapes.UmlUtils import UmlUtils

from umlshapes.mixins.ControlPointMixin import ControlPointMixin
from umlshapes.mixins.IdentifierMixin import IdentifierMixin
from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.UmlDimensions import UmlDimensions

from umlshapes.sd.SDInstanceConstrainer import SDInstanceConstrainer
from umlshapes.sd.UmlInstanceName import UmlInstanceName
from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine


if TYPE_CHECKING:
    from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

OP_NONE: int = 0    # None of OP_CLICK_LEFT, OP_CLICK_RIGHT, OP_DRAG_LEFT, OP_DRAG_RIGHT

class UmlSDInstance(ControlPointMixin, IdentifierMixin, CompositeShape, TopLeftMixin):

    def __init__(self, sdInstance: SDInstance, diagramFrame: 'SequenceDiagramFrame'):

        self._sdInstance:   SDInstance     = sdInstance
        self._preferences:  UmlPreferences = UmlPreferences()
        instanceDimensions: UmlDimensions  = self._preferences.instanceDimensions

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

        instanceName.SetPen(UmlUtils.blackSolidPen())
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
        constrainingShape.SetSensitivityFilter(OP_NONE, recursive=True)
        self.SetCentreResize(False)

        wxCallAfter(sdLifeLine.adjustLifeLineTopPosition)

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
