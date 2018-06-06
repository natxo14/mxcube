from core import bl_setup
from QtImport import QObject, pyqtSignal

from sample_changer.GenericSampleChanger import *

class SC(QObject):

    stateChangedSignal = pyqtSignal(int, int)
    statusChangedSignal = pyqtSignal(str)
    infoChangedSignal = pyqtSignal()
    sampleLoadedSignal = pyqtSignal(Pin)
    selectionChangedSignal = pyqtSignal(str)
    taskFinishedSignal = pyqtSignal(str)

    def __init__(self):
        QObject.__init__(self)
        bl_setup.sample_changer_hwobj.connect("stateChanged",
                                      self.sc_state_changed_handler)
        bl_setup.sample_changer_hwobj.connect("statusChanged",
                                      self.sc_status_changed_handler)
        bl_setup.sample_changer_hwobj.connect("infoChanged",
                                      self.sc_info_changed_handler)
        bl_setup.sample_changer_hwobj.connect("loadedSampleChanged",
                                      self.sc_loaded_sample_changed_handler)
        bl_setup.sample_changer_hwobj.connect("selectionChanged",
                                      self.sc_selection_update_handler)
        bl_setup.sample_changer_hwobj.connect("taskFinished",
                                      self.sc_task_finished_update_handler)

    def mount_sample(self, location, device_name=None, wait=False):
        """
        Mounts sample from location
        Some sample delivery devices like yets could not have a difined locations,
        so location argument could be None.

        :param LocationStr location: location
        :returns: True if mount successful otherwise False
        :rtype: bool
        """
        if not device_name:
            device = bl_setup.sample_changer_hwobj
        else:
            device = getattr(bl_setup, device_name + "_hwobj")

        return device.load_sample(holder_length=None, sample_location=location)

    def unmount_current_sample(self, device_name=None, location=None):
        """
        Un-mounts mounted sample to location, un mounts the sample
        to where it was last mounted from if nothing is passed

        :param LocationStr location: location
        :returns: True if un-mount successful otherwise False
        :rtype: bool
        """
        if not device_name:
            device = bl_setup.sample_changer_hwobj
        else:
            device = getattr(bl_setup, device_name + "_hwobj")

        return device.unload()

    def sc_state_changed_handler(self, old_state, new_state):
        """
        Triggered when the sample changer state changes
        """
        self.stateChangedSignal.emit(old_state, new_state)

    def sc_status_changed_handler(self, status):
        """
        Triggered when the sample changer state changes
        """
        self.statusChangedSignal.emit(status)

    def sc_info_changed_handler(self):
        """
        Triggered when the sample changer state changes
        """
        self.infoChangedSignal.emit()

    def sc_loaded_sample_changed_handler(self, sample):
        """
        Triggered when a sample have been loaded
        """
        if sample:
            self.sampleLoadedSignal.emit(sample)

    def sc_selection_update_handler(self, sample):
        """
        Triggered when sample_node or its contents have been updated.
        """
        self.selectionChangedSignal.emit(sample)

    def sc_task_finished_update_handler(self, info):
        """
        Triggered when sample_node or its contents have been updated.
        """
        self.taskFinishedSignal.emit(info)
