import logging
log = logging.getLogger('logger_whisper')
log.setLevel(logging.INFO)
log.addHandler(logging.NullHandler())

import time
from pydispatch import dispatcher
from openvisualizer.moteConnector import OpenParser
from openvisualizer.eventBus import eventBusClient
from WhisperParser import WhisperParser
from WhisperDioParser import WhisperDioParser
from WhisperSixtopParser import WhisperSixtopParser
from WhisperLinkTesting import WhisperLinkTester
from WhisperCoapSender import WhisperCoapSender
from WhisperCoapReceiver import WhisperCoapReceiver
from WhisperTester import WhisperTester

import WhisperDefines

class WhisperController(eventBusClient.eventBusClient):

    def __init__(self):
        super(WhisperController, self).__init__("WhisperController", [])

        self.eui = [0x00, 0x12, 0x4b, 0x00, 0x06, 0x13, 0x00, 0x00]

        # give this thread a name
        self.name = 'whisper_controller'

        # create parsers
        self.parser = WhisperParser()
        self.dio_parser = WhisperDioParser(self.eui)
        self.parser.attachSubparser("dio", self.dio_parser.parse)
        self.sixtop_parser = WhisperSixtopParser(self.eui)
        self.parser.attachSubparser("6p", self.sixtop_parser.parse)

        # Whisper link tester
        self.link_tester = WhisperLinkTester(self.eui)

        # CoAP
        self.coap_receiver = WhisperCoapReceiver("/w")
        self.coap_sender = WhisperCoapSender(self.eui)

        self.tester = WhisperTester(self)
        self.tester.setInterval(30)
        self.tester.setTimes(180)

    def parse(self, command, serialport):
        dataToSend = self.parser.parse(command)

        if not dataToSend:
            if command[0] == "neighbours":
                # Initialize data to send + indicate fake dio command
                dataToSend = [OpenParser.OpenParser.SERFRAME_PC2MOTE_WHISPER, WhisperDefines.WHISPER_COMMAND_NEIGHBOURS]

            if command[0] == "link_info":
                # Initialize data to send + indicate fake dio command
                dataToSend = [OpenParser.OpenParser.SERFRAME_PC2MOTE_WHISPER, WhisperDefines.WHISPER_COMMAND_LINK_INFO]

            if command[0] == "link":
                self.link_tester.testLink(command[1], command[2])
                return

            if command[0] == "start_test":
                self.tester.start()
                return

        if dataToSend:
            if command[-1] == "root":
                self._sendToMoteProbe(serialport, dataToSend)
                return
            else:
                try:
                    self.coap_sender.post(command[-1], dataToSend)
                except Exception as e:
                    pass
                
                return
        else:
            print "Whisper command failed."

    def _sendToMoteProbe(self, serialport, dataToSend):
        dispatcher.send(
            sender=self.name,
            signal='fromMoteConnector@' + serialport,
            data=''.join([chr(c) for c in dataToSend])
        )

    def getLinkTester(self):
        return self.link_tester

    def __del__(self):
        self.coap_sender.join()
