
from typing import cast

from logging import Logger
from logging import getLogger

from datetime import datetime

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

    @property
    def timeStamp(self) -> int:

        dt = datetime.now()

        return dt.microsecond

    def GetName(self) -> str:
        return self._name

    def CanUndo(self):
        return True

    def _removeUmlShapeFromFrame(self, umlFrame: UmlFrame, umlShape: UmlShapeGenre, modelClass: LinkedObject | None = None):

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
                    self._baseLogger.warning(f'Removing {modelClass=} from {linkedObject=}')
                    for parent in linkedObject.parents:
                        umlDiagram.RemoveShape(parent)

                umlDiagram.RemoveShape(potentialObject)
                self._baseLogger.info(f'{potentialObject} deleted')
                umlFrame.refresh()

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
