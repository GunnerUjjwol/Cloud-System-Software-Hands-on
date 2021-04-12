from types import SimpleNamespace

import pika
import json
import dateutil.parser
import time
from db_and_event_definitions import ParkingEvent, customers_database, cost_per_hour, BillingEvent, customers_database as db, cost_per_hour
from xprint import xprint
import time


class ParkingWorker:

    def __init__(self, worker_id, queue, weight="1"):
        # Do not edit the init method.
        # Set the variables appropriately in the methods below.
        self.connection = None
        self.channel = None
        self.worker_id = worker_id
        self.queue = queue
        self.weight = weight
        self.parking_state = {}
        self.parking_events = []
        self.billing_event_producer = None
        self.customer_app_event_producer = None
        self.ename = 'parking_events_exchange'
        

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMQ connection, channel, exchange and queue here
        # Also initialize the channels for the billing_event_producer and customer_app_event_producer
        xprint("ParkingWorker {}: initialize_rabbitmq() called".format(self.worker_id))
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(self.ename, exchange_type='x-consistent-hash')
        self.channel.exchange_declare(exchange='dlx', exchange_type='direct')
        self.channel.queue_declare(queue='parking_events_dead_letter_queue')
        self.channel.queue_bind(queue='parking_events_dead_letter_queue', exchange='dlx', routing_key='dlxroute')
        self.channel.queue_declare(queue=self.queue, arguments={
                'x-dead-letter-exchange': 'dlx',
                'x-dead-letter-routing-key': 'dlxroute'
            })
        self.channel.queue_bind(exchange=self.ename, queue=self.queue, routing_key=self.weight)
        self.customer_app_event_producer = CustomerEventProducer(self.connection, self.worker_id)
        self.billing_event_producer = BillingEventProducer(self.connection, self.worker_id)
        self.customer_app_event_producer.initialize_rabbitmq()
        self.billing_event_producer.initialize_rabbitmq()

    def handle_parking_event(self, ch, method, properties, body):
        # To implement - This is the callback that is passed to "on_message_callback" when a message is received
        xprint("ParkingWorker {}: handle_event() called".format(self.worker_id))
        # Handle the application logic and the publishing of events here
        details = json.loads(body.decode('utf-8'))
        
        cust = {k: v for k,v in db.items() if v == details.get('car_number')}
        cust = list(cust.keys())

        if len(cust) == 0:
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        else:
            cust = cust[0]
            
            pe = ParkingEvent(**details)

            self.parking_events.append(pe)
            
            self.customer_app_event_producer.publish_parking_event(customer_id=cust, parking_event=pe)
            if pe.event_type == 'entry':
                self.parking_state[pe.car_number] = pe.timestamp
            else:
                if pe.car_number in self.parking_state.keys():
                    entry_time = self.parking_state.get(pe.car_number)
                    exit_time = details.get('timestamp')
                    entry_time_df = dateutil.parser.isoparse(entry_time)
                    exit_time_df = dateutil.parser.isoparse(exit_time)
                    parking_duration_in_secs = self.calculate_parking_duration_in_seconds(entry_time_df, exit_time_df)
                    cost = round(parking_duration_in_secs / 3600 * cost_per_hour)
                    
                    be = BillingEvent(customer_id=cust, car_number=details.get('car_number'), entry_time=entry_time, exit_time=exit_time, parking_cost=cost)

                    self.billing_event_producer.publish(be)

                    self.customer_app_event_producer.publish_billing_event(be)

                    item_popped = self.parking_state.pop(pe.car_number)
                    
    # Utility function to get the customer_id from a parking event
    def get_customer_id_from_parking_event(self, parking_event):
        customer_id = [customer_id for customer_id, car_number in customers_database.items()
                       if parking_event.car_number == car_number]
        if len(customer_id) is 0:
            xprint("{}: Customer Id for car number {} Not found".format(self.worker_id, parking_event.car_number))
            return None
        return customer_id[0]

    # Utility function to get the time difference in seconds
    def calculate_parking_duration_in_seconds(self, entry_time, exit_time):
        timedelta = (exit_time - entry_time).total_seconds()
        return timedelta

    def start_consuming(self):
        # To implement - Start consuming from Rabbit
        self.channel.basic_consume(self.queue, on_message_callback=self.handle_parking_event)
        self.channel.start_consuming()

    def close(self):
        # Do not edit this method
        try:
            xprint("Closing worker with id = {}".format(self.worker_id))
            self.channel.stop_consuming()
            time.sleep(1)
            self.channel.close()
            self.billing_event_producer.close()
            self.customer_app_event_producer.close()
            time.sleep(1)
            self.connection.close()
        except Exception as e:
            print("Exception {} when closing worker with id = {}".format(e, self.worker_id))


class BillingEventProducer:

    def __init__(self, connection, worker_id):
        # Do not edit the init method.
        self.worker_id = worker_id
        # Reusing connection created in ParkingWorker
        self.channel = connection.channel()
        xprint('Billing Event Producer: __init__: worker_id = {}'.format(self.worker_id))

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMq connection, channel, exchange and queue here
        xprint("BillingEventProducer {}: initialize_rabbitmq() called".format(self.worker_id))
        self.channel.queue_declare('billing_events')

    def publish(self, billing_event):
        xprint("BillingEventProducer {}: Publishing billing event {}".format(
            self.worker_id,
            vars(billing_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(billing_event)) to convert the parking_event object to JSON
        self.channel.basic_publish(exchange='', routing_key='billing_events', body=json.dumps(vars(billing_event)))

    def close(self):
        # Do not edit this method
        self.channel.close()


class CustomerEventProducer:

    def __init__(self, connection, worker_id):
        # Do not edit the init method.
        self.worker_id = worker_id
        # Reusing connection created in ParkingWorker
        self.channel = connection.channel()
        self.connection = connection

    def initialize_rabbitmq(self):
        # To implement - Initialize the RabbitMq connection, channel, exchange and queue here
        xprint("CustomerEventProducer {}: initialize_rabbitmq() called".format(self.worker_id))
        self.channel.exchange_declare('customer_app_events', exchange_type='topic')

    def publish_billing_event(self, billing_event):
        xprint("{}: CustomerEventProducer: Publishing billing event {}"
              .format(self.worker_id, vars(billing_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(billing_event)) to convert the parking_event object to JSON
        self.channel.basic_publish(exchange='customer_app_events', routing_key=billing_event.customer_id, body=json.dumps(vars(billing_event)))

    def publish_parking_event(self, customer_id, parking_event):
        xprint("{}: CustomerEventProducer: Publishing parking event {} {}"
              .format(self.worker_id, customer_id, vars(parking_event)))
        # To implement - publish a message to the Rabbitmq here
        # Use json.dumps(vars(parking_event)) to convert the parking_event object to JSON
        self.channel.basic_publish(exchange='customer_app_events', routing_key=customer_id, body=json.dumps(vars(parking_event)))

    def close(self):
        # Do not edit this method
        self.channel.close()
