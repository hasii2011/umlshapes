
from wx import CommandEvent
from wx import EVT_CHECKBOX
from wx import ICON_INFORMATION
from wx import OK
from wx import RichMessageDialog
from wx import Window

from umlshapes.preferences.UmlPreferences import UmlPreferences

LOLLIPOP_PLACEMENT_MESSAGE:        str = 'Click on the UML Class edge where you want to place the interface'
LOLLIPOP_PLACEMENT_CAPTION:        str = 'Place Interface'
LOLLIPOP_PLACEMENT_CHECKBOX_LABEL: str = 'Show this dialog next time'


class DlgDisplayLollipopPlacementMsg(RichMessageDialog):
    """
    Instructions dialog for placing a lollipop interface on a UML Class shape.
    Encapsulates the RichMessageDialog and consolidates the preference callback
    logic so that when the user unchecks the checkbox, the preference is set to False.
    """

    def __init__(self, parent: Window, preferences: UmlPreferences | None = None):
        """
        Args:
            parent: The parent window.
            preferences: Optional UmlPreferences instance to update on dismissal.
        """
        super().__init__(
            parent=parent,
            message=LOLLIPOP_PLACEMENT_MESSAGE,
            caption=LOLLIPOP_PLACEMENT_CAPTION,
            style=OK | ICON_INFORMATION
        )
        self._preferences: UmlPreferences | None = preferences
        initialChecked: bool = True
        if self._preferences is not None:
            initialChecked = self._preferences.showLollipopPlacementDialog

        self.ShowCheckBox(checkBoxText=LOLLIPOP_PLACEMENT_CHECKBOX_LABEL, checked=initialChecked)
        self.Bind(EVT_CHECKBOX, self._onCheckBoxChanged)

    def ShowModal(self) -> int:
        returnCode: int = super().ShowModal()
        intChecked: int = 0
        if self.IsCheckBoxChecked() is True:
            intChecked = 1

        commandEvent: CommandEvent = CommandEvent(EVT_CHECKBOX.typeId, self.GetId())
        commandEvent.SetInt(intChecked)
        self._onCheckBoxChanged(commandEvent)
        return returnCode

    def _onCheckBoxChanged(self, event: CommandEvent):
        """
        Callback invoked when the checkbox is toggled.
        Updates the showLollipopPlacementDialog preference.

        Args:
            event: The incoming CommandEvent from the checkbox.
        """
        newValue: bool = event.IsChecked()
        if self._preferences is not None:
            self._preferences.showLollipopPlacementDialog = newValue
