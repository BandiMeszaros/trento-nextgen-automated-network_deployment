sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf

sudo echo "auto eth1
iface eth1 inet static
address 192.168.1.1
netmask 255.255.255.0
network 192.168.1.0
broadcast 192.168.1.255
" >> /etc/network/interfaces
sudo echo "auto eth2
iface eth2 inet static
address 192.168.2.1
netmask 255.255.255.0
network 192.168.2.0
broadcast 192.168.2.255
" >> /etc/network/interfaces

sudo reboot
