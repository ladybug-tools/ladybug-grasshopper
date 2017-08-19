# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to access a library of typical gradients useful throughout Ladybug. 
The output from this component should be plugged into the colors_ input of the
"Legend Parameters" component.

For an image of each of the gardients in the library, check here:
https://github.com/mostaphaRoudsari/ladybug/blob/master/resources/gradients.jpg
-

    Args:
        _index: An index refering to one of the following possible gradients:
            0 - Orignal Ladybug
            1 - Nuanced Ladybug
            2 - Multi-colored Ladybug
            3 - View Analysis 1
            4 - View Analysis 2 (Red,Green,Blue)
            5 - Sunlight Hours
            6 - Ecotect
            7 - Thermal Comfort Percentage
            8 - Thermal Comfort Colors
            9 - Thermal Comfort Colors (UTCI)
            10 - Hot Hours
            11 - Cold Hours
            12 - Shade Benefit/Harm
            13 - Thermal Comfort Colors v2 (UTCI)
            14 - Shade Harm
            15 - Shade Benefit
            16 - Black to White
            17 - CFD Colors 1
            18 - CFD Colors 2
            19 - Energy Balance
            20 - THERM
            21 - Cloud Cover
            22 - Glare Potential
            23 - Radiation Benefit
    Returns:
        colors: A series of colors to be plugged into the "Ladybug_Legend Parameters" component.
"""

ghenv.Component.Name = "LadybugPlus_Color Range"
ghenv.Component.NickName = 'colRange'
ghenv.Component.Message = 'VER 0.0.01\nAUG_18_2017'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = "03 :: Extra"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    import ladybug.color as col
    import ladybug.output as output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

_index = _index or 0
cs = col.Colorset()
colors = output.colorTocolor(cs[_index])
