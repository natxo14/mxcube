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
[Name] Centering Brick

[Description]


[Properties]
-----------------------------------------------------------------------
| name         | type   | description
-----------------------------------------------------------------------
| blah      | string | 
| blah | string | 
-----------------------------------------------------------------------

[Signals] -

[Slots] -

[Comments] -

[Hardware Objects]
-----------------------------------------------------------------------
| name         | signals             | functions
-----------------------------------------------------------------------
|          | signal0     | function0()
|  	       
-----------------------------------------------------------------------
"""

import sys
import math
import logging
import numpy

from gui.utils import Icons, Colors, QtImport


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


from gui.BaseComponents import BaseWidget
from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ESRF"

class ESRFCenteringBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.diffractometer_hwobj = None

        # Internal values -----------------------------------------------------
        self.step_editor = None
        self.move_step = 1
        self.demand_move = 0
        self.in_expert_mode = None
        self.position_history = []
        self.num_clicked_centring_pos = 0
        
        #match default values in .ui file
        self.points_for_aligment = 3
        self.delta_phi = 5

        # Properties ----------------------------------------------------------
        self.add_property("mnemonic", "string", "")
        self.add_property("clockwise", "boolean", False)
        self.add_property("table_y_inverted", "boolean", False)
        self.add_property("table_z_inverted", "boolean", False)

        # Signals ------------------------------------------------------------
        self.define_signal("getBeamPosition", ())
        self.define_signal("centring_parameters_changed", ())

        # Slots ---------------------------------------------------------------
        self.define_slot("changePixelScale", ())
        
        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Sample centering", self)
        self.ui_widgets_manager = QtImport.load_ui_file("centering.ui")

        
        # Size policy --------------------------------
        self.ui_widgets_manager.aligment_table.setSizePolicy(
            QtImport.QSizePolicy.Minimum,
            QtImport.QSizePolicy.Minimum,
        )

        #validator for input values for delta phi: min/max/decimals
        # self.ui_widgets_manager.delta_phi_textbox.setValidator(
        #     QtImport.QDoubleValidator(0, 180, 2)
        # )

        # Layout --------------------------------------------------------------
        _groupbox_vlayout = QtImport.QVBoxLayout()
        _groupbox_vlayout.addWidget(self.ui_widgets_manager)
        #_groupbox_vlayout.setSpacing(0)
        #_groupbox_vlayout.setContentsMargins(0, 0, 0, 0)
        self.main_groupbox.setLayout(_groupbox_vlayout)

        # MatPlotWidget --------------------------------------------------------------
         # a figure instance to plot on
        self.figure = plt.figure()
         # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)
        _matplotlib_widget_layout = QtImport.QVBoxLayout()
        _matplotlib_widget_layout.addWidget(self.toolbar)
        _matplotlib_widget_layout.addWidget(self.canvas)
        
        # Layout --------------------------------------------------------------
        _main_vlayout = QtImport.QHBoxLayout()
        _main_vlayout.addWidget(self.main_groupbox)
        _main_vlayout.addLayout(_matplotlib_widget_layout)
        #_main_vlayout.setSpacing(0)
        #_main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_vlayout)

        # Qt signal/slot connections ------------------------------------------
       
        self.ui_widgets_manager.show_center_checkbox.stateChanged.connect(
            self.show_center
        )

        self.ui_widgets_manager.show_help_line_checkbox.stateChanged.connect(
            self.show_help_lines
        )
        
        self.ui_widgets_manager.number_points_spinbox.valueChanged.connect(
            self.change_point_number
        )

        self.ui_widgets_manager.delta_phi_textbox.editingFinished.connect(
            self.delta_phi_changed
        )

        self.ui_widgets_manager.start_alignment_button.clicked.connect(
            self.start_centring
        )

        self.ui_widgets_manager.cancel_alignment_button.clicked.connect(
            self.cancel_centring
        )

        # TODO : add show center and show help line functionalities
        self.ui_widgets_manager.show_center_checkbox.hide()
        self.ui_widgets_manager.show_help_line_checkbox.hide()
        
        # Other ---------------------------------------------------------------

        self.plot_data_X = []
        self.plot_data_Y = []
        self.connect(HWR.beamline.sample_view, "centringStarted", self.centring_started)
        self.connect(HWR.beamline.sample_view, "centringFailed", self.centring_failed)
        self.connect(
            HWR.beamline.sample_view, "centringSuccessful", self.centring_successful
        )
        self.connect(HWR.beamline.diffractometer, "centring_image_clicked", self.image_clicked)
        self.connect(HWR.beamline.diffractometer, "centring_calculation_ended", self.show_centring_paremeters)

        self.change_point_number(self.points_for_aligment)

        # init delta_phi var value
        self.delta_phi_changed()

    def centring_started(self):
        #clean point table
        self.clean_table()
        self.num_clicked_centring_pos = 0
        self.ui_widgets_manager.number_points_spinbox.setEnabled(False)

    def centring_failed(self, method, centring_status):
        #background cell color to red
        print(f"ESRFCENTERINGBRICK ; centring_failed")
        table = self.ui_widgets_manager.aligment_table
        table.setRowCount(self.points_for_aligment)
        for row in range(table.rowCount()):
            for column in range(table.columnCount()):
                table.item(row, column).setBackground(QtImport.QColor(QtImport.Qt.red))
        self.ui_widgets_manager.number_points_spinbox.setEnabled(True)

    def centring_successful(self):
        #background cell color to green
        table = self.ui_widgets_manager.aligment_table
        table.setRowCount(self.points_for_aligment)
        for row in range(table.rowCount()):
            for column in range(table.columnCount()):
                table.item(row, column).setBackground(QtImport.QColor(QtImport.Qt.green))
        self.ui_widgets_manager.number_points_spinbox.setEnabled(True)

    # def property_changed(self, property_name, old_value, new_value):
    #     if property_name == "mnemonic":
    #         self.diffractometer_hwobj = self.get_hardware_object(new_value)
            
            # equipment = self.get_hardware_object(new_value)
            # if equipment is not None :
            #         xoryMotor = equipment.getDeviceByRole('horizontal')
            #         if xoryMotor is not None:
            #             self.__verticalPhi = True
            #         else:
            #             xoryMotor = equipment.getDeviceByRole('vertical')
            #             if xoryMotor is None:
            #                 logging.getLogger().error('%s: could not find motors horizontal nor vertical motor in Hardware Objects %s',
            #                                           str(self.name()),equipment.name())
            #                 return
            #             self.__verticalPhi = False

            #         zMotor = equipment.getDeviceByRole('inBeam')
            #         rMotor = equipment.getDeviceByRole('rotation')
            #         if zMotor is None or rMotor is None :
            #             logging.getLogger().error('%s: could not find motors inBeam or rotation motor in Hardware Objects %s',
            #                                       str(self.name()),equipment.name())
            #             return          

    def image_clicked(self, x, y):
        print(f"CenteringBrick - image_clicked {x},{y} - num click {self.num_clicked_centring_pos}")
        table = self.ui_widgets_manager.aligment_table
        print(f"CenteringBrick - image_clicked table rows, cols : {table.rowCount()} {table.columnCount()}")
        self.plot_data_Y.append(x)
        self.plot_data_X.append(math.radians(self.delta_phi) * self.num_clicked_centring_pos)
        table.item(self.num_clicked_centring_pos, 1).setText(str(x))
        table.item(self.num_clicked_centring_pos, 2).setText(str(y))
        table.item(self.num_clicked_centring_pos, 0).setText(str(self.delta_phi * self.num_clicked_centring_pos))

        self.num_clicked_centring_pos += 1
 
        # instead of ax.hold(False)
        self.figure.clear()
        # plot data
        ax = self.figure.add_subplot()
        ax.plot(self.plot_data_X, self.plot_data_Y , 'ro')
        self.canvas.draw()

    def show_centring_paremeters(self, parameter_dict):

        # from multipointcenter
        # p[0] * numpy.sin(x + p[1]) + p[2]
        amplitude = parameter_dict['r']
        phase = parameter_dict['alpha']
        offset = parameter_dict['offset']
        d_horizontal = parameter_dict['d_horizontal']
        phi_positions = parameter_dict['phi_positions']
        image_width_pix = HWR.beamline.sample_view.get_image_size()[0]
        beam_position_x = HWR.beamline.beam.get_beam_position_on_screen()[0]
        pixels_per_mm_hor = parameter_dict['pixelsPerMm_Hor']
        
        
        x_angle = numpy.linspace(phi_positions[0], 2 *numpy.pi + phi_positions[0], 360)
        sinus_signal = amplitude * numpy.sin(x_angle + phase) + offset
        
        print(f"""CenteringBrick - PLOT :
        self.plot_data_X NOT DEPLACED BY phi_positions[0] {self.plot_data_X}
        self.plot_data_Y  {self.plot_data_Y}
        """)
        # clear data
        self.figure.clear()
        # plot data
        ax = self.figure.add_subplot()
        ax.plot(x_angle, sinus_signal )
        ax.plot(
            numpy.array(phi_positions),
            numpy.array(self.plot_data_Y) / float(pixels_per_mm_hor) , 'ro'
        )
        ax.axhspan(0, float(image_width_pix / pixels_per_mm_hor), facecolor='y', alpha=0.5)
        ax.axhline(y=float(beam_position_x / pixels_per_mm_hor), color='r', linestyle='-.')

        ax.axhspan(d_horizontal, d_horizontal + float(image_width_pix / pixels_per_mm_hor), facecolor='g', alpha=0.5)
        ax.axhline(y=d_horizontal + float(beam_position_x / pixels_per_mm_hor), color='b', linestyle='-.')

        self.canvas.draw()

    def show_center(self, checkbox_state):
        """
        Doc
        """
        pass
    def show_help_lines(self, checkbox_state):
        """
        Doc
        """
        pass
    def start_centring(self):
        """
        Launch aligment process
        """
        HWR.beamline.sample_view.start_centring(tree_click=True)
    def cancel_centring(self):
        """
        Cancel aligment process
        """
        self.plot_data_X.clear()
        self.plot_data_Y.clear()
        self.figure.clear()
        HWR.beamline.sample_view.reject_centring()

    def change_point_number(self, new_int_value):
        """
        Adapt
        """
        self.points_for_aligment = new_int_value

        # restart the table and populate with items
        table = self.ui_widgets_manager.aligment_table
        table.clearContents()
        table.setRowCount(self.points_for_aligment)

        for row in range(table.rowCount()):
            table.setItem(row, 0, QtImport.QTableWidgetItem(""))
            table.setItem(row, 1, QtImport.QTableWidgetItem(""))
            table.setItem(row, 2, QtImport.QTableWidgetItem(""))
        
        if HWR.beamline.diffractometer is not None:
            HWR.beamline.diffractometer.set_centring_parameters(
                self.points_for_aligment,
                self.delta_phi
            )

        #self.emit_centring_parameters_changed()

    def delta_phi_changed(self):
        delta_phi_str = self.ui_widgets_manager.delta_phi_textbox.text()
        try:
            self.delta_phi = float(delta_phi_str.replace(" ", ""))
        except ValueError as error:
            logging.getLogger().error(
                f"""Sorry, could not transform {delta_phi_str} into a float var.
                Using default {self.delta_phi} value"""
            )
        
        self.points_for_aligment = self.ui_widgets_manager.number_points_spinbox.value()
        if HWR.beamline.diffractometer is not None:
            HWR.beamline.diffractometer.set_centring_parameters(
                self.points_for_aligment,
                self.delta_phi
            )
        #self.emit_centring_parameters_changed()
    
    # def emit_centring_parameters_changed(self):
    #     self.emit("centring_parameters_changed",
    #     (self.points_for_aligment, self.delta_phi)
    #     )
        
    def clean_table(self):
        """
        Adapt
        """
        table = self.ui_widgets_manager.aligment_table
        self.points_for_aligment = self.ui_widgets_manager.number_points_spinbox.value()
        table.setRowCount(self.points_for_aligment)
        for row in range(table.rowCount()):
            for column in range(table.columnCount()):
                table.item(row, column).setText("")
                table.item(row, column).setData(QtImport.Qt.BackgroundRole, None)
            