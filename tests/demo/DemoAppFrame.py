
from typing import cast

from logging import Logger
from logging import getLogger

from wx import OK
from wx import EVT_MENU
from wx import ID_CUT
from wx import ID_UNDO
from wx import ID_COPY
from wx import ID_EXIT
from wx import ID_PASTE
from wx import ID_PREFERENCES
from wx import ID_REDO
from wx import ID_SELECTALL
from wx import DEFAULT_FRAME_STYLE
from wx import FRAME_FLOAT_ON_PARENT

from wx import Menu
from wx import MenuBar
from wx import CommandEvent

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from pyutmodelv2.PyutInterface import PyutInterface
from pyutmodelv2.PyutInterface import PyutInterfaces
from pyutmodelv2.PyutModelTypes import ClassName

from umlshapes.UmlDiagram import UmlDiagram
from umlshapes.UmlUtils import UmlUtils
from umlshapes.dialogs.DlgEditInterface import DlgEditInterface
from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.pubsubengine.IUmlPubSubEngine import IUmlPubSubEngine
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.pubsubengine.UmlMessageType import UmlMessageType

from umlshapes.frames.DiagramFrame import FrameId
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

from umlshapes.links.UmlLollipopInterface import UmlLollipopInterface
from umlshapes.links.eventhandlers.UmlLollipopInterfaceEventHandler import UmlLollipopInterfaceEventHandler

from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.types.Common import AttachmentSide
from umlshapes.types.Common import UmlShape
from umlshapes.types.UmlPosition import UmlPosition

from tests.demo.DemoCommon import Identifiers
from tests.demo.LinkCreator import LinkCreator
from tests.demo.ShapeCreator import ShapeCreator

from tests.demo.DlgUmlShapesPreferences import DlgUmlShapesPreferences

FRAME_WIDTH:  int = 1024
FRAME_HEIGHT: int = 720


