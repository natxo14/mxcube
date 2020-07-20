papa je t´aime.ainhoa :)
:]
papa je t`aime. signé ainhoa. :)


####################
    DATA UNITS
####################
turret_positions
<position>
      <name>5x</name>
      <zoom>5</zoom>
      <light>700</light>
      <resox>2.59067357513e-06</resox> meter/pixel => self.pixels_per_mm_x = abs(1.0/float(props["resox"]))/1000.0
      <resoy>2.53164556962e-06</resoy> meter/pixel => self.pixels_per_mm_y = abs(1.0/float(props["resoy"]))/1000.0 
      <beamx>394</beamx>
      <beamy>202</beamy>
</position>

On calibration Brick:
experimental values:
CameraCalibrationBrick--diffractometer_manual_calibration_done - : deltaxpix , deltaypix = 60 - 56 - motor delta x, motor delta y = 0.2 - 0.2
resox, resoy = 0.0033333333333333335 - 0.0035714285714285718 : UNIT : mm/pixel => motor delta unit~= mm

For display in table : (nm) = > *1000
For record in xml : (metres) = > /1000

OnCalibratioBrickTable:
                resolution are displayed in nanometer/pixel and saved in metre/pixel




###### TODO #############

---------------------
USER EXPERIENCE: 
How/when to use new data : example , new beam position/calibration:
warn user with colors in table.
When this changes apply?? when created?? when saved ??

If a change is created but not explicity saved, use new data ??
show message to warn user ??
Apply / save button like in 'normal' applications ??
---------------------------------------

@HOME: SAVE CALIBRATION/BEAM POSITION DATA TO XML!!
BeamPosBrick/CalibrationBrick : highlight current pos data

ADD CALIBRATION CLICK MARKS LIKE 

CALIBRATION BRICK : Consistent data: read at loading xml file, then work only with self.calibration_dict 
Save changes when needed to xml file. 

P1 : CENTRING/CALIBRATION
------------------

fix turret_text.xml file:

MultiplePositions how to recover
roles
motors
now in xml we need to have tags 'motor' and 'object with role' with same name

FIX: copy from diffractometer-mockup.xml
list of centring_motors with same names as on the roles list:

<centring_motors>("phi", "kappa", "kappa_phi", "phiz", "phiy", "sampx", "sampy")</centring_motors>
# Centring motors ----------------------------------------------------
        try:
            self.centring_motors_list = eval(self.getProperty("centring_motors"))
        except BaseException:
            self.centring_motors_list = GenericDiffractometer.CENTRING_MOTORS_NAME

--------------------------------------------------------
Deprecation in ABC

-------------------
Deprecation fromstring to frombuffer

-------------------
class DiffractometerState: make child of ENUM
from def tostring(state): to use DiffractometerState.<state>.name

-------------------
MotorSpinBoxBrick: change behaviour
How to set GUIStep ?? By xml ?? in yml file ??

-------------------
Volpi: set layout H or V.
Hide 1 control or the other.
Add tags to dial
-------------------
Turret : add tags to dial. Set position name in the middle of control

TurretBrick: GET RID OF self.turret_hwobj
Pass everything through self.multiple_pos_hwobj : it has everything needed to interact with dial
Everything is depending on the 'name' of the new position in Multiposition hwr_obj


#####
ASK!!
#####
For Antonia:
BlissMotor states:
what we get from Bliss: a list of status.
Allways in the same order ?? How to handle this to translate them to HWObjecStatus ??
Big shit.

For Ivars:
How to write to xml files ?? It's done ??
Once that the xml file has been edited, do applications reload it ??
If I modify multiple-pos.xml and then we execute
multiplePos_hwrobj.getProperty() : it reads again the xml file ??

+++++++++++++    
Ivars: HOW TO USE GraphicsToolsBrick ??
Must convert to QMainWindow to use ToolBar and MainMenu ??
BaseWidget._menubar and
BaseWidget._toolbar never initialized ??

+++++++++++++++++++++++++++++++++++++++++++++
What is better:
try:
    self._beam_position_on_screen = HWR.beamline.diffractometer.get_beam_position()
    except AttributeError:

or
if HWR.beamline.diffractometer is not None:
    blahblah


+++++++++++++++++++++++++++++++++++++++++++++
in bricks
def run(self) ?? still valable?? what for??

On bricks: 
execution order: experimental knowledge
 __init__ ()
 property_changed() for all properties
    properties executed in alphabetical order
 run()


in bricks
def connectNotify(self) ?? What For ??

+++++++++++++++++++++++++++++++++++++++++++++
if in xml file there's a tag like 
<device class="BlissMotor">
  <actuator_name>sy_cdi</actuator_name>
  <GUIstep>0.05</GUIstep>
</device>

then it means that the HWRObject created from that xml file will have 'automatically' a member like:
self.motor_hwobj.GUIstep ??

@ https://github.com/mxcube/mxcube/blob/master/docs/source/how_to_create_hwobj.rst they say
it has to be done like
<propertyNameOne>0</propertyNameOne>
self.internal_value = self.getProperty("propertyNameOne")

But BlissMotor has nothing like that and although
self.motor_hwobj.GUIstep works and it's not None


+++++++++++++++++++++++++++++++++++++++++
On QtGraphicsManager:
Is there any like 'movetopos' functionality ??



********************************************************************
$$$$$$$$$$$$ANSWERED$$$$$$$$$$$$$$$

in cdiGUI when motor sx is moving,
then motors cx and cy change their status ( to something like not available : yellow background color/stop button available)
other interactions happen also:
sy moving -> cx cy disabled
cx moving -> cy and sy disabled
cy moving -> cx disabled

THOSE ARE CALCULATION MOTORS : their position depends on the position of other motors =>
when the 'origin' motors move, they 'move' also
+++++++++++++
On xml files : differences between: device/equipment/object


==> calc_mot1.xml <==
<?xml version="1.0" encoding="utf-8"?>
<device class="BlissMotor">

==> mini-diff-mockup.xml <==
<equipment class="GenericDiffractometer">
  <object href="/diff-omega-mockup" role="phi"/>

  ==> queue.xml <==
<object class="QueueManager">
</object>

METTRE OBJECT PARTOUT!!

##############################################
    Adding Bricks to GUI Builder
##############################################
If we`d like a brick called 'Motor mother fucker' on the list of available bricks, then we have to create a py file with:
a class inside:
class MotorMotherFuckerBrick(BaseWidget):
(the name of the .py file containing the class is irrelevant - or it seems - But better call it the same)

