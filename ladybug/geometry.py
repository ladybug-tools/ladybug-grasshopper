"""Geometry primitives."""
import Rhino.Geometry as rg


def point(x, y, z):
    """Point 3d by x, y ,z."""
    return rg.Point3d(x, y, z)


def origin():
    """Origin point."""
    return rg.Point3d.Origin


def arc(startPoint, midPoint, endPoint):
    """Arc by 3 points."""
    spt = rg.Point3d(*startPoint)
    mpt = rg.Point3d(*midPoint)
    ept = rg.Point3d(*endPoint)
    arc = rg.Arc(spt, mpt, ept)
    return arc


def plane(pt, normal):
    """Plane by center (x, y, z) and normal (x, y, z)."""
    rg.Plane(rg.Point3d(*pt), rg.Vector3d(*normal))


def line(startPoint, endPoint):
    """Line by start and end point (x, y, z)."""
    spt = rg.Point3d(*startPoint)
    ept = rg.Point3d(*endPoint)
    ln = rg.LineCurve(spt, ept)
    return ln


def circle(centerPoint, radius):
    """Circle from centerPoint and radius."""
    cenpt = rg.Point3d(*centerPoint)
    cir = rg.Circle(cenpt, radius)
    return cir


def curve(points):
    """Curve from collection of points."""
    pts = tuple(rg.Point3d(*pt) for pt in points)
    crv = rg.NurbsCurve.Create(True, 3, pts)
    return crv


def sphere(centerPoint, radius):
    """Sphere by center point and radius."""
    cenpt = rg.Point3d(*centerPoint)
    sp = rg.Sphere(cenpt, radius)
    return sp


def vector(x, y, z):
    """Vector by x, y, z."""
    return rg.Vector3d(x, y, z)


def trim(geometry, plane, pt):
    """Trim curve by plane."""
    raise NotImplementedError()


def trimCurveByPlane(geometry, plane, pt):
    """Trim curve by plane.

    All the inputs should be Rhino geometry.
    """
    raise NotImplementedError()
