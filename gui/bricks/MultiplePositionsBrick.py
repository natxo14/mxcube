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

from gui.utils import Icons, QtImport
from gui.BaseComponents import BaseWidget
from gui.bricks.MotorSpinBoxBrick import MotorSpinBoxBrick


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Motor"

class MultiplePositionsBrick(BaseWidget):
    """
    TODO: Class documentation
    """
    
    colorState = {
        'NOTINITIALIZED': 'gray', 
        'UNUSABLE': 'red',
        'READY': '#00ee00',
        'MOVING': 'yellow',
        }
    nameState = ['READY', 'MOVING', 'UNUSABLE', 'NOTINITIALIZED']
    
    def __init__(self, parent, name):
            
        BaseWidget.__init__(self, parent, name)

        #print(f"$$$$$$$$$$$$$$$ LOADING BRICK")
        # Hardware objects ----------------------------------------------------
        self.multipos_hwrobj = None
        
        # Internal values -----------------------------------------------------
        self.__brickStarted = False
        self.__lastPosition = None
        self.check_move = None
        self.appearance = None
        
        # Properties ----------------------------------------------------------
        
        #self.addProperty('appearance', "combo",
        #                ("Display", "Move", "Configure", "Incremental"), "Move")
        self.add_property("mnemonic", "string", "")
        self.add_property("check", "boolean", False)
        
        
        # Signals ------------------------------------------------------------
        self.define_signal("clicked", ())
        
        # Slots ---------------------------------------------------------------
        self.define_slot("setEnabled", ())
        
        # Graphic elements ----------------------------------------------------
        self.buildInterface()
            
    def buildInterface(self):  
        #print(f"$$$$$$$$$$$$$$$ buildInterface")
        
        """
        TODO: missing doc     
        """

        # graphical container for buttons
        self.main_group_box = QtImport.QGroupBox("", self)
        
        # 'logical' container
        self.button_group = QtImport.QButtonGroup()

        self.radio_group_layout = QtImport.QVBoxLayout()

        self.main_group_box.setLayout(self.radio_group_layout)

        self.main_hlayout = QtImport.QHBoxLayout(self)
        self.main_hlayout.addWidget(self.main_group_box)
        self.main_hlayout.setSpacing(2)
        self.main_hlayout.setContentsMargins(2, 2, 2, 2)
        
        # Qt signal/slot connections ------------------------------------------
        self.button_group.buttonClicked.connect(self.position_clicked)

    def run(self):
        #print(f"$$$$$$$$$$$$$$$ run self.multipos_hwrobj {id(self.multipos_hwrobj)}")
        #self.hardware_object_change(self.multipos_hwrobj)
        self.__brickStarted = True

    def hardware_object_change2(self, hwro):
        #print(f"$$$$$$$$$$$$$$$ hardware_object_change")
        self.connect_hardware_object()
        
        if self.multipos_hwrobj is not None:
            title = self.multipos_hwrobj.username                             
            self.main_group_box.setTitle(title)

            for index, key in enumerate(self.multipos_hwrobj.get_positions_names_list(), start=1): 
                #print(f"$$$$$$$$$$$$$$$ hardware_object_change {index} {str(key)}")
                     
                radio_button = QtImport.QRadioButton(str(key))
                self.radio_group_layout.addWidget(radio_button)
                self.button_group.addButton(radio_button, index)
                #self.positionList.insertItem(str(key))
        else:
            self.main_group_box.setTitle("<B>Unknown<B>")
        
        # self.configWindow.setHardwareObject(self.hwro)
        # self.appearanceChange(self.appearance)

    def hardware_object_change(self, hwro_name=None):
        #print(f"$$$$$$$$$$$$$$$MULTIPOSBRICK hardware_object_change2 hwro_name-  {hwro_name} ")
        if self.multipos_hwrobj is not None:
                self.disconnect_hardware_object()
        
        if hwro_name is not None:
            self.multipos_hwrobj = self.get_hardware_object(hwro_name)

        if self.multipos_hwrobj is not None:
            title = self.multipos_hwrobj.username                             
            self.main_group_box.setTitle(title)

            #clean previous widgets
            self.button_group.buttonClicked.disconnect(self.position_clicked)

            old_buttons = self.button_group.buttons()
            #print(f"$$$$$$$$$$$$$$$MULTIPOSBRICK type old_buttons {type(old_buttons)} - {len(old_buttons)}")

            for index, radio_button in enumerate(self.button_group.buttons(), start=1):
                radio_button.setParent(None)

            for index, key in enumerate(self.multipos_hwrobj.get_positions_names_list(), start=1): 
                #print(f"$$$$$$$$$$$$$$$MULTIPOSBRICK hardware_object_change {index} {str(key)}")
                radio_button = QtImport.QRadioButton(str(key))
                self.radio_group_layout.addWidget(radio_button)
                self.button_group.addButton(radio_button, index)
    
            self.button_group.buttonClicked.connect(self.position_clicked)
            self.connect_hardware_object()

            #retrieve zoom position and set the corresponding checkbox
            current_position_name = self.multipos_hwrobj.get_value()
            #print(f"$$$$$$$$$$$$$$$MULTIPOSBRICK current_position_name {current_position_name}")
            self.position_changed(current_position_name)
        
        else:
            self.main_group_box.setTitle("<B>Unknown<B>")
                

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            #print(f"$$$$$$$$$$$$$$$MULTIPOSBRICK property_changed {new_value} ")
            self.hardware_object_change(new_value)
            #self.configWindow.clearConfigurator()
            #self.disconnectHardwareObject()
            #if self.hwro is not None:
            #    self.radioGroup.clearRadioList()
            #self.__lastPosition = None

            # #print(f"@@@@@@@@@@@@ property_changed {new_value}")
            # if self.multipos_hwrobj is not None:
            #     self.disconnect_hardware_object()

            # self.multipos_hwrobj = self.get_hardware_object(new_value)

            # if self.multipos_hwrobj is not None:
            #     self.connect_hardware_object()
            # #print(f"property_changed self.multipos_hwrobj {self.multipos_hwrobj}")
            # #print(f"@@@@@@@@@@@@ self.multipos_hwrobj.positions {self.multipos_hwrobj.positions}")
            # if self.__brickStarted:
            #     self.hardware_object_change(self.multipos_hwrobj)

        if property_name == "appearance":
            self.appearance = new_value
            if self.__brickStarted:
                self.appearanceChange(self.appearance)

        if property_name == "check":
            self.check_move = new_value
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def connect_hardware_object(self):
        if self.multipos_hwrobj is not None:  
            self.connect(self.multipos_hwrobj, "predefinedPositionChanged",
                             self.position_changed)
            self.connect(self.multipos_hwrobj, "no_position",
                             self.no_position)
            self.connect(self.multipos_hwrobj, "stateChanged",
                             self.check_state)
            self.connect(self.multipos_hwrobj, "equipmentReady",
                             self.equipment_ready)
            self.connect(self.multipos_hwrobj, "equipmentNotReady",
                             self.equipment_not_ready)

    def equipment_ready(self):
        self.setEnabled(True)
    
    def equipment_not_ready(self):
        self.setEnabled(False)
    
    def disconnect_hardware_object(self):

        if self.multipos_hwrobj is not None:
            self.disconnect(self.multipos_hwrobj, "predefinedPositionChanged",
                             self.position_changed)
            self.disconnect(self.multipos_hwrobj, "no_position",
                             self.no_position)
            self.disconnect(self.multipos_hwrobj, "stateChanged",
                             self.check_state)
            self.disconnect(self.multipos_hwrobj, "equipmentReady",
                             self.equipment_ready)
            self.disconnect(self.multipos_hwrobj, "equipmentNotReady",
                             self.equipment_not_ready)

    def position_clicked(self):
        name = self.button_group.checkedButton().text()
        if self.multipos_hwrobj is not None:
            #print(f"MultiplePosBrick buttonClicked. id : {name} - {self.button_group.checkedId()}")
            if self.check_move:
                msgstr = f"You will move {self.multipos_hwrobj.username} \
                    to position {name}"
                ret = QtImport.QMessageBox.warning(None, "Move to position", msgstr,
                                    QtImport.QMessageBox.Ok,
                                    QtImport.QMessageBox.Cancel,
                                    QtImport.QMessageBox.NoButton)     
                if ret == QtImport.QMessageBox.Ok:
                    self.multipos_hwrobj.moveToPosition(name)
                else:
                    self.multipos_hwrobj.checkPosition()
            else:
                self.multipos_hwrobj.moveToPosition(name)

    def state_changed(self, state):
        """Enables/disables controls based on the state
        """
        pass 
    
    def position_changed(self, name):

        # retrieve id of qradiobutton with 'name' on it
        button_id = None
        for index, key in enumerate(self.multipos_hwrobj.get_positions_names_list(), start=1):
            if name == key:
                button_id = index
        
        if button_id is None:
            return

        radio_button = self.button_group.button(button_id)
        radio_button.setChecked(True)
        # if self.appearance == "Move" or self.appearance == "Configure":
        #     self.radioGroup.setChecked(name, True)
        #     if self.appearance == "Configure":
        #         self.__lastPosition = name
        #         self.setButton.setEnabled(True)
        #         self.setButton.setText("Set \"%s\""%name)
            
        # if self.appearance == "Display":
        #     self.valueLabel.setText(name)
            
        # if self.appearance == "Incremental":
        #     self.valueWidget.setValue(name)
    
    def no_position(self):

        self.button_group.setExclusive(False)
        self.button_group.checkedButton().setChecked(False)
        self.button_group.setExclusive(True)
        # if self.appearance == "Move" or self.appearance == "Configure":
        #     self.radioGroup.deselectAll()
            
        # if self.appearance == "Display":
        #     state = self.hwro.getState()
        #     if state == "MOVING":
        #         self.valueLabel.setText("Moving")
        #     else :
        #         self.valueLabel.setText("Unknown")
            
        # if self.appearance == "Incremental":
        #     state = self.hwro.getState()
        #     if state == "MOVING":
        #         self.valueWidget.setValue("Moving")
        #     else :
        #         self.valueWidget.setValue("Unknown")
        pass

    def check_state(self, new_state):
        
        state = self.multipos_hwrobj.get_state()
        #print(f"MultiplePosBrick check_state new state {new_state} - state {state}")
        
        # if state in MultiplePositionsBrick.nameState:
            # qcolor = QtImport.QColor(MultiplePositionsBrick.colorState[state])
            # if self.appearance == "Display":
            #     self.valueLabel.setPaletteBackgroundColor(qcolor)
            # else:
            #     self.titleLabel.setPaletteBackgroundColor(qcolor)
    
    # def setPosition(self):
    #     if self.hwro is not None and self.__lastPosition is not None:
    #         if self.hwro.mode.lower() == "absolute":
    #             allpos = {}
    #             for role,mot in self.hwro["motors"]._objectsByRole.iteritems():
    #                 allpos[role] = mot.getPosition()
    #             self.hwro.setNewPositions(self.__lastPosition, allpos)
    #         else:
    #             for role,mot in self.hwro["motors"]._objectsByRole.iteritems():
    #                 motpos = mot.getPosition()
    #                 savedpos = self.hwro.positions[self.__lastPosition][role]
    #                 offset = mot.getOffset()
    #                 newoffset = offset + savedpos - motpos
    #                 mot.setOffset(newoffset)
    # def go_to_position(self):
    #     if self.multipos_hwrobj is not None:
    #         self.multipos_hwrobj.moveToPosition(str(self.positionList.currentText()))