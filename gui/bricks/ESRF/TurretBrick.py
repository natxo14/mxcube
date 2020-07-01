#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

"""Turret brick

The standard Turret brick.
"""

import logging

from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ESRF"

class DialWithTags(QtImport.QWidget):
    """
    A QDial with tags in notches
    """
    
    def __init__(self, tag_dict):
        """
        tag_dict:
        { 
            "tag1" : value1
            "tag2" : value2
        }
        tag1/value1 
        """
        super().__init__()

        #print(f"######### DialWithTags: {tag_dict}")
        self.tags = dict(tag_dict)
        self.layout = QtImport.QVBoxLayout()
        self.layout.setContentsMargins(32, 32, 32, 32)
        self.dial = QtImport.QDial()
        self.dial.setMinimum(1)
        self.dial.setMaximum(len(self.tags))
        self.dial.setSingleStep(1)
        self.dial.setNotchesVisible(True)
        self.layout.addWidget(self.dial)
        self.setLayout(self.layout)
        #print(f"######### DialWithTags: {self.dial.value()} - {self.dial.minimum()} - {self.dial.maximum()}")

    def set_new_dict(self, new_dict):
        self.tags = dict(new_dict)
        self.dial.setMinimum(1)
        self.dial.setMaximum(len(self.tags))
        #print(f"######### DialWithTags: {self.dial.value()} - {self.dial.minimum()} - {self.dial.maximum()}")

    # def paintEvent(self, event):
    #     painter = QtImport.QPainter()
    #     painter.begin(self)
    #     self.draw_tags()
    #     painter.end()
    
    def draw_tags(self):
        # p.drawText(10,10,"WORD");
        # p.drawText(width()-40,10,"WORD2");
        # p.drawRect(0,0,width()-1, height()-1);
        pass
    def __getattr__(self, attr):
        # #print(f"######### __getattr__(self, attr): {attr}")
        return getattr(self.dial, attr)
        

class TurretBrick(BaseWidget):
    """ Brick to handle a Turret.

    So far, 5 possible different positions.
    A QDial to handle it.
    """

    def __init__(self, *args):
        """TurretBrick constructor

        Arguments:
        :params args: 
        """
        super(TurretBrick, self).__init__(*args)

        # Hardware objects ----------------------------------------------------

        self.multiple_pos_hwobj = None
        self.turret_hwobj = None  # hardware object
        
        # Graphic elements-----------------------------------------------------

        self.frame = QtImport.QGroupBox()
        self.frame_layout = QtImport.QVBoxLayout()
        
        self.custom_dial = DialWithTags(dict())
        # self.dial.setMinimum(1)
        # self.dial.setMaximum(5)
        # self.dial.setSingleStep(1)
        # self.dial.setNotchesVisible(True)
        
        # Layout --------------------------------------------------------------
        
        self.frame_layout.addWidget(self.custom_dial)
        self.frame.setLayout(self.frame_layout)
        
        self.main_layout = QtImport.QVBoxLayout()
        self.main_layout.addWidget(self.frame, 0, QtImport.Qt.AlignCenter)

        self.setLayout(self.main_layout)

        # Qt signal/slot connections -----------------------------------------
        self.custom_dial.valueChanged.connect(self.value_changed)
        
        # define properties
        self.add_property("mnemonic", "string", "")

        # member variables --------------------------------------------------------------
        self.zoom_position_dict = {}
        # 'position_name': {'dial_val': (position_tag, zoom_value), }

    def value_changed(self, new_position):
        """Move turret to new position."""
        #check if new_position is 'no_position'
        # '5' hardcoded in ESRF - id13.git turret.py file

        #print(f"######### TurretBrick: value_changed {new_position} > 5")
        if new_position > 5:
            return
        print(f"######### TurretBrick: value_changed {self.zoom_position_dict}")
        
        new_pos_props = self.zoom_position_dict.get(new_position, None)
        if new_pos_props is not None:
            new_zoom_value = new_pos_props[0]
            self.turret_hwobj.set_value(new_zoom_value)
        
    def set_mnemonic(self, mne):
        """set mnemonic."""
        self["mnemonic"] = mne

    def set_turret_object(self, multipos_ho_name=None):
        #print(f"######### TurretBrick: set_turret_object {multipos_ho_name}")
        """set turret's hardware object."""
        if self.turret_hwobj is not None:
            
            self.disconnect(self.turret_hwobj, "positionChanged", self.slot_position)
            self.disconnect(self.turret_hwobj, "modeChanged", self.slot_mode)
        
        if multipos_ho_name is not None:
            self.multiple_pos_hwobj = self.get_hardware_object(multipos_ho_name)
            #print(f"######### TurretBrick: set_turret_object multiple_pos_hwobj {type(self.multiple_pos_hwobj)}")
            if self.multiple_pos_hwobj is not None:
                self.turret_hwobj = self.multiple_pos_hwobj.get_zoom_hwr_obj()
                #print(f"######### TurretBrick: set_turret_object self.turret_hwobj {type(self.turret_hwobj)}")
            
            if self.turret_hwobj is not None:
                self.setEnabled(True)
                
                self.connect(self.turret_hwobj, "positionChanged", self.slot_position)
                self.connect(self.turret_hwobj, "modeChanged", self.slot_mode)

                # TODO : add tags on dial with positions names
                # TODO : dict between dial position/value and turret position
                self.custom_dial.set_new_dict(self.multiple_pos_hwobj.get_zoom_positions())
                self.update_zoom_position_dict()
                # recover current position and set to volpi
                #print(f"######### TurretBrick: set_turret_object current_value {self.turret_hwobj.get_value()}")
                self.custom_dial.setValue(self.turret_hwobj.get_value())
                
            # if self.turret_hwobj.is_ready():
            #     self.slot_position(self.turret_hwobj.get_position())
            #     self.slot_status(self.turret_hwobj.get_state())
            #     self.turret_ready()
            # else:
            #     self.turret_not_ready()

        # set number of positions on dial
        
        self.update_gui()
    def update_zoom_position_dict(self):
        print(f"######### TurretBrick: update_zoom_position_dict {self.zoom_position_dict}")
        zoom_dict = self.multiple_pos_hwobj.get_zoom_positions()
        for i, (key, value) in enumerate(zoom_dict.items(), start=1):
            self.zoom_position_dict[i] = (value, key)
        #print(f"########## TURRET BRICK update_zoom_position_dict {self.zoom_position_dict}")
        

    def slot_position(self, new_zoom_value):
        #print(f"########## TURRET BRICK slot_position input {new_zoom_value}")
        
        #get new dial position 
        for i, (key, value) in enumerate(self.zoom_position_dict.items(), start=1):
            #print(f"########## TURRET BRICK slot_position iter {i} - {key} - {value}")
            if new_zoom_value == value[0]:
                self.custom_dial.setValue(i)
        ##print(f"########## TURRET BRICK slot_position output {i}")
        

    def slot_mode(self,new_mode):
        self.mode = new_mode
        
    def turret_ready(self):
        """Set turret enable."""
        self.setEnabled(True)
    
    def turret_not_ready(self):
        """Set turret not enable."""
        self.setEnabled(False)
    
    def property_changed(self, property_name, old_value, new_value):
        """Property changed in GUI designer and when launching app."""
        if property_name == "mnemonic":
                self.set_turret_object(new_value)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)
    
    def update_gui(self):
        if self.turret_hwobj is not None:
            self.frame.setEnabled(True)
            if self.turret_hwobj.is_ready():
                self.turret_hwobj.update_values()
        else:
            self.frame.setEnabled(False)
