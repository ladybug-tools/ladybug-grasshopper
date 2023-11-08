# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Preview a VisualizationSet from any component with a vis_set output.
_
The VisualizationSet is often a much more detailed view of the geometry that
the component typically generates and includes features like recommended line
weights/types, display modes (eg. wireframe vs. shaded), transparency, and more.
-

    Args:
        _vis_set: VisualizationSet arguments from any Ladybug Tools component with a vis_set
            output. This can also be the path to a .vsf file that exists on this
            machine (these files are often written with the "LB Dump VisualizationSet"
            component). Lastly, this input can be a custom VisualizationSet that
            has been created with the Ladybug Tools SDK.
        legend_par_: Optional legend parameters from the "LB Legend Parameters" component,
            which will overwrite the existing legend parameters on the input
            Visualization Set.
        leg_par2d_: Optional 2D LegendParameters from the "LB Legend Parameters 2D"
            component, which will be used to customize a legend in the plane
            of the screen so that it functions like a head-up display (HUD).
            If unspecified, the VisualizationSet will be rendered with 3D
            legends in the Rhino scene much like the other native Ladybug
            Tools components.
        data_set_: Optional text or an integer to select a specific data set from analysis
            geometries within the Visualization Set. Note that this input only has
            meaning for Visualization Sets that contain multiple data sets assigned
            to the same geometry. When using an integer, this will refer to the
            index of the data set to be visualized (starting with 0). When using
            text, this will refer to the name of the data type for the data set
            to be displayed.

    Returns:
        vs: A VisualizationSet object that can be baked into the Rhino document by
            running "Bake" on this component or written to a standalone file
            using the "LB Dump VisualizationSet" component.
