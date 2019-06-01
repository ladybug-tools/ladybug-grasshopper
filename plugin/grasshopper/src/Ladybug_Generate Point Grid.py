# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
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

ghenv.Component.Name = "Ladybug_Generate Point Grid"
ghenv.Component.NickName = 'genPts'
ghenv.Component.Message = 'VER 0.0.04\nMAY_31_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = "03 :: Extra"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    from ladybug_rhino.togeometry import to_gridded_mesh3d
    from ladybug_rhino.fromgeometry import from_mesh3d
    from ladybug_rhino.fromgeometry import from_point3d, from_vector3d
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

import Rhino.Geometry as rg


if _geometry and _grid_size is not None:
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