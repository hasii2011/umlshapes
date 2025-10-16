Dragging Multiple Shapes
========================

## Problem Statement

Each individual shape type currently takes responsibility for dragging itself across the diagram via the `BaseEventHandler`.  

Actually, the base wxPtyhon event handler does the dragging and positioning.  However, it does not provide enough feedback.  The developer does not see the shape dragged.  The user drags the shape and stops.  The *dragged* shape magically appears at the new positions.  The effect is quite disturbing.  

Since each shape *drags* itself, when the user selects multiple shape only the latest selected shape drags.

The current implementation requires interactions betweent the specific shape's event handler and a listener in the `UmlFrame`

## Mini Design

### UmlBaseEventHandler

Since all UML Shapes have their own event handler and subclass from the UmlBaseEventHandler that is the perfect place to implement the appropriate code in the `.OnDragLeft` and `.OnEndDragLeft` handlers.

#### OnDragLeft

When the user starts dragging a specific shape, that shape declares itself the *master* shape mover and saves the reported position as its previous position.  Everytime thereafter it knows that it had a previous position and calculates a delta position and saves a new previous position.  It reports the delta position via the SHAPE_MOVING message.

#### OnEndDragLeft

When the user stops dragging this method essentially initializes the state for the shape back to a known starting position and repudiates itself as the *master* shape.

### UmlFrame

The master shape is issuing *SHAPE_MOVING* messages.  Someone has to be listening for those and respond.  That listener is in the UmlFrame class.  That class knows which shapes are currently selected.  It takes the delta XY positions and applies the deltas to the currently selected shapes.  That causes those shapes to synchronously move with the *master* shape.
