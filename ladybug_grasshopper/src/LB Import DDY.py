# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Import data from a standard .ddy file.
-

    Args:
        _ddy_file: A .ddy file path on your system as a string.
        
    Returns:
        location: A Ladybug Location object describing the location data in the DDY file.
        design_days: A list of DesignDay objects representing the design days
            contained within the ddy file.
"""

ghenv.Component.Name = "LB Import DDY"
ghenv.Component.NickName = 'ImportDDY'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '0 :: Import'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from ladybug.ddy import DDY
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    ddy_obj = DDY.from_ddy_file(_ddy_file)
    location = ddy_obj.location
    design_days = ddy_obj.design_days
