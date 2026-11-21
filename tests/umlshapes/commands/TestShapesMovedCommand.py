
from typing import cast

from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from umlmodel.Class import Class
from umlmodel.enumerations.LinkType import LinkType

from umlshapes.ShapeTypes import UmlShapes
from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler
from umlshapes.commands.ClassPasteCommand import ClassPasteCommand
from umlshapes.commands.CreateLinkCommand import CreateLinkCommand
from umlshapes.commands.CreateUmlClassCommand import CreateUmlClassCommand
from umlshapes.commands.shapemove.ShapeMoveInfo import MovedLinks
from umlshapes.commands.shapemove.ShapeMoveInfo import MovedShapes
from umlshapes.commands.shapemove.ShapeMoveInfo import ShapeId
from umlshapes.commands.shapemove.ShapeMoveInfo import ShapeMoveInfo
from umlshapes.commands.shapemove.ShapeMoveRecorder import ShapeMoveRecorder
from umlshapes.commands.shapemove.ShapesMovedCommand import DEFAULT_NAME_PREFIX
from umlshapes.commands.shapemove.ShapesMovedCommand import ShapesMovedCommand
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.links.UmlAssociation import UmlAssociation
from wx import Point
from wx.lib.ogl import OGLInitialize
from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.types.Common import EndPositions
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.UmlPosition import UmlPositions


