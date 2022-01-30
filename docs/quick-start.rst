クイックスタート
=================

基本
--------

Misskey.pyのメインのクラスは以下のクラスです。

.. autoclass:: misskey.Misskey
   :noindex:

クラスをインスタンス化するために、少なくとも、Misskeyインスタンスアドレスを指定してください。

必要な場合はURLプロトコルを含めることもできます。

.. code-block:: python

    from misskey import Misskey

    mk = Misskey("mk.example.com")

    mk_local = Misskey("http://localhost:3000") # URLプロトコルを含めた場合

各メソッドにエンドポイント名を記載しています。

使用するインスタンスのMisskey APIドキュメントと併用してご確認下さい。

**例:** ``i`` → Misskey APIエンドポイント ``/api/i`` へHTTPリクエスト

トークンを加える
------------------

Misskeyインスタンスで使用できるトークンを持っている場合は、
Misskey.pyはインスタンス化時、もしくはプロパティに代入することで使用することができます。

インスタンス化時に代入
^^^^^^^^^^^^^^^^^^^^^^^^^

コンストラクタに ``i`` という引数にトークンを代入します。

.. code-block:: python

    from misskey import Misskey

    mk = Misskey("mk.example.com", i="xxxxxxxxxx")

    print(mk.i()) # あなたのプロフィールが表示されます

トークンが有効でない場合は以下の例外が出されます。

.. autoexception:: misskey.exceptions.MisskeyAuthorizeFailedException
   :noindex:

プロパティに代入
^^^^^^^^^^^^^^^^^^^

インスタンスの ``token`` プロパティに代入します。

.. code-block:: python

    from misskey import Misskey

    mk = Misskey("mk.example.com")

    mk.token = "xxxxxxxxxx"

    print(mk.i()) # あなたのプロフィールが表示されます

トークンが有効でない場合は以下の例外が出されます。

.. autoexception:: misskey.exceptions.MisskeyAuthorizeFailedException
   :noindex:

投稿をしてみる
----------------

トークンを含めたインスタンスで、MisskeyにNoteを投稿してみましょう。

メソッド ``notes_create`` を使用すると、Noteを作成することができます。

.. automethod:: misskey.Misskey.notes_create
   :noindex:

以下がサンプルコードです。

.. code-block:: python

    from misskey import Misskey

    mk = Misskey("mk.example.com", i="xxxxxxxxxx")

    new_note = mk.notes_create(text="Hello Misskey.py!")

    print(new_note["createdNote"]["id"]) # 投稿されたNoteのIDが表示されます

コードを実行するとNoteが投稿されます。ブラウザなどで確認してみてください。
