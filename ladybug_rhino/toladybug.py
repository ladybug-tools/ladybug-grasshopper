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
    import Rhino.Geometry as rg
    import scriptcontext
    tolerance = scriptcontext.doc.ModelAbsoluteTolerance
except ImportError as e:
    raise ImportError(
        "Failed to import Rhino.\n{}".format(e))


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


def to_face3d(brep, meshing_parameters=None):
    """List of Ladybug Face3D objects from a Rhino Brep.

    Args:
        brep: A Rhino Brep that will be converted into a list of Ladybug Face3D.
        meshing_parameters: Optional Rhino Meshing Parameters to describe how
            curved faces should be convereted into planar elements. If None,
            Rhino's Default Meshing Parameters will be used.
    """
    meshing_parameters = meshing_parameters or rg.MeshingParameters.Default
    faces = []
    for b_face in brep.Faces:
        if b_face.IsPlanar(tolerance):
            all_verts = []
            for count in range(b_face.Loops.Count):  # Each loop is a face boundary/hole
                success, loop_pline = \
                    b_face.Loops.Item[count].To3dCurve().TryGetPolyline()
                if not success:  # If we failed to get a polyline, there are curved edges
                    loop_pcrv = b_face.Loops.Item[count].To3dCurve()
                    f_norm = b_face.NormalAt(0, 0)
                    if f_norm.Z < 0:
                        loop_pcrv.Reverse()
                    loop_verts = []
                    for i in range(loop_pcrv.SegmentCount):
                        seg = loop_pcrv.SegmentCurve(i)
                        if seg.Degree == 1:
                            loop_verts.append(to_point3d(seg.PointAtStart))
                        else:
                            # Ensure curve subdivisions align with adjacent curved faces
                            seg_mesh = rg.Mesh.CreateFromSurface(
                                rg.Surface.CreateExtrusion(seg, f_norm),
                                meshing_parameters)
                            for i in range(seg_mesh.Vertices.Count / 2 - 1):
                                loop_verts.append(to_point3d(seg_mesh.Vertices[i]))
                    all_verts.append(loop_verts)
                else:
                    all_verts.append([to_point3d(loop_pline.Item[i])
                                      for i in range(loop_pline.Count - 1)])
            if len(all_verts) == 1:  # No holes in the shape
                faces.append(lb3.face.Face3D.from_vertices(all_verts[0]))
            else:  # There's at least one hole in the shape
                faces.append(
                    lb3.face.Face3D.from_shape_with_holes(all_verts[0], all_verts[1:]))
        else:
            if b_face.OrientationIsReversed:
                b_face.Reverse(0, True)
            meshed_brep = rg.Mesh.CreateFromBrep(b_face.ToBrep(), meshing_parameters)[0]
            for m_face in meshed_brep.Faces:
                if m_face.IsQuad:
                    lb_face = lb3.face.Face3D.from_vertices(
                        tuple(to_point3d(meshed_brep.Vertices[i]) for i in
                              (m_face.A, m_face.B, m_face.C, m_face.D)))
                    if lb_face.validate_planarity(tolerance, False):
                        faces.append(lb_face)
                    else:
                        lb_face_1 = lb3.face.Face3D.from_vertices(
                            tuple(to_point3d(meshed_brep.Vertices[i]) for i in
                                  (m_face.A, m_face.B, m_face.C)))
                        lb_face_2 = lb3.face.Face3D.from_vertices(
                            tuple(to_point3d(meshed_brep.Vertices[i]) for i in
                                  (m_face.C, m_face.D, m_face.A)))
                        faces.extend([lb_face_1, lb_face_2])
                else:
                    lb_face = lb3.face.Face3D.from_vertices(
                        tuple(to_point3d(meshed_brep.Vertices[i]) for i in
                              (m_face.A, m_face.B, m_face.C)))
                    faces.append(lb_face)
    return faces


def to_polyface3d(brep, meshing_parameters=None):
    """A Ladybug Polyface3D object from a Rhino Brep.

    Args:
        brep: A Rhino Brep that will be converted into a list of Ladybug Face3D.
        meshing_parameters: Optional Rhino Meshing Parameters to describe how
            curved faces should be convereted into planar elements. If None,
            Rhino's Default Meshing Parameters will be used.
    """
    lb_faces = to_face3d(brep)
    return lb3.polyface.Polyface3D.from_faces_tolerance(lb_faces, tolerance)


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
