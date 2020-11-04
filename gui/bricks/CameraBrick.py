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

import logging
from os.path import expanduser
from gui.utils import Icons, QtImport
from gui.BaseComponents import BaseWidget
from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "Graphics"


class CameraBrick(BaseWidget):

    create_centring_point_button_toggled = QtImport.pyqtSignal(bool)
    
    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.graphics_manager_hwobj = None

        # Signals ------------------------------------------------------------
        self.define_signal("create_centring_point_button_toggled", ())
        
        # Slots ---------------------------------------------------------------
        self.define_slot("toggle_create_point_start_button", ())
        self.define_slot("set_camera_expo_and_gain_sliders", ())

        # Internal values -----------------------------------------------------
        self.graphics_scene_size = None
        self.graphics_scene_fixed_size = None
        self.graphics_view = None
        self.fixed_size = None
        self.display_beam = None
        self.display_scale = None
        self.image_scale_list = []
        self.snapshot_file_prefix = "snapshot"
        self.snapshot_file_index = 0

        # Properties ----------------------------------------------------------
        self.add_property("mnemonic", "string", "/graphics")
        self.add_property("fixedSize", "string", "")
        self.add_property("displayBeam", "boolean", True)
        self.add_property("displayScale", "boolean", True)
        self.add_property("displayOmegaAxis", "boolean", True)
        self.add_property("beamDefiner", "boolean", False)
        self.add_property("cameraControls", "boolean", False)
        
        # Graphic elements-----------------------------------------------------
        self.toolbar = QtImport.QToolBar(self)
        self.info_widget = QtImport.QWidget(self)
        self.display_beam_size_cbox = QtImport.QCheckBox("Display beam size", self)
        self.display_beam_size_cbox.setHidden(False)
        self.coord_label = QtImport.QLabel(":", self)
        self.info_label = QtImport.QLabel(self)
        self.camera_control_dialog = CameraControlDialog(self)

        self._camera_expo_spin_slider = None
        self._camera_gain_spin_slider = None

        self.move_center_to_clicked_point_button = None
        self.create_centring_point_button = None
        self.select_button = None

        # populate QMenu and QToolBar-----------------------------------------------------
        
        self.popup_menu = QtImport.QMenu(self)
        self.popup_menu.menuAction().setIconVisibleInMenu(True)

        # Select press button

        icon = QtImport.QIcon()
        qpixmap_inactive = Icons.load_pixmap("select")
        qpixmap_active = Icons.load_pixmap("select-pressed")
        
        icon.addPixmap(
            qpixmap_active,
            QtImport.QIcon.Normal,
            QtImport.QIcon.On,
        )
        icon.addPixmap(
            qpixmap_inactive,
            QtImport.QIcon.Normal,
            QtImport.QIcon.Off,
        )

        self.select_button = self.popup_menu.addAction(
            icon,
            "Select items in image",
        )
        self.select_button.setCheckable(True)
        self.select_button.toggled.connect(
            self.select_button_toggled
        )
        
        self.toolbar.addAction(self.select_button)

        create_menu = self.popup_menu.addMenu(
            Icons.load_icon("draw"),
            "Draw"
        )
        
        # CENTRING out of menus : only in centring brick
        # temp_action = create_menu.addAction(
        #     Icons.load_icon("VCRPlay2"),
        #     "Centring with N points",
        #     self.create_point_click_clicked,
        # )
        # temp_action.setShortcut("Ctrl+1")

        # tmp_menu.addAction(temp_action)

        # Draw Menu:
        # Centring point in beam position
        # Centring point on click
        # Helical Line and Square

        tmp_menu = QtImport.QMenu("Draw", self.toolbar)

        icon = QtImport.QIcon()
        qpixmap_inactive = Icons.load_pixmap("draw")
        qpixmap_active = Icons.load_pixmap("draw-pressed")
        
        icon.addPixmap(
            qpixmap_active,
            QtImport.QIcon.Normal,
            QtImport.QIcon.On,
        )
        icon.addPixmap(
            qpixmap_inactive,
            QtImport.QIcon.Normal,
            QtImport.QIcon.Off,
        )

        tmp_menu.setIcon(icon)

        temp_action = create_menu.addAction(
            Icons.load_icon("beam2"),
            "Centring point on beam position",
            self.create_point_current_clicked,
        )
        temp_action.setShortcut("Ctrl+2")

        tmp_menu.addAction(temp_action)
        
        icon_point = QtImport.QIcon()
        qpixmap_inactive = Icons.load_pixmap("calibration_point")
        qpixmap_active = Icons.load_pixmap("calibration_point_selected")
        
        icon_point.addPixmap(
            qpixmap_active,
            QtImport.QIcon.Normal,
            QtImport.QIcon.On,
        )
        icon_point.addPixmap(
            qpixmap_inactive,
            QtImport.QIcon.Normal,
            QtImport.QIcon.Off,
        )

        self.create_centring_point_button = create_menu.addAction(
            icon_point,
            "Centring points with one click",
        )
        self.create_centring_point_button.setCheckable(True)
        self.create_centring_point_button.toggled.connect(
            self.create_points_one_click_clicked
        )
        
        tmp_menu.addAction(self.create_centring_point_button)
                
        temp_action = create_menu.addAction(
            Icons.load_icon("Line.png"), "Helical line", self.create_line_clicked
        )
        temp_action.setShortcut("Ctrl+3")

        tmp_menu.addAction(temp_action)

        temp_action = create_menu.addAction(
            Icons.load_icon("Line.png"),
            "Automatic helical line",
            self.create_auto_line_clicked,
        )
        temp_action = create_menu.addAction(
            Icons.load_icon("Grid"), "Grid", self.create_grid
        )
        temp_action.setShortcut("Ctrl+4")
        temp_action = create_menu.addAction(
            Icons.load_icon("AutoGrid"), "Auto Grid", self.create_auto_grid
        )

        temp_action = QtImport.QAction(
            Icons.load_icon("square"), "Square ROI", tmp_menu
        )
        temp_action.triggered.connect(self.create_square_roi)

        tmp_menu.addAction(temp_action)

        self.toolbar.addAction(tmp_menu.menuAction())

        # move to pos menu
        # move_to_pos_menu = self.

        # Move to Position Menu:
        # Move to Position Y and Z
        # Move to Position on Horizontal
        # Move to Position on Vertical

        icon1 = QtImport.QIcon()
        qpixmap_inactive = Icons.load_pixmap("movetopos")
        qpixmap_active = Icons.load_pixmap("movetopos-pressed")
        
        icon1.addPixmap(
            qpixmap_active,
            QtImport.QIcon.Normal,
            QtImport.QIcon.On,
        )
        icon1.addPixmap(
            qpixmap_inactive,
            QtImport.QIcon.Normal,
            QtImport.QIcon.Off,
        )

        move_to_pos_menu = QtImport.QMenu("Move to Position", self.toolbar)
        move_to_pos_menu.setIcon(icon1)
        
        self.move_center_to_clicked_point_button = QtImport.QAction(
            icon1,
            "Move point to beam",
        )
        self.move_center_to_clicked_point_button.setCheckable(True)
        self.move_center_to_clicked_point_button.toggled.connect(
            self.move_center_to_clicked_point
        )
        
        move_to_pos_menu.addAction(self.move_center_to_clicked_point_button)

        icon = QtImport.QIcon()
        qpixmap_inactive = Icons.load_pixmap("movetoposhorizontal")
        qpixmap_active = Icons.load_pixmap("movetoposhorizontal-pressed")
        
        icon.addPixmap(
            qpixmap_active,
            QtImport.QIcon.Normal,
            QtImport.QIcon.On,
        )
        icon.addPixmap(
            qpixmap_inactive,
            QtImport.QIcon.Normal,
            QtImport.QIcon.Off,
        )

        self.move_hor_center_to_clicked_point_button = QtImport.QAction(
            icon,
            "Move horizontally point to beam",
        )
        self.move_hor_center_to_clicked_point_button.setCheckable(True)
        self.move_hor_center_to_clicked_point_button.toggled.connect(
            self.move_hor_center_to_clicked_point
        )

        move_to_pos_menu.addAction(self.move_hor_center_to_clicked_point_button)

        icon = QtImport.QIcon()
        qpixmap_inactive = Icons.load_pixmap("movetoposvertical")
        qpixmap_active = Icons.load_pixmap("movetoposvertical-pressed")
        
        icon.addPixmap(
            qpixmap_active,
            QtImport.QIcon.Normal,
            QtImport.QIcon.On,
        )
        icon.addPixmap(
            qpixmap_inactive,
            QtImport.QIcon.Normal,
            QtImport.QIcon.Off,
        )

        self.move_ver_center_to_clicked_point_button = QtImport.QAction(
            icon,
            "Move verticallly point to beam",
        )
        self.move_ver_center_to_clicked_point_button.setCheckable(True)
        self.move_ver_center_to_clicked_point_button.toggled.connect(
            self.move_ver_center_to_clicked_point
        )

        move_to_pos_menu.addAction(self.move_ver_center_to_clicked_point_button)

        self.popup_menu.addMenu(move_to_pos_menu)
        
        move_beam_menu = MultiModeAction(self.toolbar)
        move_beam_menu.addAction(self.move_center_to_clicked_point_button)
        move_beam_menu.addAction(self.move_hor_center_to_clicked_point_button)
        move_beam_menu.addAction(self.move_ver_center_to_clicked_point_button)

        self.toolbar.addAction(move_beam_menu)

        ##################################################

        measure_menu = self.popup_menu.addMenu(
            Icons.load_icon("measure_icon"),
            "Measure",
        )
        self.measure_distance_action = measure_menu.addAction(
            Icons.load_icon("measure_distance"),
            "Distance",
        )
        self.measure_distance_action.setCheckable(True)
        self.measure_distance_action.toggled.connect(
            self.measure_distance_clicked
        )

        self.measure_angle_action = measure_menu.addAction(
            Icons.load_icon("measure_angle"),
            "Angle",
        )
        self.measure_angle_action.setCheckable(True)
        self.measure_angle_action.toggled.connect(
            self.measure_angle_clicked
        )

        self.measure_area_action = measure_menu.addAction(
            Icons.load_icon("measure_area"),
            "Area",
        )
        self.measure_area_action.setCheckable(True)
        self.measure_area_action.toggled.connect(
            self.measure_area_clicked
        )
        
        toolbar_measure_menu = MultiModeAction(self.toolbar, Icons.load_icon("measure_icon"))
        toolbar_measure_menu.addAction(self.measure_distance_action)
        toolbar_measure_menu.addAction(self.measure_angle_action)
        toolbar_measure_menu.addAction(self.measure_area_action)
        toolbar_measure_menu.init_display()

        self.toolbar.addAction(toolbar_measure_menu)

        ##################################################

        beam_mark_menu = self.popup_menu.addMenu(
            Icons.load_icon("beam2"),
            "Beam mark",
        )
        self.move_beam_mark_manual_action = beam_mark_menu.addAction(
            "Set position manually", self.move_beam_mark_manual
        )
        self.move_beam_mark_auto_action = beam_mark_menu.addAction(
            "Set position automaticaly", self.move_beam_mark_auto
        )
        self.display_beam_size_action = beam_mark_menu.addAction(
            "Display beam size",
        )
        self.display_beam_size_action.setCheckable(True)
        self.display_beam_size_action.toggled.connect(
            self.display_beam_size_toggled
        )
        self.display_beam_action = beam_mark_menu.addAction(
            "Display beam mark", self.display_beam_toggled
        )
        self.display_beam_action.setCheckable(True)
        self.display_beam_action.setChecked(True)

        self.toolbar.addAction(beam_mark_menu.menuAction())

        self.define_beam_action = self.popup_menu.addAction(
            Icons.load_icon("Draw"),
            "Define beam size with slits",
            self.define_beam_size,
        )
        self.define_beam_action.setEnabled(False)
        self.popup_menu.addSeparator()

        temp_action = self.popup_menu.addAction(
            "Select all centring points", self.select_all_points_clicked
        )
        temp_action.setShortcut("Ctrl+A")
        temp_action = self.popup_menu.addAction(
            "Deselect all items", self.deselect_all_items_clicked
        )
        temp_action.setShortcut("Ctrl+D")
        temp_action = self.popup_menu.addAction(
            Icons.load_icon("Delete"), "Clear all items", self.clear_all_items_clicked
        )
        temp_action.setShortcut("Ctrl+X")
        self.popup_menu.addSeparator()

        tools_menu = self.popup_menu.addMenu(
            Icons.load_icon("tools"),
            "Tools",
        )
        self.display_grid_action = tools_menu.addAction(
            Icons.load_icon("Grid"), "Display grid", self.display_grid_toggled
        )
        self.display_grid_action.setCheckable(True)
        self.display_histogram_action = tools_menu.addAction(
            Icons.load_icon("Grid"),
            "Display historgram",
            self.display_histogram_toggled,
        )
        self.display_histogram_action.setCheckable(True)
        self.magnification_action = tools_menu.addAction(
            Icons.load_icon("Magnify2"),
            "Magnification tool",
        )

        self.magnification_action.toggled.connect(
            self.start_magnification_tool
        )

        self.toolbar.addAction(tools_menu.menuAction())

        self.magnification_action.setCheckable(True)
        
        self.image_scale_menu = self.popup_menu.addMenu(
            Icons.load_icon("DocumentMag2"), "Image scale"
        )
        self.image_scale_menu.setEnabled(False)
        self.image_scale_menu.triggered.connect(self.image_scale_triggered)
        
        self.toolbar.addAction(self.image_scale_menu.menuAction())

        temp_action = QtImport.QAction(
            Icons.load_icon("Camera"), "Snapshot", self.toolbar
        )
        temp_action.triggered.connect(self.save_snapshot_clicked)

        self.toolbar.addAction(temp_action)

        camera_expo_gain_menu = self.popup_menu.addMenu(
            Icons.load_icon("camera-exposure"),
            "Camera Exposure and Gain",
        )

        self._camera_expo_spin_slider = SpinAndSliderAction(0.05, 2.0, "Camera Exposition")
        self._camera_expo_spin_slider.value_changed.connect(
            self._set_camera_exposure_time
        )
        camera_expo_gain_menu.addAction(
            self._camera_expo_spin_slider
        )

        camera_expo_gain_menu.addSeparator()

        self._camera_gain_spin_slider = SpinAndSliderAction(0, 1.0, "Camera Gain")
        self._camera_gain_spin_slider.value_changed.connect(
            self._set_camera_gain
        )
        camera_expo_gain_menu.addAction(
            self._camera_gain_spin_slider
        )

        self.toolbar.addAction(camera_expo_gain_menu.menuAction())

        self.camera_control_action = self.popup_menu.addAction(
            "Camera control", self.open_camera_control_dialog
        )
        self.camera_control_action.setEnabled(False)

        # Another objects--------------------------------------------
        self.exclusive_action_group = QtImport.QActionGroup(self.toolbar)
        self.exclusive_action_group.addAction(
            self.move_center_to_clicked_point_button
        )
        self.exclusive_action_group.addAction(
            self.move_hor_center_to_clicked_point_button
        )
        self.exclusive_action_group.addAction(
            self.move_ver_center_to_clicked_point_button
        )
        self.exclusive_action_group.addAction(
            self.create_centring_point_button
        )
        self.exclusive_action_group.addAction(
            self.select_button
        )
        self.exclusive_action_group.addAction(
            self.measure_distance_action
        )
        self.exclusive_action_group.addAction(
            self.measure_angle_action
        )
        self.exclusive_action_group.addAction(
            self.measure_area_action
        )

        self.exclusive_action_group.addAction(
            self.magnification_action
        )
        
        # Layout --------------------------------------------------------------
        _info_widget_hlayout = QtImport.QHBoxLayout(self.info_widget)
        _info_widget_hlayout.addWidget(self.display_beam_size_cbox)
        _info_widget_hlayout.addWidget(self.coord_label)
        _info_widget_hlayout.addStretch(0)
        _info_widget_hlayout.addWidget(self.info_label)
        _info_widget_hlayout.setSpacing(0)
        _info_widget_hlayout.setContentsMargins(0, 0, 0, 0)
        self.info_widget.setLayout(_info_widget_hlayout)

        self.main_layout = QtImport.QVBoxLayout(self)
        self.intern_main_layout = QtImport.QHBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Qt signal/slot connections -----------------------------------------
        self.display_beam_size_cbox.stateChanged.connect(self.display_beam_size_toggled)

        # SizePolicies --------------------------------------------------------
        self.info_widget.setSizePolicy(
            QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Fixed
        )

        # Scene elements ------------------------------------------------------
        self.setMouseTracking(True)
        self.toolbar.setOrientation(QtImport.Qt.Vertical)
                
    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            if self.graphics_manager_hwobj is not None:
                self.disconnect(
                    self.graphics_manager_hwobj, "mouseMoved", self.mouse_moved
                )
                self.disconnect(
                    self.graphics_manager_hwobj, "imageScaleChanged", self.image_scaled
                )
                self.disconnect(
                    self.graphics_manager_hwobj, "infoMsg", self.set_info_msg
                )
                self.disconnect(
                    self.graphics_manager_hwobj, "escape_pressed", self.escape_pressed
                )

            self.graphics_manager_hwobj = self.get_hardware_object(new_value)

            if self.graphics_manager_hwobj is not None:
                self.connect(
                    self.graphics_manager_hwobj, "mouseMoved", self.mouse_moved
                )
                self.connect(
                    self.graphics_manager_hwobj, "imageScaleChanged", self.image_scaled
                )
                self.connect(self.graphics_manager_hwobj, "infoMsg", self.set_info_msg)
                self.connect(
                    self.graphics_manager_hwobj, "escape_pressed", self.escape_pressed
                )

                self.graphics_view = self.graphics_manager_hwobj.get_graphics_view()
                self.intern_main_layout.addWidget(self.graphics_view)
                self.intern_main_layout.addWidget(self.toolbar)
                self.main_layout.addLayout(self.intern_main_layout)
                self.main_layout.addWidget(self.info_widget)
                self.set_fixed_size()
                self.init_image_scale_list()
                if hasattr(self.graphics_manager_hwobj, "camera"):
                    self.camera_control_dialog.set_camera_hwobj(
                        self.graphics_manager_hwobj.camera
                    )
                    
                    #set gain/expo control's values from camera
                    camera_expo_limits = self.graphics_manager_hwobj.camera.get_exposure_limits()
                    #self._camera_expo_spin_slider.set_limits(*camera_expo_limits)

                    camera_gain = self.graphics_manager_hwobj.camera.get_gain()
                    camera_expo = self.graphics_manager_hwobj.camera.get_exposure_time()
                                        
                    self._camera_expo_spin_slider.set_value(camera_expo)
                    self._camera_gain_spin_slider.set_value(camera_gain)

                # Init gui -------------------------------------------------------------
                self.select_button.setChecked(True)
                    
        elif property_name == "fixedSize":
            try:
                fixed_size = list(map(int, new_value.split()))
                if len(fixed_size) == 2:
                    self.fixed_size = fixed_size
                    self.set_fixed_size()
            except BaseException:
                pass
        elif property_name == "displayBeam":
            self.display_beam = new_value
        elif property_name == "displayScale":
            self.display_scale = new_value
            if self.graphics_manager_hwobj is not None:
                if hasattr(self.graphics_manager_hwobj, "set_scale_visible"):
                    # NBNB Where did this code come from? SHould probvably be removed
                    # no known function "set_scale_visible" anywhere. TODO remove
                    self.graphics_manager_hwobj.set_scale_visible(new_value)
                else:
                    logging.getLogger().info(
                        "No such function: sample_view.set_scale_visible()"
                    )

        elif property_name == "beamDefiner":
            self.define_beam_action.setEnabled(new_value)
        elif property_name == "cameraControls":
            self.camera_control_action.setEnabled(new_value)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def escape_pressed(self):
        """
        'Unpress' all press buttons
        """
        self.select_button.setChecked(True)
        
    def display_beam_size_toggled(self, state):

        self.display_beam_size_action.setChecked(state)
        self.display_beam_size_cbox.setChecked(state)

        self.graphics_manager_hwobj.display_beam_size(
            self.display_beam_size_action.isChecked()
        )

    def display_beam_toggled(self):
        self.graphics_manager_hwobj.display_beam(
            self.display_beam_action.isChecked()
        )

    def start_magnification_tool(self, checked):
        self.graphics_manager_hwobj.set_magnification_mode(checked)

    def set_control_mode(self, have_control):
        if have_control:
            self.graphics_manager_hwobj.hide_info_msg()
        else:
            self.graphics_manager_hwobj.display_info_msg(
                [
                    "",
                    "Controls are disabled in the Slave mode",
                    "",
                    "Ask for control to be able to control MXCuBE" "",
                ],
                hide_msg=False,
            )

    def set_info_msg(self, msg):
        self.info_label.setText(msg)

    def set_fixed_size(self):
        if self.fixed_size and self.graphics_manager_hwobj:
            self.graphics_manager_hwobj.set_graphics_scene_size(self.fixed_size, True)
            self.graphics_view.setFixedSize(self.fixed_size[0], self.fixed_size[1])
    
    def image_scaled(self, scale_value):
        for index, action in enumerate(self.image_scale_menu.actions()):
            action.setChecked(scale_value == self.image_scale_list[index])

    def init_image_scale_list(self):
        self.image_scale_list = self.graphics_manager_hwobj.get_image_scale_list()
        if len(self.image_scale_list) > 0:
            self.image_scale_menu.setEnabled(True)
            self.image_scale_action_group = QtImport.QActionGroup(self.image_scale_menu)
            for scale in self.image_scale_list:
                # probably there is a way to use a single method for all actions
                # by passing index. lambda function at first try did not work
                action_temp = self.image_scale_menu.addAction(
                    "%d %%" % (scale * 100), self.not_used_function
                )
                self.image_scale_action_group.addAction(action_temp)
            for action in self.image_scale_menu.actions():
                action.setCheckable(True)
            
            self.image_scaled(self.graphics_manager_hwobj.get_image_scale())

    def not_used_function(self, *arg):
        pass

    def image_scale_triggered(self, selected_action):
        for index, action in enumerate(self.image_scale_menu.actions()):
            if selected_action == action:
                self.graphics_manager_hwobj.set_image_scale(
                    self.image_scale_list[index], action.isChecked()
                )

    def contextMenuEvent(self, event):
        self.popup_menu.popup(QtImport.QCursor.pos())

    def measure_distance_clicked(self, checked):
        if checked:
            self.graphics_manager_hwobj.start_measure_distance(wait_click=True)
        else:
            self.graphics_manager_hwobj.stop_measure_distance()

    def measure_angle_clicked(self, checked):
        if checked:
            self.graphics_manager_hwobj.start_measure_angle(wait_click=True)
        else:
            self.graphics_manager_hwobj.stop_measure_angle()
        
    def measure_area_clicked(self, checked):
        if checked:
            self.graphics_manager_hwobj.start_measure_area(wait_click=True)
        else:
            self.graphics_manager_hwobj.stop_measure_area(wait_click=True)
        
    def display_histogram_toggled(self):
        self.graphics_manager_hwobj.display_histogram(
            self.display_histogram_action.isChecked()
        )

    def set_camera_expo_and_gain_sliders(self, new_zoom_pos_dict):
        """
        slot connected to multiple positions brick
        adjust gain and expo automatically when changing zoom
        """
        new_expo = new_zoom_pos_dict["exposure"]
        new_gain = new_zoom_pos_dict["gain"]
        if new_expo:
            self.set_camera_exposure_time_slider(new_expo)
        if new_gain:
            self.set_camera_gain_slider(new_gain)

    def toggle_create_point_start_button(self, checked):
        """
        slot connected to GraphicsManagerBrick
        if checked is false => check select_item checkbutton
        """
        if checked:
            self.create_centring_point_button.setChecked(checked)
        else:
            # check if any of the exclusive action group is checked:
            if self.exclusive_action_group.checkedAction() == self.create_centring_point_button:
                self.select_button.setChecked(True)

    def create_point_click_clicked(self):
        self.graphics_manager_hwobj.start_centring(tree_click=True)

    def select_button_toggled(self, checked):
        if checked:
            self.graphics_manager_hwobj.stop_current_state()

    def create_points_one_click_clicked(self, checked):
        if checked:
            self.graphics_manager_hwobj.start_one_click_centring()
        else:
            self.graphics_manager_hwobj.stop_one_click_centring()
        
        self.create_centring_point_button_toggled.emit(checked)
        
    def move_center_to_clicked_point(self, checked):
        self.graphics_manager_hwobj.move_beam_to_clicked_point_clicked(checked)

    def move_hor_center_to_clicked_point(self, checked):
        self.graphics_manager_hwobj.move_beam_to_clicked_point_clicked(
            checked, direction="horizontal"
        )
   
    def move_ver_center_to_clicked_point(self, checked):
        self.graphics_manager_hwobj.move_beam_to_clicked_point_clicked(
            checked, direction="vertical"
        )

    def create_point_current_clicked(self):
        self.graphics_manager_hwobj.start_centring(tree_click=False)

    def create_line_clicked(self):
        self.graphics_manager_hwobj.create_line()

    def create_auto_line_clicked(self):
        self.graphics_manager_hwobj.create_auto_line()

    def create_grid(self):
        self.graphics_manager_hwobj.create_grid()

    def create_auto_grid(self):
        self.graphics_manager_hwobj.create_auto_grid()
    
    def create_square_roi(self):
        self.graphics_manager_hwobj.create_square()

    def move_beam_mark_manual(self):
        self.graphics_manager_hwobj.start_move_beam_mark()

    def move_beam_mark_auto(self):
        self.graphics_manager_hwobj.move_beam_mark_auto()

    def mouse_moved(self, x, y, scene_pixel_QRgb):
        self.coord_label.setText(
            """X: <b>%d</b> Y: <b>%d</b> - QRgb : <b>%d</b> """
            % (
                x,
                y,
                QtImport.qGray(scene_pixel_QRgb),
            )
        )

    def select_all_points_clicked(self):
        self.graphics_manager_hwobj.select_all_points()

    def deselect_all_items_clicked(self):
        self.graphics_manager_hwobj.de_select_all()

    def clear_all_items_clicked(self):
        self.graphics_manager_hwobj.clear_all_shapes()

    def zoom_window_clicked(self):
        self.zoom_dialog.set_camera_frame(
            self.graphics_manager_hwobj.get_camera_frame()
        )
        self.zoom_dialog.set_coord(100, 100)
        self.zoom_dialog.show()

    def open_camera_control_dialog(self):
        self.camera_control_dialog.show()

    def display_grid_toggled(self):
        self.graphics_manager_hwobj.display_grid(
            self.display_grid_action.isChecked()
        )

    def define_beam_size(self):
        self.graphics_manager_hwobj.start_define_beam()

    def display_radiation_damage_toggled(self):
        self.graphics_manager_hwobj.display_radiation_damage(
            self.display_radiation_damage_action.isChecked()
        )
    
    def save_snapshot_clicked(self):
        formats = [
            "*.%s" % str(image_format).lower()
            for image_format in QtImport.QImageWriter.supportedImageFormats()
        ]

        current_file_name = "%s/%s_%d.%s" % (
            expanduser("~"),
            self.snapshot_file_prefix,
            self.snapshot_file_index,
            "png",
        )
        filename, _filter = QtImport.QFileDialog.getSaveFileName(
                self,
                "Choose a filename to save under",
                current_file_name,
                "Image files (%s)" % " ".join(formats),
            )
        
        if filename:
            try:
                self.graphics_manager_hwobj.save_scene_snapshot(filename)
                self.snapshot_file_index += 1
            except BaseException:
                logging.getLogger().exception("CameraBrick: error saving snapshot!")


    def _set_camera_exposure_time(self, expo_value):
        print(f" _set_camera_exposure_time {expo_value}", type(expo_value))
        self.graphics_manager_hwobj.camera.set_exposure_time(
            float(expo_value)
        )

    def set_camera_exposure_time_slider(self, expo_value):
        print(f" set_camera_exposure_time_slider {expo_value}", type(expo_value))
        self._camera_expo_spin_slider.set_value(expo_value)
    
    def _set_camera_gain(self, gain_value):
        print(f" _set_camera_gain {gain_value}", type(gain_value))
        self.graphics_manager_hwobj.camera.set_gain(
            gain_value
        )

    def set_camera_gain_slider(self, gain_value):
        print(f" set_camera_gain_slider {gain_value}", type(gain_value))
        self._camera_gain_spin_slider.set_value(gain_value)
    
    def set_visible_mode(self, checked=False):
        
        pass

    def set_signal_mode(self, checked=False):
        pass

    def set_background_mode(self, checked=False):
        pass

