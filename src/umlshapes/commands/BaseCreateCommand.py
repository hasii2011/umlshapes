
from typing import Dict
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
from umlshapes.shapes.eventhandlers.UmlActorEventHandler import UmlActorEventHandler

from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler
from umlshapes.shapes.eventhandlers.UmlNoteEventHandler import UmlNoteEventHandler
from umlshapes.shapes.eventhandlers.UmlTextEventHandler import UmlTextEventHandler
from umlshapes.shapes.eventhandlers.UmlUseCaseEventHandler import UmlUseCaseEventHandler

from umlshapes.types.UmlPosition import UmlPosition

class MyMetaCommand(ABCMeta, type(Command)):        # type: ignore
    """
    I have no idea why this works:
    https://stackoverflow.com/questions/66591752/metaclass-conflict-when-trying-to-create-a-python-abstract-class-that-also-subcl
    """
    pass


HANDLER_MAP: Dict[type[UmlShapeGenre], type[UmlBaseEventHandler]] = {
    UmlClass:   UmlClassEventHandler,
    UmlNote:    UmlNoteEventHandler,
    UmlText:    UmlTextEventHandler,
    UmlActor:   UmlActorEventHandler,
    UmlUseCase: UmlUseCaseEventHandler,
}

ATTRIBUTE_NAME_MAP: Dict[type[UmlShapeGenre], str] = {
    UmlActor:   'modelActor',
    UmlClass:   'modelClass',
    UmlNote:    'modelNote',
    UmlUseCase: 'modelUseCase',
}


# noinspection PyAbstractClass
class BaseCreateCommand(Command, metaclass=MyMetaCommand):
    """
    Used no-inspection because Pycharm seems to think this class is not abstract
    """
    def __init__(self, canUndo: bool, name: str, umlPubSubEngine: IUmlPubSubEngine, umlFrame: UmlFrame, umlPosition: UmlPosition):

        super().__init__(canUndo=canUndo, name=name)

        self.logger:       Logger      = getLogger(__name__)
        self._umlFrame:    UmlFrame    = umlFrame
        self._umlPosition: UmlPosition = umlPosition

        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine
        self._umlPreferences:  UmlPreferences   = UmlPreferences()
        self._shape:           UmlShapeGenre    = self._createPrototypeInstance()

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
        This is common code needed to create Class, Note, Text, Actor, and UseCase shapes.

        Args:
            umlFrame:
            umlShape:
            umlPosition:
        """
        self.logger.debug(f'{umlFrame=}')

        umlShape.position = umlPosition
        umlDiagram: UmlDiagram = umlFrame.umlDiagram
        umlDiagram.AddShape(umlShape)

        umlShape.Show(show=True)

        handlerClass = HANDLER_MAP.get(type(umlShape))
        if handlerClass is None:
            raise NotImplementedError(f'No event handler for: {type(umlShape)=}')

        eventHandler: UmlBaseEventHandler = handlerClass(previousEventHandler=umlShape.GetEventHandler())
        eventHandler.SetShape(umlShape)
        eventHandler.umlPubSubEngine = self._umlPubSubEngine
        umlShape.SetEventHandler(eventHandler)

        umlFrame.refresh()

        self.logger.info(f'Created {type(self._shape)=}')

    def _removeLinkedUmlShapeFromFrame(self, umlFrame: UmlFrame, umlShape: UmlShapeGenre, modelClass: LinkedObject | None = None):

        from umlshapes.ShapeTypes import UmlShapes

        umlShapes: UmlShapes = umlFrame.umlShapes

        for obj in umlShapes:

            potentialObject: UmlShapeGenre = cast(UmlShapeGenre, obj)
            #
            #  Assumes UML Shapes use the IdentifierMixin
            #
            if umlShape == potentialObject:
                umlDiagram:   UmlDiagram   = umlFrame.umlDiagram
                linkedObject: LinkedObject = self._getLinkedObject(umlShape=potentialObject)

                if modelClass in linkedObject.parents:
                    self.logger.warning(f'Removing {modelClass=} from {linkedObject=}')
                    for parent in linkedObject.parents:
                        umlDiagram.RemoveShape(parent)

                umlDiagram.RemoveShape(potentialObject)
                self.logger.info(f'{potentialObject} deleted')
                umlFrame.refresh()

    def _getLinkedObject(self, umlShape: UmlShapeGenre) -> LinkedObject:
        """
        Retrieves the model object for a UML Shape.

        Args:
            umlShape:  The shape to get the model for

        Returns: The linked model object
        """
        attr_name = ATTRIBUTE_NAME_MAP.get(type(umlShape))
        if attr_name is None:
            raise NotImplementedError(f'Unhandled UML Shape: {type(umlShape)=}')

        return getattr(umlShape, attr_name)
