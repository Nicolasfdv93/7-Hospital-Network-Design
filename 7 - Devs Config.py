Project 7 – Hospital Network Design - Devs Configuration

### ROUTERS ###

## ALL ROUTERS ##

En
Conf t
Int se0/0/0
No shut
Int se0/0/1
No shut
Int se0/1/0
No shut
Int se0/1/1
No shut

Enable password cisco
No ip domain lookup
Banner motd ## Unauthorized access is punishable by Law ##
Line console 0
Password cisco
Login
Exit
Service password-encryption
Ip domain name cisco.net
Username admin password cisco
Crypto key generate rsa
1024
Line vty 0 15
Login local
Transport input ssh
Ip ssh version 2
Do wr
Exit

## HQ-ROUTER ##

En
Conf t
Hostname HQ-Router

Int ran g0/0-2
No shut

// g0/2 performs a network with Server-Side Site, it’s not a point-to-point

Int g0/0
Ip address 192.168.102.82 255.255.255.252
Exit

Int g0/1
Ip address 192.168.102.86 255.255.255.252
Exit

Int g0/2
Ip address 192.168.102.65 255.255.255.240
Exit

Int se0/0/0
Ip address 195.136.17.1 255.255.255.252
Exit

Int se0/0/1
Ip address 195.136.17.5 255.255.255.252
Exit

Int se0/1/0
Ip address 192.168.102.89 255.255.255.252
Exit

Int se0/1/0
Clock rate 64000
exit

// OSPF
// HQ-Router will be the DR router – Priority 10
// Reminder: Change auto-cost reference, its too low.

Router ospf 10
Ip ospf priority 10
Auto-cost reference-bandwidth 100000
Network 192.168.102.80 0.0.0.3 area 0
Network 192.168.102.84 0.0.0.3 area 0
Network 192.168.102.88 0.0.0.3 area 0
Network 192.168.102.64 0.0.0.15 area 0
Network 195.136.17.0 0.0.0.3 area 0
Network 195.136.17.8 0.0.0.3 area 0
Network 192.168.0.0 0.0.0.3 area 0
Exit

// Default static route – If the packet  doesn´t go to the internal network 
// it will be forwarded either to ISP1 or ISP2.
// Backup path (ISP2) should have higher administrative distance than Main(ISP1). 

Ip route 0.0.0.0 0.0.0.0 195.136.17.2
Ip route 0.0.0.0 0.0.0.0 195.136.17.6 70

// Inter-Vlan routing – Allows SSS-Department (VLAN70)
// to communicate with the rest of the vlans.

Int g0/2
No ip address
Int g0/2.70
Encapsulation dot1q 70
Ip address 192.168.102.65 255.255.255.240
Exit
Do wr

// PAT outside: Those interfaces that are connected to ISP.
// PAT inside: those interfaces that are connected to the internal network.

Int se0/0/0
Ip nat outside
Exit
Int se0/0/1
Ip nat outside
Exit
Int se0/1/0
Ip nat inside
Int ran g0/0-2
ip nat inside
exit

access-list 1 permit 192.168.100.0 0.0.0.63
access-list 1 permit 192.168.100.64 0.0.0.63
access-list 1 permit 192.168.100.128 0.0.0.63
access-list 1 permit 192.168.100.192 0.0.0.63
access-list 1 permit 192.168.101.0 0.0.0.63
access-list 1 permit 192.168.101.64 0.0.0.63
exit

ip nat inside source list 1 interface se0/0/0 overload
ip nat inside source list 1 interface se0/0/1 overload
exit
wr

// Site-to-Site GRE over IPSec – Activate securityk9 packet if needed
// Use route summarization + ACL * 
// ACLs format: ACL N + Permit/Deny + ip Network_Source & WC + Network_Dest & WC

License boot module c2900 technology-package securityk9
Int tunnel 1
Ip address 192.168.0.1 255.255.255.252
Bandwidth 10000
Tunnel source se0/1/0
Tunnel destination 192.168.102.90
Exit

Access-list 110 permit ip 192.168.100.0 0.0.0.255 192.168.101.128 0.0.0.255
access-list 110 permit ip 192.168.101.0 0.0.0.127 192.168.101.128 0.0.0.255
Exit

crypto isakmp policy 10
Encryption aes 256
Authentication pre-share
Group 5
Exit

Crypto isakmp key vpnproyect7 address 192.168.102.90
Exit

