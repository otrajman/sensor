#!/usr/bin/env python
import argparse, sys, json
parser = argparse.ArgumentParser(description='Measure distance')
parser.add_argument('-r', '--rounds', nargs='?', help='Rounds to measure', type=int, dest='rounds')
parser.add_argument('-t', '--test', nargs='?', help='Run in test mode', type=bool, dest='test', const=True)
parser.add_argument('-c', '--config', nargs='?', help='Configuration file', type=str, dest='config')
args = parser.parse_args()

if args.test: print("Test mode")

measurements = 5
if args.rounds: measurements = int(args.rounds)

import RPi.GPIO as GPIO
import time
TRIG=23
ECHO=24
print("Measuring",measurements,"times")

accum = 0

for i in range(measurements):
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(TRIG, GPIO.OUT)
  GPIO.setup(ECHO, GPIO.IN)
  GPIO.output(TRIG, False)
  print("Waiting",i + 1,"/",measurements)
  time.sleep(3)
  GPIO.output(TRIG, True)
  time.sleep(0.00001)
  GPIO.output(TRIG, False)

  while GPIO.input(ECHO) == 0:
    pulse_start = time.time()

  while GPIO.input(ECHO) == 1:
    pulse_end = time.time()

  pulse_duration = pulse_end - pulse_start

  distance = pulse_duration * 17150
  distance = round(distance, 2)
  print("Distance",i + 1,":",distance,"cm")
  accum += distance

  GPIO.cleanup()

print("Avg Distance:",round(accum/measurements, 2),"cm")

if args.test or not args.config: sys.exit()

from mailjet_rest import Client

config = json.loads(open(args.config, 'r').read()) 

api_key = config['api_key'] 
api_secret = config['api_secret']
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

print("Sending From", config['From'])
print("Sending To", config['To'])

data = {
  'Messages': [
    {
      "From": config['From'],
      "To": config['To'],
      "Subject": "Tree water level",
      "TextPart": 'Approximate water remaining: ' + str(round(30 - distance,2)) + ' cm',
    }
  ]
}

result = mailjet.send.create(data=data)
print(result.status_code)
print(result.json())
