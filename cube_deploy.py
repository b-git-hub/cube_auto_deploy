#!/usr/bin/python3



from netmiko import ConnectHandler
from napalm import get_network_driver
from getpass import getpass
import json



class IP_Addr_Change:
    def __init__(self, ip_change, interface):
        self.ip_change = ip_change
        self.interface = interface
    def change_ip_addr(self):
        self.subnet_mask = input("Please input the subnet mask in dotted format: ")
        config_commands = [f"int {self.interface}", f"ip address {self.ip_change} {self.subnet_mask}", "no sh"]
        ios_connection.send_config_set(config_commands)
    def change_ip_addr_verify(self):
        output = ios_connection.send_command(f"show run interface {self.interface}")
        print (output)

class Add_IP_Routes:
    def __init__(self, route, interface, gateway):
        self.route = route
        self.interface = interface
        self.gateway = gateway
        self.subnet_mask = "255.255.255.255"
    def add_route_provider(self):
        config_commands = [f"ip route {self.route} {self.subnet_mask} {self.interface} {self.gateway}"]
        ios_connection.send_config_set(config_commands)






#Get user to fill in there details
ios_connection_details = {"device_type": "cisco_ios"}
input_ip_addr = input("Input the IP/DNS of the CUBE: ")
input_username = input("Input username: ")
input_password = getpass("input password: ")

#Build the SSH connection to the CUBE with Netmiko
ios_connection_details["ip"] = input_ip_addr
ios_connection_details["username"] = input_username
ios_connection_details["password"] = input_password
ios_connection = ConnectHandler(**ios_connection_details)

#Build SSH for NAPALM
driver = get_network_driver("ios")
iosvl2 = driver(f"{input_ip_addr}", f"{input_username}", f"{input_password}")
iosvl2.open()

#Verify interfaces for users
output = ios_connection.send_command("show ip int brief")
print (output)

#Verify the internal/external interfaces for CUBE
internal_cube_interface = input("Specify the internal interface as listed above: ")
external_cube_interface = input("Specify the external interface as listed above: ")

#Verify if the internal IP address needs to be updated
verify_ip_change = input (f"Does they IP address of {internal_cube_interface} need to be updated (Y/N): ")
while True:
    if verify_ip_change == "Y":
        internal_ip = input (f"Please provide the new IP address for {internal_cube_interface}: ")
        interface_change = IP_Addr_Change(internal_ip, internal_cube_interface)
        interface_change.change_ip_addr()
        interface_change.change_ip_addr_verify()
        break
    elif verify_ip_change == "N":
        internal_ip = iosvl2.get_interfaces_ip()
        internal_ip = internal_ip[f"{internal_cube_interface}"]["ipv4"]
        for key in internal_ip.items():
            internal_ip  = key[0]
            print (f"The following IP has been detected as the internal IP {internal_ip}")
            break
        break
    else:
        print ("Please input a valid response")
        continue

#Verify if the external IP address needs to be updated
verify_ip_change = input (f"Does they IP address of {external_cube_interface} need to be updated (Y/N): ")
while True:
    if verify_ip_change == "Y":
        external_ip = input (f"Please provide the new IP address for {external_cube_interface}: ")
        interface_change = IP_Addr_Change(external_ip, external_cube_interface)
        interface_change.change_ip_addr()
        interface_change.change_ip_addr_verify()
        break
    elif verify_ip_change == "N":
        external_ip = iosvl2.get_interfaces_ip()
        external_ip = external_ip[f"{external_cube_interface}"]["ipv4"]
        for key in external_ip.items():
            external_ip  = key[0]
            print (f"The following IP has been detected as the external IP {external_ip}")
            break
        break
    else:
        print ("Please input a valid response")
        continue

#Enter CUCM to create a list
cucm_signalling_protocol = input("Please input CUCM signalling protocol: ")
number_of_cucm = int(input ("How many CUCM are required: "))
cucm_ip = []
for i in range(number_of_cucm):
    int_cucm_ip = input("Please input CUCM IP address: ")
    cucm_ip.append(int_cucm_ip)

print(cucm_ip)

#ITSP information
itsp_signalling_ip = input ("Please input your ITSP signalling IP: ")
itsp_media_ip = input ("Please input your ITSP media IP: ")
itsp_route_ip = input("Please input the ITSP gateway IP: ")
itsp_signalling_protocol = input("Please input the signalling protocol to the ITSP: ")

#Add routes for ITSP
itsp_signalling_ip_route = Add_IP_Routes(itsp_signalling_ip, external_cube_interface, itsp_route_ip)
itsp_signalling_ip_route.add_route_provider()
itsp_media_ip_route = Add_IP_Routes(itsp_media_ip, external_cube_interface, itsp_route_ip)
itsp_media_ip_route.add_route_provider()

#Add voip service voip requirements loop through CUCM for trust
for cucm_ip_trusted in cucm_ip:
    config_commands = ["voice service voip", "ip address trusted list", f"ipv4 {cucm_ip_trusted} 255.255.255.255"]
    ios_connection.send_config_set(config_commands)

config_commands = ["voice service voip", "ip address trusted list", f"ipv4 {itsp_signalling_ip} 255.255.255.255"]
ios_connection.send_config_set(config_commands)



