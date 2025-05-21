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
signal_state = 0

bus = can.interface.Bus(channel='vcan0', bustype='socketcan')

# Parses CAN frame and updates turn signal status
def update_signal_status(cf, maxdlen):
    try:
        len_cf = min(len(cf), maxdlen)
        if len_cf < signal_pos:
            return

        turn_status[0] = "ON" if cf[signal_pos] & CAN_LEFT_SIGNAL else "OFF"
        turn_status[1] = "ON" if cf[signal_pos] & CAN_RIGHT_SIGNAL else "OFF"

        socketio.emit("car_state",{'turn_status':turn_status}) 
    except:
        return

# Parses CAN frame and updates door status
def update_door_status(cf, maxdlen):
    try:
        len_cf = min(len(cf), maxdlen)
        if len_cf < door_pos:
            return

        door_status[0] = DOOR_LOCKED if cf[door_pos] & CAN_DOOR1_LOCK else DOOR_UNLOCKED
        door_status[1] = DOOR_LOCKED if cf[door_pos] & CAN_DOOR2_LOCK else DOOR_UNLOCKED
        door_status[2] = DOOR_LOCKED if cf[door_pos] & CAN_DOOR3_LOCK else DOOR_UNLOCKED
        door_status[3] = DOOR_LOCKED if cf[door_pos] & CAN_DOOR4_LOCK else DOOR_UNLOCKED
        socketio.emit("car_state",{'door_status':door_status}) 
    except:
        return

# Parses CAN frame and updates speed status 
def update_speed_status(cf, maxdlen):
    try:
        len_cf = min(len(cf), maxdlen)
        if len_cf < speed_pos + 1:
            return

        speed = cf[speed_pos]*256 + cf[speed_pos + 1]
        speed = speed / 100  # Speed in kilometers
        global current_speed
        current_speed = speed * 0.6213751  # mph
        socketio.emit("car_state",{'current_speed':current_speed})    
    except:
        return

#Capture CAN frames and calls corresponding status update functions
def can_network_intercept():
    
    try:
        while True:
            message = bus.recv()  # Receive a CAN message
            arbitration_id = message.arbitration_id
            byte_array = message.data
            message_data = [byte for byte in byte_array]

            # Specific arbitration IDs are identified and the corresponding status update functions are called
            if arbitration_id == signal_id:
                update_signal_status(message_data,8)
            elif arbitration_id == door_id:
                update_door_status(message_data,8)
            elif arbitration_id == speed_id:
                update_speed_status(message_data,8)   

    except KeyboardInterrupt:
        print("Received KeyboardInterrupt, exiting.")

    finally:
        bus.shutdown()

if __name__ == '__main__':

    # socketio.run(app, host='localhost', port=3050)
    flask_process = threading.Thread(target=socketio.run, kwargs={'app': app, 'host': 'localhost', 'port': 3050, 'allow_unsafe_werkzeug': True})
    function_process = threading.Thread(target=can_network_intercept)

    flask_process.start()
    function_process.start()

    flask_process.join()
    function_process.join()

    
    