The GUI builder detects Capital letters and splits the name into the displayed text.
see function get_brick_text_label in GUIBuilder.py

##############################################
    GETTING DATA FROM XML FILE
##############################################

Ex: mxcube.git/HardwareRepository/configuration/embl_hh_p13/energyscan.xml

<object class="EMBLEnergyScan">

<elements>
    <element>
      <symbol>K</symbol>
      <energy>K</energy>
    </element>
    <element>
      <symbol>Ca</symbol>
      <energy>K</energy>
    </element>
    <element>
      <symbol>Sc</symbol>
      <energy>K</energy>
    </element>
</elements>

Code to access those values:

class EMBLEnergyScan(AbstractEnergyScan, HardwareObject):
   def getElements(self):
        elements = []
        try:
            for el in self["elements"]:
                elements.append(
                    {
                        "symbol": el.getProperty("symbol"),
                        "energy": el.getProperty("energy"),
                    }
                )
        except IndexError:
            pass
        return elements 



#######
CODEBYTES
#######

Debug + PyQt
# from PyQt5.QtCore import pyqtRemoveInputHook
-        # pyqtRemoveInputHook()
-        # import pdb
-        # pdb.set_trace()
-        # print(f"""get object by role
-        #           object : {obj}
-        #           obj._objectsByRole : {obj._objectsByRole}
-        #           role : {role}""")


##########################
MXCuBE <=> BLISS SIGNAL/SLOTS
##########################

Ex: BlissVolpi(HardwareObject):

cfg = static.get_config()
self.volpi = cfg.get(self.volpi_name)
self.connect(self.volpi, "intensity", self.intensity_changed)

This works because:
class HardwareObjectMixin(CommandContainer):
    def connect(self, sender, signal, slot=None):
        ...
        dispatcher.connect(slot, signal, sender)
        ...

And dispatcher is part of 'Louie', that is also part of Bliss
MXCuBE and BLISS Share the same signal/slot system

#############
MXCuBE IDE SIGNAL/SLOTS
#############
 in class Connectable
 def define_signal
 def define_slot

 in BaseWidget:
 create signal.
 then self.define_signal
 ex:
 ChatBrick
    incoming_unread_messages = QtImport.pyqtSignal(int, bool)
    reset_unread_messages = QtImport.pyqtSignal(boo)lig
        self.define_signal("incoming_unread_messages", ())
        self.define_signal("reset_unread_message", ())
        self.define_slot("tabSelected", ())
Then, this signal/slots are displayed in GUI signal/slot edition

#############
 YML FILES AS GUI FILES
 #############
 exec mxcube -d guiFile.yml
 save as yml file
 edit yml file and comment following lines:

  signals:
#    enableExpertMode: !!python/tuple []
#    isHidden: !!python/tuple []
#    isShown: !!python/tuple []
#    quit: !!python/tuple []

#############
 LIST OF GUIS
 #############

 
####################################################
 WHEN SETTING HARDWARE_REPOSITORY_SERVER
####################################################

set HARDWARE_REPOSITORY_SERVER to
/path/to/mxcube/HardwareRepository/configuration/esrf_idXX/ folder

copy all files from xml-qt folder to that folder JUST IN CASE!!
Lost lot of time with a 'segmentation fault' because the mxcollect.xml file included in beamline_config_yml config file:

the file mxcollect (at the given HRepo version was like ):

<object class="CollectMockup">
  <object href="/mini-diff-mockup" role="diffractometer"/>
  <object href="/Qt4_graphics-manager" role="graphics_manager"/>
  <object href="/graphics" role="graphics_manager"/>
  <object href="/beam-info" role="beam_info"/>
  <object href="/lims-client-mockup" role="lims_client"/>

the problem came from /graphics : commented the line and the issue went away.
Maybe /graphics HObject was 'created' too many times ??

A newer version of mxcollect limits to:
<object class="CollectMockup">
</object>

#################
 BEAMLINE_CONFIGURATION .YML
#################
How does it work:
yml file 

Used to feed the HardwareObject.beam object
from HardwareRepository import HardwareRepository as HWR
HWR.beamline.

