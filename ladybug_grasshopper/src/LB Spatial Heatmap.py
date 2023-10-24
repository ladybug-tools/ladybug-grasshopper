# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Color a mesh as a heatmap using values that align with the mesh faces or vertices.
_
Note that any brep can be converted to a gridded mesh that can be consumed by 
this component using the "LB Generate Point Grid" component.
-

    Args:
        _values: A list of numerical values with which to color the mesh.
            The number of values must match the number of faces or vertices
            in the mesh.
        _mesh: A Mesh object, with a number of faces or vertices that match
            the number of input values and will be colored with results.
        offset_dom_: Optional domain (or number for distance), which will
            be used to offset the mesh faces or verticesto according to the
            values. Higher values will be offset further.
        legend_par_: Optional legend parameters from the Ladybug
            'Legend Parameters' component.
        legend_title_: A text string for Legend title. Typically, the units
            of the data are used here but the type of data might also be used.
            Default is an empty string.
        global_title_: A text string to label the entire mesh.  It will be
            displayed in the lower left of the result mesh. Default is for no
            title.

    Returns:
        mesh: The input _mesh that has been colored with results.
        legend: Geometry representing the legend for the mesh.
        title: A text object for the global_title.
        colors: The colors associated with each input value.
        legend_par: The input legend parameters with defaults filled for
            unset properties.
"""

ghenv.Component.Name = 'LB Spatial Heatmap'
ghenv.Component.NickName = 'Heatmap'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug.legend import LegendParameters
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_display.visualization import VisualizationSet
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_mesh3d
    from ladybug_rhino.fromgeometry import from_mesh3d
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.color import color_to_color
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # translate to Ladybug objects
    lb_mesh = to_mesh3d(_mesh)
    if offset_dom_:
        dom_st, dom_end = offset_dom_
        lb_mesh = lb_mesh.height_field_mesh(_values, (dom_st, dom_end))

    # check the values against the mesh
    assert len(_values) == len(lb_mesh.faces) or len(_values) == len(lb_mesh.vertices), \
        'Expected the number of data set values ({}) to align with the number of faces ' \
        '({}) or the number of vertices ({}).\nConsider flattening the _values input ' \
        'and using the "Mesh Join" component to join the _mesh input.'.format(
            len(_values), len(lb_mesh.faces), len(lb_mesh.vertices))

    # create the VisualizationSet and GraphicContainer
    if legend_title_ is not None:
        legend_par_ = legend_par_.duplicate() if legend_par_ is not None \
            else LegendParameters()
        legend_par_.title = legend_title_
    vis_set = VisualizationSet.from_single_analysis_geo(
        'Data_Mesh', [lb_mesh], _values, legend_par_)
    graphic = vis_set.graphic_container()

    # generate titles
    if global_title_ is not None:
        title = text_objects(global_title_, graphic.lower_title_location,
                             graphic.legend_parameters.text_height * 1.5,
                             graphic.legend_parameters.font)

    # draw rhino objects
    lb_mesh.colors = graphic.value_colors
    mesh = from_mesh3d(lb_mesh)
    legend = legend_objects(graphic.legend)
    colors = [color_to_color(col) for col in lb_mesh.colors]
    legend_par = graphic.legend_parameters
