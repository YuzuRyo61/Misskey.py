try:
    from Misskey import Misskey
except ImportError:
    import sys
    sys.path.append("../")
    from Misskey import Misskey
    from Misskey.Exceptions import *
import os, tkinter, tkinter.filedialog, sys

if __name__ == "__main__":
    with open("key/application.txt", "r") as appkey:
        appId = appkey.readline().replace("\n", "")
        appSecret = appkey.readline().replace("\n", "")

    with open("key/userToken.txt", "r") as usertokenf:
        userToken = usertokenf.readline().replace("\n", "")

    with open("key/instance.txt", "r") as instancefile:
        instance = instancefile.readline().replace("\n", "")

    misskey = Misskey(instance, appSecret=appSecret, accessToken=userToken)

    root = tkinter.Tk()
    root.withdraw()
    fileType = [("", "*")]
    initDir = os.path.abspath(os.path.dirname(__file__))

    print("Please select your file.")
    file = tkinter.filedialog.askopenfilename(filetypes = fileType, initialdir = initDir)

    if file == '' or file == None:
        print("You didn't select a file. exiting.")
        input("[ENTER TO EXIT]")
        sys.exit()

    print("You will be upload it: {}".format(file))

    body = input("Post to Misskey (Can be leave a blank): ")

    if body == '':
        body = None

    try:
        fileupload = misskey.drive_files_create(file)
        res = misskey.notes_create(body, fileIds=[fileupload['id']])
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
