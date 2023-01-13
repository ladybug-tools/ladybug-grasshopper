# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Perform a "mass" arithmetic operation between Data Collections. For example,
adding a list of Data Collections into one Data Collection.
-
Note that Data Collections must be aligned in order for this component to run
successfully.
-
Using this component will often be much faster and more elegant compared to
deconstructing the data collection, performing the operation with native
Grasshopper components, and rebuilding the collection.
-

    Args:
        _data: A list of Data Collections to be used in the arithmetic operation.
        _operator_: Text for the operator to use between the Data Collections.
            Valid examples include (+, -, *, /). By default this is + for addition.
        type_: Optional text for a new "type" key in the Data Collection's metadata.
            This will usually show up in most Ladybug visualiztions and it should
            usually change for most types of operations.

    Returns:
        data: A Ladybug data collection object derived from the operation between
            the two data inputs.
"""

ghenv.Component.Name = "LB Mass Arithmetic Operation"
ghenv.Component.NickName = 'MassArithOp'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    import ladybug.datatype
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # build the arithmetic statement
    operator = '+' if _operator_ is None else _operator_
    statement = 'data {} data_i'.format(operator)

    # perform the arithmetic operation
    data = _data[0]
    for data_i in _data[1:]:
        data = eval(statement, {'data': data, 'data_i': data_i})  # I love Python!

    # try to replace the data collection type
    try:
        data = data.duplicate()
        if type_:
            data.header.metadata['type'] = type_
        elif 'type' in data.header.metadata:
            d_unit = data.header.unit
            for key in ladybug.datatype.UNITS:
                if d_unit in ladybug.datatype.UNITS[key]:
                    base_type = ladybug.datatype.TYPESDICT[key]()
                    data.header.metadata['type'] = str(base_type)
                    break
            else:
                data.header.metadata['type'] = 'Unknown Data Type'
        if 'System' in data.header.metadata:
            data.header.metadata.pop('System')
        if 'Zone' in data.header.metadata:
            data.header.metadata.pop('Zone')
    except AttributeError:
        pass  # data was not a data collection; just return it anyway