class CameraControlDialog(QtImport.QDialog):
    def __init__(self, parent=None, name=None, flags=0):
        QtImport.QDialog.__init__(
            self,
            parent,
            QtImport.Qt.WindowFlags(flags | QtImport.Qt.WindowStaysOnTopHint),
        )

        # Internal variables --------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.contrast_slider = QtImport.QSlider(QtImport.Qt.Horizontal, self)
        self.contrast_doublespinbox = QtImport.QDoubleSpinBox(self)
        self.contrast_checkbox = QtImport.QCheckBox("auto", self)
        self.brightness_slider = QtImport.QSlider(QtImport.Qt.Horizontal, self)
        self.brightness_doublespinbox = QtImport.QDoubleSpinBox(self)
        self.brightness_checkbox = QtImport.QCheckBox("auto", self)
        self.gain_slider = QtImport.QSlider(QtImport.Qt.Horizontal, self)
        self.gain_doublespinbox = QtImport.QDoubleSpinBox(self)
        self.gain_checkbox = QtImport.QCheckBox("auto", self)
        self.gamma_slider = QtImport.QSlider(QtImport.Qt.Horizontal, self)
        self.gamma_doublespinbox = QtImport.QDoubleSpinBox(self)
        self.gamma_checkbox = QtImport.QCheckBox("auto", self)
        self.exposure_time_slider = QtImport.QSlider(QtImport.Qt.Horizontal, self)
        self.exposure_time_doublespinbox = QtImport.QDoubleSpinBox(self)
        self.exposure_time_checkbox = QtImport.QCheckBox("auto", self)
        __close_button = QtImport.QPushButton("Close", self)

        # Layout --------------------------------------------------------------
        __main_gridlayout = QtImport.QGridLayout(self)
        __main_gridlayout.addWidget(QtImport.QLabel("Contrast:", self), 0, 0)
        __main_gridlayout.addWidget(self.contrast_slider, 0, 1)
        __main_gridlayout.addWidget(self.contrast_doublespinbox, 0, 2)
        __main_gridlayout.addWidget(self.contrast_checkbox, 0, 3)
        __main_gridlayout.addWidget(QtImport.QLabel("Brightness:", self), 1, 0)
        __main_gridlayout.addWidget(self.brightness_slider, 1, 1)
        __main_gridlayout.addWidget(self.brightness_doublespinbox, 1, 2)
        __main_gridlayout.addWidget(self.brightness_checkbox, 1, 3)
        __main_gridlayout.addWidget(QtImport.QLabel("Gain:", self), 2, 0)
        __main_gridlayout.addWidget(self.gain_slider, 2, 1)
        __main_gridlayout.addWidget(self.gain_doublespinbox, 2, 2)
        __main_gridlayout.addWidget(self.gain_checkbox, 2, 3)
        __main_gridlayout.addWidget(QtImport.QLabel("Gamma:", self), 3, 0)
        __main_gridlayout.addWidget(self.gamma_slider, 3, 1)
        __main_gridlayout.addWidget(self.gamma_doublespinbox, 3, 2)
        __main_gridlayout.addWidget(self.gamma_checkbox, 3, 3)
        __main_gridlayout.addWidget(QtImport.QLabel("Exposure time (ms):", self), 4, 0)
        __main_gridlayout.addWidget(self.exposure_time_slider, 4, 1)
        __main_gridlayout.addWidget(self.exposure_time_doublespinbox, 4, 2)
        __main_gridlayout.addWidget(self.exposure_time_checkbox, 4, 3)
        __main_gridlayout.addWidget(__close_button, 6, 2)
        __main_gridlayout.setSpacing(2)
        __main_gridlayout.setContentsMargins(5, 5, 5, 5)
        __main_gridlayout.setSizeConstraint(QtImport.QLayout.SetFixedSize)

        # Qt signal/slot connections ------------------------------------------
        self.contrast_slider.valueChanged.connect(self.set_contrast)
        self.contrast_doublespinbox.valueChanged.connect(self.set_contrast)
        self.contrast_checkbox.stateChanged.connect(self.set_contrast_auto)
        self.brightness_slider.valueChanged.connect(self.set_brightness)
        self.brightness_doublespinbox.valueChanged.connect(self.set_brightness)
        self.brightness_checkbox.stateChanged.connect(self.set_brightness_auto)
        self.gain_slider.valueChanged.connect(self.set_gain)
        self.gain_doublespinbox.valueChanged.connect(self.set_gain)
        self.gain_checkbox.stateChanged.connect(self.set_gain_auto)
        self.gamma_slider.valueChanged.connect(self.set_gamma)
        self.gamma_doublespinbox.valueChanged.connect(self.set_gamma)
        self.gamma_checkbox.stateChanged.connect(self.set_gamma_auto)
        self.exposure_time_slider.valueChanged.connect(self.set_exposure_time)
        self.exposure_time_doublespinbox.valueChanged.connect(self.set_exposure_time)
        self.exposure_time_checkbox.stateChanged.connect(self.set_exposure_time_auto)

        __close_button.clicked.connect(self.close)

        # SizePolicies --------------------------------------------------------
        self.contrast_slider.setFixedWidth(200)
        self.brightness_slider.setFixedWidth(200)
        self.gain_slider.setFixedWidth(200)
        self.gamma_slider.setFixedWidth(200)
        self.exposure_time_slider.setFixedWidth(200)
        __close_button.setSizePolicy(
            QtImport.QSizePolicy.Fixed, QtImport.QSizePolicy.Fixed
        )

        # Other ---------------------------------------------------------------
        self.setModal(True)
        self.setWindowTitle("Camera controls")

    def set_camera_hwobj(self, camera_hwobj):

        # get attribute value
        try:
            contrast_value = self.graphics_manager_hwobj.camera.get_contrast()
        except AttributeError:
            contrast_value = None
        try:
            brightness_value = self.graphics_manager_hwobj.camera.get_brightness()
        except AttributeError:
            brightness_value = None
        try:
            gain_value = self.graphics_manager_hwobj.camera.get_gain()
        except AttributeError:
            gain_value = None
        try:
            gamma_value = self.graphics_manager_hwobj.camera.get_gamma()
        except AttributeError:
            gamma_value = None
        try:
            exposure_time_value = self.graphics_manager_hwobj.camera.get_exposure_time()
        except AttributeError:
            exposure_time_value = None

        # get attribute auto state
        try:
            contrast_auto = self.graphics_manager_hwobj.camera.get_contrast_auto()
        except AttributeError:
            contrast_auto = None
        try:
            brightness_auto = self.graphics_manager_hwobj.camera.get_brightness_auto()
        except AttributeError:
            brightness_auto = None
        try:
            gain_auto = self.graphics_manager_hwobj.camera.get_gain_auto()
        except AttributeError:
            gain_auto = None
        try:
            gamma_auto = self.graphics_manager_hwobj.camera.get_gamma_auto()
        except AttributeError:
            gamma_auto = None
        try:
            exposure_time_auto = self.graphics_manager_hwobj.camera.get_exposure_time_auto()
        except AttributeError:
            exposure_time_auto = None

        # get attribute range
        try:
            contrast_min_max = self.graphics_manager_hwobj.camera.get_contrast_min_max()
        except AttributeError:
            contrast_min_max = (0, 100)
        try:
            brightness_min_max = self.graphics_manager_hwobj.camera.get_brightness_min_max()
        except AttributeError:
            brightness_min_max = (0, 100)
        try:
            gain_min_max = self.graphics_manager_hwobj.camera.get_gain_min_max()
        except AttributeError:
            gain_min_max = (0, 100)
        try:
            gamma_min_max = self.graphics_manager_hwobj.camera.get_gamma_min_max()
        except AttributeError:
            gamma_min_max = (0, 100)
        try:
            exposure_time_min_max = self.graphics_manager_hwobj.camera.get_exposure_time_min_max()
        except AttributeError:
            exposure_time_min_max = (0, 100)

        self.contrast_slider.setDisabled(contrast_value is None)
        self.contrast_doublespinbox.setDisabled(contrast_value is None)
        self.contrast_checkbox.setDisabled(
            contrast_auto is None or contrast_value is None
        )
        self.brightness_slider.setDisabled(brightness_value is None)
        self.brightness_doublespinbox.setDisabled(brightness_value is None)
        self.brightness_checkbox.setDisabled(
            brightness_auto is None or brightness_value is None
        )
        self.gain_slider.setDisabled(gain_value is None)
        self.gain_doublespinbox.setDisabled(gain_value is None)
        self.gain_checkbox.setDisabled(gain_auto is None or gain_value is None)
        self.gamma_slider.setDisabled(gamma_value is None)
        self.gamma_doublespinbox.setDisabled(gamma_value is None)
        self.gamma_checkbox.setDisabled(gamma_auto is None or gamma_value is None)
        self.exposure_time_slider.setDisabled(exposure_time_value is None)
        self.exposure_time_doublespinbox.setDisabled(exposure_time_value is None)
        self.exposure_time_checkbox.setDisabled(
            exposure_time_auto is None or exposure_time_value is None
        )

        if contrast_value:
            self.contrast_slider.setValue(contrast_value)
            self.contrast_slider.setRange(contrast_min_max[0], contrast_min_max[1])
            self.contrast_doublespinbox.setValue(contrast_value)
            self.contrast_doublespinbox.setRange(
                contrast_min_max[0], contrast_min_max[1]
            )
            self.contrast_checkbox.blockSignals(True)
            self.contrast_checkbox.setChecked(bool(contrast_auto))
            self.contrast_checkbox.blockSignals(False)
        if brightness_value:
            self.brightness_slider.setValue(brightness_value)
            self.brightness_slider.setRange(
                brightness_min_max[0], brightness_min_max[1]
            )
            self.brightness_doublespinbox.setValue(brightness_value)
            self.brightness_doublespinbox.setRange(
                brightness_min_max[0], brightness_min_max[1]
            )
            self.brightness_checkbox.blockSignals(True)
            self.brightness_checkbox.setChecked(bool(brightness_auto))
            self.brightness_checkbox.blockSignals(False)
        if gain_value:
            self.gain_slider.setValue(gain_value)
            self.gain_slider.setRange(gain_min_max[0], gain_min_max[1])
            self.gain_doublespinbox.setValue(gain_value)
            self.gain_doublespinbox.setRange(gain_min_max[0], gain_min_max[1])
            self.gain_checkbox.blockSignals(True)
            self.gain_checkbox.setChecked(bool(gain_auto))
            self.gain_checkbox.blockSignals(False)
        if gamma_value:
            self.gamma_slider.setValue(gamma_value)
            self.gamma_slider.setRange(gamma_min_max[0], gamma_min_max[1])
            self.gamma_doublespinbox.setValue(gamma_value)
            self.gamma_doublespinbox.setRange(gamma_min_max[0], gamma_min_max[1])
            self.gamma_checkbox.blockSignals(True)
            self.gamma_checkbox.setChecked(bool(gamma_auto))
            self.gamma_checkbox.blockSignals(False)
        if exposure_time_value:
            self.exposure_time_slider.setValue(exposure_time_value)
            self.exposure_time_slider.setRange(
                exposure_time_min_max[0], exposure_time_min_max[1]
            )
            self.exposure_time_doublespinbox.setValue(exposure_time_value)
            self.exposure_time_doublespinbox.setRange(
                exposure_time_min_max[0], exposure_time_min_max[1]
            )
            self.exposure_time_checkbox.blockSignals(True)
            self.exposure_time_checkbox.setChecked(bool(exposure_time_auto))
            self.exposure_time_checkbox.blockSignals(False)

    def set_contrast(self, value):
        self.contrast_slider.setValue(value)
        self.contrast_doublespinbox.setValue(value)
        self.graphics_manager_hwobj.camera.set_contrast(value)

    def set_brightness(self, value):
        self.brightness_slider.setValue(value)
        self.brightness_doublespinbox.setValue(value)
        self.graphics_manager_hwobj.camera.set_brightness(value)

    def set_gain(self, value):
        self.gain_slider.setValue(value)
        self.gain_doublespinbox.setValue(value)
        self.graphics_manager_hwobj.camera.set_gain(value)

    def set_gamma(self, value):
        self.gamma_slider.setValue(value)
        self.gamma_doublespinbox.setValue(value)
        self.graphics_manager_hwobj.camera.set_gamma(value)

    def set_exposure_time(self, value):
        self.exposure_time_slider.setValue(value)
        self.exposure_time_doublespinbox.setValue(value)
        self.graphics_manager_hwobj.camera.set_exposure_time(value)

    def set_contrast_auto(self, state):
        state = bool(state)
        self.graphics_manager_hwobj.camera.set_contrast_auto(state)
        value = self.graphics_manager_hwobj.camera.get_contrast()
        self.contrast_slider.setValue(value)
        self.contrast_doublespinbox.setValue(value)

    def set_brightness_auto(self, state):
        state = bool(state)
        self.graphics_manager_hwobj.camera.set_brightness_auto(state)
        value = self.graphics_manager_hwobj.camera.get_brightness()
        self.brightness_slider.setValue(value)
        self.brightness_doublespinbox.setValue(value)

    def set_gain_auto(self, state):
        state = bool(state)
        self.graphics_manager_hwobj.camera.set_gain_auto(state)
        value = self.graphics_manager_hwobj.camera.get_gain()
        self.gain_slider.setValue(value)
        self.gain_doublespinbox.setValue(value)

    def set_gamma_auto(self, state):
        state = bool(state)
        self.graphics_manager_hwobj.camera.set_gamma_auto(state)
        value = self.graphics_manager_hwobj.camera.get_gamma()
        self.gamma_slider.setValue(value)
        self.gamma_doublespinbox.setValue(value)

    def set_exposure_time_auto(self, state):
        state = bool(state)
        self.graphics_manager_hwobj.camera.set_exposure_time_auto(state)
        value = self.graphics_manager_hwobj.camera.get_exposure_time()
        self.exposure_time_slider.setValue(value)
        self.exposure_time_doublespinbox.setValue(value)
