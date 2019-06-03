import os
import django
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
from sensor.models import Distance
import socketserver, json
import logging
import time

class IoTRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        client = self.request.getpeername()
        logging.info("Client connecting: {}".format(client))

        for line in self.rfile:
            # get a request message in JSON and converts into dict
            try:
                request = json.loads(line.decode('utf-8'))
            except ValueError as e:
                # reply ERROR response message
                error_msg = '{}: json decoding error'.format(e)
                status = 'ERROR {}'.format(error_msg)
                response = dict(status=status, deviceid=request.get('deviceid'),
                                msgid=request.get('msgid'))
                response = json.dumps(response)
                self.wfile.write(response.encode('utf-8') + b'\n')
                self.wfile.flush()
                logging.error(error_msg)
                break
            else:
                status = 'OK'
                logging.debug("{}:{}".format(client, request))

            # extract the sensor data from the request
            data = request.get('data')
            if data:        # data exists
                distance = float(data.get('distance'))
                #print(distance)
                Distance(distance=distance, pub_date=timezone.now()).save()

        # end of for loop
        logging.info('Client closing: {}'.format(client))

# logging.basicConfig(filename='', level=logging.INFO)
logging.basicConfig(filename='', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

serv_addr = ("",9009)
with socketserver.ThreadingTCPServer(serv_addr, IoTRequestHandler) as server:
    logging.info('Server starts: {}'.format(serv_addr))
    server.serve_forever()