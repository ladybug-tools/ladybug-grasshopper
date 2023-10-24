# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Visualize a wind profile curve for a given terrain type.
_
Wind profiles assist with understanding how wind speed decreases as one approaches
the ground or increases as one leaves the ground. 
_
By default, the wind profile output by this component will be an average over the
_met_wind_vel data collection (or it can be for a single meteorological wind
velocity for point-in-time studies).
_
If a met_wind_dir_ data collection is connected, the wind profile will point in
the direction of prevailing wind direction by default. A profile_dir_ can then
be connected to understand the average wind profile from a specific cardinal
direction (eg. NE).
-

    Args:
        north_: A number between -360 and 360 for the counterclockwise
            difference between the North and the positive Y-axis in degrees.
            90 is West and 270 is East. This can also be Vector for the
            direction to North. (Default: 0)
        _met_wind_vel: A data collection of meteorological wind speed measured at
            the _met_height_ with the _met_terrian [m/s]. Typically, this comes
            from the "LB Import EPW" component. This can also be a single number
            for the meteorological wind speed in m/s.
        met_wind_dir_: An optional number between 0 and 360 representing the degrees
            from north that the meteorological wind is blowing. 0 = North,
            90 = East, 180 = South, 270 = West. This can also a data collection
            of meteorological wind directions. in which case the wind profile
            will be oriented towards the prevailing wind (unless a profile_dir_
            is connected). When unspecified, the wind profile is simply drawn
            in the XY plane.
        profile_dir_: An optional text string representing the cardinal direction that
            the wind profile represents. This input only has an effect when a
            data collection is connected for met_wind_dir_. It will be used
            to draw a wind profile for only the hours of the data collection
            where the wind is blowing in the specified direction. This can also
            be an integer that codes for a particular orientation. Choose from
            the following.
            _
            0 = N
            1 = NE
            2 = E
            3 = SE
            4 = S
            5 = SW
            6 = W
            7 = NW
        _terrain_: Text string that sets the terrain class associated with the wind profile.
            This can also be an integer that codes for the terrain. (Default: city).
            Must be one the following.
            _
            0 = city - 50% of buildings above 21m over a distance of at least 2000m upwind.
            1 = suburban - suburbs, wooded areas.
            2 = country - open, with scattered objects generally less than 10m high.
            3 = water - flat areas downwind of a large water body (max 500m inland).
        _met_height_: A number for the height above the ground at which the meteorological
            wind speed is measured in meters. (Default: 10 meters, which is the
            standard used by most airports and EPW files).
        _met_terrain_: Text string that sets the terrain class associated with the
            meteorological wind speed. This can also be an integer that codes
            for the terrain. (Default: country, which is typical of most
            airports where wind measurements are taken). Must be one the following.
            _
            0 = city - 50% of buildings above 21m over a distance of at least 2000m upwind.
            1 = suburban - suburbs, wooded areas.
            2 = country - open, with scattered objects generally less than 10m high.
            3 = water - flat areas downwind of a large water body (max 500m inland).
        log_law_: A boolean to note whether the wind profile should use a logarithmic
            law to determine wind speeds instead of the default power law,
            which is used by EnergyPlus. (Default: False).
        _base_pt_: A point that sets the ground level frm which the wind profile is
            drawn. By default, the profile is generated at the scene origin.
        _profile_height_: A number in meters to specify the maximum height of the
            wind profile. (Default: 30 meters).
        _vec_spacing_: A number in meters to specify the difference in height between
            each of the mesh arrows. (Default 2 meters).
        _vec_scale_: A number to denote the length dimension of a 1 m/s wind vector
            in meters. This can be used to change the scale of the wind
            vector meshes in relation to the height of the wind profile
            curve. (Default: 5 meters).
        legend_par_: An optional LegendParameter object to change the display of the
            wind profile.

    Returns:
        report: Reports, errors, warnings, etc.
        wind_speeds: A list of wind speeds in [m/s] that correspond to the wind
            vectors slong the height of the wind profile visualization.
        wind_vectors: A list of vectors that built the profile. Note that the
            magnitude of these vectors is scaled based on the _vec_scale_
            input and a _vec_scale_ of 1 will make the magnitude of the
            vector equal to the wind speed in [m/s].
        anchor_pts: A list of anchor points for each of the vectors above, which
            correspond to the height above the ground for each of the vectors.
        mesh_arrows: A list of colored mesh objects that represent the wind speeds
            along the height of the wind profile.
        profile_curve: A curve outlining the wind speed as it changes with height.
        speed_axis: A list of line segments and text objects that mark the X axis,
            which relates to the wind speed in (m/s).
        height_axis: A list of line segments and text objects that mark the Y axis,
            which relates to the the height above the ground in Rhino model units.
        legend: A legend for the colored mesh_arrows, which notes their speed.
        title: A text object for the global_title.
        vis_set: An object containing VisualizationSet arguments for drawing a detailed
            version of the Wind Profile in the Rhino scene. This can be connected to
            the "LB Preview Visualization Set" component to display this version
            of the Wind Profile in Rhino.
