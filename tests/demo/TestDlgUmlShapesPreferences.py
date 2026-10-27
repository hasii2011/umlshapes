from unittest import main as unitTestMain

from wx import OK
from wx import ID_OK
from wx import CommandEvent
from wx import EVT_BUTTON

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from tests.demo.DlgUmlShapesPreferences import DlgUmlShapesPreferences


class TestDlgUmlShapesPreferences(UnitTestBaseW):

    def testOpenAndClosePreferencesDialog(self):
        with DlgUmlShapesPreferences(parent=self._listeningWindow) as dlg:
            self.assertIsNotNone(dlg)
            okBtn = dlg.FindWindowById(ID_OK)
            evt = CommandEvent(EVT_BUTTON.typeId, ID_OK)
            evt.SetEventObject(okBtn)
            dlg.GetEventHandler().ProcessEvent(evt)


if __name__ == '__main__':
    unitTestMain()
