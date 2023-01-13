# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Deconstruct location into its component properties.
-

    Args:
        _location: The output from the importEPW or constructLocation component.
    
    Returns:
        locationName: Name of the location.
        latitude: Latitude of the location.
        longitude: Longitude of the location.
        time_zone: Time zone of the location.
        elevation: Elevation of the location.
"""

ghenv.Component.Name = 'LB Deconstruct Location'
ghenv.Component.NickName = 'DecnstrLoc'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '0 :: Import'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from ladybug.location import Location
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # in case someone uses the input from an older version of ladybug
    location = Location.from_location(_location)
    name = location.city
    latitude = location.latitude
    longitude = location.longitude
    time_zone = location.time_zone
    elevation = location.elevation