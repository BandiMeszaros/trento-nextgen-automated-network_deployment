import click
import pickle
import network_generator as ng
import os
import shutil

class Config:

    def __init__(self):
        if os.path.isfile("./.spider/net.pickle"):
            try:
                file = open("./.spider/net.pickle", "rb")
                self.net = pickle.load(file)
                file.close()
            except ImportError as m:
                self.net = ''
                print("Error opening net file")
                print("Error message:")
                print(m)

        elif not os.path.isdir("./.spider"):
            os.makedirs("./.spider")
            self.net = ''

        os.remove("./.spider/net.pickle")

    def __del__(self):
        file = open(f"./.spider/net.pickle", "wb")
        pickle.dump(self.net, file)
        file.close()


config_pass = click.make_pass_decorator(Config, ensure=True)

@click.group()
@config_pass
def spider(config):
    pass

@spider.command()
@click.option("--n", is_flag=True, help="Deletes all previous network settings", type=bool, flag_value=True)
@click.argument('network_name')
@config_pass
def start_new(config, network_name, n):
    """
    Creates a new network
    """
    if n:
        shutil.rmtree("./.spider")
        os.makedirs("./.spider")

    config.net = ng.Network(network_name)


@spider.command()
@config_pass
def hi(config):
    """Just to say hi"""
    print("hi!! :)")

@spider.command()
@config_pass
def print_net(config):
    """prints out the network"""
    config.net.print_network()

@spider.command()
@click.argument("router_name")
@click.argument("links_number", type=int)
@click.argument("hosts_number", type=int)
@config_pass
def add_router(config, router_name, links_number, hosts_number):
    """Adds router to the network, hosts number and links number has to be defined

    ------

    Hosts number cannot be greater than links number"""
    config.net.add_router(router_name, links_number, hosts_number)

@spider.command()
@config_pass
def list_routers(config):
    """List the connected routers on the network"""
    print(config.net.list_routers())

@spider.command()
@config_pass
@click.argument("file_root", required=False)
@click.argument("file_name", required=False)
def save_network(config, file_root, file_name):
    """saves the created network in a pickle file
    -----
    if file_root and file_name not defined then the file is at ./network/pickles/{network name}_network.pickle"""
    config.net.save_network(file_root,file_name)
    print("Network saved....")

@spider.command()
@config_pass
@click.argument("file_root", required=False)
@click.argument("file_name")
def load_network(config, file_name, file_root="./network/pickles"):
    """
    Loads in a network which is stored in a pickle file
    default
    """
    config.net.load_network(file_name, file_root)

@spider.command()
@config_pass
@click.argument("path", type=click.Path())
def composeV(config, path):
    """composes vagrantfile and saves it to path location"""
    if not os.path.exists(path):
        os.makedirs(path)

    config.net.compose_vagrantfile(path)
    print(f"Vagrantfile generated....")
    print(f"Saved at: {os.path.join(path, 'Vagrantfile')}")

@spider.command()
@config_pass
@click.argument("linkname")
@click.argument("other_router")
@click.argument("link_owner_router")
def link_routers(config, linkname, link_owner_router, other_router):
    """connects two unconnected routers, the routers has to be part of the network
    -----

    One router has to have the link before call
    """
    config.net.link_two_router(linkname, other_router, link_owner_router)
    print("Connection created, see print network")

@spider.command()
@config_pass
@click.argument("linkname")
@click.argument("router1")
@click.argument("router2")
def unlink_routers(config, linkname, router1, router2):
    """Deletes link connection between two routers"""

    config.net.unlink_two_router(linkname, router1, router2)
    print(f"{linkname} has been deleted...")