HardwareRepository.py
beamline = None
BEAMLINE_CONFIG_FILE = "beamline_config.yml"

def load_from_yaml

++++++++++++++++++++++++++
/!\ ATTENTION /!\ OBJECTS CREATED IN APPARAITION ORDER !!!
if HWR.beamline.XX needed in YY file, then XX BEFORE YY in yml file!!
++++++++++++++++++++++++++

If two HardwareObject are created on different ways, they`re the same:
    ` all HOs are singelton objects `
ex:
On one side, GUI elements:
CameraBrick
new_value : graphics.xml
<object class="QtGraphicsManager">
             self.graphics_manager_hwobj = self.get_hardware_object(new_value)
          
In QtGraphicsManager 


In other side beamline_config.yml elements:
- beam: beam-info.xml <object class="ESRF.ESRFBeam">
- sample_view : sample-view.xml <object class="QtGraphicsManager">

TWO QtGraphicsManager objects are created, but the diffractometer created inside is SINGELTON:
QtGraphicsMananger: self.diffractometer_hwobj = self.getObjectByRole("diffractometer")
ESRFBeam : HWR.beamline.diffractometer 

/!\ DON'T USE " microscope" !! USE sample_view INSTEAD !!!

****  WHAT IS NEEDED ****
what beamline objects (described in beamline_configuration.yml file) are needed mxcube to work:
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
ANYTHING THAT NEEDS CODE LIKE HWR.beamline.
need to be on the YML FILE!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
In QtGraphicsManager:
def init:
if HWR.beamline.beam is not None:
            self.beam_info_dict = HWR.beamline.beam.get_beam_info_dict()
            self.beam_position = HWR.beamline.beam.get_beam_position_on_screen()
            self.connect(
                HWR.beamline.beam, "beamPosChanged", self.beam_position_changed
            )
            self.connect(HWR.beamline.beam, "beamInfoChanged", self.beam_info_changed)

            self.beam_info_changed(self.beam_info_dict)
            self.beam_position_changed(HWR.beamline.beam.get_beam_position_on_screen())

def stop_move_beam_mark(self): |
def stop_beam_define(self):
    HWR.beamline.beam.set_beam_position(
def refresh_camera(self): self.beam_info_dict = HWR.beamline.beam.get_info_dict()
def move_beam_mark_auto(self): HWR.beamline.beam.set_beam_position

- beam: beam-info.xml
       object class=ESRF.ESRFBeam
Look where is defined:
        AbstractBeam: where this values are set
        self._beam_info_dict = {"size_x": self._beam_width,
                                "size_y": self._beam_height,
                                "shape": self._beam_shape,
                                "label": self._beam_label}

###################
 HARDWARE OBJECTS SYSTEM
###################

FOR CAMERA : no related to yml file : all happens in xml file through QtGraphicsManager
in GUI:
class CameraBrick:
Camera Brick. mnemonic graphicsWMockupCamera.xml
       	      <object class="QtGraphicsManager">
	      	      <object href="/mini-diff-mockup" role="diffractometer"/>
   		      <object href="/beam-info" role="beam_info"/>
		      <object href="/camera-mockup" role="camera"/>

def property_changed
          property_name == "mnemonic":
          self.graphics_manager_hwobj = self.get_hardware_object(new_value)

QtGraphicsManager:
	self.camera_hwobj = self.getObjectByRole(self.getProperty("camera_name", "camera"))
	self.diffractometer_hwobj = self.getObjectByRole("diffractometer")

Diffractometer:
Two different specified in beamline_config.yml and  nmemonic in CameraBrick :
in camerabrick  :<object href="/diffractometer-mockup" role="diffractometer"/>  in diffractometer-mockup.xml : DiffractometerMockup
in beamline_config.yml : - diffractometer: mini-diff-mockup.xml  => in mini-diff-mockup.xml :  GenericDiffractomenter

The diffrac in camerabrick mnemonic is used BECAUSE we-re using
self.graphics_manager_hwobj = self.get_hardware_object(new_value) : new_value comes from mnemonic

BUT when using objects coming from
HWR.beamline => then use beamline_config.yml to create objects

ISSUES WITH MOCKUPS?? TO CHECK!!


#################
 BRANCHES CONTENT
#################

###################
HARDWARE OBJECTS HIERARCHY
###################
class CommandContainer: object
    """Mixin class for generic command and channel containers"""

class HardwareObjectMixin(CommandContainer):
   """HardwareObject functionality, for either xml- or yaml-configured subclasses"""
class HardwareObjectNode(object):
      
class HardwareObject(HardwareObjectNode, HardwareObjectMixin):    

class Equipment(HardwareObject, DeviceContainer):

class DeviceContainer:
---------------------------------
class Device(HardwareObject)
        NB Deprecated - should be replaced by AbstractActuator
class AbstractActuator(HardwareObject):

---------------------
GUI
class BaseWidget(Connectable , QFrame)

class Connectable(object)
    GUI CREATOR SIGNAL/SLOT logic
-------------------------

#################
 CALIBRATION		
#################

       HOW IT WORKS:
        input: DeltaY, DeltaZ : dont care about units: transparent for calculations
        input values are the movement of motors : how much are moving.

        Start Process
        Click in one point in the image
        Move motors: input little values : the point in the image that has been clicked has to stay in the camera field.
        Click in the SAME point in the image/sample: identify it and click on it
        Then make calculations with:
        DeltaPixelsY, DeltaPixelsZ | deltaMvmtnMotorY, deltaMvmtnMotorZ 

In CameraCalibrationBrick: displayed data is
        nanometers per pixel : how many nanometers measure each screen pixel ( Qt Coordinates ) 
from Qt Doc:
        """
Graphics View is based on the Cartesian coordinate system; items' position and geometry on the scene are represented by sets of two numbers: the x-coordinate, and the y-coordinate. When observing a scene using an untransformed view, one unit on the scene is represented by one pixel on the screen.
"""

PIXELS_PER_MM :

Origin -> Diffractometer
class DiffractometerMockup(GenericDiffractometer):
      def init
      	  self.x_calib = 0.000444
	  self.y_calib = 0.000446
	  
	  self.pixels_per_mm_x = 1.0 / self.x_calib
          self.pixels_per_mm_y = 1.0 / self.y_calib
          self.beam_position = [318, 238]



BEAM_POSITION
Origin GraphicsItem :
self.beam_position
def set_beam_position(self, beam_position):

class GraphicsItemBeam
def set_detected_beam_position(self, pos_x, pos_y):
        """Updates beam mark position

        :param pos_x: position x
        :type pos_x: int
        :param pos_y: position y
        :type pos_y: int
        :return: None
        """
        self.detected_beam_info_dict = (pos_x, pos_y)

class QtGraphicsManager | Same for GenericDiffractometer
init()
if HWR.beamline.beam is not None:
            self.beam_info_dict = HWR.beamline.beam.get_beam_info()
            self.beam_position = HWR.beamline.beam.get_beam_position()
            self.connect(
                HWR.beamline.beam, "beamPosChanged", self.beam_position_changed
            )

    def beam_position_changed(self, position):
        graphics_item.set_beam_position(position)

    SIGNAL beamPosChanged : emited by '*InfoBeam*' classes

EX: In class EMBLBeamInfo
    def beam_pos_hor_changed(self, value):
        """Updates horizontal beam position

        :param value: horizontal beam position
        :type value: float
        :return: None
        """
        self.beam_position[0] = value
        self.emit("beamPosChanged", (self.beam_position,))

    and  beam_pos_hor_changed connected to
        self.chan_beam_position_hor = self.get_channel_object("BeamPositionHorizontal")
        if self.chan_beam_position_hor:
            self.chan_beam_position_hor.connectSignal("update", self.beam_pos_hor_changed)
        
    and BeamPositionHorizontal channel present in xml files
    embl_hh_pe2/beam-info.xml:    <channel type="tine" name="BeamPositionHorizontal" tinename="/PE2/BSD/BSD_0" timeout="100">BeamPositionHorizontal</channel>
    embl_hh_p14/beam-info.xml:    <channel type="tine" name="BeamPositionHorizontal" tinename="/P14/MD3/MD3_0" timeout="100">BeamPositionHorizontal</channel>
    embl_hh_p13/beam-info.xml:    <channel type="tine" name="BeamPositionHorizontal" tinename="/P13/MD/MD_0" timeout="100">BeamPositionHorizontal</channel>


    These following two functions present in several classes
    class BeamInfo(Equipment): class ALBABeamInfo(Equipment): class BeamInfoMockup(AbstractBeam): 
    def get_beam_position(self):
    def get_beam_position(self):

    



#################
 CODE HOWS	
#################

--------- CAMERA/GRAPHICS ---------------//
class CameraBrick(BaseWidget):

    self.graphics_view = self.graphics_manager_hwobj.get_graphics_view()
    
self.graphics_manager_hwobj = self.get_hardware_object(new_value): new_value = mnemonic => graphics.xml => QtGraphicsManager

graphics.xml
   <object href="/diffractometer-mockup" role="diffractometer"/>
   <object href="/beam-info" role="beam_info"/>
   <object href="/camera-mockup" role="camera"/>


class QtGraphicsManager(AbstractSampleView):
    self.graphics_view = GraphicsLib.GraphicsView() : QWidget

    self.camera_hwobj = self.getObjectByRole( self.getProperty("camera_name", "camera") )
    




--------- NEW CALIBRATION ---------------//

HOW IT WORKS:
        input: DeltaY, DeltaZ : dont care about units: transparent for calculations
        input values are the movement of motors : how much are moving.

        Start Process
        Click in one point in the image
        Move motors: input little values : the point in the image that has been clicked has to stay in the camera field.
        Click in the SAME point in the image/sample: identify it and click on it
        Then make calculations with:
        DeltaPixelsY, DeltaPixelsZ | deltaMvmtnMotorY, deltaMvmtnMotorZ
    


GraphicsItem
        self.beam_size_mm
        self.pixels_per_mm
        self.beam_size_pix
       

        def set_pixels_per_mm(self, pixels_per_mm):
        """Sets pixels per mm and updates item
        """
        if not (math.isnan(pixels_per_mm[0]) or math.isnan(pixels_per_mm[1])):
            self.pixels_per_mm = pixels_per_mm
            self.beam_size_pix[0] = int(self.beam_size_mm[0] * self.pixels_per_mm[0])
            self.beam_size_pix[1] = int(self.beam_size_mm[1] * self.pixels_per_mm[1])
            self.update_item()

QtGraphicsManager
	def diffractometer_pixels_per_mm_changed
	    item.set_pixels_per_mm(self.pixels_per_mm)


if self.diffractometer_hwobj is not None:
            pixels_per_mm = self.diffractometer_hwobj.get_pixels_per_mm()
            self.diffractometer_pixels_per_mm_changed(pixels_per_mm)
            GraphicsLib.GraphicsItemGrid.set_grid_direction(
                self.diffractometer_hwobj.get_grid_direction()
            )

self.connect(
                self.diffractometer_hwobj,
                "pixelsPerMmChanged",
                self.diffractometer_pixels_per_mm_changed,
            )
in Diffractometer
        def init()
            elif motor_name == "zoom":
                        self.connect(
                            temp_motor_hwobj,
                            "predefinedPositionChanged",
                            self.zoom_motor_predefined_position_changed,
                        )
                        self.connect(
                            temp_motor_hwobj, "stateChanged", self.zoom_motor_state_changed
                        )

        def update_zoom_calibration(self):
            self.pixels_per_mm_x = 1.0 / self.channel_dict["CoaxCamScaleX"].getValue()
            self.pixels_per_mm_y = 1.0 / self.channel_dict["CoaxCamScaleY"].getValue()
            self.emit("pixelsPerMmChanged", ((self.pixels_per_mm_x, self.pixels_per_mm_y)))

        def motor_positions_to_screen(self, centred_positions_dict):
            if self.use_sample_centring:
                self.update_zoom_calibration()

        def zoom_motor_predefined_position_changed(self, position_name, offset):
                """
                """
                self.update_zoom_calibration()
                self.emit("zoomMotorPredefinedPositionChanged", (position_name, offset))


in QtGraphicsManager
    def diffractometer_state_changed(self, *args):
        new_x, new_y = self.diffractometer_hwobj.motor_positions_to_screen(...)
    def create_centring_point(self, centring_state, centring_status, emit=True):
        screen_pos = self.diffractometer_hwobj.motor_positions_to_screen(...)
            
        
 ---------- BEAM SIZE -------------
QtGraphicsManager
    def beam_info_changed(self, beam_info):
        graphics_item.set_beam_info(beam_info)


    def init
             self.connect(HWR.beamline.beam, "beamInfoChanged", self.beam_info_changed)
             
QGraphicsItem
def set_beam_info(self, beam_info):
        """Updates beam information

        :param beam_info: dictionary with beam parameters
                          (size_x, size_y, shape)
        :type beam_info: dict
        """
        self.beam_is_rectangle = beam_info.get("shape") == "rectangular"
        self.beam_size_mm[0] = beam_info.get("size_x", 0)
        self.beam_size_mm[1] = beam_info.get("size_y", 0)
        if not math.isnan(self.pixels_per_mm[0]):
            self.beam_size_pix[0] = int(self.beam_size_mm[0] * self.pixels_per_mm[0])
        if not math.isnan(self.pixels_per_mm[1]):
            self.beam_size_pix[1] = int(self.beam_size_mm[1] * self.pixels_per_mm[1])

####################################
###### MOVETOBEAM  ###############
####################################


####################################
#### CENTRING ########
####################################
        HOW IT WORKS:
        input: delta rotation

        Start Process
        for i in range (npoints):
            Click in one point in the image : record point y,z coordinates
            rotateMove motor with DeltaRot
            Click in the SAME point in the image/sample: identify it and click on it
            
        Then make calculations with:
        list of points
        move motors
        

CameraBrick
temp_action = create_menu.addAction(
            Icons.load_icon("ThumbUp"),
            "Centring point on current position",
            self.create_point_current_clicked,
        )

create_menu.addAction(
            Icons.load_icon("ThumbUp"),
            "Centring points with one click",
            self.create_points_one_click_clicked,
        )
def create_point_current_clicked(self):
        self.graphics_manager_hwobj.start_centring(tree_click=False)

def create_points_one_click_clicked(self):
        self.graphics_manager_hwobj.start_one_click_centring(

QtGraphicManager


def start_centring(self, tree_click=None):
    self.emit("centringInProgress", True)
    if tree_click:
    else:
            # START MOVING TO BEAM POSITION
            # self.accept_centring()
            self.diffractometer_hwobj.start_move_to_beam(
                self.beam_position[0], self.beam_position[1]
            )
def mouse_clicked(self, pos_x, pos_y, left_click=True):
    elif self.in_one_click_centering:
            self.diffractometer_hwobj.start_move_to_beam(pos_x, pos_y)
            
def start_one_click_centring(self):
        # IF USER CLICKS : CENTER IN THAT POSITION
        self.set_cursor_busy(True)
        self.emit("infoMsg", "Click on the screen to create centring points")
        self.in_one_click_centering = True : ( in mouse clicked if self.in_one_click_centering: self.diffractometer_hwobj.start_move_to_beam(pos_x, pos_y) )
        self.graphics_centring_lines_item.setVisible(True)
CameraBrick
)
        
Diffractometer ( mockup or generic )
       def start_move_to_beam(
        self, coord_x=None, coord_y=None, omega=None, wait_result=None
    )
            motors = self.get_centred_point_from_coord(
                coord_x, coord_y, return_by_names=True
            )
            self.accept_centring()
        def accept_centring()
            self.emit("centringAccepted", (True, centring_status))


QtGraphicsManager
self.connect(
                self.diffractometer_hwobj,
                "centringAccepted",
                self.create_centring_point,
            )
def create_centring_point(self, centring_state, centring_status, emit=True):
    point = GraphicsLib.GraphicsItemPoint(
                cpos, True, screen_pos[0], screen_pos[1]
            )
    return point


###### OLD FRAMEWORK #########
@id13 : lid131 machine ~/local_old
look for code @
~/python/bliss_modules
~/applications/BlissFramework
~/local/framework


###### OLD FRAMEWORK MOVETOBEAM  ###############
@class CameraMotorToolsBrick(BlissWidget):
        self.movetoAction = QubSelectPointAction(name='Move to Beam', place=self.movetoMode,actionInfo = 'Move to Beam',group='Tools')
        
        self.connect(self.movetoAction, qt.PYSIGNAL("PointSelected"),self.pointSelected)

    def pointSelected(self, drawingMgr):
        if self.horMotHwo is not None and self.verMotHwo is not None:
            if  self.YSize is not None and \
                self.ZSize is not None and \
                self.YBeam is not None and \
                self.ZBeam is not None :
                
                self.drawingMgr =  drawingMgr 
                   
                (y, z) = drawingMgr.point()
                
                self.drawingMgr.stopDrawing()
                
                movetoy = - (self.YBeam - y) * self.YSize
                movetoz = - (self.ZBeam - z) * self.ZSize
                
                self.motorArrived = 0
            
                self.connect(self.horMotHwo, qt.PYSIGNAL("moveDone"),
                             self.moveFinished)
                self.connect(self.verMotHwo, qt.PYSIGNAL("moveDone"),
                             self.moveFinished)

                self.horMotHwo.moveRelative(movetoy)
                self.verMotHwo.moveRelative(movetoz)
        
        
@ ~/python/bliss_modules/Qub/qt3/Widget/QubActionSet.py
class QubSelectPointAction(QubToggleImageAction) :
        def __init__(self,iconName='movetopos',actionInfo=None,mosaicMode = False,residualMode = False,**keys) :
        

        
###### OLD FRAMEWORK CENTERING ###############

ID13
centering_base_stage.xml
<equipment>
    <motors>
           <device role="horizontal"     hwrid="/scanning/mceny"/>
           <device role="inBeam"      hwrid="/scanning/mcenx"/>
           <device role="rotation"      hwrid="/scanning/srotz"/>
    </motors>
</equipment>

class CenteringBrick(BlissWidget) :
   def propertyChanged(self,property,oldValue,newValue):
        if property == 'mnemonic':
            xoryMotor = equipment.getDeviceByRole('horizontal')
            if xoryMotor is not None:
                        self.__verticalPhi = True
                    else:
                        xoryMotor = equipment.getDeviceByRole('vertical')
            zMotor = equipment.getDeviceByRole('inBeam')
            rMotor = equipment.getDeviceByRole('rotation')
            table_y = equipment.getDeviceByRole('table_y')
            table_z = equipment.getDeviceByRole('table_z')
            self.__centeringPlug = _centeringPlug(self,self.__widgetTree,xoryMotor,zMotor,rMotor,table_y,table_z,self.getProperty('table_y_inverted'), self.getProperty('table_z_inverted'))
                    
class _centeringPlug :
    def __init__(self,brick,widgetTree,xoryMotor,zMotor,rMotor,tableyMotor, tablezMotor, table_y_inverted, table_z_inverted) :
  
SO:
xroyMotor = motor in xml file with horizontan/vertical role : /scanning/mceny
zMotor = motor in xml file with inBeam role : /scanning/mcenx
rMotor = motor in xml file with rotation role : /scanning/srotz

IN microPX -d : MultiAxisAligment: sample_stage.xml
axis 1 : micos_axis.xml
axis 2 : micosmt55_axis

micos_axis.xml:
<device role="vertical" hwrid="/scanning/strz"></device>
<device role="horizontal" hwrid="/scanning/stry"></device>
<device role="rotation" hwrid="/scanning/strx"></device>

/equipment/micosmt55_axis.xml:
 <motors>
      <device role="vertical" hwrid="/scanning/mcenx"></device>
      <device role="horizontal" hwrid="/scanning/mceny"></device>
      <device role="rotation" hwrid="/scanning/srotz"></device>
    </motors>

SO: Motors taking part in centring are mcenx/mceny/srotz

ID10:
blissadm@ting:~/local/HardwareRepository/equipment
centering.xml
           <device role="horizontal"     hwrid="/cdi/sy"/>
           <device role="inBeam"      hwrid="/cdi/sx"/>
           <device role="rotation"      hwrid="/cdi/ths"/>
           <device role="table_y"     hwrid="/cdi/thy"/>
           <device role="table_z"     hwrid="/cdi/sz"/>
Those are motors taking part in centring

###### ###############
###### BRICKS  ###############
###### ###############
beamalignbrick : incomplete
BeamSizeBrick : only to display beam size
BeamFocusingBrick : to change beam focus mode : list of modes in xml file. Ex in : embl_hh_p14/eh1/beamFocusing.xml
BeamAlignBrick: incomplete
    def align_beam_clicked(self):
        self.beam_align_hwobj.align_beam_test()


BeamPositionBrick: 
2 motors ( change according to focus mode) . 2 buttons: 
        self.center_beam_button.clicked.connect(self.center_beam_clicked)
        self.measure_flux_button.clicked.connect(self.measure_flux_clicked)


HutchMenuBrick:
        QtGraphicsMenuBrick -> right click on image menu : to be modified!!

ToolsBrick:
       Adds a tool menu to the toolbar. Actions are configured via xml.
       Action call method from hwobj.

TreeBrick: ??

GraphicsToolsBrick: targetMenu : combobox {menubar, toolbar, both} . not yet working
GraphicsManagerBrick: Checkbox to show whole inteface: controls for points/measures/lines/grids

###### ###############
###### FRAMEWORK2 BRICKS  ###############
###### ###############
ID13RecordedSeriesBrick: no GUI
reference to xml file with commands on it 
Adds a button to view, and links action to a command on xml file

    self.__addPoint = equipment.getCommandObject('lll')

    self.__button = QubButtonAction(label='%s-----' % self.__prefix,name='ID13RecordedSeriesBrick_%s' % self.__prefix,
                                            place='toolbar',
                                            group='ID13',autoConnect = True)
            qt.QObject.connect(self.__button,qt.PYSIGNAL('ButtonPressed'),self.__lllCBK)
            view.addAction([self.__button])

def __lllCBK(self) :
        try:
            self.__addPoint()

CameraMotorToolsBrick: no GUI hmotor/vmotor

This brick allows to add a "Move to " mode as action (toolbar or popup menu)
of a camera brick. A soon as the calibration has been done and beam position
has been set, user can click on the display of the associated camera brick and
the point selected will move in the beam.

CameraToolsBrick : no GUI 

Thiss brick allows to define action to be done on a CameraBrick object.
It does not deal with Camera associated motors as CameraMotorToolsBrick
should do it.
Available tools are the following:

add a list in the tool bar or in the menu to selected camera from a Meteor2
server

#######################
MULTIPLE POSITIONS
#######################
in bliss :

    dans bliss maintenant il y a MultiplePositions class, qui defini des positions et des etiquettes. Le HWO est le BlissNState, mais c`est mieux si on regarde ca ensemble.



