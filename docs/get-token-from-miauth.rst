MiAuthでトークンを取得する
==========================

Misskeyは認証方法の一つとしてMiAuthがあります。

この認証方法はMisskey 12.39.1以降のインスタンスでサポートされます。

MiAuthでの認証を容易にするため、Misskey.pyにはMiAuthクラスがあります。

.. autoclass:: misskey.MiAuth
  :noindex:

認証URLを作成する
-------------------

まず、MiAuthクラスをインスタンス化します。

少なくとも、インスタンスアドレス( ``address`` )と名前 ( ``name`` ) を入力します。

また、必要に応じて権限( ``permission`` )やコールバックURL( ``callback`` )を追加で指定します。

.. code-block:: python

    from misskey import MiAuth

    # MiAuthインスタンスを作成
    mia = MiAuth("mk.example.com", name="Misskey.py App")

    # permissionを指定する場合
    mia_p = MiAuth(
        "mk.example.com",
        name="Misskey.py App",
        permission=[
            "read:account",
            "write:notes",
        ]
    )

インスタンス化したら、メソッド ``generate_url`` でURLを作成します。

作成したURLをエンドユーザー(認証してもらうユーザー)のブラウザで開きます。

.. code-block:: python

    from misskey import MiAuth
    import webbrowser

    mia = MiAuth("mk.example.com", name="Misskey.py App")

    url = mia.generate_url()

    webbrowser.open(url) # 例としてブラウザを開きます

トークンを取得する
--------------------

エンドユーザーの認証が完了したら、メソッド ``check`` でトークンの取得を行います。

.. code-block:: python

    from misskey import MiAuth
    import webbrowser

    mia = MiAuth("mk.example.com", name="Misskey.py App")

    token = mia.check() # 認証が行えたかをチェックします

正しく認証された場合は、トークンが返されます。問題があった場合は例外 ``MisskeyMiAuthFailedException`` が送出されます。

.. autoexception:: misskey.exceptions.MisskeyMiAuthFailedException
   :noindex:

また、認証されたトークンはプロパティ ``token`` にも保存されます。

取得したトークンは、そのままMisskeyクラスなどで使用します。

.. code-block:: python

    from misskey import MiAuth, Misskey

    mia = MiAuth("mk.example.com", name="Misskey.py App")
    token = mia.check()

    mk = Misskey("mk.example.com", i=token)

セッションIDを他で保存する場合
----------------------------------

スクリプト上、MiAuthインスタンスを保持できない場合は、
プロパティ ``session_id`` を使用してセッションIDを保存することもできます。

.. code-block:: python

    from misskey import MiAuth

    mia = MiAuth("mk.example.com", name="Misskey.py App")

    session_id = str(mia.session_id) # セッションIDを取得

MiAuthインスタンス化時に引数 ``session_id`` を代入することで同じセッションIDで再開できます。

.. code-block:: python

    from misskey import MiAuth

    session_id = "00000000-0000-0000-0000-000000000000"

    mia_n = MiAuth("mk.example.com", session_id=session_id)
