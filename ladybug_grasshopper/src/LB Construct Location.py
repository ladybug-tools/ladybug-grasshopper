# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Construct location from latitude, lognitude, and time zone data.
-

    Args:
        _name_: A name for the location you are constructing. For example,
            "Steventon Island, Antarctica". (Default: "-")
        _latitude_: Location latitude between -90 and 90 (Default: 0).
        _longitude_: Location longitude between -180 (west) and 180 (east) (Default: 0).
        _time_zone_: Time zone between -12 hours (west) and 12 hours (east). If None,
            the time zone will be an estimated integer value derived from the
            longitude in accordance with solar time (Default: None).
        _elevation_: A number for elevation of the location in meters. (Default: 0).
    
    Returns:
        location: Location data (use this output to construct the sun path).
"""

ghenv.Component.Name = 'LB Construct Location'
ghenv.Component.NickName = 'ConstrLoc'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '0 :: Import'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from ladybug.location import Location
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

location = Location(_name_, '-', '-', _latitude_, _longitude_, _time_zone_, _elevation_)
