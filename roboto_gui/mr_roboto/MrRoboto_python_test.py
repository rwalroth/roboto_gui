from RobotController import *
import time, msvcrt
import sys

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

SampleReadyPose = [145.333, -0.282, 195, 180, 0, -180]
SampleHeight = 69
MountReadyPose = [-47.761, -45.143, 351.589, -8.028, -89.263, -70.034]
MountDistance = 56.5
BarcodeScanPose = [45.526,-155.890,195.000,-180.000,0.000,-113.000]
speed = 25

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
	mr_roboto.MoveLinRelWRF(25.4*sx, 25.4*sy, 0, 0, 0, 0)
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
	mr_roboto.MoveLinRelWRF(25.4*sx, 25.4*sy, 0, 0, 0, 0)
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


if __name__ == "__main__":
	mr_roboto = MrRobotoStart()
	mr_roboto.Delay(2)
	#mr_roboto.GripperOpen()
	#mr_roboto.Delay(0.5)
	#mr_roboto.GripperClose()
	#mr_roboto.Delay(0.5)
	#mr_roboto.GripperOpen()

	ax, ay = GrabSample(mr_roboto,-1,0)
	code = ScanSample(mr_roboto)
	print("Sample code is " + str(code))
	ReplaceSample(mr_roboto, ax, ay)

	ax, ay = GrabSample(mr_roboto,0,0)
	code = ScanSample(mr_roboto)
	print("Sample code is " + str(code))
	ReplaceSample(mr_roboto, ax, ay)

	ax, ay = GrabSample(mr_roboto,1,0)
	code = ScanSample(mr_roboto)
	print("Sample code is " + str(code))
	ReplaceSample(mr_roboto, ax, ay)



	ax, ay = GrabSample(mr_roboto,-1,-1)
	code = ScanSample(mr_roboto)
	print("Sample code is " + str(code))
	mr_roboto.MoveJoints(0,0,0,0,0,0)
	#mr_roboto.Delay(3)
	MountSample(mr_roboto)
	mr_roboto.Delay(1)
	DismountSample(mr_roboto)
	ReplaceSample(mr_roboto, ax, ay)
	mr_roboto.MoveJoints(0,0,0,0,0,0)
	mr_roboto.Delay(3)

	mr_roboto.Deactivate()
	mr_roboto.Disconnect()
