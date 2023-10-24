# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Dump any Ladybug data collections into a file. You can use "LB Load Data" component
to load the data collections from the file back into Grasshopper.
-

    Args:
        _data: A list of Ladybug data collections to be written to a file.
        _format_: Text or an integer to set the format of the output file.
            Choose from the options below. (Default: CSV).
                * 0 = CSV - Compact, human-readable, importable to spreadsheets
                * 1 = JSON - Cross-language and handles any types of collections
                * 2 = PKL - Compressed format only readable with Python
        _name_: A name for the file to which the data collections will be
            written. (Default: 'data').
        _folder_: An optional directory into which the data collections will be
            written.  The default is set to a user-specific simulation folder.
        _dump: Set to "True" to save the data collection to a file.

    Returns:
        report: Errors, warnings, etc.
        data_file: The path of the file where the data collections are saved.
"""

ghenv.Component.Name = 'LB Dump Data'
ghenv.Component.NickName = 'DumpData'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

import os

try:
    from ladybug.datautil import collections_to_csv, collections_to_json, \
        collections_to_pkl
    from ladybug.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

FORMAT_MAP = {
    '0': 'csv',
    '1': 'json',
    '2': 'pkl',
    'csv': 'csv',
    'json': 'json',
    'pkl': 'pkl'
}


if all_required_inputs(ghenv.Component) and _dump:
    # set the component defaults
    name = _name_ if _name_ is not None else 'data'
    home_folder = os.getenv('HOME') or os.path.expanduser('~')
    folder = _folder_ if _folder_ is not None else \
        os.path.join(home_folder, 'simulation')
    file_format = 'csv' if _format_ is None else FORMAT_MAP[_format_.lower()]

    # write the data into the appropriate format
    if file_format == 'csv':
        try:
            data_file = collections_to_csv(_data, folder, name)
        except AssertionError as e:
            raise ValueError('{}\nTry using the JSON or PKL format.'.format(e))
    elif file_format == 'json':
        data_file = collections_to_json(_data, folder, name)
    elif file_format == 'pkl':
        data_file = collections_to_pkl(_data, folder, name)
