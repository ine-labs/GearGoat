#!/bin/bash
python3 /app/backend/backend_controller.py & python3 /app/backend/backend_simulator.py & python3 /app/backend/traffic_player.py & python3 -m http.server 80 --directory /app/car_frontend
