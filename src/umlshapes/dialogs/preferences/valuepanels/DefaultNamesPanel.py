
from typing import Callable
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx import EVT_TEXT
from wx import ID_ANY

from wx import CommandEvent
from wx import StaticText
from wx import TextCtrl
from wx import Window

from wx.lib.sized_controls import SizedPanel

from umlshapes.preferences.UmlPreferences import UmlPreferences


@dataclass
class NameData:
    textCtrl:     TextCtrl = cast(TextCtrl, None)       # noqa
    label:        str      = ''
    initialValue: str = ''
    callback:     Callable = cast(Callable, None)       # noqa


class DefaultNamesPanel(SizedPanel):
    """
    A form for all the default object names
    """

    def __init__(self, parent: Window):

        self.logger:       Logger          = getLogger(__name__)
        self._preferences: UmlPreferences = UmlPreferences()
        super().__init__(parent)

        self.SetSizerType('form')
        #
        p: UmlPreferences = self._preferences
        self._nameData: List[NameData] = [
            NameData(label='Interface Name: ',   callback=self._onInterfaceNameChanged,   initialValue=p.defaultNameInterface),
            NameData(label='Use Case Name: ',    callback=self._onUseCaseNameChanged,     initialValue=p.defaultNameUsecase),
            NameData(label='Actor Name: ',       callback=self._onActorNameChanged,       initialValue=p.defaultNameActor),
            NameData(label='Method Name: ',      callback=self._onMethodNameChanged,      initialValue=p.defaultNameMethod),
            NameData(label='Field Name: ',       callback=self._onFieldNameChanged,       initialValue=p.defaultNameField),
            NameData(label='Parameter Name: ',   callback=self._onParameterNameChanged,   initialValue=p.defaultNameParameter),
            NameData(label='Association Name: ', callback=self._onAssociationNameChanged, initialValue=p.defaultAssociationName),
        ]
        for nameData in self._nameData:

            sText = StaticText(self, ID_ANY, nameData.label)
            sText.SetSizerProps(valign='center')

            nameData.textCtrl = TextCtrl(self, value=nameData.initialValue)
            nameData.textCtrl.SetSizerProps(expand=True, valign='center')

            parent.Bind(EVT_TEXT, nameData.callback, nameData.textCtrl)

    def _onInterfaceNameChanged(self, event: CommandEvent):
        newValue: str = event.GetString()
        self._preferences.defaultNameInterface = newValue

    def _onUseCaseNameChanged(self, event: CommandEvent):
        newValue: str = event.GetString()
        self._preferences.defaultNameUsecase = newValue

    def _onActorNameChanged(self, event: CommandEvent):
        newValue: str = event.GetString()
        self._preferences.defaultNameActor = newValue

    def _onMethodNameChanged(self, event: CommandEvent):
        newValue: str = event.GetString()
        self._preferences.defaultNameMethod = newValue

    def _onFieldNameChanged(self, event: CommandEvent):
        newValue: str = event.GetString()
        self._preferences.defaultNameField = newValue

    def _onParameterNameChanged(self, event: CommandEvent):
        newValue: str = event.GetString()
        self._preferences.defaultNameParameter = newValue

    def _onAssociationNameChanged(self, event: CommandEvent):
        newValue: str = event.GetString()
        self._preferences.defaultAssociationName = newValue
