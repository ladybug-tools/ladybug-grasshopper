# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate Adaptive thermal comfort.
-
The Adaptive thermal comfort model is for use on the interior of buildings where
a heating or cooling system is not operational and occupants have the option to
open windows for natural ventilation.
-
Note that, for fully conditioned buildings, the PMV thermal comfort model should
be used.
-

    Args:
        _out_temp: Outdoor temperatures in one of the following formats:
            * A Data Collection of outdoor dry bulb temperatures recorded over
                the entire year. This Data Collection must be continouous and
                must either be an Hourly Collection or Daily Collection. In the event
                that the input adapt_par_ has a _avgm_or_runmean_ set to True,
                Monthly collections are also acceptable here. Note that, because
                an annual input is required, this input collection does not have
                to align with the _air_temp or _mrt_ inputs.
            * A Data Collection of prevailing outdoor temperature values in C.
                This Data Collection must align with the _air_temp or _mrt_
                inputs and bear the PrevailingOutdoorTemperature data type in
                its header.
            * A single prevailing outdoor temperature value in C to be used
                for all of the _air_temp or _mrt_ inputs.
        _air_temp: Data Collection or individual value for air temperature in C.
        _mrt_: Data Collection or individual value for mean radiant temperature
            (MRT) in C. Default is the same as the air_temp.
        _air_speed_: Data Collection or individual value for air speed in m/s.
            Note that higher air speeds in the adaptive model only widen the
            upper boundary of the comfort range at temperatures above 24 C
            and will not affect the lower temperature of the comfort range.
            Default is a very low speed of 0.1 m/s.
        adapt_par_: Optional comfort parameters from the "LB Adaptive Comfort Parameters"
            component to specify the criteria under which conditions are
            considered acceptable/comfortable. The default will use ASHRAE-55
            adaptive comfort criteria.
        _run: Set to True to run the component.

    Returns:
        report: Reports, errors, warnings, etc.
        prevail_temp: Data Collection of prevailing outdoor temperature in
            degrees C.
        neutral_temp: Data Collection of the desired neutral temperature in
            degrees C.
        deg_neutral: Data Collection of the degrees from desired neutral
            temperature in degrees C.
        comfort: Integers noting whether the input conditions are acceptable
            according to the assigned comfort_parameter.
            _
            Values are one of the following:
                * 0 = uncomfortable
                * 1 = comfortable
        condition: Integers noting the thermal status of a subject according to
            the assigned comfort_parameter.
            _
            Values are one of the following:
                * -1 = cold
                *  0 = netural
                * +1 = hot
        comf_obj: A Python object containing all inputs and results of the
            analysis.  This can be plugged into components like the "Comfort
            Statistics" component to get further information.
"""

ghenv.Component.Name = 'LB Adaptive Comfort'
ghenv.Component.NickName = 'Adaptive'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

try:
    from ladybug.datatype.temperature import Temperature
    from ladybug.datacollection import BaseCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_comfort.collection.adaptive import Adaptive
    from ladybug_comfort.parameter.adaptive import AdaptiveParameter
    from ladybug_comfort.adaptive import t_operative, \
        adaptive_comfort_ashrae55, adaptive_comfort_en15251, \
        cooling_effect_ashrae55, cooling_effect_en15251, \
        adaptive_comfort_conditioned
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_comfort:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def extract_collections(input_list):
    """Process inputs into collections and floats."""
    defaults = [None, None, _air_temp, 0.1]
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
    input_list = [_out_temp, _air_temp, _mrt_, _air_speed_]
    input, data_colls = extract_collections(input_list)
    adapt_par = adapt_par_ or AdaptiveParameter()

    if data_colls == []:
        # The inputs are all individual values.
        prevail_temp = input[0]
        to = t_operative(input[1], float(input[2]))
        
        # Determine the ralationship to the neutral temperature
        if adapt_par.conditioning != 0:
            comf_result = adaptive_comfort_conditioned(prevail_temp, to,
                adapt_par.conditioning, adapt_par.standard)
        elif adapt_par.ashrae55_or_en15251 is True:
            comf_result = adaptive_comfort_ashrae55(prevail_temp, to)
        else:
            comf_result = adaptive_comfort_en15251(prevail_temp, to)
        
        # Determine the cooling effect
        if adapt_par.discrete_or_continuous_air_speed is True:
            ce = cooling_effect_ashrae55(input[3], to)
        else:
            ce = cooling_effect_en15251(input[3], to)
        
        # Output results
        neutral_temp = comf_result['t_comf']
        deg_neutral = comf_result['deg_comf']
        comfort = adapt_par.is_comfortable(comf_result, ce)
        condition = adapt_par.thermal_condition(comf_result, ce)
    else:
        # The inputs include Data Collections.
        if not isinstance(_air_temp, BaseCollection):
            _air_temp = data_colls[0].get_aligned_collection(
                float(_air_temp), Temperature(), 'C')
        
        comf_obj = Adaptive.from_air_and_rad_temp(_out_temp, _air_temp, _mrt_,
                                                 _air_speed_, adapt_par)
        prevail_temp = comf_obj.prevailing_outdoor_temperature
        neutral_temp = comf_obj.neutral_temperature
        deg_neutral = comf_obj.degrees_from_neutral
        comfort = comf_obj.is_comfortable
        condition = comf_obj.thermal_condition