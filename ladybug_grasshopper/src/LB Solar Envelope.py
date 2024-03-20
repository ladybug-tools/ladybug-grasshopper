# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Generate a solar envelope boundary for a given geometry, set of sun vectors, and
context (obstacle) geometry.
_
Solar collection envelopes show the height above which one will have solar access
to certain sun positions on a given site.
_
Solar rights envelopes illustrate the volume in which one can build while ensuring
that a new development does not shade the surrounding properties for certain sun
positions.
-

    Args:
        _geometry: Rhino Breps and/or Rhino Meshes for which the solar envelope will
            be computed. If Breps are input, they will be subdivided using
            the _grid_size to yeild individual points at which analysis will
            occur. If a Mesh is input, the analysis will be performed for each
            vertex of the mesh instead of subdividing it.
        _obstacles: A list of horizontal planar Breps or curves indicating the tops (in the
            case of solar collection) or bottoms (in the case of solar rights)
            of context geometries. Being above a solar collection boundary
            ensures these top surfaces don't block the sun vectors to ones
            position. Being below a solar rights boundary ensures these bottom
            surfaces are protected from shade.
        _vectors: Sun vectors from the "LB SunPath" component, which determine the
            times of the year when sun should be accessible.
        _grid_size: A positive number in Rhino model units for the size of grid
            cells at which the input _geometry will be subdivided for envelope
            analysis. The smaller the grid size, the higher the resolution of
            the analysis and the longer the calculation will take.  So it is
            recommended that one start with a large value here and decrease
            the value as needed. The default will be a relativel coarse
            auto-calculated from the bounding box around the _geometry.
        _height_limit_: A positive number for the minimum distance below (for collections)
            or maximum distance above (for rights) the average _geometry height
            that the envelope points can be. This is used when there are no
            vectors blocked for a given point. (Default: 100 meters).
        solar_rights_: Set to True to compute a solar rights boundary and False to compute
            a solar collection boundary. Solar rights boundaries represent the
            boundary below which one can build without shading the surrounding
            obstacles from any of the _vectors. Solar collection boundaries
            represent the boundary above which one will have direct solar
            access to all of the input _vectors. (Default: False).
        _run: Set to "True" to run the component and get a solar envelope.

    Returns:
        report: ...
        points: The grid of points above the test _geometry representing the height to
            which the solar envelope boundary reaches.
        mesh: A mesh representing the solar envelope. For solar collections (the default),
            this represents the boundary above which the one will have direct
            solar access to all of the input _vectors. For solar rights envelopes,
            this represents the boundary below which one can build without shading
            the surrounding obstacles from any of the _vectors.
"""

ghenv.Component.Name = 'LB Solar Envelope'
ghenv.Component.NickName = 'SolarEnvelope'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '3 :: Analyze Geometry'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from ladybug.solarenvelope import SolarEnvelope
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.togeometry import to_joined_gridded_mesh3d, to_face3d, \
        to_vector3d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_point3d
    from ladybug_rhino.grasshopper import all_required_inputs, hide_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # set the default offset distance
    _height_limit_ = _height_limit_ if _height_limit_ is not None \
        else 100 / conversion_to_meters()

    # convert geometry, objstacles, and vectors to ladybug_geomtery
    study_mesh = to_joined_gridded_mesh3d(_geometry, _grid_size)
    obstacle_faces = [g for geo in _obstacles for g in to_face3d(geo)]
    sun_vectors = [to_vector3d(vec) for vec in _vectors]

    # compute the solar envelope
    solar_obj = SolarEnvelope(
        study_mesh, obstacle_faces, sun_vectors, _height_limit_, solar_rights_)
    lb_mesh = solar_obj.envelope_mesh()
    mesh = from_mesh3d(lb_mesh)
    points = [from_point3d(pt) for pt in lb_mesh.vertices]
    hide_output(ghenv.Component, 1)
