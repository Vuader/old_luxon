.. _install:

Installation
============

Luxon Framework currently fully supports `CPython <https://www.python.org/downloads/>`__ 3.6.

PyPi
----
pip install luxon

Source Code
-----------

Luxon infrastructure and code is hosted on `GitHub <https://github.com/TachyonicProject/luxon>`_.                                   
Making the code easy to browse, download, fork, etc. Pull requests are always welcome!

Clone the project like this:

.. code:: bash

    $ git clone https://github.com/TachyonicProject/luxon.git

Once you have cloned the repo or downloaded a tarball from GitHub, you 
can install Luxon like this:

.. code:: bash

    $ cd luxon
    $ pip install .

Or, if you want to edit the code, first fork the main repo, clone the fork
to your desktop, and then run the following to install it using symbolic
linking, so that when you change your code, the changes will be automagically
available to your app without having to reinstall the package:

.. code:: bash

    $ cd luxon
    $ pip install -e .

You can manually test changes to the luxon by switching to the 
directory of the cloned repo:

.. code:: bash

    $ pip install -r requirements-dev.txt
    $ paver test
