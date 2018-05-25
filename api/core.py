from HardwareRepository import HardwareRepository

hw_repository_client = HardwareRepository.HardwareRepository()
bl_setup = hw_repository_client.getHardwareObject("beamline-setup")
