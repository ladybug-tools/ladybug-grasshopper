# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Construct location.
-

    Args:
        _name: A name for the location you are constructing. (ie. Steventon Island, Antarctica)
        _latitude: The latitude of the location you are constructing. Values must be between -90 and 90. Default is set to the equator.
        _longitude_: An optional numerical value representing the longitude of the location you are constructing. This can improve the accuracy of the resulting sun plot.
        _timeZone_: An optional integer representing the time zone of the location you are constructing. This can improve the accuracy of the resulting sun plot.  The time zone should follow the epw convention and should be between -12 and +12, where 0 is at Greenwich, UK, positive values are to the East of Greenwich and negative values are to the West.
        _elevation_: An optional numerical value representing the elevation of the location you are constructing.
    Returns:
        location: Location data (use this output to construct the sun path).
"""

ghenv.Component.Name = "LadybugPlus_Construct Location"
ghenv.Component.NickName = 'constrLoc'
ghenv.Component.Message = 'VER 0.0.02\nNOV_16_2017'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '00 :: Ladybug'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    import ladybug.location as loc
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

location = loc.Location(_name_, '-', _latitude_, _longitude_, _timeZone_, _elevation_)