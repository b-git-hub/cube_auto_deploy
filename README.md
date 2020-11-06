# cube_auto_deploy
Program to auto-deploy CUBE. This will capture all calls from the CUCM/ITSP and pass them out a neccessary outbound dial-peer.

# Software Requirements
    Python 3.8
    NAPALM
    Netmiko

# Running the code
    git clone https://github.com/b-git-hub/cube_auto_deploy/cube_deploy.py
    python cube_deploy.py

# Information required to run
    The program assumes that you already have the below information 
    IP Address of CUBE
    Username/Password
    ITSP media, signalling and gateway IP to provider
    Signalling protocols being used
    
# Operation
    This program will configure CUBE and deploy 4 dial-peers, using server groups and dpgs any calls destined from the CUCM to the ITSP will automatically
    be sent to the ITSP and visa versa.
    There isn't any manipulation of the calls being used, the program assumes that none is required.
    There isn't any manipulation of SIP headers involved. If these are required, configure them seperately. 
    The program is very much still in beta. I've not implemented error handling to capture in the event users put in IPs instead of a signalling protocol.
    This will come in future iterations, this for the moment will deploy your CUBE provided you follow the prompts correctly.
    
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
