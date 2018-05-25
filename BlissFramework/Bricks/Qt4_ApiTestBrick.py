#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

from api import sample_changer
from QtImport import QLabel, QLineEdit, QPushButton, QVBoxLayout

from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = "General"
__version__ = 2.3

class Qt4_ApiTestBrick(BlissWidget):

    def __init__(self, *args):
        BlissWidget.__init__(self, *args)

        # Properties ----------------------------------------------------------       

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.puck_ledit = QLineEdit("1", self)
        self.sample_ledit = QLineEdit("1", self)
        self.mount_button = QPushButton("Mount", self)
        self.unmount_button = QPushButton("Unmount", self)
 
        # Layout --------------------------------------------------------------
        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.addWidget(QLabel("Puck", self))
        _main_vlayout.addWidget(self.puck_ledit)
        _main_vlayout.addWidget(QLabel("Sample", self))
        _main_vlayout.addWidget(self.sample_ledit)
        _main_vlayout.addWidget(self.mount_button)
        _main_vlayout.addWidget(self.unmount_button)
        
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.mount_button.clicked.connect(self.mount_clicked)
        self.unmount_button.clicked.connect(self.unmount_clicked)

        # Other --------------------------------------------------------------- 

    def propertyChanged(self, property_name, old_value, new_value):
        BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def mount_clicked(self):
        location_str = "%s:%s" % (str(self.puck_ledit.text()),
                                  str(self.sample_ledit.text()))
        sample_changer.mount_sample(location_str, device_name="sample_changer")

    def unmount_clicked(self):
        sample_changer.unmount_current_sample() 
