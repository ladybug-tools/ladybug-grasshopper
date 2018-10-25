# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Import location from an epw
-

    Args:
        _epw_file: An epw file path on your system as a string.
        
    Returns:
        location: Location data (use this output to construct the sun path).
"""

ghenv.Component.Name = "LadybugPlus_Import Location"
ghenv.Component.NickName = 'importLoc'
ghenv.Component.Message = 'VER 0.0.04\nFEB_07_2018'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '00 :: Ladybug'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    import ladybug.epw as epw
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

if _epw_file:
    ep = epw.EPW(_epw_file)
    location = ep.location