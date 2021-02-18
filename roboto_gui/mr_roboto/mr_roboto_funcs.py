from .RobotController import *
import msvcrt

# Standard library imports
import sys, os, glob, fnmatch, re, time

# Other Imports
from datetime import datetime

from collections import OrderedDict
from copy import deepcopy

# This module imports

# XDart imports
sys.path.append('C:\\Users\\Public\\Documents\\repos\\xdart')
from ..pySSRL_bServer.bServer_funcs import *

SampleReadyPose = [145.333, -0.282, 195, 180, 0, -180]
SampleHeight = 69
MountReadyPose = [-47.761, -45.143, 351.589, -8.028, -89.263, -70.034]
MountDistance = 58.0
BarcodeScanPose = [45.526,-155.890,195.000,-180.000,0.000,-113.000]
spacing = 25.125
speed = 25

def readInput(caption='', default=None, timeout = 1):
    start_time = time.time()
    #sys.stdout.write('%s(%s):'%(caption, default))
    #sys.stdout.flush()
    input = ''
    while True:
        if msvcrt.kbhit():
            byte_arr = msvcrt.getche()
            if ord(byte_arr) == 13: # enter_key
                break
            elif ord(byte_arr) >= 32: #space_char
                input += "".join(map(chr,byte_arr))
        if len(input) == 0 and (time.time() - start_time) > timeout:
            #print("timing out, using from Rodefault value.")
            break

    #print('')  # needed to move to next line
    if len(input) > 0:
        return input
    else:
        return default

def MrRobotoStart():
    mr_roboto = RobotController('192.0.2.42')
    mr_roboto.Connect()
    mr_roboto.Activate()
    mr_roboto.Home()
    mr_roboto.SetJointVel(speed)
    mr_roboto.SetCartAngVel(speed)
    mr_roboto.SetCartLinVel(speed)
    mr_roboto.MoveJoints(0,0,0,0,0,0)
    mr_roboto.GripperOpen()
    return mr_roboto
    
def MountSample(mr_roboto):
    status = mr_roboto.GetStatusRobot()
    joints = mr_roboto.GetJoints()
    #if joints != [0.0,0.0,0.0,0.0,0.0,0.0]:
    #    print("Cannot mount sample from current position...")
    #    return
    mr_roboto.SetConf(1,1,-1)
    mr_roboto.MovePose(*MountReadyPose)
    mr_roboto.MoveLinRelWRF(-1*MountDistance, 0,0,0,0,0)
    mr_roboto.GripperOpen()
    mr_roboto.Delay(1)
    mr_roboto.MoveLinRelWRF(MountDistance, 0,0,0,0,0)
    mr_roboto.MoveJoints(0,0,0,0,0,0)
    
def DismountSample(mr_roboto):
    status = mr_roboto.GetStatusRobot()
    joints = mr_roboto.GetJoints()
    #print(joints)
    #if joints.all != 0.0
    #    print("Cannot mount sample from current position...")
    #    return
    mr_roboto.SetConf(1,1,-1)
    mr_roboto.MovePose(*MountReadyPose)
    mr_roboto.GripperOpen()
    mr_roboto.Delay(1)
    mr_roboto.MoveLinRelWRF(-1*MountDistance, 0,0,0,0,0)
    mr_roboto.GripperClose()
    mr_roboto.Delay(1)
    mr_roboto.MoveLinRelWRF(MountDistance, 0,0,0,0,0)
    mr_roboto.MoveJoints(0,0,0,0,0,0)
    
def GrabSample(mr_roboto, sx=0, sy=0):
    #Mr. Roboto grabs the sample
    mr_roboto.SetConf(1,1,1)
    mr_roboto.MovePose(*SampleReadyPose)
    mr_roboto.GripperOpen()
    mr_roboto.Delay(1)
    mr_roboto.MoveLinRelWRF(spacing*sx, spacing*sy, 0, 0, 0, 0)
    mr_roboto.MoveLinRelWRF(0,0,-1*SampleHeight,0,0,0)
    mr_roboto.GripperClose()
    mr_roboto.Delay(1)
    mr_roboto.MoveLinRelWRF(0,0,SampleHeight,0,0,0)
    #mr_roboto.MoveJoints(0,0,0,0,0,0)
    return sx, sy
    
def ReplaceSample(mr_roboto, sx, sy):
    #Mr. Roboto replaces the sample
    mr_roboto.SetConf(1,1,1)
    mr_roboto.MovePose(*SampleReadyPose)
    mr_roboto.MoveLinRelWRF(spacing*sx, spacing*sy, 0, 0, 0, 0)
    mr_roboto.MoveLinRelWRF(0,0,-1*SampleHeight,0,0,0)
    mr_roboto.GripperOpen()
    mr_roboto.Delay(1)
    mr_roboto.MoveLinRelWRF(0,0,SampleHeight,0,0,0)
    #mr_roboto.MoveJoints(0,0,0,0,0,0)
    
