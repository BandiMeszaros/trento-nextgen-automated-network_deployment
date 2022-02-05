import os

class Host:
    def __str__(self):
        return self.hostname

    def __init__(self, hostname):
        self.hostname = hostname

class Router:
    def __str__(self):
        retrun_string = f"Router Name: {self.routername}\n" \
                        f"Number of links: {self.link_no}\n" \
                        f"Links by Name:\n"

        for l in self.link_conns:
            new_line = "> " + l + "\n"
            retrun_string += new_line

        retrun_string = retrun_string + f"Number of Hosts: {self.host_no}\n" \
                                        f"Hosts by Name, Host.name and links to them:\n"

        for h,v in self.connected_hosts.items():
            new_line = f"> {h}: {v[0]}, {v[1]}\n"
            retrun_string += new_line

        return retrun_string

    def __init__(self, name, hosts, links):
        self.routername = name
        self.host_no = hosts
        self.connected_hosts = {}
        self.link_conns = []
        self.link_no = links
        if self.link_no < self.host_no:
            print("can't do it: less links than hosts")
        else:
            for i in range(0, hosts):
                hostname = self.routername + f"_host{i}"
                linkname = f"broadcast_host{i}"
                self.connected_hosts[f"host{i}"] = (Host(hostname), linkname)
                self.link_conns.append(linkname)

            if links_left := self.link_no - self.host_no:

                for link in range(0, links_left):
                    self.link_conns.append(f"broadcast_{self.routername}_link{link}")

    def add_router_to_vagrant(self):
        """generates the string that will be included in the vagrantfile"""
        return_string = f'config.vm.define {self.routername} do |{self.routername}|\n  ' \
                        f'{self.routername}.vm.box = "ubuntu/bionic64"\n  ' \
                        f'{self.routername}.vm.hostname = "{self.routername}\n  '
        for l in self.link_conns:
            new_line = f'{self.routername}.vm.network "private_network", virtualbox__intnet: "{l}", ' \
                       f'auto_config: false\n  '
            return_string += new_line

        return_string += f'{self.routername}.vm.provision "shell", path: "router.sh"\n  ' \
                         f'{self.routername}.vm.provider "virtualbox" do |vb|\n    ' \
                         f'vb.memory = 256\n' \
                         f'end'

        return return_string


class Network_generator():
    def __init__(self, name):
        self.name = name
        self.vagrant_file = ''
        self.open_template()

    def open_template(self):
        with open("./template/Vagrant_template.rb", "r") as f:
            self.vagrant_file = f.read()


    def add_line(self, new_line):
        self.vagrant_file = self.vagrant_file + new_line + "\n"

    def save_to_file(self, filename="Vagrantfile", path = "./network"):
        """Saves the content of vagrant_file to a Vagrantfile"""
        if not os.path.exists(path):
            os.makedirs(path)

        file_root = os.path.join(path ,filename)

        with open(file_root, "w") as f:
            f.write(self.vagrant_file)


if __name__ == '__main__':
    test_r = Router("TestR", 3, 3)
    print(test_r)
    print(test_r.add_router_to_vagrant())