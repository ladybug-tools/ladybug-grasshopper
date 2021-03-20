# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a chart in the Rhino scene with data organized by month.
_
Data will display as a bar chart if the input data is monthly or daily. If the
data is hourly or sub-hourly, it will be plotted with lines and/or a colored
mesh that shows the range of the data within specific percentiles.
-

    Args:
        _data: Data collections (eg. HourlyCollection, MonthlyCollection, or
            DailyCollection), which will be used to generate the monthly chart.
        _base_pt_: An optional Point3D to be used as a starting point to generate
            the geometry of the chart (Default: (0, 0, 0)).
        _x_dim_: An optional number to set the X dimension of each month of the
            chart. (Default: 10 meters).
        _y_dim_: An optional number to set the Y dimension of the entire
            chart (Default: 40 meters).
        stack_: Boolean to note whether multiple connected monthly or daily input
            _data with the same units should be stacked on top of each other.
            Otherwise, all bars for monthly/daily data will be placed next to
            each other.  (Default: False).
        percentile_: An optional number between 0 and 50 to be used for the percentile
            difference from the mean that hourly data meshes display at. For example,
            using 34 will generate hourly data meshes with a range of one standard
            deviation from the mean. Note that this input only has significance when
            the input data collections are hourly. (Default: 34)
        global_title_: A text string to label the entire entire chart.  It will be
            displayed in the lower left of the output chart.  The default will
            display the metadata of the input _data.
        y_axis_title_: A text string to label the Y-axis of the chart.  This can
            also be a list of 2 Y-axis titles if there are two different types
            of data connected to _data and there are two axes labels on either
            side of the chart.  The default will display the data type and
            units of the first (and possibly the second) data collection
            connected to _data.
        legend_par_: An optional LegendParameter object to change the display
            of the chart (Default: None).

    Returns:
        report: ...
        data_mesh: A list of colored meshes that represent the different input data.
            These meshes will resemble a bar chart in the case of monthly or
            daily data and will resemble a band between two ranges for hourly
            and sub-hourly data. Multiple lists of meshes will be output for
            several input data streams.
        data_lines: A list of polylines that represent the input data. These will
            represent the average or total at each hour whenever the input data
            is hourly or monthly-per-hour data.
        col_lines: A list of colored polylines that represent the input data. These
            will only be output when the input data are monthly per hour.
        legend: Geometry representing the legend for the chart, noting which
            colors correspond to which input data.
        borders: A list of lines and polylines representing the axes and intervals
            of the chart.
        labels: A list of text objects that label the borders with month name
            and the intervals of the Y-axis.
        y_title: A text oject for the Y-axis title.
        title: A text object for the global_title.
"""

ghenv.Component.Name = 'LB Monthly Chart'
ghenv.Component.NickName = 'MonthlyChart'
ghenv.Component.Message = '1.2.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '2 :: Visualize Data'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug.monthlychart import MonthlyChart
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_geometry.geometry2d.pointvector import Point2D
    from ladybug_geometry.geometry3d.pointvector import Point3D
    from ladybug_geometry.geometry3d.plane import Plane
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters, tolerance
    from ladybug_rhino.color import color_to_color
    from ladybug_rhino.togeometry import to_point2d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_mesh2d, \
        from_polyline2d, from_linesegment2d
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.colorize import ColoredPolyline
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.grasshopper import all_required_inputs, schedule_solution
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set default values for the chart dimensions
    z_val = _base_pt_.Z if _base_pt_ is not None else 0
    z_val_tol = z_val + tolerance
    _base_pt_ = to_point2d(_base_pt_) if _base_pt_ is not None else Point2D()
    _x_dim_ = _x_dim_ if _x_dim_ is not None else 10.0 / conversion_to_meters()
    _y_dim_ = _y_dim_ if _y_dim_ is not None else 40.0 / conversion_to_meters()
    stack_ = stack_ if stack_ is not None else False
    percentile_ = percentile_ if percentile_ is not None else 34.0
    lpar = legend_par_[0] if len(legend_par_) != 0 else None

    # create the monthly chart object and get the main pieces of geometry
    month_chart = MonthlyChart(_data, lpar, _base_pt_, _x_dim_, _y_dim_,
                               stack_, percentile_)
    if len(legend_par_) > 1:
        if legend_par_[1].min is not None:
            month_chart.set_minimum_by_index(legend_par_[1].min, 1)
        if legend_par_[1].max is not None:
            month_chart.set_maximum_by_index(legend_par_[1].max, 1)

    #  get the main pieces of geometry
    d_meshes = month_chart.data_meshes
    if d_meshes is not None:
        data_mesh = [from_mesh2d(msh, z_val_tol) for msh in d_meshes]
    d_lines = month_chart.data_polylines
    if d_lines is not None:
        data_lines = [from_polyline2d(lin, z_val_tol) for lin in d_lines]
    borders = [from_polyline2d(month_chart.chart_border, z_val)] + \
            [from_linesegment2d(line, z_val) for line in month_chart.y_axis_lines] + \
            [from_linesegment2d(line, z_val_tol) for line in month_chart.month_lines]
    legend = legend_objects(month_chart.legend)

    # process all of the text-related outputs
    title_txt = month_chart.title_text if global_title_ is None else global_title_
    txt_hgt = month_chart.legend_parameters.text_height
    font = month_chart.legend_parameters.font
    title = text_objects(title_txt, month_chart.lower_title_location, txt_hgt, font)

    # process the first y axis
    y1_txt = month_chart.y_axis_title_text1 if len(y_axis_title_) == 0 else y_axis_title_[0]
    y_title = text_objects(y1_txt, month_chart.y_axis_title_location1, txt_hgt, font)
    label1 = [text_objects(txt, Plane(o=Point3D(pt.x, pt.y, z_val)), txt_hgt, font, 1, 0)
              for txt, pt in zip(month_chart.month_labels, month_chart.month_label_points)]
    label2 = [text_objects(txt, Plane(o=Point3D(pt.x, pt.y, z_val)), txt_hgt, font, 2, 3)
              for txt, pt in zip(month_chart.y_axis_labels1, month_chart.y_axis_label_points1)]
    labels = label1 + label2

    # process the second y axis if it exists
    if month_chart.y_axis_title_text2 is not None:
        y2_txt = month_chart.y_axis_title_text2 if len(y_axis_title_) <= 1 else y_axis_title_[1]
        y_title2 = text_objects(y2_txt, month_chart.y_axis_title_location2, txt_hgt, font)
        y_title = [y_title, y_title2]
        label3 = [text_objects(txt, Plane(o=Point3D(pt.x, pt.y, z_val)), txt_hgt, font, 0, 3)
                 for txt, pt in zip(month_chart.y_axis_labels2, month_chart.y_axis_label_points2)]
        labels = labels + label3

    # if there are colored lines, then process them to be output from the component
    if month_chart.time_interval == 'MonthlyPerHour':
        cols = [color_to_color(col) for col in month_chart.colors]
        col_lines, month_count = [], len(data_lines) / len(_data)
        for i, pline in enumerate(data_lines):
            col_line = ColoredPolyline(pline)
            col_line.color = cols[int(i / month_count)]
            col_line.thickness = 3
            col_lines.append(col_line)
        # CWM: I don't know why we have to re-schedule the solution but this is the
        # only way I found to get the colored polylines to appear (redraw did not work).
        schedule_solution(ghenv.Component, 2)
