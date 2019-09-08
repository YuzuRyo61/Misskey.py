# Misskey.py

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
[![Build Status](https://travis-ci.org/YuzuRyo61/Misskey.py.svg?branch=v1)](https://travis-ci.org/YuzuRyo61/Misskey.py)
[![Coverage Status](https://coveralls.io/repos/github/YuzuRyo61/Misskey.py/badge.svg?branch=v1)](https://coveralls.io/github/YuzuRyo61/Misskey.py?branch=v1)
[![Documentation Status](https://readthedocs.org/projects/misskeypy/badge/?version=latest)](https://misskeypy.readthedocs.io/en/latest/?badge=latest)

> Do you looking for English version? [Click Here](README.md)

Misskeyインスタンス用のPythonライブラリです。

※Python3でのみ使用できます。

[Misskey](https://github.com/syuilo/misskey)は[syuilo](https://github.com/syuilo)氏が作成した分散型SNSソフトウェアです。

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
from Misskey import Misskey

misskey = Misskey("misskey.io") # インスタンスアドレスを入力、未入力の場合は"misskey.io"が指定されます。
```

#### トークンキーを使用する

```python
from Misskey import Misskey

# トークンを指定する場合(iはappSecretとaccessTokenをsha256ハッシュ化したもの)
misskey = Misskey("misskey.io", i="abcdef123...")
```

## その他

プルリクエスト大歓迎です！

是非ともライブラリ完成に貢献していただけると幸いです。
