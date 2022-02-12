sudo echo "auto eth1
iface eth1 inet static
address 192.168.3.22
netmask 255.255.255.0
network 192.168.3.0
broadcast 192.168.3.255
post-up route add -net 192.168.0.0 netmask 255.255.0.0 gw 192.168.3.1 dev eth1
pre-down route del -net 192.168.0.0 netmask 255.255.0.0 gw 192.168.3.1 dev eth1
" >> /etc/network/interfaces
sudo reboot