#######################
BLISS MOTORS
#######################
sync_hard():
    takes the position from the motor controller and assigns it as the dial position of the BLISS axis
.offset=0
    just puts no difference between dial pos and user pos

dial pos and user pos are legacy from spec

formula: user pos = sign * dial pos + offset
 dial_pos is the position from the controller ; in case the dial and the controller have different positions
 (like, if the motor moves from somewhere else than BLISS), 

#######################
BRICKS FUNCTIONALITY
#######################





#######################
    GEVENT
#######################

To get the return value of the function
Greenlet.get() is used.
To be sure that the function has ended, we call it on the function used with 'link()'

In GenericDiffractomenter
def start_manual_centring(self, sample_info=None, wait_result=None):
        """
        """
        self.emit_progress_message("Manual 3 click centring...")
        self.current_centring_procedure = sample_centring.start(list_of_vars)
        self.current_centring_procedure.link(self.centring_done)

def centring_done(self, centring_procedure):
        """
        check return value: if it's an exception or not and so
        """
        try:
            motor_pos = centring_procedure.get()
            if isinstance(motor_pos, gevent.GreenletExit):
                raise motor_pos
        except BaseException:
            logging.exception("Could not complete centring")
            self.emit_centring_failed()
        else:
            self.emit_progress_message("Moving sample to centred position...")
            self.emit_centring_moving()

