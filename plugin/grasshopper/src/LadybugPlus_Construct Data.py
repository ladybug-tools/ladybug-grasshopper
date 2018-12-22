# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Construct a Ladybug DataCollection from values and metadata.
-

    Args:
        _values: The numerical values of the DataCollection.
        _a_period: A Ladybug AnalysisPeriod object that corresponds with the _values
        location_: Location data as a ladybug Location or location string
            (Default: unknown).
        data_type_: Type of data (e.g. Temperature) (Default: unknown).
        unit_: Units of the data_type (e.g. C) (Default: unknown).
    Returns:
        data: A Ladybug DataCollection object.
"""

ghenv.Component.Name = "LadybugPlus_Construct Data"
ghenv.Component.NickName = 'constrData'
ghenv.Component.Message = 'VER 0.0.04\nDEC_21_2018'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = '01 :: Analyze Weather Data'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    from ladybug.datatypenew import DataTypes
    from ladybug.header import Header
    from ladybug.datacollection import DataCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))


if _values != [] and _values[0] is not None and _a_period:
    data_type = DataTypes.type_by_name_and_unit(data_type_, unit_)
    header = Header(location=location_, data_type=data_type, unit=unit_)
    data = DataCollection.from_data_and_analysis_period(_values, _a_period, header)