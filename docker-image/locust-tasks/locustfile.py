import os
import random
import string
import time
import uuid
from datetime import datetime

from locust import TaskSet, task, events, Locust, HttpLocust

from additional_handlers import additional_success_handler, additional_failure_handler
from kafka_client import KafkaClient

WORK_DIR = os.path.dirname(__file__)

# read kafka brokers from config
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "kafka:9092").split(",")

# read other environment variables
QUIET_MODE = True if os.getenv("QUIET_MODE", "true").lower() in ['1', 'true', 'yes'] else False
TASK_DELAY = int(os.getenv("TASK_DELAY", "5000"))

# register additional logging handlers
if not QUIET_MODE:
    events.request_success += additional_success_handler
    events.request_failure += additional_failure_handler


class KafkaLocust(Locust):
    client = None

    def __init__(self, *args, **kwargs):
        super(KafkaLocust, self).__init__(*args, **kwargs)
        if not KafkaLocust.client:
            KafkaLocust.client = KafkaClient(KAFKA_BROKERS)


class KafkaBehaviour(TaskSet):
    _device_id = None

    def on_start(self):
        self._device_id = str(uuid.uuid4())

    def random_message(self, min_length=32, max_length=128):
        return ''.join(random.choice(string.ascii_uppercase) for _ in range(random.randrange(min_length, max_length)))

    def timestamped_message(self):
        time_str = datetime.now().strftime("%m-%d-%Y, %H:%M:%S")
        return time_str + ":" + ("MSG " * 24)[:random.randint(32, 128)]

    @task(1)
    def send_msg(self):
        self.client.send("test", message=self.timestamped_message())

    # @task(10)
    # def send_msg2(self):
    #     self.client.send("test", message=self.timestamped_message(), key="key")


class KafkaActivitiesLocust(KafkaLocust):
    """
    Locust user class that pushes messages to Kafka
    """
    task_set = KafkaBehaviour
    min_wait = TASK_DELAY
    max_wait = TASK_DELAY
