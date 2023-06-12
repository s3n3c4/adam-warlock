#!/usr/bin/env python3

from aws_cdk import core

from hello_app.hello_app_stack import HelloAppStack


app = core.App()
HelloAppStack(app, "hello-app", env={'region': 'us-west-2'})

app.synth()
