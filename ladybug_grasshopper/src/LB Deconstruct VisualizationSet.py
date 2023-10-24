# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Deconstruct a Ladybug VisualizationSet into all of its constituent objects.
_
This includes Context Geometry, Analysis Geometry, and any data sets that are
associated with the analysis geometry. The last one is particularly helpful
for performing analysis in the data associated with a particular visualization.
-

    Args:
        _vis_set: VisualizationSet arguments from any Ladybug Tools component with a vis_set
            output. This can also be the path to a .vsf file that exists on this
            machine (these files are often written with the "LB Dump VisualizationSet"
            component). Lastly, this input can be a custom VisualizationSet that
            has been created with the Ladybug Tools SDK.

    Returns:
        context: A list of geometry objects that constitute the context geometry of the
            VisualizationSet. When the VisualizationSet contains multiple context
            geometry instances, this will be a data tree with one branch for
            each context object.
        analysis: A list of geometry objects that constitute the analysis geometry of the
            VisualizationSet. When the VisualizationSet contains multiple analysis
            geometry instances, this will be a data tree with one branch for
            each analysis object.
        data: A list of numbers that constitue the data set associated with the analysis
            geometry. In the event of multiple data sets assigned to the same
            analysis geometry, this will be a data tree of numbers with one branch
            for each data set. In the event of multiple analysis geometries, this
            will be a nested data tree where the first number in the path matches
            the analysis geometry branch and the last number matches the data set
            number.
"""

ghenv.Component.Name = "LB Deconstruct VisualizationSet"
ghenv.Component.NickName = 'DeconstructVisSet'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the honeybee dependencies
    from ladybug_display.geometry3d import DisplayText3D
    from ladybug_display.visualization import ContextGeometry, AnalysisGeometry
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_display:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.fromobjects import from_geometry
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.visset import process_vis_set
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

TEXT_HORIZ = {'Left': 0, 'Center': 1, 'Right': 2}
TEXT_VERT = {'Top': 0, 'Middle': 3, 'Bottom': 5}


if all_required_inputs(ghenv.Component):
    # extract the VisualizationSet object
    _vs = process_vis_set(_vis_set)

    # loop through the constituient objects and deconstruct them
    context, analysis, data = [], [], []
    for geo_obj in _vs.geometry:
        if isinstance(geo_obj, ContextGeometry):
            con_geos = []
            for g in geo_obj.geometry:
                if not isinstance(g, DisplayText3D):
                    con_geos.append(from_geometry(g.geometry))
                else:
                    t_obj = text_objects(
                        g.text, g.plane, g.height, g.font,
                        TEXT_HORIZ[g.horizontal_alignment],
                        TEXT_VERT[g.vertical_alignment])
                    con_geos.append(t_obj)
            context.append(con_geos)
        elif isinstance(geo_obj, AnalysisGeometry):
            a_geos, data_sets = [], []
            for g in geo_obj.geometry:
                a_geos.append(from_geometry(g))
            for d in geo_obj.data_sets:
                data_sets.append(d.values)
            analysis.append([a_geos])
            data.append(data_sets)

    # convert everything into data trees
    context = list_to_data_tree(context)
    analysis = list_to_data_tree(analysis)
    data = list_to_data_tree(data)
