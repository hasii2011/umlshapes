
from typing import List
from typing import cast
from typing import NewType
from typing import TYPE_CHECKING

from logging import Logger
from logging import getLogger

from copy import deepcopy

from functools import singledispatch

from wx import OK
from wx import ICON_ERROR

from wx import ClientDC
from wx import MessageDialog

from umlmodel.Actor import Actor
from umlmodel.Class import Class
from umlmodel.Link import Links
from umlmodel.Note import Note
from umlmodel.Text import Text
from umlmodel.UseCase import UseCase
from umlmodel.UmlModelBase import UmlModelBase
from umlmodel.LinkedObject import LinkedObject

from umlshapes.UmlUtils import UmlUtils

from umlshapes.commands.ActorCutCommand import ActorCutCommand
from umlshapes.commands.ActorPasteCommand import ActorPasteCommand
from umlshapes.commands.BaseCutCommand import BaseCutCommand
from umlshapes.commands.ClassCutCommand import ClassCutCommand
from umlshapes.commands.ClassPasteCommand import ClassPasteCommand
from umlshapes.commands.DeleteLinkCommand import DeleteLinkCommand
from umlshapes.commands.NoteCutCommand import NoteCutCommand
from umlshapes.commands.NotePasteCommand import NotePasteCommand
from umlshapes.commands.TextCutCommand import TextCutCommand
from umlshapes.commands.TextPasteCommand import TextPasteCommand
from umlshapes.commands.UseCaseCutCommand import UseCaseCutCommand
from umlshapes.commands.UseCasePasteCommand import UseCasePasteCommand

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.types.DeltaXY import DeltaXY
from umlshapes.types.UmlPosition import UmlPosition

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.ShapeTypes import UmlShapes
    from umlshapes.ShapeTypes import UmlShapeGenre

ModelObjects = NewType('ModelObjects', List[UmlModelBase])

# noinspection PyUnusedLocal
@singledispatch
def createCutCommand(umlShape: 'UmlShapeGenre') -> BaseCutCommand:
    raise NotImplementedError("Unsupported type")