in sample_centring:
def start(vars):
    '''
    RETURNS A Greenlet!!!!
     Create a new Greenlet object and schedule it to run function(*args, **kwargs).
     This can be used as gevent.spawn or Greenlet.spawn
    '''
    global CURRENT_CENTRING

    phi, phiy, phiz, sampx, sampy = prepare(centring_motors_dict)

    CURRENT_CENTRING = gevent.spawn(center,list_of_vars)
    return CURRENT_CENTRING

To get 


#######################
    CONDA ENV
#######################

Clone a bliss_dev conda env

        then install opencv with pip
$ pip install opencv-python


 ###################################################
        BLISS DATA POLICY <=> BILSS AS LIBRARY
 ###################################################
from https://bliss.gitlab-pages.esrf.fr/bliss/master/data_policy.html
from https://bliss.gitlab-pages.esrf.fr/bliss/master/bliss_as_library.html
from https://bliss.gitlab-pages.esrf.fr/bliss/master/dev_data_policy_basic.html#scan_saving

>>> import bliss
>>> from bliss.config import static

>>> config = static.get_config()
>>> session = config.get('test_session')
>>> session.setup()

>>> session.scan_saving
<bliss.config.settings.BasicScanSaving object at 0x7f4223bc6d40>

>>> session.scan_saving.__info__()
"Parameters (default) - \n\n  .base_path            = '/tmp/scans'\n  .data_filename        = 'data'\n  .user_name            = 'vergaral'\n  .template             = '{session}/'\n  .images_path_relative = True\n  .images_path_template = 'scan{scan_number}'\n  .images_prefix        = '{img_acq_device}_'\n  .date_format          = '%Y%m%d'\n  .scan_number_format   = '%04d'\n  .session              = 'test_session'\n  .date                 = '20200715'\n  .scan_name            = '{scan_name}'\n  .scan_number          = '{scan_number}'\n  .img_acq_device       = '<images_* only> acquisition device name'\n  .writer               = 'hdf5'\n  .data_policy          = 'None'\n  .creation_date        = '2019-12-05-07:49'\n  .last_accessed        = '2020-07-15-14:14'\n--------------  ---------  -------------------------------\ndoes not exist  filename   /tmp/scans/test_session/data.h5\ndoes not exist  directory  /tmp/scans/test_session\n--------------  ---------  -------------------------------"
>>> print(session.scan_saving.__info__())
Parameters (default) -

  .base_path            = '/tmp/scans'
  .data_filename        = 'data'
  .user_name            = 'vergaral'
  .template             = '{session}/'
  .images_path_relative = True
  .images_path_template = 'scan{scan_number}'
  .images_prefix        = '{img_acq_device}_'
  .date_format          = '%Y%m%d'
  .scan_number_format   = '%04d'
  .session              = 'test_session'
  .date                 = '20200715'
  .scan_name            = '{scan_name}'
  .scan_number          = '{scan_number}'
  .img_acq_device       = '<images_* only> acquisition device name'
  .writer               = 'hdf5'
  .data_policy          = 'None'
  .creation_date        = '2019-12-05-07:49'
  .last_accessed        = '2020-07-15-14:14'
