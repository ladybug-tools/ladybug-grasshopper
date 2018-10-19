# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Import data from a standard .stat file.

-

    Args:
        _stat_file: A .stat file path on your system as a string.
        
    Returns:
        location: A Ladybug Location object describing the location data in the STAT file.
        ashrae_climate_zone: The ASHRAE climate zone of the STAT file.
            Numbers in the zone denote average temperature (0 = Hottest; 8 = Coldest)
            Letters in the zone denote wetness (A = Humid; B = Dry; C = Marine)
        koppen_climate_zone: The Koppen climate zone of the STAT file.
            The Koppen climate classification is the most widely used climate
            classification system and combines average annual and monthly
            temperatures, precipitation, and the seasonality of precipitation.
        ----------------: ...
        ann_heating_dday_996: A DesignDay object representing the annual 99.6% heating design day.
        ann_heating_dday_990: A DesignDay object representing the annual 99.0% heating design day.
        ann_cooling_dday_004: A DesignDay object representing the annual 0.4% cooling design day.
        ann_cooling_dday_010: A DesignDay object representing the annual 1.0% cooling design day.
        monthly_ddays_050: A list of 12 DesignDay objects representing monthly 5.0% cooling design days.
        monthly_ddays_100: A list of 12 DesignDay objects representing monthly 10.0% cooling design days.
        ----------------: ...
        extreme_cold_week: A Ladybug AnalysisPeriod object representing the
            coldest week within the corresponding EPW.
        extreme_hot_week: A Ladybug AnalysisPeriod object representing the
            hottest week within the corresponding EPW.
        seasonal_weeks: A list of 4 Ladybug AnalysisPeriod objects representing
            typical weeks for each of the 4 seasons within the corresponding EPW.
            Weeks are ordered as follows: Spring, Summer, Autumn, Winter
"""

ghenv.Component.Name = "LadybugPlus_Import STAT"
ghenv.Component.NickName = 'importSTAT'
ghenv.Component.Message = 'VER 0.0.04\nOCT_14_2018'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '00 :: Ladybug'
ghenv.Component.AdditionalHelpFromDocStrings = "4"


try:
    from ladybug.stat import STAT
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

if _stat_file:
    stat_obj = STAT(_stat_file)
    location = stat_obj.location
    ashrae_climate_zone = stat_obj.ashrae_climate_zone
    koppen_climate_zone = stat_obj.koppen_climate_zone
    ann_heating_dday_996 = stat_obj.annual_heating_design_day_996
    ann_heating_dday_990 = stat_obj.annual_heating_design_day_990
    ann_cooling_dday_004 = stat_obj.annual_cooling_design_day_004
    ann_cooling_dday_010 = stat_obj.annual_cooling_design_day_010
    monthly_ddays_050 = stat_obj.monthly_cooling_design_days_050
    monthly_ddays_100 = stat_obj.monthly_cooling_design_days_100
    extreme_cold_week = stat_obj.extreme_cold_week
    extreme_hot_week = stat_obj.extreme_hot_week
    seasonal_weeks = \
        [stat_obj.typical_winter_week,
        stat_obj.typical_spring_week,
        stat_obj.typical_summer_week,
        stat_obj.typical_autumn_week]