class MonoStateButton(QtImport.QToolButton):
    def __init__(self, parent, caption=None, icon=None):

        QtImport.QToolButton.__init__(self, parent)
        self.setSizePolicy(QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Fixed)
        self.setToolButtonStyle(QtImport.Qt.ToolButtonTextUnderIcon)
        if caption:
            self.setText(caption)
            self.setWindowIconText(caption)
        if icon:
            self.setIcon(Icons.load_icon(icon))


class DuoStateButton(QtImport.QToolButton):

    commandExecuteSignal = QtImport.pyqtSignal(bool)

    def __init__(self, parent, caption):
        QtImport.QToolButton.__init__(self, parent)

        self.setToolButtonStyle(QtImport.Qt.ToolButtonTextUnderIcon)
        self.executing = False
        self.run_icon = None
        self.stop_icon = None
        self.standard_color = self.palette().color(QtImport.QPalette.Window)
        self.setText(caption)
        self.setSizePolicy(QtImport.QSizePolicy.Expanding, QtImport.QSizePolicy.Fixed)
        self.clicked.connect(self.button_clicked)

    def set_icons(self, icon_run, icon_stop):
        self.run_icon = Icons.load_icon(icon_run)
        self.stop_icon = Icons.load_icon(icon_stop)
        if self.executing:
            self.setIcon(self.stop_icon)
        else:
            self.setIcon(self.run_icon)

    def button_clicked(self):
        self.commandExecuteSignal.emit(not self.executing)

    def command_started(self):
        Colors.set_widget_color(self, Colors.LIGHT_YELLOW, QtImport.QPalette.Button)
        if self.stop_icon is not None:
            self.setIcon(self.stop_icon)
        self.executing = True
        self.setEnabled(True)

    def is_executing(self):
        return self.executing

    def command_done(self):
        self.executing = False
        Colors.set_widget_color(self, self.standard_color, QtImport.QPalette.Button)
        if self.run_icon is not None:
            self.setIcon(self.run_icon)
        self.setEnabled(True)

    def command_failed(self):
        self.command_done()