class DemoAppFrame(SizedFrame):
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        super().__init__(parent=None, title='Test UML Shapes', size=(FRAME_WIDTH, FRAME_HEIGHT), style=DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT)

        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerProps(expand=True, proportion=1)

        self._umlPubSubEngine: UmlPubSubEngine = UmlPubSubEngine()
        self._editMenu:        Menu            = cast(Menu, None)

        self._diagramFrame = ClassDiagramFrame(
            parent=sizedPanel,
            umlPubSubEngine=self._umlPubSubEngine,
        )
        # noinspection PyUnresolvedReferences
        self._diagramFrame.SetSizerProps(expand=True, proportion=1)

        self._createApplicationMenuBar()
        self._diagramFrame.commandProcessor.SetEditMenu(menu=self._editMenu)

        self.CreateStatusBar()  # should always do this when there's a resize border
        self.SetAutoLayout(True)
        self.Show(True)

        self._shapeCreator: ShapeCreator   = ShapeCreator(diagramFrame=self._diagramFrame, umlPubSubEngine=self._umlPubSubEngine)
        self._linkCreator:  LinkCreator    = LinkCreator(diagramFrame=self._diagramFrame, umlPubSubEngine=self._umlPubSubEngine)
        self._preferences:  UmlPreferences = UmlPreferences()

        self._pyutInterfaceCount: int = 0

        self._umlPubSubEngine.subscribe(UmlMessageType.UPDATE_APPLICATION_STATUS,
                                        frameId=FrameId(self._diagramFrame.id),
                                        listener=self._updateApplicationStatusListener)
        self._umlPubSubEngine.subscribe(UmlMessageType.FRAME_MODIFIED,
                                        frameId=self._diagramFrame.id,
                                        listener=self._frameModifiedListener)

        self._umlPubSubEngine.subscribe(UmlMessageType.FRAME_LEFT_CLICK,
                                        frameId=self._diagramFrame.id,
                                        listener=self._frameLeftClickListener)

        self._umlPubSubEngine.subscribe(UmlMessageType.UML_SHAPE_SELECTED,
                                        frameId=self._diagramFrame.id,
                                        listener=self._umlShapeListener)
        self._umlPubSubEngine.subscribe(UmlMessageType.CREATE_LOLLIPOP,
                                        frameId=self._diagramFrame.id,
                                        listener=self._createLollipopInterfaceListener)

    def _createApplicationMenuBar(self):

        menuBar:  MenuBar = MenuBar()
        fileMenu: Menu    = Menu()
        editMenu: Menu    = Menu()
        viewMenu: Menu    = Menu()

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
        # viewMenu.Append(id=self._ID_DISPLAY_SEQUENCE_DIAGRAM,    item='Sequence Diagram', helpString='Display Sequence Diagram')
        viewMenu.AppendSeparator()

        menuBar.Append(fileMenu, 'File')
        menuBar.Append(editMenu, 'Edit')
        menuBar.Append(viewMenu, 'View')

        self.SetMenuBar(menuBar)

        # self.Bind(EVT_MENU, self._onOglPreferences, id=ID_PREFERENCES)

        self._editMenu = editMenu

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

        self.Bind(EVT_MENU, self._onUmlShapePreferences, id=ID_PREFERENCES)

        self.Bind(EVT_MENU, self._onEditMenu, id=ID_UNDO)
        self.Bind(EVT_MENU, self._onEditMenu, id=ID_REDO)
        self.Bind(EVT_MENU, self._onEditMenu, id=ID_CUT)
        self.Bind(EVT_MENU, self._onEditMenu, id=ID_COPY)
        self.Bind(EVT_MENU, self._onEditMenu, id=ID_PASTE)
        self.Bind(EVT_MENU, self._onEditMenu, id=ID_SELECTALL)

    def _onDisplayElement(self, event: CommandEvent):

        menuId:              int                 = event.GetId()
        shapeCreator:        ShapeCreator        = self._shapeCreator
        linkCreator: LinkCreator = self._linkCreator

        # noinspection PyUnreachableCode
        match menuId:
            case Identifiers.ID_DISPLAY_UML_CLASS:
                shapeCreator.displayShape(Identifiers.ID_DISPLAY_UML_CLASS)
                self.SetStatusText('See the shape !!')
            case Identifiers.ID_DISPLAY_UML_TEXT:
                shapeCreator.displayShape(Identifiers.ID_DISPLAY_UML_TEXT)
            case Identifiers.ID_DISPLAY_UML_NOTE:
                shapeCreator.displayShape(Identifiers.ID_DISPLAY_UML_NOTE)
            case Identifiers.ID_DISPLAY_UML_USE_CASE:
                shapeCreator.displayShape(Identifiers.ID_DISPLAY_UML_USE_CASE)
            case Identifiers.ID_DISPLAY_UML_ACTOR:
                shapeCreator.displayShape(Identifiers.ID_DISPLAY_UML_ACTOR)

            case Identifiers.ID_DISPLAY_UML_ASSOCIATION:
                linkCreator.displayAssociation(idReference=Identifiers.ID_DISPLAY_UML_ASSOCIATION)
            case Identifiers.ID_DISPLAY_UML_COMPOSITION:
                linkCreator.displayAssociation(idReference=Identifiers.ID_DISPLAY_UML_COMPOSITION)
            case Identifiers.ID_DISPLAY_UML_AGGREGATION:
                linkCreator.displayAssociation(idReference=Identifiers.ID_DISPLAY_UML_AGGREGATION)

            case Identifiers.ID_DISPLAY_UML_NOTE_LINK:
                linkCreator.displayNoteLink()

            case Identifiers.ID_DISPLAY_UML_INHERITANCE:
                linkCreator.displayUmlInheritance()
            case Identifiers.ID_DISPLAY_UML_INTERFACE:
                linkCreator.displayUmlInterface()
            # case self._ID_DISPLAY_SEQUENCE_DIAGRAM:
            #     self._displaySequenceDiagram()
            case _:
                self.logger.error(f'WTH!  I am not handling that menu item')

    def _onEditMenu(self, event: CommandEvent):

        import wx       # So pattern matching works

        eventId: int = event.GetId()
        match eventId:

            case wx.ID_UNDO:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.UNDO, frameId=self._diagramFrame.id)
            case wx.ID_REDO:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.REDO, frameId=self._diagramFrame.id)
            case wx.ID_CUT:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.CUT_SHAPES, frameId=self._diagramFrame.id)
            case wx.ID_COPY:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.COPY_SHAPES, frameId=self._diagramFrame.id)
            case wx.ID_PASTE:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.PASTE_SHAPES, frameId=self._diagramFrame.id)
            case wx.ID_PASTE:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.PASTE_SHAPES, frameId=self._diagramFrame.id)
            case wx.ID_SELECTALL:
                self._umlPubSubEngine.sendMessage(messageType=UmlMessageType.SELECT_ALL_SHAPES, frameId=self._diagramFrame.id)
            case _:
                self.logger.warning(f'Unknown event id {eventId}')

    def _createLollipopInterfaceListener(self, requestingFrame: ClassDiagramFrame, requestingUmlClass: UmlClass, pyutInterfaces: PyutInterfaces, perimeterPoint: UmlPosition):
        """
        In an application this code belongs in a Command

        Args:
            requestingFrame:        Treat this as an opaque object
            requestingUmlClass:
            perimeterPoint:
        """

        interfaceName: str = f'{self._preferences.defaultNameInterface}{self._pyutInterfaceCount}'
        self._pyutInterfaceCount += 1

        pyutInterface: PyutInterface = PyutInterface(interfaceName)
        pyutInterface.addImplementor(ClassName(requestingUmlClass.pyutClass.name))

        umlLollipopInterface: UmlLollipopInterface = UmlLollipopInterface(pyutInterface=pyutInterface)
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

        eventHandler: UmlLollipopInterfaceEventHandler = UmlLollipopInterfaceEventHandler(lollipopInterface=umlLollipopInterface)
        eventHandler.SetPreviousHandler(umlLollipopInterface.GetEventHandler())
        umlLollipopInterface.SetEventHandler(eventHandler)

        pubsubEngine: IUmlPubSubEngine  = requestingFrame.umlPubSubEngine

        # Update with our generated one
        pyutInterfaces.append(pyutInterface)
        with DlgEditInterface(parent=requestingFrame, lollipopInterface=umlLollipopInterface, umlPubSubEngine=pubsubEngine, pyutInterfaces=pyutInterfaces) as dlg:
            if dlg.ShowModal() == OK:
                requestingFrame.refresh()

    def _updateApplicationStatusListener(self, message: str):
        self.SetStatusText(text=message)

    def _frameModifiedListener(self, modifiedFrameId: str):

        self.logger.info(f'Frame Modified - {modifiedFrameId=}')

    def _frameLeftClickListener(self, frame: UmlFrame, umlPosition: UmlPosition):
        self.logger.info(f'Frame {frame.id}, clicked at {umlPosition=}')

    def _umlShapeListener(self, umlShape: UmlShape):
        self.logger.info(f'Shape was selected: {umlShape}')

    # noinspection PyUnusedLocal
    def _onUmlShapePreferences(self, event: CommandEvent):

        with DlgUmlShapesPreferences(parent=self) as dlg:
            if dlg.ShowModal() == OK:
                self.logger.info(f'Pressed Ok')
