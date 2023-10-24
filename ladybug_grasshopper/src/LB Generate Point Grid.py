# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Genrate a mesh with corresponding test points from a Rhino Brep (or Mesh).
_
The resulting mesh will be in a format that the "LB Spatial Heatmap" component
will accept.
-

    Args:
        _geometry: Brep or Mesh from which to generate the points and grid.
        _grid_size: Number for the size of the test grid.
        _offset_dist_: Number for the distance to move points from the surfaces
            of the input _geometry.  Typically, this should be a small positive
            number to ensure points are not blocked by the mesh. (Default: 0).
        quad_only_: Boolean to note whether meshing should be done using Rhino's
            defaults (False), which fills the entire _geometry to the edges
            with both quad and tringulated faces, or a mesh with only quad
            faces should be generated.
            _
            FOR ADVANCED USERS: This input can also be a vector object that will
            be used to set the orientation of the quad-only grid. Note that,
            if a vector is input here that is not aligned with the plane of
            the input _geometry, an error will be raised.

    Returns:
        points: Test points at the center of each mesh face.
        vectors: Vectors for the normal direction at each of the points.
        face_areas: Area of each mesh face.
        mesh: Analysis mesh that can be passed to the "LB Spatial Heatmap" component.
"""

ghenv.Component.Name = "LB Generate Point Grid"
ghenv.Component.NickName = 'GenPts'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug_geometry.geometry3d.plane import Plane
    from ladybug_geometry.geometry3d.face import Face3D
    from ladybug_geometry.geometry3d.mesh import Mesh3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_gridded_mesh3d, to_mesh3d, \
        to_face3d, to_vector3d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_point3d, from_vector3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check the input and generate the mesh.
    _offset_dist_ = _offset_dist_ or 0
    if quad_only_:  # use Ladybug's built-in meshing methods
        lb_faces = to_face3d(_geometry)
        try:
            x_axis = to_vector3d(quad_only_)
            lb_faces = [Face3D(f.boundary, Plane(f.normal, f[0], x_axis), f.holes)
                        for f in lb_faces]
        except AttributeError:
            pass  # no plane connected; juse use default orientation
        lb_meshes = []
        for geo in lb_faces:
            try:
                lb_meshes.append(geo.mesh_grid(_grid_size, offset=_offset_dist_))
            except AssertionError:  # tiny geometry not compatible with quad faces
                continue
        if len(lb_meshes) == 0:
            lb_mesh = None
        elif len(lb_meshes) == 1:
            lb_mesh = lb_meshes[0]
        elif len(lb_meshes) > 1:
            lb_mesh = Mesh3D.join_meshes(lb_meshes)
    else:  # use Rhino's default meshing
        try:  # assume it's a Rhino Brep
            lb_mesh = to_gridded_mesh3d(_geometry, _grid_size, _offset_dist_)
        except TypeError:  # assume it's a Rhino Mesh
            try:
                lb_mesh = to_mesh3d(_geometry)
            except TypeError:  # unidientified geometry type
                raise TypeError(
                    '_geometry must be a Brep or a Mesh. Got {}.'.format(type(_geometry)))

    # generate the test points, vectors, and areas.
    if lb_mesh is not None:
        points = [from_point3d(pt) for pt in lb_mesh.face_centroids]
        vectors = [from_vector3d(vec) for vec in lb_mesh.face_normals]
        face_areas = lb_mesh.face_areas
        mesh = [from_mesh3d(lb_mesh)]
    else:
        mesh = []