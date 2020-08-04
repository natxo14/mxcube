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

import json
import os
import copy
import datetime
from datetime import date

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Graphics"


class GraphicsManagerBrick(BaseWidget):

    get_operational_modes_list_signal = QtImport.pyqtSignal(object)

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
        
        # Properties ----------------------------------------------------------
        self.add_property("beam_cal_data_file", "string", "")
        
        # Signals ------------------------------------------------------------
        self.define_signal("get_operational_modes_list_signal", ())

        # Slots ---------------------------------------------------------------
        self.define_slot("set_data_path", ())
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

        self.manager_widget.display_all_button.clicked.connect(
            self.display_all_button_clicked
        )
        self.manager_widget.hide_all_button.clicked.connect(
            self.hide_all_button_clicked
        )
        self.manager_widget.clear_all_button.clicked.connect(
            self.clear_all_button_clicked
        )

        self.manager_widget.create_point_start_button.clicked.connect(
            self.create_point_start_button_clicked
        )
        self.manager_widget.create_point_accept_button.clicked.connect(
            self.create_point_accept_button_clicked
        )
        self.manager_widget.create_line_button.clicked.connect(
            self.create_line_button_clicked
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

        self.manager_widget.create_square_button.clicked.connect(
            self.create_square_clicked
        )

        tmp = self.manager_widget.export_data_button.clicked.connect(
            self.export_data
        )
        print(f"connection : {tmp}")


        # SizePolicies --------------------------------------------------------

        # Other ---------------------------------------------------------------
        self.manager_widget.shapes_treewidget.setContextMenuPolicy(
            QtImport.Qt.CustomContextMenu
        )

        tmp = self.manager_widget.shapes_treewidget.customContextMenuRequested.connect(
            self.prepare_tree_widget_menu
        )
        print(f"connection 2: {tmp}")

        # by default manager is closed
        self.main_groupbox.setCheckable(True)
        self.main_groupbox.setChecked(True)
        self.main_groupbox_toggled(True)
        # self.main_groupbox.setToolTip("Click to open/close item manager")

        #self.manager_widget.display_all_button.hide()

        self.connect(HWR.beamline.sample_view, "shapeCreated", self.shape_created)
        self.connect(HWR.beamline.sample_view, "shapeDeleted", self.shape_deleted)
        self.connect(HWR.beamline.sample_view, "shapeSelected", self.shape_selected)
        self.connect(
            HWR.beamline.sample_view,
            "centringInProgress",
            self.centring_in_progress_changed
        )
        self.connect(HWR.beamline.sample_view, "escape_pressed", self.escape_pressed)

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
        selection_menu.addSection("Select shape's nature")

        for tag in self.__list_of_tags:
            print(f"tag : {tag}")
            new_action = QtImport.QAction(tag, selection_menu)
            new_action.setData(tag)
            # new_action.triggered.connect(
            #     self.tree_widget_menu_selected
            # )
            selection_menu.addAction(new_action)
        
        selection_menu.triggered.connect(
            self.tree_widget_menu_selected
        )
        selection_menu.exec(
            self.manager_widget.shapes_treewidget.mapToGlobal(pos)
        )

    def tree_widget_menu_selected(self, action):
        """
        change shape's information according to selected value
        """
        print(f"selected tag : {action} -  action data {action.data()}")
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
        info_str_list = (
            str(self.manager_widget.shapes_treewidget.topLevelItemCount() + 1),
            shape.get_display_name(),
            str(True),
            str(True),
            str("Right click to select collection"),
        )
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
            info_str_list.append(str(shape.get_start_position()))
            info_str_list.append(str(shape.get_end_position()))
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
            print(f"GRPHICMANAGERBRICK shape_selected shape in self.__shape_map:")
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

    def centring_in_progress_changed(self, centring_in_progress):
        if centring_in_progress:
            self.manager_widget.create_point_start_button.setIcon(
                Icons.load_icon("Delete")
            )
        else:
            self.manager_widget.create_point_start_button.setIcon(
                Icons.load_icon("VCRPlay2")
            )

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

    def display_all_button_clicked(self):
        for shape, treewidget_item in self.__shape_map.items():
            shape.show()
            treewidget_item.setData(2, QtImport.Qt.DisplayRole, "True")
    
    def display_all_toggled(self, state):
        if state == QtImport.Qt.Checked:
            self.display_all_button_clicked()

        self.manager_widget.display_all_cbox.setChecked(True)

    def hide_all_button_clicked(self):
        
        for shape, treewidget_item in self.__shape_map.items():
            shape.hide()
            treewidget_item.setData(2, QtImport.Qt.DisplayRole, "False")

        self.mutual_exclusive_bg.setExclusive(False)
       
        self.manager_widget.display_points_cbox.setCheckState(QtImport.Qt.Unchecked)
        self.manager_widget.display_lines_cbox.setCheckState(QtImport.Qt.Unchecked)
        self.manager_widget.display_grids_cbox.setCheckState(QtImport.Qt.Unchecked)
        self.manager_widget.display_square_roi_cbox.setCheckState(QtImport.Qt.Unchecked)
        self.manager_widget.display_all_cbox.setCheckState(QtImport.Qt.Unchecked)
        
        self.mutual_exclusive_bg.setExclusive(True)

    def clear_all_button_clicked(self):
        HWR.beamline.sample_view.clear_all_shapes()

    def create_point_start_button_clicked(self):
        # HWR.beamline.sample_view.start_centring(tree_click=True)
        HWR.beamline.sample_view.start_one_click_centring()

    def create_point_accept_button_clicked(self):
        HWR.beamline.sample_view.start_centring()

    def create_line_button_clicked(self):
        HWR.beamline.sample_view.create_line()

    def draw_grid_button_clicked(self):
        HWR.beamline.sample_view.create_grid(self.get_spacing())
    
    def create_square_clicked(self):
        HWR.beamline.sample_view.create_square_roi()

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
        #self.manager_widget.display_lines_cbox.setEnabled(len(self.__shape_map) > 0)
        #self.manager_widget.display_grids_cbox.setEnabled(len(self.__shape_map) > 0)
        self.manager_widget.display_square_roi_cbox.setEnabled(len(self.__shape_map) > 0)

        self.manager_widget.display_all_button.setEnabled(len(self.__shape_map) > 0)
        self.manager_widget.hide_all_button.setEnabled(len(self.__shape_map) > 0)
        self.manager_widget.clear_all_button.setEnabled(len(self.__shape_map) > 0)

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
                if shape_type in  str(treewidget_item.data(1, QtImport.Qt.DisplayRole,)):
                    shape.show()
                    treewidget_item.setData(2, QtImport.Qt.DisplayRole, "True")
                else:
                    shape.hide()
                    treewidget_item.setData(2, QtImport.Qt.DisplayRole, "False")
        else:
            self.display_all_button_clicked()
    
    def export_data(self):
        """
        create data and export it
        """
        self.create_export_data()

    def create_export_data(self):
        """
        return dictionnary with data to be exported
        {
            "timestamp" : datetime.now()
            "diff_motors" : { 
                            "mot0.name": pos0
                            "mot1.name": pos1
                             ...
                            }
            "positions_dict" : { 
                                "pos_name_i" : {
                                            "beam_pos_x" : val, int - pixels
                                            "beam_pos_y" : val, int - pixels
                                            "cal_x" : val, int - nm / pixel
                                            "cal_y" : val, int - nm / pixel
                                            "light" : val,
                                            "zoom" : val,
                                             },
                               }
            "selected_shapes_dict": {
                                    "selected_shape1_name":
                                        {
                                        "type" : string
                                        "index" : int
                                        "collection: string ( 'visible', 'background'...)
                                        "centred_position" : dict
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
        
        positions_dict = {}
        
        #self.toto_signal.emit(positions_dict)

        print(f"create_export_data positions_dict {positions_dict}")

        data = {}

        now = datetime.datetime.now()
        data['timestamp'] = str(now)

        diff_motors_dict = {}
        if HWR.beamline.diffractometer is not None:
            diff_motors_dict = HWR.beamline.diffractometer.get_motors_dict()
            print(f"motor dict from Diffracto : {diff_motors_dict}")

        data['diff_motors'] = diff_motors_dict


        data["positions_dict"] = copy.deepcopy(positions_dict)

        
        selected_shapes_dict = {}

        for selected_item in self.manager_widget.shapes_treewidget.selectedItems():
            
            key = selected_item.data(1, QtImport.Qt.DisplayRole)
            shape_type = key.split()[0]
            index = key.split()[-1]
            collection = selected_item.data(4, QtImport.Qt.DisplayRole)
            if collection == "Right click to select collection":
                collection = "not_defined"

            centred_position = {}
            for shape, dict_item in self.__shape_map.items():
                if dict_item == selected_item:
                    centred_position = shape.get_centred_position()
            
            shape_dict = {}
            shape_dict["type"] = shape_type
            shape_dict["index"] = index
            shape_dict["collection"] = collection
            shape_dict["centred_position"] = centred_position

            selected_shapes_dict[key] = shape_dict

        data["selected_shapes_dict"] = selected_shapes_dict

        from pprint import pprint
        pprint(f"create_export_data data {data}")
            
        

