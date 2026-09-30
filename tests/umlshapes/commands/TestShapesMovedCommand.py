
from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from umlshapes.commands.CreateUmlClassCommand import CreateUmlClassCommand
from umlshapes.commands.ShapesMovedCommand import DEFAULT_NAME_PREFIX
from umlshapes.commands.ShapesMovedCommand import ShapesMovedCommand
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.frames.ShapeMoveInfo import InitialPositions
from umlshapes.frames.ShapeMoveInfo import MovedShapes
from umlshapes.frames.ShapeMoveInfo import ShapeId
from umlshapes.frames.ShapeMoveInfo import ShapeMoveInfo
from umlshapes.lib.ogl import OGLInitialize
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.types.UmlPosition import UmlPosition


class TestShapesMovedCommand(UnitTestBaseW):
    """
    Unit tests for ShapesMovedCommand.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        OGLInitialize()
        self._umlPubSubEngine:   IUmlPubSubEngine  = UmlPubSubEngine()
        self._classDiagramFrame: ClassDiagramFrame = ClassDiagramFrame(parent=self._listeningWindow, umlPubSubEngine=self._umlPubSubEngine)

    def tearDown(self):
        super().tearDown()

    def testDefaultName(self):
        """
        Verify default command name prefix uses DEFAULT_NAME_PREFIX.
        """
        initialPos:       UmlPosition      = UmlPosition(x=100, y=100)
        umlClass:         UmlClass         = self._createTestUmlClass(position=initialPos)
        shapeId:          ShapeId          = ShapeId(str(umlClass.id))
        initialPositions: InitialPositions = InitialPositions({shapeId: initialPos})
        movedShapes:      MovedShapes      = MovedShapes({
            shapeId: ShapeMoveInfo(umlShape=umlClass, originalPosition=initialPos)
        })

        command: ShapesMovedCommand = ShapesMovedCommand(
            umlFrame=self._classDiagramFrame,
            movedShapes=movedShapes,
            initialPositions=initialPositions
        )

        self.assertTrue(command.commandName.startswith(f'{DEFAULT_NAME_PREFIX}-'))
        self.assertEqual(command.commandName, command.GetName())

    def testAlternateName(self):
        """
        Verify alternate command name prefix overrides default prefix.
        """
        customPrefix:     str              = 'CustomMove'
        initialPos:       UmlPosition      = UmlPosition(x=100, y=100)
        umlClass:         UmlClass         = self._createTestUmlClass(position=initialPos)
        shapeId:          ShapeId          = ShapeId(str(umlClass.id))
        initialPositions: InitialPositions = InitialPositions({shapeId: initialPos})
        movedShapes:      MovedShapes      = MovedShapes({
            shapeId: ShapeMoveInfo(umlShape=umlClass, originalPosition=initialPos)
        })

        command: ShapesMovedCommand = ShapesMovedCommand(
            umlFrame=self._classDiagramFrame,
            movedShapes=movedShapes,
            initialPositions=initialPositions,
            name=customPrefix
        )

        self.assertTrue(command.commandName.startswith(f'{customPrefix}-'))
        self.assertEqual(command.commandName, command.GetName())

    def testCommandNamePropertySetter(self):
        """
        Verify commandName property getter and setter update name.
        """
        initialPos:       UmlPosition      = UmlPosition(x=100, y=100)
        umlClass:         UmlClass         = self._createTestUmlClass(position=initialPos)
        shapeId:          ShapeId          = ShapeId(str(umlClass.id))
        initialPositions: InitialPositions = InitialPositions({shapeId: initialPos})
        movedShapes:      MovedShapes      = MovedShapes({
            shapeId: ShapeMoveInfo(umlShape=umlClass, originalPosition=initialPos)
        })

        command: ShapesMovedCommand = ShapesMovedCommand(
            umlFrame=self._classDiagramFrame,
            movedShapes=movedShapes,
            initialPositions=initialPositions
        )

        updatedName: str = 'UpdatedCommandName-12345'
        command.commandName = updatedName

        self.assertEqual(command.commandName, updatedName)
        self.assertEqual(command.GetName(), updatedName)

    def testDoUndoRedo(self):
        """
        Verify Do, Undo, and Redo operations restore and reapply positions.
        """
        initialPos: UmlPosition = UmlPosition(x=100, y=100)
        finalPos:   UmlPosition = UmlPosition(x=250, y=300)
        umlClass:   UmlClass    = self._createTestUmlClass(position=initialPos)
        shapeId:    ShapeId     = ShapeId(str(umlClass.id))

        # Simulate shape being moved to final position
        umlClass.position = finalPos

        initialPositions: InitialPositions = InitialPositions({shapeId: initialPos})
        movedShapes:      MovedShapes      = MovedShapes({
            shapeId: ShapeMoveInfo(umlShape=umlClass, originalPosition=initialPos)
        })

        command: ShapesMovedCommand = ShapesMovedCommand(
            umlFrame=self._classDiagramFrame,
            movedShapes=movedShapes,
            initialPositions=initialPositions
        )

        # Do
        doResult: bool = command.Do()
        self.assertTrue(doResult)
        self.assertEqual(umlClass.position, finalPos)

        # Undo
        undoResult: bool = command.Undo()
        self.assertTrue(undoResult)
        self.assertEqual(umlClass.position, initialPos)

        # Redo
        redoResult: bool = command.Redo()
        self.assertTrue(redoResult)
        self.assertEqual(umlClass.position, finalPos)

    def _createTestUmlClass(self, position: UmlPosition) -> UmlClass:

        createUmlClassCommand: CreateUmlClassCommand = CreateUmlClassCommand(
            umlFrame=self._classDiagramFrame,
            umlPosition=position,
            umlPubSubEngine=self._umlPubSubEngine,
            modelClass=None
        )
        umlClass: UmlClass = createUmlClassCommand._createPrototypeInstance()
        umlClass.umlFrame = self._classDiagramFrame
        umlClass.position = position

        self._classDiagramFrame.umlDiagram.AddShape(umlClass)

        return umlClass


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(testCaseClass=TestShapesMovedCommand))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
