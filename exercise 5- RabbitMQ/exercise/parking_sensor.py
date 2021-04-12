import json

import pika

from xprint import xprint
from db_and_event_definitions import customers_database as db

class ParkingEventProducer:

    def __init__(self):
        # Do not edit the init method.
        # Set the variables appropriately in the methods below.
        self.connection = None
        self.channel = None

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMq connection, channel, exchange and queue here
        xprint("ParkingEventProducer initialize_rabbitmq() called")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='parking_events_exchange', exchange_type="x-consistent-hash")

    def publish(self, parking_event):
        xprint("ParkingEventProducer: Publishing parking event {}".format(vars(parking_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(parking_event)) to convert the parking_event object to JSON
        
        xprint('Parking Sensor: publish: routing_key = {}'.format(parking_event.car_number))
        self.channel.basic_publish(exchange='parking_events_exchange', routing_key=parking_event.car_number, body=json.dumps(vars(parking_event)))

    def close(self):
        # Do not edit this method
        self.channel.close()
        self.connection.close()
