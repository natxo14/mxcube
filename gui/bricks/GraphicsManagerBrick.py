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

from HardwareRepository import HardwareRepository as HWR
from HardwareRepository.HardwareObjects import QtGraphicsLib as GraphicsLib

import json
import os
from os.path import expanduser
from pprint import pprint
import copy
import datetime
from datetime import date
import logging

try:
    from xml.etree import cElementTree  # python2.5
except ImportError:
    import cElementTree

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Graphics"


class GraphicsManagerBrick(BaseWidget):

    get_operational_modes_list_signal = QtImport.pyqtSignal(object)
    create_centring_point_button_toggled = QtImport.pyqtSignal(bool)

    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Internal values -----------------------------------------------------
        self.__shape_map = {}
        self.__point_map = {}
        self.__line_map = {}
        self.__grid_map = {}
        self.__square_map = {}
        self.__original_height = 600
        self.__list_of_tags = list()
        self.__click_pos = None
        self.__beam_cal_file_xml_path = None
        self.__data_export_file_path = None
        self.__export_file_prefix = "export_file_prefix"
        self.__export_file_index = 0
        self.__op_modes_file_path = None
        
        # Properties ----------------------------------------------------------
        self.add_property("op_mode_list_file", "string", "")
        
        # Signals ------------------------------------------------------------
        self.define_signal("get_operational_modes_list_signal", ())
        self.define_signal("create_centring_point_button_toggled", ())

        # Slots ---------------------------------------------------------------
        self.define_slot("set_data_path", ())
        self.define_slot("update_operational_modes", ())
        self.define_slot("delete_all_button_clicked", ())
        self.define_slot("toggle_create_point_start_button", ())

        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Graphics items", self)
        self.manager_widget = QtImport.load_ui_file("graphics_manager_layout.ui")

        # Layout --------------------------------------------------------------
        _groupbox_vlayout = QtImport.QVBoxLayout(self)
        _groupbox_vlayout.addWidget(self.manager_widget)
        _groupbox_vlayout.setSpacing(0)
        _groupbox_vlayout.setContentsMargins(0, 0, 0, 0)
        self.main_groupbox.setLayout(_groupbox_vlayout)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_groupbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(_main_vlayout)

        # mutual exclusive checkboxes
        self.mutual_exclusive_op_mode = QtImport.QButtonGroup()

        self.mutual_exclusive_bg = QtImport.QButtonGroup()
        self.mutual_exclusive_bg.addButton(
            self.manager_widget.display_points_cbox
        )
        self.mutual_exclusive_bg.addButton(
            self.manager_widget.display_grids_cbox
        )
        self.mutual_exclusive_bg.addButton(
            self.manager_widget.display_lines_cbox
        )
        self.mutual_exclusive_bg.addButton(
            self.manager_widget.display_square_roi_cbox
        )
        self.mutual_exclusive_bg.addButton(
            self.manager_widget.display_all_cbox
        )
        self.mutual_exclusive_bg.addButton(
            self.manager_widget.hide_all_cbox
        )
        self.mutual_exclusive_bg.addButton(
            self.manager_widget.show_selected_cbox
        )
                
        # Qt signal/slot connections ------------------------------------------
        self.main_groupbox.toggled.connect(self.main_groupbox_toggled)
        self.manager_widget.change_color_button.clicked.connect(
            self.change_color_clicked
        )

        self.manager_widget.display_points_cbox.stateChanged.connect(
            self.display_points_toggled
        )

        self.manager_widget.display_lines_cbox.stateChanged.connect(
            self.display_lines_toggled
        )

        self.manager_widget.display_grids_cbox.stateChanged.connect(
            self.display_grids_toggled
        )

        self.manager_widget.display_square_roi_cbox.stateChanged.connect(
            self.display_squares_toggled
        )

        self.manager_widget.display_all_cbox.stateChanged.connect(
            self.display_all_toggled
        )

        self.manager_widget.hide_all_cbox.stateChanged.connect(
            self.hide_all_toggled
        )

        self.manager_widget.show_selected_cbox.stateChanged.connect(
            self.show_selected_toggled
        )
        
        self.manager_widget.delete_all_button.clicked.connect(
            self.delete_all_button_clicked
        )

        self.manager_widget.delete_selection_button.clicked.connect(
            self.delete_selection_button_clicked
        )

        self.manager_widget.create_point_start_button.toggled.connect(
            self.create_point_start_button_toggled
        )
        self.manager_widget.create_point_start_button_2.toggled.connect(
            self.create_point_start_button_toggled
        )
        self.manager_widget.create_point_accept_button.clicked.connect(
            self.create_point_accept_button_clicked
        )
        self.manager_widget.create_point_accept_button_2.clicked.connect(
            self.create_point_accept_button_clicked
        )

        # TODO : what does 'accept' mean ??
        # self.manager_widget.create_point_accept_button.hide()

        self.manager_widget.create_line_button.clicked.connect(
            self.create_line_button_clicked
        )
        self.manager_widget.create_line_button_2.clicked.connect(
            self.create_line_button_clicked
        )

        self.manager_widget.create_square_button.clicked.connect(
            self.create_square_clicked
        )
        self.manager_widget.create_square_button_2.clicked.connect(
            self.create_square_clicked
        )

        self.manager_widget.draw_grid_button.clicked.connect(
            self.draw_grid_button_clicked
        )

        # self.manager_widget.shapes_treewidget.currentItemChanged.connect(\
        #     self.shape_treewiget_current_item_changed)
        # self.manager_widget.shapes_treewidget.itemClicked.connect(
        #     self.shape_treewiget_item_clicked
        # )

        self.manager_widget.shapes_treewidget.itemSelectionChanged.connect(
            self.shape_treewiget_selection_changed
        )

        self.manager_widget.select_all_button.clicked.connect(
            self.select_all_button_clicked
        )

        self.manager_widget.select_points_button.clicked.connect(
            self.select_points_button_clicked
        )

        self.manager_widget.select_lines_button.clicked.connect(
            self.select_lines_button_clicked
        )

        self.manager_widget.select_square_roi_button.clicked.connect( 
            self.select_square_roi_button_clicked
        )

        self.manager_widget.shapes_treewidget.setSelectionMode(
            QtImport.QAbstractItemView.ExtendedSelection
        )

        self.manager_widget.hor_spacing_ledit.textChanged.connect(
            self.grid_spacing_changed
        )
        self.manager_widget.ver_spacing_ledit.textChanged.connect(
            self.grid_spacing_changed
        )
        self.manager_widget.move_left_button.clicked.connect(
            self.grid_move_left_clicked
        )
        self.manager_widget.move_right_button.clicked.connect(
            self.grid_move_right_clicked
        )
        self.manager_widget.move_up_button.clicked.connect(self.grid_move_up_clicked)
        self.manager_widget.move_down_button.clicked.connect(
            self.grid_move_down_clicked
        )
       

        # SizePolicies --------------------------------------------------------

        # Other ---------------------------------------------------------------
        self.manager_widget.shapes_treewidget.setContextMenuPolicy(
            QtImport.Qt.CustomContextMenu
        )

        tmp = self.manager_widget.shapes_treewidget.customContextMenuRequested.connect(
            self.prepare_tree_widget_menu
        )

        # by default manager is closed
        # self.main_groupbox.setCheckable(True)
        # self.main_groupbox.setChecked(True)
        # self.main_groupbox_toggled(True)
        # # self.main_groupbox.setToolTip("Click to open/close item manager")

        self.connect(HWR.beamline.sample_view, "shapeCreated", self.shape_created)
        self.connect(HWR.beamline.sample_view, "shapeDeleted", self.shape_deleted)
        self.connect(HWR.beamline.sample_view, "shapeSelected", self.shape_selected)
        self.connect(
            HWR.beamline.sample_view,
            "centringInProgress",
            self.centring_in_progress_changed
        )
        self.connect(HWR.beamline.sample_view, "escape_pressed", self.escape_pressed)
    
    def property_changed(self, property_name, old_value, new_value):
        if property_name == "op_mode_list_file":
            if new_value.startswith("/"):
                    new_value = new_value[1:]

            self.__op_modes_file_path = os.path.join(
                HWR.getHardwareRepositoryConfigPath(),
                new_value + ".xml")

            if (os.path.isfile(self.__op_modes_file_path)):
                self.load_list_of_operational_modes()
                self.create_operational_modes_checkboxes()
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)
    
    def escape_pressed(self):
        """

        """

    def set_data_path(self, new_path):

        text = self.manager_widget.file_path_label.text()
        text += new_path
        self.manager_widget.file_path_label.setText(text)
        self.__data_export_file_path = new_path

    def prepare_tree_widget_menu(self, pos):
        """
        Prepare menu to select the tag for the given shape
        """
        self.get_operational_modes_list_signal.emit(self.__list_of_tags)
        print(f"prepare_tree_widget_menu after signal : {self.__list_of_tags}")
        
        self.__click_pos = pos
        # get clicked item position in table
                
        selection_menu = QtImport.QMenu()
        selection_menu.addSection("Select shape's collection")

        for tag in self.__list_of_tags:
            print(f"tag : {tag}")
            new_action = QtImport.QAction(tag, selection_menu)
            new_action.setData(tag)
            # new_action.triggered.connect(
            #     self.tree_widget_menu_selected
            # )
            selection_menu.addAction(new_action)
        selection_menu.setMinimumWidth(200)
        selection_menu.triggered.connect(
            self.tree_widget_menu_selected
        )
        selection_menu.exec(
            self.manager_widget.shapes_treewidget.mapToGlobal(pos)
        )

    def update_operational_modes(self, new_op_mode_list):
        print(f"GraphicsManagerBrick update_operational_modes {new_op_mode_list}")

        self.__list_of_tags = new_op_mode_list
        self.create_operational_modes_checkboxes()

    def create_operational_modes_checkboxes(self):
        
        if self.__list_of_tags:
            
            self.manager_widget.operational_modes_layout
            
            while self.manager_widget.operational_modes_layout.count() > 1:

                last_widget_index = self.manager_widget.operational_modes_layout.count() - 1
                layout_item = self.manager_widget.operational_modes_layout.takeAt(last_widget_index)
                widget = layout_item.widget()
                                
                if widget.metaObject().className() == "QCheckBox":
                    self.mutual_exclusive_op_mode.removeButton(widget)
                    self.manager_widget.operational_modes_layout.removeItem(layout_item)
                    self.manager_widget.operational_modes_layout.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()
                    widget.setVisible(False)
                    widget = None
                    self.adjustSize()
                
            # create new boxes
            for index, tag in enumerate(self.__list_of_tags):
                col = index % 4
                row = index // 4
                tmp_cbox = QtImport.QCheckBox(tag, None)
                self.mutual_exclusive_op_mode.addButton(tmp_cbox)
                self.manager_widget.operational_modes_layout.addWidget(tmp_cbox, row, col + 1)
                tmp_cbox.setChecked(True)
                
        else:
            self.manager_widget.defaut_collection_label.hide()

    def tree_widget_menu_selected(self, action):
        """
        change shape's information according to selected value
        """
        #print(f"selected tag : {action} -  action data {action.data()}")
        for item in self.manager_widget.shapes_treewidget.selectedItems():
            item.setData(4, QtImport.Qt.DisplayRole, action.data())
        # clicked_item = self.manager_widget.shapes_treewidget.itemAt(self.__click_pos)
        # if clicked_item is None:
        #     #iterate over selected items
        #     for item in self.manager_widget.shapes_treewidget.selectedItems():
        #         item.setData(4, QtImport.Qt.DisplayRole, action.data())
        # else:
        #     clicked_item.setData(4, QtImport.Qt.DisplayRole, action.data())

    def shape_created(self, shape, shape_type):
        """
        Adds information about shape in all shapes treewidget
        and depending on shape type also information to
        treewidget of all points/lines/grids
        """

        if self.__list_of_tags:
            op_mode = self.mutual_exclusive_op_mode.checkedButton().text()
        else:
            op_mode = "default"    
        # get shape's operational mode
        
        info_str_list = (
            str(self.manager_widget.shapes_treewidget.topLevelItemCount() + 1),
            shape.get_display_name(),
            str(True),
            str(True),
            str(op_mode),
        )
        shape.set_operation_mode(op_mode)

        new_tree_widget_item = QtImport.QTreeWidgetItem(
            self.manager_widget.shapes_treewidget, info_str_list
        )
        
        self.__shape_map[shape] = new_tree_widget_item
        self.toggle_buttons_enabled()

        # info_str_list = QStringList()
        info_str_list = []

        info_str_list.append(str(shape.index))
        if shape_type == "Point":
            info_str_list.append(str(int(shape.get_start_position()[0])))
            info_str_list.append(str(int(shape.get_start_position()[1])))
            self.manager_widget.point_treewidget.clearSelection()
            point_treewidget_item = QtImport.QTreeWidgetItem(
                self.manager_widget.point_treewidget, info_str_list
            )
            point_treewidget_item.setSelected(True)
            self.__point_map[shape] = point_treewidget_item
        elif shape_type == "Line":
            (start_index, end_index) = shape.get_points_index()
            info_str_list.append("Point %d" % start_index)
            info_str_list.append("Point %d" % end_index)
            self.manager_widget.line_treewidget.clearSelection()
            line_treewidget_item = QtImport.QTreeWidgetItem(
                self.manager_widget.line_treewidget, info_str_list
            )
            line_treewidget_item.setSelected(True)
            self.__line_map[shape] = line_treewidget_item
        elif shape_type == "Grid":
            self.manager_widget.grid_treewidget.clearSelection()
            grid_treewidget_item = QtImport.QTreeWidgetItem(
                self.manager_widget.grid_treewidget, info_str_list
            )
            grid_treewidget_item.setSelected(True)
            self.__grid_map[shape] = grid_treewidget_item
        elif shape_type == "Square":
            positions = shape.get_pixels_positions()
            print(f"positions type {positions} {type(positions)}")
            
            init_pos_str = str(int(positions[0][0])) + ',' + str(int(positions[0][1]))
            end_pos_str = str(int(positions[1][0])) + ',' + str(int(positions[1][1]))
            
            print(f"positions init_pos_str {init_pos_str}")
            print(f"positions end_pos_str {end_pos_str}")
            

            info_str_list.append(init_pos_str)
            info_str_list.append(end_pos_str)
            self.manager_widget.square_treewidget.clearSelection()
            square_treewidget_item = QtImport.QTreeWidgetItem(
                self.manager_widget.square_treewidget, info_str_list
            )
            square_treewidget_item.setSelected(True)
            self.__square_map[shape] = square_treewidget_item

    def shape_deleted(self, shape, shape_type):
        if self.__shape_map.get(shape):
            item_index = self.manager_widget.shapes_treewidget.indexOfTopLevelItem(
                self.__shape_map[shape]
            )
            self.__shape_map.pop(shape)
            self.manager_widget.shapes_treewidget.takeTopLevelItem(item_index)
            if shape_type == "Point":
                item_index = self.manager_widget.point_treewidget.indexOfTopLevelItem(
                    self.__point_map[shape]
                )
                self.__point_map.pop(shape)
                self.manager_widget.point_treewidget.takeTopLevelItem(item_index)
            elif shape_type == "Line":
                item_index = self.manager_widget.line_treewidget.indexOfTopLevelItem(
                    self.__line_map[shape]
                )
                self.__line_map.pop(shape)
                self.manager_widget.line_treewidget.takeTopLevelItem(item_index)
            elif shape_type == "Grid":
                item_index = self.manager_widget.grid_treewidget.indexOfTopLevelItem(
                    self.__grid_map[shape]
                )
                self.__grid_map.pop(shape)
                self.manager_widget.grid_treewidget.takeTopLevelItem(item_index)
            elif shape_type == "Square":
                item_index = self.manager_widget.square_treewidget.indexOfTopLevelItem(
                    self.__square_map[shape]
                )
                self.__square_map.pop(shape)
                self.manager_widget.square_treewidget.takeTopLevelItem(item_index)
        self.toggle_buttons_enabled()

    def shape_selected(self, shape, selected_state):
        print(f"GRPHICMANAGERBRICK shape_selected type(shape) {type(shape)} selected_state {selected_state}")
        if shape in self.__shape_map:
            #print(f"GRPHICMANAGERBRICK shape_selected shape in self.__shape_map:")
            treewidget_item = self.__shape_map[shape]
            treewidget_item.setData(
                3, QtImport.Qt.DisplayRole, str(selected_state)
            )
            self.__shape_map[shape].setSelected(selected_state)
            if self.__point_map.get(shape):
                self.__point_map[shape].setSelected(selected_state)
            if self.__line_map.get(shape):
                self.__line_map[shape].setSelected(selected_state)
            if self.__grid_map.get(shape):
                self.__grid_map[shape].setSelected(selected_state)
            if self.__square_map.get(shape):
                self.__square_map[shape].setSelected(selected_state)
            self.manager_widget.change_color_button.setEnabled(
                bool(HWR.beamline.sample_view.get_selected_shapes())
            )

    def shape_treewiget_selection_changed(self):
        """
        act when selection changed in tree widget:
        update shape's status
        """
        print(f"GRPHICMANAGERBRICK shape_treewiget_selection_changed")
        selected_item_list = self.manager_widget.shapes_treewidget.selectedItems()
        shape_list = list(self.__shape_map.keys())
        item_list = list(self.__shape_map.values())
        index_list = []

        for item in selected_item_list:
            try:
                index = item_list.index(item)
                index_list.append(index)
            except ValueError:
                continue
        for i, shape in enumerate(shape_list):
            shape.setSelected(i in index_list)

        self.manager_widget.change_color_button.setEnabled(
            bool(item_list)
        )

    def select_all_button_clicked(self):
        for shape in self.__shape_map.keys():
            shape.setSelected(True)

    def select_points_button_clicked(self):
        for shape in self.__shape_map.keys():
            if isinstance(shape, GraphicsLib.GraphicsItemPoint):
                shape.setSelected(True)
            else:
                shape.setSelected(False)
    
    def select_lines_button_clicked(self):
        for shape in self.__shape_map.keys():
            if isinstance(shape, GraphicsLib.GraphicsItemLine):
                shape.setSelected(True)
            else:
                shape.setSelected(False)
    
    def select_square_roi_button_clicked(self):
        for shape in self.__shape_map.keys():
            if isinstance(shape, GraphicsLib.GraphicsItemSquareROI):
                shape.setSelected(True)
            else:
                shape.setSelected(False)
    
    def centring_in_progress_changed(self, centring_in_progress):
        # if centring_in_progress:
        #     self.manager_widget.create_point_start_button.setIcon(
        #         Icons.load_icon("Delete")
        #     )
        # else:
        #     self.manager_widget.create_point_start_button.setIcon(
        #         Icons.load_icon("VCRPlay2")
        #     )
        pass

    def main_groupbox_toggled(self, is_on):
        if is_on:
            self.setFixedHeight(self.__original_height)
        else:
            self.setFixedHeight(20)

    def change_color_clicked(self):
        color = QtImport.QColorDialog.getColor()
        if color.isValid():
            for item in HWR.beamline.sample_view.get_selected_shapes():
                item.set_base_color(color)

    def display_all(self):
        print(f"display_all")
        for shape, treewidget_item in self.__shape_map.items():
            print(f"shape {shape} to be showed")
            shape.show()
            treewidget_item.setData(2, QtImport.Qt.DisplayRole, "True")
        
        self.manager_widget.display_all_cbox.setChecked(True)
    
    def hide_all_toggled(self, state):
        if state == QtImport.Qt.Checked:
            self.hide_all()

    def display_all_toggled(self, state):
        if state == QtImport.Qt.Checked:
            self.display_all()

    def show_selected_toggled(self, state):
        if state == QtImport.Qt.Checked:
            self.show_only_selected()
    
    def show_only_selected(self):
        for shape, treewidget_item in self.__shape_map.items():
            if shape.isSelected():
                shape.show()
                treewidget_item.setData(2, QtImport.Qt.DisplayRole, "True")
            else:
                shape.hide()
                treewidget_item.setData(2, QtImport.Qt.DisplayRole, "False")

    def hide_all(self):
        
        for shape, treewidget_item in self.__shape_map.items():
            shape.hide()
            treewidget_item.setData(2, QtImport.Qt.DisplayRole, "False")

        self.manager_widget.hide_all_cbox.setChecked(True)
    
    def delete_selection_button_clicked(self):
        """
        delete selected items
        """
        
        for shape in HWR.beamline.sample_view.get_selected_shapes():
            HWR.beamline.sample_view.delete_shape(shape)

    def hide_selection_button_clicked(self):
        """
        hide selected items
        """
        
        for shape in self.__shape_map.keys():
            if shape.isSelected():
                self.__shape_map[shape].setData(2, QtImport.Qt.DisplayRole, "False")
                shape.hide()

        # selected_item_list = self.manager_widget.shapes_treewidget.selectedItems()
        # shape_list = list(self.__shape_map.keys())
        # item_list = list(self.__shape_map.values())
        # index_list = []

        # for item in selected_item_list:
        #     try:
        #         index = item_list.index(item)
        #         index_list.append(index)
        #     except ValueError:
        #         continue
        # for i, shape in enumerate(shape_list):
        #     shape.hide()

        # self.manager_widget.change_color_button.setEnabled(
        #     bool(item_list)
        # )

    def delete_all_button_clicked(self):
        HWR.beamline.sample_view.clear_all_shapes()

    def clear_selected_button_clicked(self):
        print(f"clear_selected_button_clicked")
        for shape in HWR.beamline.sample_view.get_selected_shapes():
            print(f"shape {shape} - {shape.get_display_name()} to be deleted")
            HWR.beamline.sample_view.delete_shape(shape)
    
    def toggle_create_point_start_button(self, checked):
        print(f"GRAPHICSMANAGERBRICK toggle_create_point_start_button checked {checked}")
        self.manager_widget.create_point_start_button.setChecked(checked)
        self.manager_widget.create_point_start_button_2.setChecked(checked)

    def create_point_start_button_toggled(self, checked):
        # HWR.beamline.sample_view.start_centring(tree_click=True)
        self.manager_widget.create_point_start_button.setChecked(checked)
        self.manager_widget.create_point_start_button_2.setChecked(checked)
        print(f"GRAPHICSMANAGERBRICK create_point_start_button_toggled checked {checked}")
        if checked:
            HWR.beamline.sample_view.start_one_click_centring()
        else:
            HWR.beamline.sample_view.stop_one_click_centring()
        self.create_centring_point_button_toggled.emit(checked)

    def create_point_accept_button_clicked(self):
        HWR.beamline.sample_view.start_centring()

    def create_line_button_clicked(self):
        HWR.beamline.sample_view.create_line()

    def draw_grid_button_clicked(self):
        HWR.beamline.sample_view.create_grid(self.get_spacing())
    
    def create_square_clicked(self):
        HWR.beamline.sample_view.create_square()

    def show_shape_treewidget_popup(self, item, point, col):
        QtImport.QMenu(self.manager_widget.shapes_treewidget)

    def get_spacing(self):
        spacing = [0, 0]
        try:
            spacing[0] = float(self.manager_widget.hor_spacing_ledit.text())
            spacing[1] = float(self.manager_widget.ver_spacing_ledit.text())
        except BaseException:
            pass
        return spacing

    def toggle_buttons_enabled(self):
        self.manager_widget.display_points_cbox.setEnabled(len(self.__shape_map) > 0)
        self.manager_widget.display_lines_cbox.setEnabled(len(self.__shape_map) > 0)
        self.manager_widget.display_grids_cbox.setEnabled(len(self.__shape_map) > 0)
        self.manager_widget.display_square_roi_cbox.setEnabled(len(self.__shape_map) > 0)
        self.manager_widget.hide_all_cbox.setEnabled(len(self.__shape_map) > 0)
        self.manager_widget.display_all_cbox.setEnabled(len(self.__shape_map) > 0)

        self.manager_widget.delete_all_button.setEnabled(len(self.__shape_map) > 0)

    def shape_treewiget_item_clicked(self, current_item, column):
        for key, value in self.__shape_map.items():
            if value == current_item:
                key.toggle_selected()
        self.manager_widget.change_color_button.setEnabled(current_item is not None)

    def grid_spacing_changed(self, value):
        spacing = self.get_spacing()
        for grid_treewidget_item in self.manager_widget.grid_treewidget.selectedItems():
            grid_item = self.__grid_map.keys()[
                self.__grid_map.values().index(grid_treewidget_item)
            ]
            grid_item.set_spacing(spacing)

    def grid_move_left_clicked(self):
        self.move_selected_grids("left")

    def grid_move_right_clicked(self):
        self.move_selected_grids("right")

    def grid_move_up_clicked(self):
        self.move_selected_grids("up")

    def grid_move_down_clicked(self):
        self.move_selected_grids("down")

    def move_selected_grids(self, direction):
        for grid_treewidget_item in self.manager_widget.grid_treewidget.selectedItems():
            grid_item = self.__grid_map.keys()[
                self.__grid_map.values().index(grid_treewidget_item)
            ]
            grid_item.move_by_pix(direction)

    def display_points_toggled(self, state):
        """
        Display points only according to state
        """
        self.display_only_type_button_clicked("Point", state)
                    
    def display_lines_toggled(self, state):
        """
        Display lines only according to state
        """
        self.display_only_type_button_clicked("Line", state)
        
    def display_grids_toggled(self, state):
        """
        Display grids only according to state
        """
        self.display_only_type_button_clicked("Grid", state)
        
    def display_squares_toggled(self, state):
        """
        Display squares only according to state
        """
        self.display_only_type_button_clicked("Square", state)
        
    def display_only_type_button_clicked(self, shape_type, state):
        
        if state == QtImport.Qt.Checked:
            for shape, treewidget_item in self.__shape_map.items():
                print(f"display_only_type_button_clicked {treewidget_item.data(1, QtImport.Qt.DisplayRole,)}")
                if shape_type in str(treewidget_item.data(1, QtImport.Qt.DisplayRole,)):
                    shape.show()
                    treewidget_item.setData(2, QtImport.Qt.DisplayRole, "True")
                else:
                    shape.hide()
                    treewidget_item.setData(2, QtImport.Qt.DisplayRole, "False")
    
    def load_list_of_operational_modes(self):
        """
        Parse xml file and load list of operational modes :

        'tag0', 'tag1', ...
        """
        xml_file_tree = cElementTree.parse(self.__op_modes_file_path)

        xml_tree = xml_file_tree.getroot()
        mode_list = []
        if xml_tree.find("operational_modes") is not None:
            #print(f"xml_tree.find(operational_modes) is not None:")
            mode_list = xml_tree.find("operational_modes").text

        print(f"list_of_operational_modes :mode_list {mode_list} - {type(mode_list)}")
        self.__list_of_tags = eval(mode_list)
    
    def export_data(self):
        """
        create data and export it
        """
        self.create_export_data()

        formats = [
            "txt",
            "json",
            "csv"
        ]

        current_file_name = "%s/%s_%d.%s" % (
            expanduser("~"),
            self.__export_file_prefix,
            self.__export_file_index,
            "txt",
        )
        filename, _filter = QtImport.QFileDialog.getSaveFileName(
                self,
                "Choose a filename to save under",
                current_file_name,
                "Text files (%s)" % " ".join(formats),
            )
        
        if filename:
            data_to_export = self.create_export_data()
            try:
                #self.graphics_manager_hwobj.save_scene_snapshot(filename)
                print(f"filename : {filename}")
                data_file = open(filename, 'w')
                pprint(data_to_export, data_file)
                self.__export_file_index += 1
            except BaseException:
                logging.getLogger("HWR").error("GraphicsManagerBrick: error saving data!")
        