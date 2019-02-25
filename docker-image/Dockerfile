FROM grubykarol/locust

RUN apk update \
    && apk add libpq postgresql-dev \
    && apk add build-base

RUN easy_install pip
# Add the licenses for third party software and libraries
ADD licenses /licenses

# Add the external tasks directory into /tasks
ADD locust-tasks /locust-tasks

# Install the required dependencies via pip
RUN pip install --upgrade pip && pip install -r /locust-tasks/requirements.txt

ENV ATTACKED_HOST "http://kafka"