Crypto ipsec transform-set VPN-SET esp-aes esp-sha-hmac
Crypto map VPN-MAP 10 ipsec-isakmp
Description # VPN to Branch-Network #
Set peer 192.168.102.90
Set transform-set VPN-SET
Match address 110
Exit
Int s0/1/0
Crypto map VPN-MAP
exit
Do wr

* //Route Summarization
Source Networks

{192.168.100.0/26
192.168.100.64/26
192.168.100.128/26
192.168.100.192/26
} Summarized as 192.168.100.0 /24 -> First 24 bits of those ips network match.

{192.168.101.0 /26
192.168.101.64 /26
} Summarized as 192.168.101.0 /25 -> First 25 bits of those ips network match.

Destination Networks
{192.168.101.128 /27
192.168.101.160 /27
192.168.101.192 /27
192.168.101.224 /27
192.168.102.0 /27
192.168.102.32 /27
} Summarized as 192.168.101.128 /24 -> First 24 bits of those ips network match.

## BRANCH-ROUTER ##

En
Conf t
Hostname Branch-Router

Int ran g0/0-2
No shut

Int g0/0
Ip address 192.168.102.94 255.255.255.252
Exit
Int g0/1
Ip address 192.168.102.98 255.255.255.252
exit
Int se0/0/0
Ip address 195.136.17.13 255.255.255.252
Exit
Int se0/0/1
Ip address 195.136.17.9 255.255.255.252
Exit
Int se0/1/0
Ip address 192.168.102.90 255.255.255.252
Exit
Do wr

// OSPF
// Branch-Router will be the BDR router – Priority 5
// Reminder: Change auto-cost reference, its too low.

Router ospf 10
Ip ospf priority 5
Auto-cost reference-bandwidth 100000 
Network 192.168.102.92 0.0.0.3 area 0
Network 192.168.102.96 0.0.0.3 area 0
Network 192.168.102.88 0.0.0.3 area 0
Network 195.136.17.12 0.0.0.3 area 0
Network 195.136.17.8 0.0.0.3 area 0
Network 192.168.0.0 0.0.0.3 area 0

// Default static route – If the packet doesn´t go to the internal network 
// it will be forwarded either to ISP1 or ISP2.
// Backup path (ISP2) should have higher administrative distance than Main(ISP1). 

Ip route 0.0.0.0 0.0.0.0 195.136.17.14 
Ip route 0.0.0.0 0.0.0.0 195.136.17.10 70
Do wr

// PAT
// PAT outside: Those interfaces that are connected to ISP
// PAT inside: those interfaces that are connected to the internal network.

Int se0/0/0
Ip nat outside
exit

Int se0/0/1
Ip nat outside
Exit

Int se0/1/0
Ip nat inside
Exit

Int ran g0/0-1
Ip nat inside
Exit

Access-list 1 permit 192.168.101.128 0.0.0.31
access-list 1 permit 192.168.101.160 0.0.0.31
access-list 1 permit 192.168.101.192 0.0.0.31
access-list 1 permit 192.168.101.224 0.0.0.31
access-list 1 permit 192.168.102.0 0.0.0.31
access-list 1 permit 192.168.102.32 0.0.0.31
ip nat inside source list 1 interface se0/0/0 overload
ip nat inside source list 1 interface se0/0/1 overload
exit
wr

// Site-to-Site GRE over IPSec – Activate securityk9 packet if needed
// Use route summarization + ACL * 
// ACLs format: ACL N + Permit/Deny + ip Network_Source & WC + Network_Dest & WC

License boot module c2900 technology-package securityk9
Int tunnel 1
Ip address 192.168.0.2 255.255.255.252
Bandwidth 10000
Tunnel source se0/1/0
Tunnel Destination 192.168.102.89
Exit
Access-list 110 permit ip 192.168.101.128 0.0.0.255 192.168.100.0 0.0.0.255
access-list 110 permit ip 192.168.101.128 0.0.0.255 192.168.101.0 0.0.0.127

crypto isakmp policy 10
encryption aes 256
authentication pre-share
group 5
exit

crypto isakmp key vpnproyect7 address 192.168.102.89
crypto ipsec transform-set VPN-SET esp-aes esp-sha-hmac
crypto map VPN-MAP 10 ipsec-isakmp
description ## VPN to HQ-Network ##

