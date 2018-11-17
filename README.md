# Misskey.py

> Japanese version available. [Click Here](README-JP.md).

This script is Python library for Misskey Instance.

[Misskey](https://github.com/syuilo/misskey) is made by [syuilo](https://github.com/syuilo).

---

## How to install

### Use pip (Recommend)
```bash
pip3 install Misskey.py
```

## usage

### import library (init)
```python
from Misskey import Misskey

misskey = Misskey("misskey.xyz") # Input instance address (If leaved no attribute, it sets "misskey.xyz")
```

#### Use token key
```python
from Misskey import Misskey

# If use the appSecret and accessToken
misskey = Misskey("misskey.xyz", appSecret="abcdef123...", accessToken="abcdef123...")
```

**or**

```python
from Misskey import Misskey

# If use the apiToken (apiToken is sha256 hashed from appSecret and accessToken)
misskey = Misskey("misskey.xyz", apiToken="abcdef123...")
```