
from typing import cast

from logging import Logger
from logging import getLogger

from abc import ABCMeta
from abc import abstractmethod

from datetime import datetime

from wx import Command

from umlmodel.LinkedObject import LinkedObject

from umlshapes.ShapeTypes import UmlShapeGenre
from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler
from umlshapes.UmlDiagram import UmlDiagram
from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.shapes.UmlActor import UmlActor
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlText import UmlText
from umlshapes.shapes.UmlUseCase import UmlUseCase

from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler
from umlshapes.shapes.eventhandlers.UmlNoteEventHandler import UmlNoteEventHandler
from umlshapes.shapes.eventhandlers.UmlTextEventHandler import UmlTextEventHandler

from umlshapes.types.UmlPosition import UmlPosition

class MyMetaCommand(ABCMeta, type(Command)):        # type: ignore
    """
    I have no idea why this works:
    https://stackoverflow.com/questions/66591752/metaclass-conflict-when-trying-to-create-a-python-abstract-class-that-also-subcl
    """
    pass

# noinspection PyAbstractClass
class BaseCreateCommand(Command, metaclass=MyMetaCommand):
    """
    Used no-inspection because Pycharm seems to think this class is not abstract
    """
    def __init__(self, canUndo: bool, name: str, umlPubSubEngine: IUmlPubSubEngine, umlFrame: UmlFrame, umlPosition: UmlPosition):

        super().__init__(canUndo=canUndo, name=name)

        self._baseWxCreateLogger: Logger      = getLogger(__name__)
        self._umlFrame:           UmlFrame    = umlFrame
        self._umlPosition:        UmlPosition = umlPosition

        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        self._umlPreferences:  UmlPreferences        = UmlPreferences()

        self._shape: UmlShapeGenre = self._createPrototypeInstance()

    @property
    def timeStamp(self) -> int:

        dt = datetime.now()

        return dt.microsecond

    def Do(self) -> bool:
        self._placeShapeOnFrame()
        return True

    @abstractmethod
    def Undo(self) -> bool:
        pass

    @abstractmethod
    def _createPrototypeInstance(self) -> UmlShapeGenre:
        """
        Creates an appropriate class for the new command

        Returns:    The newly created class
        """
        pass

    @abstractmethod
    def _placeShapeOnFrame(self):
        """
        Implemented by subclasses to support .Do
        """
        pass

    def _addUmlShapeToFrame(self, umlFrame: UmlFrame, umlShape: UmlShapeGenre, umlPosition: UmlPosition):
        """
        This is common code needed to create Note, Text, Actor, and UseCase shapes.

        Args:
            umlFrame:
            umlShape:
            umlPosition:
        """
        self._baseWxCreateLogger.debug(f'{umlFrame=}')

        umlShape.position = umlPosition
        umlDiagram: UmlDiagram = umlFrame.umlDiagram
        umlDiagram.AddShape(umlShape)

        umlShape.Show(show=True)

        eventHandler: UmlBaseEventHandler = cast(UmlBaseEventHandler, None)
        if isinstance(umlShape, UmlClass):
            eventHandler = UmlClassEventHandler(previousEventHandler=umlShape.GetEventHandler())
        elif isinstance(umlShape, UmlNote):
            eventHandler = UmlNoteEventHandler(previousEventHandler=umlShape.GetEventHandler())
        elif isinstance(umlShape, UmlText):
            eventHandler = UmlTextEventHandler(previousEventHandler=umlShape.GetEventHandler())
        else:
            pass

        if eventHandler is not None:
            eventHandler.SetShape(umlShape)
            eventHandler.umlPubSubEngine = self._umlPubSubEngine
            umlShape.SetEventHandler(eventHandler)

        umlFrame.refresh()

        self._baseWxCreateLogger.info(f'Created {self._shape}')

    def _removeLinkedUmlShapeFromFrame(self, umlFrame: UmlFrame, umlShape: UmlShapeGenre, modelClass: LinkedObject | None = None):

        from umlshapes.ShapeTypes import UmlShapes

        umlShapes: UmlShapes = umlFrame.umlShapes

        for obj in umlShapes:

            potentialObject: UmlClass = cast(UmlClass, obj)
            #
            #  Assumes UML Shapes use the IdentifierMixin
            #
            if umlShape == potentialObject:
                umlDiagram:   UmlDiagram   = umlFrame.umlDiagram
                linkedObject: LinkedObject = self._getLinkedObject(umlShape=potentialObject)

                if modelClass in linkedObject.parents:
                    self._baseWxCreateLogger.warning(f'Removing {modelClass=} from {linkedObject=}')
                    for parent in linkedObject.parents:
                        umlDiagram.RemoveShape(parent)

                umlDiagram.RemoveShape(potentialObject)
                self._baseWxCreateLogger.info(f'{potentialObject} deleted')
                umlFrame.refresh()

    def _getLinkedObject(self, umlShape: UmlShapeGenre) -> LinkedObject:

        if isinstance(umlShape, UmlActor) is True:
            umlActor: UmlActor = cast(UmlActor, umlShape)       # noqa
            return umlActor.modelActor
        elif isinstance(umlShape, UmlClass) is True:
            umlClass: UmlClass = cast(UmlClass, umlShape)       # noqa
            return umlClass.modelClass
        elif isinstance(umlShape, UmlNote) is True:
            umlNote: UmlNote = cast(UmlNote, umlShape)          # noqa
            return umlNote.modelNote
        else:
            umlUseCase: UmlUseCase = cast(UmlUseCase, umlShape)     # noqa
            return umlUseCase.modelUseCase
