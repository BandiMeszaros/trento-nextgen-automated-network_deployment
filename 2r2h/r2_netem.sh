sudo tc qdisc replace dev eth1 root netem delay 0ms rate 300Mbit
sudo tc qdisc replace dev eth2 root netem delay 500ms rate 30Mbit