set peer 192.168.102.89
set transform-set VPN-SET
match address 110
exit

int s0/1/0
crypto map VPN-MAP
exit
do wr

* //Route Summarization
Source Networks
{192.168.101.128 /27
192.168.101.160 /27
192.168.101.192 /27
192.168.101.224 /27
192.168.102.0 /27
192.168.102.32 /27
} Summarized as 192.168.101.128 /24 -> First 24 bits of those ip networks match.

Destination Networks
{192.168.100.0/26
192.168.100.64/26
192.168.100.128/26
192.168.100.192/26
} Summarized as 192.168.100.0 /24 -> First 24 bits of those ip networks match.

{192.168.101.0 /26
192.168.101.64 /26
} Summarized as 192.168.101.0 /25 -> First 25 bits of those ip networks match.

## ISP-1 ROUTER ##

En
Conf t
Hostname ISP-1

Int se0/0/0
Clock rate 64000
Ip address 195.136.17.2 255.255.255.252
Exit

Int se0/0/1
Clock rate 64000
Ip address 195.136.17.10 255.255.255.252
Exit
Do wr

//OSPF

Router ospf 10
Auto-cost reference-bandwidth 100000
Network 195.136.17.0 0.0.0.3 area 0
Network 195.136.17.8 0.0.0.3 area 0
Exit
Do wr

## ISP-2 ROUTER ## 

En
Conf t
Hostname ISP-2

Int se0/0/0
Clock rate 64000
Ip address 195.136.17.14 255.255.255.252
Exit
Int se0/0/1
Clock rate 64000
Ip address 195.136.17.6 255.255.255.252
Exit

// OSPF

Router ospf 10
Auto-cost reference-bandwidth 100000
Network 195.136.17.4 0.0.0.3 area 0
Network 195.136.17.12 0.0.0.3 area 0
Exit
Do wr

### L3-Switches ###

## ALL L3-Switches ##

En
Conf t
Enable password cisco
No ip domain lookup
Banner motd #Unauthorized access !!!#
Line console 0
Password cisco
Login
Exit
Service password-encryption
Ip domain name cisco.net
Username admin password cisco
Crypto key generate rsa
1024
Line vty 0 15
Login local
Transport input ssh
Ip ssh version 2

Do wr
Exit

## Both HQ-Multilayer-1&2 ##

Vlan 10
Name MLOCS
Vlan 20
Name MER
Vlan 30
Name MRM
Vlan 40
Name IT
Vlan 50
Name CS
Vlan 60
Name GWA-1
Vlan 999
Name native

Int ran g1/0/2-7
No shut
Switchport mode trunk
Switchport trunk native vlan 999
Exit 

// Inter-Vlan routing 
// Helper-address -> DHCP Server´s IP

Int vlan 10
Ip address 192.168.100.1 255.255.255.192
Ip helper-address 192.168.102.67
Exit
Int vlan 20
Ip address 192.168.100.65 255.255.255.192
Ip helper-address 192.168.102.67
Exit
Int vlan 30
Ip address 192.168.100.129 255.255.255.192
Ip helper-address 192.168.102.67
Exit
Int vlan 40
Ip address 192.168.100.193 255.255.255.192
Ip helper-address 192.168.102.67
Exit
Int vlan 50
Ip address 192.168.101.1 255.255.255.192
Ip helper-address 192.168.102.67
Exit
Int vlan 60
Ip address 192.168.101.65 255.255.255.192
Ip helper-address 192.168.102.67
Exit
Do wr


## HQ-Multilayer-1 ##
En
Conf t
Hostname HQ-Multilayer-1

//L3 Port
Int g1/0/1
No switchport
Ip address 192.168.102.81 255.255.255.252
Exit


// Default static route
// If the packet doesn´t belong to the HQ-Network
// it will be forwarded to the next hop (HQ-Router if 192.168.102.82)

Ip route 0.0.0.0 0.0.0.0 192.168.102.82
Do wr

//OSPF

Ip routing
Router ospf 10
Auto-cost reference-bandwidth 100000
Network 192.168.100.0 0.0.0.63 area 0
Network 192.168.100.64 0.0.0.63 area 0
Network 192.168.100.128 0.0.0.63 area 0
Network 192.168.100.192 0.0.0.63 area 0
Network 192.168.101.0 0.0.0.63 area 0
Network 192.168.101.64 0.0.0.63 area 0
Network 192.168.102.80 0.0.0.3 area 0
Exit

