# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Get statitics of thermal comfort from a Ladybug Comfort Object.
-

    Args:
        _comf_obj: A Ladybug ComfortCollection object from any of the comfort model components.
    Returns:
        pct_hot: The percent of time that conditions are hotter than acceptable limits.
        pct_neutral: The percent of time that conditions are within acceptable limits
            (aka. the percent of time comfortable).
        pct_cold: The percent of time that conditions are colder than acceptable limits.
"""

ghenv.Component.Name = "LadybugPlus_Comfort Statistics"
ghenv.Component.NickName = 'comfStat'
ghenv.Component.Message = 'VER 0.0.04\nAUG_11_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:
    from ladybug_comfort.collection.base import ComfortCollection
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_comfort:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    assert isinstance(_comf_obj, ComfortCollection), '_comf_obj must be a ' \
        'Ladybug ComfortCollection object. Got {}.'.format(type(_comf_obj))
    
    pct_hot = _comf_obj.percent_hot
    pct_neutral = _comf_obj.percent_neutral
    pct_cold = _comf_obj.percent_cold