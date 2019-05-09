"""Functions to create ladybug geometries from Rhino geometries."""

try:
    import ladybug_geometry.geometry2d as lb2
    import ladybug_geometry.geometry3d as lb3
except ImportError as e:
    raise ImportError(
        "Failed to import ladybug_geometry.\n{}".format(e))
try:
    import ladybug.color as lbc
except ImportError as e:
    raise ImportError(
        "Failed to import ladybug.\n{}".format(e))
try:
    import scriptcontext
    tolerance = scriptcontext.doc.ModelAbsoluteTolerance
except ImportError as e:
    raise ImportError(
        "Failed to import scriptcontext.\n{}".format(e))


"""____________2D GEOMETRY TRANSLATORS____________"""


def to_vector2d(vector):
    """Ladybug Vector2D from Rhino Vector3d."""
    return lb2.pointvector.Vector2D(vector.X, vector.Y)


def to_point2d(point):
    """Ladybug Point2D from Rhino Point3d."""
    return lb2.pointvector.Point2D(point.X, point.Y)


def to_ray2d(ray):
    """Ladybug Ray2D from Rhino Ray3d."""
    return lb2.ray.Ray2D(to_point2d(ray.Position), to_vector2d(ray.Direction))


def to_linesegment2d(line):
    """Ladybug LineSegment2D from Rhino LineCurve."""
    return lb2.line.LineSegment2D(
        to_point2d(line.PointAtStart), to_point2d(line.PointAtEnd))


def to_polygon2d(polygon):
    """Ladybug Polygon2D from Rhino closed PolyLineCurve."""
    assert polygon.IsClosed, \
        'Rhino PolyLineCurve must be closed to make a Ladybug Polygon2D.'
    return lb2.polygon.Polygon2D(
        [to_point2d(polygon.Point(i)) for i in range(polygon.PointCount - 1)])


def to_mesh2d(mesh, color_by_face=True):
    """Ladybug Mesh2D from Rhino Mesh."""
    lb_verts = tuple(to_point2d(pt) for pt in mesh.Vertices)
    lb_faces, colors = _extract_mesh_faces_colors(mesh, color_by_face)
    return lb2.mesh.Mesh2D(lb_verts, lb_faces, colors)


"""____________3D GEOMETRY TRANSLATORS____________"""


def to_vector3d(vector):
    """Ladybug Vector3D from Rhino Vector3d."""
    return lb3.pointvector.Vector3D(vector.X, vector.Y, vector.Z)


def to_point3d(point):
    """Ladybug Point3D from Rhino Point3d."""
    return lb3.pointvector.Point3D(point.X, point.Y, point.Z)


def to_ray3d(ray):
    """Ladybug Ray3D from Rhino Ray3d."""
    return lb3.ray.Ray3D(to_point3d(ray.Position), to_vector3d(ray.Direction))


def to_linesegment3d(line):
    """Ladybug LineSegment3D from Rhino LineCurve."""
    return lb3.line.LineSegment3D(
        to_point3d(line.PointAtStart), to_point3d(line.PointAtEnd))


def to_plane(pl):
    """Ladybug Plane from Rhino Plane."""
    return lb3.plane.Plane(
        to_vector3d(pl.ZAxis), to_point3d(pl.Origin), to_vector3d(pl.XAxis))


def to_mesh3d(mesh, color_by_face=True):
    """Ladybug Mesh3D from Rhino Mesh."""
    lb_verts = tuple(to_point3d(pt) for pt in mesh.Vertices)
    lb_faces, colors = _extract_mesh_faces_colors(mesh, color_by_face)
    return lb3.mesh.Mesh3D(lb_verts, lb_faces, colors)


def to_face3d(brep):
    """List of Ladybug Face3D objects from a Rhino Brep."""
    curved_error = 'to_face3d has not yet been implemented for curved breps.'
    faces = []
    for b_face in brep.Faces:
        if b_face.IsPlanar(tolerance):
            all_verts = []
            for count in range(b_face.Loops.Count):  # Each loop is a face boundary/hole
                success, loop_pline = \
                    b_face.Loops.Item[count].To3dCurve().TryGetPolyline()
                if not success:  # If we failed to get a polyline, an edge is curved
                    raise NotImplementedError(curved_error)
                all_verts.append([to_point3d(loop_pline.Item[i])
                                  for i in range(loop_pline.Count - 1)])
            if len(all_verts) == 1:  # No holes in the shape
                faces.append(lb3.face.Face3D.from_vertices(all_verts[0]))
            else:  # There's at least one hole in the shape
                faces.append(
                    lb3.face.Face3D.from_shape_with_holes(all_verts[0], all_verts[1:]))
        else:
            raise NotImplementedError(curved_error)
    return faces


def _extract_mesh_faces_colors(mesh, color_by_face):
    colors = None
    lb_faces = []
    for face in mesh.Faces:
        if face.IsQuad:
            lb_faces.append((face[0], face[1], face[2], face[3]))
        else:
            lb_faces.append((face[0], face[1], face[2]))

    if len(mesh.VertexColors) != 0:
        colors = []
        if color_by_face is True:
            for face in mesh.Faces:
                col = mesh.VertexColors[face[0]]
                colors.append(lbc.Color(col.R, col.G, col.B))
        else:
            for col in mesh.VertexColors:
                colors.append(lbc.Color(col.R, col.G, col.B))
    return lb_faces, colors
