# Spider

Spider is a command line tool, for simple network design. With spider the user can create networks of virtual machines. Spider is capable of generating a Vagrantfile, which can the user can use for network deployment.

## Prerequisites
Make sure that the right version of Python is preinstalled on your system.
 > Python 3.9
## Requiered Python modules
> click

## Running for the first time
After cloning the repository, navigate to the repository folder on your machine.
Open a terminal window and run the following commands:
 > virtualenv venv
 
 > source ./venv/bin/activate
 
 > pip install --editable .
 
 Now you have your virtual machine set up. Run  'pip freeze' to see if the click module is installed properly.
 
 
## Test
If spider is working correctly it says hi to you if you greet it.
Run in the terminal:

> spider hi

## One easy example
First clear the working directory :

> spider clear-work

Then start a new design :

> spider start-new myfirstdesign

Add a router to the network:

> spider add-router router0

Add a link to your new router:

> spider add-link-to-router router0 link0 50 1000

(This command creates a link to the router0 and applies a 50 Mbits bandwith and a 1000 ms delay)

Add a host to your router :
> spider add-host router0 host0 link0

If you would like to see your network design you can always print it out in your terminal window. Type:

> spider print-net

At this point you suppose to have one router and one host in your system. If you would like to save your work:

> spider save-network ./demo myfirstnet.pickle

(This command generates a pickle file and save all of your previous work)

To generate the vagrantfile:

> spider composev ./vagrant

## Examples
Three examples are available in /testnets folder. To load one of them type the following command.

> spider clear-work

> spider load-network ./testnets/2hosts_1router final.pickle

Now you can edit the network or generate a vagrantfile.

## Tips and tricks

1. It is a good practice to clear your working cache before loading or starting a new network. Run: 'spider clear-work' every time before a 'start-new' or a 'load-network' command
2. If you don't know what a particular command does type 'spider $COMMAND --help'
3. Sometimes it happens after vagrant up that the set link delays and bandwidths are not applied. In this case run 'vagrant reload'
4. It is a good practice to add the routers first to your network design and then the links and after that the hosts. Because spider only stores those links and hosts which are connected to a router.