config_commands = [
    f"voice service voip", "address-hiding", "allow-connections sip to sip",
     "no supplementary-service sip moved-temporarily", "no supplementary-service sip refer",
     "supplementary-service media-renegotiate", "redirect ip2ip",
     "fax protocol pass-through g711ulaw", "sip",
     "session refresh", "asserted-id pai", "early-offer forced",
     "midcall-signaling passthru", "pass-thru subscribe-notify-events all",
     "pass-thru content unsupp", "sip-profiles inbound"
     ]
ios_connection.send_config_set(config_commands)

#Dial-peers need to be added before pushing configuration due to IOS limit
dial_peer_range = int(input("Please enter the starting range for the dial-peers, this will create 4 dial-peers beginning with your number: "))
dial_peer_range_initial = dial_peer_range
dial_peer_list = []
for i in range(0, 4):
    config_commands = [f"dial-peer voice {dial_peer_range_initial} voip"]
    ios_connection.send_config_set(config_commands)
    dial_peer_list.append(dial_peer_range_initial)
    dial_peer_range_initial = dial_peer_range_initial+1

#Create voice class URI for CUCM
for cucm_ip_uri in cucm_ip:
    config_commands = ["voice class uri FromCUCM sip", f"host ipv4:{cucm_ip_uri}"]
    ios_connection.send_config_set(config_commands)

#Create voice class URI for ITSP
config_commands = ["voice class uri FromITSP sip", f"host ipv4:{itsp_signalling_ip}"]
ios_connection.send_config_set(config_commands)

#Create voice class codec
config_commands = ["voice class codec 1", "codec preference 1 g711alaw", "codec preference 2 g711ulaw"]
ios_connection.send_config_set(config_commands)

#Add Incoming DPG from CUCM
config_commands = [f"voice class dpg {dial_peer_list[0]}", f"dial-peer {dial_peer_list[1]}"]
ios_connection.send_config_set(config_commands)

#Add Incoming DPG from ITSP
config_commands = [f"voice class dpg {dial_peer_list[2]}", f"dial-peer {dial_peer_list[3]}"]
ios_connection.send_config_set(config_commands)

#Add voice class server-group from CUCM towards ITSP
config_commands = [f"voice class server-group {dial_peer_list[1]}", f"ipv4 {itsp_signalling_ip} preference 1"]
ios_connection.send_config_set(config_commands)

#Add voice class server-group from ITSP towards CUCM
pref = 1
for cucm_ip_server_group in cucm_ip:
    config_commands = [f"voice class server-group {dial_peer_list[3]}", f"ipv4 {cucm_ip_server_group} preference {pref}"]
    ios_connection.send_config_set(config_commands)
    pref = pref+1

#Incoming Dial-Peer from CUCM can now be configured
config_commands = [
    f"dial-peer voice {dial_peer_list[0]} voip", "description Incoming from CUCM", 
    "session protocol sipv2", f"session transport {cucm_signalling_protocol}",
    f"destination dpg {dial_peer_list[0]}", "incoming uri via FromCUCM",
    "voice-class codec 1", "voice-class sip options-keepalive",
    f"voice-class sip bind control source-interface {internal_cube_interface}",
    f"voice-class sip bind media source-interface {internal_cube_interface}",
    "dtmf-relay rtp-nte", "fax protocol pass-through g711ulaw", "no vad"
]
ios_connection.send_config_set(config_commands)

#Outgoing dial-peer from CUCM to ITSP 
config_commands = [
    f"dial-peer voice {dial_peer_list[1]} voip", "description Outbound to ITSP", 
    "session protocol sipv2", f"session transport {itsp_signalling_protocol}",
    f"destination-pattern 99999999$", f"session server-group {dial_peer_list[1]}",
    "voice-class codec 1", "voice-class sip options-keepalive",
    f"voice-class sip bind control source-interface {external_cube_interface}",
    f"voice-class sip bind media source-interface {external_cube_interface}",
    "dtmf-relay rtp-nte", "fax protocol pass-through g711ulaw", "no vad"
]
ios_connection.send_config_set(config_commands)

#Incoming Dial-Peer from ITSP
config_commands = [
    f"dial-peer voice {dial_peer_list[2]} voip", "description Incoming from ITSP", 
    "session protocol sipv2", f"session transport {itsp_signalling_protocol}",
    f"destination dpg {dial_peer_list[2]}", "incoming uri via FromITSP",
    "voice-class codec 1", "voice-class sip options-keepalive",
    f"voice-class sip bind control source-interface {external_cube_interface}",
    f"voice-class sip bind media source-interface {external_cube_interface}",
    "dtmf-relay rtp-nte", "fax protocol pass-through g711ulaw", "no vad"
]
ios_connection.send_config_set(config_commands)

#Outgoing dial-peer from ITSP to CUCM 
config_commands = [
    f"dial-peer voice {dial_peer_list[3]} voip", "description Outbound to ITSP", 
    "session protocol sipv2", f"session transport {cucm_signalling_protocol}",
    f"destination-pattern 99999999$", f"session server-group {dial_peer_list[3]}",
    "voice-class codec 1", "voice-class sip options-keepalive",
    f"voice-class sip bind control source-interface {internal_cube_interface}",
    f"voice-class sip bind media source-interface {internal_cube_interface}",
    "dtmf-relay rtp-nte", "fax protocol pass-through g711ulaw", "no vad"
]
ios_connection.send_config_set(config_commands)


print("Verify running configuration")
output = ios_connection.send_command("show run")
print (output)