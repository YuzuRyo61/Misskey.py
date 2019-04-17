# Misskey.py

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
[![Build Status](https://travis-ci.org/YuzuRyo61/Misskey.py.svg?branch=v1)](https://travis-ci.org/YuzuRyo61/Misskey.py)
[![Coverage Status](https://coveralls.io/repos/github/YuzuRyo61/Misskey.py/badge.svg?branch=v1)](https://coveralls.io/github/YuzuRyo61/Misskey.py?branch=v1)

> Japanese version available. [Click Here](README-JP.md).

This script is Python library for Misskey Instance.

This library is only available in Python3.

[Misskey](https://github.com/syuilo/misskey) is made by [syuilo](https://github.com/syuilo).

⚠ **This branch is currently undergoing destructive changes! Therefore, there is a possibility that the function until now can not be used.**

---

## How to install

### Use pip (Recommend)

```bash
pip install Misskey.py
# or
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

# If use the token (i is sha256 hashed from appSecret and accessToken)
misskey = Misskey("misskey.xyz", i="abcdef123...")
```

## Other

**Pull requests are HUGE WELCOME!**

We hope you will contribute to the completion of the library by all means.
