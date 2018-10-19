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
        _values: A numerical data set.
        legend_par_: Optional legend parameters from the Ladybug Legend Parameters component.
    Returns:
        colors: The colors associated with each input value.
"""

ghenv.Component.Name = "LadybugPlus_Generate Colors"
ghenv.Component.NickName = 'genColors'
ghenv.Component.Message = 'VER 0.0.04\nOCT_14_2018'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = "03 :: Extra"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    import ladybug.legendparameters as lpar
    import ladybug.output as output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

if _values:
    legend_par = legend_par_ or lpar.LegendParameters()
    colors = output.color_to_color(legend_par.calculate_colors(_values))
