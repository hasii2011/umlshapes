
from typing import cast

from logging import Logger
from logging import getLogger

from wx import Command

from umlmodel.LinkedObject import LinkedObject

from umlshapes.ShapeTypes import UmlShapeGenre
from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.shapes.UmlActor import UmlActor
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlUseCase import UmlUseCase
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.ShapeTypes import UmlShapes

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine


class BaseWxCommand(Command):

    def __init__(self, canUndo: bool, name: str, umlPubSubEngine: IUmlPubSubEngine):
        """

        Args:
            canUndo:
            name:
            umlPubSubEngine:
        """
        super().__init__(canUndo=canUndo, name=name)

        self._baseLogger:      Logger           = getLogger(__name__)
        self._name:            str              = name
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine

        self._umlPreferences:  UmlPreferences        = UmlPreferences()

    def _removeUmlShapeFromFrame(self, umlFrame: UmlFrame, umlShape: UmlShapeGenre, modelClass: LinkedObject | None = None):

        umlShapes: UmlShapes = umlFrame.umlShapes

        for obj in umlShapes:

            potentialObject: UmlClass = cast(UmlClass, obj)

            # TODO: implement __eq__ for UmlNote, UmlText, UmlUseCase, UmlActor
            # if self._isSameShape(objectToRemove=umlShape, potentialObject=potentialObject):
            if umlShape == potentialObject:
                umlDiagram:   UmlDiagram   = umlFrame.umlDiagram
                linkedObject: LinkedObject = self._getLinkedObject(umlShape=potentialObject)

                if modelClass in linkedObject.parents:
                    self._baseLogger.warning(f'Removing {modelClass=} from {linkedObject=}')
                    for parent in linkedObject.parents:
                        umlDiagram.RemoveShape(parent)

                umlDiagram.RemoveShape(potentialObject)
                self._baseLogger.info(f'{potentialObject} deleted')
                umlFrame.refresh()

    def _isSameShape(self, objectToRemove: UmlShapeGenre, potentialObject: UmlShapeGenre) -> bool:
        """
        This probably could be done by updating the UML Shapes with the __equ__ dunder method.
        Wait until the umlshapes project updates

        Args:
            objectToRemove:   Object we were told to remove
            potentialObject:  The one that is on the frame

        Returns:  `True` if they are one and the same, else `False`

        """
        ans: bool = False

        # if isinstance(objectToRemove, UmlSDInstance):
        #     nonOglObject: OglSDInstance = cast(OglSDInstance, objectToRemove)
        #     if nonOglObject.sdInstance.id == nonOglObject.sdInstance.id:
        #         ans = True
        # else:
        if objectToRemove.id == potentialObject.id:
            ans = True

        return ans

    def _getLinkedObject(self, umlShape: UmlActor | UmlClass | UmlNote | UmlUseCase) -> LinkedObject:

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
