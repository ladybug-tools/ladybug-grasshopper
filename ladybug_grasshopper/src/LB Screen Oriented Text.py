# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Generate screen-oriented text that displays in the Rhino scene as a head-up
display (HUD).
_
This is useful when there are certain summary results or information that should
always be displayed on-screen.
-

    Args:
        _text: Text string to be displayed in the plane of the screen.
        leg_par2d_: Optional 2D LegendParameters from the "LB Legend Parameters 2D"
            component, which will be used to customize a text in the plane
            of the screen. Note that only the text_height, origin_x and origin_y
            inputs of this component affect the placement of the text.
        _font_: An optional text string to specify the font to be used for the text.
            Examples include "Arial", "Times New Roman", "Courier" (all without
            quotations). Default is "Arial".
        _color_: An optional color to set the color of the text. If unspecified,
            it will be black.
        viewport_: Text for the name of the Rhino viewport to which the 2D screen-oriented
            legend will be rendered. If unspecified, the 2D legend will be rendered
            in all viewports. Acceptable inputs include:
                -
                Perspective
                Top
                Bottom
                Left
                Right
                Front
                Back
                any view name that has been saved within the Rhino file
"""

from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs

class MyComponent(component):
    
    def __init__(self):
        super(MyComponent,self).__init__()
        self.text_2d_args = None
        self.viewport = None
    
    def RunScript(self, _text, leg_par2d_, _font_, _color_, viewport_):
        ghenv.Component.Name = 'LB Screen Oriented Text'
        ghenv.Component.NickName = 'Text2D'
        ghenv.Component.Message = '1.8.1'
        ghenv.Component.Category = 'Ladybug'
        ghenv.Component.SubCategory = '4 :: Extra'
        ghenv.Component.AdditionalHelpFromDocStrings = '0'
        
        try:
            from ladybug.legend import Legend, Legend2DParameters
        except ImportError as e:
            raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))
        
        try:
            from ladybug_rhino.color import black
            from ladybug_rhino.grasshopper import all_required_inputs, longest_list
        except ImportError as e:
            raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
        
        import scriptcontext as sc
        import Rhino.Geometry as rg
        
        if all_required_inputs(ghenv.Component):
            # get the screen dimensions
            active_view = sc.doc.Views.ActiveView.ActiveViewport
            v_size = active_view.Size
            vw = v_size.Width
            vh = v_size.Height
            _font = 'Arial' if _font_ is None else _font_
            _color_ = black() if _color_ is None else _color_
            
            # convert the inputs into arguments to be rendered
            self.text_2d_args = []
            for i, txt in enumerate(_text):
                if len(leg_par2d_) == 0:  # make default 2D parameters
                    l_par = Legend2DParameters()
                else:
                    l_par = longest_list(leg_par2d_, i)
                _height = Legend.parse_dim_2d(l_par.text_height, vh)
                or_x = Legend.parse_dim_2d(l_par.origin_x, vw)
                or_y = Legend.parse_dim_2d(l_par.origin_y, vh)
                d_args = (
                    txt, _color_, rg.Point2d(or_x,or_y), False, _height, _font)
                self.text_2d_args.append(d_args)
            self.viewport = viewport_
        else:
            self.text_2d_args = None
            self.viewport = None
    
    def DrawViewportWires(self, args):
        try:
            if self.text_2d_args is not None:
                # get the DisplayPipeline from the event arguments
                display = args.Display
                # render the 2D text from the arguments
                if self.viewport is None or \
                        self.viewport.lower() == args.Viewport.Name.lower():
                    for draw_args in self.text_2d_args:
                        display.Draw2dText(*draw_args)
        except Exception, e:
            System.Windows.Forms.MessageBox.Show(str(e), "script error")
    
    def get_ClippingBox(self):
        return Rhino.Geometry.BoundingBox()
