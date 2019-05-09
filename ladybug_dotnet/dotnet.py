"""Collection of methods for dealing with general .NET objects."""
import os

try:
    from ladybug.futil import preparedir
except ImportError as e:
    print "Failed to import ladybug.\n{}".format(e)

try:
    from System.Drawing import Color
    import System.Net
except ImportError as e:
    print "Failed to import System.\n{}".format(e)


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


def color_to_color(color):
    """Convert a ladybug color into DotNet color."""
    try:
        return Color.FromArgb(255, color.r, color.g, color.b)
    except AttributeError as e:
        raise AttributeError('Input must be of type of Color:\n{}'.format(e))


def gray():
    """Get a DotNet gray color object. Useful when you need a placeholder color."""
    return Color.Gray
