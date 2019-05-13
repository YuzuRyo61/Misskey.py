# Contributing

## Send a issue

If you find a bug or want to support the new API, please suggest it.

## Pull Request

Performed when other API functions are implemented. It should be in the following format:

```python
# Original API URI is "example/new-api"
def example_newApi(self, a=None, b=None):
  """
  This is example API
  
  :param a: This attribute is nullable
  :param b: This attribute must not null (but optional)
  :rtype: dict, list, or bool
  """
  payload = {
    'a': a
  }
  
  if b != None: # pragma: no cover
    payload['b'] = b
  
  # (APIURI, isIncludeApiToken, expectHttpStatus, **kwargs(payload))
  return self.__API('example/new-api', True, 200, **payload)
```
