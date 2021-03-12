# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Convert a hourly Ladybug data collection to a continuous collection at a
specific timestep.
_
This will be done either through linear interpolation or by culling out values
that do not fit the timestep.  It can also be used to convert a discontinous
data collection to a continuous one by linearly interpolating over holes in
the data set.
-

    Args:
        _data: A Ladybug Hourly DataCollection object.  This can be either
            continuous or discontinuous.
        _timestep_: The timestep to which the data will be converted. If this
            is higher than the input _data timestep, values will be
            linerarly interpolated to the new timestep.  If it is lower,
            values that do not fit the timestep will be removed from the
            DataCollection. (Defaut: 1)

    Returns:
        data: A Continuous DataCollection at the input _timestep_.
"""

ghenv.Component.Name = 'LB Convert to Timestep'
ghenv.Component.NickName = 'ToStep'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug.datacollection import HourlyDiscontinuousCollection, \
        HourlyContinuousCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check the inputs
    assert isinstance(_data, HourlyDiscontinuousCollection), \
        ' Connected _data is not a Hourly Data Collection. Got{}'.format(type(_data))
    if _timestep_ is not None:
        valid_timesteps = _data.header.analysis_period.VALIDTIMESTEPS
        assert _timestep_ in valid_timesteps, ' Connected _timestep_ is not a'\
            ' hourly timestep.\n Got {}. Choose from: {}'.format(
            _timestep_, sorted(valid_timesteps.keys()))

    # if the data is not continuous, interpolate over holes.
    if not isinstance(_data, HourlyContinuousCollection):
        if _data.validated_a_period is False:
            _data = data.validate_analysis_period
        _data = _data.interpolate_holes()

    # convert the data to the timestep
    if _timestep_ and _timestep_ != _data.header.analysis_period.timestep:
        if _timestep_ < _data.header.analysis_period.timestep:
            data = _data.cull_to_timestep(_timestep_)
        else:
            data = _data.interpolate_to_timestep(_timestep_)
    else:
        data = _data