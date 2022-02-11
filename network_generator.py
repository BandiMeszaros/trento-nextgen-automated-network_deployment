import os
import pickle
import copy

class Link:
    def __str__(self):
        return self.name

    def __init__(self, name, net, delay, bw):
        self.name = name
        self.netmask = "255.255.255.0"
        self.network = f"192.168.{net}.0"
        self.bc = f"192.168.{net}.255"
        # delay in ms
        self.delay = delay
        # bandwidth in Mbits
        self.bandwidth = bw

    def set_delay(self, delay_value):
        self.delay = delay_value

    def set_bw(self, bw_value):
        self.bandwidth = bw_value

class Host:
    def __str__(self):
        return self.hostname

    def __init__(self, hostname, link):
        self.hostname = hostname
        # link has to exist before creating host
        self.link = link
        self.ip = self.generate_ip()

    def generate_ip(self):

        return self.link.network.rstrip('.0') + '.22'

    def generate_bootstrap_file(self, path):
        """generates the bootstrap.sh for the host machine"""

        file_root = os.path.join(path, f"{self.hostname}.sh")

        if not os.path.exists(path):
            os.makedirs(path)

        router = self.link.network.rstrip(".0") +".1"
        file_content = f'sudo echo "auto eth1\n' \
                       f'iface eth1 inet static\n' \
                       f'address {self.ip}\n' \
                       f'netmask {self.link.netmask}\n' \
                       f'network {self.link.network}\n' \
                       f'broadcast {self.link.bc}\n' \
                       f'post-up route add -net 192.168.0.0 netmask 255.255.0.0 gw {router} dev eth1\n' \
                       f'pre-down route del -net 192.168.0.0 netmask 255.255.0.0 gw {router} dev eth1\n"' \
                       f' >> /etc/network/interfaces\n' \
                       f'sudo reboot' \

        with open(file_root, "w") as f:
            f.write(file_content)

    def add_host_to_vagrant(self):
        """this function adds the host to the vagrantfile"""
        return_string = f'  config.vm.define "{self.hostname}" do |{self.hostname}|\n    ' \
                        f'{self.hostname}.vm.box = "ubuntu/trusty64"\n    ' \
                        f'{self.hostname}.vm.hostname = "{self.hostname}"\n    ' \
                        f'{self.hostname}.vm.network "private_network", virtualbox__intnet: "{self.link}", ' \
                        f'ip: "{self.ip}"' \
                        f', auto_config: false\n    ' \
                        f'{self.hostname}.vm.provision "shell", path: "{self.hostname}.sh"\n    ' \
                        f'{self.hostname}.vm.provider "virtualbox" do |vb|\n      ' \
                        f'vb.memory = 256\n    ' \
                        f'end\n  ' \
                        f'end'
        return return_string