def ScanSample(mr_roboto):
    code = None
    mr_roboto.MovePose(*BarcodeScanPose)
    code = readInput(timeout = 3)
    barcode_joints = list(mr_roboto.GetJoints())
    #print(barcode_joints)
    if code:
        #mr_roboto.MoveJoints(0,0,0,0,0,0)
        return code
    sign = -1
    while not code:
        mr_roboto.SetJointVel(5)
        barcode_joints[-1] -= 30
        barcode_joints[-2] -= 10
        #print(barcode_joints)
        mr_roboto.MoveJoints(*barcode_joints)
        code = readInput(timeout=1)
        if code:
            break
        barcode_joints[-1] += 30
        barcode_joints[-2] += 10
        #print(barcode_joints)
        mr_roboto.MoveJoints(*barcode_joints)
        code = readInput(timeout=1)
        if code:
            break
        mr_roboto.SetJointVel(5)
        barcode_joints[-1] -= 30
        barcode_joints[-2] += 10
        #print(barcode_joints)
        mr_roboto.MoveJoints(*barcode_joints)
        code = readInput(timeout=1)
        if code:
            break
        barcode_joints[-1] += 30
        barcode_joints[-2] -= 10
        #print(barcode_joints)
        mr_roboto.MoveJoints(*barcode_joints)
        code = readInput(timeout=1)
        if code:
            break
        mr_roboto.MoveLinRelWRF(0,0,sign*25,0,0,0)
        sign *= -1
    mr_roboto.SetJointVel(speed)
    #mr_roboto.MoveJoints(0,0,0,0,0,0)
    return code
        
def SPEC_startspin():
    """Send SPEC command to start the capillary spinner"""

    print(f'Sending SPEC command startspin...')
    command = f'startspin'
    try:
        specCommand(command, queue=True)
    except Exception as e:
        print(e)
        print(f"Command '{command}' not sent")
        sys.exit()    
    return 
    
def SPEC_stopspin():
    """Send SPEC command to start the capillary spinner"""

    print(f'Sending SPEC command stopspin...')
    command = f'stopspin'
    try:
        specCommand(command, queue=True)
    except Exception as e:
        print(e)
        print(f"Command '{command}' not sent")
        sys.exit()    
    return 

def create_SPEC_file(path, name):
    """Create new calibration spec file with date time stamp"""

    print(f'Creating new SPEC file {name} for calibration scan in {path}..')
    command = f'newfile {path}/{name}'
    try:
        specCommand(command, queue=True)
    except Exception as e:
        print(e)
        print(f"Command '{command}' not sent")
        sys.exit()    
    return

def SPEC_stopspin():
    """Send SPEC command to start the capillary spinner"""

    print(f'Sending SPEC command stopspin...')
    command = f'stopspin'
    try:
        specCommand(command, queue=True)
    except Exception as e:
        print(e)
        print(f"Command '{command}' not sent")
        sys.exit()    
    return 

def set_PD_savepath(img_path):
    """Change PD Savepath to img_path
    
    args:
        img_path: New PD savepath
    """

    print(f'Changing PD SavePath to {img_path}')
    command = f'pd savepath {img_path}'
    try:
        specCommand(command, queue=True)
    except Exception as e:
        print(e)
        print(f"Command '{command}' not sent")
        sys.exit()

def move_sample_stage(cassette_num = 0):
    ald_pos = cassette_num * 4 * 25.4
    command = f'umv ald {ald_pos}'
    print(f'Moving sample stage to cassette number {cassette_num}...')
    try:
        specCommand(command, queue=True)
    except Exception as e:
        print(e)
        print(f"Command '{command}' not sent")
        sys.exit()
        
    # Wait till Scan is finished to continue
    print('Waiting for scan to finish..')
    wait_until_SPECfinished(polling_time=5)
    time.sleep(1)
    print('Done', '\n')

def run_absorption_scan():
    command = f'umv v0gap 0.1; pd nosave; umvr bsx -5; umv tth 71.26'
    try:
        specCommand(command, queue=True)
    except Exception as e:
        print(e)
        print(f"Command '{command}' not sent")
        sys.exit()
    wait_until_SPECfinished(polling_time=5)
    
    command = f'lup gony -1.5 1.5 60 1'
    try:
        specCommand(command, queue=True)
    except Exception as e:
        print(e)
        print(f"Command '{command}' not sent")
        sys.exit()
    wait_until_SPECfinished(polling_time=5)
    
    command = f'umv v0gap 0.75; pd save; umvr bsx 5'
    try:
        specCommand(command, queue=True)
    except Exception as e:
        print(e)
        print(f"Command '{command}' not sent")
        sys.exit()
    wait_until_SPECfinished(polling_time=5)
    

