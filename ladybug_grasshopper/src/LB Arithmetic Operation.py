# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Perform simple arithmetic operations between Data Collections. For example,
adding two Data Collections together, subtracting one collection from another,
or multiplying/dividing a data in a collection by a factor.
-
Note that Data Collections must be aligned in order for this component to run
successfully.
-
Using this component will often be much faster and more elegant compared to
deconstructing the data collection, performing the operation with native
Grasshopper components, and rebuilding the collection.
-

    Args:
        _data_1: The first Data Collection in the operation. If the operator is
            not commutative, this collection comes before the operator. For
            example, in subtraction, this is the collection being subtracted from.
            This can also be a list of Data Collections that align with _data_2.
            It cal also be a single number that will be added, multiplied, etc.
            to all of _data_2.
        _data_2: The second Data Collection in the operation. If the operator is
            not commutative, this collection comes after the operator. For
            example, in subtraction, this is the collection being subtracted with.
            This can also be a list of Data Collections that align with _data_1.
            It cal also be a single number that will be added, multiplied, etc.
            to all of _data_1.
        _operator_: Text for the operator to use between the two Data Collections.
            Valid examples include (+, -, *, /). By default this is + for addition.
        type_: Optional text for a new "type" key in the Data Collection's metadata.
            This will usually show up in most Ladybug visualiztions and it should
            usually change for most types of operations.
    
    Returns:
        data: A Ladybug data collection object derived from the operation between
            the two data inputs.
"""

ghenv.Component.Name = "LB Arithmetic Operation"
ghenv.Component.NickName = 'ArithOp'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    import ladybug.datatype
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:
    from itertools import izip as zip  # python 2
except ImportError:
    pass  # some future time when GHPython upgrades to python 3


if all_required_inputs(ghenv.Component):
    # build the arithmetic statement
    operator = '+' if _operator_ is None else _operator_
    statement = 'data_1 {} data_2'.format(operator)

    # perform the arithmetic operation
    data = []
    for i, data_1 in enumerate(_data_1):
        data_2 = longest_list(_data_2, i)
        data_1 = float(data_1) if isinstance(data_1, str) else data_1
        data_2 = float(data_2) if isinstance(data_2, str) else data_2
        result = eval(statement, {'data_1': data_1, 'data_2': data_2})

        # try to replace the data collection type
        try:
            result = result.duplicate()
            if type_:
                result.header.metadata['type'] = type_
            elif 'type' in result.header.metadata:  # infer data type from units
                d_unit = result.header.unit
                for key in ladybug.datatype.UNITS:
                    if d_unit in ladybug.datatype.UNITS[key]:
                        base_type = ladybug.datatype.TYPESDICT[key]()
                        result.header.metadata['type'] = str(base_type)
                        break
                else:
                    result.header.metadata['type'] = 'Unknown Data Type'
        except AttributeError:
            pass  # result was not a data collection; just return it anyway
        data.append(result)