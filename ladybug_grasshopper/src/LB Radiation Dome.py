# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Visualize the radiation falling on an object from different directions over a dome.
_
The Radiation Dome depicts the amount of solar energy received by all directions
over a dome. This is useful for understanding the optimal orientation of solar
panels and how the performance of the panel might change if it's orientation
is off from the optimal position. It can also be used to identify the optimal
wall orientation for passive solar heating when used with skies of
radiation harm/benefit. When used with clear sky matrices, it can identify
the orientations that result in the highest and lowest peak cooling load.
_
The Radiation Dome can be understood in different ways:
1) It's a 3D representation of the "LB Radiation Rose," depicting all tilt angles
    for that rose at once.
2) It's the reciprocal of the "LB Sky Dome," since it shows how the radiation from
    that sky falls onto a hemispherical object.
3) It's an radiation study of a hemisphere. The results here are effectively the
    same as running a hemisphere through the "LB Incident Radiation" component.
-

    Args:
        _sky_mtx: A Sky Matrix from the "LB Cumulative Sky Matrix" component or the
            "LB Benefit Sky Matrix" component, which describes the radiation
            coming from the various patches of the sky.
        context_:  Rhino Breps and/or Rhino Meshes representing context geometry
            that can block solar radiation to the center of the radiation dome.
        _az_count_: An integer greater than or equal to 3, which notes the number of
            horizontal orientations to be evaluated on the dome. (Default: 72).
        _alt_count_: An integer greater than or equal to 3, which notes the number of
            vertical orientations to be evaluated on the dome. (Default: 18).
        _center_pt_: A point for the center of the radiation dome. (Default: (0, 0, 0))
        _scale_: A number to set the scale of the Radiation Dome. The default is 1,
            which corresponds to a radius of 100 meters in the current Rhino
            model's unit system.
        projection_: Optional text for the name of a projection to use from the sky
            dome hemisphere to the 2D plane. If None, a 3D sky dome will be drawn
            instead of a 2D one. (Default: None) Choose from the following:
                * Orthographic
                * Stereographic
        irradiance_: Boolean to note whether the radiation dome should be plotted with units
            of cumulative Radiation (kWh/m2) [False] or with units of average
            Irradiance (W/m2) [True]. (Default: False).
        show_comp_: Boolean to indicate whether only one dome with total radiation
            should be displayed (False) or three domes with the solar radiation
            components (total, direct, and diffuse) should be shown. (Default: False).
        legend_par_: An optional LegendParameter object to change the display of the
            radiation dome (Default: None).

    Returns:
        report: ...
        mesh: A colored mesh of a dome, representing the intensity of radiation/irradiance
            from different cardinal directions.
        compass: A set of circles, lines and text objects that mark the cardinal
            directions in relation to the radiation dome.
        legend: A legend showing the kWh/m2 or W/m2 values that correspond to the colors
            of the mesh.
        title: A text object for the title of the radiation dome.
        dir_vecs: A list of vectors for each of the directions the dome is facing.
            All vectors are unit vectors.
        dir_values: Radiation values for each of the dome directions in kWh/m2 or W/m2.
            This will be one list if show_comp_ is "False" and a list of 3
            lists (aka. a Data Tree) for total, direct, diffuse if show_comp_
            is "True".
        max_pt: A point on the radiation dome with the greatest amount of solar
            radiation/irradiance. For a radiation benefit sky, this is the
            orientation with the greatest benefit. This can be used to
            understand the optimalorientation of solar panels or the best
            direction to face for passive solar heating.
        max_info: Information about the direction with the greates amount of radiation.
            This includes the altitude, azimuth, and radiation/irradiance value.
        vis_set: An object containing VisualizationSet arguments for drawing a detailed
            version of the Radiation Dome in the Rhino scene. This can be
            connected to the "LB Preview Visualization Set" component to display
            this version of the Radiation Dome in Rhino.
