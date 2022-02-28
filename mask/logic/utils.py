import os
from qgis.PyQt.QtCore import QLocale, QUrl, QDir
from qgis.PyQt.QtGui import QDesktopServices

"""
    A problem it seems in the 'utils' module of QGis.
    The showPluginHelp function mixes '/' and '', and the Qt Url produced is invalid, under windows.
    This code, while waiting for a QGis API patch.
"""
def showPluginHelp(packageName: str = None, filename: str = "index", section: str = ""):
    try:
        source = ""
        if packageName is None:
            import inspect
            source = inspect.currentframe().f_back.f_code.co_filename
        else:
            import sys
            source = sys.modules[packageName].__file__
    except:
        return
    path = os.path.dirname(source)
    locale = str(QLocale().name())
    helpfile = os.path.join(path, filename + "-" + locale + ".html")
    if not os.path.exists(helpfile):
        helpfile = os.path.join(path, filename + "-" + locale.split("_")[0] + ".html")
    if not os.path.exists(helpfile):
        helpfile = os.path.join(path, filename + "-en.html")
    if not os.path.exists(helpfile):
        helpfile = os.path.join(path, filename + "-en_US.html")
    if not os.path.exists(helpfile):
        helpfile = os.path.join(path, filename + ".html")
    if os.path.exists(helpfile):
        url = "file://" + QDir.fromNativeSeparators(helpfile)
        if section != "":
            url = url + "#" + section
        QDesktopServices.openUrl(QUrl(url, QUrl.TolerantMode))