--------------  ---------  -------------------------------
does not exist  filename   /tmp/scans/test_session/data.h5
does not exist  directory  /tmp/scans/test_session
--------------  ---------  -------------------------------



        
###### TEMP ###############

---------------------- gui/bricks/CameraBrick.py --------------------------
index e7a03fac..77c9585b 100644
@@ -388,7 +388,7 @@ class CameraBrick(BaseWidget):
         HWR.beamline.microscope.de_select_all()
 
     def clear_all_items_clicked(self):
-        HWR.beamline.microscope.clear_all()
+        HWR.beamline.microscope.clear_all_shapes()
 
     def zoom_window_clicked(self):
         self.zoom_dialog.set_camera_frame(

----------------------- gui/bricks/MotorSpinBoxBrick.py -----------------------
index 4d73f42d..193c996b 100644
@@ -574,6 +574,8 @@ class MotorSpinBoxBrick(BaseWidget):
                 instance_filter=True,
             )
 
+        # get motor position and set to brick
+        self.position_changed(self.motor_hwobj.get_value())
         self.position_history = []
         self.update_gui()
         # self['label'] = self['label']

gui/bricks/ESRF/MotorBrick.py ------------------------
index daf52545..75708f67 100644
@@ -682,7 +682,7 @@ class MotorBrick(BaseWidget):
 
     def step_forward_value_changed(self, value):
         """Act when forward step button value changed."""
