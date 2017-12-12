"""Geometry primitives."""
try:
    import Rhino.Geometry as rg
except ImportError:
    raise ImportError(
        "Failed to import Grasshopper. Make sure the path is added to sys.path.")


def point(x, y, z):
    """Point 3d by x, y ,z."""
    return rg.Point3d(x, y, z)


def origin():
    """Origin point."""
    return rg.Point3d.Origin


def arc(start_point, mid_point, end_point):
    """Arc by 3 points."""
    spt = rg.Point3d(*start_point)
    mpt = rg.Point3d(*mid_point)
    ept = rg.Point3d(*end_point)
    arc = rg.Arc(spt, mpt, ept)
    return arc


def plane(pt, normal):
    """Plane by center (x, y, z) and normal (x, y, z)."""
    rg.Plane(rg.Point3d(*pt), rg.Vector3d(*normal))


def line(start_point, end_point):
    """Line by start and end point (x, y, z)."""
    spt = rg.Point3d(*start_point)
    ept = rg.Point3d(*end_point)
    ln = rg.LineCurve(spt, ept)
    return ln


def circle(center_point, radius):
    """Circle from center_point and radius."""
    cenpt = rg.Point3d(*center_point)
    cir = rg.Circle(cenpt, radius)
    return cir


def curve(points):
    """Curve from collection of points."""
    pts = tuple(rg.Point3d(*pt) for pt in points)
    crv = rg.NurbsCurve.Create(True, 3, pts)
    return crv


def sphere(center_point, radius):
    """Sphere by center point and radius."""
    cenpt = rg.Point3d(*center_point)
    sp = rg.Sphere(cenpt, radius)
    return sp


def vector(x, y, z):
    """Vector by x, y, z."""
    return rg.Vector3d(x, y, z)


def trim(geometry, plane, pt):
    """Trim curve by plane."""
    raise NotImplementedError()


def trim_curve_by_plane(geometry, plane, pt):
    """Trim curve by plane.

    All the inputs should be Rhino geometry.
    """
    raise NotImplementedError()
