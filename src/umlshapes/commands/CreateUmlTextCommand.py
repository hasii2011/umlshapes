
from typing import cast

from umlmodel.Text import Text

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.shapes.UmlText import UmlText

from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.pubsubengine.UmlMessageType import UmlMessageType
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.commands.BaseCreateCommand import BaseCreateCommand


class CreateUmlTextCommand(BaseCreateCommand):
    """
    Command that creates a new UML Text on the UML frame
    """

    def __init__(self, umlFrame: UmlFrame, umlPosition: UmlPosition, umlPubSubEngine: IUmlPubSubEngine):

        self._uniqueId: int = self.timeStamp

        name: str = f'Create Text-{self._uniqueId}'

        super().__init__(canUndo=True, name=name, umlFrame=umlFrame, umlPosition=umlPosition, umlPubSubEngine=umlPubSubEngine)

    def _createPrototypeInstance(self) -> UmlText:
        """
        Creates an appropriate UML shape for the new command

        Returns:    The newly created text shape
        """
        textName: str = f'UmlText{self._uniqueId}'

        text: Text = Text(content=self._umlPreferences.textValue)
        text.name = textName

        umlText: UmlText = UmlText(text)

        return umlText

    def _placeShapeOnFrame(self):
        """
        Place self._shape on the UML frame
        """
        umlText:   UmlText = cast(UmlText, self._shape)     # noqa             # get old
        modelText: Text    = umlText.modelText

        self._addUmlShapeToFrame(umlFrame=self._umlFrame, umlShape=umlText, umlPosition=self._umlPosition)

        self._umlFrame.refresh()

        self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.EDIT_TEXT, frameId=self._umlFrame.id, modelText=modelText)
