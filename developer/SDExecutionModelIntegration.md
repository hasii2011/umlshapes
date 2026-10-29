# SDExecution Domain Model Integration in `umlshapes`

## Overview

With the release of **`umlmodel 4.0.0`**, the domain layer now provides formal model support for sequence diagram execution specifications via `SDExecution`:

```python
from umlmodel.SDExecution import SDExecution
from umlmodel.SDInstance import SDInstance
from umlmodel.SDMessage import SDMessage
```

Currently, in `umlshapes`, `UmlSDExecution` functions purely as a presentation-layer visual rectangle on a lifeline (`lifeLine`, `startY`, `endY`, `nestingLevel`) without an associated domain model instance. This document outlines the implementation plan to bind `UmlSDExecution` directly to `SDExecution`.

---

## 1. Prerequisites & Dependencies

Update `pyproject.toml` in `umlshapes`:
* Bump dependency to `umlmodel >= 4.0.0` to pull in `SDExecution` and the keyword-only base class `UmlModelBase`.

---

## 2. Model Association in `UmlSDExecution`

### Constructor & Property
In `src/umlshapes/sd/UmlSDExecution.py`:
1. Add `sdExecution: Optional[SDExecution] = None` to `UmlSDExecution.__init__`:
   - If `sdExecution` is provided:
     - Initialize `startY` and `endY` from `sdExecution.startTime` and `sdExecution.endTime`.
     - Initialize `nestingLevel` from `sdExecution.nestingLevel`.
   - If `sdExecution` is omitted (e.g., interactive creation on canvas):
     - Instantiate a new `SDExecution` bound to `lifeLine.sdInstance`:
       ```python
       self._sdExecution = SDExecution(
           instance=lifeLine.sdInstance,
           startTime=self._startY,
           endTime=self._endY,
           nestingLevel=self._nestingLevel,
       )
       ```
2. Provide a getter and setter property:
   ```python
   @property
   def sdExecution(self) -> SDExecution:
       return self._sdExecution

   @sdExecution.setter
   def sdExecution(self, sdExecution: SDExecution):
       self._sdExecution = sdExecution
       self._startY = sdExecution.startTime
       self._endY = sdExecution.endTime
       self._nestingLevel = sdExecution.nestingLevel
       self.recomputeGeometry()
   ```

---

## 3. Geometry & Event Handler Synchronization

In `src/umlshapes/sd/eventhandlers/UmlSDExecutionEventHandler.py`:
* **Dragging & Resizing:**
  When control points or the shape move along the time axis:
  - Update `self._sdExecution.startTime = self._startY`
  - Update `self._sdExecution.endTime = self._endY`
  - Update `self._sdExecution.nestingLevel = self._nestingLevel`

---

## 4. Message Linkage (Start & Finish Messages)

In `SDMessageCreationHandler.py` and `UmlSDMessage.py`:
* When a synchronous or asynchronous message connects to an execution occurrence:
  - If it is the initiating / trigger message, associate `sdExecution.startMessage = umlSDMessage.sdMessage`.
  - If it is the return / reply message, associate `sdExecution.finishMessage = umlSDMessage.sdMessage`.
* Support optional operation binding (`sdExecution.operation`) when an execution represents an explicit method invocation.

---

## 5. Downstream `umlio` Serialization Alignment

Linking `UmlSDExecution` to `SDExecution` prepares for the XML schema update in `umlio`:
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
This mirrors how `<UmlSDInstance>` wraps `<ModelSDInstance>` and `<UmlSDMessage>` wraps `<ModelSDMessage>`.
