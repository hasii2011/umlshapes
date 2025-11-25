
from typing import Callable
from typing import Dict
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from umlmodel.Actor import Actor
from umlmodel.Class import Class
from umlmodel.Field import Field
from umlmodel.Field import Fields
from umlmodel.FieldType import FieldType
from umlmodel.Method import Method
from umlmodel.Method import Methods
from umlmodel.Method import Parameters
from umlmodel.Note import Note
from umlmodel.Parameter import Parameter
from umlmodel.ParameterType import ParameterType

from umlmodel.ReturnType import ReturnType
from umlmodel.UseCase import UseCase
from umlmodel.Text import Text
from umlmodel.enumerations.DisplayParameters import DisplayParameters
from umlmodel.enumerations.Stereotype import Stereotype
from umlmodel.enumerations.Visibility import Visibility

from wx import ID_OK
from wx import OK

from umlshapes.ShapeTypes import UmlShapeGenre
from umlshapes.lib.ogl import ShapeEvtHandler

from umlshapes.UmlDiagram import UmlDiagram

from umlshapes.dialogs.DlgEditActor import DlgEditActor
from umlshapes.dialogs.DlgEditNote import DlgEditNote
from umlshapes.dialogs.DlgEditText import DlgEditText
from umlshapes.dialogs.DlgEditUseCase import DlgEditUseCase

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine
from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame
from umlshapes.preferences.UmlPreferences import UmlPreferences
from umlshapes.UmlBaseEventHandler import UmlBaseEventHandler

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

from umlshapes.types.UmlPosition import UmlPosition

from tests.demo.DemoCommon import ID_REFERENCE
from tests.demo.DemoCommon import INCREMENT_X
from tests.demo.DemoCommon import INCREMENT_Y
from tests.demo.DemoCommon import INITIAL_X
from tests.demo.DemoCommon import INITIAL_Y
from tests.demo.DemoCommon import Identifiers

CreateModel      = Callable[[], ModelObject]
InvokeEditDialog = Callable[[ModelObject, ClassDiagramFrame], None]


@dataclass
class ShapeDescription:
    umlShape:         type[UmlShapeGenre]   = cast(type[UmlShapeGenre], None)
    modelClass:       type[ModelObject]     = cast(type[ModelObject], None)
    createModel:      CreateModel           = cast(CreateModel, None)
    invokeEditDialog: InvokeEditDialog      = cast(InvokeEditDialog, None)
    eventHandler:     type[ShapeEvtHandler] = cast(type[ShapeEvtHandler], None)
    defaultValue:     str = ''
    instanceCounter:  int = 1000


ShapesToCreate = NewType('ShapesToCreate', Dict[ID_REFERENCE, ShapeDescription])


