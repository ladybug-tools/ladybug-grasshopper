# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Export a Ladybug Tools Grasshopper GHPython component as a UserObject that can
be installed on other's machines.
-

    Args:
        _components: A Ladybug Tools GHPython component to be exported. This
            can also be a list of of components to be exported together. Lastly,
            this can be a '*' and all of the Ladybug Tools components on the
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

            * release: You are changing the versions for a new release.
                Bump the major with 1 and set minor and patch to 0.
            * feat: You have added a new feature. Adding a new feature usually
                results in a change in inputs or outputs of the component.
                Bump minor by 1 and set patch to 0.
            * perf: You have improved the component for better performance.
                Similar to adding a feature you should bump the minor by 1 and
                set patch to 0.
            * fix: You have fixed the code inside the component. It results in
                a single bump in patch.
            * docs: You have improved the documentation. No change in version.
            * ignore: This is an exception to the rule and you want the change
                type to be ignored. You should use this option only in rare
                occasional cases.
        _export: Set to True to export the component.
    
    Returns:
        report: Errors, warnings, etc.
"""

ghenv.Component.Name = 'LB Export UserObject'
ghenv.Component.NickName = 'ExportUO'
ghenv.Component.Message = '0.2.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '5 :: Version'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import Grasshopper.Folders as Folders
import Grasshopper.Kernel as gh
import scriptcontext as sc
import os
import shutil


# dictionary to map input values for exposure
exposure_dict = {
    0 : ghenv.Component.Exposure.dropdown,
    1 : ghenv.Component.Exposure.primary,
    2 : ghenv.Component.Exposure.secondary,
    3 : ghenv.Component.Exposure.tertiary,
    4 : ghenv.Component.Exposure.quarternary,
    5 : ghenv.Component.Exposure.quinary,
    6 : ghenv.Component.Exposure.senary,
    7 : ghenv.Component.Exposure.septenary
}


folder_dict = {
    'Ladybug': 'ladybug_grasshopper',
    'Honeybee': 'honeybee_grasshopper_core',
    'HB-Radiance': 'honeybee_grasshopper_radiance',
    'HB-Energy': 'honeybee_grasshopper_energy',
    'Dragonfly': 'dragonfly_grasshopper'
}

UOFOLDER = Folders.UserObjectFolders[0]


# Master array of all identifiers of Ladybug Tools components
ladybug_tools = ('LB', 'HB', 'DF', 'Ladybug', 'Honeybee', 'Butterfly', 'HoneybeePlus')

def is_ladybug_tools(component):
    """Check if a component is a part of Ladybug Tools."""
    return component.Name.split(' ')[0] in ladybug_tools or \
        component.Name.split('_')[0] in ladybug_tools


def get_all_components():
    """Get all of the Ladybug Tools componentsfound on the canvass."""
    components = []
    document = ghenv.Component.OnPingDocument()
    for component in document.Objects:
        if type(component) == type(ghenv.Component):  # GHPython component
            if is_ladybug_tools(component):  # Ladybug Tools component
                components.append(component)

    # remove this sync component from the array
    components = tuple(comp for comp in components if \
                       comp.InstanceGuid != ghenv.Component.InstanceGuid)

    return components


def get_components():
    """Get list of GHPython components that are connected to this component."""
    param = ghenv.Component.Params.Input[0]  # components input
    sources = param.Sources

    if sources.Count == 0:
        # no component is connected
        yield []
    
    for src in sources:
        attr = src.Attributes
        if attr is None or attr.GetTopLevel is None:
            continue

        #  collect components
        component = attr.GetTopLevel.DocObject
        if component is None:
            continue
        if type(component) != type(ghenv.Component):
            # not a GHPython component
            continue

        yield component


def create_userobject(component, move=True):
    """Create UserObject from a component.
    
    Args:
        component: A Grasshopper Python component.
        move: A Boolean to move the component a subdirectory based on
            folder_dict.
    """
    # initiate userobject
    uo = gh.GH_UserObject()
    # set attributes
    uo.Icon = component.Icon_24x24
    try:
        exposure = int(component.AdditionalHelpFromDocStrings)
    except:
        expousre = 1
    uo.Exposure = exposure_dict.get(exposure, 1)
    uo.BaseGuid = component.ComponentGuid
    uo.Description.Name = component.Name
    uo.Description.Description = component.Description
    uo.Description.Category = component.Category
    uo.Description.SubCategory = component.SubCategory

    # save the userobject
    uo.SetDataFromObject(component)
    uo.SaveToFile()

    # move to the assigned folder
    if move:
        ufd = os.path.join(UOFOLDER, folder_dict[comp.Category], 'user_objects')
        ufp = os.path.join(ufd, '%s.ghuser' % comp.Name)
        if not os.path.isdir(ufd):
            # create folder if it is not already created
            os.mkdir(ufd)
        elif os.path.isfile(ufp):
            # remove current userobject
            os.remove(ufp)
        uo.Path = ufp

    uo.SaveToFile()
    return uo


def validate_change_type(c_type):
    assert c_type in ('fix', 'release', 'feat', 'perf', 'docs', 'ignore'), \
        'Invalid change_type input "%s". For valid options' \
        ' see "_change_type_" input description.' % c_type
    return c_type


def get_current_version(comp):
    """Find the current userobject with the same name and get its version."""
    
    # load component from possible folder
    assert comp.Category in folder_dict, \
        'Unknown category: %s. Add category to folder_dict.' % comp.Category

    fp = os.path.join(
        UOFOLDER,
        folder_dict[comp.Category],
        'user_objects',
        '%s.ghuser' % comp.Name
    )

    if os.path.isfile(fp):
        uo = gh.GH_UserObject(fp).InstantiateObject()
        # uo.Message returns None so we have to find it the old school way!
        for lc, line in enumerate(uo.Code.split('\n')):
            if lc > 200:
                # this should never happen for valid userobjects
                raise ValueError(
                    'Failed to find version from UserObject for %s' % uo.Name
                    )
            if line.strip().startswith("ghenv.Component.Message"):
                return line.split("=")[1].strip()[1:-1]
    else:
        # this is no previous version of this userobject
        return None


def break_down_version(semver):
    """Break down semantic version into major, minor, patch."""
    try:
        major, minor, patch = [int(d) for d in semver.strip().split('.')]
    except ValueError:
        raise ValueError(
            '\nInvalid version format: %s\n'
            'You must follow major.minor.patch format with'
            ' 3 integer values' % semver
        )
    
    return major, minor, patch


def validate_version(current_version, new_version, change_type):
    """Validate the change in version."""

    if current_version is None:
        # this is the first time that this component is created
        print('    New component. No change in version: %s' % current_version)
        return True

    x, y, z = break_down_version(current_version)
    break_down_version(new_version)

    msg = '\nFor a \'%s\' the component version should change to %s not %s.' \
        '\nFix the version or select the correct change type and try again.'
    if change_type == 'ignore':
        valid_version = new_version
    elif change_type == 'fix':
        valid_version = '.'.join(str(i) for i in (x, y, z + 1))
    elif change_type == 'feat' or change_type == 'perf':
        valid_version = '.'.join(str(i) for i in (x, y + 1, 0))
    elif change_type == 'release':
        valid_version = '.'.join(str(i) for i in (x + 1, 0, 0))
    elif change_type == 'docs':
        valid_version = '.'.join(str(i) for i in (x, y, z))
    else:
        raise ValueError('Invalid change_type: %s' % change_type)

    assert valid_version == new_version, \
            msg % (change_type, valid_version, new_version)
    
    if current_version == new_version:
        print('    No change in version: %s' % current_version)
    else:
        print('    Version is changed from %s to %s.' % (current_version, new_version))


def export_content(folder, uo):
    """Export UserObject to a folder.
    
    This method generates a ghuser and a py file under user_objects and src
    subfolders.
    """

    # create subfolders if not created
    uo_folder = os.path.join(folder, 'user_objects')
    src_folder = os.path.join(folder, 'src')
    for f in (folder, uo_folder, src_folder):
        if not os.path.isdir(f):
            os.mkdir(f)

    # remove files if already exist
    uo_fp = os.path.join(uo_folder, '%s.ghuser' % uo.Description.Name)
    src_fp = os.path.join(src_folder, '%s.py' % uo.Description.Name)

    # export userobject
    if os.path.isfile(uo_fp):
        os.remove(uo_fp)
    uo.Path = uo_fp
    uo.SaveToFile()

    # export src
    code = uo.InstantiateObject().Code
    if isinstance(code, unicode):
        code = code.encode('utf8','ignore').replace("\r", "")
    with open(src_fp, 'w') as outf:
        outf.write(code)
    print('    UserObject and source code are copied to folder.')


if _export and _folder and len(_components) != 0:
    change_type = validate_change_type(_change_type_)
    coomps_to_export = get_components() if str(_components[0]) != '*' else \
        get_all_components()
    for comp in coomps_to_export:
        print('Processing %s...' % comp.Name)
        current_version = get_current_version(comp)
        validate_version(current_version, comp.Message, change_type)
        uo = create_userobject(comp)
        export_content(_folder, uo)
    cs = gh.GH_ComponentServer.UpdateRibbonUI()
else:
    print('Connect _components and _folder')