class SpinAndSliderAction(QtImport.QWidgetAction):

    value_changed = QtImport.pyqtSignal(float)

    def __init__(self, spin_min_value, spin_max_value, action_string="default label"):

        QtImport.QWidgetAction.__init__(self, None)

        self.main_widget = QtImport.QWidget(None)
        self._main_layout = QtImport.QHBoxLayout()

        self._label = QtImport.QLabel(action_string)
        
        self._slider = QtImport.QSlider(QtImport.Qt.Horizontal)
        self._spinbox = QtImport.QDoubleSpinBox()

        self._spinbox.setRange(spin_min_value, spin_max_value)
        self._spinbox.setSingleStep((spin_max_value - spin_min_value)/100.0)
        
        self._slider.setRange(0, 100)

        self._slider.valueChanged.connect(self.set_value_from_slider)
        self._spinbox.valueChanged.connect(self.set_value_from_spin)

        self._main_layout.addWidget(self._label)
        self._main_layout.addWidget(self._slider)
        self._main_layout.addWidget(self._spinbox)

        self.main_widget.setLayout(self._main_layout)

        self.setDefaultWidget(self.main_widget)

    def set_value_from_slider(self, slider_value):
        print(f"SpinAndSliderAction ^^^^^^^^^^^ set_value_from_slider : {slider_value} ")
        spin_min = self._spinbox.minimum()
        spin_max = self._spinbox.maximum()
        spin_range = spin_max - spin_min

        spinbox_val = 
        print(f"SpinAndSliderAction ^^^^^^^^^^^ set_value_from_slider : spinbox_val {spinbox_val} ")
        
        self._spinbox.setValue(spin_min + (slider_value/100.0) * spin_range)
        self.value_changed.emit(self._spinbox.value())

    def set_value_from_spin(self, spin_value):
        
        print(f"SpinAndSliderAction ^^^^^^^^^^^ set_value_from_spin : {spin_value} ")
        slider_val = ((spin_value - self._spinbox.minimum()) * 100.0) / self._spinbox.maximum()
        print(f"SpinAndSliderAction ^^^^^^^^^^^ set_value_from_spin : slider_val {slider_val} ")
        self._slider.setValue(slider_val)
        self.value_changed.emit(spin_value)

    def set_value(self, spin_value):
        print(f"SpinAndSliderAction ^^^^^^^^^^^ set_value : {spin_value} ")
        self._spinbox.setValue(spin_value)

    def set_limits(self, min_value, max_value):
        
        self._spinbox.valueChanged.disconnect(self.set_value_from_spin)

        if min_value < 0.01:
            min_value = 0.01
            
        self._spinbox.setRange(min_value, max_value)
        spin_step = (max_value - min_value)/100.0
        if spin_step < 0.01:
            spin_step = 0.01
        self._spinbox.setSingleStep(spin_step)

        self._spinbox.valueChanged.connect(self.set_value_from_spin)