"""

ghenv.Component.Name = 'LB Radiation Dome'
ghenv.Component.NickName = 'RadiationDome'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '2 :: Visualize Data'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from ladybug_geometry.geometry3d.pointvector import Point3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug.viewsphere import view_sphere
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_radiance.visualize.raddome import RadiationDome
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_radiance:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.togeometry import to_point3d
    from ladybug_rhino.fromgeometry import from_point3d, \
        from_vector3d, from_mesh3d
    from ladybug_rhino.intersect import join_geometry_to_mesh, intersect_mesh_rays
    from ladybug_rhino.fromobjects import legend_objects, compass_objects
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.grasshopper import all_required_inputs, \
        objectify_output, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def translate_dome(lb_mesh, lb_compass, graphic, title_txt):
    """Translate radiation dome geometry into a format suitable for Rhino.

    Args:
        lb_mesh: A ladybug Mesh3D for the dome.
        lb_compass: A ladybug Compass object.
        graphic: A GraphicContainer for the dome.
        title_txt: Text for title of the dome.

    Returns:
        dome_mesh: A Rhino colored mesh for the dome.
        dome_compass: Rhino objects for the dome compass.
        dome_legend:  Rhino objects for the dome legend.
        dome_title: A bake-able title for the dome.
    """
    # translate the dome visualization, including legend and compass
    dome_mesh = from_mesh3d(lb_mesh)
    dome_legend = legend_objects(graphic.legend)
    dome_angles = list(range(0, 360, int(360 / _az_count_)))
    start, stop, step, dome_angles = 0, 360, 360 / _az_count_, []
    while start < stop:
        dome_angles.append(start)
        start += step
    dome_angles = [int(n) for n in dome_angles]
    if len(dome_angles) > 36:
        dome_angles = dome_angles[::2]
    dome_compass = compass_objects(
        lb_compass, z, dome_angles, projection_, graphic.legend_parameters.font)

    # construct a title from the metadata
    dome_title = text_objects(title_txt, graphic.lower_title_location,
                              graphic.legend_parameters.text_height,
                              graphic.legend_parameters.font)

    return dome_mesh, dome_compass, dome_legend, dome_title


if all_required_inputs(ghenv.Component):
    # set defaults for global variables
    _az_count_ = 72 if _az_count_ is None else _az_count_
    _alt_count_ = 18 if _alt_count_ is None else _alt_count_
    _scale_ = 1 if _scale_ is None else _scale_
    radius = (100 * _scale_) / conversion_to_meters()
    if _center_pt_ is not None:  # process the center point
        center_pt3d = to_point3d(_center_pt_)
        z = center_pt3d.z
    else:
        center_pt3d, z = Point3D(), 0

    # compute the intersection matrix if context is specified
    n_vecs = RadiationDome.dome_vectors(_az_count_, _alt_count_)
    dir_vecs = [from_vector3d(vec) for vec in n_vecs]
    int_mtx = None
    if len(context_) != 0 and context_[0] is not None:
        shade_mesh = join_geometry_to_mesh(context_)
        p_vecs = view_sphere.tregenza_sphere_vectors if len(_sky_mtx.data[1]) == 145 \
            else view_sphere.reinhart_sphere_vectors
        patch_dirs = [from_vector3d(vec) for vec in p_vecs]
        int_mtx, angles = intersect_mesh_rays(
            shade_mesh, [from_point3d(center_pt3d)] * len(dir_vecs),
            patch_dirs, dir_vecs)

    # create the RadiationRose object
    rad_dome = RadiationDome(
        _sky_mtx, int_mtx, _az_count_, _alt_count_, legend_par_,
        irradiance_, center_pt3d, radius, projection_)

    # create the dome visualization
    if not show_comp_:  # only create the total dome mesh
        mesh, compass, legend, title = translate_dome(*rad_dome.draw())
        dir_values = rad_dome.total_values
    else:  # create domes for total, direct and diffuse
        # loop through the 3 radiation types and produce a dome
        mesh, compass, legend, title = [], [], [], []
        rad_types = ('total', 'direct', 'diffuse')
        for dome_i in range(3):
            cent_pt = Point3D(center_pt3d.x + radius * 3 * dome_i,
                              center_pt3d.y, center_pt3d.z)
            dome_mesh, dome_compass, dome_legend, dome_title = \
                translate_dome(*rad_dome.draw(rad_types[dome_i], cent_pt))
            mesh.append(dome_mesh)
            compass.extend(dome_compass)
            legend.extend(dome_legend)
            title.append(dome_title)
        dir_values = list_to_data_tree(
            (rad_dome.total_values, rad_dome.direct_values, rad_dome.diffuse_values))

    # output infomration about the maximum direction
    max_pt = from_point3d(rad_dome.max_point)
    max_info = rad_dome.max_info

    # output the visualization set
    vis_set = [rad_dome, show_comp_]
    vis_set = objectify_output('VisualizationSet Aruments [RadiationDome]', vis_set)
