# Spider

Spider is a command line tool, for simple network design. With spider the user can create networks of virtual machines. Spider is capable of generating a Vagrantfile, which can the user can use for network deployment.

## Prerequisites
 > Python 3.9
## Requiered Python modules
> click

If you have python preisntalled on your system, create a virtual environment, and run:
> pip install click.

## Test
If spider is working correctly it says hi to you if you greet it it.
Run in the terminal:
> spider hi

## Available commands
  add-host            Adds a host to the router
  add-link-to-router  Adds a link to the existing router
  add-router          Adds router to the network
  clear-work          Deletes everything that was previously done
  composev            composes vagrantfile and saves it to path location
  del-host            delete the selected host of the router
  del-link            deletes link of the selected router
  hi                  Just to say hi
  link-routers        connects two unconnected routers
  list-hosts          Lists all hosts of the selected router
  list-routers        List the connected routers on the network
  load-network        Loads in a network which is stored in a pickle file
  print-net           prints out the network
  save-network        saves the created network in a pickle file
  start-new           Creates a new network
  unlink-routers      Deletes link connection between two routers
