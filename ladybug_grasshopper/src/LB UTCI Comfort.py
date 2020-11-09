# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Calculate Universal Thermal Climate Index (UTCI).
-
UTCI is a thermal comfort model strictly for the outdoors.
It is an interational standard for outdoor temperature sensation
(aka. "feels-like" temperature) and is the most common of such
"feels-like" temperature metrics used by meteorologists.
-
While UTCI is valid in all climates, seasons, and scales, it assumes
that human subjects are walking and that they naturally adapt their
clothing with the outdoor temperature.
For outdoor situations that do not fit these criteria, the Physiological
Equivalent Temperature (PET) model should be used.

-

    Args:
        _air_temp: Data Collection or individual value of air temperature in C.
        _mrt_: Data Collection or individual value of mean radiant temperature
            (MRT) in C. Default is the same as the air_temp.
        _rel_humid: Data Collection or individual value of relative humidity in %.
        _wind_vel_: Data Collection or individual of air speed values in m/s.
            Default is a low speed of 0.5 m/s, which is the lowest input
            speed that is recommended for the UTCI model.
        _run: Set to True to run the component.

    Returns:
        report: Reports, errors, warnings, etc.
        utci: Universal Thermal Climate Index (UTCI) in Celcius.
        comfort: Integers noting whether the input conditions result in no
            thermal stress.
            .
            Values are one of the following:
                0 = thermal stress
                1 = no thremal stress
        condition: Integers noting the thermal status of a subject.
            .
            Values are one of the following:
                -1 = cold
                 0 = netural
                +1 = hot
        category: Integers noting the category that the UTCI conditions fall
            under on an 11-point scale.
            .
            Values are one of the following:
                -5 = Extreme Cold Stress       (UTCI < -40)
                -4 = Very Strong Cold Stress   (-40 <= UTCI < -27)
                -3 = Strong Cold Stress        (-27 <= UTCI < -13)
                -2 = Moderate Cold Stress      (-12 <= UTCI < 0)
                -1 = Slight Cold Stress        (0 <= UTCI < 9)
                 0 = No Thermal Stress         (9 <= UTCI < 26)
                +1 = Slight Heat Stress        (26 <= UTCI < 28)
                +2 = Moderate Heat Stress      (28 <= UTCI < 32)
                +3 = Strong Heat Stress        (32 <= UTCI < 38)
                +4 = Very Strong Heat Stress   (38 <= UTCI < 46)
                +5 = Extreme Heat Stress       (46 < UTCI)
        comf_obj: A Python object containing all inputs and results of the
            analysis.  This can be plugged into components like the "Comfort
            Statistics" component to get further information.
"""

ghenv.Component.Name = 'LB UTCI Comfort'
ghenv.Component.NickName = 'UTCI'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

try:
    from ladybug.datatype.temperature import Temperature
    from ladybug.datacollection import BaseCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_comfort.collection.utci import UTCI
    from ladybug_comfort.parameter.utci import UTCIParameter
    from ladybug_comfort.utci import universal_thermal_climate_index
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_comfort:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def extract_collections(input_list):
    """Process inputs into collections and floats."""
    defaults = [None, _air_temp, 0.5, None]
    data_colls = []
    for i, input in enumerate(input_list):
        if input is None:
            input_list[i] = defaults[i]
        elif isinstance(input, BaseCollection):
            data_colls.append(input)
        else:
            try:
                input_list[i] = float(input)
            except ValueError as e:
                raise TypeError('input {} is not valid. Expected float or '
                                'DataCollection. Got {}'.format(input, type(input)))
    return input_list, data_colls

if all_required_inputs(ghenv.Component) and _run is True:
    # Process inputs and assign defaults.
    input_list = [_air_temp, _mrt_, _wind_vel_, _rel_humid]
    input, data_colls = extract_collections(input_list)
    
    if data_colls == []:
        # The inputs are all individual values.
        utci = universal_thermal_climate_index(
            input[0], float(input[1]), input[2], input[3])
        utci_par = UTCIParameter()
        comfort = utci_par.is_comfortable(utci)
        condition = utci_par.thermal_condition(utci)
        category = utci_par.thermal_condition_eleven_point(utci)
    else:
        # The inputs include Data Collections.
        if not isinstance(_air_temp, BaseCollection):
            _air_temp = data_colls[0].get_aligned_collection(
                float(_air_temp), Temperature(), 'C')
        
        comf_obj = UTCI(_air_temp, _rel_humid, _mrt_, _wind_vel_)
        utci = comf_obj.universal_thermal_climate_index
        comfort = comf_obj.is_comfortable
        condition = comf_obj.thermal_condition
        category = comf_obj.thermal_condition_eleven_point