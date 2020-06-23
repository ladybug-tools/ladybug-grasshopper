# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
#
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a plot of hourly wind data by wind directions.
-

    Args:
        north_: A number between -360 and 360 for the counterclockwise
            difference between the North and the positive Y-axis in degrees.
            90 is West and 270 is East. This can also be Vector for the
            direction to North. (Default: 0)
        _wind_speed_data: A HourlyContinuousCollection or HourlyDiscontinuousCollection of wind
            values, corresponding to the wind directions, which is "binned" by the
            calculated direction intervals.
        _wind_direction_data: A HourlyContinuousCollection or
            HourlyDiscontinuousCollection of wind directions which will be used to "bin"
            the intervals for the windrose.
        _number_of_directions_: Number that determines the number of directions to the
            wind rose will display. The number of directions must be greater then three
            to plot the wind rose. (Default: 16).
        _center_pt_: Point3D to be used as a starting point to generate the geometry of
            the plot (Default: (0, 0, 0)).
        _show_calmrose_: A boolean to indicate if the wind rose displays a calm rose. The
            calm rose is a radial plot in the center of the wind rose with a radius
            corresponding to the total zero values divided by the number of directions.
            This allows the wind rose to represent zero values from _wind_speed_data
            even though such values don't have any direction associated with them.
        _show_frequency_: A boolean to show the frequency of _wind_speed_data values
            in the wind direction bins. The frequency lines represent constant intervals
            in time while the color illustrates the average _wind_speed_data values
            associated with each interval. The number of frequency lines with similar
            colors therefore indicate a higher frequency of that value.
        _frequency_distance_: The distance for the frequency interval in model units
            (Default: 10). If _show_calmrose is set to True, then the initial frequency
            interval corresponds to the number of calm hours in the data collection,
            which may not align with this _frequency_spacing.
       _frequency_hours_: The number of hours represented in each frequency interval
            (Default: 200).
        _max_frequency_:A number representing the maximum hours that the outermost ring
            of the wind rose. By default, this value is set by the wind direction with
            the largest number of hours (the highest frequency) but you may want to change
            this if you have several wind roses that you want to compare to each other.
            For example, if you have wind roses for different months or seasons, which each
            have different maximum frequencies. Note that the percentage of wind hours does
            not assumes non-zero hours unless the _show_calmrose option is selected.
        _legend_par_: A LegendParameter object to change the display of the WindRose
            plot. The number of segments in the legend determines the number of
            frequency intervals in the wind rose. If nothing is provided, a default
            LegendParameter object is computed using values from the wind data with
            11 segments (Default: None).
        period_: A Ladybug analysis period to be applied to all of the input _data.

    Returns:
        report: ...
        wind_histogram_data: A Grasshopper data tree with the number of branches equal to the
            number of directions. Each branch lists the _wind_speed_values_ specific to that
            direction.
        mesh: A colored mesh representing the wind rose derived from the input data.
        compass: A set of circles, lines and text objects that mark the cardinal
            directions in relation to the wind rose.
        orientation_lines: Line geometries representing the edges (or "spokes") of the wind rose
            directions.
        frequency_lines: Polygon geometries representing the frequency intervals of the wind rose.
        legend: Geometry representing the legend for the wind rose.
        title: A text object for the global_title.
"""
ghenv.Component.Name = "LB Wind Rose Plot"
ghenv.Component.NickName = 'WindRose'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '2 :: VisualizeWeatherData'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import math

try:
    from ladybug.windrose import WindRose
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_geometry.geometry2d.pointvector import Point2D, Vector2D
    from ladybug_geometry.geometry3d.pointvector import Point3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_point3d, to_vector2d
    from ladybug_rhino.fromgeometry import from_mesh2d, from_linesegment2d, \
        from_polygon2d
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.fromobjects import legend_objects, compass_objects
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def title_text(data_col):
    """Get a text string for the title of the windrose."""
    title_array = ['{} ({})'.format(data_col.header.data_type,
                                    data_col.header.unit)]
    for key, val in data_col.header.metadata.items():
        title_array.append('{}: {}'.format(key, val))
    return '\n'.join(title_array)


if all_required_inputs(ghenv.Component):

    # Check for errors in input
    if _number_of_directions_ is None:
        _number_of_directions_ = 16

    assert _number_of_directions_ > 2, 'The number of directions must be greater then ' \
        'three to plot the wind rose. Got: {}'.format(_number_of_directions_)

    # Apply any analysis periods to the input collections
    if period_ is not None:
        _wind_speed_data = _wind_speed_data.filter_by_analysis_period(period_)
        _wind_direction_data = _wind_direction_data.filter_by_analysis_period(period_)

    # Make the windrose
    windrose = WindRose(_wind_direction_data, _wind_speed_data, _number_of_directions_)

    # Add and check optional visualization parameters
    windrose.show_freq = _show_frequency_
    windrose.show_zeros = _show_calmrose_
    _center_pt_ = Point3D() if _center_pt_ is None else to_point3d(_center_pt_)
    windrose.base_point = Point2D(_center_pt_.x, _center_pt_.y)

    if north_ is not None:  # process the north_
        try:
            north_ = math.degrees(to_vector2d(north_).angle_clockwise(Vector2D(0, 1)))
        except AttributeError:  # north angle instead of vector
            assert -360.0 <= north_ <= 360.0, 'The north orientation must be greater ' \
                'then -360 and less then 360 to plot the wind rose. ' \
                'Got: {}'.format(north_)
            north_ = float(north_)
        windrose.north = north_

    if _max_frequency_ is not None:
        windrose.frequency_maximum = _max_frequency_

    if _frequency_hours_ is not None:
        windrose.frequency_hours = _frequency_hours_

    if _frequency_distance_ is not None:
        windrose.frequency_spacing_distance = _frequency_distance_

    if _legend_par_ is not None:
        windrose.legend_parameters = _legend_par_

    # Make the mesh
    mesh = from_mesh2d(windrose.colored_mesh, _center_pt_.z)

    # Make the data outputs
    wind_histogram_data = list_to_data_tree(
        [sorted(bin) for bin in windrose.histogram_data])

    # Make the graphic outputs
    legend = legend_objects(windrose.legend)
    title = text_objects(title_text(_wind_speed_data),
                         windrose.container.lower_title_location,
                         windrose.legend_parameters.text_height,
                         windrose.legend_parameters.font)
    compass = compass_objects(windrose.compass, _center_pt_.z, None)
    orientation_lines = [from_linesegment2d(seg, _center_pt_.z)
                         for seg in windrose.orientation_lines]
    if _show_frequency_:
        frequency_lines = [from_polygon2d(poly) for poly in windrose.frequency_lines]