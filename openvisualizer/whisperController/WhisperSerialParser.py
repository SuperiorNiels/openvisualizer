import struct, csv

class WhisperSerialParser:

    def __init__(self):
        self.UINJECT_MASK    = 'whispersender'
        self.SLOT_DURATION   = 0.015
        self.last_counter         = None
        self.file = open("output.csv", mode="w")
        self.writer = csv.writer(self.file , delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    def parse(self, input):
        if input[0]==ord('D'):
            if self.UINJECT_MASK == ''.join(chr(i) for i in input[-13:]):

                request = input[:-13]
                counter = request[-2:]
                counter = struct.unpack("<H", ''.join([chr(c) for c in counter]))[0]
                request = request[:-2]

                asn_arrive = request[-5:]
                asn_arrive = struct.unpack('<HHB', ''.join([chr(c) for c in asn_arrive]))

                asn_inital = input[3:8]
                asn_inital = struct.unpack('<HHB', ''.join([chr(c) for c in asn_inital]))

                if self.last_counter!=None:
                    if counter-self.last_counter!=1:
                        print 'MISSING {0} packets!!'.format(counter-self.last_counter-1)
                self.last_counter = counter

                latency = self.SLOT_DURATION*((asn_inital[0]-asn_arrive[0])+(asn_inital[1]-asn_arrive[1])*256+(asn_inital[2]-asn_arrive[2])*65536)

                self.writer.writerow([counter, latency])
                self.file.flush()
                
    def __del__(self):
        self.file.close()