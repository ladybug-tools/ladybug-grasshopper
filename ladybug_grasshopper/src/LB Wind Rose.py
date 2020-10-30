# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
#
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a plot of any hourly data by wind directions.
-

    Args:
        north_: An optional number between -360 and 360 for the counterclockwise
            difference between the North and the positive Y-axis in degrees. 90 is West
            and 270 is East. This can also be Vector for the direction to North
            (Default: 0).
        _data: A HourlyContinuousCollection or HourlyDiscontinuousCollection of
            values corresponding to the wind directions, which is "binned" by
            the direction intervals. This input usually consists of wind speed
            values, but is not limited to this data type. It can also be a list
            of data collections in which case multiple wind roses will be output.
        _wind_direction: A HourlyContinuousCollection or HourlyDiscontinuousCollection
            of wind directions which will be used to "bin" the _data items for the
            windrose.
        _dir_count_: Number that determines the number of directions to the wind rose
            will display. The number of directions must be greater then three to plot
            the wind rose (Default: 16).
        _center_pt_: Point3D to be used as a starting point to generate the geometry of
            the plot (Default: (0, 0, 0)).
        _show_calmrose_: A boolean to indicate if the wind rose displays a calm rose. The
            calm rose is a radial plot in the center of the wind rose with a radius
            corresponding to the total zero values divided by the number of
            directions. This allows the wind rose to represent zero values
            from _data even though such values don't have any direction
            associated with them. (Default: False).
        _show_freq_: A boolean to show the frequency of _data data values in the
            wind direction bins. The frequency lines represent constant intervals
            in time while the color illustrates the average _data data values
            associated with each interval. The number of frequency lines with
            similar colors therefore indicate a higher frequency of that
            value. (Default: True)
        _freq_dist_: The distance for the frequency interval in model units. If 
            _show_calmrose is True, then the initial frequency interval corresponds
            to the number of calm hours in the data collection, which may not
            align with this _freq_dist (Default: 5 meters)
       _freq_hours_: The number of hours in each frequency interval (Default: 50).
        _max_freq_lines_: A number representing the maximum frequency intervals in
            the rose, which determines the maximum amount of hours represented by the
            outermost ring of the windrose. Specifically, this number multiplied by the
            _freq_hours_ parameter will equal the maximum hours in that outermost
            ring. By default, this value is determined by the wind direction with the
            largest number of hours (the highest frequency) but you may want to change
            this if you have several wind roses that you want to compare to each other.
            For example, if you have wind roses for different months or seasons, which
            each have different maximum frequencies.
        legend_par_: An optional LegendParameter object to change the display of the
            WindRose plot. The number of segments in the legend determines the number of
            frequency intervals in the wind rose. If nothing is provided, a default
            LegendParameter object is computed using values from the wind data with
            11 segments (Default: None).
        statement_: A conditional statement as a string (e.g. a > 25) for
            the _data and _wind_direction inputs.
            .
            The variable of the first collection input to _data should always
            be named 'a' (without quotations), the variable of the second list
            should be named 'b', and so on. The wind direction is always the
            last variable, though most statements won't have a need for it.
            .
            For example, if three data collections are connected to _data
            and the following statement is applied:
            '18 < a < 26 and b < 80 and c > 2'
            The resulting collections will only include values where the first
            data collection is between 18 and 26, the second collection is less
            than 80 and the third collection is greater than 2.
        period_: An optional Ladybug analysis period to be applied to all of
            the input data.

    Returns:
        report: ...
        mesh: A colored mesh representing the wind rose derived from the input data.
            Multiple meshes will be output for several data collections are input.
        compass: A set of circles, lines and text objects that mark the cardinal
            directions in relation to the wind rose.
        orient_line: Line geometries representing the edges (or "spokes") of the wind
            rose directions.
        freq_line: Polygon geometries representing the frequency intervals of the wind
            rose.
        windrose_line: Polygon geometries representing the windrose outlines.
        legend: Geometry representing the legend for the wind rose.
        title: A text object for the global_title.
        prevailing: The predominant direction of the outpt wind rose in clockwise
            degrees from north. 0 is North, 90 is East, 180 is South, 270 is West.
        freq_by_dir: A list of frequency _data values (bound by max_freq_lines_) for each wind 
            direction as number of hours. This does not include calm hours since they 
            do not have any direction associated with their values. This hourly count can be 
            divided by the total wind hours to calculating frequency as a percentage.
        avg_by_dir: A list of average _data values (bound by max_freq_lines_) with one value 
            for each wind direction. This does not include calm hours since they do not have 
            any direction associated with their values. 
        calm_hours: The number of hours with calm wind speeds. Only returns a value if the input 
            _data is wind speed. 
        data: The input _data after it has gone through any of the statement or
            period operations input to this component.
