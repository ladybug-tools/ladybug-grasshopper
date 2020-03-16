# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

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

ghenv.Component.Name = "LadybugPlus_Construct Location"
ghenv.Component.NickName = 'constrLoc'
ghenv.Component.Message = 'VER 0.0.04\nMAR_15_2020'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '00 :: Ladybug'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

try:
    import ladybug.location as loc
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

location = loc.Location(_name_, '-', '-', _latitude_, _longitude_, _time_zone_, _elevation_)