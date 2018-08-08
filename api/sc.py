from core import CoreComponent
from core import sample_changer_hwobj
#from sample_changer.GenericSampleChanger import *


class SC(CoreComponent):
    """
    Sample changer core component describes the api between MXCuBE GUI and
    the sample mounting device. Further any device that delivers sample on the
    diffractometer will be called sample changer.
    """
    

    def __init__(self):
        CoreComponent.__init__(self, "sample_changer")
        sample_changer_hwobj.connect("stateChanged",
                                     self.sc_state_changed_handler)

    # Methods -----------------------------------------------------------------

    def mount_sample(self, location, device_name=None, wait=False):
        """
        Mounts sample to the diffractometer. If there is a sample on the
        diffractometer then it is unmounted and requested sample is mounted.
        During the sample mount queue is blocked.
        If the sample mount fails then user is informed with an error message.

        :param LocationStr location: location
        :returns: True if mount successful otherwise False
        :rtype: bool
        """
        if not device_name:
            device = sample_changer_hwobj
        else:
            device = getattr(bl_setup, device_name + "_hwobj")

        return device.load_sample(holder_length=None, sample_location=location)

    def unmount_sample(self, location=None):
        """
        Un-mounts mounted sample to location,
        If no location passed then unmounts the sample to where it was last
        time mounted from.
        During the sample unmount queue is blocked.

        :param LocationStr location: location
        :returns: True if un-mount successful otherwise False
        :rtype: bool
        """
        sample_changer_hwobj.unload_sample(sample_location=location)

    # Event handlers ----------------------------------------------------------

    def sc_state_changed_handler(self, old_state, new_state):
        """
        Method is called when the sample changer state has been changed
        (from ready to busy, busy to error, etc). Sample changer state is
        represented as an integer in the GenericSampleChanger
        """
 
        data = {"old_state": old_state,
                "new_state": new_state}

        self.send_signal("stateChanged",
                         data)
