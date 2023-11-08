# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Export a Ladybug Tools Grasshopper GHPython component as a UserObject that can
be installed on other's machines.
-

    Args:
        _components: A Ladybug Tools GHPython component to be exported. This
            can also be a list of of components to be exported together. Lastly,
            this can be a "*" and all of the Ladybug Tools components on the
            Grasshopper canvass will be exported.
        _folder: Full path to folder to copy the updated UserObject and the
            source code. It is usually path to where you have cloned the
            repository from GitHub. Exported contents will be created under src
            and userobject folders.
        _change_type_: One of the values listed below based on the type of
            change made to the component. Export component will validate the
            version of the newly created UserObject against the version of the
            current installed UserObject with the same name based on the change
            type. If an older version of the component does not exist the
            current version of the component will be used. The version is
            structured as major.minor.patch. (Default: fix)
            _
            * release: You are changing the versions for a new release.
                Bump the major with 1 and set minor and patch to 0.
            _
            * feat: You have added a new feature. Adding a new feature usually
                results in a change in inputs or outputs of the component.
                Bump minor by 1 and set patch to 0.
            _
            * perf: You have improved the component for better performance.
                Similar to adding a feature you should bump the minor by 1 and
                set patch to 0.
            _
            * fix: You have fixed the code inside the component. It results in
                a single bump in patch.
            _
            * docs: You have improved the documentation. No change in version.
            _
            * ignore: This is an exception to the rule and you want the change
                type to be ignored. You should use this option only in rare
                occasional cases.
        _export: Set to True to export the component.

    Returns:
        report: Errors, warnings, etc.
"""

ghenv.Component.Name = 'LB Export UserObject'
ghenv.Component.NickName = 'ExportUO'
ghenv.Component.Message = '1.7.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '5 :: Version'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug_rhino.versioning.gather import gather_canvas_components, \
        gather_connected_components
    from ladybug_rhino.versioning.diff import validate_change_type
    from ladybug_rhino.versioning.export import export_component, refresh_toolbar
    from ladybug_rhino.grasshopper import turn_off_old_tag
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
turn_off_old_tag(ghenv.Component)  # turn off the OLD tag in Rhino 8


if _export and _folder and len(_components) != 0:
    change_type = validate_change_type(_change_type_)
    comps_to_export = gather_connected_components(ghenv.Component) \
        if str(_components[0]) != '*' \
        else gather_canvas_components(ghenv.Component)
    for comp in comps_to_export:
        print('Processing %s...' % comp.Name)
        export_component(_folder, comp, _change_type_)
    refresh_toolbar()  # try to update the toolbar
else:
    print('Connect _components and _folder')
