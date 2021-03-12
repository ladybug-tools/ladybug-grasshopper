# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Create a custom legend for any set of data or range. Creating a legend with this
component allows for a bit more flexibility than what can be achieved by working
with the legends automatically output from different studies.
-

    Args:
        _values: A list of numerical values or data collections that the legend refers
            to. This can also be the minimum and maximum numerical values of the
            data. The legend's maximum and minimum values will be set by the max
            and min of the data set.
        _base_plane_: An optional plane or point to set the location of the
            legend. (Default: Rhino origin - (0, 0, 0))
        title_: A text string representing a legend title. Legends are usually
            titled with the units of the data.
        legend_par_: Optional legend parameters from the  Legend Parameters component.

    Returns:
        mesh: A colored mesh for the legend colors.
        title_obj: A text object for the  legend title.
        label_objs: An array of text objects for the label text.
        label_text: An array of text strings for the label text.
        colors: An array of colors that align with the input _values. This can
            be used to color geometry that aligns with the values.
"""

ghenv.Component.Name = "LB Create Legend"
ghenv.Component.NickName = 'CreateLegend'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug.datacollection import BaseCollection
    from ladybug.legend import Legend, LegendParameters
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_plane
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.color import color_to_color
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set default values
    legend_par_ = legend_par_.duplicate() if legend_par_ is not None else \
        LegendParameters()
    if _base_plane_:
        legend_par_.base_plane = to_plane(_base_plane_)
    legend_par_.title = title_

    # create the legend
    values = []
    for val in _values:
        try:
            values.append(float(val))
        except AttributeError:  # assume it's a data collection
            values.extend(val.values)
    legend = Legend(values, legend_par_)

    # separate all of the outputs from this component
    rhino_objs = legend_objects(legend)
    mesh = rhino_objs[0]
    title_obj = rhino_objs[1]
    label_objs = rhino_objs[2:]
    label_text = legend.segment_text
    colors = [color_to_color(col) for col in legend.value_colors]
