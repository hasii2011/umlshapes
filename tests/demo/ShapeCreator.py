
from typing import Callable
from typing import Dict
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx import ID_OK
from wx import OK

from wx.lib.ogl import ShapeEvtHandler

from pyutmodelv2.PyutActor import PyutActor
from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutField import PyutField
from pyutmodelv2.PyutField import PyutFields
from pyutmodelv2.PyutMethod import PyutMethod
from pyutmodelv2.PyutMethod import PyutMethods
from pyutmodelv2.PyutMethod import PyutParameters
from pyutmodelv2.PyutNote import PyutNote
from pyutmodelv2.PyutParameter import PyutParameter
from pyutmodelv2.PyutText import PyutText
from pyutmodelv2.PyutType import PyutType
from pyutmodelv2.PyutUseCase import PyutUseCase

from pyutmodelv2.enumerations.PyutDisplayParameters import PyutDisplayParameters
from pyutmodelv2.enumerations.PyutStereotype import PyutStereotype
from pyutmodelv2.enumerations.PyutVisibility import PyutVisibility

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.dialogs.DlgEditActor import DlgEditActor
from umlshapes.dialogs.DlgEditNote import DlgEditNote
from umlshapes.dialogs.DlgEditText import DlgEditText
from umlshapes.dialogs.DlgEditUseCase import DlgEditUseCase

from umlshapes.eventengine.UmlEventEngine import UmlEventEngine
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.preferences.UmlPreferences import UmlPreferences

from umlshapes.shapes.UmlActor import UmlActor
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlText import UmlText
from umlshapes.shapes.UmlUseCase import UmlUseCase

from umlshapes.shapes.eventhandlers.UmlActorEventHandler import UmlActorEventHandler
from umlshapes.shapes.eventhandlers.UmlClassEventHandler import UmlClassEventHandler
from umlshapes.shapes.eventhandlers.UmlNoteEventHandler import UmlNoteEventHandler
from umlshapes.shapes.eventhandlers.UmlTextEventHandler import UmlTextEventHandler
from umlshapes.shapes.eventhandlers.UmlUseCaseEventHandler import UmlUseCaseEventHandler

from umlshapes.types.Common import ModelObject
from umlshapes.types.Common import UmlShape

from umlshapes.types.UmlPosition import UmlPosition

from tests.demo.DemoCommon import ID_REFERENCE
from tests.demo.DemoCommon import INCREMENT_X
from tests.demo.DemoCommon import INCREMENT_Y
from tests.demo.DemoCommon import INITIAL_X
from tests.demo.DemoCommon import INITIAL_Y
from tests.demo.DemoCommon import Identifiers

CreateModel      = Callable[[], ModelObject]
InvokeEditDialog = Callable[[ModelObject], None]


@dataclass
class ShapeDescription:
    umlShape:         type[UmlShape]        = cast(type[UmlShape], None)
    modelClass:       type[ModelObject]     = cast(type[ModelObject], None)
    createModel:      CreateModel           = cast(CreateModel, None)
    invokeEditDialog: InvokeEditDialog      = cast(InvokeEditDialog, None)
    eventHandler:     type[ShapeEvtHandler] = cast(type[ShapeEvtHandler], None)
    defaultValue:     str = ''
    instanceCounter:  int = 0


ShapesToCreate = NewType('ShapesToCreate', Dict[ID_REFERENCE, ShapeDescription])


