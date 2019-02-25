import time

from locust import events
from sqlalchemy import create_engine
from sqlalchemy.engine import url
from sqlalchemy import event
from argparse import ArgumentParser


class PostgresClient:

    # def __init__(self, host, port, dbname, user, password,
    #              request_type='pg8000', pool_size=1, max_overflow=0):
    def __init__(self, connection_string, request_type='pg8000'):
        self.request_type = request_type

        self.engine = create_engine(connection_string)
        # self.engine = create_engine(url.URL(**database_connection_params),
        #                             pool_size=pool_size, max_overflow=max_overflow,
        #                             isolation_level="AUTOCOMMIT"
        #                             )

    # def __handle_success(self, *arguments, **kwargs):
    #     end_time = time.time()
    #     elapsed_time = int((end_time - kwargs["start_time"]) * 1000)
    #     try:
    #         record_metadata = kwargs["future"].get(timeout=1)
    #
    #         request_data = dict(request_type="send",
    #                             name=record_metadata.topic,
    #                             response_time=elapsed_time,
    #                             response_length=record_metadata.serialized_value_size)
    #
    #         self.__fire_success(**request_data)
    #     except Exception as ex:
    #         print("Logging the exception : {0}".format(ex))
    #         raise  # ??
    #
    # def __handle_failure(self, *arguments, **kwargs):
    #     print("failure " + str(locals()))
    #     end_time = time.time()
    #     elapsed_time = int((end_time - kwargs["start_time"]) * 1000)
    #
    #     request_data = dict(request_type="send", name=kwargs["topic"], response_time=elapsed_time,
    #                         exception=arguments[0])
    #
    #     self.__fire_failure(**request_data)
    #
    # def __fire_failure(self, **kwargs):
    #     events.request_failure.fire(**kwargs)
    #
    # def __fire_success(self, **kwargs):
    #     events.request_success.fire(**kwargs)

    def send(self, name, query, values=None):
        start_time = time.time()
        try:
            result = self.engine.execute(query, values)
            # self.__handle_success(start_time, future = future)
            total_time = int((time.time() - start_time) * 1000)
            events.request_success.fire(request_type=self.request_type, name=name, response_time=total_time,
                                        response_length=len(str(result)))
            return result
        except Exception as e:
            print('Exception occurred: ' + str(e))
            # self.__handle_failure(start_time=start_time, topic=topic)
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type=self.request_type, name=name, response_time=total_time,
                                        exception=e)
            # future.add_callback(self.__handle_success, start_time=start_time, future=future)
            # future.add_errback(self.__handle_failure, start_time=start_time, topic=topic)

    def finalize(self):
        print("flushing the messages")
        # self.producer.flush(timeout=5)
        print("flushing finished")