## HQ-Multilayer-2 ##

En
Conf t
Hostname HQ-Multilayer-2

//L3 Ports

Int g1/0/1
No switchport
Ip address 192.168.102.85 255.255.255.252
Exit

// Default static route
// If the packet doesn´t belong to the HQ-Network
// it will be forwarded to the next hop (HQ-Router if 192.168.102.86)

Ip route 0.0.0.0 0.0.0.0 192.168.102.86
Do wr

//OSPF

Ip routing
Router ospf 10
Auto-cost reference-bandwidth 100000
Network 192.168.100.0 0.0.0.63 area 0
Network 192.168.100.64 0.0.0.63 area 0
Network 192.168.100.128 0.0.0.63 area 0
Network 192.168.100.192 0.0.0.63 area 0
Network 192.168.101.0 0.0.0.63 area 0
Network 192.168.101.64 0.0.0.63 area 0
Network 192.168.102.84 0.0.0.3 area 0
Exit

## Both Branch-Multilayer-1&2 ## 

Vlan 80
Name NSO
Vlan 90
Name HL
Vlan 100
Name HR
Vlan 110
Name MK
Vlan 120
Name FIN
Vlan 130
Name GWA-2
Vlan 999
Name native

Int ran g1/0/2-7
No shut
Switchport mode trunk
Switchport trunk native vlan 999
Exit

// Inter-Vlan routing 
// Helper-address -> DHCP Server´s IP

Int vlan 80
Ip address 192.168.101.129 255.255.255.224
Ip helper-address 192.168.102.67
Exit
Int vlan 90
Ip address 192.168.101.161 255.255.255.224
Ip helper-address 192.168.102.67
Exit
Int vlan 100
Ip address 192.168.101.193 255.255.255.224
Ip helper-address 192.168.102.67
Exit
Int vlan 110
Ip address 192.168.101.225 255.255.255.224
Ip helper-address 192.168.102.67
Exit
Int vlan 120
Ip address 192.168.102.1 255.255.255.224
Ip helper-address 192.168.102.67
Exit
Int vlan 130
Ip address 192.168.102.33 255.255.255.224
Ip helper-address 192.168.102.67
Exit
Do wr

## Branch-Multilayer-1 ##

En
Conf t
Hostname Branch-Multilayer-1

//L3 Ports
Int g1/0/1
No switchport
Ip address 192.168.102.93 255.255.255.252
Exit

// Default static route
// If the packet doesn´t belong to the Branch-Network
// it will be forwarded to the next hop (Branch-Router if 192.168.102.94)

Ip route 0.0.0.0 0.0.0.0 192.168.102.94
Do wr

//OSPF

Ip routing
Router ospf 10
Auto-cost reference-bandwidth 100000
Network 192.168.101.128 0.0.0.31 area 0
Network 192.168.101.160 0.0.0.31 area 0
Network 192.168.101.192 0.0.0.31 area 0
Network 192.168.101.224 0.0.0.31 area 0
Network 192.168.102.0 0.0.0.31 area 0
Network 192.168.102.32 0.0.0.31 area 0
Network 192.168.102.92 0.0.0.3 area 0
Exit

## Branch-Multilayer-2 ##
En
Conf t
Hostname Branch-Multilayer-2

//L3 Ports
Int g1/0/1
No switchport
Ip address 192.168.102.97 255.255.255.252
Exit

// Default static route
// If the packet doesn´t belong to the Branch-Network
// it will be forwarded to the next hop (Branch-Router if 192.168.102.98)

Ip route 0.0.0.0 0.0.0.0 192.168.102.98
Do wr

// OSPF

Ip routing
Router ospf 10
Auto-cost reference-bandwidth 100000
Network 192.168.101.128 0.0.0.31 area 0
Network 192.168.101.160 0.0.0.31 area 0
Network 192.168.101.192 0.0.0.31 area 0
Network 192.168.101.224 0.0.0.31 area 0
Network 192.168.102.0 0.0.0.31 area 0
Network 192.168.102.32 0.0.0.31 area 0
Network 192.168.102.96 0.0.0.3 area 0
Exit
Do wr

### L2 Switches ###

## All L2 Switches ##

