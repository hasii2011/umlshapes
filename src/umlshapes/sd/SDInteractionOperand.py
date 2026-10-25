from dataclasses import dataclass


@dataclass
class SDInteractionOperand:
    """
    Represents an operand compartment within a Combined Fragment (UML 2.5.1 Section 17.6).
    """

    guard:         str = ''
    startTimeStep: int = 0
    endTimeStep:   int = 0
