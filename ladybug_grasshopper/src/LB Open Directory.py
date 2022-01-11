# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Open a file's directory in Windows Explorer or Mac Finder.
This is useful for understanding weather data or simulation files.
-

    Args:
        _file_path: Full path to a file or directory to be opened in Explorer/Finder.
    
    Returns:
        report: Reports, errors, warnings, etc.
"""

ghenv.Component.Name = 'LB Open Directory'
ghenv.Component.NickName = 'OpenDir'
ghenv.Component.Message = '1.4.0'
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
        'No file or directory was found at: {}'.format(_file_path)
    folder = _file_path if os.path.isdir(_file_path) else os.path.dirname(_file_path)

    # open the file in explorer or finder
    if os.name == 'nt':  # we are on Windows
        folder = folder.replace('/', '\\')
        subprocess.Popen('explorer.exe ' + folder)
    else:  # assume we are on Mac
        subprocess.call(['open', '-R', _file_path])
