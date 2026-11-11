
from typing import cast

from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from umlmodel.Class import Class

from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler
from umlshapes.commands.ClassPasteCommand import ClassPasteCommand
from umlshapes.commands.CreateUmlClassCommand import CreateUmlClassCommand
from umlshapes.commands.ShapesMovedCommand import DEFAULT_NAME_PREFIX
from umlshapes.commands.ShapesMovedCommand import ShapesMovedCommand
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.frames.ShapeMoveInfo import InitialPositions
from umlshapes.frames.ShapeMoveInfo import MovedShapes
from umlshapes.frames.ShapeMoveInfo import ShapeId
from umlshapes.frames.ShapeMoveInfo import ShapeMoveInfo
from wx.lib.ogl import OGLInitialize
from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.types.UmlPosition import UmlPosition


class TestShapesMovedCommand(UnitTestBaseW):
    """
    Unit tests for ShapesMovedCommand and grid snapping behavior.
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

    def testDiagramSnapAndGridSpacing(self):
        """
        Verify DiagramFrame initializes grid spacing from preferences and
        UmlDiagram.Snap rounds to the nearest grid multiple without +0.5 bias.
        """
        preferences: UmlPreferences = UmlPreferences()
        self.assertEqual(
            self._classDiagramFrame.umlDiagram.GetGridSpacing(),
            preferences.backgroundGridInterval
        )

        self._classDiagramFrame.umlDiagram.SetGridSpacing(25)
        self._classDiagramFrame.umlDiagram.SetSnapToGrid(True)

        snappedX: int
        snappedY: int
        snappedX, snappedY = self._classDiagramFrame.umlDiagram.Snap(x=1, y=12)
        self.assertEqual((snappedX, snappedY), (0, 0))

        snappedX, snappedY = self._classDiagramFrame.umlDiagram.Snap(x=13, y=26)
        self.assertEqual((snappedX, snappedY), (25, 25))

        self._classDiagramFrame.umlDiagram.SetSnapToGrid(False)
        snappedX, snappedY = self._classDiagramFrame.umlDiagram.Snap(x=13, y=26)
        self.assertEqual((snappedX, snappedY), (13, 26))

    def testCreateAndPasteCommandsSnapTopLeftToGrid(self):
        """
        Verify BaseCreateCommand._addUmlShapeToFrame and BaseCommand._setupUmlShape
        snap the shape's top-left position to the grid when snapToGrid is enabled.
        """
        self._classDiagramFrame.umlDiagram.SetGridSpacing(25)
        self._classDiagramFrame.umlDiagram.SetSnapToGrid(True)

        unsnappedPos: UmlPosition = UmlPosition(x=108, y=114)
        createCommand: CreateUmlClassCommand = CreateUmlClassCommand(
            umlFrame=self._classDiagramFrame,
            umlPosition=unsnappedPos,
            umlPubSubEngine=self._umlPubSubEngine,
            modelClass=Class(name='SnappedCreateClass')
        )
        createCommand._addUmlShapeToFrame(
            umlFrame=self._classDiagramFrame,
            umlShape=createCommand.shape,
            umlPosition=unsnappedPos
        )
        self.assertEqual(createCommand.shape.position, UmlPosition(x=100, y=125))

        pasteCommand: ClassPasteCommand = ClassPasteCommand(
            umlModelBase=Class(name='SnappedPasteClass'),
            umlPosition=UmlPosition(x=163, y=189),
            umlFrame=self._classDiagramFrame,
            umlPubSubEngine=self._umlPubSubEngine
        )
        pasteCommand.Do()
        self.assertEqual(pasteCommand._umlClass.position, UmlPosition(x=175, y=200))

    def testInteractiveDragSnapsTopLeftCornerToGrid(self):
        """
        Verify interactive dragging via UmlBaseEventHandler snaps the shape's
        top-left corner (not its center) to the grid and records the snapped
        final position in ShapesMovedCommand.
        """
        self._classDiagramFrame.umlDiagram.SetGridSpacing(25)
        self._classDiagramFrame.umlDiagram.SetSnapToGrid(True)

        initialPos: UmlPosition = UmlPosition(x=100, y=100)
        createCommand: CreateUmlClassCommand = CreateUmlClassCommand(
            umlFrame=self._classDiagramFrame,
            umlPosition=initialPos,
            umlPubSubEngine=self._umlPubSubEngine,
            modelClass=Class(name='DraggableClass')
        )
        createCommand._addUmlShapeToFrame(
            umlFrame=self._classDiagramFrame,
            umlShape=createCommand.shape,
            umlPosition=initialPos
        )
        umlClass: UmlClass = cast(UmlClass, createCommand.shape)
        self.assertEqual(umlClass.position, initialPos)

        eventHandler: UmlBaseEventHandler = cast(UmlBaseEventHandler, umlClass.GetEventHandler())
        eventHandler.OnBeginDragLeft(x=150, y=120)
        eventHandler.OnDragLeft(draw=True, x=180, y=160)
        eventHandler.OnEndDragLeft(x=180, y=160)

        expectedSnappedPos: UmlPosition = UmlPosition(x=125, y=150)
        self.assertEqual(umlClass.position, expectedSnappedPos)

        self._classDiagramFrame.commandProcessor.Undo()
        self.assertEqual(umlClass.position, initialPos)

        self._classDiagramFrame.commandProcessor.Redo()
        self.assertEqual(umlClass.position, expectedSnappedPos)

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
