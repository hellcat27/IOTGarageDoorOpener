import RPi.GPIO as GPIO
import time
import logging
import smtplib
import socket
import sys
import errno
import multiprocessing
#setup the Environment
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
chan_list_output = [6, 5]
chan_list_input = [18, 25]
GPIO.setup(chan_list_input, GPIO.IN)
GPIO.setup(chan_list_output, GPIO.OUT)
GPIO.output(5,GPIO.HIGH)
GPIO.output(6,GPIO.HIGH)
#Setup the email realy
logging.basicConfig(filename='logfile.log',level=logging.DEBUG,format='%(asctime)s %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')
gmail_user = 'testemail@gmail.com'
gmail_password = '246234sQ@!da'
sender = 'test123123@gmail.com'
receivers = ['number@vtext.com', 'number@vtext.com']
#take a port as arugment if none supplied use default port
if len(sys.argv) > 1:
   if sys.argv[1].isdigit() and int(sys.argv[1]) > 1024:
      PORT = int(sys.argv[1])
   else:
        logging.error('Please provide a port greater than 1024')
        sys.exit(1)
else:
   PORT=9001
#Auth token for requests
TOKEN="2C9EC7BA1FCA4534186DD8082571D547ADA2A6B4E8C5BCC9AA0E093CCFC69BB7"
#function to map gpio to garage door
def gdo_to_gpio_door(gdo):
   if(gdo == 0):
      return 6
   elif(gdo == 1):
      return 5
#function to map gdo sensor to do gpio
def gdo_to_gpio_sensor(gdo):
   if(gdo == 0):
      return 18
   elif(gdo == 1):
      return 25
#function to open the garage door
def gdo_open(gdo):
   GPIO.output(gdo_to_gpio_door(gdo),GPIO.LOW)
   time.sleep(1)
   GPIO.output(gdo_to_gpio_door(gdo),GPIO.HIGH)
   logging.info('Door opened.')
#function to close garage door
def gdo_close(gdo):
   GPIO.output(gdo_to_gpio_door(gdo),GPIO.LOW)
   time.sleep(1)
   GPIO.output(gdo_to_gpio_door(gdo),GPIO.HIGH)
   logging.info('Door closed')
def get_status(gdo):
   return GPIO.input(gdo_to_gpio_sensor(gdo))
def map_status(status):
   if status == 1:
        return "Open"
   elif status == 0:
        return "Closed"
#function to send email
def send_email(msg):
   try:
        smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtpObj.ehlo()
        smtpObj.login(gmail_user, gmail_password)
        smtpObj.sendmail(sender, receivers, msg)
        logging.info('Alert sent')
   except:
        logging.error('Error: Unable to send email.')
#function is used by child processes to monitor the doors.  After so long alerts are sent to the email list and after even long the door will auto close
def alert_door_open(gdo):
   #max counters are low for demo purpuse
   counter_max = 30
   over_counter_max = 60
   while True:
        counter = 0
        over_counter =0
        time.sleep(1)
        if map_status(get_status(gdo)) == "Open":
                while True:
                        time.sleep(1)
                        if map_status(get_status(gdo)) == "Closed":
                                break
                        elif over_counter == over_counter_max:
                                send_email("Garage Door %s has been open longer than %s seconds.  Closing door" % (gdo,over_counter))
                                gdo_close(gdo)
                                over_counter=0
                                counter=0
                        elif counter == counter_max:
                                send_email("Garage Door %s has been open longer than %s seconds." % (gdo,counter))
                                counter = 0
                        else:
                                counter+=1
                                over_counter+=1
                                logging.info('garage door "%s" open for "%s"' % (gdo,counter))
# child process function to handel connection requests
def client(connection,client_address):
   command = ""
   try:
     logging.info('connection from %s' % str(client_address))
     # Receive the data in small chunks and retransmit it
     while True:
         data = connection.recv(4096)
         command += data
        #disabled printing the auth token for security reasons
         command = command.replace('\r', '').replace('\n', '')
#        logging.info('received "%s"' % command)
         if len(command) < 64:
             continue
         if data:
             logging.info('sending data back to the client')
#              connection.sendall(data)
                #check the authenticatio token
             if command == TOKEN:
                response = "OK"
                connection.sendall(response)
                command = ""
                counter = 0;
                #retrieve command only if the auth token is good
                while True:
                     data = connection.recv(4096)
                     command += data
                     command = command.replace('\r', '').replace('\n', '')
                     logging.info('received "%s"' % command)
                        #execute command that was issued by the client
                     if len(command) < 6:
                        continue
                     if data:
                        logging.info('sending data back to the client')
                        if command ==  "0,open":
                           gdo_open(0)
                           response = "OK"
                           connection.sendall(response)
                        elif command == "0,close":
                           gdo_close(0)
                           response = "OK"
                           connection.sendall(response)
                        elif command == "1,open":
                           gdo_open(1)
                           response = "OK"
                           connection.sendall(response)
                        elif command == "1,close":
                           gdo_close(1)
                           response = "OK"
                           connection.sendall(response)
                        elif command == "0,status":
                           response = map_status(get_status(0))
                           connection.sendall(response)
                        elif command == "1,status":
                           response = map_status(get_status(1))
                           connection.sendall(response)
                        else:
                           response = "garbage command"
                           connection.sendall(response)
                     else:
                        logging.info('no more data from %s' % str(client_address))
                        break
             else:
                #response for unauthorized requests
                response = "Unauthorized"
                connection.sendall(response)
                break
         else:
            logging.info('no more data from %s' % str(client_address))
            break
   except socket.error as e:
     if e.errno != errno.ECONNRESET:
        raise # Not error we are looking for
     pass # Handle error here.
   finally:
  # Clean up the connection
     connection.close()
     sys.exit(0)

def main():
   serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#   serversocket.settimeout(100)
   logging.info("starting server on port %d" % PORT)
   logging.info("Default socket timeout: %s" %serversocket.gettimeout())
   serversocket.bind(('0.0.0.0', PORT))
   serversocket.listen(1)
   for i in range(2):
        p = multiprocessing.Process(target=alert_door_open, args=(i,))
        p.start()
   while True:
        # Wait for a connection
        logging.info('waiting for a connection')
        connection, client_address = serversocket.accept()
#       connection.settimeout(5000)
        logging.info("Default socket timeout: %s" %connection.gettimeout())
        p = multiprocessing.Process(target=client, args=(connection,client_address,))
        p.start()

   #cleans up the GPIO Status on the pins.
   GPIO.cleanup()

main()