class Router:
    def __str__(self):
        return_string = f"Router Name: {self.router_name}\n" \
                        f"Number of links: {self.link_no}\n" \
                        f"Links by Name:\n"

        for L in self.link_conns:
            new_line = "> " + L + "\n"
            return_string += new_line

        return_string = return_string + f"Number of Hosts: {self.host_no}\n" \
                                        f"Hosts by Name, Host.name and links to them:\n"

        for h, v in self.connected_hosts.items():
            new_line = f"> {h}: {v[0]}, {v[1]}\n"
            return_string += new_line

        return_string = return_string + f"Number of router connections: {len(self.connected_routers)}\n" \
                                        f"Routers by name, links: \n"

        for r, v in self.connected_routers.items():
            new_line = f"> {r}: {v}\n"
            return_string += new_line

        return return_string

    def __init__(self, name):
        self.router_name = name
        self.host_no = 0
        self.connected_hosts = {}
        self.link_conns = []
        self.link_no = 0
        self.interfaces = {}  # "interface_name" : (Link,IP)
        self.interface_no = 0
        self.connected_routers = {}

    def add_router_to_vagrant(self):
        """generates the string that will be included in the vagrantfile"""
        return_string = f'  config.vm.define "{self.router_name}" do |{self.router_name}|\n    ' \
                        f'{self.router_name}.vm.box = "ubuntu/trusty64"\n    ' \
                        f'{self.router_name}.vm.hostname = "{self.router_name}"\n    '
        for interface, li in self.interfaces.items():
            L = li[0].name
            new_line = f'{self.router_name}.vm.network "private_network", virtualbox__intnet: "{L}", ip: "{li[1]}"' \
                       f', auto_config: false\n    '
            return_string += new_line

        return_string += f'{self.router_name}.vm.provision "shell", path: "{self.router_name}.sh"\n    ' \
                         f'{self.router_name}.vm.provider "virtualbox" do |vb|\n      ' \
                         f'vb.memory = 256\n    ' \
                         f'end\n  ' \
                         f'end'

        return return_string

    def generate_bootstrap_file(self, path):
        """generates bootstrap.sh file """
        file_root = os.path.join(path, f"{self.router_name}.sh")

        if not os.path.exists(path):
            os.makedirs(path)


        file_content = 'sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf\n\n'
        for interface, link in self.interfaces.items():
            file_content += f'sudo echo "auto {interface}\n' \
                           f'iface {interface} inet static\n' \
                           f'address {link[1]}\n' \
                           f'netmask {link[0].netmask}\n' \
                           f'network {link[0].network}\n' \
                           f'broadcast {link[0].bc}\n' \
                            f'" >> /etc/network/interfaces\n'


        file_content += '\n'
        file_content += f"sudo reboot\n"

        for interface, link in self.interfaces.items():
            file_content += f'sudo tc qdisc replace dev {interface} root netem delay {link[0].delay}ms rate ' \
                            f'{link[0].bandwidth}Mbit\n'
        with open(file_root, "w") as f:
            f.write(file_content)


    def define_link(self, link_name, other_router):
        """if link_name is an existing link, defines connection"""

        if link_name in self.link_conns:
            self.connected_routers[other_router] = link_name

    def add_link(self, link_name, net, delay=0, bw=40):
        """Adds a link to the router"""
        self.link_no += 1
        self.link_conns.append(link_name)
        link_obj = Link(link_name, net, delay, bw)
        link_ip_router = f"192.168.{net}.1"
        self.interface_no += 1
        self.interfaces[f"eth{self.interface_no}"] = (link_obj, link_ip_router)

    def add_new_host(self, link_name, host_name):
        """Adds new host to the router, link has to be added before"""

        if link_name in self.link_conns:
            for interface, link in self.interfaces.items():
                if link[0].name == link_name:
                    new_host = Host(host_name, link[0])
                    self.host_no += 1
                    self.connected_hosts[host_name] = (new_host, link_name)
                    break

    def list_hosts(self):
        """returns a list of the connected hosts"""
        all_hosts = list(map(lambda x: x[0].hostname, self.connected_hosts.values()))
        return all_hosts

    def host(self, hostname):
        """returns the host if it is connected"""
        for hn, v in self.connected_hosts.items():
            if hn == hostname:
                return v[0]

        return f"No host called: {hostname}"

    def delete_host(self, hostname):
        """removes host from the router"""

        if hostname in self.connected_hosts.keys():
            host, link = self.connected_hosts[hostname]
            self.link_conns.remove(link)
            del self.connected_hosts[hostname]
            self.host_no -= 1
            self.link_no -= 1
            to_be_deleted = []

            for interface, li in self.interfaces.items():
                if li[0].name == link:
                    to_be_deleted.append(interface)

            for i in to_be_deleted:
                del self.interfaces[i]

            self.interface_no -= 1

            print(f"{hostname} has been removed from router {self.router_name}")
        else:
            print(f"No such host: {hostname}")

    def delete_router_link(self, linkname):
        """removes link from the router"""

        if linkname in self.link_conns:
            self.link_conns.remove(linkname)
            for name, k in self.connected_routers.items():
                if k == linkname:
                    del self.connected_routers[name]
                    print(f"{linkname} link has been removed")
                    self.link_no -= 1
                    break

            to_be_deleted = []
            for interface, li in self.interfaces.items():
                if li[0].name == linkname:
                    to_be_deleted.append(interface)

            for i in to_be_deleted:
                del self.interfaces[i]

            self.interface_no -= 1