class UmlFrameOperationsListener:

    def __init__(self, umlFrame: 'UmlFrame', umlPubSubEngine: IUmlPubSubEngine):

        from umlshapes.frames.UmlFrame import UmlFrame

        self.logger: Logger = getLogger(__name__)

        self._umlFrame:        UmlFrame         = umlFrame
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        self._preferences:     UmlPreferences   = UmlPreferences()

        self._clipboard: ModelObjects = ModelObjects([])            # will be re-created at every copy

        self._setupListeners()

    def _setupListeners(self):
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.UNDO, frameId=self._umlFrame.id, listener=self._undoListener)
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.REDO, frameId=self._umlFrame.id, listener=self._redoListener)

        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.CUT_SHAPES,   frameId=self._umlFrame.id, listener=self._cutShapesListener)
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.COPY_SHAPES,  frameId=self._umlFrame.id, listener=self._copyShapesListener)
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.PASTE_SHAPES, frameId=self._umlFrame.id, listener=self._pasteShapesListener)

        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.SELECT_ALL_SHAPES, frameId=self._umlFrame.id, listener=self._selectAllShapesListener)
        self._umlPubSubEngine.subscribe(messageType=UmlMessageType.SHAPE_MOVING,      frameId=self._umlFrame.id, listener=self._shapeMovingListener)

    def _undoListener(self):
        self._umlFrame.commandProcessor.Undo()
        self._umlFrame.frameModified = True

    def _redoListener(self):
        self._umlFrame.commandProcessor.Redo()
        self._umlFrame.frameModified = True

    def _cutShapesListener(self):
        """
        We don't need to copy anything to the clipboard.  The cut commands
        know how to recreate them.  Notice we pass the full UML Shape to the command
        for direct removal
        """
        selectedShapes: UmlShapes = self._umlFrame.selectedShapes
        if len(selectedShapes) == 0:        # noqa
            with MessageDialog(parent=None, message='No shapes selected', caption='', style=OK | ICON_ERROR) as dlg:
                dlg.ShowModal()
        else:
            self._cutShapes(selectedShapes)

    def _copyShapesListener(self):
        """
        Only copy the model objects to the clipboard.  Paste can then recreate them
        """

        selectedShapes: UmlShapes = self._umlFrame.selectedShapes
        if len(selectedShapes) == 0:        # noqa
            with MessageDialog(parent=None, message='No shapes selected', caption='', style=OK | ICON_ERROR) as dlg:
                dlg.ShowModal()
        else:
            self._copyToInternalClipboard(selectedShapes=selectedShapes)

            self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.UPDATE_APPLICATION_STATUS,
                                              frameId=self._umlFrame.id,
                                              message=f'Copied {len(self._clipboard)} shapes')  # noqa

    def _pasteShapesListener(self):
        """
        We don't do links

        Assumes that the model objects are deep copies and that the ID has been made unique

        """
        self.logger.info(f'Pasting {len(self._clipboard)} shapes')  # noqa

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
                                                                         umlFrame=self._umlFrame,
                                                                         umlPubSubEngine=self._umlPubSubEngine
                                                                         )
                self._umlFrame.commandProcessor.Submit(classPasteCommand)

                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.FRAME_MODIFIED, frameId=self._umlFrame.id, modifiedFrameId=self._umlFrame.id)
            elif isinstance(umlModelBase, Actor):
                actorPasteCommand: ActorPasteCommand = ActorPasteCommand(umlModelBase=umlModelBase,
                                                                         umlPosition=UmlPosition(x=x, y=y),
                                                                         umlFrame=self._umlFrame,
                                                                         umlPubSubEngine=self._umlPubSubEngine
                                                                         )
                self._umlFrame.commandProcessor.Submit(actorPasteCommand)
            elif isinstance(umlModelBase, Note):
                notePasteCommand: NotePasteCommand = NotePasteCommand(umlModelBase=umlModelBase,
                                                                      umlPosition=UmlPosition(x=x, y=y),
                                                                      umlFrame=self._umlFrame,
                                                                      umlPubSubEngine=self._umlPubSubEngine
                                                                      )
                self._umlFrame.commandProcessor.Submit(notePasteCommand)
            elif isinstance(umlModelBase, Text):
                textPasteCommand: TextPasteCommand = TextPasteCommand(umlModelBase=umlModelBase,
                                                                      umlPosition=UmlPosition(x=x, y=y),
                                                                      umlFrame=self._umlFrame,
                                                                      umlPubSubEngine=self._umlPubSubEngine
                                                                      )
                self._umlFrame.commandProcessor.Submit(textPasteCommand)
            elif isinstance(umlModelBase, UseCase):
                useCasePasteCommand: UseCasePasteCommand = UseCasePasteCommand(umlModelBase=umlModelBase,
                                                                               umlPosition=UmlPosition(x=x, y=y),
                                                                               umlFrame=self._umlFrame,
                                                                               umlPubSubEngine=self._umlPubSubEngine
                                                                               )
                self._umlFrame.commandProcessor.Submit(useCasePasteCommand)

            else:
                continue

            numbObjectsPasted += 1
            x += pasteDeltaXY.deltaX
            y += pasteDeltaXY.deltaY

        self.frameModified = True
        self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.UPDATE_APPLICATION_STATUS,
                                          frameId=self._umlFrame.id,
                                          message=f'Pasted {len(self._clipboard)} shape')       # noqa

    def _selectAllShapesListener(self):

        from umlshapes.ShapeTypes import UmlShapeGenre
        from umlshapes.ShapeTypes import UmlLinkGenre

        for shape in self._umlFrame.umlDiagram.shapes:
            if isinstance(shape, UmlShapeGenre) is True or isinstance(shape, UmlLinkGenre) is True:
                shape.selected = True

        self._umlFrame.refresh()

    def _shapeMovingListener(self, deltaXY: DeltaXY):
        """
        The move master is sending the message;  We don't need to move it
        Args:
            deltaXY:
        """
        from umlshapes.links.UmlLink import UmlLink
        from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel
        from umlshapes.ShapeTypes import UmlShapeGenre

        self.logger.debug(f'{deltaXY=}')
        shapes = self._umlFrame.selectedShapes
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

    def _cutShapes(self, selectedShapes: 'UmlShapes'):

        from umlshapes.ShapeTypes import UmlShapeGenre
        from umlshapes.ShapeTypes import UmlLinkGenre

        from umlshapes.shapes.UmlClass import UmlClass
        from umlshapes.shapes.UmlNote import UmlNote
        from umlshapes.shapes.UmlActor import UmlActor
        from umlshapes.shapes.UmlText import UmlText
        from umlshapes.shapes.UmlUseCase import UmlUseCase

        @createCutCommand.register
        def classCutCommand(umlShape: UmlClass) -> ClassCutCommand:
            cutCommand: ClassCutCommand = ClassCutCommand(umlClass=umlShape,
                                                          umlPosition=umlShape.position,
                                                          umlFrame=self._umlFrame,
                                                          umlPubSubEngine=self._umlPubSubEngine
                                                          )
            return cutCommand

        @createCutCommand.register
        def noteCutCommand(umlShape: UmlNote) -> NoteCutCommand:
            cutCommand: NoteCutCommand = NoteCutCommand(umlNote=umlShape,
                                                        umlPosition=umlShape.position,
                                                        umlFrame=self._umlFrame,
                                                        umlPubSubEngine=self._umlPubSubEngine
                                                        )
            return cutCommand

        @createCutCommand.register
        def actorCutCommand(umlShape: UmlActor) -> ActorCutCommand:

            cutCommand: ActorCutCommand = ActorCutCommand(umlActor=umlShape,
                                                          umlPosition=umlShape.position,
                                                          umlFrame=self._umlFrame,
                                                          umlPubSubEngine=self._umlPubSubEngine
                                                          )
            return cutCommand

        @createCutCommand.register
        def textCutCommand(umlText: UmlText) -> TextCutCommand:
            cutCommand: TextCutCommand = TextCutCommand(umlText=umlText,
                                                        umlPosition=umlText.position,
                                                        umlFrame=self._umlFrame,
                                                        umlPubSubEngine=self._umlPubSubEngine
                                                        )
            return cutCommand

        @createCutCommand.register
        def useCaseCutCommand(umlUseCase: UmlUseCase) -> UseCaseCutCommand:
            cutCommand: UseCaseCutCommand = UseCaseCutCommand(umlUseCase=umlUseCase,
                                                              umlPosition=umlUseCase.position,
                                                              umlFrame=self._umlFrame,
                                                              umlPubSubEngine=self._umlPubSubEngine
                                                              )

            return cutCommand

        self._copyToInternalClipboard(selectedShapes=selectedShapes)  # In case we want to paste them back

        for shape in selectedShapes:
            if isinstance(shape, UmlShapeGenre):
                self._umlFrame.commandProcessor.Submit(createCutCommand(shape))
            elif isinstance(shape, UmlLinkGenre):
                deleteLinkCommand: DeleteLinkCommand = DeleteLinkCommand(partialName='Delete-', umlLink=shape, umlPubSubEngine=self._umlPubSubEngine)
                self._umlFrame.commandProcessor.Submit(deleteLinkCommand)
            else:
                assert False, f'Now do I delete this: {shape=}'
        self._umlFrame.frameModified = True

        self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.UPDATE_APPLICATION_STATUS,
                                          frameId=self._umlFrame.id,
                                          message=f'Cut {len(self._clipboard)} shapes')     # noqa

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
        from umlshapes.shapes.UmlText import UmlText

        self._clipboard = ModelObjects([])

        # put a copy of the model instances in the clipboard
        for umlShape in selectedShapes:
            linkedObject: LinkedObject = cast(LinkedObject, None)

            if isinstance(umlShape, UmlClass):
                linkedObject = deepcopy(umlShape.modelClass)
            elif isinstance(umlShape, UmlNote):
                linkedObject = deepcopy(umlShape.modelNote)
            elif isinstance(umlShape, UmlActor):
                linkedObject = deepcopy(umlShape.modelActor)
            elif isinstance(umlShape, UmlUseCase):
                linkedObject = deepcopy(umlShape.modelUseCase)
            elif isinstance(umlShape, UmlText):
                umlText: UmlText = umlShape
                text:    Text    = deepcopy(umlText.modelText)
                self._clipboard.append(text)
            else:
                self.logger.warning(f'Unhandled copy of shape {type(umlShape)}')

            if linkedObject is not None:
                linkedObject.id = UmlUtils.getID()
                linkedObject.links = Links([])  # we don't want to copy the links
                self._clipboard.append(linkedObject)
