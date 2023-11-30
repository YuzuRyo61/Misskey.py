##########
Misskey.py
##########

Python wrapper library for the Misskey( https://github.com/misskey-dev/misskey ) API.

It is mainly compatible with the latest version of Misskey's API.

Features
========

- User-friendly design using Python type support
- Each method defines a data class based on the Misskey API documentation
- In addition to synchronous processing with requests, asynchronous processing with aiohttp is also supported

Installation
============

.. warning::
    A new Misskey.py is currently under development.

    Therefore, it is subject to change from what is described in the README.

**Python 3.8 or later required**

Misskey.py can be obtained using pip:

.. code-block::
    pip install Misskey.py

Use the ``async`` extra if you want to use the asynchronous processing version of the class using aiohttp:

.. code-block::
    pip install Misskey.py[async]

Usage
=====

Synchronization
---------------

.. highlight:: python
    from pprint import pprint
    from misskey import Misskey

    mk = Misskey(address="https://misskey.example.com")
    pprint(mk.meta())

Asynchronous
------------

.. highlight:: python
    import asyncio
    from pprint import pprint

    import aiohttp

    from misskey.asynchronous import AsyncMisskey


    async def main():
        async with aiohttp.ClientSession() as client:
            mk = AsyncMisskey(address="https://misskey.example.com/", session=client)
            pprint(await mk.meta())

    if __name__ == '__main__':
        asyncio.run(main())

License
=======

MIT License

.. code-block::
    MIT License

    Copyright (c) 2019 YuzuRyo61

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
