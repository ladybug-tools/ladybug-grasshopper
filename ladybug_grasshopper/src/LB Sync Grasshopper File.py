# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Sync the Ladybug Tools components in a Grasshopper file with the version of the
components that currently exist in the Grasshopper toolbar.
-
This is useful for updating old Grasshopper definitions to newer plugin versions.
However, this component will sync components regardless of version number or
date, even if the components in the toolbar are of an older version than those
currently on the Grasshopper canvass.
-
Any components that cannot be updated automatically (because their inputs or
outputs have changed) will be circled in red and should be replaced manually.
-

    Args:
        _sync: Set to "True" to have this component to search through the
            current Grasshopper file and sync all Ladybug Tools components
            with the version in the Grasshopper toolbar.
    
    Returns:
        report: Errors, warnings, etc.
"""

ghenv.Component.Name = 'LB Sync Grasshopper File'
ghenv.Component.NickName = 'SyncGHFile'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '5 :: Version'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug_rhino.versioning.gather import gather_canvas_components
    from ladybug_rhino.versioning.diff import sync_component
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _sync:
    # load all of the GHPython userobjects and update the versions
    components = gather_canvas_components(ghenv.Component)
    report_init = []
    for comp in components:
        try:
            report_init.append(sync_component(comp, ghenv.Component))
        except Exception:
            if hasattr(comp, 'Name'):
                msg = 'Failed to Update "{}"'.format(comp.Name)
                print msg
                give_warning(ghenv.Component, msg)
    report = '\n'.join(r for r in report_init if r)
