'''
# CDK Construct Library for Amazon Simple Notification Service Subscriptions

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

This library provides constructs for adding subscriptions to an Amazon SNS topic.
Subscriptions can be added by calling the `.addSubscription(...)` method on the topic.

## Subscriptions

Subscriptions can be added to the following endpoints:

* HTTPS
* Amazon SQS
* AWS Lambda
* Email
* SMS

Subscriptions to Amazon SQS and AWS Lambda can be added on topics across regions.

Create an Amazon SNS Topic to add subscriptions.

```python
my_topic = sns.Topic(self, "MyTopic")
```

### HTTPS

Add an HTTP or HTTPS Subscription to your topic:

```python
my_topic = sns.Topic(self, "MyTopic")

my_topic.add_subscription(subscriptions.UrlSubscription("https://foobar.com/"))
```

The URL being subscribed can also be [tokens](https://docs.aws.amazon.com/cdk/latest/guide/tokens.html), that resolve
to a URL during deployment. A typical use case is when the URL is passed in as a [CloudFormation
parameter](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html). The
following code defines a CloudFormation parameter and uses it in a URL subscription.

```python
my_topic = sns.Topic(self, "MyTopic")
url = CfnParameter(self, "url-param")

my_topic.add_subscription(subscriptions.UrlSubscription(url.value_as_string))
```

### Amazon SQS

Subscribe a queue to your topic:

```python
my_queue = sqs.Queue(self, "MyQueue")
my_topic = sns.Topic(self, "MyTopic")

my_topic.add_subscription(subscriptions.SqsSubscription(my_queue))
```

KMS key permissions will automatically be granted to SNS when a subscription is made to
an encrypted queue.

Note that subscriptions of queues in different accounts need to be manually confirmed by
reading the initial message from the queue and visiting the link found in it.

### AWS Lambda

Subscribe an AWS Lambda function to your topic:

```python
import aws_cdk.aws_lambda as lambda_
# my_function: lambda.Function


my_topic = sns.Topic(self, "myTopic")
my_topic.add_subscription(subscriptions.LambdaSubscription(my_function))
```

### Email

Subscribe an email address to your topic:

```python
my_topic = sns.Topic(self, "MyTopic")
my_topic.add_subscription(subscriptions.EmailSubscription("foo@bar.com"))
```

The email being subscribed can also be [tokens](https://docs.aws.amazon.com/cdk/latest/guide/tokens.html), that resolve
to an email address during deployment. A typical use case is when the email address is passed in as a [CloudFormation
parameter](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html). The
following code defines a CloudFormation parameter and uses it in an email subscription.

```python
my_topic = sns.Topic(self, "Topic")
email_address = CfnParameter(self, "email-param")

my_topic.add_subscription(subscriptions.EmailSubscription(email_address.value_as_string))
```

Note that email subscriptions require confirmation by visiting the link sent to the
email address.

### SMS

Subscribe an sms number to your topic:

```python
my_topic = sns.Topic(self, "Topic")

my_topic.add_subscription(subscriptions.SmsSubscription("+15551231234"))
```

The number being subscribed can also be [tokens](https://docs.aws.amazon.com/cdk/latest/guide/tokens.html), that resolve
to a number during deployment. A typical use case is when the number is passed in as a [CloudFormation
parameter](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html). The
following code defines a CloudFormation parameter and uses it in an sms subscription.

```python
my_topic = sns.Topic(self, "Topic")
sms_number = CfnParameter(self, "sms-param")

my_topic.add_subscription(subscriptions.SmsSubscription(sms_number.value_as_string))
```
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_5443dbc3
import aws_cdk.aws_sns as _aws_cdk_aws_sns_889c7272
import aws_cdk.aws_sqs as _aws_cdk_aws_sqs_48bffef9


@jsii.implements(_aws_cdk_aws_sns_889c7272.ITopicSubscription)
class EmailSubscription(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-sns-subscriptions.EmailSubscription",
):
    '''Use an email address as a subscription target.

    Email subscriptions require confirmation.

    :exampleMetadata: infused

    Example::

        my_topic = sns.Topic(self, "Topic")
        email_address = CfnParameter(self, "email-param")
        
        my_topic.add_subscription(subscriptions.EmailSubscription(email_address.value_as_string))
    '''

    def __init__(
        self,
        email_address: builtins.str,
        *,
        json: typing.Optional[builtins.bool] = None,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
        filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
    ) -> None:
        '''
        :param email_address: -
        :param json: Indicates if the full notification JSON should be sent to the email address or just the message text. Default: false (Message text)
        :param dead_letter_queue: Queue to be used as dead letter queue. If not passed no dead letter queue is enabled. Default: - No dead letter queue enabled.
        :param filter_policy: The filter policy. Default: - all messages are delivered
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66bf6df28f3509479122a4a6cf116ede9475d591d0694d21af87f897f1901e0a)
            check_type(argname="argument email_address", value=email_address, expected_type=type_hints["email_address"])
        props = EmailSubscriptionProps(
            json=json, dead_letter_queue=dead_letter_queue, filter_policy=filter_policy
        )

        jsii.create(self.__class__, self, [email_address, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _topic: _aws_cdk_aws_sns_889c7272.ITopic,
    ) -> _aws_cdk_aws_sns_889c7272.TopicSubscriptionConfig:
        '''Returns a configuration for an email address to subscribe to an SNS topic.

        :param _topic: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__842fd663e00fc30c6d1498c868ae256fc997cb87c8c23c641205c4b3e7c9101a)
            check_type(argname="argument _topic", value=_topic, expected_type=type_hints["_topic"])
        return typing.cast(_aws_cdk_aws_sns_889c7272.TopicSubscriptionConfig, jsii.invoke(self, "bind", [_topic]))


@jsii.implements(_aws_cdk_aws_sns_889c7272.ITopicSubscription)
class LambdaSubscription(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-sns-subscriptions.LambdaSubscription",
):
    '''Use a Lambda function as a subscription target.

    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_lambda as lambda_
        # fn: lambda.Function
        
        
        my_topic = sns.Topic(self, "MyTopic")
        
        # Lambda should receive only message matching the following conditions on attributes:
        # color: 'red' or 'orange' or begins with 'bl'
        # size: anything but 'small' or 'medium'
        # price: between 100 and 200 or greater than 300
        # store: attribute must be present
        my_topic.add_subscription(subscriptions.LambdaSubscription(fn,
            filter_policy={
                "color": sns.SubscriptionFilter.string_filter(
                    allowlist=["red", "orange"],
                    match_prefixes=["bl"]
                ),
                "size": sns.SubscriptionFilter.string_filter(
                    denylist=["small", "medium"]
                ),
                "price": sns.SubscriptionFilter.numeric_filter(
                    between=sns.BetweenCondition(start=100, stop=200),
                    greater_than=300
                ),
                "store": sns.SubscriptionFilter.exists_filter()
            }
        ))
    '''

    def __init__(
        self,
        fn: _aws_cdk_aws_lambda_5443dbc3.IFunction,
        *,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
        filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
    ) -> None:
        '''
        :param fn: -
        :param dead_letter_queue: Queue to be used as dead letter queue. If not passed no dead letter queue is enabled. Default: - No dead letter queue enabled.
        :param filter_policy: The filter policy. Default: - all messages are delivered
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83d259e3e187dba7bd835379d97fd66d68d22b95510aac2b80556503f0456897)
            check_type(argname="argument fn", value=fn, expected_type=type_hints["fn"])
        props = LambdaSubscriptionProps(
            dead_letter_queue=dead_letter_queue, filter_policy=filter_policy
        )

        jsii.create(self.__class__, self, [fn, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        topic: _aws_cdk_aws_sns_889c7272.ITopic,
    ) -> _aws_cdk_aws_sns_889c7272.TopicSubscriptionConfig:
        '''Returns a configuration for a Lambda function to subscribe to an SNS topic.

        :param topic: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c75cb1cf97d7f154b95818c7e0d898885682028e63de0dfb7a4964a7e2cf901)
            check_type(argname="argument topic", value=topic, expected_type=type_hints["topic"])
        return typing.cast(_aws_cdk_aws_sns_889c7272.TopicSubscriptionConfig, jsii.invoke(self, "bind", [topic]))


@jsii.implements(_aws_cdk_aws_sns_889c7272.ITopicSubscription)
class SmsSubscription(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-sns-subscriptions.SmsSubscription",
):
    '''Use an sms address as a subscription target.

    :exampleMetadata: infused

    Example::

        my_topic = sns.Topic(self, "Topic")
        
        my_topic.add_subscription(subscriptions.SmsSubscription("+15551231234"))
    '''

    def __init__(
        self,
        phone_number: builtins.str,
        *,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
        filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
    ) -> None:
        '''
        :param phone_number: -
        :param dead_letter_queue: Queue to be used as dead letter queue. If not passed no dead letter queue is enabled. Default: - No dead letter queue enabled.
        :param filter_policy: The filter policy. Default: - all messages are delivered
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e24075f8f517f3fa10950e05d0c1c001e5712cba1bc5a316333561dcfc5639d2)
            check_type(argname="argument phone_number", value=phone_number, expected_type=type_hints["phone_number"])
        props = SmsSubscriptionProps(
            dead_letter_queue=dead_letter_queue, filter_policy=filter_policy
        )

        jsii.create(self.__class__, self, [phone_number, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _topic: _aws_cdk_aws_sns_889c7272.ITopic,
    ) -> _aws_cdk_aws_sns_889c7272.TopicSubscriptionConfig:
        '''Returns a configuration used to subscribe to an SNS topic.

        :param _topic: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e5f240130a5fe542ca1346c2899f4ea0de9179b289e1abee42fc204d155e4b3)
            check_type(argname="argument _topic", value=_topic, expected_type=type_hints["_topic"])
        return typing.cast(_aws_cdk_aws_sns_889c7272.TopicSubscriptionConfig, jsii.invoke(self, "bind", [_topic]))


@jsii.implements(_aws_cdk_aws_sns_889c7272.ITopicSubscription)
class SqsSubscription(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-sns-subscriptions.SqsSubscription",
):
    '''Use an SQS queue as a subscription target.

    :exampleMetadata: infused

    Example::

        # queue: sqs.Queue
        
        my_topic = sns.Topic(self, "MyTopic")
        
        my_topic.add_subscription(subscriptions.SqsSubscription(queue))
    '''

    def __init__(
        self,
        queue: _aws_cdk_aws_sqs_48bffef9.IQueue,
        *,
        raw_message_delivery: typing.Optional[builtins.bool] = None,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
        filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
    ) -> None:
        '''
        :param queue: -
        :param raw_message_delivery: The message to the queue is the same as it was sent to the topic. If false, the message will be wrapped in an SNS envelope. Default: false
        :param dead_letter_queue: Queue to be used as dead letter queue. If not passed no dead letter queue is enabled. Default: - No dead letter queue enabled.
        :param filter_policy: The filter policy. Default: - all messages are delivered
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bce12291b35c5fa7100c5a75ef998119e6b788a8e3f19a0c5fe47ceebb39cd6d)
            check_type(argname="argument queue", value=queue, expected_type=type_hints["queue"])
        props = SqsSubscriptionProps(
            raw_message_delivery=raw_message_delivery,
            dead_letter_queue=dead_letter_queue,
            filter_policy=filter_policy,
        )

        jsii.create(self.__class__, self, [queue, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        topic: _aws_cdk_aws_sns_889c7272.ITopic,
    ) -> _aws_cdk_aws_sns_889c7272.TopicSubscriptionConfig:
        '''Returns a configuration for an SQS queue to subscribe to an SNS topic.

        :param topic: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80a3f4950b19902f259b6d2ba12e9f27428af228aa6064c8c4bbc2832e11807b)
            check_type(argname="argument topic", value=topic, expected_type=type_hints["topic"])
        return typing.cast(_aws_cdk_aws_sns_889c7272.TopicSubscriptionConfig, jsii.invoke(self, "bind", [topic]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-sns-subscriptions.SubscriptionProps",
    jsii_struct_bases=[],
    name_mapping={
        "dead_letter_queue": "deadLetterQueue",
        "filter_policy": "filterPolicy",
    },
)
class SubscriptionProps:
    def __init__(
        self,
        *,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
        filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
    ) -> None:
        '''Options to subscribing to an SNS topic.

        :param dead_letter_queue: Queue to be used as dead letter queue. If not passed no dead letter queue is enabled. Default: - No dead letter queue enabled.
        :param filter_policy: The filter policy. Default: - all messages are delivered

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_sns as sns
            import aws_cdk.aws_sns_subscriptions as sns_subscriptions
            import aws_cdk.aws_sqs as sqs
            
            # queue: sqs.Queue
            # subscription_filter: sns.SubscriptionFilter
            
            subscription_props = sns_subscriptions.SubscriptionProps(
                dead_letter_queue=queue,
                filter_policy={
                    "filter_policy_key": subscription_filter
                }
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f733132ec2f29cc503ba4b375f9c6092baf6d8b42858216cd2c120e487cb5e8)
            check_type(argname="argument dead_letter_queue", value=dead_letter_queue, expected_type=type_hints["dead_letter_queue"])
            check_type(argname="argument filter_policy", value=filter_policy, expected_type=type_hints["filter_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dead_letter_queue is not None:
            self._values["dead_letter_queue"] = dead_letter_queue
        if filter_policy is not None:
            self._values["filter_policy"] = filter_policy

    @builtins.property
    def dead_letter_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue]:
        '''Queue to be used as dead letter queue.

        If not passed no dead letter queue is enabled.

        :default: - No dead letter queue enabled.
        '''
        result = self._values.get("dead_letter_queue")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue], result)

    @builtins.property
    def filter_policy(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]]:
        '''The filter policy.

        :default: - all messages are delivered
        '''
        result = self._values.get("filter_policy")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SubscriptionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_aws_sns_889c7272.ITopicSubscription)
