# Stduio21 REST API
Access Now Playing information of Studio21 at `/current_song` endpoint

# Systemd service
```
[Unit]
Description=Studio21 REST API Service
After=network.target

[Service]
user=pi
WorkingDirectory=/home/pi/studio21_RestAPI
ExecStart=/home/pi/studio21_RestAPI/s21/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```
