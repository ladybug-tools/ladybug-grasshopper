# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Convert a hourly Ladybug data collection to a continuous collection at a
specific timestep.
-
This will be done either through linear interpolation or by culling out values
that do not fit the timestep.  It can also be used to convert a discontinous
data collection to a continuous one by linearly interpolating over holes in
the data set.
-

    Args:
        _data: A Ladybug Hourly DataCollection object.  This can be either
            Continuous or discontinuous.
        _time_st_: The timestep to which the data will be converted. If this
            is higher than the input _data timestep, values will be linerarly
            interpolated to the new timestep.  If it is lower, values that do
            not fit the timestep will be culled out of the DataCollection.
            Default is 1.
    Returns:
        data: A Continuous DataCollection at the input _time_st_.
"""

ghenv.Component.Name = "LadybugPlus_Convert to Timestep"
ghenv.Component.NickName = 'toStep'
ghenv.Component.Message = 'VER 0.0.04\nJUN_07_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "0"

try:
    from ladybug.datacollection import HourlyDiscontinuousCollection, \
        HourlyContinuousCollection
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check the inputs
    assert isinstance(_data, HourlyDiscontinuousCollection), \
        ' Connected _data is not a Hourly Data Collection. Got{}'.format(type(_data))
    if _time_st_ is not None:
        valid_timesteps = _data.header.analysis_period.VALIDTIMESTEPS
        assert _time_st_ in valid_timesteps, ' Connected _time_st_ is not a'\
            ' hourly timestep.\n Got {}. Choose from: {}'.format(
            _time_st_, sorted(valid_timesteps.keys()))
    
    # if the data is not continuous, interpolate over holes.
    if not isinstance(_data, HourlyContinuousCollection):
        if _data.validated_a_period is False:
            _data = data.validate_analysis_period
        _data = _data.interpolate_holes()
    
    # convert the data to the timestep
    if _time_st_ and _time_st_ != _data.header.analysis_period.timestep:
        if _time_st_ < _data.header.analysis_period.timestep:
            data = _data.cull_to_timestep(_time_st_)
        else:
            data = _data.interpolate_to_timestep(_time_st_)
    else:
        data = _data