class UrlSubscription(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-sns-subscriptions.UrlSubscription",
):
    '''Use a URL as a subscription target.

    The message will be POSTed to the given URL.

    :see: https://docs.aws.amazon.com/sns/latest/dg/sns-http-https-endpoint-as-subscriber.html
    :exampleMetadata: infused

    Example::

        my_topic = sns.Topic(self, "MyTopic")
        
        my_topic.add_subscription(subscriptions.UrlSubscription("https://foobar.com/"))
    '''

    def __init__(
        self,
        url: builtins.str,
        *,
        protocol: typing.Optional[_aws_cdk_aws_sns_889c7272.SubscriptionProtocol] = None,
        raw_message_delivery: typing.Optional[builtins.bool] = None,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
        filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
    ) -> None:
        '''
        :param url: -
        :param protocol: The subscription's protocol. Default: - Protocol is derived from url
        :param raw_message_delivery: The message to the queue is the same as it was sent to the topic. If false, the message will be wrapped in an SNS envelope. Default: false
        :param dead_letter_queue: Queue to be used as dead letter queue. If not passed no dead letter queue is enabled. Default: - No dead letter queue enabled.
        :param filter_policy: The filter policy. Default: - all messages are delivered
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8cfd8a596d1b2d35304c1ca2ebccc875ae4c3d3df4749b2e576cf416f277a07)
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
        props = UrlSubscriptionProps(
            protocol=protocol,
            raw_message_delivery=raw_message_delivery,
            dead_letter_queue=dead_letter_queue,
            filter_policy=filter_policy,
        )

        jsii.create(self.__class__, self, [url, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _topic: _aws_cdk_aws_sns_889c7272.ITopic,
    ) -> _aws_cdk_aws_sns_889c7272.TopicSubscriptionConfig:
        '''Returns a configuration for a URL to subscribe to an SNS topic.

        :param _topic: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f415e4ca3a8db6da2655810994e67ee8003f866eae535dd4e40cc8d697b6a842)
            check_type(argname="argument _topic", value=_topic, expected_type=type_hints["_topic"])
        return typing.cast(_aws_cdk_aws_sns_889c7272.TopicSubscriptionConfig, jsii.invoke(self, "bind", [_topic]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-sns-subscriptions.UrlSubscriptionProps",
    jsii_struct_bases=[SubscriptionProps],
    name_mapping={
        "dead_letter_queue": "deadLetterQueue",
        "filter_policy": "filterPolicy",
        "protocol": "protocol",
        "raw_message_delivery": "rawMessageDelivery",
    },
)
class UrlSubscriptionProps(SubscriptionProps):
    def __init__(
        self,
        *,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
        filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
        protocol: typing.Optional[_aws_cdk_aws_sns_889c7272.SubscriptionProtocol] = None,
        raw_message_delivery: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Options for URL subscriptions.

        :param dead_letter_queue: Queue to be used as dead letter queue. If not passed no dead letter queue is enabled. Default: - No dead letter queue enabled.
        :param filter_policy: The filter policy. Default: - all messages are delivered
        :param protocol: The subscription's protocol. Default: - Protocol is derived from url
        :param raw_message_delivery: The message to the queue is the same as it was sent to the topic. If false, the message will be wrapped in an SNS envelope. Default: false

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_sns as sns
            import aws_cdk.aws_sns_subscriptions as sns_subscriptions
            import aws_cdk.aws_sqs as sqs
            
            # queue: sqs.Queue
            # subscription_filter: sns.SubscriptionFilter
            
            url_subscription_props = sns_subscriptions.UrlSubscriptionProps(
                dead_letter_queue=queue,
                filter_policy={
                    "filter_policy_key": subscription_filter
                },
                protocol=sns.SubscriptionProtocol.HTTP,
                raw_message_delivery=False
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f51a649a8dfc2e7a670860f5185bdfa6826e2eb15735e95342c5852f63c5965d)
            check_type(argname="argument dead_letter_queue", value=dead_letter_queue, expected_type=type_hints["dead_letter_queue"])
            check_type(argname="argument filter_policy", value=filter_policy, expected_type=type_hints["filter_policy"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument raw_message_delivery", value=raw_message_delivery, expected_type=type_hints["raw_message_delivery"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dead_letter_queue is not None:
            self._values["dead_letter_queue"] = dead_letter_queue
        if filter_policy is not None:
            self._values["filter_policy"] = filter_policy
        if protocol is not None:
            self._values["protocol"] = protocol
        if raw_message_delivery is not None:
            self._values["raw_message_delivery"] = raw_message_delivery

    @builtins.property
    def dead_letter_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue]:
        '''Queue to be used as dead letter queue.

        If not passed no dead letter queue is enabled.

        :default: - No dead letter queue enabled.
        '''
        result = self._values.get("dead_letter_queue")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue], result)

    @builtins.property
    def filter_policy(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]]:
        '''The filter policy.

        :default: - all messages are delivered
        '''
        result = self._values.get("filter_policy")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]], result)

    @builtins.property
    def protocol(
        self,
    ) -> typing.Optional[_aws_cdk_aws_sns_889c7272.SubscriptionProtocol]:
        '''The subscription's protocol.

        :default: - Protocol is derived from url
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_889c7272.SubscriptionProtocol], result)

    @builtins.property
    def raw_message_delivery(self) -> typing.Optional[builtins.bool]:
        '''The message to the queue is the same as it was sent to the topic.

        If false, the message will be wrapped in an SNS envelope.

        :default: false
        '''
        result = self._values.get("raw_message_delivery")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UrlSubscriptionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-sns-subscriptions.EmailSubscriptionProps",
    jsii_struct_bases=[SubscriptionProps],
    name_mapping={
        "dead_letter_queue": "deadLetterQueue",
        "filter_policy": "filterPolicy",
        "json": "json",
    },
)
class EmailSubscriptionProps(SubscriptionProps):
    def __init__(
        self,
        *,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
        filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
        json: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Options for email subscriptions.

        :param dead_letter_queue: Queue to be used as dead letter queue. If not passed no dead letter queue is enabled. Default: - No dead letter queue enabled.
        :param filter_policy: The filter policy. Default: - all messages are delivered
        :param json: Indicates if the full notification JSON should be sent to the email address or just the message text. Default: false (Message text)

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_sns as sns
            import aws_cdk.aws_sns_subscriptions as sns_subscriptions
            import aws_cdk.aws_sqs as sqs
            
            # queue: sqs.Queue
            # subscription_filter: sns.SubscriptionFilter
            
            email_subscription_props = sns_subscriptions.EmailSubscriptionProps(
                dead_letter_queue=queue,
                filter_policy={
                    "filter_policy_key": subscription_filter
                },
                json=False
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__800bf06002be22a53c168e41524e42eeb57e06da500371468479d127abea9b4a)
            check_type(argname="argument dead_letter_queue", value=dead_letter_queue, expected_type=type_hints["dead_letter_queue"])
            check_type(argname="argument filter_policy", value=filter_policy, expected_type=type_hints["filter_policy"])
            check_type(argname="argument json", value=json, expected_type=type_hints["json"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dead_letter_queue is not None:
            self._values["dead_letter_queue"] = dead_letter_queue
        if filter_policy is not None:
            self._values["filter_policy"] = filter_policy
        if json is not None:
            self._values["json"] = json

    @builtins.property
    def dead_letter_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue]:
        '''Queue to be used as dead letter queue.

        If not passed no dead letter queue is enabled.

        :default: - No dead letter queue enabled.
        '''
        result = self._values.get("dead_letter_queue")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue], result)

    @builtins.property
    def filter_policy(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]]:
        '''The filter policy.

        :default: - all messages are delivered
        '''
        result = self._values.get("filter_policy")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]], result)

    @builtins.property
    def json(self) -> typing.Optional[builtins.bool]:
        '''Indicates if the full notification JSON should be sent to the email address or just the message text.

        :default: false (Message text)
        '''
        result = self._values.get("json")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmailSubscriptionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-sns-subscriptions.LambdaSubscriptionProps",
    jsii_struct_bases=[SubscriptionProps],
    name_mapping={
        "dead_letter_queue": "deadLetterQueue",
        "filter_policy": "filterPolicy",
    },
)
class LambdaSubscriptionProps(SubscriptionProps):
    def __init__(
        self,
        *,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
        filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
    ) -> None:
        '''Properties for a Lambda subscription.

        :param dead_letter_queue: Queue to be used as dead letter queue. If not passed no dead letter queue is enabled. Default: - No dead letter queue enabled.
        :param filter_policy: The filter policy. Default: - all messages are delivered

        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_lambda as lambda_
            # fn: lambda.Function
            
            
            my_topic = sns.Topic(self, "MyTopic")
            
            # Lambda should receive only message matching the following conditions on attributes:
            # color: 'red' or 'orange' or begins with 'bl'
            # size: anything but 'small' or 'medium'
            # price: between 100 and 200 or greater than 300
            # store: attribute must be present
            my_topic.add_subscription(subscriptions.LambdaSubscription(fn,
                filter_policy={
                    "color": sns.SubscriptionFilter.string_filter(
                        allowlist=["red", "orange"],
                        match_prefixes=["bl"]
                    ),
                    "size": sns.SubscriptionFilter.string_filter(
                        denylist=["small", "medium"]
                    ),
                    "price": sns.SubscriptionFilter.numeric_filter(
                        between=sns.BetweenCondition(start=100, stop=200),
                        greater_than=300
                    ),
                    "store": sns.SubscriptionFilter.exists_filter()
                }
            ))
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e56dd01cd9e94b0dd3281370319ba556eebc5528f146f5f5fdd9eebfbe5ad95)
            check_type(argname="argument dead_letter_queue", value=dead_letter_queue, expected_type=type_hints["dead_letter_queue"])
            check_type(argname="argument filter_policy", value=filter_policy, expected_type=type_hints["filter_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dead_letter_queue is not None:
            self._values["dead_letter_queue"] = dead_letter_queue
        if filter_policy is not None:
            self._values["filter_policy"] = filter_policy

    @builtins.property
    def dead_letter_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue]:
        '''Queue to be used as dead letter queue.

        If not passed no dead letter queue is enabled.

        :default: - No dead letter queue enabled.
        '''
        result = self._values.get("dead_letter_queue")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue], result)

    @builtins.property
    def filter_policy(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]]:
        '''The filter policy.

        :default: - all messages are delivered
        '''
        result = self._values.get("filter_policy")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaSubscriptionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-sns-subscriptions.SmsSubscriptionProps",
    jsii_struct_bases=[SubscriptionProps],
    name_mapping={
        "dead_letter_queue": "deadLetterQueue",
        "filter_policy": "filterPolicy",
    },
)
class SmsSubscriptionProps(SubscriptionProps):
    def __init__(
        self,
        *,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
        filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
    ) -> None:
        '''Options for SMS subscriptions.

        :param dead_letter_queue: Queue to be used as dead letter queue. If not passed no dead letter queue is enabled. Default: - No dead letter queue enabled.
        :param filter_policy: The filter policy. Default: - all messages are delivered

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_sns as sns
            import aws_cdk.aws_sns_subscriptions as sns_subscriptions
            import aws_cdk.aws_sqs as sqs
            
            # queue: sqs.Queue
            # subscription_filter: sns.SubscriptionFilter
            
            sms_subscription_props = sns_subscriptions.SmsSubscriptionProps(
                dead_letter_queue=queue,
                filter_policy={
                    "filter_policy_key": subscription_filter
                }
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce928566c2cb5ee2c01d9b46b709b7a55136424627b6731558e46d63c6c9f8fa)
            check_type(argname="argument dead_letter_queue", value=dead_letter_queue, expected_type=type_hints["dead_letter_queue"])
            check_type(argname="argument filter_policy", value=filter_policy, expected_type=type_hints["filter_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dead_letter_queue is not None:
            self._values["dead_letter_queue"] = dead_letter_queue
        if filter_policy is not None:
            self._values["filter_policy"] = filter_policy

    @builtins.property
    def dead_letter_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue]:
        '''Queue to be used as dead letter queue.

        If not passed no dead letter queue is enabled.

        :default: - No dead letter queue enabled.
        '''
        result = self._values.get("dead_letter_queue")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue], result)

    @builtins.property
    def filter_policy(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]]:
        '''The filter policy.

        :default: - all messages are delivered
        '''
        result = self._values.get("filter_policy")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SmsSubscriptionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-sns-subscriptions.SqsSubscriptionProps",
    jsii_struct_bases=[SubscriptionProps],
    name_mapping={
        "dead_letter_queue": "deadLetterQueue",
        "filter_policy": "filterPolicy",
        "raw_message_delivery": "rawMessageDelivery",
    },
)
class SqsSubscriptionProps(SubscriptionProps):
    def __init__(
        self,
        *,
        dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
        filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
        raw_message_delivery: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Properties for an SQS subscription.

        :param dead_letter_queue: Queue to be used as dead letter queue. If not passed no dead letter queue is enabled. Default: - No dead letter queue enabled.
        :param filter_policy: The filter policy. Default: - all messages are delivered
        :param raw_message_delivery: The message to the queue is the same as it was sent to the topic. If false, the message will be wrapped in an SNS envelope. Default: false

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_sns as sns
            import aws_cdk.aws_sns_subscriptions as sns_subscriptions
            import aws_cdk.aws_sqs as sqs
            
            # queue: sqs.Queue
            # subscription_filter: sns.SubscriptionFilter
            
            sqs_subscription_props = sns_subscriptions.SqsSubscriptionProps(
                dead_letter_queue=queue,
                filter_policy={
                    "filter_policy_key": subscription_filter
                },
                raw_message_delivery=False
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfcc271364229be4712c2a7d415b7b4ef6b058b465f7bfbed4f5aa36e5e98992)
            check_type(argname="argument dead_letter_queue", value=dead_letter_queue, expected_type=type_hints["dead_letter_queue"])
            check_type(argname="argument filter_policy", value=filter_policy, expected_type=type_hints["filter_policy"])
            check_type(argname="argument raw_message_delivery", value=raw_message_delivery, expected_type=type_hints["raw_message_delivery"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dead_letter_queue is not None:
            self._values["dead_letter_queue"] = dead_letter_queue
        if filter_policy is not None:
            self._values["filter_policy"] = filter_policy
        if raw_message_delivery is not None:
            self._values["raw_message_delivery"] = raw_message_delivery

    @builtins.property
    def dead_letter_queue(self) -> typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue]:
        '''Queue to be used as dead letter queue.

        If not passed no dead letter queue is enabled.

        :default: - No dead letter queue enabled.
        '''
        result = self._values.get("dead_letter_queue")
        return typing.cast(typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue], result)

    @builtins.property
    def filter_policy(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]]:
        '''The filter policy.

        :default: - all messages are delivered
        '''
        result = self._values.get("filter_policy")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]], result)

    @builtins.property
    def raw_message_delivery(self) -> typing.Optional[builtins.bool]:
        '''The message to the queue is the same as it was sent to the topic.

        If false, the message will be wrapped in an SNS envelope.

        :default: false
        '''
        result = self._values.get("raw_message_delivery")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SqsSubscriptionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "EmailSubscription",
    "EmailSubscriptionProps",
    "LambdaSubscription",
    "LambdaSubscriptionProps",
    "SmsSubscription",
    "SmsSubscriptionProps",
    "SqsSubscription",
    "SqsSubscriptionProps",
    "SubscriptionProps",
    "UrlSubscription",
    "UrlSubscriptionProps",
]

publication.publish()

def _typecheckingstub__66bf6df28f3509479122a4a6cf116ede9475d591d0694d21af87f897f1901e0a(
    email_address: builtins.str,
    *,
    json: typing.Optional[builtins.bool] = None,
    dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
    filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__842fd663e00fc30c6d1498c868ae256fc997cb87c8c23c641205c4b3e7c9101a(
    _topic: _aws_cdk_aws_sns_889c7272.ITopic,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83d259e3e187dba7bd835379d97fd66d68d22b95510aac2b80556503f0456897(
    fn: _aws_cdk_aws_lambda_5443dbc3.IFunction,
    *,
    dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
    filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c75cb1cf97d7f154b95818c7e0d898885682028e63de0dfb7a4964a7e2cf901(
    topic: _aws_cdk_aws_sns_889c7272.ITopic,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e24075f8f517f3fa10950e05d0c1c001e5712cba1bc5a316333561dcfc5639d2(
    phone_number: builtins.str,
    *,
    dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
    filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e5f240130a5fe542ca1346c2899f4ea0de9179b289e1abee42fc204d155e4b3(
    _topic: _aws_cdk_aws_sns_889c7272.ITopic,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bce12291b35c5fa7100c5a75ef998119e6b788a8e3f19a0c5fe47ceebb39cd6d(
    queue: _aws_cdk_aws_sqs_48bffef9.IQueue,
    *,
    raw_message_delivery: typing.Optional[builtins.bool] = None,
    dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
    filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80a3f4950b19902f259b6d2ba12e9f27428af228aa6064c8c4bbc2832e11807b(
    topic: _aws_cdk_aws_sns_889c7272.ITopic,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f733132ec2f29cc503ba4b375f9c6092baf6d8b42858216cd2c120e487cb5e8(
    *,
    dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
    filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8cfd8a596d1b2d35304c1ca2ebccc875ae4c3d3df4749b2e576cf416f277a07(
    url: builtins.str,
    *,
    protocol: typing.Optional[_aws_cdk_aws_sns_889c7272.SubscriptionProtocol] = None,
    raw_message_delivery: typing.Optional[builtins.bool] = None,
    dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
    filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f415e4ca3a8db6da2655810994e67ee8003f866eae535dd4e40cc8d697b6a842(
    _topic: _aws_cdk_aws_sns_889c7272.ITopic,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f51a649a8dfc2e7a670860f5185bdfa6826e2eb15735e95342c5852f63c5965d(
    *,
    dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
    filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
    protocol: typing.Optional[_aws_cdk_aws_sns_889c7272.SubscriptionProtocol] = None,
    raw_message_delivery: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__800bf06002be22a53c168e41524e42eeb57e06da500371468479d127abea9b4a(
    *,
    dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
    filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
    json: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e56dd01cd9e94b0dd3281370319ba556eebc5528f146f5f5fdd9eebfbe5ad95(
    *,
    dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
    filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce928566c2cb5ee2c01d9b46b709b7a55136424627b6731558e46d63c6c9f8fa(
    *,
    dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
    filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfcc271364229be4712c2a7d415b7b4ef6b058b465f7bfbed4f5aa36e5e98992(
    *,
    dead_letter_queue: typing.Optional[_aws_cdk_aws_sqs_48bffef9.IQueue] = None,
    filter_policy: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_aws_sns_889c7272.SubscriptionFilter]] = None,
    raw_message_delivery: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass
