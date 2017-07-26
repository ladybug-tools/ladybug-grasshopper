# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to change the colors, numerical range, and/or number of divisions
of any Ladybug legend along with the corresponding colored mesh that the legend refers to.

Any Ladybug component that outputs a colored mesh and a legend will have an input
that can accept Legend Parameters from this component.

This component particularly helpful in making the colors of Ladybug graphics consistent
for a presentation or for synchonizing the numerical range and colors between Ladybug graphics.
-


    Args:
        _domain_: A number representing the higher boundary of the legend's numerical range. The default is set to the highest value of the data stream that the legend refers to.
        _cType_:
        _colors_: A list of colors that will be used to re-color the legend and the corresponding colored mesh(es).  The number of colors input here should match the numSegments_ value input above.  An easy way to generate a list of colors to input here is with the Grasshopper "Gradient" component and a Grasshopper "Series" component connected to the Gradient component's "t" input.  A bunch of Grasshopper "Swatch" components is another way to generate a list of custom colors.  The default colors are a gradient spectrum from blue to yellow to red.
    Returns:
        legendPar: A legend parameters to be plugged into any of the Ladybug components with a legend.
"""

ghenv.Component.Name = "LadybugPlus_Legend Parameters"
ghenv.Component.NickName = 'legendPar'
ghenv.Component.Message = 'VER 0.0.01\nJUL_21_2017'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = "3 :: Extra"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    import ladybug.legendparameters as lpar
    import ladybug.color as col
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

# TODO: Add color convertor to [+]
if _colors_:
    pass
    # colors = tuple(col.ColorConvertor.toLBColor(_colors_))

legendPar = lpar.LegendParameters(
    legendRange=_domain_, numberOfSegments=11,
    colors=_colors_, chartType=_cType_
)