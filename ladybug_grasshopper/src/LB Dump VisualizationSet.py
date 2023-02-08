# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Dump a Ladybug VisualiztionSet into a file.
_
The "LB Preview VisualizationSet" component can be used to visualize the content
from the file back into Grasshopper.
-

    Args:
        _vis_set: A VisualizationSet object to be written to a file. This can also be
            VisualizationSet arguments from any Ladybug Tools component with
            a vis_set output.
        _format_: Text or an integer to set the format of the output file.
            Choose from the options below. (Default: JSON).
                * 0 = JSON - Cross-language and handles any types of collections
                * 1 = PKL - Compressed format only readable with Python
        _name_: A name for the file to which the VisualizationSet will be written.
            The default is derived from the identifier of the visualization set.
        _folder_: An optional directory into which the VisualizationSet will be
            written.  The default is set to a user-specific simulation folder.
        _dump: Set to "True" to save the VisualizationSet to a file.

    Returns:
        report: Errors, warnings, etc.
        vs_file: The path of the file where the VisualisationSet is saved. The
            "LB Preview VisualizationSet" component can be used to visualize
            the content from the file back into Grasshopper.
"""

ghenv.Component.Name = 'LB Dump VisualizationSet'
ghenv.Component.NickName = 'DumpVisSet'
ghenv.Component.Message = '1.6.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import os

try:
    from ladybug.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.visset import process_vis_set
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

FORMAT_MAP = {
    '0': 'json',
    '1': 'pkl',
    'json': 'json',
    'pkl': 'pkl'
}


if all_required_inputs(ghenv.Component) and _dump:
    # extract the VisualizationSet object
    _vs = process_vis_set(_vis_set)

    # set the component defaults
    name = _name_ if _name_ is not None else _vs.identifier
    home_folder = os.getenv('HOME') or os.path.expanduser('~')
    folder = _folder_ if _folder_ is not None else \
        os.path.join(home_folder, 'simulation')
    file_format = 'json' if _format_ is None else FORMAT_MAP[_format_.lower()]

    # write the data into the appropriate format
    if file_format == 'json':
        vs_file = _vs.to_json(name, folder)
    elif file_format == 'pkl':
        vs_file = _vs.to_pkl(name, folder)
