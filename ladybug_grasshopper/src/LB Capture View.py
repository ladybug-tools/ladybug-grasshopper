# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Capture views of the Rhino scene and save them to your hard drive as as a .png files.
_
This is particularly useful when creating animations and one needs to automate
the capturing of views. Note that images will likely have a Rhino world axes icon
in the lower left of the image unless you go to Options > Grid > and uncheck
"Show world axes icon".
-

    Args:
        _file_name: The file name, which the image will be saved as. Note that, for
            animations, each saved image should have a different name. Otherwise,
            the previous image will be overwritten by each successive image.
            Unique names for each animation frame can be achieved by using the
            animating slider to generate the file name.
        _folder_: The folder into which the image file will be written. This should
            be a complete path to the folder. If None, the images will be written
            to one of the following default locations:
            -
            Windows - C:/Users/[USERNAME]/ladybug_tools/resources/captured_views/
            Mac - /Users/[USERNAME]/ladybug_tools/resources/captured_views/
        viewport_: Text for the Rhino viewport name which will be captured. This can
            also be a list of viewports in which case multiple views will be
            captured. If None, the default will be the active viewport (the
            last viewport in which you navigated). Acceptable inputs include:
                -
                Perspective
                Top
                Bottom
                Left
                Right
                Front
                Back
                any view name that has been saved within the Rhino file
        width_: Integer for the width of the image to be captured in pixels. If None,
            the default is the width of the Rhino viewport currently on the screen.
        height_: Integer for the height of the image to be captured in pixels. If None,
            the default is the height of the Rhino viewport currently on the screen.
        mode_: Text for the display mode of the viewport to be captured.If None, the default
            will be the display mode of the active viewport (the last viewport in
            which you navigated). Acceptable inputs include:
                -
                Wireframe
                Shaded
                Rendered
                Ghosted
                X-Ray
                Technical
                Artistic
                Pen
        transparent_: Boolean to note whether the captured .png file should have a
            transparent background. If None or False, the image will have the
            Rhino viewport background color.
        _capture: Set to "True" to capture the image of the Rhino viewport.

    Returns:
        file: The file path of the image taken with this component.

"""
ghenv.Component.Name = 'LB Capture View'
ghenv.Component.NickName = 'CaptureView'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import os

try:
    from ladybug.futil import preparedir
    from ladybug.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
    default_folder = os.path.join(folders.default_simulation_folder, 'captured_views')
except:
    home_folder = os.getenv('HOME') or os.path.expanduser('~')
    default_folder = os.path.join(home_folder, 'captured_views')

try:
    from ladybug_rhino.grasshopper import all_required_inputs, bring_to_front
    from ladybug_rhino.viewport import viewport_by_name, capture_view
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _capture:
    # ensure the component runs last on the canvas
    bring_to_front(ghenv.Component)

    # prepare the folder
    folder = _folder_ if _folder_ is not None else default_folder
    preparedir(folder, remove_content=False)

    # get the viewport objects
    vp_names = viewport_ if len(viewport_) != 0 else [None]
    viewports = [viewport_by_name(vp) for vp in vp_names]

    # save the viewports to images
    for i, view_p in enumerate(viewports):
        f_name = _file_name if len(viewports) == 1 else \
            '{}_{}'.format(_file_name, vp_names[i])
        file_p = os.path.join(folder, f_name)
        fp = capture_view(view_p, file_p, width_, height_, mode_, transparent_)
        print(fp)
