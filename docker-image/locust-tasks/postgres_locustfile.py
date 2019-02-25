import os
import random
import string
import uuid
from datetime import datetime

from locust import TaskSet, task, events, Locust

from additional_handlers import additional_success_handler, additional_failure_handler
from postgres_client import PostgresClient

WORK_DIR = os.path.dirname(__file__)

# read kafka brokers from config
POSTGRES_CONNECTION_STRING = os.getenv("POSTGRES_CONNECTION_STRING", "postgres://postgres:mysecretpassword@localhost:5432/postgres")

# read other environment variables
QUIET_MODE = True if os.getenv("QUIET_MODE", "true").lower() in ['1', 'true', 'yes'] else False
TASK_DELAY = int(os.getenv("TASK_DELAY", "5000"))

# register additional logging handlers
if not QUIET_MODE:
    events.request_success += additional_success_handler
    events.request_failure += additional_failure_handler


class PostgresLocust(Locust):
    client = None

    def __init__(self, *args, **kwargs):
        super(PostgresLocust, self).__init__(*args, **kwargs)
        if not PostgresLocust.client:
            PostgresLocust.client = PostgresClient(POSTGRES_CONNECTION_STRING)


class PostgresBehaviour(TaskSet):
    _device_id = None

    def on_start(self):
        self._device_id = str(uuid.uuid4())

    def random_message(self, min_length=32, max_length=128):
        return ''.join(random.choice(string.ascii_uppercase) for _ in range(random.randrange(min_length, max_length)))

    def timestamped_message(self):
        time_str = datetime.now().strftime("%m-%d-%Y, %H:%M:%S")
        return time_str + ":" + ("MSG " * 24)[:random.randint(32, 128)]

    @task
    def send_msg1(self):
        # self.client.send("test", message=self.timestamped_message())
        self.client.send("select", "SELECT * FROM films")

    @task
    def send_msg2(self):
        # self.client.send("test", message=self.timestamped_message())
        self.client.send("insert", "INSERT INTO films (title, director, year) VALUES ('Doctor Strange', 'Scott Derrickson', '2016')")
    # @task(10)
    # def send_msg2(self):
    #     self.client.send("test", message=self.timestamped_message(), key="key")


class PostgresActivitiesLocust(PostgresLocust):
    """
    Locust user class that pushes messages to Kafka
    """
    task_set = PostgresBehaviour
    min_wait = TASK_DELAY
    max_wait = TASK_DELAY
