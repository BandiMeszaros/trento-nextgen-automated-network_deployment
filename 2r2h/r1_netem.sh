sudo tc qdisc replace dev eth1 root netem delay 750ms rate 30Mbit
sudo tc qdisc replace dev eth2 root netem delay 0ms rate 300Mbit
