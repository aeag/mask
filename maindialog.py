from PyQt4.QtCore import * 
from PyQt4.QtGui import *

from ui_plugin_mask import Ui_MainDialog

class MainDialog( QDialog ):
    def __init__( self ):
        QDialog.__init__( self, None )

        self.ui = Ui_MainDialog()
        self.ui.setupUi(self)

        # mask_mode: selection | mask
        self.mask_mode = None

    def accept( self ):
        # get data before closing
        idx = self.ui.contentCombo.currentIndex()
        self.mask_mode = ('selection', 'mask')[idx]

        QDialog.accept( self )