class MultiModeAction(QtImport.QWidgetAction):
    """This action provides a default checkable action from a list of checkable
    actions.
    The default action can be selected from a drop down list. The last one used
    became the default one.
    The default action is directly usable without using the drop down list.
    """

    def __init__(self, parent=None, head_icon=None):
        assert isinstance(parent, QtImport.QWidget)
        QtImport.QWidgetAction.__init__(self, parent)
        button = QtImport.QToolButton(parent)
        button.setPopupMode(QtImport.QToolButton.MenuButtonPopup)
        self.setDefaultWidget(button)
        self.__button = button
        self.__head_icon = head_icon

    def getMenu(self):
        """Returns the menu.
        :rtype: qt.QMenu
        """
        button = self.__button
        menu = button.menu()
        if menu is None:
            menu = QtImport.QMenu(button)
            button.setMenu(menu)
        return menu

    def addAction(self, action):
        """Add a new action to the list.
        :param qt.QAction action: New action
        """
        menu = self.getMenu()
        button = self.__button
        menu.addAction(action)
        if button.defaultAction() is None:
            button.setDefaultAction(action)
        if action.isCheckable():
            action.toggled.connect(self._toggled)
        if self.__head_icon is None:
            self.__head_icon = action.icon()

    def _toggled(self, checked):
        if checked:
            action = self.sender()
            button = self.__button
            button.setDefaultAction(action)
        else:
            #if all actions unchecked => display head_icon
            if not any(action.isChecked() for action in self.getMenu().actions()):
                self.__button.setIcon(self.__head_icon)
    
    def init_display(self):
        if self.__head_icon is not None:
            self.__button.setDefaultAction(None)
            self.__button.setIcon(self.__head_icon)
            
