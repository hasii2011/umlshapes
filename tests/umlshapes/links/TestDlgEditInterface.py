from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from wx import CommandEvent
from wx import ID_OK
from wx.lib.ogl import OGLInitialize

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from umlmodel.Class import Class
from umlmodel.Interface import Interface
from umlmodel.Interface import Interfaces
from umlmodel.Method import Method
from umlmodel.ModelTypes import ClassName

from umlshapes.dialogs.DlgEditInterface import DlgEditInterface
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

IMPLEMENTING_CLASS_NAME: str = 'OrderService'
INITIAL_INTERFACE_NAME:  str = 'Interface0'
EXISTING_INTERFACE_NAME: str = 'IExistingService'
NEW_INTERFACE_NAME:      str = 'INewService'


class TestDlgEditInterface(UnitTestBaseW):
    """
    Unit tests for DlgEditInterface validating interface selection and creation.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        OGLInitialize()
        self._umlPubSubEngine: IUmlPubSubEngine = UmlPubSubEngine()
        self._classDiagramFrame: ClassDiagramFrame = ClassDiagramFrame(
            parent=self._listeningWindow,
            umlPubSubEngine=self._umlPubSubEngine
        )

    def tearDown(self):
        super().tearDown()

    def testEmptyInterfaceNameRejectionOnOk(self):
        """
        Verify that clicking OK with an empty interface name is rejected and does not close dialog.
        """
        initialInterface: Interface = Interface(INITIAL_INTERFACE_NAME)
        initialInterface.addImplementor(ClassName(IMPLEMENTING_CLASS_NAME))
        umlLollipop: UmlLollipopInterface = UmlLollipopInterface(interface=initialInterface)
        existingInterfaces: Interfaces = Interfaces([])

        with DlgEditInterface(
            parent=self._classDiagramFrame,
            umlPubSubEngine=self._umlPubSubEngine,
            lollipopInterface=umlLollipop,
            interfaces=existingInterfaces,
            editMode=False
        ) as dlg:
            cmdEvent: CommandEvent = CommandEvent()
            dlg._onOk(cmdEvent)

            self.assertNotEqual(ID_OK, dlg.GetReturnCode())
            self.assertEqual('', dlg._interfaceNameControl.GetValue())

    def testSpecifyNewInterfaceName(self):
        """
        Verify specifying a new interface name updates modelInterface without AttributeError.
        """
        initialInterface: Interface = Interface(INITIAL_INTERFACE_NAME)
        initialInterface.addImplementor(ClassName(IMPLEMENTING_CLASS_NAME))
        umlLollipop: UmlLollipopInterface = UmlLollipopInterface(interface=initialInterface)
        existingInterfaces: Interfaces = Interfaces([])

        with DlgEditInterface(
            parent=self._classDiagramFrame,
            umlPubSubEngine=self._umlPubSubEngine,
            lollipopInterface=umlLollipop,
            interfaces=existingInterfaces,
            editMode=False
        ) as dlg:
            dlg._interfaceNameControl.SetValue(NEW_INTERFACE_NAME)
            cmdEvent: CommandEvent = CommandEvent()
            dlg._onOk(cmdEvent)

            self.assertEqual(ID_OK, dlg.GetReturnCode())
            self.assertEqual(NEW_INTERFACE_NAME, umlLollipop.modelInterface.name)
            self.assertIn(ClassName(IMPLEMENTING_CLASS_NAME), umlLollipop.modelInterface.implementors)

    def testSelectExistingInterface(self):
        """
        Verify selecting an existing interface loads its methods and adds the implementor.
        """
        initialInterface: Interface = Interface(INITIAL_INTERFACE_NAME)
        initialInterface.addImplementor(ClassName(IMPLEMENTING_CLASS_NAME))
        umlLollipop: UmlLollipopInterface = UmlLollipopInterface(interface=initialInterface)

        existingInterface: Interface = Interface(EXISTING_INTERFACE_NAME)
        existingInterface.methods.append(Method(name='execute'))
        existingInterfaces: Interfaces = Interfaces([existingInterface])

        with DlgEditInterface(
            parent=self._classDiagramFrame,
            umlPubSubEngine=self._umlPubSubEngine,
            lollipopInterface=umlLollipop,
            interfaces=existingInterfaces,
            editMode=False
        ) as dlg:
            changeEvent: CommandEvent = CommandEvent()
            changeEvent.SetString(EXISTING_INTERFACE_NAME)
            dlg._onInterfaceNameChanged(changeEvent)
            dlg._interfaceNameControl.SetValue(EXISTING_INTERFACE_NAME)

            cmdEvent: CommandEvent = CommandEvent()
            dlg._onOk(cmdEvent)

            self.assertEqual(ID_OK, dlg.GetReturnCode())
            self.assertEqual(EXISTING_INTERFACE_NAME, umlLollipop.modelInterface.name)
            self.assertEqual(1, len(umlLollipop.modelInterface.methods))
            self.assertEqual('execute', umlLollipop.modelInterface.methods[0].name)
            self.assertIn(ClassName(IMPLEMENTING_CLASS_NAME), umlLollipop.modelInterface.implementors)


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(testCaseClass=TestDlgEditInterface))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
