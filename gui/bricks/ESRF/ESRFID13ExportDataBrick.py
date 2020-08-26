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
"""
ESRF ID13 Export Data Brick

[Description]

This brick exports data to different files:

Exported data:
    * Information related to microscope status:
        * motor positions
        * camera calibration
    * Information on graphical items:
        * beam position
        * created points/lines/ROI's positions
    * Microscope snapshots

Created files:
    * JSON file with 
    * Image file with raw microscope image
    * Image file with microscope image plus graphics items (if any)

[Properties]

xml file

[Signals]

delete_graphic_items : sent after export data (if option checked)

[Slots]

sample_changed - sample changed from outside GUI


[Comments]

"""

import sys
import math
import logging
import json
import os
from os.path import expanduser
from pprint import pprint
import copy
import datetime
from datetime import date
import logging

from gui.utils import Icons, Colors, QtImport
from gui.BaseComponents import BaseWidget
from HardwareRepository import HardwareRepository as HWR

from bliss.config import static
from bliss.config import get_sessions_list


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ESRF"

class ESRFID13ExportDataBrick(BaseWidget):

    delete_graphic_items = QtImport.pyqtSignal(object)
    
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Slots ---------------------------------------------------------------
        self.define_slot("sample_changed", ())

        
        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Export Data", self)
        self.ui_widgets_manager = QtImport.load_ui_file("export_data_layout.ui")

        # Internal values -----------------------------------------------------
        
        # Layout --------------------------------------------------------------
        _groupbox_vlayout = QtImport.QVBoxLayout(self)
        _groupbox_vlayout.addWidget(self.ui_widgets_manager)
        _groupbox_vlayout.setSpacing(0)
        _groupbox_vlayout.setContentsMargins(0, 0, 0, 0)
        self.main_groupbox.setLayout(_groupbox_vlayout)

        # Qt signal/slot connections ------------------------------------------
        self.main_groupbox.toggled.connect(self.main_groupbox_toggled)
        self.ui_widgets_manager.export_button.clicked.connect(
            self.export_button_clicked
        )

        self.ui_widgets_manager.sample_name_tbox.editingFinished.connect(
            self.set_export_file_path
        )

        self.ui_widgets_manager.filename_tbox.editingFinished.connect(
            self.set_export_file_path
        )

        self.ui_widgets_manager.file_index_tbox.editingFinished.connect(
            self.set_export_file_path
        )


    def set_export_file_path(self):
        
        #get full path from bliss 

    def export_button_clicked(self):

        """
        File to be exported.
        Format: python dict
        {
            "timestamp" : datetime.now()
            "diff_motors" : { 
                            "mot0.name": pos0
                            "mot1.name": pos1
                             ...
                            }
            "position_dict" : { 
                            "beam_pos_x" : val, int - pixels
                            "beam_pos_y" : val, int - pixels
                            "cal_x" : val, int - nm / pixel
                            "cal_y" : val, int - nm / pixel
                            "light" : val,
                            "zoom" : val,
                               }
            "selected_shapes_dict": {
                                    "selected_shape1_name":
                                        {
                                        "type" : string
                                        "index" : int
                                        "collection: string ( 'visible', 'background'...)
                                        "centred_positions" : list( dict )
                                                {
                                                    "phi":
                                                    "phiz":
                                                    "phiy":
                                                    "sampx":
                                                    "sampy":
                                                }
                                        }

                                    }

        }

        """

        if self.ui_widgets_manager.overwrite_warn_cbbox.isChecked():
            # get full filename and check if file already exists
            file_full_path = self.ui_widgets_manager.export_full_path_tbox.text()

            if os.path.exists(file_full_path):
                if (
                    QtImport.QMessageBox.warning(
                        None,
                        "File already exists!",
                        f"Are you sure you want to overwrite existing file ?",
                        QtImport.QMessageBox.Yes,
                        QtImport.QMessageBox.No,
                    )
                    == QtImport.QMessageBox.No
                    ):
                    return

        if self.ui_widgets_manager.clean_comment_cbox.isChecked():
            self.ui_widgets_manager.comment_text_edit.clear()

        if self.ui_widgets_manager.delete_items_cbox.isChecked():
            HWR.beamline.sample_view.clear_all_shapes()

        data = {}

        now = datetime.datetime.now()
        data['timestamp'] = str(now)

        data['data_creator'] = "GUIApplication"

        diff_motors_dict = {}
        positions_dict = {}
        selected_shapes_dict = {}

        if HWR.beamline.diffractometer is not None:

            diff_motors_dict = HWR.beamline.diffractometer.get_motors_dict()
            position_dict = HWR.beamline.diffractometer.get_diffractometer_status()

            for shape in HWR.beamline.sample_view.get_selected_shapes():
                
                display_name = shape.get_display_name()
                shape_type = display_name.split()[0]
                index = display_name.split()[-1]
                
                centred_positions = []

                if shape_type == "Point":
                    centred_positions.append(shape.get_centred_position())
                elif shape_type == "Line":
                    centred_positions.append(list(shape.get_centred_positions()))
                elif shape_type == "Square":
                    centred_positions.append(list(shape.get_centred_positions()))


                shape_dict = {}
                shape_dict["type"] = shape_type
                shape_dict["index"] = index
                shape_dict["collection"] = collection
                shape_dict["centred_positions"] = centred_positions

                selected_shapes_dict[display_name] = shape_dict

        data['diff_motors'] = diff_motors_dict
        data["position_dict"] = position_dict


        file_index = int(self.ui_widgets_manager.file_index_tbox.text())
        file_index += 1
        self.ui_widgets_manager.file_index_tbox.setText(str(file_index))


        