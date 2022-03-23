#!/usr/bin/env bash
# if you decide to run it on BSD

# modified version of https://github.com/cryptolok/GhostInTheNet
# but can still be imrpoved

# cyan cyberpunk style
echo -e "\033[01;36m"
echo '
                                                 ^
                                                / \
  _____ _    _  ____   _____ _______           /   \         _   _ ______ _______
 / ____| |  | |/ __ \ / ____|__   __|         /     \       | \ | |  ____|__   __|
| |  __| |__| | |  | | (___    | |           /       \      |  \| | |__     | |
| | |_ |  __  | |  | |\___ \   | |          /   in    \     | . ` |  __|    | |
| |__| | |  | | |__| |____) |  | |         /           \    | |\  | |____   | |
 \_____|_|  |_|\____/|_____/   |_|        /     the     \   |_| \_|______|  |_|
                                         /               \
                                        /_________________\
'
echo -e "\e[0m"

# check for root access
#[ "${UID}" -eq 0 ] || { echo -e "sudo !!\n" ; exit 1; }
if [[ $UID -ne 0 ]]
then
    echo 'sudo !!'
    echo
    exit 1
fi
# use 0 to deactivate network manager and/or dhclient
# usage of the network manager results in exposing your client
# because it will use dhclient with a default configuration
use_nm=0
# USAGE OF DHCLIENT WILL EXPOSE YOU
use_dhc=0
# NETWORK if use_dhc=0 - you have to discover this yourself!
client_network="192.168.20.0/24"
# CLIENT IP use_dhc=0 - you have to discover this yourself!
client_ip="192.168.20.123"


# just type it and it will execute the last command as root
# arguments/variables assignments
#SWITCH=$(echo $1 | tr '[:upper:]' '[:lower:]')
SWITCH=${1,,*}
INTERFACE=$2
TMPMAC=/tmp/mac.ghost
# here we are going to store the original MAC address
ORGMAC=""

# network stealther
#[ $# -gt 1 ] || { echo 'Usage: GhostInTheNet on|off $INTERFACE'; exit 2; }
if [[ "$INTERFACE" = "" ]]
then
    echo 'Usage: GhostInTheNet on|off $INTERFACE'
    echo
    exit 2
fi

# let's use ifconfig by default
CMD=$( which ifconfig 2>/dev/null)
if [[ $? -gt 0 ]]; then
    # or ip if not present
    CMD=$( which ip )
fi

echo $CMD

#case $SWITCH in on)
if [[ "$SWITCH" = "on" ]]
then

    # storing original MAC
    if [ ! $(which ethtool) ] && [ ! -f /etc/udev/rules.d/70-persistent-net.rules ]
    then
        if [[ $CMD =~ .*ifconfig ]]; then
            ORGMAC=$( $CMD $INTERFACE | grep ether | awk '{print $2}' )
        else
            ORGMAC=$( $CMD link show $INTERFACE | awk '$1~/^link/{print $2}' )
        fi
    else
        if [[ $(which ethtool) ]]
        then
            ORGMAC=$(ethtool -P $INTERFACE)
            ORGMAC=${ORGMAC#*:}
        else
            ORGMAC=$(cat /etc/udev/rules.d/70-persistent-net.rules | grep $INTERFACE | cut -d '"' -f 8)
        fi
    fi

    echo "Saving original MAC address for $INTERFACE"
    echo -n $ORGMAC > $TMPMAC
    echo 'Spoofing MAC address ...'
    echo
#	ifdown $INTERFACE &> /dev/null

    nmcli con down $INTERFACE
    /etc/init.d/network-manager stop

    if [[ $CMD =~ .*ifconfig ]]; then
        $CMD $INTERFACE down
    else
        $CMD link set $INTERFACE down
    fi
#[[ $? -eq 0 ]] || { echo -e 'Wrong INTERFACE? Try eth0 or wlan0 or execute `ip a`' ; exit 3; }
    if [[ $? -ne 0 ]]
    then
        echo 'Wrong INTERFACE? Try eth0 or wlan0 or execute `ip a`'
        echo
        exit 3
    fi
#	MAC=$(echo $RANDOM|md5sum|sed 's/^\(..\)\(..\)\(..\)\(..\)\(..\).*$/64:\1:\2:\3:\4:\5/')
    MAC="480fcf"$(head -c 6 /proc/sys/kernel/random/uuid)
# random HP vendor MAC, to avoid reserved addresses (unicast, etc) and MAC blacklisting due to lack of randomness
#TODO add vendors choice (dell,hp,intel,vmware,cisco,belkin...) ?
    if [[ $CMD =~ .*ifconfig ]]; then
        $CMD $INTERFACE hw ether $MAC
    else
        $CMD link set dev $INTERFACE address $MAC
    fi

#	ip link set $INTERFACE address $MAC > /dev/null
    echo "New MAC addresse : $MAC"
    echo
    echo 'Configuring kernel to restrict ARP/NDP requests in linking network mode ...'
    echo
    sysctl net.ipv4.conf.$INTERFACE.arp_ignore=1 2> /dev/null
# ignore ARP broadcasts
    sysctl net.ipv4.conf.$INTERFACE.arp_announce=0 2> /dev/null
# deactivate ARP
    sysctl net.ipv4.conf.$INTERFACE.proxy_arp=0 2> /dev/null
    sysctl net.ipv4.conf.$INTERFACE.proxy_arp_pvlan=0 2> /dev/null
    sysctl net.ipv4.conf.$INTERFACE.arp_accept=0 2> /dev/null
# deactivate BOOTP RELAY
    sysctl net.ipv4.conf.$INTERFACE.bootp_relay=0 2> /dev/null
# ignore invalid ICMP
    echo 1 > /proc/sys/net/ipv4/icmp_ignore_bogus_error_responses 2> /dev/null
# ignore ICMP broadcasts
    echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_broadcasts 2> /dev/null
# ignore ICMP v4
    iptables -I INPUT -i $INTERFACE -p icmp -j DROP
# restrict ARP announces to unicast
    ip6tables -I INPUT -i $INTERFACE --protocol icmpv6 --icmpv6-type echo-request -j DROP
# ignore ICMPv6 echo requests type 128 code 0
    ip6tables -I INPUT -i $INTERFACE --protocol icmpv6 --icmpv6-type neighbor-solicit -j DROP
# ignore ICMPv6/NDP neighbor solicitation requests type 135 code 0
# IPv6 scanning isn't too much realistic though
    hostname $RANDOM
    echo 'New hostname : '$(hostname)
    echo 'Reinitializing network interface ...'
    echo 'If not connected or taking too long - reconnect manually'
    echo
#	ifup $INTERFACE &> /dev/null
#	nmcli radio wifi off
#	rfkill unblock wlan
    if [[ $CMD =~ .*ifconfig ]]; then
        $CMD $INTERFACE up
    else
        $CMD link set $INTERFACE up
    fi
    if [ $use_nm = 1 ]; then
        /etc/init.d/network-manager start
        nmcli con up $INTERFACE
        sleep 5
    fi
    # use_dhc=1 WILL EXPOSE YOUR CLIENT TO THE ROUTER
    if [ $use_dhc = 1 ]; then
        dhclient $INTERFACE &> /dev/null
    else
        ifconfig $INTERFACE $client_ip
        ip route add $client_network dev $INTERFACE proto kernel scope link src $client_ip
    fi
    fi

#TODO use already achived IP configuration to avoid broadcast ?
    echo 'Now you are a cyberspy, robotic guy'
    echo
#;;off)
elif [[ "$SWITCH" = "off" ]]
then
    # load original MAC address
    if [ ! $(which ethtool) ] && [ ! -f /etc/udev/rules.d/70-persistent-net.rules ]
    then
        ORGMAC=$( cat $TMPMAC )
    else
        if [[ $(which ethtool) ]]
        then
            ORGMAC=$(ethtool -P $INTERFACE)
            ORGMAC=${ORGMAC#*:}
        else
            ORGMAC=$(cat /etc/udev/rules.d/70-persistent-net.rules | grep $INTERFACE | cut -d '"' -f 8)
        fi
    fi
    echo 'Reinitializing MAC address ...'
    echo
#	ifdown $INTERFACE &> /dev/null

    if [ $use_nm = 1 ]; then
        /etc/init.d/network-manager stop
        nmcli con down $INTERFACE
    fi

    if [[ $CMD =~ .*ifconfig ]]; then
        $CMD $INTERFACE down
#	    rfkill unblock wlan
#	    nmcli radio wifi on
        $CMD $INTERFACE hw ether $ORGMAC
    else
        $CMD link set $INTERFACE down
#	rfkill unblock wlan
#	nmcli radio wifi on
        $CMD link set dev $INTERFACE address $ORGMAC
    fi

#	ip link set $INTERFACE address $MAC &> /dev/null
    if [[ $? -ne 0 ]]
    then
        echo 'Wrong INTERFACE? Try eth0 or wlan0 or execute `ip a`'
        echo
        exit 3
    fi
    echo 'Reconfiguring kernel to normal ARP/NDP linking network mode ...'
    echo
    sysctl net.ipv4.conf.$INTERFACE.arp_ignore=0 2> /dev/null
    sysctl net.ipv4.conf.$INTERFACE.arp_announce=0 2> /dev/null
    #for i in /proc/sys/net/ipv4/conf/*; do echo 1 > $i/proxy_arp 2> /dev/null; done
    #echo 0 > /proc/sys/net/ipv4/icmp_ignore_bogus_error_responses 2> /dev/null
    iptables -D INPUT -i $INTERFACE -p icmp -j ACCEPT
    ip6tables -D INPUT -i $INTERFACE --protocol icmpv6 --icmpv6-type echo-request -j ACCEPT
    ip6tables -D INPUT -i $INTERFACE --protocol icmpv6 --icmpv6-type neighbor-solicit -j ACCEPT
    echo 'Restoring hostname ...'
    hostname $(cat /etc/hostname)
    echo 'Reinitializing network interface ...'
    echo 'If not connected or taking too long - reconnect manually'
    echo
#	ifup $INTERFACE &> /dev/null
    if [[ $CMD =~ .*ifconfig ]]; then
        $CMD $INTERFACE up
    else
        $CMD link set $INTERFACE up
    fi
    if [ $use_nm = 1 ]; then
        /etc/init.d/network-manager start
        nmcli con up $INTERFACE
        sleep 5
    fi

    if [ $use_dhc = 1 ]; then
        dhclient $INTERFACE &> /dev/null
    fi

    rm -f $TMPMAC
    echo 'Waiting like a ghost, when you need me the most'
    echo
#;;*)
else
    echo 'Usage: GhostInTheNet on|off $INTERFACE'
    echo
    exit 4
#;;esac
fi
#exit 0
