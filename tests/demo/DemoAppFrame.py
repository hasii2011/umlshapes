
from typing import cast

from logging import Logger

from logging import getLogger

from pathlib import Path

from wx import ClientDC
from wx import OK
from wx import ID_CUT
from wx import ID_COPY
from wx import ID_EXIT
from wx import ID_REDO
from wx import ID_UNDO
from wx import EVT_MENU
from wx import ID_PASTE
from wx import EVT_CLOSE
from wx import ICON_ERROR
from wx import ID_SELECTALL
from wx import ID_PREFERENCES
from wx import DEFAULT_FRAME_STYLE
from wx import FRAME_FLOAT_ON_PARENT
from wx import EVT_NOTEBOOK_PAGE_CHANGED

from wx import Menu
from wx import MenuBar
from wx import Notebook
from wx import CommandEvent
from wx import BookCtrlEvent
from wx import Point
from wx import MenuItem
from wx import MessageDialog

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from umlmodel.Interface import Interface
from umlmodel.Interface import Interfaces
from umlmodel.ModelTypes import ClassName
from umlmodel.SDInstance import SDInstance

from umlshapes.UmlUtils import UmlUtils
from umlshapes.ShapeTypes import UmlShapeGenre
from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.dialogs.DlgEditInterface import DlgEditInterface
from umlshapes.frames.SequenceDiagramFrame import SequenceDiagramFrame

from umlshapes.pubsubengine.UmlMessageType import UmlMessageType
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine

from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.frames.DiagramFrame import FrameId
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface
from umlshapes.links.eventhandlers.UmlLollipopInterfaceEventHandler import UmlLollipopInterfaceEventHandler

from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.sd.UmlSDInstance import UmlSDInstance
from umlshapes.shapes.eventhandlers.UmlSdInstanceEventHandler import UmlSdInstanceEventHandler
from umlshapes.shapes.sd.UmlSDLifeLineEventHandler import LifeLineClickDetails

from umlshapes.types.Common import AttachmentSide
from umlshapes.types.UmlPosition import UmlPosition

from tests.demo.DemoCommon import Identifiers
from tests.demo.LinkCreator import LinkCreator
from tests.demo.ShapeCreator import ShapeCreator
from tests.demo.DemoClassDiagramFrame import DemoClassDiagramFrame

from tests.demo.DlgUmlShapesPreferences import DlgUmlShapesPreferences

DEMO_RUNNING_INDICATOR: str = '/tmp/DemoRunning.txt'

FRAME_WIDTH:  int = 1024
FRAME_HEIGHT: int = 720

DemoFrame = DemoClassDiagramFrame | SequenceDiagramFrame

