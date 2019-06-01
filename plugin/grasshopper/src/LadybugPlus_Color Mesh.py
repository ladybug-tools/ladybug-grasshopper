# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to generate colors based on values and legend parameters.
-
    Args:
        _values: A list of numerical values with which to color the mesh.
            The number of values must match the number of faces or vertices
            in the mesh.
        _mesh: A Mesh object, with a number of faces or vertices that match
            the number of input values and will be colored with restults.
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

ghenv.Component.Name = "LadybugPlus_Color Mesh"
ghenv.Component.NickName = 'colorMesh'
ghenv.Component.Message = 'VER 0.0.04\nMAY_31_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = "03 :: Extra"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    from ladybug.resultmesh import ResultMesh
    from ladybug_rhino.togeometry import to_mesh3d
    from ladybug_rhino.fromgeometry import from_mesh3d
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.text import text_objects
    from ladybug_dotnet.color import color_to_color
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

if len(_values) != 0 and _values[0] is not None and _mesh:
    # generate Ladybug objects
    res_mesh = ResultMesh(_values, to_mesh3d(_mesh), legend_par_)
    
    # generate titles
    if legend_title_ is not None:
        res_mesh.legend_parameters.title = legend_title_
    if global_title_ is not None:
        title = text_objects(global_title_, res_mesh.lower_title_location,
                             res_mesh.legend_parameters.text_height,
                             res_mesh.legend_parameters.font)
    
    # draw rhino objects
    lb_mesh = res_mesh.colored_mesh
    mesh = from_mesh3d(lb_mesh)
    legend = legend_objects(res_mesh.legend)
    colors = [color_to_color(col) for col in lb_mesh.colors]
    legend_par = res_mesh.legend_parameters
