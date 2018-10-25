"""Collection of methods for dealing with general .NET objects."""
import os

from .futil import preparedir

try:
    from System.Drawing import Color
    import System.Net
except ImportError:
    print "Failed to import System."


def download_file_by_name(url, target_folder, file_name, mkdir=False):
    """Download a file to a directory.

    Args:
        url: A string to a valid URL.
        target_folder: Target folder for download (e.g. c:/ladybug)
        file_name: File name (e.g. testPts.zip).
        mkdir: Set to True to create the directory if doesn't exist (Default: False)
    """
    # create the target directory.
    if not os.path.isdir(target_folder):
        if mkdir:
            preparedir(target_folder)
        else:
            created = preparedir(target_folder, False)
            if not created:
                raise ValueError("Failed to find %s." % target_folder)
    file_path = os.path.join(target_folder, file_name)

    # set the security protocol to the most recent version
    try:
        # TLS 1.2 is needed to download over https
        System.Net.ServicePointManager.SecurityProtocol = \
            System.Net.SecurityProtocolType.Tls12
    except AttributeError:
        # TLS 1.2 is not provided by MacOS .NET
        if url.lower().startswith('https'):
            print ('This system lacks the necessary security'
                   ' libraries to download over https.')

    # attempt to download the file
    client = System.Net.WebClient()
    try:
        client.DownloadFile(url, file_path)
    except Exception as e:
        raise Exception(' Download failed with the error:\n{}'.format(e))


def download_file(url, file_path, mkdir=False):
    """Write a string of data to file.

    Args:
        url: A string to a valid URL.
        file_path: Full path to intended download location (e.g. c:/ladybug/testPts.pts)
        mkdir: Set to True to create the directory if doesn't exist (Default: False)
    """
    folder, fname = os.path.split(file_path)
    return download_file_by_name(url, folder, fname, mkdir)


def color_to_color(colors):
    """Convert a ladybug color into Grasshopper color."""
    if not hasattr(colors, '__iter__'):
        colors = (colors,)
    try:
        return tuple(Color.FromArgb(255, col.r, col.g, col.b) for col in colors)
    except AttributeError as e:
        raise AttributeError('Inputs must be of type of Color:\n{}'.format(e))
