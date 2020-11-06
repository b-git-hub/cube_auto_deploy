# cube_auto_deploy
Program to auto-deploy CUBE. This will capture all calls from the CUCM/ITSP and pass them out a neccessary outbound dial-peer.

# Prerequirements
    Python 3.8
    NAPALM
    Netmiko

# Running the code
    git clone https://github.com/b-git-hub/cube_auto_deploy/cube_deploy.py
    python cube_deploy.py

# Assumptions - You as a user
    The program assumes that you already have the below information 
    IP Address of CUBE
    Username/Password
    ITSP media, signalling and gateway IP to provider
    Signalling protocols being used
# Assumptions - Hardware 
    This code was tested on CSR and ISR4331. It should function on any Cisco device that supports CUBE as it is using it's standard commands
# Enviornment Variables
    input_ip_addr = Hostname (must be resolvable) or IP address of CSR/ISR
    input_username = User with priviledge to make configuration changes
    input_password = Password for User
    internal_cube_interface = internal interface for binding signalling/media. This is the interface that the CUCM SIP trunk will send traffic towards and also recieve
    external_cube_interface = external interface for binding signalling/media. This is the interface that the ITSP SIP trunk will send traffic towards and also recieve
    verify_ip_change = Prompt to register response to external/internal IP address changes requirements
    external_ip = Verify the IP of the external interface
    internal_ip = Verifying the IP of the external interface
    subnet_mask = Used in methods to verify subnet during IP address change on internal/external interface
    cucm_signalling_protocol = CUCM signalling protocol for SIP trunks (tcp/udp)
    number_of_cucm = Number of CUCM in the cluster
    cucm_ip = IP/Hostnames of each CUCM held in a list
    itsp_signalling_ip = ITSP signaling IP
    itsp_media_ip = ITSP media IP
    itsp_route_ip = Route to use to forward traffic to ITSP SIP gateway
    itsp_signalling_protocol = ITSP signalling protocol(udp/tcp)
    dial_peer_range = Dial-Peer numbering . It will ask for a single number and create 4 dialpeer 1 after another a.g 1000 will result in 1000,1001,1002 and 1003   being created 

# License
Copyright (C) 2020 Brian McBride
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software           Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
