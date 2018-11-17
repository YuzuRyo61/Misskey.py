try:
    from Misskey import Misskey
except ImportError:
    import sys
    sys.path.append("../")
    from Misskey import Misskey

import webbrowser
import os

if __name__ == "__main__":
    instance = input("Your Misskey instance Address: ")
    os.makedirs("key", exist_ok=True)
    with open("key/instance.txt", "w") as inst:
        inst.write(instance)

    permission = [
      "account-read",
      "account-write",
      "note-read",
      "note-write",
      "reaction-read",
      "reaction-write",
      "following-read",
      "following-write",
      "drive-read",
      "drive-write",
      "notification-read",
      "notification-write",
      "favorite-read",
      "favorites-read",
      "favorite-write",
      "account/read",
      "account/write",
      "messaging-read",
      "messaging-write",
      "vote-read",
      "vote-write"
    ]
    
    res_createApp = Misskey().create_app(instance, "Misskey.py SAMPLE", "Misskey.py Sample Application", permission)
    
    with open("key/application.txt", "w") as key:
        key.write("{0}\n{1}".format(res_createApp['id'], res_createApp['secret']))
    
    res_auth = Misskey().auth_session_generate(instance, res_createApp['secret'])

    webbrowser.open(res_auth['url'])
    print("Browser opened, Please authorize in your browser.\nIf you don't open your browser, Please access below: {}".format(res_auth['url']))
    input("If finished authorize, Please Enter key: ")

    res_authorize = Misskey().auth_session_userkey(instance, res_createApp['secret'], res_auth['token'])

    with open("key/userToken.txt", "w") as token:
        token.write(res_authorize['accessToken'])

    print("Finish!")