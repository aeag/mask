from PyQt4.QtCore import * 
from PyQt4.QtGui import *

from ui_plugin_mask import Ui_MainDialog

class MainDialog( QDialog ):
    def __init__( self ):
        QDialog.__init__( self, None )

        self.ui = Ui_MainDialog()
        self.ui.setupUi(self)

        self.ui.bufferCheckBox.stateChanged.connect( lambda s: self.ui.bufferFrame.setEnabled(s) )
        self.ui.bufferUnits.setValidator(QDoubleValidator())
        self.ui.bufferSegments.setValidator(QIntValidator())

        # mask_mode: selection | mask
        self.mask_mode = None
        #
        self.do_buffer = False
        self.buffer_units = 0
        self.buffer_segments = 0

    def accept( self ):
        # get data before closing
        idx = self.ui.contentCombo.currentIndex()
        self.mask_mode = ('selection', 'mask')[idx]
        self.do_buffer = self.ui.bufferFrame.isEnabled()
        self.buffer_units = float(self.ui.bufferUnits.text() or 0)
        self.buffer_segments = float(self.ui.bufferSegments.text() or 0)

        QDialog.accept( self )

