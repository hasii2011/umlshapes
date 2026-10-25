
from logging import Logger
from logging import getLogger

from codeallybasic.Position import Position
from codeallybasic.Dimensions import Dimensions
from codeallybasic.SingletonV3 import SingletonV3
from codeallybasic.SecureConversions import SecureConversions

from umlshapes.preferences.Defaults import DEFAULT_ACTOR_SIZE
from umlshapes.preferences.Defaults import DEFAULT_ASSOCIATION_LABEL_FORMAT
from umlshapes.preferences.Defaults import DEFAULT_ASSOCIATION_LABEL_SIZE
from umlshapes.preferences.Defaults import DEFAULT_AUTO_GROW_LIFELINES
from umlshapes.preferences.Defaults import DEFAULT_BACKGROUND_COLOR
from umlshapes.preferences.Defaults import DEFAULT_CLASS_BACKGROUND_COLOR
from umlshapes.preferences.Defaults import DEFAULT_CLASS_TEXT_COLOR
from umlshapes.preferences.Defaults import DEFAULT_DARK_MODE_BACKGROUND_COLOR
from umlshapes.preferences.Defaults import DEFAULT_DARK_MODE_GRID_LINE_COLOR
from umlshapes.preferences.Defaults import DEFAULT_GRID_LINE_COLOR
from umlshapes.preferences.Defaults import DEFAULT_GRID_LINE_STYLE
from umlshapes.preferences.Defaults import DEFAULT_MESSAGE_LABEL_PLACEMENT
from umlshapes.preferences.Defaults import DEFAULT_SD_INSTANCE_DIMENSIONS
from umlshapes.preferences.Defaults import DEFAULT_REFLEXIVE_MESSAGE_WIDTH
from umlshapes.preferences.Defaults import DEFAULT_TEXT_BACKGROUND_COLOR
from umlshapes.preferences.Defaults import DEFAULT_EXECUTION_SHIFT_DELTA
from umlshapes.preferences.Defaults import DEFAULT_EXECUTION_WIDTH
from umlshapes.preferences.Defaults import DEFAULT_AUTO_GENERATE_EXECUTIONS
from umlshapes.preferences.Defaults import DEFAULT_TIME_STEP_HEIGHT
from umlshapes.preferences.Defaults import DEFAULT_UNIFORM_LIFELINE_LENGTH
from umlshapes.preferences.Defaults import DEFAULT_USE_CASE_SIZE
from umlshapes.preferences.Defaults import DEFAULT_FRAGMENT_HEADER_WIDTH
from umlshapes.preferences.Defaults import DEFAULT_FRAGMENT_HEADER_HEIGHT
from umlshapes.preferences.Defaults import DEFAULT_FRAGMENT_PADDING
from umlshapes.preferences.Defaults import FRAME_HEIGHT
from umlshapes.preferences.Defaults import FRAME_WIDTH

from umlshapes.types.DeltaXY import DeltaXY
from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlPenStyle import UmlPenStyle
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.WiggleFactor import WiggleFactor
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlFontFamily import UmlFontFamily

from umlshapes.links.UmlAssociationLabelFormat import UmlAssociationLabelFormat
from umlshapes.sd.SDMessageLabelPlacement import SDMessageLabelPlacement

from codeallybasic.DynamicConfiguration import DynamicConfiguration
from codeallybasic.DynamicConfiguration import KeyName
from codeallybasic.DynamicConfiguration import SectionName
from codeallybasic.DynamicConfiguration import Sections
from codeallybasic.DynamicConfiguration import ValueDescription
from codeallybasic.DynamicConfiguration import ValueDescriptions

DEFAULT_NAME_RELATIVE_HEIGHT: str = '0.10'
DEFAULT_LIFE_LINE_LENGTH:     str = '360'
DEFAULT_INSTANCE_Y:           str = '50'

MODULE_NAME:           str = 'umlshapes'
PREFERENCES_FILE_NAME: str = f'{MODULE_NAME}.ini'

TEST_POSITION: str = Position(20, 40).__str__()
TEST_SIZE:     str = str(Dimensions(width=FRAME_WIDTH + 300, height=FRAME_HEIGHT + 300))


