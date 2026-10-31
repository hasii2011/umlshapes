# Refactoring: Decouple `IUmlPubSubEngine` and Diagram Frame from Sequence Diagram Shape Constructors

## Objective
Remove both `IUmlPubSubEngine` and diagram canvas frames (`SequenceDiagramFrame` / `diagramFrame`) from the constructors of `UmlSDInstance` and `UmlSDMessage` (as well as helper shapes `SDInstanceConstrainer` and `UmlSDLifeLine`) in `umlshapes`. 

Align Sequence Diagram shapes with the established pattern used by `UmlClass`, `UmlActor`, `UmlUseCase`, and `UmlNote`: shapes are constructed with only their model/domain objects, and their canvas frame is assigned late via the `umlFrame` property setter or `diagram.AddShape()`. Event handlers that publish events dynamically obtain the pub-sub engine from the canvas frame (`self.GetCanvas().umlPubSubEngine` or `shape.umlFrame.umlPubSubEngine`) rather than holding a constructor-injected engine reference.

---

## Motivation & Architectural Defects

1. **Premature & Redundant Frame Coupling:**
   - In `umlshapes`, shapes like `UmlClass` and `UmlActor` do not require a frame in their constructors:
     - `UmlClass(modelClass)`
     - `UmlActor(modelActor)`
   - In the demo and command architecture (`CreateUmlClassCommand`, `CreateUmlActorCommand`, `LinkCreator`), shapes are instantiated as prototypes without any canvas or frame dependencies. Frame attachment occurs late during `_placeShapeOnFrame` / `_addUmlShapeToFrame` when the shape is added to the diagram (`diagram.AddShape(shape)`) and `shape.umlFrame = diagramFrame` is set.
   - Currently, `UmlSDInstance` forces `diagramFrame: SequenceDiagramFrame` into `__init__` solely to pass it to `SDInstanceConstrainer` and `UmlSDLifeLine`, which only use it to call `self.SetCanvas(diagramFrame)`.
   - Because `UmlSDInstance` inherits from wx OGL's `CompositeShape`, `CompositeShape.SetCanvas(theCanvas)` automatically propagates the canvas to all child shapes (`constrainingShape`, `instanceName`, `sdLifeLine`). Setting `umlSDInstance.umlFrame = diagramFrame` or adding it via `diagram.AddShape(umlSDInstance)` automatically sets the canvas across the entire composite hierarchy without requiring frame injection in the constructors.

2. **Redundant Pub-Sub Engine Injection:**
   - Every `UmlFrame` (including `SequenceDiagramFrame`) already owns and manages `self.umlPubSubEngine`.
   - Shapes and their event handlers already maintain a reference to their canvas frame via `GetCanvas()` / `umlFrame`.
   - In `UmlSDLifeLineEventHandler.OnLeftClick`, the handler already queries `umlFrame = sdLifeLine.GetCanvas()` to obtain the frame ID. Passing `IUmlPubSubEngine` into `UmlSDInstance.__init__` just to forward it to the event handler is redundant.

3. **Pollution of Pure I/O & Deserialization Layer (`umlio`):**
   - Serialization and deserialization in `umlio` translate XML to/from shapes and model objects.
   - Forcing `UmlSDInstance` and `UmlSDMessage` to require GUI canvas frames and pub-sub engines forces `umlio` to require active GUI frame and pub-sub parameters during deserialization, tightly coupling file I/O to runtime GUI event dispatching.

---

## Action Items

### 1. `SDInstanceConstrainer`
- **File:** `src/umlshapes/sd/SDInstanceConstrainer.py`
- Remove `diagramFrame: SequenceDiagramFrame` from `__init__`.
- Signature:
  ```python
  def __init__(self, width: Optional[int] = None):
  ```
- Remove `self.SetCanvas(diagramFrame)`.

### 2. `UmlSDLifeLine`
- **File:** `src/umlshapes/sd/UmlSDLifeLine.py`
- Remove `sequenceDiagramFrame: SequenceDiagramFrame` from `__init__`.
- Signature:
  ```python
  def __init__(self, instanceName: UmlInstanceName, instanceConstrainer: SDInstanceConstrainer):
  ```
