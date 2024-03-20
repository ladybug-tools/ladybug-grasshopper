# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Create a set of parameters that define the body characteristics for the PET model.
-
These parameters can be plugged into any of the components that compute
PET thermal comfort.
-

    Args:
        _age_: The age of the human subject in years. (Default: 36 years for middle age
            of the average worldwide life expectancy).
        _sex_: A value between 0 and 1 to indicate the sex of the human subject,
            which influences the computation of basal metabolism. 0 indicates male.
            1 indicates female and any number in between denotes a weighted average
            between the two. (Default: 0.5).
        _height_: The height of the human subject in meters. Average male height
            is around 1.75m while average female height is 1.55m. (Default: 1.65m
            for a worldwide average between male and female height).
        _body_mass_: The body mass of the human subject in kilograms. (Default: 62 kg
            for the worldwide average adult human body mass).
        _posture_: A text string indicating the posture of the body. Letters must
            be lowercase. Default is "standing". Choose from the following:
            _
            * standing
            * seated
            * crouching
        humid_acclim_: A boolean to note whether the human subject is acclimated
            to a humid/tropical climate (True) or is acclimated to a temperate
            climate (False). When True, the categories developed by Lin and
            Matzarakis (2008) will be used to assess comfort instead of the original
            categories developed by Matzarakis and Mayer (1996).

    Returns:
        pet_par: A PET comfort parameter object that can be plugged into any of the
            components that compute PET thermal comfort.
"""

ghenv.Component.Name = 'LB PET Body Parameters'
ghenv.Component.NickName = 'PETPar'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug_comfort.parameter.pet import PETParameter
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_comfort:\n\t{}'.format(e))
try:
    from ladybug_rhino.grasshopper import turn_off_old_tag
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
turn_off_old_tag(ghenv.Component)


pet_par = PETParameter(_age_, _sex_, _height_, _body_mass_, _posture_, humid_acclim_)
