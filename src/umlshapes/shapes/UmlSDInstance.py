
from logging import Logger
from logging import getLogger
from typing import TYPE_CHECKING

from umlmodel.SDInstance import SDInstance

from umlshapes.lib.ogl import CONSTRAINT_ALIGNED_TOP
from umlshapes.lib.ogl import CompositeShape
from umlshapes.lib.ogl import Constraint

from umlshapes.UmlUtils import UmlUtils

from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.UmlDimensions import UmlDimensions

from umlshapes.shapes.SDInstanceContainer import SDInstanceContainer
from umlshapes.shapes.UmlInstanceName import UmlInstanceName


if TYPE_CHECKING:
    from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame


class UmlSDInstance(CompositeShape, TopLeftMixin):

    def __init__(self, sdInstance: SDInstance, diagramFrame: 'SequenceDiagramFrame'):

        self._sdInstance:   SDInstance     = sdInstance
        self._preferences:  UmlPreferences = UmlPreferences()
        instanceDimensions: UmlDimensions  = self._preferences.instanceDimensions

        super().__init__()
        TopLeftMixin.__init__(self, umlShape=self, width=instanceDimensions.width, height=instanceDimensions.height)

        self.SetCanvas(diagramFrame)

        self.logger:        Logger         = getLogger(__name__)

        constrainingShape: SDInstanceContainer = SDInstanceContainer(diagramFrame)
        instanceName:      UmlInstanceName     = UmlInstanceName(sdInstance=sdInstance)

        instanceName.SetPen(UmlUtils.blackSolidPen())
        instanceName.SetTextColour('Black')

        self.AddChild(constrainingShape)
        self.AddChild(instanceName)

        constraint: Constraint = Constraint(CONSTRAINT_ALIGNED_TOP, constrainingShape, [instanceName])
        self.AddConstraint(constraint)
        self.Recompute()

        # If we don't do this, the shapes will be able to move on their
        # own, instead of moving the composite
        constrainingShape.SetDraggable(False)
        instanceName.SetDraggable(False)

        # If we don't do this the shape will take all left-clicks for itself
        constrainingShape.SetSensitivityFilter(0)

    @property
    def umlFrame(self) -> 'SequenceDiagramFrame':
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: 'SequenceDiagramFrame'):
        self.SetCanvas(frame)
