# -*- coding: utf-8 -*-
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time
import datetime
import json
import hashlib
from Misskey.Exceptions import MisskeyWebSocketException

idHash = None
ch = None
omf = None

class MisskeyStreamListener:
    def __init__(self, channel, on_message_func):
        self.ch = channel

        idHashRaw = str(datetime.datetime.today())
        self.idHash = hashlib.sha256(idHashRaw.encode('utf-8')).hexdigest()

        global idHash
        idHash = self.idHash

        global ch
        ch = self.ch

        global omf
        omf = on_message_func

    def insertchannel(self, channel):
        global ch
        ch = channel

    @staticmethod
    def on_message(ws, message):
        omf(message)

    @staticmethod
    def on_error(ws, error):
        raise MisskeyWebSocketException("Websocket error throwed: " + error)

    @staticmethod
    def on_open(ws):
        def run(*args):
            # for debug output:
            # print("ch: " + str(ch) + "\nidHash: " + str(idHash))
            contAttr = {
                'type': 'connect',
                'body': {
                    'channel': ch,
                    'id': idHash
                }
            }
            ws.send(json.dumps(contAttr))
        try:
            thread.start_new_thread(run, ())
        except KeyboardInterrupt:
            MisskeyStreamListener.on_close(ws)

    @staticmethod
    def on_close(ws):
        disContAttr = {
            'type': 'disconnect',
            'body': {
                'id': idHash
            }
        }
        ws.send(json.dumps(disContAttr))
