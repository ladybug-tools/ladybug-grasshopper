# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a colored plot of any hourly data collection.
-

    Args:
        _data: A HourlyContinuousCollection or HourlyDiscontinuousCollection
            which will be used to generate the hourly plot.
        _base_pt_: An optional Point3D to be used as a starting point to generate
            the geometry of the plot (Default: (0, 0, 0)).
        _x_dim_: A number to set the X dimension of the mesh cells (Default: 1 meters).
        _y_dim_: A number to set the Y dimension of the mesh cells (Default: 4 meters).
        _z_dim_: A number to set the Z dimension of the entire chart. This will
            be used to make the colored_mesh3d of the chart vary in the Z
            dimension according to the data. The value input here should usually be
            several times larger than the x_dim or y_dim in order to be noticable
            (e.g. 100). If 0, the colored_mesh3d will simply be flat. (Default: 0).
        reverse_y_: Boolean to note whether the Y-axis of the chart is reversed
            If True, time over the course of the day will flow from the top of
            the chart to the bottom instead of the bottom to the top.
        legend_par_: An optional LegendParameter object to change the display of the
            HourlyPlot. This can also be a list of legend parameters to be
            applied to the different connected _data.
        statement_: A conditional statement as a string (e.g. a > 25).
            .
            The variable of the first data collection should always be named 'a'
            (without quotations), the variable of the second list should be
            named 'b', and so on.
            .
            For example, if three data collections are connected to _data
            and the following statement is applied:
            '18 < a < 26 and b < 80 and c > 2'
            The resulting collections will only include values where the first
            data collection is between 18 and 26, the second collection is less
            than 80 and the third collection is greater than 2.
        period_: A Ladybug analysis period to be applied to all of the input _data.
    
    Returns:
        report: ...
        mesh: A colored mesh derived from the input _data. Multiple meshes will
            be output for several data collections are input.
        legend: Geometry representing the legend for each mesh.
        borders: A list of lines and polylines representing different time
            intervals of the plot.
        labels: A list of text objects that label the borders with the time
            intervals that they demarcate.
        title: A text object for the global_title.
"""

ghenv.Component.Name = "LB Hourly Plot"
ghenv.Component.NickName = 'HourlyPlot'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '2 :: Visualize Data'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.hourlyplot import HourlyPlot
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_geometry.geometry3d.pointvector import Point3D
    from ladybug_geometry.geometry3d.plane import Plane
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.togeometry import to_point3d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_mesh2d, \
        from_polyline2d, from_linesegment2d
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # apply any analysis periods and conditional statements to the input collections
    if period_ is not None:
        _data = [coll.filter_by_analysis_period(period_) for coll in _data]
    if statement_ is not None:
        _data = HourlyContinuousCollection.filter_collections_by_statement(
            _data, statement_)

    # set default values for the chart dimensions
    _base_pt_ = to_point3d(_base_pt_) if _base_pt_ is not None else Point3D()
    _x_dim_ = _x_dim_ if _x_dim_ is not None else 1.0 / conversion_to_meters()
    _y_dim_ = _y_dim_ if _y_dim_ is not None else 4.0 / conversion_to_meters()
    _z_dim_ = _z_dim_ if _z_dim_ is not None else 0
    reverse_y_ = reverse_y_ if reverse_y_ is not None else False

    # empty lists of objects to be filled with visuals
    mesh, title, all_legends, all_borders, all_labels = [], [], [], [], []

    for i, data_coll in enumerate(_data):
        try:  # sense when several legend parameters are connected
            lpar = legend_par_[i]
        except IndexError:
            lpar = None if len(legend_par_) == 0 else legend_par_[-1]

        # create the hourly plot object and get the main pieces of geometry
        hour_plot = HourlyPlot(data_coll, lpar, _base_pt_,
                               _x_dim_, _y_dim_, _z_dim_, reverse_y_)
        msh = from_mesh2d(hour_plot.colored_mesh2d, _base_pt_.z) if _z_dim_ == 0 else \
            from_mesh3d(hour_plot.colored_mesh3d)
        mesh.append(msh)
        border = [from_polyline2d(hour_plot.chart_border2d, _base_pt_.z)] + \
            [from_linesegment2d(line, _base_pt_.z) for line in hour_plot.hour_lines2d] + \
            [from_linesegment2d(line, _base_pt_.z) for line in hour_plot.month_lines2d]
        all_borders.append(border)
        legnd = legend_objects(hour_plot.legend)
        all_legends.append(legnd)
        tit_txt = text_objects(hour_plot.title_text, hour_plot.lower_title_location,
                               hour_plot.legend_parameters.text_height,
                               hour_plot.legend_parameters.font)
        title.append(tit_txt)

        # create the text label objects
        label1 = [text_objects(txt, Plane(o=Point3D(pt.x, pt.y, _base_pt_.z)),
                               hour_plot.legend_parameters.text_height,
                               hour_plot.legend_parameters.font, 2, 3)
                  for txt, pt in zip(hour_plot.hour_labels, hour_plot.hour_label_points2d)]
        label2 = [text_objects(txt, Plane(o=Point3D(pt.x, pt.y, _base_pt_.z)),
                               hour_plot.legend_parameters.text_height,
                               hour_plot.legend_parameters.font, 1, 0)
                  for txt, pt in zip(hour_plot.month_labels, hour_plot.month_label_points2d)]
        all_labels.append(label1 + label2)
        
        # increment the base point so that the next chart doesn't overlap this one
        try:
            next_tstep = _data[i + 1].header.analysis_period.timestep
        except IndexError:
            next_tstep = 1
        increment = 24 * next_tstep * _y_dim_ * 1.5
        _base_pt_ = Point3D(_base_pt_.x, _base_pt_.y - increment, _base_pt_.z)

    # convert nexted lists into data trees
    legend = list_to_data_tree(all_legends)
    borders = list_to_data_tree(all_borders)
    labels = list_to_data_tree(all_labels)
