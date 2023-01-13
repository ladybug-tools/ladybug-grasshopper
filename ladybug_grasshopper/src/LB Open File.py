# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Open a file in whatever program is associated with the file extension.
This can be used to open simulation files in particular applications (eg. opening
an OSM file in the OpenStudio Application).
-

    Args:
        _file_path: Full path to a file to be opened.
    
    Returns:
        report: Reports, errors, warnings, etc.
"""

ghenv.Component.Name = 'LB Open File'
ghenv.Component.NickName = 'OpenFile'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

import os
import subprocess

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check that the file exists
    assert os.path.exists(_file_path), \
        'No file was found at: {}'.format(_file_path)
    _file_path = _file_path.replace('/', '\\') if os.name == 'nt' else _file_path
    os.startfile(_file_path)
