# cube_auto_deploy
Program to auto-deploy CUBE. This will capture all calls from the CUCM/ITSP and pass them out a neccessary outbound dial-peer.

# Prerequirements
Python 3.8,
NAPALM,
Netmiko

# Running the code
git clone https://github.com/b-git-hub/cube_auto_deploy/cube_deploy.py
python cube_deploy.py

# CUBE Pre-Req Information
CUCM IPs, ITSP IP (signaling/media), internal/external interfaces, dial-peer numbers, signalling protocols