- Remove `self.SetCanvas(sequenceDiagramFrame)`.

### 3. `UmlSDInstance`
- **File:** `src/umlshapes/sd/UmlSDInstance.py`
- Remove both `diagramFrame: 'SequenceDiagramFrame'` and `umlPubSubEngine: IUmlPubSubEngine` from `__init__`.
- Signature:
  ```python
  def __init__(self, sdInstance: SDInstance):
  ```
- Remove `self._umlPubSubEngine` attribute and `self.SetCanvas(diagramFrame)` from `__init__`.
- Update instantiation of `SDInstanceConstrainer` and `UmlSDLifeLine` to omit `diagramFrame`.
- Retain existing `umlFrame` property getter and setter:
  ```python
  @property
  def umlFrame(self) -> 'SequenceDiagramFrame':
      return self.GetCanvas()

  @umlFrame.setter
  def umlFrame(self, frame: 'SequenceDiagramFrame'):
      self.SetCanvas(frame)
  ```
  *(Note: wx OGL's `CompositeShape.SetCanvas` automatically cascades `theCanvas` down to all child shapes).*
- Update `_setEventHandlers()` so `UmlSDLifeLineEventHandler` is constructed without `umlPubSubEngine`.

### 4. `UmlSDLifeLineEventHandler`
- **File:** `src/umlshapes/sd/eventhandlers/UmlSDLifeLineEventHandler.py`
- Remove `umlPubSubEngine: IUmlPubSubEngine` from `__init__`.
- In `OnLeftClick()` (and any other event dispatch methods), obtain the engine directly from the canvas frame:
  ```python
  sdLifeLine: UmlSDLifeLine = self.GetShape()
  umlFrame:   UmlFrame      = sdLifeLine.GetCanvas()
  if umlFrame is not None and hasattr(umlFrame, 'umlPubSubEngine') and umlFrame.umlPubSubEngine is not None:
      umlFrame.umlPubSubEngine.sendMessage(...)
  ```

### 5. `UmlSDMessage` & `UmlSDMessageLabelEventHandler`
- **File:** `src/umlshapes/sd/UmlSDMessage.py`
- Remove `umlPubSubEngine: IUmlPubSubEngine` parameter from `UmlSDMessage.__init__`.
- Signature:
  ```python
  def __init__(self, sdMessage: SDMessage, messageType: SDMessageType = SDMessageType.SYNCHRONOUS):
  ```
- Remove `self._umlPubSubEngine` and update `_setMessageLabelEventHandler()`.
- **File:** `src/umlshapes/sd/eventhandlers/UmlSDMessageLabelEventHandler.py`
- Obtain `umlPubSubEngine` dynamically from the message's canvas / `umlFrame` when publishing label edit events.

### 6. Creation Pattern in Commands & Demos
- Follow the standard shape lifecycle used in `CreateUmlClassCommand` and `LinkCreator._displayUmlClass`:
  1. Instantiate the shape cleanly: `umlSDInstance = UmlSDInstance(sdInstance)`.
  2. Late-bind to frame:
     ```python
     umlSDInstance.umlFrame = diagramFrame
     diagramFrame.umlDiagram.AddShape(umlSDInstance)
     ```
- Update `tests/demo/DemoAppFrame.py` where `UmlSDInstance` is created to follow this pattern.

### 7. Tests & Verification in `umlshapes`
- Update all unit tests in `tests/umlshapes/sd/` (e.g. `TestSDCombinedFragment.py`, `TestSDExecution.py`, `TestSDInstanceNameResizing.py`, `TestSDLifeLineResizing.py`, `TestSDLostFoundMessage.py`, `TestSDReflexiveMessage.py`) to instantiate `UmlSDInstance` and `UmlSDMessage` without `diagramFrame` or `umlPubSubEngine`.
- Verify with `runmypy -d` and `unittests`.

### 8. Downstream Updates in `umlio`
- Update `XmlSDInstancesToUmlSDInstances` and `XmlSDMessagesToUmlSDMessages` in `umlio` to remove `diagramFrame` and `umlPubSubEngine` parameters, achieving a pure deserialization model.
