# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Create a custom legend for any set of data or range. Creating a legend with this
component allows for a bit more flexibility than what can be achieved by working
with the legends automatically output from different studies.
-

    Args:
        _values: A list of numerical values or data collections that the legend refers
            to. This can also be the minimum and maximum numerical values of the
            data. The legend's maximum and minimum values will be set by the max
            and min of the data set.
        _base_plane_: An optional plane or point to set the location of the
            legend. (Default: Rhino origin - (0, 0, 0))
        title_: A text string representing a legend title. Legends are usually
            titled with the units of the data.
        legend_par_: Optional legend parameters from the  Legend Parameters component.
        leg_par2d_: Optional 2D LegendParameters from the "LB Legend Parameters 2D"
            component, which will be used to customize a legend in the plane
            of the screen so that it functions like a head-up display (HUD).
            If unspecified, the VisualizationSet will be rendered with 3D
            legends in the Rhino scene much like the other native Ladybug
            Tools components.

    Returns:
        mesh: A colored mesh for the legend colors.
        title_obj: A text object for the  legend title.
        label_objs: An array of text objects for the label text.
        label_text: An array of text strings for the label text.
        colors: An array of colors that align with the input _values. This can
            be used to color geometry that aligns with the values.
"""

from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs

class MyComponent(component):
    
    def RunScript(self, _values, _base_plane_, title_, legend_par_, leg_par2d_):
        ghenv.Component.Name = "LB Create Legend"
        ghenv.Component.NickName = 'CreateLegend'
        ghenv.Component.Message = '1.6.1'
        ghenv.Component.Category = 'Ladybug'
        ghenv.Component.SubCategory = '4 :: Extra'
        ghenv.Component.AdditionalHelpFromDocStrings = '0'
        
        try:
            from ladybug.datacollection import BaseCollection
            from ladybug.legend import Legend, LegendParameters
        except ImportError as e:
            raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))
        
        try:
            import scriptcontext as sc
            import Rhino.Display as rd
            import Rhino.Geometry as rg
            from System.Drawing import Color
            from ladybug_rhino.togeometry import to_plane
            from ladybug_rhino.fromobjects import legend_objects
            from ladybug_rhino.color import color_to_color
            from ladybug_rhino.grasshopper import all_required_inputs
        except ImportError as e:
            raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
        
        
        if all_required_inputs(ghenv.Component):
            # set default values
            legend_par_ = legend_par_.duplicate() if legend_par_ is not None else \
                LegendParameters()
            if _base_plane_:
                legend_par_.base_plane = to_plane(_base_plane_)
            legend_par_.title = title_
            
            # create the legend
            values = []
            for val in _values:
                try:
                    values.append(float(val))
                except AttributeError:  # assume it's a data collection
                    values.extend(val.values)
            legend = Legend(values, legend_par_)
            
            if leg_par2d_ is None:  # output a 3D legend
                self.draw_2d_text, self.draw_sprite = None, None
                rhino_objs = legend_objects(legend)
                mesh = rhino_objs[0]
                title_obj = rhino_objs[1]
                label_objs = rhino_objs[2:]
                label_text = legend.segment_text
                colors = [color_to_color(col) for col in legend.value_colors]
            else:  # output a 2D legend that is oriented to the screen
                # set the 3D legend outputs to None
                mesh, title_obj, label_objs, label_text, colors = \
                    None, None, None, None, None
                self.draw_2d_text, self.draw_sprite = [], []
                legend.legend_parameters.properties_2d = leg_par2d_
                
                # figure out the dimensions of the active viewport
                active_view = sc.doc.Views.ActiveView.ActiveViewport
                v_size = active_view.Size
                vw, vh = v_size.Width, v_size.Height
                
                # translate the color matrix to a bitmap
                l_par = legend.legend_parameters
                color_mtx = legend.color_map_2d(vw, vh)
                color_mtx = [[color_to_color(c) for c in row] for row in color_mtx]
                net_bm = System.Drawing.Bitmap(len(color_mtx[0]), len(color_mtx))
                for y, row in enumerate(color_mtx):
                    for x, col in enumerate(row):
                        net_bm.SetPixel(x, y, col)
                rh_bm = rd.DisplayBitmap(net_bm)
                or_x, or_y, sh, sw, th = legend._pixel_dims_2d(vw, vh)
                s_count = l_par.segment_count
                s_count = s_count - 1 if l_par.continuous_legend else s_count
                leg_width = sw if l_par.vertical else sw * s_count
                leg_height = sh if not l_par.vertical else sh * s_count
                cent_pt = rg.Point2d(or_x + (leg_width / 2), or_y + (leg_height / 2))
                self.draw_sprite.append((rh_bm, cent_pt, leg_width, leg_height))
                
                # translate the legend text
                _height = legend.parse_dim_2d(l_par.text_height_2d, vh)
                _font = l_par.font
                txt_pts = legend.segment_text_location_2d(vw, vh)
                cent_txt = False if l_par.vertical else True
                legend_text = [
                    (txt, Color.Black, rg.Point2d(loc.x, loc.y), cent_txt, _height, _font)
                    for txt, loc in zip(legend.segment_text, txt_pts)]
                t_pt = legend.title_location_2d(vw, vh)
                legend_title = (legend.title, Color.Black, rg.Point2d(t_pt.x, t_pt.y),
                                False, _height, _font)
                legend_text.insert(0, legend_title)
                self.draw_2d_text.extend(legend_text)
        else:
            mesh, title_obj, label_objs, label_text, colors = \
                None, None, None, None, None
            self.draw_2d_text, self.draw_sprite = None, None
        
        # return outputs if you have them; here I try it for you
        self.colored_mesh = mesh
        return (mesh, title_obj, label_objs, label_text, colors)
        
    def DrawViewportMeshes(self, args):
        try:
            # get the DisplayPipeline from the event arguments
            display = args.Display
            # draw the objects in the scene
            if self.colored_mesh is not None:
                display.DrawMeshFalseColors(self.colored_mesh)
            if self.draw_2d_text is not None:
                for draw_args in self.draw_2d_text:
                    display.Draw2dText(*draw_args)
            if self.draw_sprite is not None:
                for draw_args in self.draw_sprite:
                    display.DrawSprite(*draw_args)
        except Exception, e:
            System.Windows.Forms.MessageBox.Show(str(e), "script error")
    
    def get_ClippingBox(self):
        return Rhino.Geometry.BoundingBox()
