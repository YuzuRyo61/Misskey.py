try:
    from Misskey import Misskey
except ImportError:
    import sys
    sys.path.append("../")
    from Misskey import Misskey

import pprint

if __name__ == "__main__":
    with open("key/application.txt", "r") as appkey:
        appId = appkey.readline().replace("\n", "")
        appSecret = appkey.readline().replace("\n", "")

    with open("key/userToken.txt", "r") as usertokenf:
        userToken = usertokenf.readline().replace("\n", "")

    with open("key/instance.txt", "r") as instancefile:
        instance = instancefile.readline().replace("\n", "")
    
    misskey = Misskey(instance, appSecret=appSecret, accessToken=userToken)
    
    res = misskey.i()

    print("Name: {}".format(res['name']))
    print("UserName: @{}".format(res['username']))
    print("Notes: {}".format(res['notesCount']))
    print("Following: {}".format(res['followingCount']))
    print("Followers: {}".format(res['followersCount']))
    print("Location: {}".format(res['profile']['location']))
    if res['isCat'] == True:
        print("(=^・・^=)Meow!")