class DemoAppFrame(SizedFrame):
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=None, title='Test UML Shapes', size=(FRAME_WIDTH, FRAME_HEIGHT), style=DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT)

        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)

        self._umlPubSubEngine: UmlPubSubEngine = UmlPubSubEngine()
        self._editMenu:        Menu            = cast(Menu, None)
        self._shapeItem:       MenuItem        = cast(MenuItem, None)

        self._noteBook: Notebook = Notebook(parent=sizedPanel)
        self._noteBook.SetSizerProps(expand=True, proportion=1)

        self._diagramFrame1 = DemoClassDiagramFrame(
            parent=self._noteBook,
            umlPubSubEngine=self._umlPubSubEngine,
        )
        self._diagramFrame2 = SequenceDiagramFrame(
            parent=self._noteBook,
            umlPubSubEngine=self._umlPubSubEngine,
        )

        self._noteBook.AddPage(page=self._diagramFrame1, text='Class Diagram',    select=False)
        self._noteBook.AddPage(page=self._diagramFrame2, text='Sequence Diagram', select=True)

        self._currentFrame: DemoClassDiagramFrame | SequenceDiagramFrame = cast(DemoFrame, self._noteBook.GetCurrentPage())

        self._createApplicationMenuBar()
        self._diagramFrame1.commandProcessor.SetEditMenu(menu=self._editMenu)
        self._diagramFrame2.commandProcessor.SetEditMenu(menu=self._editMenu)

        self.CreateStatusBar()  # should always do this when there's a resize border
        self.SetAutoLayout(True)

        self.SetPosition(pt=Point(x=20, y=40))

        self.Show(True)

        self._shapeCreator: ShapeCreator   = ShapeCreator(umlPubSubEngine=self._umlPubSubEngine)
        self._linkCreator:  LinkCreator    = LinkCreator(umlPubSubEngine=self._umlPubSubEngine)
        self._preferences:  UmlPreferences = UmlPreferences()

        self._interfaceCount: int = 0

        self._subscribeFrameToRelevantFrameTopics(frameId=self._diagramFrame1.id)
        self._subscribeFrameToRelevantFrameTopics(frameId=self._diagramFrame2.id)

        self.Bind(EVT_NOTEBOOK_PAGE_CHANGED, self._onFrameDisplayedChanged)
        self.Bind(EVT_CLOSE,    self.Close)

        iAmRunningPath: Path = Path(DEMO_RUNNING_INDICATOR)
        iAmRunningPath.touch()

    def Close(self, force: bool = False) -> bool:
        iAmRunningPath: Path = Path(DEMO_RUNNING_INDICATOR)
        iAmRunningPath.unlink(missing_ok=True)

        self.Destroy()

        return True

    def _createApplicationMenuBar(self):

        menuBar:  MenuBar = MenuBar()
        fileMenu: Menu    = Menu()
        editMenu: Menu    = Menu()
        viewMenu: Menu    = Menu()

        self._shapeItem = fileMenu.AppendCheckItem(Identifiers.ID_DEMO_SHAPE_BOUNDARIES, item='Shape Boundaries', help='Demo Shape Boundaries')
        fileMenu.AppendSeparator()
        fileMenu.Append(ID_EXIT, '&Quit', "Quit Application")
        fileMenu.AppendSeparator()
        fileMenu.Append(ID_PREFERENCES, "P&references", "Uml preferences")

        #
        # Use all the stock properties
        #
        editMenu.Append(ID_UNDO)
        editMenu.Append(ID_REDO)
        editMenu.AppendSeparator()
        editMenu.Append(ID_CUT)
        editMenu.Append(ID_COPY)
        editMenu.Append(ID_PASTE)
        editMenu.AppendSeparator()
        editMenu.Append(ID_SELECTALL)
        editMenu.AppendSeparator()

        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_INTERFACE,   item='UML Interface',   helpString='Display Normal Interface')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_AGGREGATION, item='UML Aggregation', helpString='Display a aggregation Link')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_COMPOSITION, item='UML Composition', helpString='Display a composition Link')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_INHERITANCE, item='UML Inheritance', helpString='Display an Inheritance Link')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_ASSOCIATION, item='Uml Association', helpString='Display Bare Association')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_NOTE_LINK,   item='Uml Note Link',   helpString='Display a note link')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_CLASS,       item='Uml Class',          helpString='Display an Uml Class')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_TEXT,        item='Uml Text',           helpString='Display Uml Text')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_NOTE,        item='Uml Note',           helpString='Display Uml Note')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_USE_CASE,    item='Uml Use Case',       helpString='Display Uml Use Case')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_UML_ACTOR,       item='Uml Actor',          helpString='Display Uml Actor')
        viewMenu.Append(id=Identifiers.ID_DISPLAY_ORTHOGONAL_LINK, item='Orthogonal Link',    helpString='Display Orthogonal Link')

        viewMenu.Append(id=Identifiers.ID_DISPLAY_SEQUENCE_DIAGRAM,    item='Sequence Diagram', helpString='Display Sequence Diagram')
        viewMenu.AppendSeparator()

        menuBar.Append(fileMenu, 'File')
        menuBar.Append(editMenu, 'Edit')
        menuBar.Append(viewMenu, 'View')

        self.SetMenuBar(menuBar)

        # self.Bind(EVT_MENU, self._onOglPreferences, id=ID_PREFERENCES)

        self._editMenu = editMenu

        self.Bind(EVT_MENU, self._onDemoShapeBoundaries, id=Identifiers.ID_DEMO_SHAPE_BOUNDARIES)

        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_TEXT)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_NOTE)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_USE_CASE)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_ACTOR)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_CLASS)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_ASSOCIATION)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_INHERITANCE)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_COMPOSITION)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_AGGREGATION)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_INTERFACE)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_UML_NOTE_LINK)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_ORTHOGONAL_LINK)
        self.Bind(EVT_MENU, self._onDisplayElement, id=Identifiers.ID_DISPLAY_SEQUENCE_DIAGRAM)

        self.Bind(EVT_MENU, self._onUmlShapePreferences, id=ID_PREFERENCES)

        self.Bind(EVT_MENU, self._onEditMenu, id=ID_UNDO)
        self.Bind(EVT_MENU, self._onEditMenu, id=ID_REDO)
        self.Bind(EVT_MENU, self._onEditMenu, id=ID_CUT)
        self.Bind(EVT_MENU, self._onEditMenu, id=ID_COPY)
        self.Bind(EVT_MENU, self._onEditMenu, id=ID_PASTE)
        self.Bind(EVT_MENU, self._onEditMenu, id=ID_SELECTALL)

    # noinspection PyUnusedLocal
    def _onDemoShapeBoundaries(self, event: CommandEvent):

        from umlshapes.ShapeTypes import UmlShapes

        if event.IsChecked() is True:
            frame: ClassDiagramFrame = self._currentFrame

            umlShapes:  UmlShapes = frame.umlShapes
            if len(umlShapes) == 0:     # noqa
                with MessageDialog(parent=None, message='There are no shapes on the current frame', caption='You messed up!', style=OK | ICON_ERROR) as dlg:
                    dlg.ShowModal()
            else:
                self._currentFrame.drawShapeBoundary = True
        else:
            self._currentFrame.drawShapeBoundary = False
        self._currentFrame.refresh()
        self.logger.info(f'Drawing Shapes Boundary=`{self._currentFrame.drawShapeBoundary}` frame=`{self._currentFrame.id}`')

    def _onDisplayElement(self, event: CommandEvent):

        menuId:              int                 = event.GetId()
        shapeCreator:        ShapeCreator        = self._shapeCreator
        linkCreator: LinkCreator = self._linkCreator

        # noinspection PyUnreachableCode
        match menuId:
            case Identifiers.ID_DISPLAY_UML_CLASS:
                shapeCreator.displayShape(Identifiers.ID_DISPLAY_UML_CLASS, self._currentFrame)
                self.SetStatusText('See the shape !!')
            case Identifiers.ID_DISPLAY_UML_TEXT:
                shapeCreator.displayShape(Identifiers.ID_DISPLAY_UML_TEXT, self._currentFrame)
            case Identifiers.ID_DISPLAY_UML_NOTE:
                shapeCreator.displayShape(Identifiers.ID_DISPLAY_UML_NOTE, self._currentFrame)
            case Identifiers.ID_DISPLAY_UML_USE_CASE:
                shapeCreator.displayShape(Identifiers.ID_DISPLAY_UML_USE_CASE, self._currentFrame)
            case Identifiers.ID_DISPLAY_UML_ACTOR:
                shapeCreator.displayShape(Identifiers.ID_DISPLAY_UML_ACTOR, self._currentFrame)

            case Identifiers.ID_DISPLAY_UML_ASSOCIATION:
                linkCreator.displayAssociation(idReference=Identifiers.ID_DISPLAY_UML_ASSOCIATION, diagramFrame=self._currentFrame)
            case Identifiers.ID_DISPLAY_UML_COMPOSITION:
                linkCreator.displayAssociation(idReference=Identifiers.ID_DISPLAY_UML_COMPOSITION, diagramFrame=self._currentFrame)
            case Identifiers.ID_DISPLAY_UML_AGGREGATION:
                linkCreator.displayAssociation(idReference=Identifiers.ID_DISPLAY_UML_AGGREGATION, diagramFrame=self._currentFrame)

            case Identifiers.ID_DISPLAY_UML_NOTE_LINK:
                linkCreator.displayNoteLink(diagramFrame=self._currentFrame)

            case Identifiers.ID_DISPLAY_UML_INHERITANCE:
                linkCreator.displayUmlInheritance(diagramFrame=self._currentFrame)
            case Identifiers.ID_DISPLAY_UML_INTERFACE:
                linkCreator.displayUmlInterface(diagramFrame=self._currentFrame)
            case Identifiers.ID_DISPLAY_ORTHOGONAL_LINK:
                linkCreator.displayOrthogonalLink(diagramFrame=self._currentFrame)
            case Identifiers.ID_DISPLAY_SEQUENCE_DIAGRAM:
                self._displaySequenceDiagram(diagramFrame=self._currentFrame)
                # self._displaySequenceDiagram2(diagramFrame=self._currentFrame)
            case _:
                self.logger.error(f'WTH!  I am not handling that menu item')

    def _displaySequenceDiagram(self, diagramFrame: SequenceDiagramFrame):
        """

        Args:
            diagramFrame:

        """
        if isinstance(diagramFrame, SequenceDiagramFrame) is True:

            self._createSDInstance(diagramFrame=diagramFrame, instanceName='instance1', xCoordinate=100)
            self._createSDInstance(diagramFrame=diagramFrame, instanceName='instance2', xCoordinate=300)

        else:
            msgDlg: MessageDialog = MessageDialog(
                parent=None,
                message='Sequence Diagrams must be placed on a Sequence Diagram frame',
                caption='Bad News',
                style=OK | ICON_ERROR
            )
            msgDlg.ShowModal()

    def _onEditMenu(self, event: CommandEvent):

        import wx       # So pattern matching works

        eventId: int = event.GetId()
        frameId: FrameId = self._currentFrame.id
        match eventId:

            case wx.ID_UNDO:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.UNDO, frameId=frameId)
            case wx.ID_REDO:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.REDO, frameId=frameId)
            case wx.ID_CUT:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.CUT_SHAPES, frameId=frameId)
            case wx.ID_COPY:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.COPY_SHAPES, frameId=frameId)
            case wx.ID_PASTE:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.PASTE_SHAPES, frameId=frameId)
            case wx.ID_PASTE:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.PASTE_SHAPES, frameId=frameId)
            case wx.ID_SELECTALL:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.SELECT_ALL_SHAPES, frameId=frameId)
            case _:
                self.logger.warning(f'Unknown event id {eventId}')

    def _createLollipopInterfaceListener(self, requestingFrame: ClassDiagramFrame, requestingUmlClass: UmlClass, interfaces: Interfaces, perimeterPoint: UmlPosition):
        """
        In an application this code belongs in a Command

        Args:
            requestingFrame:        Treat this as an opaque object
            requestingUmlClass:
            interfaces:
            perimeterPoint:
        """

        interfaceName: str = f'{self._preferences.defaultNameInterface}{self._interfaceCount}'
        self._interfaceCount += 1

        interface: Interface = Interface(interfaceName)
        interface.addImplementor(ClassName(requestingUmlClass.modelClass.name))

        umlLollipopInterface: UmlLollipopInterface = UmlLollipopInterface(interface=interface)
        umlLollipopInterface.attachedTo            = requestingUmlClass

        attachmentSide: AttachmentSide      = UmlUtils.attachmentSide(x=perimeterPoint.x, y=perimeterPoint.y, rectangle=requestingUmlClass.rectangle)
        umlLollipopInterface.attachmentSide = attachmentSide
        umlLollipopInterface.lineCentum     = UmlUtils.computeLineCentum(attachmentSide=attachmentSide, umlPosition=perimeterPoint, rectangle=requestingUmlClass.rectangle)

        self.logger.debug(f'{umlLollipopInterface.attachmentSide=} {umlLollipopInterface.lineCentum=}')

        umlLollipopInterface.umlFrame = requestingFrame
        diagram: UmlDiagram = requestingFrame.umlDiagram    # And then I break the opaqueness

        diagram.AddShape(umlLollipopInterface)
        umlLollipopInterface.Show(show=True)
        self.logger.info(f'UmlInterface added: {umlLollipopInterface}')

        # eventHandler: UmlLollipopInterfaceEventHandler = UmlLollipopInterfaceEventHandler(lollipopInterface=umlLollipopInterface)
        # eventHandler.SetPreviousHandler(umlLollipopInterface.GetEventHandler())
        # umlLollipopInterface.SetEventHandler(eventHandler)
        # Looks weired but don't need the result
        UmlLollipopInterfaceEventHandler(lollipopInterface=umlLollipopInterface)

        pubsubEngine: IUmlPubSubEngine  = requestingFrame.umlPubSubEngine

        # Update with our generated one
        interfaces.append(interface)
        with DlgEditInterface(parent=requestingFrame, lollipopInterface=umlLollipopInterface, umlPubSubEngine=pubsubEngine, interfaces=interfaces) as dlg:
            if dlg.ShowModal() == OK:
                requestingFrame.refresh()

    def _updateApplicationStatusListener(self, message: str):
        self.SetStatusText(text=message)

    def _frameModifiedListener(self, modifiedFrameId: str):

        self.logger.info(f'Frame Modified - {modifiedFrameId=}')

    def _frameLeftClickListener(self, frame: UmlFrame, umlPosition: UmlPosition):
        self.logger.debug(f'Frame {frame.id}, clicked at {umlPosition=}')

    def _umlShapeListener(self, umlShape: UmlShapeGenre):
        self.logger.info(f'Shape was selected: {umlShape}')

    # noinspection PyUnusedLocal
    def _onUmlShapePreferences(self, event: CommandEvent):

        with DlgUmlShapesPreferences(parent=self) as dlg:
            if dlg.ShowModal() == OK:
                self.logger.info(f'Pressed Ok')

    # noinspection PyUnusedLocal
    def _onFrameDisplayedChanged(self, event: BookCtrlEvent):

        self._currentFrame = cast(DemoFrame, self._noteBook.GetCurrentPage())

        self._currentFrame.commandProcessor.SetMenuStrings()

        self.logger.info(f'{self._currentFrame.id=}')
        #
        # Toggle the menu item based on the current frame value
        #
        if isinstance(self._currentFrame, DemoClassDiagramFrame) is True:
            self._shapeItem.Check(check=self._currentFrame.drawShapeBoundary)

    def _lifeLineClicked(self, clickDetails: LifeLineClickDetails):
        self.logger.info(f'{clickDetails}=')

    def _subscribeFrameToRelevantFrameTopics(self, frameId: FrameId):

        self._umlPubSubEngine.subscribe(UmlMessageType.UPDATE_APPLICATION_STATUS,
                                        frameId=frameId,
                                        listener=self._updateApplicationStatusListener)
        self._umlPubSubEngine.subscribe(UmlMessageType.FRAME_MODIFIED,
                                        frameId=frameId,
                                        listener=self._frameModifiedListener)

        self._umlPubSubEngine.subscribe(UmlMessageType.FRAME_LEFT_CLICK,
                                        frameId=frameId,
                                        listener=self._frameLeftClickListener)

        self._umlPubSubEngine.subscribe(UmlMessageType.UML_SHAPE_SELECTED,
                                        frameId=frameId,
                                        listener=self._umlShapeListener)

        self._umlPubSubEngine.subscribe(UmlMessageType.CREATE_LOLLIPOP,
                                        frameId=frameId,
                                        listener=self._createLollipopInterfaceListener)

        self._umlPubSubEngine.subscribe(UmlMessageType.SD_LIFE_LINE_CLICKED,
                                        frameId=frameId,
                                        listener=self._lifeLineClicked)

    def _createSDInstance(self, diagramFrame: SequenceDiagramFrame, instanceName: str, xCoordinate: int) -> UmlSDInstance:

        sdInstance: SDInstance = SDInstance()
        sdInstance.instanceName = instanceName

        umlSDInstance: UmlSDInstance = UmlSDInstance(sdInstance=sdInstance, diagramFrame=diagramFrame, umlPubSubEngine=self._umlPubSubEngine)

        instanceY:   int         = self._preferences.instanceYPosition
        umlPosition: UmlPosition = UmlPosition(x=xCoordinate, y=instanceY)

        dc:        ClientDC = ClientDC(diagramFrame)
        diagramFrame.PrepareDC(dc)

        x, y = umlSDInstance.computeCenterXY(umlPosition)
        umlSDInstance.Move(dc, x, y)
        self.logger.debug(f'{xCoordinate=} {instanceY=}')

        umlSDInstance.SetCanvas(diagramFrame)

        umlSDInstance.position = umlPosition

        diagramFrame.umlDiagram.AddShape(umlSDInstance)
        umlSDInstance.Show(True)

        umlSDInstance.connectInstanceNameToBottomOfContainer()

        eventHandler: UmlSdInstanceEventHandler = UmlSdInstanceEventHandler(umlPubSubEngine=self._umlPubSubEngine)
        eventHandler.SetShape(umlSDInstance)
        eventHandler.SetPreviousHandler(umlSDInstance.GetEventHandler())
        umlSDInstance.SetEventHandler(eventHandler)

        diagramFrame.refresh()

        return umlSDInstance
