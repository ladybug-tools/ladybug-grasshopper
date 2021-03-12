# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Create a set of parameters that define the acceptable conditions of the
Adaptive thermal comfort model.
-
These parameters can be plugged into any of the components that compute
Adaptive thermal comfort.
-

    Args:
        _ashrae_or_en15251_: A boolean to note whether to use the ASHRAE-55 neutral
            temperature function (True) or the EN-15251 function (False).
            Note that this input will also determine default values for many of
            the other properties of this object.
        _neutral_offset_:  The number of degrees Celcius from the neutral temperature
            where the input operative temperature is considered acceptable.
            The default is 2.5C when the neutral temperature function is ASHRAE-55
            and 3C when the neutral temperature function is EN-15251.
            You may want to use the set_neutral_offset_from_ppd() or the
            set_neutral_offset_from_comfort_class() methods on this object to set
            this value using ppd from the ASHRAE-55 standard or comfort classes
            from the EN-15251 standard respectively.
        _avgm_or_runmean_: A boolean to note whether the prevailing outdoor
            temperature is computed from the average monthly temperature (True) or
            a weighted running mean of the last week (False).  The default is True
            when the neutral temperature function is ASHRAE-55 and False when the
            neutral temperature function is EN-15251.
        _discr_or_cont_vel_: A boolean to note whether discrete
            categories should be used to assess the effect of elevated air speed
            (True) or whether a continuous function should be used (False).
            The default is True when the neutral temperature function is ASHRAE-55
            and False when the neutral temperature function is EN-15251.
        _cold_prevail_limit_: A number indicating the prevailing outdoor
            temperature below which acceptable indoor operative temperatures
            flatline. The default is 10C when the neutral temperature function is
            ASHRAE-55 and 15C when the neutral temperature function is EN-15251.
            This number cannot be greater than 22C and cannot be less than 10C.
        _conditioning_: A number between 0 and 1 that represents how "conditioned"
            vs. "free-running" the building is.
                0 = free-running (completely passive with no air conditioning)
                1 = conditioned (no operable windows and fully air conditioned)
            The default is 0 since both the ASHRAE-55 and EN-15251 standards prohibit
            the use of adaptive comfort methods when a heating/cooling system is active.
            When set to a non-zero number, a neutral temperature function for
            heated/cooled operation derived from the SCATs database will be used.
            For more information on how adaptive comfort methods can be applied to
            conditioned buildings, see the neutral_temperature_conditioned function
            in the ladybug_comfort documentation.
    
    Returns:
        adapt_par: An Adaptive comfort parameter object that can be plugged into
            any of the components that compute Adaptive thermal comfort.
"""

ghenv.Component.Name = 'LB Adaptive Comfort Parameters'
ghenv.Component.NickName = 'AdaptPar'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from ladybug_comfort.parameter.adaptive import AdaptiveParameter
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_comfort:\n\t{}'.format(e))


adapt_par = AdaptiveParameter(_ashrae_or_en15251_, _neutral_offset_,
                              _avgm_or_runmean_, _discr_or_cont_vel_,
                              _cold_prevail_limit_, _conditioning_)
