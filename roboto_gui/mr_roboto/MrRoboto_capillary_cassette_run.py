from RobotController import *
import time, msvcrt
import sys

def readInput(caption='', default=None, timeout = 0.25):
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
            #print("timing out, using default value.")
            break

    #print('')  # needed to move to next line
    if len(input) > 0:
        return input
    else:
        return default

SampleReadyPose = [145.333, -0.282, 195, 180, 0, -180]
SampleHeight = 69
MountReadyPose = [-47.761, -45.143, 351.589, -8.028, -89.263, -70.034]
MountDistance = 56.5

def MrRobotoStart():
    mr_roboto = RobotController('192.168.0.100')
    mr_roboto.Connect()
    mr_roboto.Activate()
    mr_roboto.Home()
    mr_roboto.SetJointVel(25)
    mr_roboto.SetCartAngVel(25)
    mr_roboto.SetCartLinVel(25)
    mr_roboto.MoveJoints(0,0,0,0,0,0)
    return mr_roboto
    
def MountSample(mr_roboto):
    status = mr_roboto.GetStatusRobot()
    joints = mr_roboto.GetJoints()
    if joints != [0,0,0,0,0,0]:
        print("Cannot mount sample from current position...")
        return
    mr_roboto.MovePose(MountReadyPose)
    mr_roboto.MoveRelWRF(-1*MountDistance, 0,0,0,0,0)
    mr_roboto.GripperOpen()
    mr_roboto.Delay(1)
    mr_roboto.MoveRelWRF(MountDistance, 0,0,0,0,0)
    mr_roboto.MoveJoints(0,0,0,0,0,0)

#Connect, Activate, Home, and zero Mr. Roboto
mr_roboto = RobotController('192.168.0.100')
mr_roboto.Connect()
mr_roboto.Activate()
mr_roboto.Home()
mr_roboto.MoveJoints(0,0,0,0,0,0)

#Set Mr. Roboto Motion Speeds
mr_roboto.SetJointVel(25)
mr_roboto.SetCartAngVel(25)
mr_roboto.SetCartLinVel(25)

#Mr. Roboto grabs the sample
mr_roboto.SetConf(1,1,1)
mr_roboto.MovePose(145.333, -0.282, 195, 180, 0, -180)
mr_roboto.GripperOpen()
mr_roboto.Delay(1)
mr_roboto.LinRelWRF(0,0,-69,0,0,0)
mr_roboto.GripperClose()
mr_roboto.Delay(1)
mr_roboto.LinRelWRF(0,0,69,0,0,0)

#Mr. Roboto scans the sample barcode
code = None
mr_roboto.MovePose()
mr_roboto.Delay(3)  #this is just to make sure the move can finish
barcode_joints_1 = mr_roboto.GetJoints()
barcode_joints_2 = barcode_joints_1
barcode_joints_2[5] += 30
while not code:
    code = readInput()
    if code:
        break
    mr_roboto.MoveJoints(barcode_joints_2)
    code = readInput()
    if code:
        break
    mr_roboto.MoveJoints(barcode_joints_1)
    code = readInput()
    if code:
        break
mr_roboto.MoveJoints(0,0,0,0,0,0)


#Mr. Roboto mounts sample
mr_roboto.MovePose(MountReadyPose)
mr_roboto.MoveRelWRF(-1*MountDistance, 0,0,0,0,0)
mr_roboto.GripperOpen()
mr_roboto.Delay(1)
mr_roboto.MoveRelWRF(MountDistance, 0,0,0,0,0)
mr_roboto.MoveJoints(0,0,0,0,0,0)



#Mr. Roboto returns sample to holder
mr_roboto.MoveLinRelTRF(0,0,-150,0,0,0)
mr_roboto.MoveJoints(0,0,0,0,0,0)
mr_roboto.MovePose(200.315, -115.999, 120, -180, 0, -154.946)
mr_roboto.SetJointVel(5)
mr_roboto.MovePose(200.315, -115.999, 68.323, -180, 0, -154.946)
mr_roboto.Delay(0.5)
mr_roboto.GripperOpen()
mr_roboto.Delay(1)

#Return Mr. Roboto to rest position
mr_roboto.MovePose(200.315, -115.999, 120, -180, 0, -154.946)
mr_roboto.SetJointVel(25)
mr_roboto.MoveJoints(0,0,0,0,0,0)

#Mr. Roboto has done a good job, let him have a rest
mr_roboto.Deactivate()
mr_roboto.Disconnect()