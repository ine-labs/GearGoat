import subprocess

canplayer_command = 'canplayer -I "/app/backend/sample-can.log" -l i'

subprocess.run(canplayer_command, shell=True)
