# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Genrate a mesh with corresponding test points.
The resulting mesh will be in a format that the 'Color Mesh' component will accept.
-

    Args:
        _geometry: Brep or Mesh from which to generate the points and grid.
        _grid_size: Number for the size of the test grid.
        _dist_surface_: Number for the distance to move points from the surfaces
            of the input _geometry.  Typically, this should be a small positive
            number to ensure points are not blocked by the mesh. Default is 0.
    
    Returns:
        points: Test points at the center of each mesh face.
        vectors: Vectors for the normal direction at each of the points.
        face_areas: Area of each mesh face.
        mesh: Analysis mesh that can be passed to the 'Color Mesh' component.
"""

ghenv.Component.Name = "LB Generate Point Grid"
ghenv.Component.NickName = 'GenPts'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug_rhino.togeometry import to_gridded_mesh3d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_point3d, from_vector3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import Rhino.Geometry as rg


if all_required_inputs(ghenv.Component):
    # check the input and generate the mesh.
    _dist_surface_ = _dist_surface_ or 0
    if type(_geometry) == rg.Brep:
        lb_mesh = to_gridded_mesh3d(_geometry, _grid_size, _dist_surface_)
    elif type(_geometry) == rg.Mesh:
        lb_mesh = to_mesh3d(_geometry)
    else:
        raise TypeError(
            '_geometry must be a Brep or a Mesh. Got {}.'.format(type(_geometry)))
    
    # generate the test points, vectors, and areas.
    points = [from_point3d(pt) for pt in lb_mesh.face_centroids]
    vectors = [from_vector3d(vec) for vec in lb_mesh.face_normals]
    face_areas = lb_mesh.face_areas
    mesh = from_mesh3d(lb_mesh)