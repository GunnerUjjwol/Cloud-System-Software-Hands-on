import datetime
import sys
# Update to path where your code is
sys.path.append('../')

from db_and_event_definitions import ParkingEvent
from parking_sensor import ParkingEventProducer
from worker import *
import argparse


def get_date_with_delta(minutes):
    d = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)
    return d.isoformat("T")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Send entry or exit parking event message")
    parser.add_argument('--event', '-e', type=str.lower,
                        choices=['entry', 'exit'],
                        help="Type of event")
    parser.add_argument('--customer_id', '-c', type=str.lower,
                        choices=customers_database.keys(),
                        help="Customer ID")
    parser.add_argument('--timeoffset', '-t', type=int,
                        help='Number of minutes to add to current timestamp',
                        default=0)
    args = parser.parse_args()

    parking_event_producer = ParkingEventProducer()
    parking_event_producer.initialize_rabbitmq()
    parking_event = ParkingEvent(args.event,
                                 customers_database[args.customer_id], # sending car number plate
                                 get_date_with_delta(args.timeoffset)
                                 )
    parking_event_producer.publish(parking_event)
    parking_event_producer.close()
