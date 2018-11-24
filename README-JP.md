# Misskey.py

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

misskey = Misskey("misskey.xyz") # インスタンスアドレスを入力、未入力の場合は"misskey.xyz"が指定されます。
```

#### トークンキーを使用する
```python
from Misskey import Misskey

# appSecretとaccessTokenを指定する場合
misskey = Misskey("misskey.xyz", appSecret="abcdef123...", accessToken="abcdef123...")
```

**もしくは**

```python
from Misskey import Misskey

# apiTokenを指定する場合(apiTokenはappSecretとaccessTokenをsha256ハッシュ化したもの)
misskey = Misskey("misskey.xyz", apiToken="abcdef123...")
```

# その他
プルリクエスト大歓迎です！

是非ともライブラリ完成に貢献していただけると幸いです。
