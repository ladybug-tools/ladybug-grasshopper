# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Drop suggested Ladybug Tools components into a Grasshopper file for every
Legacy Ladybug + Honeybee component on the canvas.
-
All existing LBT and native Grasshopper components will be left as they are and
only the Legacy components will be circled in Red and have the suggested LBT
component placed next to them (if applicable). Note that, after this component
runs, you must then connect the new LBT components to the others and delete the
Legacy components.
-
Where applicable, each red circle will have a message about how the LBT component
differs from the Legacy one or if there may be a more appropirate LBT component
in the future. Also note that some Legacy workflows have been heavily refactored
since Legacy, meaning a different number of components may be necessary to achieve
the same thing (typically fewer in LBT than Legacy, meaning some LEgacy components
should be deleted without replacement).
-

    Args:
        _update: Set to "True" to have this component to search through the current
            Grasshopper file and drop suggested Ladybug Tools components
            for every Legacy Ladybug + Honeybee component on the canvas.

    Returns:
        report: Errors, warnings, etc.
"""

ghenv.Component.Name = 'LB Legacy Updater'
ghenv.Component.NickName = 'Legacy'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '5 :: Version'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug_rhino.versioning.gather import gather_canvas_components
    from ladybug_rhino.versioning.legacy import suggest_new_component
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _update:
    # load all of the GHPython userobjects and update the versions
    components = gather_canvas_components(ghenv.Component)
    report_init = []
    for comp in components:
        try:
            report_init.append(suggest_new_component(comp, ghenv.Component))
        except Exception:
            if hasattr(comp, 'Name'):
                msg = 'Failed to Update "{}"'.format(comp.Name)
                print(msg)
                give_warning(ghenv.Component, msg)
    print('\n'.join(r for r in report_init if r))
