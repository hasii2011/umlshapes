from typing import Callable
from typing import List
from typing import NewType
from typing import cast
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from sys import maxsize

from collections.abc import Iterable

from copy import deepcopy

from dataclasses import dataclass

from wx import OK
from wx import WXK_UP
from wx import EVT_CHAR
from wx import EVT_MOTION
from wx import WXK_DELETE
from wx import WXK_DOWN
from wx import ICON_ERROR

from wx import ClientDC
from wx import CommandProcessor
from wx import MessageDialog
from wx import MouseEvent
from wx import KeyEvent
from wx import Window

from umlmodel.Actor import Actor
from umlmodel.Class import Class
from umlmodel.Link import Links
from umlmodel.Note import Note
from umlmodel.Text import Text
from umlmodel.UseCase import UseCase
from umlmodel.LinkedObject import LinkedObject
from umlmodel.UmlModelBase import UmlModelBase

from umlshapes.lib.ogl import Shape
from umlshapes.lib.ogl import ShapeCanvas

from umlshapes.frames.ShapeSelector import ShapeSelector

from umlshapes.commands.ActorCutCommand import ActorCutCommand
from umlshapes.commands.ClassCutCommand import ClassCutCommand
from umlshapes.commands.NoteCutCommand import NoteCutCommand
from umlshapes.commands.TextCutCommand import TextCutCommand
from umlshapes.commands.UseCaseCutCommand import UseCaseCutCommand

from umlshapes.commands.TextPasteCommand import TextPasteCommand
from umlshapes.commands.UseCasePasteCommand import UseCasePasteCommand
from umlshapes.commands.ActorPasteCommand import ActorPasteCommand
from umlshapes.commands.ClassPasteCommand import ClassPasteCommand
from umlshapes.commands.NotePasteCommand import NotePasteCommand

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.frames.DiagramFrame import DiagramFrame

from umlshapes.UmlUtils import UmlUtils

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.DeltaXY import DeltaXY
from umlshapes.types.UmlLine import UmlLine
from umlshapes.types.UmlPosition import UmlPoint
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlDimensions import UmlDimensions

if TYPE_CHECKING:
    from umlshapes.ShapeTypes import UmlShapes

A4_FACTOR:     float = 1.41

PIXELS_PER_UNIT_X: int = 20
PIXELS_PER_UNIT_Y: int = 20

ModelObjects = NewType('ModelObjects', List[UmlModelBase])

BIG_NUM: int = 10000    # Hopefully, there are less than this number of shapes on frame

BOUNDARY_RIGHT_MARGIN:  int = 5
BOUNDARY_LEFT_MARGIN:   int = 5
BOUNDARY_TOP_MARGIN:    int = 5
BOUNDARY_BOTTOM_MARGIN: int = 5

@dataclass
class Ltrb:
    left:   int = 0
    top:    int = 0
    right:  int = 0
    bottom: int = 0


