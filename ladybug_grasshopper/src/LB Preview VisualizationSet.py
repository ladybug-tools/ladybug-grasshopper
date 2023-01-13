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
        leg_par2d_: Optional 2D LegendParameters from the "LB Legend Parameters 2D"
            component, which will be used to customize a legend in the plane
            of the screen so that it functions like a head-up display (HUD).
            If unspecified, the VisualizationSet will be rendered with 3D
            legends in the Rhino scene much like the other native Ladybug
            Tools components.

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
    
    def RunScript(self, _vis_set, leg_par2d_):
        ghenv.Component.Name = 'LB Preview VisualizationSet'
        ghenv.Component.NickName = 'VisSet'
        ghenv.Component.Message = '1.5.5'
        ghenv.Component.Category = 'Ladybug'
        ghenv.Component.SubCategory = '4 :: Extra'
        ghenv.Component.AdditionalHelpFromDocStrings = '1'
        
        try:
            from ladybug_display.visualization import VisualizationSet, AnalysisGeometry
        except ImportError as e:
            raise ImportError('\nFailed to import ladybug_display:\n\t{}'.format(e))
        
        try:
            from ladybug_rhino.grasshopper import all_required_inputs, \
                objectify_output, de_objectify_output
            from ladybug_rhino.preview import VisualizationSetConverter
            from ladybug_rhino.bakeobjects import VisSetGoo
        except ImportError as e:
            raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
        
        
        def process_vis_set(vis_set):
            """Process various different types of VisualizationSet inputs.
        
            This includes VisualizationSet files, classes that have to_vis_set methods
            on them, and objects containing arguments for to_vis_set methods
            """
            if isinstance(vis_set, VisualizationSet):
                return vis_set
            elif isinstance(vis_set, str):  # assume that it's a file
                return VisualizationSet.from_file(vis_set)
            elif hasattr(vis_set, 'to_vis_set'):  # an object with a method to be called
                return vis_set.to_vis_set()
            elif hasattr(vis_set, 'data'):  # an object to be decoded
                args_list = de_objectify_output(vis_set)
                if isinstance(args_list[0], (list, tuple)):  # a list of VisaulizationSets
                    base_set = args_list[0][0].to_vis_set(*args_list[0][1:])
                    for next_vis_args in args_list[1:]:
                        for geo_obj in next_vis_args[0].to_vis_set(*next_vis_args[1:]):
                            base_set.add_geometry(geo_obj)
                    return base_set
                else:  # a single list of arguments for to_vis_set
                    return args_list[0].to_vis_set(*args_list[1:])
            else:
                msg = 'Input _vis_set was not recognized as a valid input.'
                raise ValueError(msg)
        
        
        if all_required_inputs(ghenv.Component):
            # process the input visualization set
            if len(_vis_set) == 1:
                vis_set = _vis_set[0]
            else:
                vis_set = objectify_output(
                    'Multiple Vis Sets', [[obj] for obj in _vis_set])
            vis_set_obj = process_vis_set(vis_set)
            # process connected 2D legend parameters
            if leg_par2d_ is None:
                leg3d, leg2d = True, False
            else:
                leg3d, leg2d = False, True
                for geo in vis_set_obj:
                    if isinstance(geo, AnalysisGeometry):
                        for data in geo.data_sets:
                            data.legend_parameters.properties_2d = leg_par2d_
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
