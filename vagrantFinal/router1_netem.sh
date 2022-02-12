sudo tc qdisc replace dev eth1 root netem delay 0ms rate 40Mbit
sudo tc qdisc replace dev eth2 root netem delay 1300ms rate 10Mbit
