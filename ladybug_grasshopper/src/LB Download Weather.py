# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Automatically download a .zip file from a URL where climate data resides,
unzip the file, and open .epw, .stat, and ddy weather files.
-

    Args:
        _weather_URL: Text representing the URL at which the climate data resides. 
            To open the a map interface for all publicly availabe climate data (epwmap),
            use the "EPWmap" component.
        _folder_: An optional file path to a directory into which the weather file
            will be downloaded and unziped.  If None, the weather files will be
            downloaded to the ladybug default weather data folder and placed in
            a sub-folder with the name of the weather file location.

    Returns:
        epw_file: The file path of the downloaded epw file.
        stat_file: The file path of the downloaded stat file.
        ddy_file: The file path of the downloaded ddy file.
"""

ghenv.Component.Name = 'LB Download Weather'
ghenv.Component.NickName = 'DownloadEPW'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '0 :: Import'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug.futil import unzip_file
    from ladybug.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.download import download_file
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import os


if all_required_inputs(ghenv.Component):
    # name for the weather files
    if _weather_URL.lower().endswith('.zip'):
        # onebuilding URL type
        _folder_name = _weather_URL.split('/')[-1][:-4]
    else:
        # dept of energy URL type
        _folder_name = _weather_URL.split('/')[-2]
    
    # create default working_dir
    if _folder_ is None:
        _folder_ = folders.default_epw_folder
    try:
        _folder_.decode('ascii')
    except UnicodeDecodeError:
        raise UnicodeDecodeError(
            '\nYour download folder "{}" contains non-ASCII characters\n'
            '\nUse the _folder_ input to this component to download EPW files'
            ' to a valid location.'.format(_folder_))
    else:
        print 'Files will be downloaded to: {}'.format(_folder_)
    
    
    # default file names
    epw = os.path.join(_folder_, _folder_name, _folder_name + '.epw')
    stat = os.path.join(_folder_, _folder_name, _folder_name + '.stat')
    ddy = os.path.join(_folder_, _folder_name, _folder_name + '.ddy')
    
    # download and unzip the files if they do not exist
    if not os.path.isfile(epw) or not os.path.isfile(stat) or not os.path.isfile(ddy):
        zip_file_path = os.path.join(_folder_, _folder_name, _folder_name + '.zip')
        download_file(_weather_URL, zip_file_path, True)
        unzip_file(zip_file_path)
    
    # set output
    epw_file, stat_file, ddy_file = epw, stat, ddy