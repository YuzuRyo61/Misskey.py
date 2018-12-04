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

    pollchoices = []
    pollappend = None

    print("Up to 10 pieces can be added.")
    print("Hint: Leave it blank to finish adding the choice.")
    while pollappend == '' or len(pollchoices) < 10:
        pollappend = input("Poll Choice(Choices) No.{}: ".format(len(pollchoices) + 1))
        if pollappend == '':
            if len(pollchoices) >= 2:
                break
            else:
                print("You have to add two choices.")
                continue
        else:
            pollchoices.append(pollappend)

    print("Post in this ballot item: ")
    for i in range(len(pollchoices)):
        print(pollchoices[i])
    body = input("Post to Misskey (Can be leave a blank): ")

    try:
        res = misskey.notes_create(body, poll=pollchoices)
    except MisskeyBadRequestException:
        print("Failed!")
    except MisskeyResponseException:
        print("Failed!")
    except:
        print("Failed other exception!")
    else:
        print("Success!")
    finally:
        input("[ENTER TO EXIT]")
