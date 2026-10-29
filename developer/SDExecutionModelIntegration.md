# SDExecution Domain Model Integration in `umlshapes`

## Overview

With the release of **`umlmodel 4.0.0`**, the domain layer provides formal model support for sequence diagram execution specifications via `SDExecution`:

```python
from umlmodel.SDExecution import SDExecution
from umlmodel.SDInstance import SDInstance
from umlmodel.SDMessage import SDMessage
```

In `umlshapes`, `UmlSDExecution` is directly bound to `SDExecution` as its **Single Source of Truth (SSOT)**. This document outlines the completed implementation and downstream integration points.

---

## 1. Prerequisites & Dependencies `[Completed]`

Updated `pyproject.toml` in `umlshapes`:
* Bumped dependency to `umlmodel >= 4.0.0` to pull in `SDExecution` and keyword-only base class `UmlModelBase`.

---

## 2. Model Association in `UmlSDExecution` `[Completed]`

### Single Source of Truth (SSOT) Architecture
Rather than duplicating coordinates in local instance variables (`_startY`, `_endY`, `_nestingLevel`) alongside `_sdExecution`, `UmlSDExecution` maintains `self._sdExecution: SDExecution` as its sole state store.

### Constructor & Property Delegation
In `src/umlshapes/sd/UmlSDExecution.py`:
1. `UmlSDExecution.__init__`:
   - Accepts `lifeLine: UmlSDLifeLine, startY: int = 0, endY: int = 0, nestingLevel: int = 0, sdExecution: Optional[SDExecution] = None`.
   - If `sdExecution` is provided: wraps the domain model directly.
   - If `sdExecution` is omitted (canvas creation): instantiates a new `SDExecution` bound to `lifeLine.sdInstance`.
2. Property Delegations:
   - `startY` delegates to `_sdExecution.startTime` (and enforces minimum time step duration).
   - `endY` delegates to `_sdExecution.endTime`.
   - `nestingLevel` delegates to `_sdExecution.nestingLevel`.
   - `operation` delegates to `_sdExecution.operation`.
   - `startMessage` delegates to `_sdExecution.startMessage`.
   - `finishMessage` delegates to `_sdExecution.finishMessage`.
   - `sdExecution` getter and setter properties allow inspection and complete model swapping.

In `src/umlshapes/sd/UmlSDLifeLine.py`:
* Added `sdInstance` property delegating to `self._umlInstanceName.sdInstance`.

---

## 3. Geometry & Event Handler Synchronization `[Completed]`

In `src/umlshapes/sd/eventhandlers/UmlSDExecutionEventHandler.py` and `UmlSDMessageEventHandler.py`:
* **Dragging & Resizing:**
  When control points or the shape move along the time axis:
  - Interactive top and bottom sizing handle drags update `execution.startY` and `execution.endY`, which directly mutate `sdExecution.startTime` and `sdExecution.endTime`.
  - Message dragging via `_synchronizeAssociatedExecution` updates attached execution coordinates in lockstep.
  - Lifeline nesting recalculation updates `execution.nestingLevel`, mutating `sdExecution.nestingLevel`.

---

## 4. Message Linkage (Start & Finish Messages) `[Completed]`

In `src/umlshapes/sd/UmlSDMessage.py`:
* `UmlSDMessage.execution.setter`:
  - When attaching a call message (`SYNCHRONOUS`, `ASYNCHRONOUS`, `FOUND`):
    - Sets `execution.startMessage = self._sdMessage`.
    - Auto-populates `execution.operation = self._sdMessage.message` if not already set.
  - When attaching a return message (`RETURN`):
    - Sets `execution.finishMessage = self._sdMessage`.

In `src/umlshapes/sd/SDMessageCreationHandler.py`:
* Return messages are guarded against spurious execution creation on destination lifelines.
* Return messages link directly to the originating active execution occurrence (`fromExecution.finishMessage = modelMessage`).

---

## 5. Downstream `umlio` Serialization Alignment `[Ready]`

`UmlSDExecution` exposes all necessary attributes for the XML schema update in `umlio`:
```xml
<UmlSDExecution id="...">
    <ModelSDExecution
        instanceId="..."
        startTime="..."
        endTime="..."
        nestingLevel="..."
        operation="..."
    />
</UmlSDExecution>
```

### Shape Traversal API Contract for `umlio`:
* `umlSDLifeLine.executions -> list[UmlSDExecution]`
* `umlSDExecution.id` -> presentation shape ID
* `umlSDExecution.sdExecution` -> domain model instance:
  - `sdExecution.id` -> unique model ID
  - `sdExecution.instance.id` -> participant instance ID
  - `sdExecution.startTime` -> start time offset
  - `sdExecution.endTime` -> end time offset
  - `sdExecution.nestingLevel` -> nesting level
  - `sdExecution.operation` -> optional operation name
  - `sdExecution.startMessage.id` -> trigger message ID (if present)
  - `sdExecution.finishMessage.id` -> return message ID (if present)
