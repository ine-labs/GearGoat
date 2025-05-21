import can
from flask import Flask
import os
import sys
import random
import time
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit
import threading

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app,resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app,cors_allowed_origins='*')

DOOR_LOCKED = 0
DOOR_UNLOCKED = 1
OFF = 0
ON = 1
DEFAULT_DOOR_ID = 411 # 0x19b
DEFAULT_DOOR_BYTE = 2
CAN_DOOR1_LOCK = 1
CAN_DOOR2_LOCK = 2
CAN_DOOR3_LOCK = 4
CAN_DOOR4_LOCK = 8
DEFAULT_SIGNAL_ID = 392 # 0x188
DEFAULT_SIGNAL_BYTE = 0
CAN_LEFT_SIGNAL = 1
CAN_RIGHT_SIGNAL = 2
DEFAULT_SPEED_ID = 580 # 0x244
DEFAULT_SPEED_BYTE = 3
DEFAULT_SIGNAL_POS = 0
DEFAULT_DOOR_POS = 2
DEFAULT_SPEED_POS = 3
DEFAULT_CAN_TRAFFIC = "./sample-can.log"
MAX_SPEED = 90.0
ACCEL_RATE = 8.0 

door_len = DEFAULT_DOOR_POS + 1
signal_len = DEFAULT_DOOR_POS + 1
speed_len = DEFAULT_SPEED_POS + 2
canfd_on = 1
debug = 0
randomize = 0
seed = 0
door_pos = DEFAULT_DOOR_BYTE  
signal_pos = DEFAULT_SIGNAL_BYTE  
speed_pos = DEFAULT_SPEED_BYTE  
current_speed = 0
door_status = [0] * 4 
turn_status = [0] * 2
door_id = DEFAULT_DOOR_ID
signal_id = DEFAULT_SIGNAL_ID
speed_id = DEFAULT_SPEED_ID
lock_enabled = 0
unlock_enabled = 0
door_state = 0xF
signal_state = 0
throttle = 0
current_speed = 0.0
turning = 0
currentTime = 0
lastAccel = 0
lastTurnSignal = 0
traffic_log = DEFAULT_CAN_TRAFFIC

bus = can.interface.Bus(channel='vcan0', bustype='socketcan')

# Sends the CAN packet to the CAN Bus
def send_packet(arbitration_id, message_data):
    message = can.Message(arbitration_id=arbitration_id, data=message_data, is_extended_id=False)
    bus.send(message)  


# Calls "send_packet" to send turn signal data to the CAN Bus
def send_turn_signal(signal_state):
    cf = [0]*8 
    arb_id = signal_id
    cf[signal_pos] = signal_state
    cf = bytearray(cf)
    send_packet(arb_id, cf)

# Calls "send_packet" to send door lock data to the CAN Bus
def send_lock(door):
    global door_state
    cf = [0]*8
    door_state |= door
    arb_id = door_id
    cf[door_pos] = door_state
    cf = bytearray(cf)
    send_packet(arb_id, cf)

# Calls "send_packet" to send door unlock data to the CAN Bus
def send_unlock(door):
    global door_state
    cf = [0]*8
    door_state &= ~door
    arb_id = door_id
    cf[door_pos] = door_state
    cf = bytearray(cf)
    send_packet(arb_id, cf)

# Updates the signal state value based on the turning status and calls "send_turn_signal" 
def check_turn():
    
    global currentTime, lastTurnSignal, turning, signal_state

    if currentTime > lastTurnSignal + 500:
        if turning < 0:
            signal_state ^= CAN_LEFT_SIGNAL
        elif turning > 0:
            signal_state ^= CAN_RIGHT_SIGNAL
        else:
            signal_state = 0

        send_turn_signal(signal_state)
        lastTurnSignal = currentTime

# Calls "send_packet" to send speed data to the CAN Bus
def send_speed():
    global current_speed, speed_id, speed_pos
    cf = [0]*8
    kph = int((current_speed / 0.6213751) * 100)
    cf = [0]*8
    cf[speed_pos + 1] = int(kph & 0xff)
    cf[speed_pos] = int((kph >> 8) & 0xff) # Extract the least significant 8 bit
    # if kph == 0:
    #     cf[speed_pos] = 1
    #     cf[speed_pos + 1] = random.randint(100,354)

    arb_id = speed_id
    send_packet(arb_id, cf)


# Calls "send_speed" to update the speed values
def check_accel():
    global lastAccel, currentTime, throttle, current_speed 
    rate = MAX_SPEED / (ACCEL_RATE * 100)
    # Updated every 10 ms
    if currentTime > lastAccel + 10:
        if throttle < 0:
            current_speed -= rate
            if current_speed < 1:
                current_speed = 0
                # throttle = 0                
        elif throttle > 0:
            current_speed += rate
            if current_speed > MAX_SPEED:
                # Limiter
                current_speed = MAX_SPEED
        send_speed()
        lastAccel = currentTime


# Reads the data from the frontend
@socketio.on('canframe')
def handle_message(data):

    global signal_state, turning, currentTime, lastTurnSignal, lock_enabled, unlock_enabled, lastAccel, throttle, current_speed
    print("######################")
    print(data)

    # Call respective functions based on the data received
    if "turning" in data:
        turning = data['turning']

    elif "unlockdoor" in data:
        door_id = data['unlockdoor']
        if door_id == '1st':
            send_unlock(CAN_DOOR1_LOCK)
        elif door_id == '2nd':
            send_unlock(CAN_DOOR2_LOCK)
        elif door_id == '3rd':
            send_unlock(CAN_DOOR3_LOCK)
        elif door_id == '4th':
            send_unlock(CAN_DOOR4_LOCK)                                    
    
    elif "lockdoor" in data:
        door_id = data['lockdoor']
        if door_id == '1st':
            send_lock(CAN_DOOR1_LOCK)
        elif door_id == '2nd':
            send_lock(CAN_DOOR2_LOCK)
        elif door_id == '3rd':
            send_lock(CAN_DOOR3_LOCK)
        elif door_id == '4th':
            send_lock(CAN_DOOR4_LOCK)     

    elif "throttle" in data:
        throttle = data['throttle']

#Handles all controller messages from frontend.
def can_controller_intercept():
    global throttle, currentTime
    while(True): 

        currentTime = int(time.time() * 1000)

        # if throttle > 0 or throttle < 0:
        check_accel()
        
        check_turn()

        # Introduce a 5-millisecond delay
        time.sleep(0.005)        

if __name__ == '__main__':

    # socketio.run(app, host='localhost', port=3500)
    flask_process = threading.Thread(target=socketio.run, kwargs={'app': app, 'host': 'localhost', 'port': 3500, 'allow_unsafe_werkzeug': True})
    function_process = threading.Thread(target=can_controller_intercept)

    flask_process.start()
    function_process.start()

    flask_process.join()
    function_process.join()

    
    
