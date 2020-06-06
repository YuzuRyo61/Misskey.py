====================
Getting Started
====================

Installing
---------------
Normally you would install the library from PyPi:

.. code-block:: console

    pip install Misskey.py

Quickstart
---------------
Import the Misskey class. Enter an instance of Misskey as the first argument during class initialization.

.. code-block:: python3

    from Misskey import Misskey

    misskey = Misskey("misskey.io")

In the above construction, the specified server will be accessed without a token.
If you want to use token, do as follows.

.. code-block:: python3

    from Misskey import Misskey

    misskey = Misskey("misskey.io", i="abcdefg123456")

Enter the token in the argument i.
With this argument, the Misskey class validates that this token is available at initialization.
Throws ``MisskeyInitException`` if not available.

.. automethod:: Misskey.Exceptions.MisskeyInitException

Even after creating the instance, you can change it later by doing the following.

.. code-block:: python3

    from Misskey import Misskey

    misskey = Misskey("misskey.io")

    misskey.apiToken = "abcdefg123456"

If you have set a token, you can read your account information.

.. code-block:: python3

    from Misskey import Misskey

    misskey = Misskey("misskey.io", i="abcdefg123456")

    your_data = misskey.i()

.. automethod:: Misskey.Misskey.Misskey.i

To post using your account:

.. code-block:: python3

    from Misskey import Misskey

    misskey = Misskey("misskey.io", i="abcdefg123456")

    created_notes = misskey.notes_create("This note is posted from Misskey.py!")

.. automethod:: Misskey.Misskey.Misskey.notes_create
