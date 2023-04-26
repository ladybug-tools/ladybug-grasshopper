# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Dragonfly.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
This component updates the Ladybug Tools core libraries and grasshopper components
to either the latest development version available (default) or to a specific
version of the grasshopper plugin.
_
The input version_ does not need to be newer than the current installation and can
be older but grasshopper plugin versions less than 0.3.0 are not supported.
A list of all versions of the Grasshopper plugin and corresponding release notes
can be found at: https://github.com/ladybug-tools/lbt-grasshopper/releases
-
    Args:
        _update: Set to True to update your installation of Ladybug Tools to the
            latest development version or to be at the version specified below.
        version_: An optional text string for the version of the grasshopper
            plugin which you would like to update to. The input should contain
            only integers separated by two periods (eg. 1.0.0). The version does
            not need to be newer than the current installation and can be older
            but grasshopper plugin versions less than 0.3.0 are not supported.
            A list of all versions of the Grasshopper plugin can be found
            here - https://github.com/ladybug-tools/lbt-grasshopper/releases

    Returns:
        Vviiiiiz!: !!!
"""

ghenv.Component.Name = 'LB Versioner'
ghenv.Component.NickName = 'Versioner'
ghenv.Component.Message = '1.6.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '5 :: Version'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os
import tempfile
import subprocess

try:
    from ladybug.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.versioning.diff import current_userobject_version
    from ladybug_rhino.versioning.change import latest_github_version
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning, \
        give_popup_message, is_user_admin
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _update:
    # get the paths to the executables
    lb_rhino_exe = os.path.join(folders.python_scripts_path, 'ladybug-rhino.exe') \
        if os.name == 'nt' else os.path.join(folders.python_scripts_path, 'ladybug-rhino')
    executor_path = os.path.join(
        folders.ladybug_tools_folder, 'grasshopper', 'ladybug_grasshopper_dotnet',
        'Ladybug.Executor.exe')

    # run the command to update everything
    if os.name == 'nt' and os.path.isfile(executor_path) and \
            'Program Files' in executor_path and not is_user_admin():
        cmd = [
            executor_path, folders.python_exe_path,
            '-m ladybug_rhino change-installed-version'
        ]
    else:
        cmd = [lb_rhino_exe, 'change-installed-version']
    if version_ is not None:
        cmd.extend(['--version', version_])
    use_shell = True if os.name == 'nt' else False
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=use_shell)
    cmd_output = process.communicate()  # ensure that the canvas is frozen
    stdout = cmd_output[0]
    print(stdout)
    if 'Error' in stdout:
        if 'ladybug-rhino.exe' not in stdout:
            raise ValueError(stdout)
        else:  # recent Windows permission issue; reinstall ladybug-rhino
            cmd = cmds = [folders.python_exe_path, '-m', 'pip', 'install', 'ladybug-rhino', '-U']
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=use_shell)
            cmd_output = process.communicate()  # ensure that the canvas is frozen

    # give a completion message
    if version_ is None:
        temp_dir = tempfile.gettempdir()
        version_ = latest_github_version('lbt-grasshopper', temp_dir)
    version = 'LATEST' if version_ is None else version_
    success_msg = 'Change to Version {} Successful!'.format(version)
    restart_msg = 'RESTART RHINO to load the new components + library.'
    sync_msg = 'The "LB Sync Grasshopper File" component can be used\n' \
        'to sync Grasshopper definitions with your new installation.'
    for msg in (success_msg, restart_msg, sync_msg):
        print (msg)
    give_popup_message('\n'.join([restart_msg, sync_msg]), success_msg)

    # do a check to see if the versioner has, itself, been updated
    new_version = current_userobject_version(ghenv.Component)
    current_version = ghenv.Component.Message
    if new_version != current_version:
        msg = 'The Versioner component has, itself, been changed between the\n' \
            'current version ({}) and the version you are changing to ({}).\n' \
            'It is recommended that you resart Rhino and run the new Versioner\n' \
            'coponent to ensure that everything is consistent.'.format(
                current_version, new_version)
        print (msg)
        give_warning(ghenv.Component, msg)
else:  # give a message to the user about what to do
    print ('Make sure you are connected to the internet and set _update to True!')
