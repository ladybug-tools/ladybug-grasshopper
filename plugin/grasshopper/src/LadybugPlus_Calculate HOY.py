# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Calculate hour of the year.

-

    Args:
        _month_: Month (1-12).
        _day_: Day (1-31).
        _hour_: Hour (0-23).
        _minute_: Minute (0-59).
    Returns:
        hoy: Hour of the year.
        doy: Day of the year.
        date: Human readable date.
"""

ghenv.Component.Name = "LadybugPlus_Calculate HOY"
ghenv.Component.NickName = 'hoy'
ghenv.Component.Message = 'VER 0.0.04\nDEC_21_2018'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    import ladybug.dt as dt
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

datetime = dt.DateTime(_month_, _day_, _hour_, _minute_)
hoy = datetime.hoy
doy = datetime.doy
date = datetime
