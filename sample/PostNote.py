try:
    from Misskey import Misskey
except ImportError:
    import sys
    sys.path.append("../")
    from Misskey import Misskey
    from Misskey.Exceptions import *

if __name__ == "__main__":
    with open("key/application.txt", "r") as appkey:
        appId = appkey.readline().replace("\n", "")
        appSecret = appkey.readline().replace("\n", "")

    with open("key/userToken.txt", "r") as usertokenf:
        userToken = usertokenf.readline().replace("\n", "")

    with open("key/instance.txt", "r") as instancefile:
        instance = instancefile.readline().replace("\n", "")

    misskey = Misskey(instance, appSecret=appSecret, accessToken=userToken)

    body = input("Post to Misskey: ")

    try:
        res = misskey.notes_create(body)
    except MisskeyBadRequestException:
        print("Failed!")
    except MisskeyResponseException:
        print("Failed!")
    else:
        print("Success!")
    finally:
        input("[ENTER TO EXIT]")