def run_sample_scan(start=3, stop=113.55, steps=110):
    """Function to run sample scan

    Arguments:
        start {float} -- minimum 2th value to scan. Scan is performed from start to stop
        stop  {float} -- maximum 2th value for scan
        steps {int} -- number of steps
    """
    command = f'pscan  tth {start} {stop} 1 2 10 1 {steps}'
    print(f'Running sample scan [{command}]')
    try:
        specCommand(command, queue=True)
    except Exception as e:
        print(e)
        print(f"Command '{command}' not sent")
        sys.exit()
        
    # Wait till Scan is finished to continue
    print('Waiting for scan to finish..')
    wait_until_SPECfinished(polling_time=5)
    time.sleep(5)
    print('Done', '\n')

def SPEC_scan_sample(remote_path, local_path, samplecode):
    """Main function to perform calibration

    Arguments:
        remote_path {str} -- path on remote computer (SPEC)
        local_path {str} -- path on local computer (Windows)
        samplecode  {str} -- string read from sample barcode
    """
    
    # Extract Sample Name from samplecode
    samplenum = samplecode.split()[-1]
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d-%H%M")
    print(f"Sample number is {samplenum}...")
    samplename = f"BL21Robot_{samplenum}-{timestamp}"

    # Remote (SPEC) Computer Paths
    remote_scan_path = f'{remote_path}/scans'
    remote_img_path  = f'{remote_path}/images'

    # Local (Windows) paths
    scan_path = os.path.join(local_path, 'scans')
    img_path  = os.path.join(local_path, 'images')
    pdi_path  = img_path

    # Make Directories if they don't exist
    print("Creating folders if they don't exist")
    os.makedirs(scan_path, exist_ok=True)
    os.makedirs(img_path, exist_ok=True)    

    # Check if filters are in place to allow direct beam scan
    #check_ready()
    
    # Save current pd_savepath, filename and scan number
    #saved_state = get_current_state()

    # Create remote_paths on SPEC computer if it doesn't exist
    #create_remote_paths(remote_scan_path, remote_img_path)

    # Create SPEC file and set PD savepath
    create_SPEC_file(remote_scan_path, samplename)
    print("SPEC file created...")
    set_PD_savepath(remote_img_path)
    print("PD_savepath set...")

    # Run direct beam scan
    run_absorption_scan()
    run_sample_scan()

    # Restore saved current pd_savepath, specfilename, and scan number
    #restore_state(saved_state)

def MeasureSample(mr_roboto, ax, ay):
    GrabSample(mr_roboto, ax, ay)
    code = ScanSample(mr_roboto)
    print("Sample code is " + str(code))
    mr_roboto.MoveJoints(0,0,0,0,0,0)
    mr_roboto.Delay(3)
    MountSample(mr_roboto)
    mr_roboto.Delay(1)
    mr_roboto.MoveJoints(0,0,0,0,0,0)
    #SPEC_startspin()
    #mr_roboto.Delay(2)
    #remote_path = '~/data/mr_roboto/Dec2020/'
    #local_path  = 'P:\\bl2-1\\mr_roboto\\Dec2020\\'
    #SPEC_scan_sample(remote_path, local_path, code)
    #SPEC_stopspin()
    DismountSample(mr_roboto)
    ReplaceSample(mr_roboto, ax, ay)
    mr_roboto.MoveJoints(0,0,0,0,0,0)
    mr_roboto.Delay(3)

if __name__ == "__main__":
    mr_roboto = MrRobotoStart()
    mr_roboto.Delay(2)
    mr_roboto.MoveJoints(0,0,0,0,0,0)

    #move_sample_stage(1)
    #MeasureSample(mr_roboto, -1,-1)
    #MeasureSample(mr_roboto, -1,0)
    #MeasureSample(mr_roboto, -1,1)
    #MeasureSample(mr_roboto, 0,-1)
    #MeasureSample(mr_roboto, 0,0)
    #MeasureSample(mr_roboto, 0,1)
    #MeasureSample(mr_roboto, 1,-1)
    #MeasureSample(mr_roboto, 1,0)
    #MeasureSample(mr_roboto, 1,1)

    move_sample_stage(0)
    #MeasureSample(mr_roboto, -1,-1)
    #MeasureSample(mr_roboto, -1,0)
    #MeasureSample(mr_roboto, -1,1)
    #MeasureSample(mr_roboto, 0,-1)
    MeasureSample(mr_roboto, 0,0)
    #MeasureSample(mr_roboto, 0,1)
    #MeasureSample(mr_roboto, 1,-1)
    #MeasureSample(mr_roboto, 1,0)
    #MeasureSample(mr_roboto, 1,1)

    #move_sample_stage(-1)
    #MeasureSample(mr_roboto, -1,-1)
    #MeasureSample(mr_roboto, -1,0)
    #MeasureSample(mr_roboto, -1,1)
    #MeasureSample(mr_roboto, 0,-1)
    #MeasureSample(mr_roboto, 0,0)
    #MeasureSample(mr_roboto, 0,1)
    #MeasureSample(mr_roboto, 1,-1)
    #MeasureSample(mr_roboto, 1,0)
    #MeasureSample(mr_roboto, 1,1)

    mr_roboto.MoveJoints(0,0,0,0,0,0)
    mr_roboto.Delay(3)

    mr_roboto.Deactivate()
    mr_roboto.Disconnect()