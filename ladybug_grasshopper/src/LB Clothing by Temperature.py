# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Estimate levels of clothing using a temperature value or data collection of
temperatures to which a human subject is adapting (typically the outdoor
air temperature).
_
This resulting clothing values can be plugged into the _clothing_ input of the
"LB PMV Comfort" component or the "HB PMV Comfort Map".
_
By default, this function derives clothing levels using a model developed by
Schiavon, Stefano based on outdoor air temperature, which is implemented in the
CBE comfort tool (https://comfort.cbe.berkeley.edu/).
_
The version of the model implemented here allows changing of the maximum and minimum
clothing levels, which the Schiavon model sets at 1 and 0.46 respectively, and the
temperatures at which these clothing levels occur, which the Schiavon model sets
at -5 C and 26 C respectively.
-

    Args:
        _temperature: A data collection or single number representing the temperature to
            which the human subject adapts their clothing. This is typically the
            dry bulb temperature obtained from the "LB Import EPW" component.
        _period_: An optional analysis period to select a subset of the whole outdoor
            temperature data collection for which clothing levels will be
            computed. By default the whole analysis period of the _temperature
            will be used.
        _max_clo_: A number for the maximum clo value that the human subject wears
            on the coldest days. (Default: 1 clo, per the original Schiavon
            clothing function).
        _max_clo_temp_: A number for the temperature below which the _max_clo_ value
            is applied (in Celsius). (Default: -5 C, per the original
            Schiavon clothing function with outdoor temperature).
        _min_clo_: A number for the minimum clo value that the human subject wears
            wears on the hotest days. (Default: 0.46 clo,
            per the original Schiavon clothing function).
        _min_clo_temp_: A number for the temperature above which the _min_clo_ value
            is applied (in Celsius). (Default: 26 C, per the original
            Schiavon clothing function).

    Returns:
        report: Reports, errors, warnings, etc.
        clo: A single number or data collection of numbers representing the clothing
            that would be worn (in clo). Note that, if you have hooked up an
            hourly continuous data collection, the clothing levels will change
            on a 12-hour basis to simulate the typical cycle on which a human
            changes their clothing.

"""

ghenv.Component.Name = "LB Clothing by Temperature"
ghenv.Component.NickName = 'CloByTemp'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug.datacollection import BaseCollection, HourlyContinuousCollection
    from ladybug.datatype.rvalue import ClothingInsulation
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_comfort.clo import schiavon_clo
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set default values
    _max_clo_ = _max_clo_ if _max_clo_ is not None else 1.0
    _max_clo_temp_ = _max_clo_temp_ if _max_clo_temp_ is not None else -5
    _min_clo_ = _min_clo_ if _min_clo_ is not None else 0.46
    _min_clo_temp_ = _min_clo_temp_ if _min_clo_temp_ is not None else 26

    # if the temperature is hourly continuous, simplify the values
    if isinstance(_temperature, HourlyContinuousCollection):
        date_times, temps = _temperature.datetimes, _temperature.values
        last_time, last_val = date_times[0].sub_hour(6), temps[0]
        new_vals = []
        for v, dt in zip(temps, date_times):
            time_diff = dt - last_time
            if time_diff.seconds / 3600 >= 12:
                last_time, last_val = dt, v
            new_vals.append(last_val)
        _temperature = _temperature.duplicate()
        _temperature.values = new_vals

    # apply the analysis period if requests
    if period_ is not None and isinstance(_temperature, BaseCollection):
        _temperature = _temperature.filter_by_analysis_period(period_)

    clo = HourlyContinuousCollection.compute_function_aligned(
        schiavon_clo, [_temperature, _max_clo_, _max_clo_temp_, _min_clo_, _min_clo_temp_],
        ClothingInsulation(), 'clo')
