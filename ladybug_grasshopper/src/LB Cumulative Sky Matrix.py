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
ghenv.Component.Message = '1.1.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '2 :: Visualize Data'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import os
import subprocess
import math

try:
    from ladybug_geometry.geometry2d.pointvector import Vector2D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug.wea import Wea
    from ladybug.viewsphere import view_sphere
    from ladybug.dt import DateTime
    from ladybug.config import folders as lb_folders
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_vector2d
    from ladybug_rhino.grasshopper import all_required_inputs, objectify_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


# TODO: Remove dependency on honeybee + Radiance after genskymtx is in its own LB extension
try:
    from honeybee_radiance.config import folders as hb_folders
    compatible_rad_date = (2020, 9, 3)
    hb_url = 'https://github.com/ladybug-tools/lbt-grasshopper/wiki/1.4-Compatibility-Matrix'
    rad_msg = 'Download and install the version of Radiance listed in the Ladybug ' \
        'Tools compatibility matrix\n{}'.format(hb_url)
    assert hb_folders.radiance_path is not None, \
        'No Radiance installation was found on this machine.\n{}'.format(rad_msg)
    assert hb_folders.radiance_version_date >= compatible_rad_date, \
        'The installed Radiance is not from {} or later.' \
        '\n{}'.format('/'.join(str(v) for v in compatible_rad_date), rad_msg)
    # get the path to the gemdaymtx executable
    gendaymtx_exe = os.path.join(hb_folders.radbin_path, 'gendaymtx.exe') if \
        os.name == 'nt' else os.path.join(hb_folders.radbin_path, 'gendaymtx')
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))


# constants for converting RGB values output by gendaymtx to broadband radiation
PATCHES_PER_ROW = {
    1: view_sphere.TREGENZA_PATCHES_PER_ROW + (1,),
    2: view_sphere.REINHART_PATCHES_PER_ROW + (1,)
}
PATCH_ROW_COEFF = {
    1 : view_sphere.TREGENZA_COEFFICIENTS,
    2: view_sphere.REINHART_COEFFICIENTS
}


def broadband_radiation(patch_row_str, row_number, wea_duration, sky_density=1):
    """Parse a row of gendaymtx RGB patch data in W/sr/m2 to radiation in kWh/m2.

    This includes aplying broadband weighting to the RGB bands, multiplication
    by the steradians of each patch, and multiplying by the duration of time that
    they sky matrix represents in hours.

    Args:
        patch_row_str: Text string for a single row of RGB patch data.
        row_number: Interger for the row number that the patch corresponds to.
        sky_density: Integer (either 1 or 2) for the density.
        wea_duration: Number for the duration of the Wea in hours. This is used
            to convert between the average value output by the command and the
            cumulative value that is needed for all ladybug analyses.
    """
    R, G, B = patch_row_str.split(' ')
    weight_val = 0.265074126 * float(R) + 0.670114631 * float(G) + 0.064811243 * float(B)
    return weight_val * PATCH_ROW_COEFF[sky_density][row_number] * wea_duration / 1000


def parse_mtx_data(data_str, wea_duration, sky_density=1):
    """Parse a string of Radiance gendaymtx data to a list of radiation-per-patch.

    This function handles the removing of the header and the conversion of the
    RGB irradianc-=per-steraidian values to broadband radiation. It also removes
    the first patch, which is the ground and is not used by Ladybug.

    Args:
        data_str: The string that has been output by gendaymtx to stdout.
        wea_duration: Number for the duration of the Wea in hours. This is used
            to convert between the average value output by the command and the
            cumulative value that is needed for all ladybug analyses.
        sky_density: Integer (either 1 or 2) for the density.
    """
    # split lines and remove the header, ground patch and last line break
    data_lines = data_str.split('\n')
    patch_lines = data_lines[9:-1]

    # loop through the rows and convert the radiation RGB values
    broadband_irr = []
    patch_counter = 0
    for i, row_patch_count in enumerate(PATCHES_PER_ROW[sky_density]):
        row_slice = patch_lines[patch_counter:patch_counter + row_patch_count]
        irr_vals = (broadband_radiation(row, i, wea_duration, sky_density)
                    for row in row_slice)
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
    wea_duration = len(wea) / wea.timestep
    wea_folder = _folder_ if _folder_ is not None else \
        os.path.join(lb_folders.default_epw_folder, 'sky_matrices')
    metd = _direct_rad.header.metadata
    wea_basename = metd['city'].replace(' ', '_') if 'city' in metd else 'unnamed'
    wea_path = os.path.join(wea_folder, wea_basename)
    wea_file = wea.write(wea_path)

    # execute the Radiance gendaymtx command
    use_shell = True if os.name == 'nt' else False
    # command for direct patches
    cmds = [gendaymtx_exe, '-m', str(density), '-d', '-O1', '-A', wea_file]
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE, shell=use_shell)
    stdout = process.communicate()
    dir_data_str = stdout[0]
    # command for diffuse patches
    cmds = [gendaymtx_exe, '-m', str(density), '-s', '-O1', '-A', wea_file]
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE, shell=use_shell)
    stdout = process.communicate()
    diff_data_str = stdout[0]

    # parse the data into a single matrix
    dir_vals = parse_mtx_data(dir_data_str, wea_duration, density)
    diff_vals = parse_mtx_data(diff_data_str, wea_duration, density)

    # collect sky metadata like the north, which will be used by other components
    metadata = [north_]
    if _hoys_:
        metadata.extend([DateTime.from_hoy(h) for h in (_hoys_[0], _hoys_[-1])])
    else:
        metadata.extend([wea.analysis_period.st_time, wea.analysis_period.end_time])
    for key, val in _direct_rad.header.metadata.items():
        metadata.append('{} : {}'.format(key, val))

    # wrap everything together into an object to output from the component
    mtx_data = (metadata, dir_vals, diff_vals)
    sky_mtx = objectify_output('Cumulative Sky Matrix', mtx_data)
