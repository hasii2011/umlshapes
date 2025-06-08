
from logging import Logger
from logging import getLogger

from codeallybasic.SecureConversions import SecureConversions
from codeallybasic.SingletonV3 import SingletonV3

from umlshapes.types.UmlColor import UmlColor

from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPenStyle import UmlPenStyle
from umlshapes.types.UmlFontFamily import UmlFontFamily

from codeallybasic.DynamicConfiguration import DynamicConfiguration
from codeallybasic.DynamicConfiguration import KeyName
from codeallybasic.DynamicConfiguration import SectionName
from codeallybasic.DynamicConfiguration import Sections
from codeallybasic.DynamicConfiguration import ValueDescription
from codeallybasic.DynamicConfiguration import ValueDescriptions

MODULE_NAME:           str = 'ogl'
PREFERENCES_FILE_NAME: str = f'{MODULE_NAME}.ini'

DEFAULT_BACKGROUND_COLOR:           str = UmlColor.WHITE.value
DEFAULT_DARK_MODE_BACKGROUND_COLOR: str = UmlColor.DIM_GREY.value

DEFAULT_GRID_LINE_COLOR:           str = UmlColor.AF_BLUE.value
DEFAULT_DARK_MODE_GRID_LINE_COLOR: str = UmlColor.WHITE.value

DEFAULT_CLASS_BACKGROUND_COLOR: str = UmlColor.MINT_CREAM.value
DEFAULT_CLASS_TEXT_COLOR:       str = UmlColor.BLACK.value
DEFAULT_GRID_LINE_STYLE:        str = UmlPenStyle.DOT.value

# When the text value is selected
DEFAULT_TEXT_BACKGROUND_COLOR:  str = UmlColor.WHITE.value

DEFAULT_USE_CASE_SIZE:          str = str(UmlDimensions(width=100, height=60))
DEFAULT_ACTOR_SIZE:             str = str(UmlDimensions(width=80, height=100))
DEFAULT_ASSOCIATION_LABEL_SIZE: str = str(UmlDimensions(width=20, height=14))


OGL_PROPERTIES: ValueDescriptions = ValueDescriptions(
    {
        KeyName('textValue'):            ValueDescription(defaultValue='fac America magna iterum'),
        KeyName('noteText'):             ValueDescription(defaultValue='This is the note text'),
        KeyName('noteDimensions'):       ValueDescription(defaultValue=str(UmlDimensions(100, 50)), deserializer=UmlDimensions.deSerialize),
        KeyName('textDimensions'):       ValueDescription(defaultValue=str(UmlDimensions(125, 50)), deserializer=UmlDimensions.deSerialize),
        KeyName('textBold'):             ValueDescription(defaultValue='False',                     deserializer=SecureConversions.secureBoolean),
        KeyName('textItalicize'):        ValueDescription(defaultValue='False',                     deserializer=SecureConversions.secureBoolean),
        KeyName('textFontFamily'):       ValueDescription(defaultValue='Swiss',                     deserializer=UmlFontFamily.deSerialize),
        KeyName('textFontSize'):         ValueDescription(defaultValue='14',                        deserializer=SecureConversions.secureInteger),
        KeyName('textBackGroundColor'):  ValueDescription(defaultValue=DEFAULT_TEXT_BACKGROUND_COLOR, enumUseValue=True, deserializer=UmlColor),
        KeyName('textBackGroundColor'):  ValueDescription(defaultValue=DEFAULT_TEXT_BACKGROUND_COLOR, enumUseValue=True, deserializer=UmlColor),

        KeyName('displayConstructor'):   ValueDescription(defaultValue='True',                      deserializer=SecureConversions.secureBoolean),
        KeyName('displayDunderMethods'): ValueDescription(defaultValue='True',                      deserializer=SecureConversions.secureBoolean),
        KeyName('classDimensions'):      ValueDescription(defaultValue=str(UmlDimensions(150, 75)), deserializer=UmlDimensions.deSerialize),
        KeyName('classBackGroundColor'): ValueDescription(defaultValue=DEFAULT_CLASS_BACKGROUND_COLOR, enumUseValue=True, deserializer=UmlColor),
        KeyName('classTextColor'):       ValueDescription(defaultValue=DEFAULT_CLASS_TEXT_COLOR,       enumUseValue=True, deserializer=UmlColor),
        KeyName('classTextMargin'):      ValueDescription(defaultValue='10',                        deserializer=SecureConversions.secureInteger),
        KeyName('useCaseSize'):          ValueDescription(defaultValue=DEFAULT_USE_CASE_SIZE,       deserializer=UmlDimensions.deSerialize),
        KeyName('actorSize'):            ValueDescription(defaultValue=DEFAULT_ACTOR_SIZE,          deserializer=UmlDimensions.deSerialize),

        KeyName('autoSizeHeightAdjustment'): ValueDescription(defaultValue='0.20', deserializer=SecureConversions.secureFloat),
        KeyName('autoSizeWidthAdjustment'):  ValueDescription(defaultValue='0.20', deserializer=SecureConversions.secureFloat),
        KeyName('lineHeightAdjustment'):     ValueDescription(defaultValue='1',    deserializer=SecureConversions.secureInteger),
        KeyName('autoResizeShapesOnEdit'):   ValueDescription(defaultValue='True', deserializer=SecureConversions.secureBoolean),
        KeyName('controlPointSize'):         ValueDescription(defaultValue='4',    deserializer=SecureConversions.secureInteger),

    }
)
DIAGRAM_PROPERTIES: ValueDescriptions = ValueDescriptions(
    {
        KeyName('centerDiagram'):           ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
        KeyName('backGroundGridEnabled'):   ValueDescription(defaultValue='True',  deserializer=SecureConversions.secureBoolean),
        KeyName('snapToGrid'):              ValueDescription(defaultValue='True',  deserializer=SecureConversions.secureBoolean),
        KeyName('showParameters'):          ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
        KeyName('backgroundGridInterval'):  ValueDescription(defaultValue='25',    deserializer=SecureConversions.secureInteger),

        KeyName('gridLineStyle'):           ValueDescription(defaultValue=DEFAULT_GRID_LINE_STYLE,   enumUseValue=True, deserializer=UmlPenStyle),

        KeyName('backGroundColor'):         ValueDescription(defaultValue=DEFAULT_BACKGROUND_COLOR, enumUseValue=True, deserializer=UmlColor),
        KeyName('darkModeBackGroundColor'): ValueDescription(defaultValue=DEFAULT_DARK_MODE_BACKGROUND_COLOR, enumUseValue=True, deserializer=UmlColor),
        KeyName('gridLineColor'):           ValueDescription(defaultValue=DEFAULT_GRID_LINE_COLOR, enumUseValue=True, deserializer=UmlColor),
        KeyName('darkModeGridLineColor'):   ValueDescription(defaultValue=DEFAULT_DARK_MODE_GRID_LINE_COLOR, enumUseValue=True, deserializer=UmlColor),
    }
)

