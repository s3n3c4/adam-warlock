import json
import pytest

from aws_cdk import core
from hello-app.hello_app_stack import HelloAppStack


def get_template():
    app = core.App()
    HelloAppStack(app, "hello-app")
    return json.dumps(app.synth().get_stack("hello-app").template)


def test_sqs_queue_created():
    assert("AWS::SQS::Queue" in get_template())


def test_sns_topic_created():
    assert("AWS::SNS::Topic" in get_template())
