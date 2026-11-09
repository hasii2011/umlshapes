
from typing import cast

from logging import Logger
from logging import getLogger

from umlshapes.commands.CreateUmlActorCommand import CreateUmlActorCommand
from umlshapes.commands.CreateUmlClassCommand import CreateUmlClassCommand
from umlshapes.commands.CreateUmlNoteCommand import CreateUmlNoteCommand
from umlshapes.commands.CreateUmlTextCommand import CreateUmlTextCommand
from umlshapes.commands.CreateUmlUseCaseCommand import CreateUmlUseCaseCommand

from umlshapes.shapes.UmlActor import UmlActor
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlText import UmlText
from umlshapes.shapes.UmlUseCase import UmlUseCase

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.types.UmlPosition import UmlPosition

from tests.demo.DemoCommon import INITIAL_X
from tests.demo.DemoCommon import INITIAL_Y


class ShapeCreator:

    def __init__(self, umlPubSubEngine: UmlPubSubEngine):

        self.logger: Logger = getLogger(__name__)

        self._umlPubSubEngine: UmlPubSubEngine = umlPubSubEngine
        self._preferences:     UmlPreferences  = UmlPreferences()
        self._currentPosition: UmlPosition     = UmlPosition(x=INITIAL_X, y=INITIAL_Y)

    def displayUndoableUmlClass(self, diagramFrame: UmlFrame, umlPosition: UmlPosition | None = None) -> UmlClass:

        if umlPosition is None:
            umlPosition = self._computePosition()

        cmd: CreateUmlClassCommand = CreateUmlClassCommand(
            umlFrame=diagramFrame,
            umlPosition=umlPosition,
            umlPubSubEngine=self._umlPubSubEngine
        )
        submitStatus: bool = diagramFrame.commandProcessor.Submit(command=cmd, storeIt=True)
        self.logger.debug(f'Create class submission status: {submitStatus}')
        return cast(UmlClass, cmd.shape)

    def displayUndoableUmlNote(self, diagramFrame: UmlFrame, umlPosition: UmlPosition | None = None) -> UmlNote:

        if umlPosition is None:
            umlPosition = self._computePosition()

        cmd: CreateUmlNoteCommand = CreateUmlNoteCommand(
            umlFrame=diagramFrame,
            umlPosition=umlPosition,
            umlPubSubEngine=self._umlPubSubEngine
        )

        submitStatus: bool = diagramFrame.commandProcessor.Submit(command=cmd, storeIt=True)
        self.logger.debug(f'Create note submission status: {submitStatus}')
        return cast(UmlNote, cmd.shape)

    def displayUndoableUmlText(self, diagramFrame: UmlFrame, umlPosition: UmlPosition | None = None) -> UmlText:

        if umlPosition is None:
            umlPosition = self._computePosition()

        cmd: CreateUmlTextCommand = CreateUmlTextCommand(
            umlFrame=diagramFrame,
            umlPosition=umlPosition,
            umlPubSubEngine=self._umlPubSubEngine
        )

        submitStatus: bool = diagramFrame.commandProcessor.Submit(command=cmd, storeIt=True)
        self.logger.debug(f'Create text submission status: {submitStatus}')
        return cast(UmlText, cmd.shape)

    def displayUndoableUmlActor(self, diagramFrame: UmlFrame, umlPosition: UmlPosition | None = None) -> UmlActor:
        if umlPosition is None:
            umlPosition = self._computePosition()

        cmd: CreateUmlActorCommand = CreateUmlActorCommand(
            umlFrame=diagramFrame,
            umlPosition=umlPosition,
            umlPubSubEngine=self._umlPubSubEngine
        )

        submitStatus: bool = diagramFrame.commandProcessor.Submit(command=cmd, storeIt=True)
        self.logger.debug(f'Create actor submission status: {submitStatus}')
        return cast(UmlActor, cmd.shape)

    def displayUndoableUmlUseCase(self, diagramFrame: UmlFrame, umlPosition: UmlPosition | None = None) -> UmlUseCase:
        if umlPosition is None:
            umlPosition = self._computePosition()

        cmd: CreateUmlUseCaseCommand = CreateUmlUseCaseCommand(
            umlFrame=diagramFrame,
            umlPosition=umlPosition,
            umlPubSubEngine=self._umlPubSubEngine
        )

        submitStatus: bool = diagramFrame.commandProcessor.Submit(command=cmd, storeIt=True)
        self.logger.debug(f'Create use case submission status: {submitStatus}')
        return cast(UmlUseCase, cmd.shape)

    def _computePosition(self) -> UmlPosition:
        """
        TODO: Put in an option to compute position or just put at a fixed
        place.  For UI testing we want fixed

        Returns:

        """

        currentPosition: UmlPosition = UmlPosition(x=self._currentPosition.x, y=self._currentPosition.y)

        # self._currentPosition.x += INCREMENT_X
        # self._currentPosition.y += INCREMENT_Y

        return currentPosition