class ShapeCreator:

    def __init__(self, umlPubSubEngine: UmlPubSubEngine):

        self.logger: Logger = getLogger(__name__)

        self._umlPubSubEngine: UmlPubSubEngine   = umlPubSubEngine

        self._currentPosition: UmlPosition = UmlPosition(x=INITIAL_X, y=INITIAL_Y)

        self._preferences: UmlPreferences = UmlPreferences()
        self._textCounter:        int = 0
        self._noteCounter:        int = 0
        self._useCaseCounter:     int = 0
        self._actorCounter:       int = 0
        self._classCounter:       int = 1000

        shapeUmlText:    ShapeDescription = ShapeDescription(
            umlShape=UmlText,
            modelClass=Text,
            invokeEditDialog=self._invokeEditTextDialog,        # type: ignore
            eventHandler=UmlTextEventHandler,
            defaultValue=self._preferences.textValue
        )
        shapeUmlNote:    ShapeDescription = ShapeDescription(
            umlShape=UmlNote,
            modelClass=Note,
            invokeEditDialog=self._invokeEditNoteDialog,        # type: ignore
            eventHandler=UmlNoteEventHandler,
            defaultValue=self._preferences.noteText
        )
        shapeUmlUseCase: ShapeDescription = ShapeDescription(
            umlShape=UmlUseCase,
            modelClass=UseCase,
            invokeEditDialog=self._invokeEditUseCaseDialog,     # type: ignore
            eventHandler=UmlUseCaseEventHandler,
            defaultValue=self._preferences.defaultNameUsecase
        )
        shapeUmlActor:   ShapeDescription = ShapeDescription(
            umlShape=UmlActor,
            modelClass=Actor,
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

    def displayShape(self, idReference: ID_REFERENCE, diagramFrame: ClassDiagramFrame,):

        shapeDescription: ShapeDescription = self._shapes[idReference]

        defaultValue: str = f'{shapeDescription.defaultValue} {shapeDescription.instanceCounter}'
        if shapeDescription.modelClass is None:
            modelClass = shapeDescription.createModel()
        else:
            modelClass = shapeDescription.modelClass(defaultValue)
        shapeDescription.instanceCounter += 1

        umlShape: UmlShapeGenre = shapeDescription.umlShape(modelClass)      # type: ignore

        umlPosition: UmlPosition = self._computePosition()
        umlShape.umlFrame = diagramFrame
        umlShape.position = umlPosition

        diagram: UmlDiagram = diagramFrame.umlDiagram

        diagram.AddShape(umlShape)
        umlShape.Show(True)

        eventHandler = shapeDescription.eventHandler()
        eventHandler.SetShape(umlShape)
        cast(UmlBaseEventHandler, eventHandler).umlPubSubEngine = self._umlPubSubEngine
        eventHandler.SetPreviousHandler(umlShape.GetEventHandler())
        umlShape.SetEventHandler(eventHandler)

        diagramFrame.refresh()
        if shapeDescription.invokeEditDialog is not None:
            shapeDescription.invokeEditDialog(modelClass, diagramFrame)
            diagramFrame.refresh()

    def _computePosition(self) -> UmlPosition:
        """
        TODO: Put in an option to compute position or just put at a fixed
        place.  For UI testing we want fixed

        Returns:

        """

        currentPosition: UmlPosition = UmlPosition(x=self._currentPosition.x, y=self._currentPosition.y)


        # self._currentPosition.x += INCREMENT_X
        # self._currentPosition.y += INCREMENT_Y

        return currentPosition

    @property
    def _createDemoPyutClass(self) -> Class:

        className: str = f'{self._preferences.defaultClassName} {self._classCounter}'
        self._classCounter += 1
        pyutClass: Class      = Class(name=className)
        pyutClass.stereotype  = Stereotype.METACLASS
        pyutClass.showFields  = True
        pyutClass.showMethods = True
        pyutClass.displayParameters = DisplayParameters.UNSPECIFIED

        pyutField1: Field = Field(
            name='DemoField1',
            visibility=Visibility.PUBLIC,
            type=FieldType('float'),
            defaultValue='42.0'
        )

        pyutField2: Field = Field(
            name='DemoField2',
            visibility=Visibility.PUBLIC,
            type=FieldType('int'),
            defaultValue='666'
        )

        pyutClass.fields  = Fields([pyutField1, pyutField2])

        pyutMethod:    Method    = Method(name='DemoMethod', visibility=Visibility.PUBLIC)
        pyutParameter: Parameter = Parameter(name='DemoParameter', type=ParameterType("str"), defaultValue='Ozzee')

        pyutMethod.parameters = Parameters([pyutParameter])

        constructorMethod: Method = Method(name='__init__')
        constructorMethod.parameters = self._manyParameters()
        dunderStrMethod:   Method = Method(name='__str__', visibility=Visibility.PUBLIC, returnType=ReturnType(value='str'))

        pyutClass.methods = Methods([constructorMethod, pyutMethod, dunderStrMethod])

        return pyutClass

    def _manyParameters(self) -> Parameters:

        pyutParameters: Parameters = Parameters([])

        pyutParameter1: Parameter = Parameter(name='parameter1', type=ParameterType("str"),   defaultValue='Ozzee')
        pyutParameter2: Parameter = Parameter(name='parameter2', type=ParameterType("int"),   defaultValue='0')
        pyutParameter3: Parameter = Parameter(name='parameter3', type=ParameterType("float"), defaultValue='42.00')

        pyutParameters.append(pyutParameter1)
        pyutParameters.append(pyutParameter2)
        pyutParameters.append(pyutParameter3)

        return pyutParameters

    def _invokeEditNoteDialog(self, pyutNote: Note, diagramFrame: ClassDiagramFrame):

        self.logger.info(f'{pyutNote=}')

        with DlgEditNote(diagramFrame, note=pyutNote) as dlg:
            if dlg.ShowModal() == OK:
                self.logger.info(f'UpdatedNote: {pyutNote}')

    def _invokeEditTextDialog(self, pyutText: Text, diagramFrame: ClassDiagramFrame,):

        self.logger.info(f'{pyutText=}')

        with DlgEditText(diagramFrame, text=pyutText) as dlg:
            if dlg.ShowModal() == OK:
                self.logger.info(f'Updated text: {pyutText}')

    def _invokeEditUseCaseDialog(self, pyutUseCase: UseCase, diagramFrame: ClassDiagramFrame,):

        self.logger.info(f'{pyutUseCase=}')

        with DlgEditUseCase(diagramFrame, useCaseName=pyutUseCase.name) as dlg:
            if dlg.ShowModal() == ID_OK:
                pyutUseCase.name = dlg.useCaseName
                self.logger.info(f'Updated use case: {pyutUseCase}')
            else:
                self.logger.warning('Not Ok')

    def _invokeEditActorDialog(self, pyutActor: Actor, diagramFrame: ClassDiagramFrame,) -> None:

        with DlgEditActor(diagramFrame, actorName=pyutActor.name) as dlg:
            if dlg.ShowModal() == ID_OK:
                pyutActor.name = dlg.actorName
                self.logger.info(f'Updated note: {pyutActor}')
            else:
                self.logger.warning('Not Ok')
