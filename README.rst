
Misskey.py
==========

..

   Japanese version available. `Click Here <README-JP.md>`_.


This script is Python library for Misskey Instance.

This library is only available in Python3.

`Misskey <https://github.com/syuilo/misskey>`_ is made by `syuilo <https://github.com/syuilo>`_.

----

How to install
--------------

Use pip (Recommend)
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pip install Misskey.py
   # or
   pip3 install Misskey.py

usage
-----

import library (init)
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from Misskey import Misskey

   misskey = Misskey("misskey.xyz") # Input instance address (If leaved no attribute, it sets "misskey.xyz")

Use token key
~~~~~~~~~~~~~

.. code-block:: python

   from Misskey import Misskey

   # If use the appSecret and accessToken
   misskey = Misskey("misskey.xyz", appSecret="abcdef123...", accessToken="abcdef123...")

**or**

.. code-block:: python

   from Misskey import Misskey

   # If use the apiToken (apiToken is sha256 hashed from appSecret and accessToken)
   misskey = Misskey("misskey.xyz", apiToken="abcdef123...")

Other
=====

**Pull requests are HUGE WELCOME!**

We hope you will contribute to the completion of the library by all means.
