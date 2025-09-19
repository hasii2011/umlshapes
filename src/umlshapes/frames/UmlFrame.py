
from typing import List
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from collections.abc import Iterable

from copy import deepcopy

from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutLinkedObject import PyutLinkedObject
from wx import ICON_ERROR
from wx import OK

from wx import ClientDC
from wx import CommandProcessor
from wx import MessageDialog
from wx import MouseEvent
from wx import Window

from pyutmodelv2.PyutObject import PyutObject
from pyutmodelv2.PyutLink import PyutLinks
# from pyutmodelv2.PyutActor import PyutActor
# from pyutmodelv2.PyutClass import PyutClass
# from pyutmodelv2.PyutNote import PyutNote
# from pyutmodelv2.PyutText import PyutText
# from pyutmodelv2.PyutUseCase import PyutUseCase

from umlshapes.frames.commands.ClassPasteCommand import ClassPasteCommand
from umlshapes.lib.ogl import Shape
from umlshapes.lib.ogl import ShapeCanvas

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.frames.DiagramFrame import DiagramFrame

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.preferences.UmlPreferences import UmlPreferences


from umlshapes.types.Common import UmlShapeList
from umlshapes.types.UmlPosition import UmlPosition


A4_FACTOR:     float = 1.41

PIXELS_PER_UNIT_X: int = 20
PIXELS_PER_UNIT_Y: int = 20

PyutObjects = NewType('PyutObjects', List[PyutObject])

BIG_NUM: int = 10000    # Hopefully, there are less than this number of shapes on frame

# @dataclass
# class PasteCreatorResults:
#     umlShape:     UmlShape              = cast(UmlShape, None)
#     eventHandler: 'UmlBaseEventHandler' = cast('UmlBaseEventHandler', None)


class UmlFrame(DiagramFrame):

    def __init__(self, parent: Window, umlPubSubEngine: IUmlPubSubEngine):

        self.ufLogger:         Logger           = getLogger(__name__)
        self._preferences:     UmlPreferences   = UmlPreferences()
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        super().__init__(parent=parent)

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

        self._clipboard: PyutObjects = PyutObjects([])            # will be re-created at every copy

        self._setupListeners()

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
    def umlShapes(self) -> UmlShapeList:

        diagram: UmlDiagram = self.GetDiagram()
        return diagram.GetShapeList()

    @property
    def selectedShapes(self) -> UmlShapeList:

        selectedShapes: UmlShapeList = UmlShapeList([])
        umlshapes:      UmlShapeList = self.umlShapes

        for shape in umlshapes:
            if shape.Selected() is True:
                selectedShapes.append(shape)
        return selectedShapes

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

    def _setupListeners(self):
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.UNDO, frameId=self.id, listener=self._undoListener)
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.REDO, frameId=self.id, listener=self._redoListener)

        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.CUT_SHAPES,   frameId=self.id, listener=self._cutShapes)
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.COPY_SHAPES,  frameId=self.id, listener=self._copyShapes)
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.PASTE_SHAPES, frameId=self.id, listener=self._pasteShapes)

        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.SELECT_ALL_SHAPES, frameId=self.id, listener=self.selectAllShapes)

    def _undoListener(self):
        self._commandProcessor.Undo()

    def _redoListener(self):
        self._commandProcessor.Redo()

    def _cutShapes(self, ):
        self.ufLogger.warning(f'Cut is unimplemented')

        selectedShapes: UmlShapeList = self.selectedShapes
        if len(selectedShapes) == 0:
            with MessageDialog(parent=None, message='No shapes selected', caption='Invalid Destination', style=OK | ICON_ERROR) as dlg:
                dlg.ShowModal()
        else:
            pass

    def _copyShapes(self, ):
        from umlshapes.shapes.UmlClass import UmlClass
        from umlshapes.shapes.UmlNote import UmlNote
        from umlshapes.shapes.UmlActor import UmlActor
        from umlshapes.shapes.UmlUseCase import UmlUseCase
        from umlshapes.shapes.UmlText import UmlText

        selectedShapes: UmlShapeList = self.selectedShapes
        if len(selectedShapes) == 0:
            with MessageDialog(parent=None, message='No shapes selected', caption='Invalid Destination', style=OK | ICON_ERROR) as dlg:
                dlg.ShowModal()
        else:
            self._clipboard = PyutObjects([])

            # put a copy of the PyutObjects in the clipboard
            for umlShape in selectedShapes:
                pyutObject: PyutLinkedObject = cast(PyutLinkedObject, None)

                if isinstance(umlShape, UmlClass):
                    pyutObject = deepcopy(umlShape.pyutClass)
                elif isinstance(umlShape, UmlNote):
                    pyutObject = deepcopy(umlShape.pyutNote)
                elif isinstance(umlShape, UmlText):
                    pyutObject = deepcopy(umlShape.pyutText)
                elif isinstance(umlShape, UmlActor):
                    pyutObject = deepcopy(umlShape.pyutActor)
                elif isinstance(umlShape, UmlUseCase):
                    pyutObject = deepcopy(umlShape.pyutUseCase)
                else:
                    pass
                if  pyutObject is not None:
                    pyutObject.id += BIG_NUM
                    pyutObject.links = PyutLinks([])              # we don't want to copy the links
                    self._clipboard.append(pyutObject)

            self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.UPDATE_APPLICATION_STATUS,
                                              frameId=self.id,
                                              message=f'Copied {len(self._clipboard)} shapes')

    def _pasteShapes(self):
        """
        We don't do links

        Assumes that the model objects are deep copies and that the ID has been made unique

        """
        self.ufLogger.info(f'Pasting {len(self._clipboard)} shapes')

        # put the objects in the clipboard and remove them from the diagram
        x: int = 100
        y: int = 100
        numbObjectsPasted: int = 0
        for clipboardObject in self._clipboard:
            pyutObject:   PyutObject = clipboardObject

            if isinstance(pyutObject, PyutClass) is True:
                pasteCommand: ClassPasteCommand = ClassPasteCommand(pyutObject=pyutObject,
                                                                    umlPosition=UmlPosition(x=x, y=y),
                                                                    umlFrame=self,
                                                                    umlPubSubEngine=self._umlPubSubEngine
                                                                    )
                self._commandProcessor.Submit(pasteCommand)


                numbObjectsPasted += 1
                x += 50
                y += 50

                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.FRAME_MODIFIED, frameId=self.id, modifiedFrameId=self.id)
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.UPDATE_APPLICATION_STATUS,
                                                  frameId=self.id,
                                                  message=f'Pasted {len(self._clipboard)} shapes')

    def selectAllShapes(self, ):
        self.ufLogger.warning(f'Paste is unimplemented')

    def _unSelectAllShapesOnCanvas(self):

        shapes:  Iterable = self.umlDiagram.shapes

        for s in shapes:
            s.Select(True)

        self.Refresh(False)

    # def _setEventHandler(self, umlShape, eventHandler: 'UmlBaseEventHandler'):
    #
    #     eventHandler.SetShape(umlShape)        # cast(UmlBaseEventHandler, eventHandler).umlPubSubEngine = self._umlPubSubEngine
    #     eventHandler.umlPubSubEngine = self._umlPubSubEngine
    #     eventHandler.SetPreviousHandler(umlShape.GetEventHandler())
    #     umlShape.SetEventHandler(eventHandler)