"""

ghenv.Component.Name = 'LB Wind Rose'
ghenv.Component.NickName = 'WindRose'
ghenv.Component.Message = '1.0.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '2 :: Visualize Data'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import math

try:
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.windrose import WindRose
    from ladybug.datatype.speed import Speed
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_geometry.geometry2d.pointvector import Point2D, Vector2D
    from ladybug_geometry.geometry3d.pointvector import Point3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.togeometry import to_point3d, to_vector2d
    from ladybug_rhino.fromgeometry import from_mesh2d, from_linesegment2d, \
        from_polygon2d
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.fromobjects import legend_objects, compass_objects
    from ladybug_rhino.grasshopper import \
        all_required_inputs, list_to_data_tree, data_tree_to_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def title_text(data_col):
    """Get a text string for the title of the windrose."""
    title_array = ['{} ({})'.format(data_col.header.data_type,
                                    data_col.header.unit)]
    for key, val in data_col.header.metadata.items():
        title_array.append('{}: {}'.format(key, val))
    title_array.append('period: {}'.format(data_col.header.analysis_period))
    return '\n'.join(title_array)


if all_required_inputs(ghenv.Component):
    # Apply any analysis periods and conditional statement to the input collections
    if period_ is not None:
        _data = [dat.filter_by_analysis_period(period_) for dat in _data]
        _wind_direction = _wind_direction.filter_by_analysis_period(period_)

    if statement_ is not None and statement_.strip() != "":
        _fdata = HourlyContinuousCollection.filter_collections_by_statement(
            _data + [_wind_direction], statement_)
        _data = _fdata[:-1]
        _wind_direction = _fdata[-1]

    # set defaults and check errors in dir_count and north input
    if _dir_count_ is None:
        _dir_count_ = 16
    assert _dir_count_ > 2, 'The number of directions must be greater then three to ' \
        'plot the wind rose. Got: {}'.format(_dir_count_)

    if north_ is not None:  # process the north_
        try:
            north_ = math.degrees(to_vector2d(north_).angle_clockwise(Vector2D(0, 1)))
        except AttributeError:  # north angle instead of vector
            north_ = float(north_)
            assert -360.0 <= north_ <= 360.0, 'The north orientation must be greater ' \
                'then -360 and less then 360 to plot the wind rose. ' \
                'Got: {}'.format(north_)
    else:
        north_ = 0.0

    # set default values for the chart dimensions
    _center_pt_ = to_point3d(_center_pt_) if _center_pt_ is not None else Point3D()
    center_pt_2d = Point2D(_center_pt_.x, _center_pt_.y)

    # set defaults frequency hours and distance so chart is same scale as other LB plots
    if _freq_hours_ is None:
        _freq_hours_ = 50.0
    if _freq_dist_ is None:
        _freq_dist_ = 5.0 / conversion_to_meters()

    # set default show_freq and _show_calmrose_
    _show_calmrose_ = False if _show_calmrose_ is None else _show_calmrose_
    _show_freq_ = True if _show_freq_ is None else _show_freq_

    # set up empty lists of objects to be filled
    all_wind_avg_val = []
    all_wind_frequency = []
    all_windrose_lines = []
    all_mesh = []
    all_compass = []
    all_orient_line = []
    all_freq_line = []
    all_legends = []
    all_title = []
    all_calm_hours = []

    # Calculate _max_freq_lines_ if it's not already set, to use to
    # determine spacing for multiple plots.
    if len(_data) > 1 and _max_freq_lines_ is None:
        max_freqs = []
        for i, _data_item in enumerate(_data):
            win_dir = _wind_direction
            w = WindRose(win_dir, _data_item, _dir_count_)
            if _freq_hours_ is not None:
                w.frequency_hours = _freq_hours_
            if _freq_dist_ is not None:
                w.frequency_spacing_distance = _freq_dist_
            max_freqs.append(w.frequency_intervals_compass)
        _max_freq_lines_ = max(max_freqs)
    
    # Plot the windroses
    for i, speed_data in enumerate(_data):

        # Make the windrose
        win_dir = _wind_direction
        windrose = WindRose(win_dir, speed_data, _dir_count_)

        if len(legend_par_) > 0:
            try:  # sense when several legend parameters are connected
                lpar = legend_par_[i]
            except IndexError:
                lpar = legend_par_[-1]
            windrose.legend_parameters = lpar

        if _freq_hours_ is not None:
            windrose.frequency_hours = _freq_hours_

        # Add and check optional visualization parameters
        if _max_freq_lines_ is not None:
            windrose.frequency_intervals_compass = _max_freq_lines_

        if _freq_dist_ is not None:
            windrose.frequency_spacing_distance = _freq_dist_

        windrose.north = north_
        windrose.show_freq = _show_freq_
        
        calm_text = ''
        if isinstance(speed_data.header.data_type, Speed):
            windrose.show_zeros = _show_calmrose_
            calm_text = '\nCalm for {}% of the time = {} hours.'.format(
                round(windrose._zero_count / 
                len(windrose.analysis_values) * 100.0, 2),
                windrose._zero_count)
        windrose.base_point = Point2D(center_pt_2d.x, center_pt_2d.y)
        
        # Make the mesh
        mesh = from_mesh2d(windrose.colored_mesh, _center_pt_.z)
        
        # Make the graphic outputs
        legend = legend_objects(windrose.legend)
        freq_per = windrose._frequency_hours / \
            len([b for a in windrose.histogram_data for b in a])
        freq_text = '\nEach closed polyline shows frequency of {}% = {} hours.'.format(
                round(freq_per * 100, 1), windrose._frequency_hours)
        title = text_objects(title_text(speed_data) + calm_text + freq_text,
                             windrose.container.lower_title_location,
                             windrose.legend_parameters.text_height,
                             windrose.legend_parameters.font)
        compass = compass_objects(windrose.compass, _center_pt_.z, None)
        orient_line = [from_linesegment2d(seg, _center_pt_.z)
                            for seg in windrose.orientation_lines]
        freq_line = [from_polygon2d(poly) for poly in windrose.frequency_lines]
        windrose_lines = [from_polygon2d(poly) for poly in windrose.windrose_lines]
        fac = (i + 1) * windrose.compass_radius * 3
        center_pt_2d = Point2D(_center_pt_.x + fac, _center_pt_.y)
        
        all_mesh.append(mesh)
        all_compass.append(compass)
        all_orient_line.append(orient_line)
        all_freq_line.append(freq_line)
        all_windrose_lines.append(windrose_lines)
        all_legends.append(legend)
        all_title.append(title)
        calm = windrose.zero_count if isinstance(speed_data.header.data_type, Speed) else None
        all_calm_hours.append(calm)
        
        # compute the average values
        wind_avg_val = []
        for bin in windrose.histogram_data:
            try:
                wind_avg_val.append(sum(bin) / len(bin))
            except ZeroDivisionError:
                wind_avg_val.append(0)
        all_wind_avg_val.append(wind_avg_val)
        all_wind_frequency.append([len(bin) for bin in windrose.histogram_data])
        
    # convert nested lists into data trees
    mesh = list_to_data_tree(all_mesh)
    compass = list_to_data_tree(all_compass)
    orient_line = list_to_data_tree(all_orient_line)
    freq_line = list_to_data_tree(all_freq_line)
    windrose_line = list_to_data_tree(all_windrose_lines)
    legend = list_to_data_tree(all_legends)
    title = list_to_data_tree(all_title)
    avg_by_dir = list_to_data_tree(all_wind_avg_val)
    freq_by_dir = list_to_data_tree(all_wind_frequency)
    calm_hours = list_to_data_tree(all_calm_hours)
    
    # output prevailing direction and processed data
    prevailing = windrose.prevailing_direction
    data = _data