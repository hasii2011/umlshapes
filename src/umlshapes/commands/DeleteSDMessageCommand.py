from datetime import datetime
from logging import Logger
from logging import getLogger
from typing import Optional
from typing import cast
from typing import TYPE_CHECKING

from wx import Command

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.sd.UmlSDMessage import UmlSDMessage
from umlshapes.sd.UmlSDMessageLabel import UmlSDMessageLabel
from umlshapes.UmlDiagram import UmlDiagram

if TYPE_CHECKING:
    from umlshapes.frames.UmlFrame import UmlFrame
    from umlshapes.sd.UmlSDLifeLine import UmlSDLifeLine


class DeleteSDMessageCommand(Command):
    """
    Command to delete and restore an UmlSDMessage in a sequence diagram.
    """

    def __init__(self, partialName: str, umlSDMessage: UmlSDMessage, umlPubSubEngine: IUmlPubSubEngine):

        self.logger: Logger = getLogger(__name__)

        self._umlSDMessage:    UmlSDMessage     = umlSDMessage
        self._umlPubSubEngine: IUmlPubSubEngine = umlPubSubEngine
        self._umlFrame:        'UmlFrame'       = umlSDMessage.umlFrame

        self._fromLifeLine: Optional['UmlSDLifeLine'] = cast(Optional['UmlSDLifeLine'], umlSDMessage.GetFrom())
        self._toLifeLine:   Optional['UmlSDLifeLine'] = cast(Optional['UmlSDLifeLine'], umlSDMessage.GetTo())

        self._name: str = f'{partialName}-{self.timeStamp}'

        super().__init__(canUndo=True, name=self._name)

    @property
    def timeStamp(self) -> int:
        dt: datetime = datetime.now()
        return dt.microsecond

    def GetName(self) -> str:
        return self._name

    def CanUndo(self) -> bool:
        return True

    def Do(self) -> bool:
        """
        Delete the SD message from the diagram and lifelines.
        """
        umlDiagram: UmlDiagram = self._umlFrame.umlDiagram

        self._umlSDMessage.selected = False

        messageLabel: Optional[UmlSDMessageLabel] = self._umlSDMessage.messageLabel
        if messageLabel is not None:
            messageLabel.Select(False)
            umlDiagram.RemoveShape(messageLabel)
            messageLabel.Show(False)

        if self._fromLifeLine is not None and self._umlSDMessage in self._fromLifeLine.GetLines():
            self._fromLifeLine.GetLines().remove(self._umlSDMessage)

        if self._toLifeLine is not None and self._umlSDMessage in self._toLifeLine.GetLines():
            self._toLifeLine.GetLines().remove(self._umlSDMessage)

        umlDiagram.RemoveShape(self._umlSDMessage)
        self._umlSDMessage.Show(False)

        self._umlFrame.refresh()
        return True

    def Undo(self) -> bool:
        """
        Restore the SD message to the diagram and lifelines.
        """
        umlDiagram: UmlDiagram = self._umlFrame.umlDiagram

        if self._fromLifeLine is not None:
            self._umlSDMessage.SetFrom(self._fromLifeLine)
            if self._umlSDMessage not in self._fromLifeLine.GetLines():
                self._fromLifeLine.GetLines().append(self._umlSDMessage)

        if self._toLifeLine is not None:
            self._umlSDMessage.SetTo(self._toLifeLine)
            if self._umlSDMessage not in self._toLifeLine.GetLines():
                self._toLifeLine.GetLines().append(self._umlSDMessage)

        umlDiagram.AddShape(self._umlSDMessage)
        self._umlSDMessage.Show(True)

        messageLabel: Optional[UmlSDMessageLabel] = self._umlSDMessage.messageLabel
        if messageLabel is not None:
            umlDiagram.AddShape(messageLabel)
            messageLabel.Show(True)

        self._umlFrame.refresh()
        return True
