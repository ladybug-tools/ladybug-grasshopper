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
        _data: A list of aligned Data Collections to be evaluated against
            the _statement.
        _statement: A conditional statement as a string (e.g. a > 25).
        .   
            The variable of the first data collection should always be named 'a'
            (without quotations), the variable of the second list should be
            named 'b', and so on.
            .
            For example, if three data collections are connected to _data
            and the following statement is applied:
            '18 < a < 26 and b < 80 and c > 2'
            The resulting collections will only include values where the first
            data collection is between 18 and 26, the second collection is less
            than 80 and the third collection is greater than 2.
    Returns:
        data: A list of Data Collections that have been filtered by the statement_.
"""

ghenv.Component.Name = "LadybugPlus_Apply Conditional Statement"
ghenv.Component.NickName = 'applyState'
ghenv.Component.Message = 'VER 0.0.04\nMAR_11_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "0"

try:
    from ladybug.datacollection import HourlyContinuousCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

if _data != [] and _data[0] is not None and _statement:
    for dat in _data:
        assert hasattr(dat, 'isDataCollection'), '_data must be a data' \
            ' collection. Got {}.'.format(type(dat))
    
    data = HourlyContinuousCollection.filter_collections_by_statement(
        _data, _statement)