class ShapeCreator:

    def __init__(self, diagramFrame: ClassDiagramFrame, umlEventEngine: UmlEventEngine):

        self.logger: Logger = getLogger(__name__)

        self._diagramFrame:   ClassDiagramFrame = diagramFrame
        self._umlEventEngine: UmlEventEngine    = umlEventEngine

        self._currentPosition: UmlPosition = UmlPosition(x=INITIAL_X, y=INITIAL_Y)

        self._preferences: UmlPreferences = UmlPreferences()
        self._textCounter:        int = 0
        self._noteCounter:        int = 0
        self._useCaseCounter:     int = 0
        self._actorCounter:       int = 0
        self._classCounter:       int = 0

        shapeUmlText:    ShapeDescription = ShapeDescription(
            umlShape=UmlText,
            modelClass=PyutText,
            invokeEditDialog=self._invokeEditTextDialog,        # type: ignore
            eventHandler=UmlTextEventHandler,
            defaultValue=self._preferences.textValue
        )
        shapeUmlNote:    ShapeDescription = ShapeDescription(
            umlShape=UmlNote,
            modelClass=PyutNote,
            invokeEditDialog=self._invokeEditNoteDialog,        # type: ignore
            eventHandler=UmlNoteEventHandler,
            defaultValue=self._preferences.noteText
        )
        shapeUmlUseCase: ShapeDescription = ShapeDescription(
            umlShape=UmlUseCase,
            modelClass=PyutUseCase,
            invokeEditDialog=self._invokeEditUseCaseDialog,     # type: ignore
            eventHandler=UmlUseCaseEventHandler,
            defaultValue=self._preferences.defaultNameUsecase
        )
        shapeUmlActor:   ShapeDescription = ShapeDescription(
            umlShape=UmlActor,
            modelClass=PyutActor,
            invokeEditDialog=self._invokeEditActorDialog,       # type: ignore
            eventHandler=UmlActorEventHandler,
            defaultValue=self._preferences.defaultNameActor
        )
        shapeUmlClass:   ShapeDescription = ShapeDescription(
            umlShape=UmlClass,
            createModel=lambda: self._createDemoPyutClass,
            eventHandler=UmlClassEventHandler,
            defaultValue=self._preferences.defaultClassName
        )

        self._shapes: ShapesToCreate = ShapesToCreate(
            {
                Identifiers.ID_DISPLAY_UML_TEXT:     shapeUmlText,
                Identifiers.ID_DISPLAY_UML_NOTE:     shapeUmlNote,
                Identifiers.ID_DISPLAY_UML_USE_CASE: shapeUmlUseCase,
                Identifiers.ID_DISPLAY_UML_ACTOR:    shapeUmlActor,
                Identifiers.ID_DISPLAY_UML_CLASS:    shapeUmlClass,
            }
        )

    def displayShape(self, idReference: ID_REFERENCE):

        shapeDescription: ShapeDescription = self._shapes[idReference]

        defaultValue: str = f'{shapeDescription.defaultValue} {shapeDescription.instanceCounter}'
        if shapeDescription.modelClass is None:
            modelClass = shapeDescription.createModel()
        else:
            modelClass = shapeDescription.modelClass(defaultValue)
        shapeDescription.instanceCounter += 1

        umlShape: UmlShape = shapeDescription.umlShape(modelClass)      # type: ignore

        umlPosition: UmlPosition = self._computePosition()
        umlShape.umlFrame = self._diagramFrame
        umlShape.position = umlPosition

        diagram: UmlDiagram = self._diagramFrame.umlDiagram

        diagram.AddShape(umlShape)
        umlShape.Show(True)

        eventHandler = shapeDescription.eventHandler()
        eventHandler.SetShape(umlShape)
        eventHandler.umlEventEngine = self._umlEventEngine
        eventHandler.SetPreviousHandler(umlShape.GetEventHandler())

        umlShape.SetEventHandler(eventHandler)
        self._diagramFrame.refresh()
        if shapeDescription.invokeEditDialog is not None:
            shapeDescription.invokeEditDialog(modelClass)
            self._diagramFrame.refresh()

    def _computePosition(self) -> UmlPosition:

        currentPosition: UmlPosition = UmlPosition(x=self._currentPosition.x, y=self._currentPosition.y)

        self._currentPosition.x += INCREMENT_X
        self._currentPosition.y += INCREMENT_Y

        return currentPosition

    @property
    def _createDemoPyutClass(self) -> PyutClass:

        className: str = f'{self._preferences.defaultClassName} {self._classCounter}'
        self._classCounter += 1
        pyutClass: PyutClass  = PyutClass(name=className)
        pyutClass.stereotype  = PyutStereotype.METACLASS
        pyutClass.showFields  = True
        pyutClass.showMethods = True
        pyutClass.displayParameters = PyutDisplayParameters.UNSPECIFIED

        pyutField1: PyutField = PyutField(
            name='DemoField1',
            visibility=PyutVisibility.PUBLIC,
            type=PyutType('float'),
            defaultValue='42.0'
        )

        pyutField2: PyutField = PyutField(
            name='DemoField2',
            visibility=PyutVisibility.PUBLIC,
            type=PyutType('int'),
            defaultValue='666'
        )

        pyutClass.fields  = PyutFields([pyutField1, pyutField2])

        pyutMethod:    PyutMethod    = PyutMethod(name='DemoMethod', visibility=PyutVisibility.PUBLIC)
        pyutParameter: PyutParameter = PyutParameter(name='DemoParameter', type=PyutType("str"), defaultValue='Ozzee')

        pyutMethod.parameters = PyutParameters([pyutParameter])

        constructorMethod: PyutMethod = PyutMethod(name='__init__')
        constructorMethod.parameters = self._manyParameters()
        dunderStrMethod:   PyutMethod = PyutMethod(name='__str__', visibility=PyutVisibility.PUBLIC, returnType=PyutType(value='str'))

        pyutClass.methods = PyutMethods([constructorMethod, pyutMethod, dunderStrMethod])

        return pyutClass

    def _manyParameters(self) -> PyutParameters:

        pyutParameters: PyutParameters = PyutParameters([])

        pyutParameter1: PyutParameter = PyutParameter(name='parameter1', type=PyutType("str"),   defaultValue='Ozzee')
        pyutParameter2: PyutParameter = PyutParameter(name='parameter2', type=PyutType("int"),   defaultValue='0')
        pyutParameter3: PyutParameter = PyutParameter(name='parameter3', type=PyutType("float"), defaultValue='42.00')

        pyutParameters.append(pyutParameter1)
        pyutParameters.append(pyutParameter2)
        pyutParameters.append(pyutParameter3)

        return pyutParameters

    def _invokeEditNoteDialog(self, pyutNote: PyutNote):

        self.logger.info(f'{pyutNote=}')

        with DlgEditNote(self._diagramFrame, pyutNote=pyutNote) as dlg:
            if dlg.ShowModal() == OK:
                self.logger.info(f'UpdatedNote: {pyutNote}')

    def _invokeEditTextDialog(self, pyutText: PyutText):

        self.logger.info(f'{pyutText=}')

        with DlgEditText(self._diagramFrame, pyutText=pyutText) as dlg:
            if dlg.ShowModal() == OK:
                self.logger.info(f'Updated text: {pyutText}')

    def _invokeEditUseCaseDialog(self, pyutUseCase: PyutUseCase):

        self.logger.info(f'{pyutUseCase=}')

        with DlgEditUseCase(self._diagramFrame, useCaseName=pyutUseCase.name) as dlg:
            if dlg.ShowModal() == ID_OK:
                pyutUseCase.name = dlg.useCaseName
                self.logger.info(f'Updated use case: {pyutUseCase}')
            else:
                self.logger.warning('Not Ok')

    def _invokeEditActorDialog(self, pyutActor: PyutActor) -> None:

        with DlgEditActor(self._diagramFrame, actorName=pyutActor.name) as dlg:
            if dlg.ShowModal() == ID_OK:
                pyutActor.name = dlg.actorName
                self.logger.info(f'Updated note: {pyutActor}')
            else:
                self.logger.warning('Not Ok')