PASTE_PREFERENCES: ValueDescriptions = ValueDescriptions(
    {
        KeyName('pasteStart'):   ValueDescription(defaultValue=str(UmlPosition(150, 150)), deserializer=UmlPosition.deSerialize),
        KeyName('pasteDeltaXY'): ValueDescription(defaultValue=str(DeltaXY(100, 100)),     deserializer=DeltaXY.deSerialize),
    }
)
UML_SHAPE_PREFERENCES: ValueDescriptions = ValueDescriptions(
    {
        KeyName('textValue'):            ValueDescription(defaultValue='fac America magna iterum'),
        KeyName('noteText'):             ValueDescription(defaultValue='This is the note text'),
        KeyName('noteDimensions'):       ValueDescription(defaultValue=str(UmlDimensions(150, 50)), deserializer=UmlDimensions.deSerialize),
        KeyName('textDimensions'):       ValueDescription(defaultValue=str(UmlDimensions(125, 50)), deserializer=UmlDimensions.deSerialize),
        KeyName('useCaseDimensions'):    ValueDescription(defaultValue=DEFAULT_USE_CASE_SIZE,       deserializer=UmlDimensions.deSerialize),
        KeyName('textBold'):             ValueDescription(defaultValue='False',                     deserializer=SecureConversions.secureBoolean),
        KeyName('textItalicize'):        ValueDescription(defaultValue='False',                     deserializer=SecureConversions.secureBoolean),
        KeyName('textFontFamily'):       ValueDescription(defaultValue='Swiss',                     deserializer=UmlFontFamily.deSerialize),
        KeyName('textFontSize'):         ValueDescription(defaultValue='14',                        deserializer=SecureConversions.secureInteger),
        KeyName('textBackGroundColor'):  ValueDescription(defaultValue=DEFAULT_TEXT_BACKGROUND_COLOR, enumUseValue=True, deserializer=UmlColor),

        KeyName('displayConstructor'):   ValueDescription(defaultValue='True',                      deserializer=SecureConversions.secureBoolean),
        KeyName('displayDunderMethods'): ValueDescription(defaultValue='True',                      deserializer=SecureConversions.secureBoolean),
        KeyName('classDimensions'):      ValueDescription(defaultValue=str(UmlDimensions(150, 75)), deserializer=UmlDimensions.deSerialize),
        KeyName('classBackGroundColor'): ValueDescription(defaultValue=DEFAULT_CLASS_BACKGROUND_COLOR, enumUseValue=True, deserializer=UmlColor),
        KeyName('classTextColor'):       ValueDescription(defaultValue=DEFAULT_CLASS_TEXT_COLOR,       enumUseValue=True, deserializer=UmlColor),
        KeyName('classTextMargin'):      ValueDescription(defaultValue='10',                        deserializer=SecureConversions.secureInteger),
        KeyName('actorSize'):            ValueDescription(defaultValue=DEFAULT_ACTOR_SIZE,          deserializer=UmlDimensions.deSerialize),

        KeyName('autoSizeHeightAdjustment'): ValueDescription(defaultValue='0.20', deserializer=SecureConversions.secureFloat),
        KeyName('autoSizeWidthAdjustment'):  ValueDescription(defaultValue='0.20', deserializer=SecureConversions.secureFloat),
        KeyName('lineHeightAdjustment'):     ValueDescription(defaultValue='1',    deserializer=SecureConversions.secureInteger),
        KeyName('autoResizeShapesOnEdit'):   ValueDescription(defaultValue='True', deserializer=SecureConversions.secureBoolean),
        KeyName('controlPointSize'):         ValueDescription(defaultValue='4',    deserializer=SecureConversions.secureInteger),
        KeyName('shapeWiggleFactor'):        ValueDescription(defaultValue=str(WiggleFactor()), deserializer=WiggleFactor.deSerialize),

    }
)
DIAGRAM_PREFERENCES: ValueDescriptions = ValueDescriptions(
    {
        KeyName('virtualWindowWidth'):      ValueDescription(defaultValue='16000', deserializer=SecureConversions.secureInteger),
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

NAME_PREFERENCES: ValueDescriptions = ValueDescriptions(
    {
        KeyName('defaultClassName'):       ValueDescription(defaultValue='ClassName'),
        KeyName('defaultNameInterface'):   ValueDescription(defaultValue='IClassInterface'),
        KeyName('defaultNameUsecase'):     ValueDescription(defaultValue='UseCaseName'),
        KeyName('defaultNameActor'):       ValueDescription(defaultValue='ActorName'),
        KeyName('defaultNameMethod'):      ValueDescription(defaultValue='MethodName'),
        KeyName('defaultNameField'):       ValueDescription(defaultValue='FieldName'),
        KeyName('defaultNameParameter'):   ValueDescription(defaultValue='ParameterName'),
        KeyName('defaultAssociationName'): ValueDescription(defaultValue='Association'),
        KeyName('defaultInstanceName'):    ValueDescription(defaultValue='Unnamed instance'),
    }
)
SEQUENCE_DIAGRAM_PREFERENCES: ValueDescriptions = ValueDescriptions(
    {
        KeyName('instanceDimensions'):               ValueDescription(defaultValue=DEFAULT_SD_INSTANCE_DIMENSIONS, deserializer=UmlDimensions.deSerialize),
        KeyName('instanceYPosition'):                ValueDescription(defaultValue=DEFAULT_INSTANCE_Y,             deserializer=SecureConversions.secureInteger),
        KeyName('instanceNameRelativeHeight'):       ValueDescription(defaultValue=DEFAULT_NAME_RELATIVE_HEIGHT,   deserializer=SecureConversions.secureFloat),
        KeyName('initialLifeLineLength'):            ValueDescription(defaultValue=DEFAULT_LIFE_LINE_LENGTH, deserializer=SecureConversions.secureInteger),
        KeyName('messageArrowHeadSize'):             ValueDescription(defaultValue='10.0', deserializer=SecureConversions.secureFloat),
        KeyName('messageLabelPlacement'):            ValueDescription(defaultValue=DEFAULT_MESSAGE_LABEL_PLACEMENT, enumUseValue=True, deserializer=SDMessageLabelPlacement),
        KeyName('autoGrowLifeLines'):                ValueDescription(defaultValue=str(DEFAULT_AUTO_GROW_LIFELINES),     deserializer=SecureConversions.secureBoolean),
        KeyName('uniformLifeLineLength'):            ValueDescription(defaultValue=str(DEFAULT_UNIFORM_LIFELINE_LENGTH), deserializer=SecureConversions.secureBoolean),
        KeyName('timeStepHeight'):                   ValueDescription(defaultValue=str(DEFAULT_TIME_STEP_HEIGHT),        deserializer=SecureConversions.secureInteger),
        KeyName('reflexiveMessageWidth'):            ValueDescription(defaultValue=str(DEFAULT_REFLEXIVE_MESSAGE_WIDTH), deserializer=SecureConversions.secureInteger),
        KeyName('executionWidth'):                  ValueDescription(defaultValue=str(DEFAULT_EXECUTION_WIDTH),        deserializer=SecureConversions.secureInteger),
        KeyName('autoGenerateExecutions'):          ValueDescription(defaultValue=str(DEFAULT_AUTO_GENERATE_EXECUTIONS), deserializer=SecureConversions.secureBoolean),
        KeyName('executionShiftDelta'):             ValueDescription(defaultValue=str(DEFAULT_EXECUTION_SHIFT_DELTA),  deserializer=SecureConversions.secureInteger),
        KeyName('fragmentHeaderWidth'):             ValueDescription(defaultValue=str(DEFAULT_FRAGMENT_HEADER_WIDTH),   deserializer=SecureConversions.secureInteger),
        KeyName('fragmentHeaderHeight'):            ValueDescription(defaultValue=str(DEFAULT_FRAGMENT_HEADER_HEIGHT),  deserializer=SecureConversions.secureInteger),
        KeyName('fragmentPadding'):                 ValueDescription(defaultValue=str(DEFAULT_FRAGMENT_PADDING),        deserializer=SecureConversions.secureInteger),
    }
)
ASSOCIATION_PREFERENCES: ValueDescriptions = ValueDescriptions(
    {
        KeyName('associationTextFontSize'):   ValueDescription(defaultValue='12', deserializer=SecureConversions.secureInteger),
        KeyName('diamondSize'):               ValueDescription(defaultValue='7',  deserializer=SecureConversions.secureInteger),
        KeyName('associationLabelSize'):      ValueDescription(defaultValue=DEFAULT_ASSOCIATION_LABEL_SIZE,   deserializer=UmlDimensions.deSerialize),
        KeyName('associationLabelFormat'):    ValueDescription(defaultValue=DEFAULT_ASSOCIATION_LABEL_FORMAT, deserializer=UmlAssociationLabelFormat.toWxFormat),
        KeyName('associationLabelOffsetFix'): ValueDescription(defaultValue='30', deserializer=SecureConversions.secureInteger),
    }
)

LOLLIPOP_PREFERENCES: ValueDescriptions = ValueDescriptions(
    {
        KeyName('lollipopLineLength'):   ValueDescription(defaultValue='90',  deserializer=SecureConversions.secureInteger),
        KeyName('lollipopCircleRadius'): ValueDescription(defaultValue='4',   deserializer=SecureConversions.secureInteger),
        KeyName('interfaceNameIndent'):  ValueDescription(defaultValue='10',  deserializer=SecureConversions.secureInteger),
        KeyName('hitAreaInflationRate'): ValueDescription(defaultValue='2',   deserializer=SecureConversions.secureInteger),
        KeyName('horizontalOffset'):     ValueDescription(defaultValue='0.5', deserializer=SecureConversions.secureFloat),
    }
)
DEBUG_PREFERENCES: ValueDescriptions = ValueDescriptions(
    {
        KeyName('debugDiagramFrame'):       ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
        KeyName('debugBasicShape'):         ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
        KeyName('classDiagramFromCtxMenu'): ValueDescription(defaultValue='True',  deserializer=SecureConversions.secureBoolean),
        KeyName('trackMouse'):              ValueDescription(defaultValue='True',  deserializer=SecureConversions.secureBoolean),
        KeyName('trackMouseInterval'):      ValueDescription(defaultValue='10',    deserializer=SecureConversions.secureInteger),
        KeyName('drawLabelMarker'):         ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
        KeyName('debugSDInstance'):         ValueDescription(defaultValue='True',  deserializer=SecureConversions.secureBoolean),
        KeyName('inTestMode'):              ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
        KeyName('testPosition'):            ValueDescription(defaultValue=TEST_POSITION, deserializer=Position.deSerialize),
        KeyName('testSize'):                ValueDescription(defaultValue=TEST_SIZE,     deserializer=Dimensions.deSerialize),
        KeyName('genericClassName'):        ValueDescription(defaultValue='False', deserializer=SecureConversions.secureBoolean),
        KeyName('enableCompositeShapeLiveDragging'): ValueDescription(defaultValue='True', deserializer=SecureConversions.secureBoolean),
    }
)

sections: Sections = Sections(
    {
        SectionName('UMLShapes'):        UML_SHAPE_PREFERENCES,
        SectionName('Paste'):            PASTE_PREFERENCES,
        SectionName('Diagram'):          DIAGRAM_PREFERENCES,
        SectionName('Names'):            NAME_PREFERENCES,
        SectionName('SequenceDiagrams'): SEQUENCE_DIAGRAM_PREFERENCES,
        SectionName('Associations'):     ASSOCIATION_PREFERENCES,
        SectionName('Lollipops'):        LOLLIPOP_PREFERENCES,
        SectionName('Debug'):            DEBUG_PREFERENCES,
    }
)


class UmlPreferences(DynamicConfiguration, metaclass=SingletonV3):

    def __init__(self):
        self._logger: Logger = getLogger(__name__)

        super().__init__(baseFileName=f'{PREFERENCES_FILE_NAME}', moduleName=MODULE_NAME, sections=sections)
