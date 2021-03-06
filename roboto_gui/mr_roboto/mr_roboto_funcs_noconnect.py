import time

# This module imports

# XDart imports

SLEEP_TIME = 2
NOCONNECT_IMPORTED = True

SampleReadyPose = [145.333, -0.282, 195, 180, 0, -180]
SampleHeight = 69
MountReadyPose = [-47.761, -45.143, 351.589, -8.028, -89.263, -70.034]
MountDistance = 58.0
BarcodeScanPose = [45.526, -155.890, 195.000, -180.000, 0.000, -113.000]
spacing = 25.125
speed = 25


def wait_until_SPECfinished(t):
    print("Waiting for spec")
    time.sleep(SLEEP_TIME)


def specCommand(command, *args, **kwargs):
    print(f"Spec command called with {command}")
    time.sleep(SLEEP_TIME)


def readInput(caption='', default=None, timeout=1):
    print("readInput called")


def MrRobotoStart():
    print("MrRobotoStart called")
    time.sleep(SLEEP_TIME)


def MountSample(mr_roboto):
    print("MountSample called")
    time.sleep(SLEEP_TIME)


def DismountSample(mr_roboto):
    print("DismountSample called")
    time.sleep(SLEEP_TIME)


def GrabSample(mr_roboto, sx=0, sy=0):
    print("GrabSample called")
    time.sleep(SLEEP_TIME)
    return sx, sy


def ReplaceSample(mr_roboto, sx, sy):
    print("ReplaceSample called")
    time.sleep(SLEEP_TIME)


def ScanSample(mr_roboto):
    code = None
    print("ScanSample called")
    time.sleep(SLEEP_TIME)
    return code


def MovePose(mr_roboto, pose):
    print("MovePose called")
    time.sleep(SLEEP_TIME)


def SPEC_startspin():
    """Send SPEC command to start the capillary spinner"""

    print(f'Sending SPEC command startspin...')
    return


def SPEC_stopspin():
    """Send SPEC command to start the capillary spinner"""

    print(f'Sending SPEC command stopspin...')
    return


def create_SPEC_file(path, name):
    """Create new calibration spec file with date time stamp"""

    print(f'Creating new SPEC file {name} for calibration scan in {path}..')
    return


def set_PD_savepath(img_path):
    """Change PD Savepath to img_path

    args:
        img_path: New PD savepath
    """

    print(f'Changing PD SavePath to {img_path}')


def move_sample_stage(cassette_num=0):
    print(f'Moving sample stage to cassette number {cassette_num}...')
    time.sleep(SLEEP_TIME)
    print('Done', '\n')


def run_absorption_scan():
    command = f'umv v0gap 0.1; pd nosave; umvr bsx -5; umv tth 71.26'
    print(command)
    time.sleep(SLEEP_TIME)


def run_sample_scan(start=3, stop=113.55, steps=110):
    """Function to run sample scan

    Arguments:
        start {float} -- minimum 2th value to scan. Scan is performed from start to stop
        stop  {float} -- maximum 2th value for scan
        steps {int} -- number of steps
    """
    command = f'pscan  tth {start} {stop} 1 2 10 1 {steps}'
    print(f'Running sample scan [{command}]')
    time.sleep(SLEEP_TIME)
    print('Done', '\n')


def SPEC_scan_sample(remote_path, local_path, samplecode):
    """Main function to perform calibration

    Arguments:
        remote_path {str} -- path on remote computer (SPEC)
        local_path {str} -- path on local computer (Windows)
        samplecode  {str} -- string read from sample barcode
    """
    print(f"Spec scan sample called")
    time.sleep(SLEEP_TIME)


def MeasureSample(mr_roboto, ax, ay):
    print("MeasureSample called")
    time.sleep(SLEEP_TIME)