"""

ghenv.Component.Name = 'LB Wind Profile'
ghenv.Component.NickName = 'WindProfile'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '2 :: Visualize Data'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

import math

try:
    from ladybug_geometry.geometry2d import Vector2D
    from ladybug_geometry.geometry3d import Point3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug.datatype.speed import WindSpeed
    from ladybug.datacollection import BaseCollection
    from ladybug.graphic import GraphicContainer
    from ladybug.windprofile import WindProfile
    from ladybug.windrose import WindRose
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_point3d, to_vector2d
    from ladybug_rhino.fromgeometry import from_point3d, from_vector3d, \
        from_mesh3d, from_linesegment3d, from_polyline3d
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.grasshopper import all_required_inputs, objectify_output
    from ladybug_rhino.config import conversion_to_meters, units_system
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# dictionary to map integers to terrain types
TERRAIN_TYPES = {
    '0': 'city',
    '1': 'suburban',
    '2': 'country',
    '3': 'water',
    'city': 'city',
    'suburban': 'suburban',
    'country': 'country',
    'water': 'water'
}

# dictionary to map integers to cardinal directions
DIR_TEXT = {
    '0': 'N', '1': 'NE', '2': 'E', '3': 'SE', '4': 'S', '5': 'SW', '6': 'W', '7': 'NW',
    'N': 'N', 'NE': 'NE', 'E': 'E', 'SE': 'SE', 'S': 'S', 'SW': 'SW', 'W': 'W', 'NW': 'NW'
}
DIR_RANGE = {
    'N': (337.5, 22.5), 'NE': (22.5, 67.5), 'E': (67.5, 112.5), 'SE': (112.5, 157.5),
    'S': (157.5, 202.5), 'SW': (202.5, 247.5), 'W': (247.5, 292.5), 'NW': (292.5, 337.5)
}


if all_required_inputs(ghenv.Component):
    # interpret the model units
    scale_fac = 1 / conversion_to_meters()
    unit_sys = units_system()

    # set default values
    if north_ is not None:  # process the north_
        try:
            north_ = math.degrees(
                to_vector2d(north_).angle_clockwise(Vector2D(0, 1)))
        except AttributeError:  # north angle instead of vector
            north_ = float(north_)
    else:
        north_ = 0
    _terrain_ = 'city' if _terrain_ is None else TERRAIN_TYPES[_terrain_.lower()]
    _met_height_ = 10 if _met_height_ is None else _met_height_
    _met_terrain_ = 'country' if _met_terrain_ is None \
        else TERRAIN_TYPES[_met_terrain_.lower()]
    log_law_ = False if log_law_ is None else log_law_
    bp = Point3D(0, 0, 0) if _base_pt_ is None else to_point3d(_base_pt_)
    if unit_sys in ('Feet', 'Inches'):
        _profile_height_ = 30.48 if _profile_height_ is None else _profile_height_
        _vec_spacing_ = 3.048 if _vec_spacing_ is None else _vec_spacing_
        feet_labels = True
    else:
        _profile_height_ = 30 if _profile_height_ is None else _profile_height_
        _vec_spacing_ = 2 if _vec_spacing_ is None else _vec_spacing_
        feet_labels = False
    _vec_scale_ = 5 if _vec_scale_ is None else _vec_scale_
    len_d, height_d = _vec_scale_, _vec_scale_ / 5

    # process the data collections and wind direction if reuqested
    if isinstance(met_wind_dir_, BaseCollection):
        if profile_dir_ is not None:
            dir_label = DIR_TEXT[profile_dir_]
            dir_txt = '\nWind Direction = {}'.format(dir_label)
        else:  # get the prevailing wind direction
            prev_dir = WindRose.prevailing_direction_from_data(met_wind_dir_, 8)[0]
            dir_label = DIR_TEXT[str(int(prev_dir / 45))]
            dir_txt = '\nPrevailing Wind Direction = {}'.format(dir_label)
        dir_range = DIR_RANGE[dir_label]
        met_wd = sum(dir_range) / 2 if dir_range != (337.5, 22.5) else 0
        if isinstance(_met_wind_vel, BaseCollection):
            lw, hg = dir_range
            if dir_range == (337.5, 22.5):
                pattern = [lw < v or v < hg for v in met_wind_dir_]
            else:
                pattern = [lw < v < hg for v in met_wind_dir_]
            _met_wind_vel = _met_wind_vel.filter_by_pattern(pattern)
    else:
        met_wd = float(met_wind_dir_) if met_wind_dir_ is not None else None
        dir_txt = '\nWind Direction = {} degrees'.format(int(met_wd)) \
            if met_wind_dir_ is not None else ''
    if isinstance(_met_wind_vel, BaseCollection):
        met_ws = _met_wind_vel.average
        head = _met_wind_vel.header
        loc_txt = '{} Terrain'.format(_terrain_.title()) if 'city' not in head.metadata \
            else '{} - {} Terrain'.format(head.metadata['city'], _terrain_.title())
        title_txt = '{}{}\nAverage Met Wind Speed = {} m/s'.format(
            loc_txt, dir_txt, round(met_ws, 2))
    else:
        met_ws = float(_met_wind_vel)
        title_txt = '{} Terrain{}\nMeteorological Speed = {} m/s'.format(
            _terrain_.title(), dir_txt, round(met_ws, 2))
    if met_wd is not None and north_ != 0:
        met_wd = met_wd - north_

    # create the wind profile and the graphic container
    profile = WindProfile(_terrain_, _met_terrain_, _met_height_, log_law_)
    _, mesh_ars, wind_speeds, wind_vectors, anchor_pts = \
        profile.mesh_arrow_profile(
            met_ws, _profile_height_, _vec_spacing_, met_wd, bp,
            len_d, height_d, scale_fac)
    profile_polyline, _, _ = profile.profile_polyline3d(
            met_ws, _profile_height_, 0.1,
            met_wd, bp, len_d, scale_fac)
    max_speed = round(wind_speeds[-1]) if _max_speed_ is None else _max_speed_
    max_pt = Point3D(bp.x + ((max_speed + 2) * len_d * scale_fac),
                     bp.y + (30 * scale_fac), bp.z)
    graphic = GraphicContainer(
        wind_speeds, bp, max_pt, legend_par_, WindSpeed(), 'm/s')

    # draw profile geometry and mesh arrows in the scene
    mesh_arrows = []
    for mesh, col in zip(mesh_ars, graphic.value_colors):
        mesh.colors = [col] * len(mesh)
        mesh_arrows.append(from_mesh3d(mesh))
    profile_curve = from_polyline3d(profile_polyline)

    # draw axes and legend in the scene
    txt_h = graphic.legend_parameters.text_height
    axis_line, axis_arrow, axis_ticks, text_planes, text = \
        profile.speed_axis(max_speed, met_wd, bp, len_d, scale_fac, txt_h)
    speed_axis = [from_linesegment3d(axis_line), from_mesh3d(axis_arrow)]
    for tic in axis_ticks:
        speed_axis.append(from_linesegment3d(tic))
    for i, (pl, txt) in enumerate(zip(text_planes, text)):
        txt_i_h = txt_h if i != len(text) - 1 else txt_h * 1.25
        txt_obj = text_objects(txt, pl, txt_i_h, graphic.legend_parameters.font, 1, 0)
        speed_axis.append(txt_obj)
    axis_line, axis_arrow, axis_ticks, text_planes, text = \
        profile.height_axis(_profile_height_, _vec_spacing_ * 2, met_wd, bp,
                            scale_fac, txt_h, feet_labels)
    height_axis = [from_linesegment3d(axis_line), from_mesh3d(axis_arrow)]
    for tic in axis_ticks:
        height_axis.append(from_linesegment3d(tic))
    for i, (pl, txt) in enumerate(zip(text_planes, text)):
        if i != len(text) - 1:
            txt_i_h, ha, va = txt_h, 2, 3
        else:
            txt_i_h, ha, va = txt_h * 1.25, 1, 5
        txt_obj = text_objects(txt, pl, txt_i_h, graphic.legend_parameters.font, ha, va)
        height_axis.append(txt_obj)
    
    # draw the legend and the title
    if graphic.legend_parameters.is_base_plane_default:
        graphic.legend_parameters.base_plane = \
            profile.legend_plane(max_speed, met_wd, bp, len_d, scale_fac)
    legend = legend_objects(graphic.legend)
    title_pl = profile.title_plane(met_wd, bp, len_d, scale_fac, txt_h)
    title = text_objects(title_txt, title_pl, txt_h, graphic.legend_parameters.font, 0, 0)

    # process the output lists of data
    anchor_pts = [from_point3d(pt) for pt in anchor_pts]
    wind_vectors = [from_vector3d(vec) for vec in wind_vectors]
    wind_speeds.insert(0, 0)  # insert 0 wind speed for bottom of curve

    # create the output VisualizationSet arguments
    vis_set = [profile, met_ws, met_wd, legend_par_, bp, _profile_height_,
               _vec_spacing_, len_d, height_d, max_speed, scale_fac, feet_labels]
    vis_set = objectify_output('VisualizationSet Aruments [WindProfile]', vis_set)
