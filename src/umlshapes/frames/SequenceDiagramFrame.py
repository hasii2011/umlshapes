
from typing import cast
from typing import Optional
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from wx import ClientDC
from wx import Window

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.types.DeltaXY import DeltaXY
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.frames.UmlFrame import UmlFrame

if TYPE_CHECKING:
    from umlshapes.sd.SDLayoutEngine import SDLayoutEngine
    from umlshapes.sd.UmlSDInstance import UmlSDInstance
    from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine
    from umlshapes.sd.UmlSDMessage import UmlSDMessage


class SequenceDiagramFrame(UmlFrame):
    def __init__(self, parent: Window, umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            parent:
            umlPubSubEngine:
        """
        self.logger: Logger = getLogger(__name__)
        super().__init__(parent=parent, umlPubSubEngine=umlPubSubEngine)

        self.umlDiagram.SetSnapToGrid(False)
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.SHAPE_MOVING,  frameId=self.id, listener=self._shapeMovingListener)

    def _shapeMovingListener(self, deltaXY: DeltaXY):
        self.logger.debug(f'{deltaXY=}')
        self.moveSelectedShapes(deltaXY=deltaXY)

    def moveSelectedShapes(self, deltaXY: DeltaXY):
        """
        Overrides UmlFrame.moveSelectedShapes to move all selected shapes (except
        the move master) on the sequence diagram. Participant instances are
        constrained strictly to horizontal movement, messages shift vertically
        along with their attached execution bars, and combined fragments, notes,
        and text move by both deltaX and deltaY.

        Args:
            deltaXY: The difference between the previous position and the new position.
        """
        from umlshapes.ShapeTypes import UmlShapeGenre
        from umlshapes.links.UmlLink import UmlLink
        from umlshapes.mixins.TopLeftMixin import TopLeftMixin
        from umlshapes.sd.SDLayoutEngine import SDLayoutEngine
        from umlshapes.sd.UmlSDExecution import UmlSDExecution
        from umlshapes.sd.UmlSDInstance import UmlSDInstance
        from umlshapes.sd.UmlSDMessage import UmlSDMessage
        from umlshapes.shapes.UmlBaseLabel import UmlBaseLabel

        self.logger.debug(f'{deltaXY=}')
        shapes = self.selectedShapes

        if self._shapesMoving is False:
            for s in shapes:
                if (
                    isinstance(s, TopLeftMixin) and not isinstance(s, (UmlLink, UmlBaseLabel, UmlSDExecution))
                ):
                    u: UmlShapeGenre = s
                    self.markShapeAsMoved(umlShape=u)
                elif isinstance(s, UmlSDMessage):
                    uSDMessage: UmlShapeGenre = cast(UmlShapeGenre, s)
                    self.markShapeAsMoved(umlShape=uSDMessage)
            self._shapesMoving = True

        dc: ClientDC = ClientDC(self)
        self.PrepareDC(dc)
        layoutEngine: SDLayoutEngine = SDLayoutEngine()

        for s in shapes:
            if (
                isinstance(s, TopLeftMixin)
                and not isinstance(s, (UmlLink, UmlBaseLabel, UmlSDExecution))
            ):
                umlShape: UmlShapeGenre = s
                if umlShape.moveMaster is False:
                    if isinstance(umlShape, UmlSDInstance):
                        umlShape.position = UmlPosition(
                            x=umlShape.position.x + deltaXY.deltaX,
                            y=umlShape.position.y
                        )
                        umlShape.ResetControlPoints()
                    else:
                        umlShape.position = UmlPosition(
                            x=umlShape.position.x + deltaXY.deltaX,
                            y=umlShape.position.y + deltaXY.deltaY
                        )
                        umlShape.ResetControlPoints()
                        umlShape.MoveLinks(dc)
            elif isinstance(s, UmlSDMessage) and deltaXY.deltaY != 0:
                if s.moveMaster is False:
                    self._moveSelectedMessageVertically(
                        umlSDMessage=s,
                        deltaY=deltaXY.deltaY,
                        layoutEngine=layoutEngine,
                        dc=dc
                    )

        self.refresh()

    def _moveSelectedMessageVertically(
        self,
        umlSDMessage: 'UmlSDMessage',
        deltaY: int,
        layoutEngine: 'SDLayoutEngine',
        dc: ClientDC
    ):
        """
        Shift a selected non-master UmlSDMessage vertically by deltaY, respecting
        lifeline bounds or auto-grow preferences.

        Args:
            umlSDMessage: The selected message to shift vertically
            deltaY:       Vertical offset in pixels
            layoutEngine: Sequence diagram layout engine
            dc:           Prepared client device context
        """
        from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine

        span:     int = umlSDMessage.toY - umlSDMessage.fromY
        newFromY: int = umlSDMessage.fromY + deltaY
        newToY:   int = umlSDMessage.toY + deltaY

        referenceLifeLine: Optional[UmlSDLifeLine] = umlSDMessage.GetFrom()
        if referenceLifeLine is None:
            referenceLifeLine = umlSDMessage.GetTo()

        if referenceLifeLine is not None:
            headerBottomY: int = referenceLifeLine.rectangle.top
            minFromY:      int = layoutEngine.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=0)
            if newFromY < minFromY:
                newFromY = minFromY
                newToY   = minFromY + span

            if self._preferences.autoGrowLifeLines:
                neededHeight: int = (newToY - headerBottomY) + layoutEngine.parameters.bottomPadding
                umlSDMessage.growLifeLinesIfNeeded(neededHeight=neededHeight, umlFrame=self)
            else:
                maxTimeStepIndex: int = max(
                    0,
                    (referenceLifeLine.size.height - layoutEngine.parameters.topPadding - layoutEngine.parameters.bottomPadding - span)
                    // layoutEngine.parameters.timeStepHeight
                )
                maxFromY: int = layoutEngine.computeTimeStepY(headerBottomY=headerBottomY, timeStepIndex=maxTimeStepIndex)
                if newFromY > maxFromY:
                    newFromY = maxFromY
                    newToY   = maxFromY + span

        umlSDMessage.setVerticalEndpoints(fromY=newFromY, toY=newToY, dc=dc)

    def getSDInstances(self) -> list['UmlSDInstance']:
        """
        Retrieve all UmlSDInstance shapes currently on this diagram frame.
        """
        from umlshapes.sd.UmlSDInstance import UmlSDInstance

        instances: list[UmlSDInstance] = []
        for shape in self.umlShapes:
            if isinstance(shape, UmlSDInstance):
                instances.append(shape)
        return instances

    def setAllLifeLinesLength(self, length: int):
        """
        Resize all lifelines on this diagram frame to maintain uniform length.

        Args:
            length: The new lifeline length in pixels.
        """
        from umlshapes.sd.UmlSDInstance import UmlSDInstance

        for shape in self.umlShapes:
            if isinstance(shape, UmlSDInstance):
                shape.setLifeLineLength(newLength=length)
        self.refresh()

    def reFitAllInstancesWidth(self):
        """
        Re-fit all instances on this diagram to match their participant names.
        """
        from umlshapes.sd.UmlSDInstance import UmlSDInstance

        for shape in self.umlShapes:
            if isinstance(shape, UmlSDInstance):
                shape.reFitWidth()
        self.refresh()
