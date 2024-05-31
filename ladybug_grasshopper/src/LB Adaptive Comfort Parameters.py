# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Create a set of parameters that define the acceptable conditions of the
Adaptive thermal comfort model.
-
These parameters can be plugged into any of the components that compute
Adaptive thermal comfort.
-

    Args:
        _ashrae_or_en_: A boolean to note whether to use the ASHRAE-55 neutral
            temperature function (True) or the european neutral function (False),
            which is consistent with EN-16798 (and the older EN-15251).
            Preference is given to EN-16798 in places where EN-16798 and
            EN-15251 differ (eg. the 1C lower cold threshold in EN-16798).
            Note that this input will also determine default values for
            many of the other properties of this object.
        _neutral_offset_:  The number of degrees Celcius from the neutral temperature
            where the input operative temperature is considered acceptable.
            The default is 2.5C when the neutral temperature function is ASHRAE-55
            (consistent with 90% PPD) and 3C when the neutral temperature
            function is EN-16798 (consistent with comfort class II). Note that,
            when the neutral temperature function is EN-16798, one degree
            Celsius is automatically added to the offset value input here to
            get the lower temperature threshold. This accounts for the fact that
            EN-16798 does not interpret the neutral offset symmetically.
            _
            For ASHRAE-55, the following neutral offsets apply.
                * 90 PPD - 2.5C
                * 80 PPD - 3.5C
            _
            For the EN standard, the following neutral offsets apply.
                * Class I - 2C
                * Class II - 3C
                * Class III - 4C
        _avgm_or_runmean_: A boolean to note whether the prevailing outdoor
            temperature is computed from the average monthly temperature (True) or
            a weighted running mean of the last week (False).  The default is True
            when the neutral temperature function is ASHRAE-55 and False when the
            neutral temperature function is EN.
        _discr_or_cont_vel_: A boolean to note whether discrete categories should be
            used to assess the effect of elevated air speed (True) or whether
            a continuous function should be used (False). Note that continuous
            air speeds were only used in the older EN-15251 standard and are
            not a part of the more recent EN-16798 standard.
            When unassigned, this will be True for discrete air speeds.
        _cold_prevail_limit_: A number indicating the prevailing outdoor temperature
            below which acceptable indoor operative temperatures flat line.
            The default is 10C, which is consistent with both ASHRAE-55 and
            EN-16798. However, 15C was used for the older EN-15251 standard.
            This number cannot be greater than 22C and cannot be less than 10C.
        _conditioning_: A number between 0 and 1 that represents how "conditioned"
            vs. "free-running" the building is.
                0 = free-running (completely passive with no air conditioning)
                1 = conditioned (no operable windows and fully air conditioned)
            The default is 0 since both the ASHRAE-55 and the EN standards prohibit
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
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from ladybug_comfort.parameter.adaptive import AdaptiveParameter
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_comfort:\n\t{}'.format(e))
try:
    from ladybug_rhino.grasshopper import turn_off_old_tag
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
turn_off_old_tag(ghenv.Component)


adapt_par = AdaptiveParameter(_ashrae_or_en_, _neutral_offset_,
                              _avgm_or_runmean_, _discr_or_cont_vel_,
                              _cold_prevail_limit_, _conditioning_)