class TestShapesMovedCommand(UnitTestBaseW):
    """
    Unit tests for ShapesMovedCommand, ShapeMoveRecorder, link bend restoration, and grid snapping behavior.
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
        initialPos:  UmlPosition = UmlPosition(x=100, y=100)
        umlClass:    UmlClass    = self._createTestUmlClass(position=initialPos)
        shapeId:     ShapeId     = ShapeId(str(umlClass.id))
        movedShapes: MovedShapes = MovedShapes({
            shapeId: ShapeMoveInfo(umlShape=umlClass, originalPosition=initialPos)
        })
        movedLinks:  MovedLinks  = MovedLinks({})

        command: ShapesMovedCommand = ShapesMovedCommand(
            umlFrame=self._classDiagramFrame,
            movedShapes=movedShapes,
            movedLinks=movedLinks
        )

        self.assertTrue(command.commandName.startswith(f'{DEFAULT_NAME_PREFIX}-'))
        self.assertEqual(command.commandName, command.GetName())

    def testAlternateName(self):
        """
        Verify alternate command name prefix overrides default prefix.
        """
        customPrefix: str         = 'CustomMove'
        initialPos:   UmlPosition = UmlPosition(x=100, y=100)
        umlClass:     UmlClass    = self._createTestUmlClass(position=initialPos)
        shapeId:      ShapeId     = ShapeId(str(umlClass.id))
        movedShapes:  MovedShapes = MovedShapes({
            shapeId: ShapeMoveInfo(umlShape=umlClass, originalPosition=initialPos)
        })
        movedLinks:   MovedLinks  = MovedLinks({})

        command: ShapesMovedCommand = ShapesMovedCommand(
            umlFrame=self._classDiagramFrame,
            movedShapes=movedShapes,
            movedLinks=movedLinks,
            name=customPrefix
        )

        self.assertTrue(command.commandName.startswith(f'{customPrefix}-'))
        self.assertEqual(command.commandName, command.GetName())

    def testCommandNamePropertySetter(self):
        """
        Verify commandName property getter and setter update name.
        """
        initialPos:  UmlPosition = UmlPosition(x=100, y=100)
        umlClass:    UmlClass    = self._createTestUmlClass(position=initialPos)
        shapeId:     ShapeId     = ShapeId(str(umlClass.id))
        movedShapes: MovedShapes = MovedShapes({
            shapeId: ShapeMoveInfo(umlShape=umlClass, originalPosition=initialPos)
        })
        movedLinks:  MovedLinks  = MovedLinks({})

        command: ShapesMovedCommand = ShapesMovedCommand(
            umlFrame=self._classDiagramFrame,
            movedShapes=movedShapes,
            movedLinks=movedLinks
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

        movedShapes: MovedShapes = MovedShapes({
            shapeId: ShapeMoveInfo(umlShape=umlClass, originalPosition=initialPos)
        })
        movedLinks:  MovedLinks  = MovedLinks({})

        command: ShapesMovedCommand = ShapesMovedCommand(
            umlFrame=self._classDiagramFrame,
            movedShapes=movedShapes,
            movedLinks=movedLinks
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

    def testUndoRedoRestoresAddedLinkIntermediateControlPoints(self):
        """
        Verify that when intermediate control points (bends) are added to a link
        during a move/layout operation, Undo removes the bends and control point
        handles, and Redo restores the bends and control point handles.
        """
        initialPosA: UmlPosition = UmlPosition(x=50, y=50)
        initialPosB: UmlPosition = UmlPosition(x=50, y=250)
        finalPosA:   UmlPosition = UmlPosition(x=100, y=50)
        finalPosB:   UmlPosition = UmlPosition(x=300, y=350)

        classA: UmlClass = self._createTestUmlClass(position=initialPosA)
        classB: UmlClass = self._createTestUmlClass(position=initialPosB)
        umlLink: UmlAssociation = self._createTestAssociation(sourceShape=classA, destinationShape=classB)

        self.assertEqual(len(umlLink.GetLineControlPoints()), 2)

        selectedShapes: UmlShapes = UmlShapes([classA, classB, umlLink])
        movedShapes: MovedShapes = ShapeMoveRecorder.recordInitialShapePositions(umlShapes=selectedShapes)
        movedLinks:  MovedLinks  = ShapeMoveRecorder.recordInitialLinkPositions(umlShapes=selectedShapes)

        # Simulate layout moving nodes and inserting two intermediate bends
        classA.position = finalPosA
        classB.position = finalPosB
        bendOne: UmlPosition = UmlPosition(x=150, y=180)
        bendTwo: UmlPosition = UmlPosition(x=250, y=260)
        umlLink.addLineControlPoint(umlPosition=bendOne)
        umlLink.addLineControlPoint(umlPosition=bendTwo)
        umlLink.MakeControlPoints()

        self.assertEqual(len(umlLink.GetLineControlPoints()), 4)
        self.assertEqual(
            ShapeMoveRecorder.extractBendPositions(umlLink=umlLink),
            UmlPositions([bendOne, bendTwo])
        )

        command: ShapesMovedCommand = ShapesMovedCommand(
            umlFrame=self._classDiagramFrame,
            movedShapes=movedShapes,
            movedLinks=movedLinks,
            name='Sugiyama'
        )
        command.Do()

        # Undo should restore class positions and remove intermediate control points
        command.Undo()
        self.assertEqual(classA.position, initialPosA)
        self.assertEqual(classB.position, initialPosB)
        self.assertEqual(len(umlLink.GetLineControlPoints()), 2)
        self.assertEqual(
            ShapeMoveRecorder.extractBendPositions(umlLink=umlLink),
            UmlPositions([])
        )
        self.assertEqual(len(umlLink.controlPositions), 0)

        # Redo should reapply final class positions and restore intermediate control points
        command.Redo()
        self.assertEqual(classA.position, finalPosA)
        self.assertEqual(classB.position, finalPosB)
        self.assertEqual(len(umlLink.GetLineControlPoints()), 4)
        self.assertEqual(
            ShapeMoveRecorder.extractBendPositions(umlLink=umlLink),
            UmlPositions([bendOne, bendTwo])
        )
        self.assertEqual(len(umlLink.controlPositions), 4)

    def testUndoRedoRestoresPreExistingLinkIntermediateControlPoints(self):
        """
        Verify that when a link already has intermediate control points prior to
        a move/layout operation, Undo restores the original intermediate bend
        positions and Redo restores the post-move intermediate bend positions.
        """
        initialPosA: UmlPosition = UmlPosition(x=60, y=60)
        initialPosB: UmlPosition = UmlPosition(x=260, y=260)
        finalPosA:   UmlPosition = UmlPosition(x=120, y=80)
        finalPosB:   UmlPosition = UmlPosition(x=360, y=320)

        classA: UmlClass = self._createTestUmlClass(position=initialPosA)
        classB: UmlClass = self._createTestUmlClass(position=initialPosB)
        umlLink: UmlAssociation = self._createTestAssociation(sourceShape=classA, destinationShape=classB)

        initialBend: UmlPosition = UmlPosition(x=160, y=140)
        umlLink.addLineControlPoint(umlPosition=initialBend)
        self.assertEqual(len(umlLink.GetLineControlPoints()), 3)

        selectedShapes: UmlShapes = UmlShapes([classA, classB])
        movedShapes: MovedShapes = ShapeMoveRecorder.recordInitialShapePositions(umlShapes=selectedShapes)
        movedLinks:  MovedLinks  = ShapeMoveRecorder.recordInitialLinkPositions(umlShapes=selectedShapes)

        # Simulate replacing the initial bend with a new bend position
        umlLink.DeleteControlPoints()
        lineControlPoints: list[Point] = umlLink.GetLineControlPoints()
        firstPoint: Point = lineControlPoints[0]
        lastPoint:  Point = lineControlPoints[-1]
        lineControlPoints.clear()
        lineControlPoints.extend([firstPoint, lastPoint])

        finalBend: UmlPosition = UmlPosition(x=220, y=200)
        umlLink.addLineControlPoint(umlPosition=finalBend)
        classA.position = finalPosA
        classB.position = finalPosB

        command: ShapesMovedCommand = ShapesMovedCommand(
            umlFrame=self._classDiagramFrame,
            movedShapes=movedShapes,
            movedLinks=movedLinks
        )
        command.Do()

        command.Undo()
        self.assertEqual(classA.position, initialPosA)
        self.assertEqual(classB.position, initialPosB)
        self.assertEqual(
            ShapeMoveRecorder.extractBendPositions(umlLink=umlLink),
            UmlPositions([initialBend])
        )

        command.Redo()
        self.assertEqual(classA.position, finalPosA)
        self.assertEqual(classB.position, finalPosB)
        self.assertEqual(
            ShapeMoveRecorder.extractBendPositions(umlLink=umlLink),
            UmlPositions([finalBend])
        )

    def testInteractiveDragOfTwoConnectedShapesPreservesLinkBendsAndEndpoints(self):
        """
        Verify that dragging two selected connected shapes together translates
        the link's custom endpoints and intermediate bend points intact by the
        same delta, and that Undo/Redo restores and reapplies them accurately.
        """
        self._classDiagramFrame.umlDiagram.SetGridSpacing(25)
        self._classDiagramFrame.umlDiagram.SetSnapToGrid(True)

        initialPosA: UmlPosition = UmlPosition(x=100, y=100)
        initialPosB: UmlPosition = UmlPosition(x=300, y=250)

        createCommandA: CreateUmlClassCommand = CreateUmlClassCommand(
            umlFrame=self._classDiagramFrame,
            umlPosition=initialPosA,
            umlPubSubEngine=self._umlPubSubEngine,
            modelClass=Class(name='BaseClass')
        )
        createCommandA._addUmlShapeToFrame(
            umlFrame=self._classDiagramFrame,
            umlShape=createCommandA.shape,
            umlPosition=initialPosA
        )
        classA: UmlClass = cast(UmlClass, createCommandA.shape)

        createCommandB: CreateUmlClassCommand = CreateUmlClassCommand(
            umlFrame=self._classDiagramFrame,
            umlPosition=initialPosB,
            umlPubSubEngine=self._umlPubSubEngine,
            modelClass=Class(name='SubClass')
        )
        createCommandB._addUmlShapeToFrame(
            umlFrame=self._classDiagramFrame,
            umlShape=createCommandB.shape,
            umlPosition=initialPosB
        )
        classB: UmlClass = cast(UmlClass, createCommandB.shape)

        umlLink: UmlAssociation = self._createTestAssociation(sourceShape=classB, destinationShape=classA)
        initialFromEnd: UmlPosition = UmlPosition(x=350, y=250)
        initialToEnd:   UmlPosition = UmlPosition(x=200, y=125)
        initialBend:    UmlPosition = UmlPosition(x=350, y=125)
        initialEnds:    EndPositions = EndPositions(fromPosition=initialFromEnd, toPosition=initialToEnd)

        umlLink.endPositions = initialEnds
        umlLink.addLineControlPoint(umlPosition=initialBend)
        umlLink.MakeControlPoints()

        classA.selected = True
        classB.selected = True
        umlLink.selected = True

        eventHandler: UmlBaseEventHandler = classA.GetEventHandler()
        eventHandler.OnBeginDragLeft(x=120, y=120)
        eventHandler.OnDragLeft(draw=True, x=170, y=195)
        eventHandler.OnEndDragLeft(x=170, y=195)

        expectedPosA:    UmlPosition  = UmlPosition(x=150, y=175)
        expectedPosB:    UmlPosition  = UmlPosition(x=350, y=325)
        expectedBend:    UmlPosition  = UmlPosition(x=400, y=200)
        expectedFromEnd: UmlPosition  = UmlPosition(x=400, y=325)
        expectedToEnd:   UmlPosition  = UmlPosition(x=250, y=200)
        expectedEnds:    EndPositions = EndPositions(fromPosition=expectedFromEnd, toPosition=expectedToEnd)

        self.assertEqual(classA.position, expectedPosA)
        self.assertEqual(classB.position, expectedPosB)
        self.assertEqual(ShapeMoveRecorder.extractBendPositions(umlLink=umlLink), UmlPositions([expectedBend]))
        self.assertEqual(umlLink.endPositions, expectedEnds)

        self._classDiagramFrame.commandProcessor.Undo()
        self.assertEqual(classA.position, initialPosA)
        self.assertEqual(classB.position, initialPosB)
        self.assertEqual(ShapeMoveRecorder.extractBendPositions(umlLink=umlLink), UmlPositions([initialBend]))
        self.assertEqual(umlLink.endPositions, initialEnds)

        self._classDiagramFrame.commandProcessor.Redo()
        self.assertEqual(classA.position, expectedPosA)
        self.assertEqual(classB.position, expectedPosB)
        self.assertEqual(ShapeMoveRecorder.extractBendPositions(umlLink=umlLink), UmlPositions([expectedBend]))
        self.assertEqual(umlLink.endPositions, expectedEnds)

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

        eventHandler: UmlBaseEventHandler = umlClass.GetEventHandler()
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

    def _createTestAssociation(self, sourceShape: UmlClass, destinationShape: UmlClass) -> UmlAssociation:
        createLinkCommand: CreateLinkCommand = CreateLinkCommand(
            umlFrame=self._classDiagramFrame,
            partialName='TestAssoc',
            sourceShape=sourceShape,
            destinationShape=destinationShape,
            linkType=LinkType.ASSOCIATION,
            umlPubSubEngine=self._umlPubSubEngine
        )
        createLinkCommand.Do()
        return cast(UmlAssociation, createLinkCommand.umlLink)


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(testCaseClass=TestShapesMovedCommand))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
