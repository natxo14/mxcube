from core import bl_setup

def mount_sample(location, device_name=None, wait=False):
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

def unmount_current_sample(device_name=None, location=None):
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

def sc_state_changed_handler(old_state, new_state):
    """
    Triggered when the sample changer state changes
    """
    pass

def sc_status_changed_handler(status):
    """
    Triggered when the sample changer state changes
    """
    pass

def sc_info_changed_handler():
    """
    Triggered when the sample changer state changes
    """
    pass

def sc_loaded_sample_changed_handler(sample):
    """
    Triggered when a sample have been loaded
    """
    pass

def sc_selection_update_handler(sample):
    """
    Triggered when sample_node or its contents have been updated.
    """
    pass

def sc_task_finished_update_handler(info):
    """
    Triggered when sample_node or its contents have been updated.
    """
    pass

bl_setup.sample_changer_hwobj.connect("stateChanged",
                                      sc_state_changed_handler)
bl_setup.sample_changer_hwobj.connect("statusChanged",
                                      sc_status_changed_handler)
bl_setup.sample_changer_hwobj.connect("infoChanged",
                                      sc_info_changed_handler)
bl_setup.sample_changer_hwobj.connect("loadedSampleChanged",
                                      sc_loaded_sample_changed_handler)
bl_setup.sample_changer_hwobj.connect("selectionChanged",
                                      sc_selection_update_handler)
bl_setup.sample_changer_hwobj.connect("taskFinished",
                                      sc_task_finished_update_handler)