En
Conf t
Enable password cisco
No ip domain lookup
Banner motd #Unauthorized access !!!#
Line console 0
Password cisco
Login
Exit
Service password-encryption
Ip domain name cisco.net
Username admin password cisco
Crypto key generate rsa
1024
Line vty 0 15
Login local
Transport input ssh
Ip Ssh version 2
Do wr

## MLOCS-SW ##
En
Conf t
Hostname MLOCS-SW

Vlan 10
Name MLOCS
Vlan 999
Name native

int ran gi0/1-2
switchport mode trunk
switchport trunk native vlan 999
exit

int ran fa0/1-24
switchport mode access
switchport access vlan 10
exit
do wr

## MER-SW ##
En
Conf t
Hostname MER-SW

Vlan 20
Name MER
Vlan 999
Name native

int ran gi0/1-2
switchport mode trunk
switchport trunk native vlan 999
exit

int ran fa0/1-24
switchport mode access
switchport access vlan 20
exit
do wr

## MRM-SW ##
En
Conf t
Hostname MRM-SW

Vlan 30
Name MRM
Vlan 999
Name native

int ran gi0/1-2
switchport mode trunk
switchport trunk native vlan 999
exit

int ran fa0/1-24
switchport mode access
switchport access vlan 30
exit
do wr

## IT-SW ##
En
Conf t
Hostname IT-SW

Vlan 40
Name IT
Vlan 999
Name native

int ran gi0/1-2
switchport mode trunk
switchport trunk native vlan 999
exit

int ran fa0/1-24
switchport mode access
switchport access vlan 40
exit
do wr

## CS-SW ##

En
Conf t
Hostname CS-SW

Vlan 50
Name CS
Vlan 999
Name native

int ran gi0/1-2
switchport mode trunk
switchport trunk native vlan 999
exit

int ran fa0/1-24
switchport mode access
switchport access vlan 50
exit
do wr

## GWA-SW-1 ##
En
Conf t
Hostname GWA-SW-1

Vlan 60
Name GWA-1
Vlan 999
Name native

int ran gi0/1-2
switchport mode trunk
switchport trunk native vlan 999
exit

int ran fa0/1-24
switchport mode access
switchport access vlan 60
exit
do wr

## SSS-SW ##
En
Conf t
Hostname SSS-SW

Vlan 70
Name SSS
Vlan 999
Name native

int gi0/1
switchport mode trunk
switchport trunk native vlan 999
exit

int ran fa0/1-24
switchport mode access
switchport access vlan 70
exit

// Port Security config
// Only one device can access
// Apply to all free ports – Restrict means drop packets

Int ran fa0/5-24
Switchport port-security maximum 1
Switchport port-security mac-address sticky
Switchport port-security violation restrict
exit
Do wr


## NSO-SW ##
En
Conf t
Hostname NSO-SW

Vlan 80
Name NSO
Vlan 999
Name native

int ran gi0/1-2
switchport mode trunk
switchport trunk native vlan 999
exit

int ran fa0/1-24
switchport mode access
switchport access vlan 80
exit

## HL-SW ##
En
Conf t
Hostname HL-SW

Vlan 90
Name HL
Vlan 999
Name native

int ran gi0/1-2
switchport mode trunk
switchport trunk native vlan 999
exit

int ran fa0/1-24
switchport mode access
switchport access vlan 90
exit

## HR-SW ##
En
Conf t
Hostname HR-SW

Vlan 100
Name NSO
Vlan 999
Name native

int ran gi0/1-2
switchport mode trunk
switchport trunk native vlan 999
exit

int ran fa0/1-24
switchport mode access
switchport access vlan 100
exit

## MK-SW ##

En
Conf t
Hostname MK-SW

Vlan 110
Name MK
Vlan 999
Name native

int ran gi0/1-2
switchport mode trunk
switchport trunk native vlan 999
exit

int ran fa0/1-24
switchport mode access
switchport access vlan 110
exit

## FIN-SW ##
En
Conf t
Hostname FIN-SW

Vlan 120
Name FIN
Vlan 999
Name native

int ran gi0/1-2
switchport mode trunk
switchport trunk native vlan 999
exit

int ran fa0/1-24
switchport mode access
switchport access vlan 120
exit

## GWA-SW-2 ##
En
Conf t
Hostname GWA-SW-2

Vlan 130
Name GWA-2
Vlan 999
Name native

int ran gi0/1-2
switchport mode trunk
switchport trunk native vlan 999
exit

int ran fa0/1-24
switchport mode access
switchport access vlan 130
exit

