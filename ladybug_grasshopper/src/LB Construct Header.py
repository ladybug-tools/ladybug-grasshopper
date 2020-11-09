# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Construct a Ladybug Header to be used to create a ladybug DataCollection.
-

    Args:
        _data_type: Text representing the type of data (e.g. Temperature). A full list
            of acceptable inputs can be seen by checking the all_u output of
            the "LB Unit Converter" component. This input can also be a custom
            DataType object that has been created with the "LB Construct Data
            Type" component.
        _unit_: Units of the data_type (e.g. C). Default is to use the
            base unit of the connected_data_type.
        _a_period: A Ladybug AnalysisPeriod object. (Default
        metadata_: Optional metadata to be associated with the Header.
            Input should be a list of text strings with a property name
            and value for the property separated by a colon.
            (eg. ['source: TMY3', 'city: New York'])
    
    Returns:
        header: A Ladybug Header object.
"""

ghenv.Component.Name = "LB Construct Header"
ghenv.Component.NickName = 'ConstrHeader'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    import ladybug.datatype
    from ladybug.datatype.base import DataTypeBase
    from ladybug.header import Header
    from ladybug.analysisperiod import AnalysisPeriod
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# error message if the data type is not recognized
msg = 'The connected _data_type is not recognized.\nMake your own with ' \
    'the "LB Construct Data Type" component or choose from the following:' \
    '\n{}'.format('\n'.join(ladybug.datatype.BASETYPES))


if all_required_inputs(ghenv.Component):
    if isinstance(_data_type, DataTypeBase):
        pass
    elif isinstance(_data_type, str):
        _data_type = _data_type.replace(' ', '')
        try:
            _data_type = ladybug.datatype.TYPESDICT[_data_type]()
        except KeyError:  # check to see if it's a captilaization issue
            _data_type = _data_type.lower()
            for key in ladybug.datatype.TYPESDICT:
                if key.lower() == _data_type:
                    _data_type = ladybug.datatype.TYPESDICT[key]()
                    break
            else:
                raise TypeError(msg)
    else:
        raise TypeError(msg)

    if _unit_ is None:
        _unit_ = _data_type.units[0]

    if _a_period_ is None:
        _a_period_ = AnalysisPeriod()

    metadata_dict = {}
    if metadata_ != []:
        for prop in metadata_:
            key, value = prop.split(':')
            metadata_dict[key] = value.strip()

    header = Header(_data_type, _unit_, _a_period_, metadata_dict)