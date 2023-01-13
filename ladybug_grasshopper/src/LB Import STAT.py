# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Import data from a standard .stat file.
-

    Args:
        _stat_file: A .stat file path on your system as a string.

    Returns:
        location: A Ladybug Location object describing the location data in the STAT file.
        ashrae_zone: The ASHRAE climate zone of the STAT file. Numbers in the zone
            denote average temperature (0 = Hottest; 8 = Coldest). Letters in
            the zone denote wetness (A = Humid; B = Dry; C = Marine)
        koppen_zone: The Koppen climate zone of the STAT file. The Koppen climate
            system uses vegetation as in indicator fo climate and combines
            average monthly temperatures, precipitation, and the seasonality
            of precipitation.
        clear_dir_norm_rad: The hourly "Clear Sky" Direct Normal Radiation in Wh/m2.
            Such clear sky radiation is typically used for sizing cooling
            systems. If monthly optical depths are found within the STAT
            file, these values will come from the Revised ASHARAE Clear Sky
            (Tau model). If no optical depths are found, they will come from
            the original ASHARE lear sky model.
        clear_diff_horiz_rad: The hourly "Clear Sky" Diffuse Horizontal Radiation
            in Wh/m2. Such clear sky radiation is typically used for sizing
            cooling systems. If monthly optical depths are found within the
            STAT file, these values will come from the Revised ASHARAE Clear Sky
            (Tau model). If no optical depths are found, they will come from
            the original ASHARE lear sky model.
        ann_heat_dday_996: A DesignDay object representing the annual 99.6%
            heating design day.
        ann_heat_dday_990: A DesignDay object representing the annual 99.0%
            heating design day.
        ann_cool_dday_004: A DesignDay object representing the annual 0.4%
            cooling design day.
        ann_cool_dday_010: A DesignDay object representing the annual 1.0%
            cooling design day.
        monthly_ddays_050: A list of 12 DesignDay objects representing monthly
            5.0% cooling design days.
        monthly_ddays_100: A list of 12 DesignDay objects representing monthly
            10.0% cooling design days.
        extreme_cold_week: A Ladybug AnalysisPeriod object representing the
            coldest week within the corresponding EPW.
        extreme_hot_week: A Ladybug AnalysisPeriod object representing the
            hottest week within the corresponding EPW.
        typical_weeks: A list of Ladybug AnalysisPeriod objects representing
            typical weeks within the corresponding EPW.
            The type of week can vary depending on the climate.
            _
            For mid and high lattitude climates with 4 seasons (eg. New York),
            these weeks are for each of the 4 seasons ordered as follows:
            Winter, Spring, Summer, Autumn
            _
            For low lattitude climates with wet/dry seasons (eg. Mumbai),
            these weeks might also include:
            Wet Season, Dry Season
            _
            For equitorial climates with no seasons (eg. Singapore),
            This output is usually a single week representing typical
            conditions of the entire year.
"""

ghenv.Component.Name = "LB Import STAT"
ghenv.Component.NickName = 'ImportSTAT'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '0 :: Import'
ghenv.Component.AdditionalHelpFromDocStrings = '4'


try:
    from ladybug.stat import STAT
    from ladybug.wea import Wea
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    stat_obj = STAT(_stat_file)

    # output location and climate zone
    location = stat_obj.location
    ashrae_zone = stat_obj.ashrae_climate_zone
    koppen_zone = stat_obj.koppen_climate_zone

    # output clear sky radiation
    try:  # first see if we can get the values from monthly optical depths
        wea = Wea.from_stat_file(_stat_file)
    except:  # no optical data was found; use the original clear sky
        wea = Wea.from_ashrae_clear_sky(location)
    clear_dir_norm_rad = wea.direct_normal_irradiance
    clear_diff_horiz_rad = wea.diffuse_horizontal_irradiance

    # output design day objects
    ann_heat_dday_996 = stat_obj.annual_heating_design_day_996
    ann_heat_dday_990 = stat_obj.annual_heating_design_day_990
    ann_cool_dday_004 = stat_obj.annual_cooling_design_day_004
    ann_cool_dday_010 = stat_obj.annual_cooling_design_day_010
    monthly_ddays_050 = stat_obj.monthly_cooling_design_days_050
    monthly_ddays_100 = stat_obj.monthly_cooling_design_days_100

    # output extreme and typical weeks
    extreme_cold_week = stat_obj.extreme_cold_week
    extreme_hot_week = stat_obj.extreme_hot_week
    typical_weeks = []
    seasonal_wks = [stat_obj.typical_winter_week, stat_obj.typical_spring_week,
                   stat_obj.typical_summer_week, stat_obj.typical_autumn_week]
    for wk in seasonal_wks:
        if wk is not None:
            typical_weeks.append(wk)
    typical_weeks.extend(stat_obj.other_typical_weeks)