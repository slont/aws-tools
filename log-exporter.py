#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import boto3
import time
from datetime import datetime

client = None


class Client:
    def __init__(self, profile, log_group, start_at):
        self.client = boto3.Session(profile_name=profile).client('logs')
        self.log_group = log_group
        self.start_at = start_at

    def find_events(self):
        streams = [stream['logStreamName'] for stream in self.find_streams()]
        events = []
        for stream in streams:
            events.extend(self.find_event(stream, None, None))
        return events

    def find_streams(self, token=None):
        if token is None:
            data = self.client.describe_log_streams(logGroupName=self.log_group)
        else:
            data = self.client.describe_log_streams(logGroupName=self.log_group, nextToken=token)

        streams = list(filter(self.is_valid_stream, data['logStreams']))
        if 'nextToken' not in data:
            return streams

        # レート制限
        time.sleep(0.5)

        streams.extend(self.find_streams(data['nextToken']))
        return streams

    def find_event(self, stream, token, last_token):
        if token is None:
            data = self.client.get_log_events(logGroupName=self.log_group,
                                              logStreamName=stream,
                                              startFromHead=True)
        else:
            data = self.client.get_log_events(logGroupName=self.log_group,
                                              logStreamName=stream,
                                              startFromHead=True,
                                              nextToken=token)
        event = data['events']

        if data['nextForwardToken'] != last_token:
            # レート制限
            time.sleep(0.5)
            event.extend(self.find_event(stream, data['nextForwardToken'], token))

        return event

    def is_valid_stream(self, stream):
        return self.start_at <= stream.get('lastIngestionTime')


if __name__ == '__main__':
    args = sys.argv

    epoc = datetime(1970, 1, 1)
    start_at = (datetime.strptime(args[3], '%Y-%m-%dT%H:%M:%S') - epoc).total_seconds() * 1000

    client = Client(args[1], args[2], start_at)

    events = client.find_events()
    events = sorted(events, key=lambda e: e['timestamp'])
    for e in events:
        print('[%s] %s' % (
            datetime.fromtimestamp(e['timestamp'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f'), e['message']))
