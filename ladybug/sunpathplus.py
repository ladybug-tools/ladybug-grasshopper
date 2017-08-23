"""Methods for drawing sunpath geometry."""
import Rhino.Geometry as rg


def analemmaCurves(suns, origin, radius):
    """Create analemma curves.

    Args:
        suns: A list of lists of sun positions.
        origin: Sunpath origin.
        radius: Sunpath radius.
    Returns:
        A generator of analemma curves.
    """
    origin = rg.Point3d(*origin)
    for hour in suns:
        try:
            pts = tuple(
                origin.Add(origin,
                           rg.Vector3d(sun.sunVector.x,
                                       sun.sunVector.y, sun.sunVector.z) *
                           -radius)
                for sun in hour)
        except AttributeError:
            # no sun poistion / all night
            continue
        else:
            # create the analemma curve and send it back
            yield rg.Curve.CreateInterpolatedCurve(pts, 3,
                                                   rg.CurveKnotStyle.ChordPeriodic)


def baseCurves(origin, radius, northAngle):
    origin = rg.Point3d(*origin)
    innerCircle = rg.Circle(origin, radius)
    middleCircle = rg.Circle(origin, 1.02 * radius)
    outterCircle = rg.Circle(origin, 1.08 * radius)

    return innerCircle, middleCircle, outterCircle


def dailyCurves(suns, origin, radius):
    """Create daily sunpath curves."""
    origin = rg.Point3d(*origin)
    for day, isArc in suns:
        pts = tuple(
            origin.Add(origin,
                       rg.Vector3d(sun.sunVector.x, sun.sunVector.y, sun.sunVector.z) *
                       -radius)
            for sun in day)
        if isArc:
            yield rg.Arc(*pts)
        else:
            if pts[2].Z > 0:
                yield rg.Circle(*pts)


def sunGeometry(suns, origin, radius):
    """Get sun geometries as points."""
    origin = rg.Point3d(*origin)
    return tuple(
        origin.Add(origin,
                   rg.Vector3d(sun.sunVector.x, sun.sunVector.y, sun.sunVector.z) *
                   -radius)
        for sun in suns)