class Network:
    """creates a network"""

    def __init__(self, name=""):
        self.name = name
        self.routers = []
        self.network_generator = NetworkGenerator()
        self.nets = 0

    def add_link_to_router(self, router_name, link_name, delay=0, bw=40):
        """adds a link to the router"""
        r = self.router(router_name)
        self.nets += 1
        net = self.nets
        r.add_link(link_name, net, delay, bw)
        print(f"Link called {link_name} has been added to the {router_name}...")

    def compose_vagrantfile(self, path):
        """generates a vagrantfile"""

        for router in self.routers:
            self.network_generator.add_line(router.add_router_to_vagrant())
            router.generate_bootstrap_file(path)

            for hn, v in router.connected_hosts.items():
                self.network_generator.add_line(v[0].add_host_to_vagrant())
                v[0].generate_bootstrap_file(path)

        self.network_generator.add_line("end")

        self.network_generator.save_to_file(path)

    def link_two_router(self, link_name, to_router_name, from_router_name):
        """links two router, just a wrapper"""

        # adding link to the to_router
        delay = 0
        bw = 40
        to_router = self.router(to_router_name)
        for interface, li in to_router.interfaces.items():
            if link_name == li[0].name:
                delay = li[0].delay
                bw = li[0].bandwith
                break
        self.nets += 1
        self.router(to_router_name).add_link(link_name, self.nets, delay, bw)

        # defining the link between the two routers
        self.router(to_router_name).define_link(link_name, from_router_name)
        self.router(from_router_name).define_link(link_name, to_router_name)

    def unlink_two_router(self, link_name, router_name1, router_name2):
        """deletes connections between two routers"""

        router1 = self.router(router_name1)
        router2 = self.router(router_name2)

        router1.delete_router_link(link_name)
        router2.delete_router_link(link_name)

    def router(self, router_name):
        """
        returns a router object
        :param router_name: the router_name
        :return: router object
        """
        for r in self.routers:
            if r.router_name == router_name:
                return r

        return f"No router called: {router_name}"

    def list_routers(self):
        """
        Lists all the routers on the network
        """
        all_routers = list(map(lambda x: x.router_name, self.routers))
        return all_routers

    def add_router(self, router_name):

        new_router = Router(router_name)
        self.routers.append(new_router)
        print(f"{router_name} has been added to the network...")

    def print_network(self):

        if (num := len(self.routers)) == 0:
            print("Empty network...")
        else:
            print(f"This is the network called: {self.name}")
            print(f"There is {num} router(s) in the network")
            print("Router(s) by name")
            list(map(lambda x: print(x), self.routers))

    def save_network(self, file_root="./network/pickles", file_name=""):
        """saves the created network to a pickle file"""

        if file_name == "" or file_name is None:
            file_name = f"{self.name}_network.pickle"
        if not os.path.isdir(file_root):
            os.makedirs(file_root)

        file_address = os.path.join(file_root, file_name)

        with open(file_address, "wb") as file:
            pickle.dump(self, file)

    def load_network(self, file_name, file_root="./network/pickles"):

        file_address = os.path.join(file_root, file_name)

        with open(file_address, "rb") as file:
            loaded_network = pickle.load(file)

        print("Network successfully loaded...")
        self.name = copy.deepcopy(loaded_network.name)
        self.routers = copy.deepcopy(loaded_network.routers)
        self.network_generator = copy.deepcopy(loaded_network.network_generator)

        print("The loaded network looks like this:")
        self.print_network()

    def add_host_to_router(self, router_name, host_name, link_name):
        """adds a host to the selected router, the user needs to define the link name"""
        self.router(router_name).add_new_host(link_name, host_name)
        print("added host to router...")


class NetworkGenerator:

    def __init__(self):
        self.vagrant_file = ''
        self.open_template()

    def open_template(self):
        with open("./template/Vagrant_template.rb", "r") as f:
            self.vagrant_file = f.read()

    def add_line(self, new_line):
        self.vagrant_file = self.vagrant_file + new_line + "\n"

    def save_to_file(self, path="./network"):
        """Saves the content of vagrant_file to a Vagrantfile"""

        filename = "Vagrantfile"
        if not os.path.exists(path):
            os.makedirs(path)

        file_root = os.path.join(path, filename)

        if os.path.isfile(file_root):
            os.remove(file_root)

        with open(file_root, "w") as f:
            f.write(self.vagrant_file)


if __name__ == '__main__':

    n = Network("test")
    n.add_router("r1")
    n.print_network()
    n.add_link_to_router("r1", "netA", 100, 20)
    n.add_host_to_router("r1", "host1", "netA")
    n.add_link_to_router("r1", "netB", 0, 30)
    n.add_host_to_router("r1", "host1", "netB")
    n.add_router("r2")
    n.add_link_to_router("r2", "routernetA")
    n.add_host_to_router("r2", "hostr21", "routernetA")
    n.add_link_to_router("r2", "connectRouters")
    n.link_two_router("connectRouters", "r1", "r2")
    n.compose_vagrantfile("/testfoldaer")
