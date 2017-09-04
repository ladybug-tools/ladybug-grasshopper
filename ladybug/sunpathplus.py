"""Methods for drawing sunpath geometry."""
try:
    import Rhino.Geometry as rg
except ImportError:
    raise ImportError(
        "Failed to import Grasshopper. Make sure the path is added to sys.path.")


def analemma_curves(suns, origin, radius):
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


def base_curves(origin, radius, north_angle):
    origin = rg.Point3d(*origin)
    inner_circle = rg.Circle(origin, radius)
    middle_circle = rg.Circle(origin, 1.02 * radius)
    outter_circle = rg.Circle(origin, 1.08 * radius)

    return inner_circle, middle_circle, outter_circle


def daily_curves(suns, origin, radius):
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


def sun_geometry(suns, origin, radius):
    """Get sun geometries as points."""
    origin = rg.Point3d(*origin)
    return tuple(
        origin.Add(origin,
                   rg.Vector3d(sun.sunVector.x, sun.sunVector.y, sun.sunVector.z) *
                   -radius)
        for sun in suns)
