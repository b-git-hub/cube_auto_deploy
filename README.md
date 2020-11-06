# cube_auto_deploy
Program to auto-deploy CUBE. This will capture all calls from the CUCM/ITSP and pass them out a necessary outbound dial-peer. This is achieved by matching on the URI of the CUCM and ITSP. The benefit of matching on URI rather than destination patterns, incoming called/calling, etc is that it allows this solution to be a almost a one size fits all solution. It doesn't matter what country the code is ran in so long as the IPs/DNS are provide this code will accept any type of dialling patterns e.g if it's +44, 900353, 0061, they'll all be accepted and depending on who they're sent from will determine the path the call will take. If you're following Cisco’s best practise of globalising the number to e.164 prior to arriving to the CUBE and the ITSP supports e.164 dialling then this program is the right fit for you. Yes there will be exceptions were certain providers will need SIP profiles and others registrar information, something that I will look to further add as I develop into the future but if you just require a standard CUBE stood up, this will achieve that goal. Codecs supported are g711u/alaw

# Software Requirements
    Python 3.8
    NAPALM
    Netmiko
    requirements.txt 

# Running the code
    git clone https://github.com/b-git-hub/cube_auto_deploy/cube_deploy.py
    pip install requirements.txt 
    python cube_deploy.py

# Information required to run
    The program assumes that you already have the below information 
    IP Address of CUBE
    Username/Password
    ITSP media, signalling and gateway IP to provider
    Signalling protocols being used
    
# Operation
This program will configure CUBE and deploy 4 dial-peers, using server groups and dpgs any calls destined from the CUCM to the ITSP will automatically be sent to the ITSP and visa versa.
There isn't any manipulation of the calls being used, the program assumes that none is required.
There isn't any manipulation of SIP headers involved. If these are required, configure them seperately. 
The program is very much still in beta. I've not implemented error handling to capture in the event users put in IPs instead of a signalling protocol.
This will come in future iterations, this for the moment will deploy your CUBE provided you follow the prompts correctly.

    The operator of this code will need access to the CUBE via SSH
![Capture](https://user-images.githubusercontent.com/68473827/98389089-80c59300-204b-11eb-90a4-11e0396d3d94.JPG)
    
    
# Call Flow
The call flow is very simple, it takes the call from CUCM via any means and passes it through the CUBE to the ITSP without any manipulation other than signalling and media which is required to send/recieve calls. Matching from a CUBE perspective is done via the URI headers. This means 
![Capture](https://user-images.githubusercontent.com/68473827/98388699-fed56a00-204a-11eb-94f2-9695e7230427.JPG)

    
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

# Successful Output
    When the program has ran a successful out put will look like the below. The program will produce this for you. I've excluded any irrelevant configuration and my comments on the code can be seen with ()

    voice service voip
    ip address trusted list
    ipv4 1.1.1.2 255.255.255.255
    ipv4 1.1.1.3 255.255.255.255
    ipv4 2.2.2.3 255.255.255.255    (IPs of CUCM/ITSP for signalling any IPs not listed will get rejected)
    address-hiding
    allow-connections sip to sip
    no supplementary-service sip moved-temporarily
    no supplementary-service sip refer
    supplementary-service media-renegotiate
    redirect ip2ip
    fax protocol pass-through g711ulaw
    sip
    session refresh
    asserted-id pai
    early-offer forced
    midcall-signaling passthru
    pass-thru subscribe-notify-events all
    pass-thru content unsupp
    sip-profiles inbound
    !
    !
    voice class uri FromCUCM sip (IPs/DNS of all CUCM nodes inputted during run time)
    host ipv4:1.1.1.2
    host ipv4:1.1.1.3
    !
    voice class uri FromITSP sip (ITSP IP address)
    host ipv4:2.2.2.3
    voice class codec 1
     codec preference 1 g711alaw
    codec preference 2 g711ulaw
    !
    !
    !
    voice class dpg 1000
    dial-peer 1001
    !
    voice class dpg 1002
    dial-peer 1003
    !
    voice class server-group 1001
    ipv4 2.2.2.3 preference 1
    !
    voice class server-group 1003
    ipv4 1.1.1.2 preference 1
    ipv4 1.1.1.3 preference 2

    interface GigabitEthernet2
    ip address 1.1.1.1 255.255.255.0
    negotiation auto
    no mop enabled
    no mop sysid
    !
    interface GigabitEthernet3
    ip address 2.2.2.2 255.255.255.0
    negotiation auto
    no mop enabled
    no mop sysid
    !

    ip route 2.2.2.3 255.255.255.255 GigabitEthernet3 2.2.2.3  (Static routes to providers IPs via the gateway provided during runtime)
    ip route 2.2.2.4 255.255.255.255 GigabitEthernet3 2.2.2.3
    dial-peer voice 1000 voip
    description Incoming from CUCM
    session protocol sipv2
    session transport tcp
    destination dpg 1000
    incoming uri via FromCUCM
    voice-class codec 1  
    voice-class sip options-keepalive
    voice-class sip bind control source-interface GigabitEthernet2
    voice-class sip bind media source-interface GigabitEthernet2
    dtmf-relay rtp-nte
    fax protocol pass-through g711ulaw
    no vad
    !
    dial-peer voice 1001 voip
    description Outbound to ITSP
    destination-pattern 99999999$
    session protocol sipv2
    session transport udp
    session server-group 1001
    voice-class codec 1  
    voice-class sip options-keepalive
    voice-class sip bind control source-interface GigabitEthernet3
    voice-class sip bind media source-interface GigabitEthernet3
    dtmf-relay rtp-nte
    fax protocol pass-through g711ulaw
    no vad
    !
    dial-peer voice 1002 voip
    description Incoming from ITSP
    session protocol sipv2
    session transport udp
    destination dpg 1002
    incoming uri via FromITSP
    voice-class codec 1  
    voice-class sip options-keepalive
    voice-class sip bind control source-interface GigabitEthernet3
    voice-class sip bind media source-interface GigabitEthernet3
    dtmf-relay rtp-nte
    fax protocol pass-through g711ulaw
    no vad

    dial-peer voice 1003 voip
    description Outbound to ITSP
    destination-pattern 99999999$
    session protocol sipv2
    session transport tcp
    session server-group 1003
    voice-class codec 1  
    voice-class sip options-keepalive
    voice-class sip bind control source-interface GigabitEthernet2
    voice-class sip bind media source-interface GigabitEthernet2
    dtmf-relay rtp-nte
    fax protocol pass-through g711ulaw
    no vad

