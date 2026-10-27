from typing import cast
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
from umlshapes.lib.ogl import CONTROL_POINT_HORIZONTAL
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

HANDLE_LIFELINE_BOTTOM:   int = 0
HANDLE_NAME_MIDDLE_LEFT:  int = 1
HANDLE_NAME_MIDDLE_RIGHT: int = 2


class UmlSDInstance(ControlPointMixin, IdentifierMixin, CompositeShape, TopLeftMixin):

    def __init__(self, sdInstance: SDInstance, diagramFrame: 'SequenceDiagramFrame', umlPubSubEngine: IUmlPubSubEngine):

        self._preferences:  UmlPreferences = UmlPreferences()

        self._sdInstance:      SDInstance       = sdInstance
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        instanceDimensions: UmlDimensions = self._preferences.instanceDimensions

        instanceName:      UmlInstanceName       = UmlInstanceName(sdInstance=sdInstance)
        initialWidth:      int                   = round(instanceName.GetWidth())
        constrainingShape: SDInstanceConstrainer = SDInstanceConstrainer(
            diagramFrame=diagramFrame,
            width=initialWidth
        )
        sdLifeLine:        UmlSDLifeLine         = UmlSDLifeLine(
            instanceConstrainer=constrainingShape,
            instanceName=instanceName,
            sequenceDiagramFrame=diagramFrame
        )

        ControlPointMixin.__init__(self, shape=self)
        IdentifierMixin.__init__(self)
        CompositeShape.__init__(self)
        TopLeftMixin.__init__(self, umlShape=self, width=initialWidth, height=instanceDimensions.height)

        self.SetCanvas(diagramFrame)

        self.logger: Logger = getLogger(__name__)

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

        self._setEventHandlers(instanceName=instanceName, umlSDLifeLine=sdLifeLine)
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

    @property
    def instanceWidth(self) -> int:
        return self._instanceName.width

    @instanceWidth.setter
    def instanceWidth(self, newWidth: int):
        from umlshapes.preferences.Defaults import MIN_INSTANCE_WIDTH

        targetWidth: int
        if newWidth < MIN_INSTANCE_WIDTH:
            targetWidth = MIN_INSTANCE_WIDTH
        else:
            targetWidth = round(newWidth)

        self._instanceName.width = targetWidth

        constrainingHeight: int = round(self._constrainingShape.GetHeight())
        self._constrainingShape.size = UmlDimensions(width=targetWidth, height=constrainingHeight)

        self.Recompute()
        self.ResetControlPoints()
        self._umlSDLifeLine.recomputeExecutionsGeometry()

    def getInstanceWidth(self) -> int:
        return self.instanceWidth

    def setInstanceWidth(self, newWidth: int):
        self.instanceWidth = newWidth

    def reFitWidth(self):
        """
        Re-compute and apply the auto-fitted width based on the current instance name.
        """
        autoFitWidth: int = self._instanceName.computeAutoFitWidth(text=self._sdInstance.instanceName)
        self.instanceWidth = autoFitWidth

    def setLifeLineLength(self, newLength: int):
        targetLength: int
        if newLength < MIN_LIFELINE_LENGTH:
            targetLength = MIN_LIFELINE_LENGTH
        else:
            targetLength = round(newLength)

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
        self._umlSDLifeLine.recomputeExecutionsGeometry()

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

        umlFrame: UmlFrame = self.GetCanvas()
        umlControlPointSize: int = self._preferences.controlPointSize

        compositeCenterX: float = self.GetX()
        compositeCenterY: float = self.GetY()

        # Handle 0: Lifeline Bottom
        lifelineBottomY: float = self._umlSDLifeLine.GetY() + (self._umlSDLifeLine.GetHeight() / 2.0)
        yOffsetBottom:   float = lifelineBottomY - compositeCenterY
        bottomControl:   UmlControlPoint = UmlControlPoint(
            umlFrame=umlFrame,
            shape=self,
            size=umlControlPointSize,
            xOffSet=0.0,
            yOffSet=yOffsetBottom,
            controlPointType=CONTROL_POINT_VERTICAL
        )
        bottomControl.SetX(compositeCenterX)
        bottomControl.SetY(compositeCenterY + yOffsetBottom)
        bottomControl.SetParent(self)
        self.GetChildren().append(bottomControl)
        self.GetCanvas().AddShape(bottomControl)
        self._controlPoints.append(bottomControl)
        self._addEventHandler(umlControlPoint=bottomControl)

        if not self._preferences.autoFitInstanceWidth:
            # Handle 1: Name Middle-Left
            nameLeftX:   float = self._instanceName.GetX() - (self._instanceName.GetWidth() / 2.0)
            xOffsetLeft: float = nameLeftX - compositeCenterX
            yOffsetName: float = self._instanceName.GetY() - compositeCenterY
            leftControl: UmlControlPoint = UmlControlPoint(
                umlFrame=umlFrame,
                shape=self,
                size=umlControlPointSize,
                xOffSet=xOffsetLeft,
                yOffSet=yOffsetName,
                controlPointType=CONTROL_POINT_HORIZONTAL
            )
            leftControl.SetX(compositeCenterX + xOffsetLeft)
            leftControl.SetY(compositeCenterY + yOffsetName)
            leftControl.SetParent(self)
            self.GetChildren().append(leftControl)
            self.GetCanvas().AddShape(leftControl)
            self._controlPoints.append(leftControl)
            self._addEventHandler(umlControlPoint=leftControl)

            # Handle 2: Name Middle-Right
            nameRightX:   float = self._instanceName.GetX() + (self._instanceName.GetWidth() / 2.0)
            xOffsetRight: float = nameRightX - compositeCenterX
            rightControl: UmlControlPoint = UmlControlPoint(
                umlFrame=umlFrame,
                shape=self,
                size=umlControlPointSize,
                xOffSet=xOffsetRight,
                yOffSet=yOffsetName,
                controlPointType=CONTROL_POINT_HORIZONTAL
            )
            rightControl.SetX(compositeCenterX + xOffsetRight)
            rightControl.SetY(compositeCenterY + yOffsetName)
            rightControl.SetParent(self)
            self.GetChildren().append(rightControl)
            self.GetCanvas().AddShape(rightControl)
            self._controlPoints.append(rightControl)
            self._addEventHandler(umlControlPoint=rightControl)

    def ResetControlPoints(self):

        self.ResetMandatoryControlPoints()
        if len(self._controlPoints) == 0:
            return

        compositeCenterX: float = self.GetX()
        compositeCenterY: float = self.GetY()

        # Handle 0: Lifeline Bottom
        lifelineBottomY: float = self._umlSDLifeLine.GetY() + (self._umlSDLifeLine.GetHeight() / 2.0)
        yOffsetBottom:   float = lifelineBottomY - compositeCenterY
        bottomControl:   UmlControlPoint = cast(UmlControlPoint, self._controlPoints[HANDLE_LIFELINE_BOTTOM])
        bottomControl.xOffset = 0.0
        bottomControl.yOffset = yOffsetBottom
        bottomControl.SetX(compositeCenterX)
        bottomControl.SetY(compositeCenterY + yOffsetBottom)

        if len(self._controlPoints) >= 3:
            # Handle 1: Name Middle-Left
            nameLeftX:   float = self._instanceName.GetX() - (self._instanceName.GetWidth() / 2.0)
            xOffsetLeft: float = nameLeftX - compositeCenterX
            yOffsetName: float = self._instanceName.GetY() - compositeCenterY
            leftControl: UmlControlPoint = cast(UmlControlPoint, self._controlPoints[HANDLE_NAME_MIDDLE_LEFT])
            leftControl.xOffset = xOffsetLeft
            leftControl.yOffset = yOffsetName
            leftControl.SetX(compositeCenterX + xOffsetLeft)
            leftControl.SetY(compositeCenterY + yOffsetName)

            # Handle 2: Name Middle-Right
            nameRightX:   float = self._instanceName.GetX() + (self._instanceName.GetWidth() / 2.0)
            xOffsetRight: float = nameRightX - compositeCenterX
            rightControl: UmlControlPoint = cast(UmlControlPoint, self._controlPoints[HANDLE_NAME_MIDDLE_RIGHT])
            rightControl.xOffset = xOffsetRight
            rightControl.yOffset = yOffsetName
            rightControl.SetX(compositeCenterX + xOffsetRight)
            rightControl.SetY(compositeCenterY + yOffsetName)

        self._umlSDLifeLine.recomputeExecutionsGeometry()

    def DeleteControlPoints(self, dc = None):
        super().DeleteControlPoints(dc)

    def _setEventHandlers(self, instanceName: UmlInstanceName, umlSDLifeLine: UmlSDLifeLine):
        """
        Set the event handlers for the constrained shapes

        Args:
            instanceName:
            umlSDLifeLine:

        """
        from umlshapes.sd.eventhandlers.UmlInstanceNameEventHandler import UmlInstanceNameEventHandler

        nameEventHandler: UmlInstanceNameEventHandler = UmlInstanceNameEventHandler(
            umlInstanceName=instanceName,
            umlSDInstance=self,
            previousEventHandler=instanceName.GetEventHandler()
        )
        instanceName.SetEventHandler(nameEventHandler)

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