-        logging.getLogger().error(
+        logging.getLogger().warning(
             f"MotorBrick step_forward_value_changed : {value}"
         )
         self.step_backward.set_value(value)

    Author: natxo vergara <vergaral@esrf.fr>  2020-02-26 18:01:30
Committer: natxo vergara <vergaral@esrf.fr>  2020-02-26 18:01:30
----------------------- gui/bricks/MotorSpinBoxBrick.py -----------------------
index a519442a..4d73f42d 100644
@@ -107,10 +107,16 @@ class MotorSpinBoxBrick(BaseWidget):
         self.move_left_button.setIcon(Icons.load_icon("Left2"))
]         self.move_left_button.setToolTip("Moves the motor down (while pressed)")
         self.move_left_button.setFixedSize(27, 27)
+        self.move_left_button.setAutoRepeat(True)
+        self.move_left_button.setAutoRepeatDelay(500)
+        self.move_left_button.setAutoRepeatInterval(500)
         self.move_right_button = QtImport.QPushButton(self.main_gbox)
         self.move_right_button.setIcon(Icons.load_icon("Right2"))
         self.move_right_button.setToolTip("Moves the motor up (while pressed)")
         self.move_right_button.setFixedSize(27, 27)
+        self.move_right_button.setAutoRepeat(True)
+        self.move_right_button.setAutoRepeatDelay(500)
+        self.move_right_button.setAutoRepeatInterval(500)
 
         self.position_spinbox = QtImport.QDoubleSpinBox(self.main_gbox)
         self.position_spinbox.setMinimum(-10000)
@@ -277,6 +283,7 @@ class MotorSpinBoxBrick(BaseWidget):
         # self.demand_move = -1
         self.update_gui()
         state = self.motor_hwobj.get_state()
+        print(f"MSBBrick @move_down> state : {state} vs {self.motor_hwobj.motor_states.READY}")
         if state == self.motor_hwobj.motor_states.READY:
             if self["invertButtons"]:
                 self.really_move_up()
@@ -429,8 +436,10 @@ class MotorSpinBoxBrick(BaseWidget):
             # self.update_history(self.motor_hwobj.getPosition())
             self.position_spinbox.setEnabled(False)
             self.stop_button.setEnabled(True)
-            self.move_left_button.setEnabled(False)
-            self.move_right_button.setEnabled(False)
+            buttons = QtImport.QApplication.mouseButtons()
+            if QtImport.QApplication.mouseButtons() != QtImport.Qt.LeftButton:
+                self.move_left_button.setEnabled(False)
+                self.move_right_button.setEnabled(False)
             self.step_combo.setEnabled(False)
         elif state in (
             self.motor_hwobj.motor_states.LOWLIMIT,

