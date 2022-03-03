はじめに
========

Misskey.pyはMisskeyのAPIの利用を容易にするためのラッパーAPIライブラリです。

前提
-------

Misskey.pyはPython 3.7以降からサポートしています。

Python 2.xやPython 3.6以前はサポートされませんのでご注意ください。

インストール
-------------

PyPIから直接インストールすることができます。

::

    pip install Misskey.py

基本概念
----------

Misskey.pyはメソッドでAPIリクエストを送信する仕組みになっています。

インスタンス化するときに少なくともMisskeyのインスタンスアドレスを指定するだけで使用できます。

.. code-block:: python

    from misskey import Misskey

    mk = Misskey("mk.example.com")

    info = mk.meta()

    print(info["name"]) # インスタンス名