namePreferences: ValueDescriptions = ValueDescriptions(
    {
        KeyName('defaultClassName'):       ValueDescription(defaultValue='ClassName'),
        KeyName('defaultNameInterface'):   ValueDescription(defaultValue='IClassInterface'),
        KeyName('defaultNameUsecase'):     ValueDescription(defaultValue='UseCaseName'),
        KeyName('defaultNameActor'):       ValueDescription(defaultValue='ActorName'),
        KeyName('defaultNameMethod'):      ValueDescription(defaultValue='MethodName'),
        KeyName('defaultNameField'):       ValueDescription(defaultValue='FieldName'),
        KeyName('defaultNameParameter'):   ValueDescription(defaultValue='ParameterName'),
        KeyName('defaultAssociationName'): ValueDescription(defaultValue='Association'),
    }
)
sequenceDiagramPreferences: ValueDescriptions = ValueDescriptions(
    {
        KeyName('instanceYPosition'):  ValueDescription(defaultValue='50',                         deserializer=SecureConversions.secureInteger),
        KeyName('instanceDimensions'): ValueDescription(defaultValue=str(UmlDimensions(100, 400)), deserializer=UmlDimensions.deSerialize)
    }
)
associationsPreferences: ValueDescriptions = ValueDescriptions(
    {
        KeyName('associationTextFontSize'): ValueDescription(defaultValue='12', deserializer=SecureConversions.secureInteger),
        KeyName('diamondSize'):             ValueDescription(defaultValue='7',  deserializer=SecureConversions.secureInteger),
        KeyName('associationLabelSize'):    ValueDescription(defaultValue=DEFAULT_ASSOCIATION_LABEL_SIZE, deserializer=UmlDimensions.deSerialize),
    }
)

lollipopPreferences: ValueDescriptions = ValueDescriptions(
    {
        KeyName('lollipopLineLength'):   ValueDescription(defaultValue='90',  deserializer=SecureConversions.secureInteger),
        KeyName('lollipopCircleRadius'): ValueDescription(defaultValue='4',   deserializer=SecureConversions.secureInteger),
        KeyName('interfaceNameIndent'):  ValueDescription(defaultValue='10',  deserializer=SecureConversions.secureInteger),
        KeyName('horizontalOffset'):     ValueDescription(defaultValue='0.5', deserializer=SecureConversions.secureFloat),
        KeyName('hitAreaInflationRate'): ValueDescription(defaultValue='2', deserializer=SecureConversions.secureInteger),
    }
)
debugPreferences: ValueDescriptions = ValueDescriptions(
    {
        KeyName('debugDiagramFrame'):       ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
        KeyName('debugBasicShape'):         ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
        KeyName('classDiagramFromCtxMenu'): ValueDescription(defaultValue='True',  deserializer=SecureConversions.secureBoolean),
        KeyName('trackMouse'):              ValueDescription(defaultValue='True',  deserializer=SecureConversions.secureBoolean),
        KeyName('trackMouseInterval'):      ValueDescription(defaultValue='10',    deserializer=SecureConversions.secureInteger),
        KeyName('drawLabelMarker'):         ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
    }
)

sections: Sections = Sections(
    {
        SectionName('Ogl'):              OGL_PROPERTIES,
        SectionName('Diagram'):          DIAGRAM_PROPERTIES,
        SectionName('Names'):            namePreferences,
        SectionName('SequenceDiagrams'): sequenceDiagramPreferences,
        SectionName('Associations'):     associationsPreferences,
        SectionName('Lollipops'):        lollipopPreferences,
        SectionName('Debug'):            debugPreferences,
    }
)


class UmlPreferences(DynamicConfiguration, metaclass=SingletonV3):

    def __init__(self):
        self._logger: Logger = getLogger(__name__)

        super().__init__(baseFileName=f'{PREFERENCES_FILE_NAME}', moduleName=MODULE_NAME, sections=sections)
