# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Use this component to access a library of typical gradients useful throughout Ladybug. 
The output from this component should be plugged into the colors_ input of the
"Legend Parameters" component.
-
For an image of each of the gardients in the library, check here:
https://github.com/ladybug-tools/lbt-grasshopper/blob/master/gradients.png
-

    Args:
        _index_: An index refering to one of the following possible gradients:
            0 - Original Ladybug
            1 - Nuanced Ladybug
            2 - Multi-colored Ladybug
            3 - Ecotect
            4 - View Study
            5 - Shadow Study
            6 - Glare Study
            7 - Annual Comfort
            8 - Thermal Comfort
            9 - Peak Load Balance
            10 - Heat Sensation
            11 - Cold Sensation
            12 - Benefit/Harm
            13 - Harm
            14 - Benefit
            15 - Shade Benefit/Harm
            16 - Shade Harm
            17 - Shade Benefit
            18 - Energy Balance
            19 - Energy Balance w/ Storage
            20 - THERM
            21 - Cloud Cover
            22 - Black to White
            23 - Blue, Green, Red
            24 - Multicolored 2
            25 - Multicolored 3
            26 - OpenStudio Palette

    Returns:
        colors: A series of colors to be plugged into the "LB Legend Parameters"
            component.
"""

ghenv.Component.Name = 'LB Color Range'
ghenv.Component.NickName = 'ColRange'
ghenv.Component.Message = '1.4.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug.color import Colorset
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.color import color_to_color
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


_index_ = _index_ or 0
cs = Colorset()
colors = [color_to_color(col) for col in cs[_index_]]
