# Misskey.py

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
[![Python test](https://github.com/YuzuRyo61/Misskey.py/actions/workflows/test.yml/badge.svg)](https://github.com/YuzuRyo61/Misskey.py/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/YuzuRyo61/Misskey.py/branch/main/graph/badge.svg?token=97A1HJHUMW)](https://codecov.io/gh/YuzuRyo61/Misskey.py)
[![Documentation Status](https://readthedocs.org/projects/misskeypy/badge/?version=latest)](https://misskeypy.readthedocs.io/ja/latest/?badge=latest)

Misskeyインスタンス用のPythonライブラリです。

※Python3でのみ使用できます。

[Misskey](https://github.com/misskey-dev/misskey) は [syuilo](https://github.com/syuilo) 氏が作成した分散型SNSソフトウェアです。

---

## インストール

### pipを使う (推奨)

```bash
pip install Misskey.py
# or
pip3 install Misskey.py
```

## 使い方

### ライブラリのインポートと初期化

```python
from misskey import Misskey

mk = Misskey("misskey.io")  # インスタンスアドレスを入力、未入力の場合は"misskey.io"が指定されます。

# ノートしてみましょう！
mk.notes_create(
    text="Hello Misskey.py!"
)
```

#### トークンキーを使用する

```python
from misskey import Misskey

# トークンを指定する場合
mk = Misskey("misskey.io", i="abcdef123...")
```

### トークンを作成する

```python
from misskey import Misskey, MiAuth

auth = MiAuth("misskey.io", name="misskey.py")
# 認証URLを取得し、クライアントのブラウザでこれを開きます。
url = auth.generate_url()
# 認証許可後、この関数を実行します。
token = auth.check()
# トークンを使ってMisskey.pyを使う場合は以下のようにします。
mk = Misskey("misskey.io", i=token)  # または: misskey = misskey("misskey.io", i=auth.token)
```

## その他

プルリクエスト大歓迎です！

是非ともライブラリ完成に貢献していただけると幸いです。
