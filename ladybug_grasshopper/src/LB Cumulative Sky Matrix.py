# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Get a matrix containing radiation values from each patch of a sky dome.
_
Creating this matrix is a necessary pre-step before doing incident radiation
analysis with Rhino geometry or generating a radiation rose.
_
This component uses Radiance's gendaymtx function to calculate the radiation
for each patch of the sky. Gendaymtx is written by Ian Ashdown and Greg Ward.
Morere information can be found in Radiance manual at:
http://www.radiance-online.org/learning/documentation/manual-pages/pdfs/gendaymtx.pdf
-

    Args:
        north_: A number between -360 and 360 for the counterclockwise
            difference between the North and the positive Y-axis in degrees.
            90 is West and 270 is East. This can also be Vector for the
            direction to North. (Default: 0)
        _location: A ladybug Location that has been output from the "LB Import EPW"
            component or the "LB Construct Location" component.
        _direct_rad: An annual hourly DataCollection of Direct Normal Radiation such
            as that which is output from the "LB Import EPW" component or the
            "LB Import STAT" component.
        _diffuse_rad: An annual hourly DataCollection of Diffuse Horizontal Radiation
            such as that which is output from the "LB Import EPW" component or
            the "LB Import STAT" component.
        _hoys_: A number or list of numbers between 0 and 8760 that respresent
            the hour(s) of the year for which to generate the sky matrix. The
            "LB Calculate HOY" component can output this number given a month,
            day and hour. The "LB Analysis Period" component can output a
            list of HOYs within a certain hour or date range. By default,
            the matrix will be for the entire year.
        high_density_: A Boolean to indicate whether the higher-density Reinhart
            sky matrix should be generated (True), which has roughly 4 times
            the sky patches as the (default) original Tregenza sky (False).
            Note that, while the Reinhart sky has a higher resolution and is
            more accurate, it will result in considerably longer calculation
            time for incident radiation studies. The difference in sky
            resolution can be observed with the (Default: False).
        _folder_: The folder in which the Radiance commands are executed to
            produce the sky matrix. If None, it will be written to Ladybug's
            default EPW folder.

    Returns:
        report: ...
        sky_mtx: A sky matrix object containing the radiation coming from each patch
            of the sky. This can be used for a radiation study, a radition rose,
            or a sky dome visualization. It can also be deconstructed into its
            individual values with the "LB Deconstruct Matrix" component.
