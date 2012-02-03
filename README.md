Abiquo API Command Line Tool
============================

This project is a simple command line tool for the Abiquo Cloud Platform API, using
Jython as a wrapper to the [Official Java client](https://github.com/abiquo/jclouds-abiquo).
To understand the code and adapt it to your needs, you may want to take a
look at the official Java client project page:

 * [jclouds-abiquo Source code](https://github.com/abiquo/jclouds-abiquo)
 * [jclouds-abiquo Documentation](https://github.com/abiquo/jclouds-abiquo/wiki)


Requirements
------------

To run Kahuna you will need to install *Maven >= 2.2.1*, *JRE >= 1.6* and ***Jython >= 2.5.2***.


Configuration
-------------

Since this project is currently in development process and we don't have any egg 
package ready, the *$JYHTONPATH* environment variable needs to be set manually:

    export JYTHONPATH=$(YOUR_PROJECT_HOME_DIRECTORY)

You must also copy the **config/kahuna.conf** file to **$HOME/.kahuna/kahuna.conf**
and edit it to configure the connection to your Abiquo Platform. It is also a good choice
to add the script to your PATH. You could simply create a symlink to the kahuna script
in */usr/local/bin*:

    cd <kahuna source directory>
    cp config/kahuna.conf ~/.kahuna/kahuna.conf  # Then edit the file accordingly
    chmod u+x kahuna.sh
    ln -s $(pwd)/kahuna.sh /usr/local/bin/kahuna


Running
-------

You can run now the command line as follows. If you run it without parameters, it will
print the help with all the available options:

    $ kahuna
    
    Usage: kahuna <plugin> <command> [<options>]
    The following plugins are available:
    
    Interactive shell plugin. 
        shell open     Opens an interactive shell.
    
    Template plugin. 
        template find	 Find a template given its name. 
        template list	 List all available templates. 
    
    Virtual machine plugin. 
        vm create	 Creates a virtual machine based on a given template. 
        vm delete	 Delete a virtual machine given its name. 
        vm deploy	 Deploy an existing virtual machine given its name. 
        vm find	     Find a virtual machine given its name. 
        vm list      List all virtual machines. 
        vm undeploy	 Undeploy an existing virtual machine given its name. 


Use it interactively
--------------------

You can also perform actions against the Api in an interactive way. You just need to
use the 'shell' plugin as follows:

    $ kahuna shell open
    Jython 2.5.2 (Release_2_5_2:7206, Mar 2 2011, 23:12:06) 
    [Java HotSpot(TM) Server VM (Sun Microsystems Inc.)] on java1.6.0_18
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from kahuna.session import ContextLoader
    >>> ctx = ContextLoader().load_context()
    Using endpoint: http://10.60.1.222/api
    >>> cloud = ctx.getCloudService()         
    >>> cloud.listVirtualDatacenters()
    [VirtualDatacenter [id=11, type=XENSERVER, name=Kaahumanu]]
    >>> vdc = cloud.listVirtualDatacenters()[0]
    >>> vdc.setName("Updated VDC")
    >>> vdc.update()
    >>> cloud.listVirtualDatacenters()         
    [VirtualDatacenter [id=11, type=XENSERVER, name=Updated VDC]]
    >>> ctx.close()
    >>> exit()


Adding more plugins
-------------------

Plugins are easy to create. Take a look at the [Project Wiki](https://github.com/nacx/kahuna/wiki)
to see how to create and add your own plugins.


Note on patches/pull requests
-----------------------------
 
 * Fork the project.
 * Create a topic branch for your feature or bug fix.
 * Develop in the just created feature/bug branch.
 * Add tests for it. This is important so I don't break it in a future version unintentionally.
 * Commit.
 * Send me a pull request.


Issue Tracking
--------------

If you find any issue, please submit it to the [Bug tracking system](https://github.com/nacx/kahuna/issues) and we
will do our best to fix it.

License
-------

This software is licensed under the MIT license.

Copyright (c) 2011 Ignasi Barrera

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

