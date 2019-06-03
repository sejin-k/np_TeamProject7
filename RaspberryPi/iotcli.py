import socket, json, time, sys
import selectors , uuid
import logging
import serial
# import random, math


def sensor_data():
   s = serial.Serial('/dev/ttyACM0', 9600)
   s.flushInput()
   while 1:
      distance = s.readline()
      yield distance[:-2].decode('utf-8')


class IoTClient:
    def __init__(self, server_addr, deviceid):
        """IoT client with persistent connection
        Each message separated by b'\n'

        :param server_addr: (host, port)
        :param deviceid: id of this IoT
        """


        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(server_addr)  # connect to server process
        rfile = sock.makefile('rb')  # file-like obj
        sel = selectors.DefaultSelector()
        sel.register(sock, selectors.EVENT_READ)

        self.sock = sock
        self.rfile = rfile
        self.deviceid = deviceid
        self.sel = sel
        self.requests = {}      # messages sent but not yet received their responses
        self.time_to_expire = None

    def select_periodic(self, interval):
        """Wait for ready events or time interval.
        Timeout event([]) occurs every interval, periodically.
        """
        now = time.time()
        if self.time_to_expire is None:
            self.time_to_expire = now + interval
        timeout_left = self.time_to_expire - now
        if timeout_left > 0:
            events = self.sel.select(timeout=timeout_left)
            if events:
                return events
        # time to expire elapsed or timeout event occurs
        self.time_to_expire += interval # set next time to expire
        return []


    def run(self):
        # Report sensors' data forever
        s_dis =  sensor_data()

        msgid = 0

        while True:
            try:
                events = self.select_periodic(interval=5)
                if not events:      # timeout occurs
                    try:
                        distance = next(s_dis)
                    except StopIteration:
                        logging.info('No more sensor data to send')
                        break
                    data = dict(distance=distance)
                    # msgid = str(uuid.uuid1())
                    msgid += 1
                    request = dict(method='POST', deviceid=self.deviceid, msgid=msgid, data=data)
                    logging.debug(request)
                    request_bytes = json.dumps(request).encode('utf-8') + b'\n'
                    self.sock.sendall(request_bytes)
                    self.requests[msgid] = request_bytes
                else:               # EVENT_READ
                    response_bytes = self.rfile.readline()     # receive response
                    if not response_bytes:
                        self.sock.close()
                        raise OSError('Server abnormally terminated')
                    response = json.loads(response_bytes.decode('utf-8'))
                    logging.debug(response)

                    # msgid in response allows to identify the specific request message
                    # It enables asynchronous transmission of request messages in pipelining
                    msgid = response.get('msgid')
                    if msgid and msgid in self.requests:
                        del self.requests[msgid]
                    else:
                        logging.warning('{}: illegal msgid received. Ignored'.format(msgid))
            except Exception as e:
                logging.error(e)
                break
        # end of while loop

        logging.info('client terminated')
        self.sock.close()

if __name__ == '__main__':
    if len(sys.argv) == 3:
        host, port = sys.argv[1].split(':')
        port = int(port)
        deviceid = sys.argv[2]
    else:
        print('Usage: {} host:port deviceid'.format(sys.argv[0]))
        sys.exit(1)

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    client = IoTClient((host, port), deviceid)
    client.run()
