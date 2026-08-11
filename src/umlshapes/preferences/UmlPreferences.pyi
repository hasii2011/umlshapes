
from codeallybasic.Dimensions import Dimensions
from codeallybasic.Position import Position

from umlshapes.types.DeltaXY import DeltaXY
from umlshapes.types.UmlColor import UmlColor
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlFontFamily import UmlFontFamily
from umlshapes.types.UmlPenStyle import UmlPenStyle
from umlshapes.types.UmlPosition import UmlPosition
from umlshapes.types.WiggleFactor import WiggleFactor


class UmlPreferences:
    textValue: str
    noteText: str
    noteDimensions: UmlDimensions
    textDimensions: UmlDimensions
    useCaseDimensions: UmlDimensions
    textBold: bool
    textItalicize: bool
    textFontFamily: UmlFontFamily
    textFontSize: int
    textBackGroundColor: UmlColor
    displayConstructor: bool
    displayDunderMethods: bool
    classDimensions: UmlDimensions
    classBackGroundColor: UmlColor
    classTextColor: UmlColor
    classTextMargin: int
    actorSize: UmlDimensions
    autoSizeHeightAdjustment: float
    autoSizeWidthAdjustment: float
    lineHeightAdjustment: int
    autoResizeShapesOnEdit: bool
    controlPointSize: int
    shapeWiggleFactor: WiggleFactor
    pasteStart: UmlPosition
    pasteDeltaXY: DeltaXY
    virtualWindowWidth: int
    centerDiagram: bool
    backGroundGridEnabled: bool
    snapToGrid: bool
    showParameters: bool
    backgroundGridInterval: int
    gridLineStyle: UmlPenStyle
    backGroundColor: UmlColor
    darkModeBackGroundColor: UmlColor
    gridLineColor: UmlColor
    darkModeGridLineColor: UmlColor
    defaultClassName: str
    defaultNameInterface: str
    defaultNameUsecase: str
    defaultNameActor: str
    defaultNameMethod: str
    defaultNameField: str
    defaultNameParameter: str
    defaultAssociationName: str
    defaultInstanceName: str
    instanceDimensions: UmlDimensions
    instanceYPosition: int
    instanceNameRelativeHeight: float
    enableCompositeShapeLiveDragging: bool
    initialLifeLineLength: int
    messageArrowHeadSize: float
    associationTextFontSize: int
    diamondSize: int
    associationLabelSize: UmlDimensions
    associationLabelFormat: int
    associationLabelOffsetFix: int
    lollipopLineLength: int
    lollipopCircleRadius: int
    interfaceNameIndent: int
    hitAreaInflationRate: int
    horizontalOffset: float
    debugDiagramFrame: bool
    debugBasicShape: bool
    classDiagramFromCtxMenu: bool
    trackMouse: bool
    trackMouseInterval: int
    drawLabelMarker: bool
    debugSDInstance: bool
    inTestMode: bool
    testPosition: Position
    testSize: Dimensions
    genericClassName: bool
