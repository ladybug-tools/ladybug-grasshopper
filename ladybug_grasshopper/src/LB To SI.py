# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Convert a DataCollection to SI values.
-

    Args:
        _data_ip: A DataCollection in IP (or other) units.

    Returns:
        data_si: The DataCollection in SI units.
"""

ghenv.Component.Name = "LB To SI"
ghenv.Component.NickName = 'ToSI'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from ladybug.datacollection import BaseCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    assert isinstance(_data_ip, BaseCollection), \
        '_data_ip must be a Data Collection. Got {}.'.format(type(_data_ip))
    data_si = _data_ip.to_si()