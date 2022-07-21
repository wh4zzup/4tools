#!/bin/sh
#
###################################################################################################################
#
# Idea / Written by Sebastian Vivian Gresser
#
###################################################################################################################
# a wrapper for the ip command to prevent command injections origined from the vpn server.
# If you want to use this as wrapper for super user execution you have to remove
# sudo or configure your sudo.conf to allow all commands for root/super user invoked by sudo.
#
# Add the following line to your openvpn config if you plan to use this script with your OpenVPN client.
# openvpn_config.ovpn:
# iproute *absolute location of this script* (do not use *)
#
###################################################################################################################
#
# INFOS
#
# SECURITY:
#
# e.g.
#diff --git a/ip/ip.c b/ip/ip.c
#index 82282bab..bcd873d8 100644
#--- a/ip/ip.c
#+++ b/ip/ip.c
#@@ -90,11 +90,11 @@ static const struct cmd {
#        const char *cmd;
#        int (*func)(int argc, char **argv);
# } cmds[] = {
#-       { "address",    do_ipaddr },
#+       /*{ "address",  do_ipaddr },
#        { "addrlabel",  do_ipaddrlabel },
#-       { "maddress",   do_multiaddr },
#+       { "maddress",   do_multiaddr },*/
#        { "route",      do_iproute },
#-       { "rule",       do_iprule },
#+       /*{ "rule",     do_iprule },
#        { "neighbor",   do_ipneigh },
#        { "neighbour",  do_ipneigh },
#        { "ntable",     do_ipntable },
#@@ -121,9 +121,9 @@ static const struct cmd {
#        { "sr",         do_seg6 },
#        { "nexthop",    do_ipnh },
#        { "mptcp",      do_mptcp },
#-       { "ioam",       do_ioam6 },
#+       { "ioam",       do_ioam6 },*/
#        { "help",       do_help },
#-       { "stats",      do_ipstats },
#+       /*{ "stats",    do_ipstats },*/
#        { 0 }
# };
#
# For unprivileged use you should take a look in the tools folder.
# HOWTO building your own ip binary:
#
#   git clone git://git.kernel.org/pub/scm/network/iproute2/iproute2.git
#   cd iproute2
#   ./configure
#   patch -p1 < ip_route_2_hardcoded_wrapper_hack.patch (located @ tools/3rdparty_patches/)
#   (you should check your Makefile and modify the hardening flags if needed)
#   make
#
#   secure your original ip binary and copy your own build ip binary in place (/bin/ip)
#   or better use a new name for it like (/bin/ip_min rename your original /bin/ip to
#   /bin/ip.bak by using mv and link your new one with ln -s /bin/ip_min /bin/ip)
#
#   Do not forget to set your paxflags with:
#   paxctl-ng -PeMRS /bin/ip or /bin/ip_min
#
#   add following line to your openvpn config
#   file:
#   iproute (replace with the absolute location of your new binary)
#
#   in vpnencap.conf:
#   ip_command="(replace with the absolute location of your new binary)"
#
# The command wrapper script can be used as an alternative solution to prevent simple
# command injections attempts if you do not like the hardcoded_wrapper_hack solution.
#
# The wrapper will be needed for the following tutorial... using the hack above prevents
# cmd injections via nsnet exec.                  ||
#                                                 \/
# https://community.openvpn.net/openvpn/wiki/UnprivilegedUser
#
# If you want to enable the unprivileged_user functionality you need to pre-init tun devices properly
# according to your tun_start setting. This can be done with tools/init_tuns.sh executed as super user.
# Reconsider to check if your user is set properly in your sudoers config to execute the ip_command as
# super user without a password or patch the script to pipe the correct password automatically.
# According to the first case you should cut the functionality of ip route definitively to
# the minimum like it is done with the 3rd party patch.
#
###################################################################################################################
#
# If you are using this with the 4routing script you can comment out the link and addr if clauses
# to just make the route subcommand accessible. This will prevent at least any command injection.

if [ ! "$( echo $1 | grep route )" = "" ]
then
  sudo /usr/local/bin/ip $*
elif [ ! "$( echo $1 | grep link )" = "" ]
then
  sudo /usr/local/bin/ip $*
elif [ ! "$( echo $1 | grep addr )" = "" ]
then
  sudo /usr/local/bin/ip $*
fi

#the most common location is /bin/ip if you do not user your own patched version
#sudo /bin/ip $*
#sudo /usr/local/bin/ip $*
