# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Adjust the assumptions of the passive strategies that can be overalid on the
Psychrometric Chart using the "LB PMV Polygon" component. The default assumptions
of each of the strategies are as follows: 
_
Thermal Mass + Night Vent - The polygon represents the conditions under which
shaded, night-flushed thermal mass can keep occupants cool. By default, this
polygon assumes that temperatures can get as high as 12 C above the max temperature
of the comfort polygon as long temperatures 8 hours before the hot hour are
3.0 C lower than the max temperture of the comfort polygon. This parameter
component can be used to adjust these two temperature values and the number of
hours that the building keeps its "coolth".
_
Occupant Use of Fans - This polygon is made by assuming that an air speed of 1.0 m/s
is the maximum speed tolerable before papers start blowing around and conditions
become annoying to occupants. The polygon is determined by running a PMV model
with this fan air speed and the PMV inputs of the warmest comfort conditions.
This parameter component can be used to adjust this maximum acceptable air speed.
_
Capture Internal Heat - The polygon is made by assuming a minimum building balance
point of 12.8 C and any conditions that are warmer than that will keep occupants
comfortable (up to the comfort polygon). It is assumed that, above this building
balance temperature, the building is free-running and occupants are able to open
windows as they wish to keep conditions from overshooting the comfort polygon.
Note that the default balance temperature of 12.8 C is fairly low and assumes a
significant amount of internal heat from people, equipment. etc. Or the building 
as a well-insulated envelope to ensure what internal heat there is can leave the
building slowly. This parameter component can be used to adjust the balance
temperature.
_
Passive Solar Heating - The polygon represents the conditions under which
sun-exposed thermal mass can keep occupants warm in winter. By default, this
polygon assumes that temperatures can get as high as 12 C above the max temperature
of the comfort polygon as long temperatures 8 hours before the hot hour are
3.0 C lower than the max temperture of the comfort polygon. This parameter
component can be used to adjust these two temperature values and the number of
hours that the building keeps its "coolth".
-

    Args:
        _day_above_comf_: A number in degrees Celsius representing the maximum daily
            temperature above the comfort range which can still be counted in
            the "Mass + Night Vent" polygon. (Default: 12 C).
        _night_below_comf_: A number in degrees Celsius representing the minimum temperature
            below the maximum comfort polygon temperature that the outdoor
            temperature must drop at night in order to count towards the "Mass
            + Night Vent" polygon. (Default: 3C).
        _fan_air_speed_: The air speed around the occupants that the fans create in m/s.
            This is used to create the "Occupant Use of Fans" polygon. Note that
            values above 1 m/s tend to blow papers off desks. (Default: 1.0 m/3)
        _balance_temp_: The balance temperature of the building in Celsius when accounting
            for all internal heat. This is used to create the "Capture Internal
            Heat" polygon. This value must be greater or equal to 5 C (balance
            temperatures below 10 C are exceedingly rare) and it should be less
            than the coldest temperature of the merged comfort polygon in order
            to be meaningful. (Default: 12.8 C)
        _solar_heat_cap_: A number representing the amount of outdoor solar flux (W/m2)
            that is needed to raise the temperature of the theoretical building by
            1 degree Celsius. The lower this number, the more efficiently the
            space is able to absorb passive solar heat. The default assumes a
            relatively small passively solar heated zone without much mass. A
            higher number will be required the larger the space is and the more
            mass that it has. (Default: 50 W/m2)
        _time_constant_: A number that represents the amount of time in hours that a
            therortical building can passively maintain its temperature. This
            is used to determine how many hours a space can maintain a cool
            temperature after night flushing for the "Mass + Night Vent" polygon.
            It is also used to determine how many hours a space can store solar
            radiation for the "Passive Solar Heating" polygon. The default
            assumes a relatively well-isulated building with a thermal mass
            typical of most contemporary buildings. Higher mass buildings will
            be able to support a longer time constant. (Default: 8 hours).

    Returns:
        strategy_par: Passive strategy parameters that can be plugged into the "LB
            PMV Polygon" to adjust the assumptions of the passive strategy
            polygons.
"""

ghenv.Component.Name = 'LB Passive Strategy Parameters'
ghenv.Component.NickName = 'StrategyPar'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug_rhino.grasshopper import give_warning, objectify_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def check_strategy(value, name, default, max, min):
    """Check a strategy parameter to ensure it is correct."""
    if value is None:
        strategy_par.append(default)
    elif value <= max and value >= min:
        strategy_par.append(value)
    else:
        strategy_par.append(default)
        msg = '"{}" must be between {} and {}. Got {}.\nReverting to default ' \
            'value of {}'.format(name, min, max, value, default)
        print(msg)
        give_warning(ghenv.Component, msg)


#check and add each of the strategies
strategy_par = []
check_strategy(_day_above_comf_, '_day_above_comf_', 12.0, 30.0, 0.0)
check_strategy(_night_below_comf_, '_night_below_comf_', 3.0, 15.0, 0.0)
check_strategy(_fan_air_speed_, '_fan_air_speed_', 1.0, 10.0, 0.1)
check_strategy(_balance_temp_, '_balance_temp_', 12.8, 20.0, 5.0)
check_strategy(_solar_heat_cap_, '_solar_heat_cap_', 50.0, 1000.0, 1.0)
check_strategy(_time_constant_, '_time_constant_', 8, 48, 1)
strategy_par = objectify_output('Passive Strategy Parameters', strategy_par)
