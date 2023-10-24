# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Load Ladybug data collections from a CSV, JSON, or PKL file.
-

    Args:
        _data_file: A file path to a CSV, JSON or PKL file from which data collections
            will be loaded.
        _load: Set to "True" to load the data collections from the _data_file.

    Returns:
        report: Reports, errors, warnings, etc.
        hb_objs: A list of honeybee objects that have been re-serialized from
            the input file.
"""

ghenv.Component.Name = 'LB Load Data'
ghenv.Component.NickName = 'LoadData'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

try:
    from ladybug.datautil import collections_from_csv, collections_from_json, \
        collections_from_pkl
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _load:
    # load the data from the appropriate format
    lower_file = _data_file.lower()
    if lower_file.endswith('.csv'):
        data = collections_from_csv(_data_file)
    elif lower_file.endswith('.json'):
        data = collections_from_json(_data_file)
    elif lower_file.endswith('.pkl'):
        data = collections_from_pkl(_data_file)
    else:
        raise ValueError(
            'Could not recognize the file extension of: {}'.format(_data_file))