class UmlFrame(DiagramFrame):

    KEY_CODE_DELETE: int = WXK_DELETE
    KEY_CODE_UP:     int = WXK_UP
    KEY_CODE_DOWN:   int = WXK_DOWN

    KEY_CODE_CAPITAL_S:    int = ord('S')
    KEY_CODE_LOWER_CASE_S: int = ord('s')

    def __init__(self, parent: Window, umlPubSubEngine: IUmlPubSubEngine):

        self.ufLogger:         Logger           = getLogger(__name__)
        self._preferences:     UmlPreferences   = UmlPreferences()
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        super().__init__(parent=parent)

        # Doing this so key up/down Z Order code works
        self.DisableKeyboardScrolling()

        self._commandProcessor: CommandProcessor = CommandProcessor()
        self._maxWidth:  int  = self._preferences.virtualWindowWidth
        self._maxHeight: int = int(self._maxWidth / A4_FACTOR)  # 1.41 is for A4 support

        nbrUnitsX: int = self._maxWidth // PIXELS_PER_UNIT_X
        nbrUnitsY: int = self._maxHeight // PIXELS_PER_UNIT_Y
        initPosX:  int = 0
        initPosY:  int = 0
        self.SetScrollbars(PIXELS_PER_UNIT_X, PIXELS_PER_UNIT_Y, nbrUnitsX, nbrUnitsY, initPosX, initPosY, False)

        self.setInfinite(True)
        self._currentReportInterval: int = self._preferences.trackMouseInterval
        self._frameModified: bool = False

        self._clipboard: ModelObjects = ModelObjects([])            # will be re-created at every copy

        self._setupListeners()
        self.Bind(EVT_CHAR, self._onProcessKeystrokes)

    def markFrameSaved(self):
        """
        Clears the commands an ensures that CommandProcess.isDirty() is rationale
        """
        self.commandProcessor.MarkAsSaved(),
        self.commandProcessor.ClearCommands()

    @property
    def frameModified(self) -> bool:
        return self._frameModified

    @frameModified.setter
    def frameModified(self, newValue: bool):
        self._frameModified = newValue

    @property
    def commandProcessor(self) -> CommandProcessor:
        return self._commandProcessor

    @property
    def umlPubSubEngine(self) -> IUmlPubSubEngine:
        return self._umlPubSubEngine

    @property
    def umlShapes(self) -> 'UmlShapes':

        diagram: UmlDiagram = self.GetDiagram()
        return diagram.GetShapeList()

    @property
    def selectedShapes(self) -> 'UmlShapes':
        from umlshapes.ShapeTypes import UmlShapes

        selectedShapes: UmlShapes = UmlShapes([])
        umlshapes:      UmlShapes = self.umlShapes

        for shape in umlshapes:
            if shape.Selected() is True:
                selectedShapes.append(shape)

        return selectedShapes

    @property
    def shapeBoundaries(self) -> Ltrb:
        """

        Return shape boundaries as and LTRB instance

        """
        minX: int = maxsize
        maxX: int = -maxsize
        minY: int = maxsize
        maxY: int = -maxsize

        # Compute the boundaries
        for shapeInstance in self.umlDiagram.shapes:

            from umlshapes.ShapeTypes import UmlShapeGenre

            if isinstance(shapeInstance, UmlShapeGenre):
                umlShape: UmlShapeGenre = shapeInstance
                # Get shape limits
                topLeft: UmlPosition   = umlShape.position
                size:    UmlDimensions = umlShape.size

                ox1: int = topLeft.x
                oy1: int = topLeft.y
                ox2: int = size.width
                oy2: int = size.height
                ox2 += ox1
                oy2 += oy1

                # Update min-max
                minX = min(minX, ox1)
                maxX = max(maxX, ox2)
                minY = min(minY, oy1)
                maxY = max(maxY, oy2)

        # Return values
        return Ltrb(left=minX - BOUNDARY_LEFT_MARGIN,
                    top=minY - BOUNDARY_TOP_MARGIN,
                    right=maxX + BOUNDARY_RIGHT_MARGIN,
                    bottom=maxY + BOUNDARY_BOTTOM_MARGIN
                    )

    def OnLeftClick(self, x, y, keys=0):
        """
        Maybe this belongs in DiagramFrame

        Args:
            x:
            y:
            keys:
        """
        diagram: UmlDiagram = self.umlDiagram
        shapes:  Iterable = diagram.GetShapeList()

        for shape in shapes:
            umlShape: Shape     = cast(Shape, shape)
            canvas: ShapeCanvas = umlShape.GetCanvas()
            dc:     ClientDC    = ClientDC(canvas)
            canvas.PrepareDC(dc)

            umlShape.Select(select=False, dc=dc)

        self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.FRAME_LEFT_CLICK,
                                          frameId=self.id,
                                          frame=self,
                                          umlPosition=UmlPosition(x=x, y=y)
                                          )
        self.refresh()

    def OnMouseEvent(self, mouseEvent: MouseEvent):
        """
        Debug hook
        TODO:  Update the UI via an event
        Args:
            mouseEvent:

        """
        super().OnMouseEvent(mouseEvent)

        if self._preferences.trackMouse is True:
            if self._currentReportInterval == 0:
                x, y = self.CalcUnscrolledPosition(mouseEvent.GetPosition())
                self.ufLogger.info(f'({x},{y})')
                self._currentReportInterval = self._preferences.trackMouseInterval
            else:
                self._currentReportInterval -= 1

    def OnDragLeft(self, draw, x, y, keys=0):
        self.ufLogger.debug(f'{draw=} - x,y=({x},{y}) - {keys=}')

        if self._selector is None:
            self._beginSelect(x=x, y=y)

    def OnEndDragLeft(self, x, y, keys=0):

        from umlshapes.links.UmlLink import UmlLink

        self.Unbind(EVT_MOTION, handler=self._onSelectorMove)
        self.umlDiagram.RemoveShape(self._selector)

        for s in self.umlDiagram.shapes:
            if self._ignoreShape(shapeToCheck=s) is False:
                if isinstance(s, UmlLink):
                    umlLink: UmlLink = s
                    x1, y1, x2, y2 = umlLink.GetEnds()
                    umlLine: UmlLine = UmlLine(start=UmlPoint(x=x1, y=y1), end=UmlPoint(x=x2, y=y2))
                    if UmlUtils.isLineWhollyContainedByRectangle(boundingRectangle=self._selector.rectangle, umlLine=umlLine) is True:
                        umlLink.selected = True
                else:
                    from umlshapes.ShapeTypes import UmlShapeGenre
                    shape: UmlShapeGenre = cast(UmlShapeGenre, s)
                    if UmlUtils.isShapeInRectangle(boundingRectangle=self._selector.rectangle, shapeRectangle=shape.rectangle) is True:
                        shape.selected = True

        self.refresh()
        self._selector = cast(ShapeSelector, None)

        return True

    def _onProcessKeystrokes(self, event: KeyEvent):
        """

        Args:
            event:  The wxPython key event

        """
        c: int = event.GetKeyCode()
        match c:
            case UmlFrame.KEY_CODE_DELETE:
                self._cutShapes(selectedShapes=self.selectedShapes)
            case UmlFrame.KEY_CODE_UP:
                self._changeTheSelectedShapesZOrder(callback=self._moveShapeToFront)
                event.Skip(skip=True)
            case UmlFrame.KEY_CODE_DOWN:
                self._changeTheSelectedShapesZOrder(callback=self._moveShapeToBack)
                event.Skip(skip=True)
            case UmlFrame.KEY_CODE_LOWER_CASE_S:
                self._toggleSpline()
            case UmlFrame.KEY_CODE_CAPITAL_S:
                self._toggleSpline()
            case _:
                self.ufLogger.warning(f'Key code not supported: {c}')
                event.Skip(skip=True)

    def _setupListeners(self):
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.UNDO, frameId=self.id, listener=self._undoListener)
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.REDO, frameId=self.id, listener=self._redoListener)

        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.CUT_SHAPES,   frameId=self.id, listener=self._cutShapesListener)
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.COPY_SHAPES,  frameId=self.id, listener=self._copyShapesListener)
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.PASTE_SHAPES, frameId=self.id, listener=self._pasteShapesListener)

        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.SELECT_ALL_SHAPES, frameId=self.id, listener=self._selectAllShapesListener)
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.SHAPE_MOVING,      frameId=self.id, listener=self._shapeMovingListener)

    def _undoListener(self):
        self._commandProcessor.Undo()
        self.frameModified = True

    def _redoListener(self):
        self._commandProcessor.Redo()
        self.frameModified = True

    def _cutShapesListener(self):
        """
        We don't need to copy anything to the clipboard.  The cut commands
        know how to recreate them.  Notice we pass the full UML Shape to the command
        for direct removal
        """
        selectedShapes: UmlShapes = self.selectedShapes
        if len(selectedShapes) == 0:
            with MessageDialog(parent=None, message='No shapes selected', caption='', style=OK | ICON_ERROR) as dlg:
                dlg.ShowModal()
        else:
            self._cutShapes(selectedShapes)

    def _cutShapes(self, selectedShapes: 'UmlShapes'):
        from umlshapes.shapes.UmlClass import UmlClass
        from umlshapes.shapes.UmlNote import UmlNote
        from umlshapes.shapes.UmlActor import UmlActor
        from umlshapes.shapes.UmlText import UmlText
        from umlshapes.shapes.UmlUseCase import UmlUseCase

        self._copyToInternalClipboard(selectedShapes=selectedShapes)  # In case we want to paste them back

        for shape in selectedShapes:
            if isinstance(shape, UmlClass) is True:
                umlClass: UmlClass = cast(UmlClass, shape)
                classCutCommand: ClassCutCommand = ClassCutCommand(umlClass=umlClass,
                                                                   umlPosition=umlClass.position,
                                                                   umlFrame=self,
                                                                   umlPubSubEngine=self._umlPubSubEngine
                                                                   )
                self._commandProcessor.Submit(classCutCommand)
            elif isinstance(shape, UmlNote):
                umlNote: UmlNote = shape
                noteCutCommand: NoteCutCommand = NoteCutCommand(umlNote=umlNote,
                                                                umlPosition=umlNote.position,
                                                                umlFrame=self,
                                                                umlPubSubEngine=self._umlPubSubEngine
                                                                )
                self._commandProcessor.Submit(noteCutCommand)
            elif isinstance(shape, UmlActor):
                umlActor: UmlActor = shape
                actorCutCommand: ActorCutCommand = ActorCutCommand(umlActor=umlActor,
                                                                   umlPosition=umlActor.position,
                                                                   umlFrame=self,
                                                                   umlPubSubEngine=self._umlPubSubEngine
                                                                   )
                self._commandProcessor.Submit(actorCutCommand)
            elif isinstance(shape, UmlText):
                umlText: UmlText = shape
                textCutCommand: TextCutCommand = TextCutCommand(umlText=umlText,
                                                                umlPosition=umlText.position,
                                                                umlFrame=self,
                                                                umlPubSubEngine=self._umlPubSubEngine
                                                                )
                self._commandProcessor.Submit(textCutCommand)
            elif isinstance(shape, UmlUseCase):
                umlUseCase: UmlUseCase = shape
                useCaseCutCommand: UseCaseCutCommand = UseCaseCutCommand(umlUseCase=umlUseCase,
                                                                         umlPosition=umlUseCase.position,
                                                                         umlFrame=self,
                                                                         umlPubSubEngine=self._umlPubSubEngine
                                                                         )
                self._commandProcessor.Submit(useCaseCutCommand)

        self.frameModified = True

        self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.UPDATE_APPLICATION_STATUS,
                                          frameId=self.id,
                                          message=f'Cut {len(self._clipboard)} shapes')

    def _copyShapesListener(self):
        """
        Only copy the model objects to the clipboard.  Paste can then recreate them
        """

        selectedShapes: UmlShapes = self.selectedShapes
        if len(selectedShapes) == 0:
            with MessageDialog(parent=None, message='No shapes selected', caption='', style=OK | ICON_ERROR) as dlg:
                dlg.ShowModal()
        else:
            self._copyToInternalClipboard(selectedShapes=selectedShapes)

            self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.UPDATE_APPLICATION_STATUS,
                                              frameId=self.id,
                                              message=f'Copied {len(self._clipboard)} shapes')

    def _pasteShapesListener(self):
        """
        We don't do links

        Assumes that the model objects are deep copies and that the ID has been made unique

        """
        self.ufLogger.info(f'Pasting {len(self._clipboard)} shapes')

        # Get the objects out of the internal clipboard and let the appropriate command process them
        pasteStart:   UmlPosition = self._preferences.pasteStart
        pasteDeltaXY: DeltaXY     = self._preferences.pasteDeltaXY
        x: int = pasteStart.x
        y: int = pasteStart.y
        numbObjectsPasted: int = 0
        for clipboardObject in self._clipboard:

            umlModelBase: UmlModelBase = clipboardObject

            if isinstance(umlModelBase, Class) is True:
                classPasteCommand: ClassPasteCommand = ClassPasteCommand(umlModelBase=umlModelBase,
                                                                         umlPosition=UmlPosition(x=x, y=y),
                                                                         umlFrame=self,
                                                                         umlPubSubEngine=self._umlPubSubEngine
                                                                         )
                self._commandProcessor.Submit(classPasteCommand)

                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.FRAME_MODIFIED, frameId=self.id, modifiedFrameId=self.id)
            elif isinstance(umlModelBase, Actor):
                actorPasteCommand: ActorPasteCommand = ActorPasteCommand(umlModelBase=umlModelBase,
                                                                         umlPosition=UmlPosition(x=x, y=y),
                                                                         umlFrame=self,
                                                                         umlPubSubEngine=self._umlPubSubEngine
                                                                         )
                self._commandProcessor.Submit(actorPasteCommand)
            elif isinstance(umlModelBase, Note):
                notePasteCommand: NotePasteCommand = NotePasteCommand(umlModelBase=umlModelBase,
                                                                      umlPosition=UmlPosition(x=x, y=y),
                                                                      umlFrame=self,
                                                                      umlPubSubEngine=self._umlPubSubEngine
                                                                      )
                self._commandProcessor.Submit(notePasteCommand)
            elif isinstance(umlModelBase, Text):
                textPasteCommand: TextPasteCommand = TextPasteCommand(umlModelBase=umlModelBase,
                                                                      umlPosition=UmlPosition(x=x, y=y),
                                                                      umlFrame=self,
                                                                      umlPubSubEngine=self._umlPubSubEngine
                                                                      )
                self._commandProcessor.Submit(textPasteCommand)
            elif isinstance(umlModelBase, UseCase):
                useCasePasteCommand: UseCasePasteCommand = UseCasePasteCommand(umlModelBase=umlModelBase,
                                                                               umlPosition=UmlPosition(x=x, y=y),
                                                                               umlFrame=self,
                                                                               umlPubSubEngine=self._umlPubSubEngine
                                                                               )
                self._commandProcessor.Submit(useCasePasteCommand)

            else:
                continue

            numbObjectsPasted += 1
            x += pasteDeltaXY.deltaX
            y += pasteDeltaXY.deltaY

        self.frameModified = True
        self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.UPDATE_APPLICATION_STATUS,
                                          frameId=self.id,
                                          message=f'Pasted {len(self._clipboard)} shape')

    def _selectAllShapesListener(self):
        from umlshapes.ShapeTypes import UmlShapeGenre
        from umlshapes.ShapeTypes import UmlLinkGenre

        for shape in self.umlDiagram.shapes:
            if isinstance(shape, UmlShapeGenre) is True or isinstance(shape, UmlLinkGenre) is True:
                shape.selected = True

        self.refresh()

    def _shapeMovingListener(self, deltaXY: DeltaXY):
        """
        The move master is sending the message;  We don't need to move it
        Args:
            deltaXY:
        """
        from umlshapes.links.UmlLink import UmlLink
        from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
        from umlshapes.ShapeTypes import UmlShapeGenre

        self.ufLogger.debug(f'{deltaXY=}')
        shapes = self.selectedShapes
        for s in shapes:
            umlShape: UmlShapeGenre = cast(UmlShapeGenre, s)
            if not isinstance(umlShape, UmlLink) and not isinstance(umlShape, UmlAssociationLabel):
                if umlShape.moveMaster is False:
                    umlShape.position = UmlPosition(
                        x=umlShape.position.x + deltaXY.deltaX,
                        y=umlShape.position.y + deltaXY.deltaY
                    )
                    dc: ClientDC = ClientDC(umlShape.umlFrame)
                    umlShape.umlFrame.PrepareDC(dc)
                    umlShape.MoveLinks(dc)

    def _copyToInternalClipboard(self, selectedShapes: 'UmlShapes'):
        """
        Makes a copy of the selected shape's data model and puts in our
        internal clipboard

        First clears the internal clipboard and then fills it up

        Args:
            selectedShapes:   The selected shapes
        """
        from umlshapes.shapes.UmlClass import UmlClass
        from umlshapes.shapes.UmlNote import UmlNote
        from umlshapes.shapes.UmlActor import UmlActor
        from umlshapes.shapes.UmlUseCase import UmlUseCase
        # from umlshapes.shapes.UmlText import UmlText

        self._clipboard = ModelObjects([])

        # put a copy of the model instances in the clipboard
        for umlShape in selectedShapes:
            linkedObject: LinkedObject = cast(LinkedObject, None)

            if isinstance(umlShape, UmlClass):
                linkedObject = deepcopy(umlShape.modelClass)
            elif isinstance(umlShape, UmlNote):
                linkedObject = deepcopy(umlShape.modelNote)
            # elif isinstance(umlShape, UmlText):
            #     linkedObject = deepcopy(umlShape.modelText)
            elif isinstance(umlShape, UmlActor):
                linkedObject = deepcopy(umlShape.modelActor)
            elif isinstance(umlShape, UmlUseCase):
                linkedObject = deepcopy(umlShape.modelUseCase)
            else:
                pass
            if linkedObject is not None:
                linkedObject.id = UmlUtils.getID()
                linkedObject.links = Links([])  # we don't want to copy the links
                self._clipboard.append(linkedObject)

    def _unSelectAllShapesOnCanvas(self):

        shapes:  Iterable = self.umlDiagram.shapes

        for s in shapes:
            s.Select(True)

        self.Refresh(False)

    def _beginSelect(self, x: int, y: int):
        """
        Create a selector box and manage it.

        Args:
            x:
            y:

        Returns:
        """
        selector: ShapeSelector = ShapeSelector(width=0, height=0)     # RectangleShape(x, y, 0, 0)
        selector.position = UmlPosition(x, y)
        selector.originalPosition = selector.position

        selector.moving = True
        selector.diagramFrame = self

        diagram: UmlDiagram = self.umlDiagram
        diagram.AddShape(selector)

        selector.Show(True)

        self._selector = selector

        self.Bind(EVT_MOTION, self._onSelectorMove)

    def _onSelectorMove(self, event: MouseEvent):
        # from wx import Rect as WxRect

        if self._selector is not None:
            eventPosition: UmlPosition = self._getEventPosition(event)
            umlPosition:   UmlPosition = self._selector.position

            x: int = eventPosition.x
            y: int = eventPosition.y

            x0 = umlPosition.x
            y0 = umlPosition.y

            # self._selector.SetSize(x - x0, y - y0)
            self._selector.size = UmlDimensions(width=x - x0, height=y - y0)
            self._selector.position = self._selector.originalPosition

            self.refresh()

    def _getEventPosition(self, event: MouseEvent) -> UmlPosition:
        """
        Return the position of a click in the diagram.
        Args:
            event:   The mouse event

        Returns: The UML Position
        """
        x, y = self._convertEventCoordinates(event)
        return UmlPosition(x=x, y=y)

    def _ignoreShape(self, shapeToCheck):
        """

        Args:
            shapeToCheck:  The shape to check

        Returns: True if the shape is one of our ignore shapes
        """
        from umlshapes.shapes.UmlControlPoint import UmlControlPoint
        from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
        from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface
        from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPoint

        ignore: bool = False

        if (isinstance(shapeToCheck, UmlControlPoint) or
                isinstance(shapeToCheck, UmlAssociationLabel) or
                isinstance(shapeToCheck, UmlLollipopInterface) or
                isinstance(shapeToCheck, UmlLineControlPoint)):
            ignore = True

        return ignore

    def _toggleSpline(self):
        from umlshapes.ShapeTypes import UmlLinkGenre

        selectedShapes = self.selectedShapes

        for shape in selectedShapes:
            if isinstance(shape, UmlLinkGenre):
                shape.spline = (not shape.spline)
        self.refresh()

    def _changeTheSelectedShapesZOrder(self, callback: Callable):
        """
        Move the selected shape one level in the z-order

        Args:
            callback:  The input method determines which way
        """
        from umlshapes.ShapeTypes import UmlShapeGenre

        selectedShapes = self.selectedShapes

        if len(selectedShapes) > 0:
            for shape in selectedShapes:
                if isinstance(shape, UmlShapeGenre):
                    callback(shape)
        self.refresh()

    def _moveShapeToFront(self, shape: Shape):
        """
        Move the given shape to the top of the Z order

        Args:
            shape: The shape to move
        """
        shapesToMove = [shape] + shape.GetChildren()
        currentShapes = list(self.umlDiagram.shapes)

        for s in shapesToMove:
            currentShapes.remove(s)

        self.umlDiagram.shapes = currentShapes + shapesToMove

    def _moveShapeToBack(self, shape: Shape):
        """
        Move the given shape to the bottom of the Z order

        Args:
            shape: The shape to move
        """
        shapesToMove = [shape] + shape.GetChildren()
        currentShapes = list(self.umlDiagram.shapes)
        for s in shapesToMove:
            currentShapes.remove(s)

        self.umlDiagram.shapes = shapesToMove + currentShapes