"""

ghenv.Component.Name = 'LB Cumulative Sky Matrix'
ghenv.Component.NickName = 'SkyMatrix'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '2 :: Visualize Data'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import os
import subprocess

try:
    from ladybug.wea import Wea
    from ladybug.config import folders as lb_folders
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_vector2d
    from ladybug_rhino.grasshopper import all_required_inputs, objectify_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


# TODO: Remove dependency on honeybee + Radiance after genskymtx is in its own extension
try:
    from honeybee_radiance.config import folders as hb_folders
    rad_url = 'https://github.com/LBNL-ETA/Radiance/releases/tag/012cb178'
    assert hb_folders.radiance_path is not None, \
        'No Radiance installation was found on this machine.\n' \
        'Download and install Radiance from\n{}.'.format(rad_url)
    assert hb_folders.radiance_version[:2] >= (5, 3), \
        'The installed Radiance is not version 5.3 or greater.\n' \
        'Download and install Radiance from\n{}.'.format(rad_url)
    # get the path to the gemdaymtx executable
    gendaymtx_exe = os.path.join(hb_folders.radbin_path, 'gendaymtx.exe') if \
        os.name == 'nt' else os.path.join(hb_folders.radbin_path, 'gendaymtx')
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))


# constants for converting RGB values output by gendaymtx to broadband irradiance
TREGENZA_COUNT = (30, 30, 24, 24, 18, 12, 6, 1)
REINHART_COUNT = (60, 60, 60, 60, 48, 48, 48, 48, 36, 36, 24, 24, 12, 12, 1)
TREGENZA_COEFFICIENTS = \
    (0.0435449227, 0.0416418006, 0.0473984151, 0.0406730411, 0.0428934136,
     0.0445221864, 0.0455168385, 0.0344199465)
REINHART_COEFFICIENTS = \
    (0.0113221971, 0.0111894547, 0.0109255262, 0.0105335058, 0.0125224872,
     0.0117312774, 0.0108025291, 0.00974713106, 0.011436609, 0.00974295956,
     0.0119026242, 0.00905126163, 0.0121875626, 0.00612971396, 0.00921483254)
PATCH_COUNTS = {1: 145, 2: 577}
PATCHES_PER_ROW = {1: TREGENZA_COUNT, 2: REINHART_COUNT}
PATCH_ROW_COEFFICIENTS = {1 : TREGENZA_COEFFICIENTS, 2: REINHART_COEFFICIENTS}


def broadband_irradiance(patch_row_str, row_number, sky_density=1):
    """Parse a row of gendaymtx RGB patch data to a broadband irradiance value.

    Args:
        patch_row_str: Text string for a single row of RGB patch data.
        row_number: Interger for the row number that the patch corresponds to.
        sky_density: Integer (either 1 or 2) for the density.
    """
    R, G, B = patch_row_str.split(' ')
    weight_val = 0.265074126 * float(R) + 0.670114631 * float(G) + 0.064811243 * float(B)
    return weight_val * PATCH_ROW_COEFFICIENTS[sky_density][row_number]


def parse_mtx_data(data_str, sky_density=1):
    """Parse a string of Radiance gendaymtx data to a list of one value per patch.

    This function handles the removing of the header and the conversion of the
    RGB values to single broadband irradiance. It also removes the first patch,
    which is the ground and is not used by Ladybug.

    Args:
        data_str: The string that has been output by gendaymtx to stdout.
        sky_density: Integer (either 1 or 2) for the density.
    """
    # split lines and remove the header, ground patch and last line break
    data_lines = data_str.split('\n')
    patch_lines = data_lines[9:-1]

    # loop through the rows and convert the irradiance RGB values
    broadband_irr = []
    patch_counter = 0
    for i, row_patch_count in enumerate(PATCHES_PER_ROW[sky_density]):
        row_slice = patch_lines[patch_counter:patch_counter + row_patch_count]
        irr_vals = (broadband_irradiance(row, i, sky_density) for row in row_slice)
        broadband_irr.extend(irr_vals)
        patch_counter += row_patch_count
    return broadband_irr


if all_required_inputs(ghenv.Component):
    # process and set defaults for all of the global inputs
    if north_ is not None:  # process the north_
        try:
            north_ = math.degrees(
                to_vector2d(north_).angle_clockwise(Vector2D(0, 1)))
        except AttributeError:  # north angle instead of vector
            north_ = float(north_)
    else:
        north_ = 0
    density = 2 if high_density_ else 1

    # filter the radiation by _hoys if they are input
    if len(_hoys_) != 0:
        _direct_rad = _direct_rad.filter_by_hoys(_hoys_)
        _diffuse_rad = _diffuse_rad.filter_by_hoys(_hoys_)

    # create the wea and write it to the default_epw_folder
    wea = Wea(_location, _direct_rad, _diffuse_rad)
    wea_folder = _folder_ if _folder_ is not None else \
        os.path.join(lb_folders.default_epw_folder, 'sky_matrices')
    metd = _direct_rad.header.metadata
    wea_basename = os.path.join(wea_folder, metd['city'].replace(' ', '_')) \
        if 'city' in metd else 'unnamed'
    wea_file =wea.write(wea_basename)

    # execute the Radiance gendaymtx command
    use_shell = True if os.name == 'nt' else False
    # command for diffuse patches
    cmds = [gendaymtx_exe, '-m', str(density), '-s', '-O1', '-A', wea_file]
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE, shell=use_shell)
    stdout = process.communicate()
    diff_data_str = stdout[0]
    # command for direct patches
    cmds = [gendaymtx_exe, '-m', str(density), '-d', '-O1', '-A', wea_file]
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE, shell=use_shell)
    stdout = process.communicate()
    dir_data_str = stdout[0]

    # parse the data into a single matrix
    diff_vals = parse_mtx_data(diff_data_str, density)
    dir_vals = parse_mtx_data(dir_data_str, density)

    # wrap everything together into an object to output from the component
    mtx_data = (north_, diff_vals, dir_vals)
    sky_mtx = objectify_output('Cumulative Sky Matrix', mtx_data)
