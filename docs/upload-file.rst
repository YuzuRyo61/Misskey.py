ファイルのアップロード
========================

Misskey.pyはMisskeyのドライブにファイルをアップロードするためのメソッドを含んでいます。

.. automethod:: misskey.Misskey.drive_files_create
   :noindex:

ファイルをアップロードするには、ファイルストリーミングを開き、それをメソッドに渡します。

.. code-block:: python

    from misskey import Misskey

    mk = Misskey("mk.example.com", i="xxxxxxxxxx")

    with open("test.png", "rb") as f:
        data = mk.drive_files_create(f)

    print(data["id"]) # アップロードされたファイルのIDを表示

ファイルストリーミング以外指定してない場合は、名前はファイル名、フォルダはルートフォルダが指定されます。
