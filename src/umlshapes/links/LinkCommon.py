
from typing import TYPE_CHECKING

from wx import Point as wxPoint

if TYPE_CHECKING:
    from umlshapes.links.UmlLink import UmlLink

from umlshapes.links.UmlAssociationLabel import UmlAssociationLabel

from umlshapes.types.ClosestPoint import ClosestPoint
from umlshapes.types.ClosestPoint import FromPoint
from umlshapes.types.ClosestPoint import LinePoint
from umlshapes.types.ClosestPoint import determineClosestPoint

from umlshapes.types.UmlPosition import UmlPosition


def getClosestPointOnLine(umlLink: 'UmlLink', umlAssociationLabel: UmlAssociationLabel):
    """
    The line may have multiple segments.  Test each segment

    Args:
        umlLink:
        umlAssociationLabel:

    Returns:  The closest point on a given line segment

    """
    controlPoints = umlLink.GetLineControlPoints()
    if len(controlPoints) > 2:
        pass
    else:
        wxPoint1: wxPoint = controlPoints[0]
        startPoint: LinePoint = LinePoint(
            x=wxPoint1.x,
            y=wxPoint1.y
        )
        wxPoint2: wxPoint = controlPoints[1]
        endPoint: LinePoint = LinePoint(
            x=wxPoint2.x,
            y=wxPoint2.y
        )
        topLeft: UmlPosition = umlAssociationLabel.position

        fromPoint: FromPoint = FromPoint(
            x=topLeft.x,
            y=topLeft.y
        )
        closestPoint: ClosestPoint = determineClosestPoint(
            startPoint=startPoint,
            endPoint=endPoint,
            fromPoint=fromPoint
        )

        return closestPoint
