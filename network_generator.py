import os
import pickle
import copy
class Host:
    def __str__(self):
        return self.hostname

    def __init__(self, hostname, link):
        self.hostname = hostname
        # link has to exist before creating host
        self.link = link

    def add_host_to_vagrant(self):
        """this function adds the host to the vagrantfile"""
        return_string = f'  config.vm.define "{self.hostname}" do |{self.hostname}|\n    ' \
                        f'{self.hostname}.vm.box = "ubuntu/bionic64"\n    ' \
                        f'{self.hostname}.vm.hostname = "{self.hostname}"\n    ' \
                        f'{self.hostname}.vm.network "private_network", virtualbox__intnet: "{self.link}"' \
                        f', auto_config: false\n    ' \
                        f'{self.hostname}.vm.provision "shell", path: "host.sh"\n    ' \
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

    def __init__(self, name, hosts, links):
        self.router_name = name
        self.host_no = hosts
        self.connected_hosts = {}
        self.link_conns = []
        self.link_no = links
        self.connected_routers = {}
        if self.link_no < self.host_no:
            print("can't do it: less links than hosts")
        else:
            for i in range(0, hosts):
                hostname = self.router_name + f"host{i}"
                link_name = f"broadcast_host{i}"
                self.connected_hosts[f"host{i}"] = (Host(hostname, link_name), link_name)
                self.link_conns.append(link_name)

            if links_left := self.link_no - self.host_no:

                for link in range(0, links_left):
                    self.link_conns.append(f"broadcast_{self.router_name}_link{link}")

    def add_router_to_vagrant(self):
        """generates the string that will be included in the vagrantfile"""
        return_string = f'  config.vm.define "{self.router_name}" do |{self.router_name}|\n    ' \
                        f'{self.router_name}.vm.box = "ubuntu/bionic64"\n    ' \
                        f'{self.router_name}.vm.hostname = "{self.router_name}"\n    '
        for L in self.link_conns:
            new_line = f'{self.router_name}.vm.network "private_network", virtualbox__intnet: "{L}", ' \
                       f'auto_config: false\n    '
            return_string += new_line

        return_string += f'{self.router_name}.vm.provision "shell", path: "router.sh"\n    ' \
                         f'{self.router_name}.vm.provider "virtualbox" do |vb|\n      ' \
                         f'vb.memory = 256\n    ' \
                         f'end\n  ' \
                         f'end'

        return return_string

    def define_link(self, link_name, other_router):
        """if link_name is an existing link, defines connection"""

        if link_name in self.link_conns:
            self.connected_routers[other_router] = link_name

    def add_link(self, link_name):
        """Adds a link to the router"""
        self.link_no += 1
        self.link_conns.append(link_name)

    def list_hosts(self):
        """returns a list of the connected hosts"""
        all_hosts = list(map(lambda x: x.hostname, self.connected_hosts))
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
            print(f"{hostname} has been removed from router {self.router_name}")
        else:
            print(f"No such host: {hostname}")

    def delete_router_link(self, linkname):
        """removes link from the router"""

        if linkname in self.link_conns:
            self.link_conns.remove(linkname)
            for name, k in self.connected_routers.items():
                if k[1] == linkname:
                    del self.connected_routers[name]
                    print(f"{linkname} link has been reomeved")
                    self.link_no -= 1

class Network:
    """creates a network"""
    def __init__(self, name=""):
        self.name = name
        self.routers = []
        self.network_generator = NetworkGenerator()

    def compose_vagrantfile(self, filename="Vagrantfile", path="./network"):
        """generates a vagrantfile"""

        for router in self.routers:
            self.network_generator.add_line(router.add_router_to_vagrant())

            for hn, v in router.connected_hosts.items():
                self.network_generator.add_line(v[0].add_host_to_vagrant())

        self.network_generator.add_line("end")

        self.network_generator.save_to_file(filename, path)

    def link_two_router(self, link_name, to_router_name, from_router_name):
        """links two router, just a wrapper"""

        # adding link to the to_router
        self.router(to_router_name).add_link(link_name)

        # defining the link between the two routers
        self.router(to_router_name).define_link(link_name, from_router_name)
        self.router(from_router_name).define_link(link_name, to_router_name)

    def unlink_to_router(self, link_name, router_name1, router_name2):
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

    def add_router(self, router_name, router_links, router_hosts):
        new_router = Router(router_name, router_hosts, router_links)
        self.routers.append(new_router)
        print(f"{router_name} has been added to the network...")

    def print_network(self):

        if (num := len(self.routers)) == 0:
            print("Empty network...")
        else:
            print(f"There is {num} router(s) in the network")
            print("Router(s) by name")
            list(map(lambda x: print(x), self.routers))

    def save_network(self, file_root, file_name=""):
        """saves the created network to a pickle file"""

        if file_name == "":
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

class NetworkGenerator:

    def __init__(self):
        self.vagrant_file = ''
        self.open_template()

    def open_template(self):
        with open("./template/Vagrant_template.rb", "r") as f:
            self.vagrant_file = f.read()

    def add_line(self, new_line):
        self.vagrant_file = self.vagrant_file + new_line + "\n"

    def save_to_file(self, filename="Vagrantfile", path="./network"):
        """Saves the content of vagrant_file to a Vagrantfile"""
        if not os.path.exists(path):
            os.makedirs(path)

        file_root = os.path.join(path, filename)

        with open(file_root, "w") as f:
            f.write(self.vagrant_file)


if __name__ == '__main__':
    N = Network()
    N.add_router("testrouter0", 3, 2)
    N.add_router("testrouter1", 2, 2)
    N.link_two_router("broadcast_testrouter0_link0", "testrouter1", "testrouter0")
    print(N.list_routers())
    N.print_network()