"""

from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs

class MyComponent(component):
    
    def __init__(self):
        super(MyComponent,self).__init__()
        self.vis_con = None
        self.vs_goo = None
    
    def RunScript(self, _vis_set, legend_par_, leg_par2d_, data_set_):
        ghenv.Component.Name = 'LB Preview VisualizationSet'
        ghenv.Component.NickName = 'VisSet'
        ghenv.Component.Message = '1.7.0'
        ghenv.Component.Category = 'Ladybug'
        ghenv.Component.SubCategory = '4 :: Extra'
        ghenv.Component.AdditionalHelpFromDocStrings = '1'
        
        try:
            from ladybug_display.visualization import AnalysisGeometry
        except ImportError as e:
            raise ImportError('\nFailed to import ladybug_display:\n\t{}'.format(e))
        
        try:
            from ladybug_rhino.grasshopper import all_required_inputs, objectify_output
            from ladybug_rhino.preview import VisualizationSetConverter
            from ladybug_rhino.visset import VisSetGoo, process_vis_set
        except ImportError as e:
            raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
        
        
        if all_required_inputs(ghenv.Component):
            # process the input visualization set
            if len(_vis_set) == 1:
                vis_set = _vis_set[0]
            else:
                if hasattr(_vis_set[0], 'data'):
                    vis_set = objectify_output(
                        'Multiple Vis Set Args', [obj.data for obj in _vis_set])
                else:
                    vis_set = objectify_output(
                        'Multiple Vis Sets', [[obj] for obj in _vis_set])
            vis_set_obj = process_vis_set(vis_set)
            
            # process the connected legend parameters
            if legend_par_ is not None:
                for geo in vis_set_obj:
                    if isinstance(geo, AnalysisGeometry):
                        for data in geo.data_sets:
                            # override legend properties if they are specified
                            if legend_par_.min is not None:
                                data.legend_parameters.min = legend_par_.min
                            if legend_par_.max is not None:
                                data.legend_parameters.max = legend_par_.max
                            if not legend_par_.are_colors_default:
                                data.legend_parameters.colors = legend_par_.colors
                            if not legend_par_.is_segment_count_default:
                                data.legend_parameters.segment_count = \
                                    legend_par_.segment_count
                            if data.data_type is not None:
                                unit = data.unit if data.unit else data.data_type.units[0]
                                data.legend_parameters.title = \
                                    '{} ({})'.format(data.data_type.name, unit) \
                                    if not legend_par_.vertical else unit
                            # set the other genreic legend parameter properties
                            data.legend_parameters.continuous_legend = \
                                legend_par_.continuous_legend
                            data.legend_parameters.decimal_count = \
                                legend_par_.decimal_count
                            data.legend_parameters.include_larger_smaller = \
                                legend_par_.include_larger_smaller
                            data.legend_parameters.font = legend_par_.font
                            data.legend_parameters.vertical = legend_par_.vertical
                            # override any 3D geometry properties
                            if not legend_par_.is_base_plane_default:
                                data.legend_parameters.base_plane = \
                                    legend_par_.base_plane
                            if not legend_par_.is_segment_height_default:
                                data.legend_parameters.segment_height = \
                                    legend_par_.segment_height
                            if not legend_par_.is_segment_width_default:
                                data.legend_parameters.segment_width = \
                                    legend_par_.segment_width
                            if not legend_par_.is_text_height_default:
                                data.legend_parameters.text_height = \
                                    legend_par_.text_height
            # process connected 2D legend parameters
            if leg_par2d_ is None:
                leg3d, leg2d = True, False
            else:
                leg3d, leg2d = False, True
                for geo in vis_set_obj:
                    if isinstance(geo, AnalysisGeometry):
                        for data in geo.data_sets:
                            data.legend_parameters.properties_2d = leg_par2d_
            # process the active data_set_ if it is specified
            if data_set_ is not None:
                try:  # data set is an integer referring to an index
                    data_set_ = int(data_set_)
                except ValueError:
                    pass  # data set is text referring to the data type
                for geo in vis_set_obj:
                    if isinstance(geo, AnalysisGeometry):
                        if isinstance(data_set_, int):
                            if data_set_ < len(geo.data_sets):
                                geo.active_data = data_set_
                        else:
                            for i, dat in enumerate(geo.data_sets):
                                if str(dat.data_type) == data_set_:
                                    geo.active_data = i
            self.vis_con = VisualizationSetConverter(vis_set_obj, leg3d, leg2d)
            self.vs_goo = VisSetGoo(vis_set_obj)
        else:
            self.vis_con = None
            self.vs_goo = None
        
        # return the bake-able version of the visualization set 
        return self.vs_goo
    
    def DrawViewportWires(self, args):
        try:
            if self.vis_con is not None:
                # get the DisplayPipeline from the event arguments
                display = args.Display
                
                # for each object to be rendered, pass the drawing arguments
                for draw_args in self.vis_con.draw_3d_text:
                    display.Draw3dText(*draw_args)
                for draw_args in self.vis_con.draw_mesh_wires:
                    display.DrawMeshWires(*draw_args)
                for draw_args in self.vis_con.draw_mesh_vertices:
                    display.DrawMeshVertices(*draw_args)
                for draw_args in self.vis_con.draw_point:
                    display.DrawPoint(*draw_args)
                for draw_args in self.vis_con.draw_arrow:
                    display.DrawArrow(*draw_args)
                for draw_args in self.vis_con.draw_brep_wires:
                    display.DrawBrepWires(*draw_args)
                for draw_args in self.vis_con.draw_line:
                    display.DrawLine(*draw_args)
                for draw_args in self.vis_con.draw_patterned_line:
                    display.DrawPatternedLine(*draw_args)
                for draw_args in self.vis_con.draw_patterned_polyline:
                    display.DrawPatternedPolyline(*draw_args)
                for draw_args in self.vis_con.draw_curve:
                    display.DrawCurve(*draw_args)
                for draw_args in self.vis_con.draw_circle:
                    display.DrawCircle(*draw_args)
                for draw_args in self.vis_con.draw_arc:
                    display.DrawArc(*draw_args)
                for draw_args in self.vis_con.draw_sphere:
                    display.DrawSphere(*draw_args)
                for draw_args in self.vis_con.draw_cone:
                    display.DrawCone(*draw_args)
                for draw_args in self.vis_con.draw_cylinder:
                    display.DrawCylinder(*draw_args)
                for draw_args in self.vis_con.draw_2d_text:
                    display.Draw2dText(*draw_args)
                for draw_args in self.vis_con.draw_sprite:
                    display.DrawSprite(*draw_args)
        except Exception, e:
            System.Windows.Forms.MessageBox.Show(str(e), "script error")
    
    def DrawViewportMeshes(self, args):
        try:
            if self.vis_con is not None:
                # get the DisplayPipeline from the event arguments
                display = args.Display
                
                # for each object to be rendered, pass the drawing arguments
                for draw_args in self.vis_con.draw_mesh_false_colors:
                    display.DrawMeshFalseColors(draw_args)
                for draw_args in self.vis_con.draw_mesh_shaded:
                    display.DrawMeshFalseColors(draw_args[0])
                for draw_args in self.vis_con.draw_brep_shaded:
                    display.DrawBrepShaded(*draw_args)
        except Exception, e:
            System.Windows.Forms.MessageBox.Show(str(e), "script error")
    
    def get_ClippingBox(self):
        if self.vis_con is not None:
            return self.vis_con.bbox
        else:
            return Rhino.Geometry.BoundingBox()
