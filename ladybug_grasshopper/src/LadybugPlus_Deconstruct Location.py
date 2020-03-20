# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Deconstruct location.
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

ghenv.Component.Name = "LadybugPlus_Deconstruct Location"
ghenv.Component.NickName = 'decnstrLoc'
ghenv.Component.Message = 'VER 0.0.04\nJUN_07_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '00 :: Ladybug'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

try:
    import ladybug.location as loc
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

if all_required_inputs(ghenv.Component):
    # in case someone uses the input from an older version of ladybug
    location = loc.Location.from_location(_location)
    name = location.city
    latitude = location.latitude
    longitude = location.longitude
    time_zone = location.time_zone
    elevation = location.elevation