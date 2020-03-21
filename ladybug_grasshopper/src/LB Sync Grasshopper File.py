# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


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
ghenv.Component.Message = '0.1.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '5 :: Version'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import Grasshopper.Kernel as gh
from Grasshopper.Folders import UserObjectFolders
import System.Drawing as sd
import os


# Master array of all identifiers of Ladybug Tools components
ladybug_tools = ('LB', 'HB', 'DF', 'Ladybug', 'Honeybee', 'Butterfly', 'HoneybeePlus')

def is_ladybug_tools(component):
    """Check if a component is a part of Ladybug Tools."""
    return component.Name.split(' ')[0] in ladybug_tools or \
        component.Name.split('_')[0] in ladybug_tools


def collect_ladybug_tools_components(document=None):
    """Collect all of the Ladybug Tools GHPython components on the Grasshopper canvass.
    
    Args:
        document: A Grasshopper document to be arched for components. The current
            document will be used if None.
    """
    components = []
    document = document or ghenv.Component.OnPingDocument()

    # check if there is any cluster and collect the objects inside clusters
    for obj in document.Objects:
        if type(obj) == gh.Special.GH_Cluster:
            cluster_doc = obj.Document("")
            if not cluster_doc:
                continue
            for cluster_obj in  cluster_doc.Objects:
                if type(cluster_obj) == type(ghenv.Component)and \
                        is_ladybug_tools(cluster_obj):
                    if cluster_obj.Locked:
                        continue
                    components.append(cluster_obj)
        elif type(obj) == type(ghenv.Component)and is_ladybug_tools(obj):
            if obj.Locked:
                continue
            components.append(obj)

    # remove this sync component from the array
    components = tuple(comp for comp in components if \
                       comp.InstanceGuid != ghenv.Component.InstanceGuid)

    return components


def has_version_changed(uo, component):
    """Check if the version of a user object has changed."""
    return not uo.Message == component.Message


def compare_port(p1, p2):
    """Compare two component port objects and return True if they are equal.

    Args:
        p1: The first port object.
        p2: The second port object.
    """
    if hasattr(p1, 'TypeHint'):
        if p1.Name != p2.Name:
            return False
        elif p1.TypeHint.TypeName != p2.TypeHint.TypeName:
            return False
        elif str(p1.Access) != str(p2.Access):
            return False
        else:
            return True
    else:
        # output
        if p1.Name != p2.Name:
            return False
        else:
            return True        


def compare_ports(c1, c2):
    """Compare all of the ports of two components and return True if they are equal.

    Args:
        c1: The first component object.
        c2: The second component object.
    """
    for i in xrange(c1.Params.Input.Count):
        if not compare_port(c1.Params.Input[i], c2.Params.Input[i]):
            return True

    for i in xrange(c1.Params.Output.Count):
        if not compare_port(c1.Params.Output[i], c2.Params.Output[i]):
            return True

    return False


def input_output_changed(uo, component):
    """Check if inputs or outputs have changed between two components."""
    if uo.Params.Input.Count != component.Params.Input.Count:
        return True
    elif uo.Params.Output.Count != component.Params.Output.Count:
        return True

    return compare_ports(uo, component)


def insert_new_uo(uo, component, doc):
    """Insert a new user object next to an existing one in the Grasshopper doc.

    Args:
        uo: The user object component instance
        component: The outdated component where the userobject will be inserted
            next to.
        cod: The Grasshopper document object.
    """
    # use component to find the location
    x = component.Attributes.Pivot.X + 30
    y = component.Attributes.Pivot.Y - 20

    # insert the new one
    uo.Attributes.Pivot = sd.PointF(x, y)
    doc.AddObject(uo , False, 0)


def mark_component(doc, comp, note=None):
    """Put a circular red group areound a component and label it with a note."""
    note = note or 'There is a change in the input or output! ' \
        'Replace this component manually.'
    grp = gh.Special.GH_Group()
    grp.CreateAttributes()
    grp.Border = gh.Special.GH_GroupBorder.Blob
    grp.AddObject(comp.InstanceGuid)
    grp.Colour = sd.Color.IndianRed
    grp.NickName = note
    doc.AddObject(grp, False);    
    return True


def update_component(component, uofolder):
    """Update a component using its version in the user object folder."""

    # identify the correct user object sub-folder to which the component belongs
    if str(component.Name).startswith('LB'):  # ladybug [+]
        fp = os.path.join(uofolder, 'ladybug_grasshopper', 'user_objects',
                          '%s.ghuser' % component.Name)
    elif str(component.Name).startswith('HB'):  # honeybee[+]
        if str(component.Category) == 'Honeybee':
            fp = os.path.join(uofolder, 'honeybee_grasshopper_core', 'user_objects',
                              '%s.ghuser' % component.Name)
        elif str(component.Category) == 'HB-Energy':
            fp = os.path.join(uofolder, 'honeybee_grasshopper_energy', 'user_objects',
                              '%s.ghuser' % component.Name)
        elif str(component.Category) == 'HB-Radiance':
            fp = os.path.join(uofolder, 'honeybee_grasshopper_radiance', 'user_objects',
                              '%s.ghuser' % component.Name)
    elif str(component.Name).startswith('DF'):  # dragonfly [+]
        fp = os.path.join(uofolder, 'dragonfly_grasshopper', 'user_objects',
                          '%s.ghuser' % component.Name)
    elif str(component.Name).startswith('Ladybug'):  # ladybug legacy
        fp = os.path.join(uofolder, 'Ladybug', '%s.ghuser' % component.Name)
    elif str(component.Name).startswith('Honeybee'):  # honeybee legacy
        fp = os.path.join(uofolder, 'Honeybee', '%s.ghuser' % component.Name)
    elif str(component.Name).startswith('HoneybeePlus'):  # old honeybee [+]
        fp = os.path.join(uofolder, 'HoneybeePlus', '%s.ghuser' % component.Name)
    else:  # unidentified plugin; see if we can find it in the root
        fp = os.path.join(uofolder, '%s.ghuser' % component.Name)
        if not os.path.isfile(fp):
            category = str(component.Name).split('_')[0]
            fp = os.path.join(uofolder, category, '%s.ghuser' % component.Name)

    if not os.path.isfile(fp):
        warning = 'Failed to find the userobject for %s' % component.Name
        give_warning(ghenv.Component, warning)
        return False

    # the the instance of the user object
    uo = gh.GH_UserObject(fp).InstantiateObject()

    # check to see if the version of the userobject has changed
    if not has_version_changed(uo, component):
        return False 

    # the version has changed
    component.Code = uo.Code

    # define the callback function
    def call_back(document):
        component.ExpireSolution(False)

    # update the solution
    doc.ScheduleSolution(2,
        gh.GH_Document.GH_ScheduleDelegate(call_back))

    # check if the inputs or outputs have changed
    if input_output_changed(uo, component):
        insert_new_uo(uo, component, doc)
        mark_component(doc, component)  # mark component with a warning to the user
        return 'Cannot update %s. Replace manually.' % component.Name

    return 'Updated %s' % component.Name


if _sync:
    # find the Grasshopper UserObjects folder and get the current canvass
    uofolder = UserObjectFolders[0]
    doc = ghenv.Component.OnPingDocument()
    
    # load all of the GHPython userobjects and update the versions
    components = collect_ladybug_tools_components(doc)
    report_init = (update_component(comp, uofolder) for comp in components)
    report = '\n'.join(r for r in report_init if r)