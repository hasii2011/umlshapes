
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from umlmodel.SDInstance import SDInstance

from umlshapes.lib.ogl import CompositeShape
from umlshapes.lib.ogl import Constraint
from umlshapes.lib.ogl import ControlPoint
from umlshapes.lib.ogl import CONSTRAINT_ALIGNED_TOP
from umlshapes.lib.ogl import CONSTRAINT_BELOW
from umlshapes.lib.ogl import CONSTRAINT_CENTRED_HORIZONTALLY
from umlshapes.lib.ogl import CONTROL_POINT_VERTICAL

from umlshapes.utils.ResourceUtils import ResourceUtils

from umlshapes.mixins.ControlPointMixin import ControlPointMixin
from umlshapes.mixins.IdentifierMixin import IdentifierMixin
from umlshapes.mixins.TopLeftMixin import TopLeftMixin

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.sd.eventhandlers.UmlSDLifeLineEventHandler import UmlSDLifeLineEventHandler
from umlshapes.shapes.UmlControlPoint import UmlControlPoint

from umlshapes.types.UmlDimensions import UmlDimensions

from umlshapes.sd.SDInstanceConstrainer import SDInstanceConstrainer
from umlshapes.sd.UmlInstanceName import UmlInstanceName
from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine

if TYPE_CHECKING:
    from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame
    from umlshapes.frames.UmlFrame import UmlFrame

OP_NONE:             int = 0    # None of OP_CLICK_LEFT, OP_CLICK_RIGHT, OP_DRAG_LEFT, OP_DRAG_RIGHT
MIN_LIFELINE_LENGTH: int = 80


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

        topConstraint:            Constraint = Constraint(CONSTRAINT_ALIGNED_TOP, constrainingShape, [instanceName])
        centerNameConstraint:     Constraint = Constraint(CONSTRAINT_CENTRED_HORIZONTALLY, constrainingShape, [instanceName])
        centerLifeLineConstraint: Constraint = Constraint(CONSTRAINT_CENTRED_HORIZONTALLY, constrainingShape, [sdLifeLine])
        belowConstraint:          Constraint = Constraint(CONSTRAINT_BELOW, instanceName, [sdLifeLine])

        self.AddConstraint(topConstraint)
        self.AddConstraint(centerNameConstraint)
        self.AddConstraint(centerLifeLineConstraint)
        self.AddConstraint(belowConstraint)
        self.Recompute()

        # If we don't do this, the shapes will be able to move on their
        # own, instead of moving the composite
        constrainingShape.SetDraggable(False)
        instanceName.SetDraggable(False)
        sdLifeLine.SetDraggable(False)

        # If we don't do this the shape will take all left-clicks for itself
        constrainingShape.SetSensitivityFilter(OP_NONE)
        self.SetCentreResize(False)

        self._setEventHandlers(umlSDLifeLine=sdLifeLine)
        self._constrainingShape: SDInstanceConstrainer = constrainingShape
        self._instanceName:      UmlInstanceName       = instanceName
        self._umlSDLifeLine:     UmlSDLifeLine         = sdLifeLine

        sdLifeLine.umlSDInstance = self

    @property
    def umlFrame(self) -> 'SequenceDiagramFrame':
        return self.GetCanvas()

    @umlFrame.setter
    def umlFrame(self, frame: 'SequenceDiagramFrame'):
        self.SetCanvas(frame)

    @property
    def umlSDLifeLine(self) -> UmlSDLifeLine:
        return self._umlSDLifeLine

    @property
    def constrainingShape(self) -> SDInstanceConstrainer:
        return self._constrainingShape

    @property
    def instanceName(self) -> UmlInstanceName:
        return self._instanceName

    @property
    def controlPoints(self) -> list[ControlPoint]:
        return self._controlPoints

    def getLifeLineLength(self) -> int:
        return round(self._umlSDLifeLine.GetHeight())

    def setLifeLineLength(self, newLength: int):
        targetLength: int
        if newLength < MIN_LIFELINE_LENGTH:
            targetLength = MIN_LIFELINE_LENGTH
        else:
            targetLength = newLength

        instanceNameHeight: int = round(self._instanceName.GetHeight())
        newTotalHeight: int = instanceNameHeight + targetLength

        instanceTopY: float = self._instanceName.GetY() - (instanceNameHeight / 2.0)

        self._umlSDLifeLine.SetSize(1, targetLength)
        self._umlSDLifeLine.size = UmlDimensions(width=1, height=targetLength)

        constrainingWidth: float = self._constrainingShape.GetWidth()
        self._constrainingShape.SetSize(constrainingWidth, newTotalHeight)
        self._constrainingShape.size = UmlDimensions(width=round(constrainingWidth), height=newTotalHeight)
        self._constrainingShape.SetY(instanceTopY + (newTotalHeight / 2.0))

        self.Recompute()
        self.ResetControlPoints()

    def CalculateSize(self):
        maxX: float = -999999.9
        maxY: float = -999999.9
        minX: float = 999999.9
        minY: float = 999999.9

        for child in self._children:
            if isinstance(child, ControlPoint):
                continue
            if isinstance(child, CompositeShape):
                child.CalculateSize()

            w, h = child.GetBoundingBoxMax()
            childX: float = child.GetX()
            childY: float = child.GetY()
            if childX + w / 2.0 > maxX:
                maxX = childX + w / 2.0
            if childX - w / 2.0 < minX:
                minX = childX - w / 2.0
            if childY + h / 2.0 > maxY:
                maxY = childY + h / 2.0
            if childY - h / 2.0 < minY:
                minY = childY - h / 2.0

        self._width = maxX - minX
        self._height = maxY - minY
        self._xpos = self._width / 2.0 + minX
        self._ypos = self._height / 2.0 + minY

    def MakeControlPoints(self):
        from umlshapes.frames.UmlFrame import UmlFrame

        canvas: UmlFrame = self.GetCanvas()
        umlControlPointSize: int = self._preferences.controlPointSize

        yOffset: float = self._umlSDLifeLine.GetY() + (self._umlSDLifeLine.GetHeight() / 2.0) - self.GetY()
        control: UmlControlPoint = UmlControlPoint(
            umlFrame=canvas,
            shape=self,
            size=umlControlPointSize,
            xOffSet=0.0,
            yOffSet=yOffset,
            controlPointType=CONTROL_POINT_VERTICAL
        )
        control.SetParent(self)
        self.GetChildren().append(control)
        self.GetCanvas().AddShape(control)
        self._controlPoints.append(control)
        self._addEventHandler(umlControlPoint=control)

    def ResetControlPoints(self):
        self.ResetMandatoryControlPoints()
        if len(self._controlPoints) == 0:
            return
        yOffset: float = self._umlSDLifeLine.GetY() + (self._umlSDLifeLine.GetHeight() / 2.0) - self.GetY()
        self._controlPoints[0]._xoffset = 0.0
        self._controlPoints[0]._yoffset = yOffset

    def DeleteControlPoints(self, dc = None):
        super().DeleteControlPoints(dc)

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
