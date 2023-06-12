'''
# Lifecycle Hook for the CDK AWS AutoScaling Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

This library contains integration classes for AutoScaling lifecycle hooks.
Instances of these classes should be passed to the
`autoScalingGroup.addLifecycleHook()` method.

Lifecycle hooks can be activated in one of the following ways:

* Invoke a Lambda function
* Publish to an SNS topic
* Send to an SQS queue

For more information on using this library, see the README of the
`@aws-cdk/aws-autoscaling` library.

For more information about lifecycle hooks, see
[Amazon EC2 AutoScaling Lifecycle hooks](https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html) in the Amazon EC2 User Guide.
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

import aws_cdk.aws_autoscaling as _aws_cdk_aws_autoscaling_92cc07a7
import aws_cdk.aws_iam as _aws_cdk_aws_iam_940a1ce0
import aws_cdk.aws_kms as _aws_cdk_aws_kms_e491a92b
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_5443dbc3
import aws_cdk.aws_sns as _aws_cdk_aws_sns_889c7272
import aws_cdk.aws_sqs as _aws_cdk_aws_sqs_48bffef9
import constructs as _constructs_77d1e7e8


@jsii.implements(_aws_cdk_aws_autoscaling_92cc07a7.ILifecycleHookTarget)
class FunctionHook(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-autoscaling-hooktargets.FunctionHook",
):
    '''Use a Lambda Function as a hook target.

    Internally creates a Topic to make the connection.

    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_autoscaling_hooktargets as autoscaling_hooktargets
        import aws_cdk.aws_kms as kms
        import aws_cdk.aws_lambda as lambda_
        
        # function_: lambda.Function
        # key: kms.Key
        
        function_hook = autoscaling_hooktargets.FunctionHook(function_, key)
    '''

    def __init__(
        self,
        fn: _aws_cdk_aws_lambda_5443dbc3.IFunction,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
    ) -> None:
        '''
        :param fn: Function to invoke in response to a lifecycle event.
        :param encryption_key: If provided, this key is used to encrypt the contents of the SNS topic.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ec48f6eb8699d8b1a278992cacac9cdf1222205e55b0cbef7a9884214e2175e)
            check_type(argname="argument fn", value=fn, expected_type=type_hints["fn"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
        jsii.create(self.__class__, self, [fn, encryption_key])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _constructs_77d1e7e8.Construct,
        *,
        lifecycle_hook: _aws_cdk_aws_autoscaling_92cc07a7.LifecycleHook,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    ) -> _aws_cdk_aws_autoscaling_92cc07a7.LifecycleHookTargetConfig:
        '''If the ``IRole`` does not exist in ``options``, will create an ``IRole`` and an SNS Topic and attach both to the lifecycle hook.

        If the ``IRole`` does exist in ``options``, will only create an SNS Topic and attach it to the lifecycle hook.

        :param _scope: -
        :param lifecycle_hook: The lifecycle hook to attach to. [disable-awslint:ref-via-interface]
        :param role: The role to use when attaching to the lifecycle hook. [disable-awslint:ref-via-interface] Default: : a role is not created unless the target arn is specified
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c671a567d0ba75d0f4190cd5af886929b29496f1cf04e19c9e296e8f22c1a9ec)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        options = _aws_cdk_aws_autoscaling_92cc07a7.BindHookTargetOptions(
            lifecycle_hook=lifecycle_hook, role=role
        )

        return typing.cast(_aws_cdk_aws_autoscaling_92cc07a7.LifecycleHookTargetConfig, jsii.invoke(self, "bind", [_scope, options]))


@jsii.implements(_aws_cdk_aws_autoscaling_92cc07a7.ILifecycleHookTarget)
class QueueHook(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-autoscaling-hooktargets.QueueHook",
):
    '''Use an SQS queue as a hook target.

    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_autoscaling_hooktargets as autoscaling_hooktargets
        import aws_cdk.aws_sqs as sqs
        
        # queue: sqs.Queue
        
        queue_hook = autoscaling_hooktargets.QueueHook(queue)
    '''

    def __init__(self, queue: _aws_cdk_aws_sqs_48bffef9.IQueue) -> None:
        '''
        :param queue: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__595929baac1b303a68bc3d8a29fdbbc7717483018624bebb1e2bc79b3b8ee431)
            check_type(argname="argument queue", value=queue, expected_type=type_hints["queue"])
        jsii.create(self.__class__, self, [queue])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _constructs_77d1e7e8.Construct,
        *,
        lifecycle_hook: _aws_cdk_aws_autoscaling_92cc07a7.LifecycleHook,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    ) -> _aws_cdk_aws_autoscaling_92cc07a7.LifecycleHookTargetConfig:
        '''If an ``IRole`` is found in ``options``, grant it access to send messages.

        Otherwise, create a new ``IRole`` and grant it access to send messages.

        :param _scope: -
        :param lifecycle_hook: The lifecycle hook to attach to. [disable-awslint:ref-via-interface]
        :param role: The role to use when attaching to the lifecycle hook. [disable-awslint:ref-via-interface] Default: : a role is not created unless the target arn is specified

        :return: the ``IRole`` with access to send messages and the ARN of the queue it has access to send messages to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cda9db7b90b74a064c29a557097496cb5dae0fbede0164b546aff4ab7316c7b2)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        options = _aws_cdk_aws_autoscaling_92cc07a7.BindHookTargetOptions(
            lifecycle_hook=lifecycle_hook, role=role
        )

        return typing.cast(_aws_cdk_aws_autoscaling_92cc07a7.LifecycleHookTargetConfig, jsii.invoke(self, "bind", [_scope, options]))


@jsii.implements(_aws_cdk_aws_autoscaling_92cc07a7.ILifecycleHookTarget)
class TopicHook(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-autoscaling-hooktargets.TopicHook",
):
    '''Use an SNS topic as a hook target.

    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_autoscaling_hooktargets as autoscaling_hooktargets
        import aws_cdk.aws_sns as sns
        
        # topic: sns.Topic
        
        topic_hook = autoscaling_hooktargets.TopicHook(topic)
    '''

    def __init__(self, topic: _aws_cdk_aws_sns_889c7272.ITopic) -> None:
        '''
        :param topic: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac667e9b66abf6fdae4873c1ff8a967a6eacbc8087ff9b68a4de01492dc47391)
            check_type(argname="argument topic", value=topic, expected_type=type_hints["topic"])
        jsii.create(self.__class__, self, [topic])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _constructs_77d1e7e8.Construct,
        *,
        lifecycle_hook: _aws_cdk_aws_autoscaling_92cc07a7.LifecycleHook,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    ) -> _aws_cdk_aws_autoscaling_92cc07a7.LifecycleHookTargetConfig:
        '''If an ``IRole`` is found in ``options``, grant it topic publishing permissions.

        Otherwise, create a new ``IRole`` and grant it topic publishing permissions.

        :param _scope: -
        :param lifecycle_hook: The lifecycle hook to attach to. [disable-awslint:ref-via-interface]
        :param role: The role to use when attaching to the lifecycle hook. [disable-awslint:ref-via-interface] Default: : a role is not created unless the target arn is specified

        :return: the ``IRole`` with topic publishing permissions and the ARN of the topic it has publishing permission to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49a008743df2d5f69fa67cd5f6ccc728a5b98e83255618de2f3cf578e2a90bc6)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        options = _aws_cdk_aws_autoscaling_92cc07a7.BindHookTargetOptions(
            lifecycle_hook=lifecycle_hook, role=role
        )

        return typing.cast(_aws_cdk_aws_autoscaling_92cc07a7.LifecycleHookTargetConfig, jsii.invoke(self, "bind", [_scope, options]))


__all__ = [
    "FunctionHook",
    "QueueHook",
    "TopicHook",
]

publication.publish()

def _typecheckingstub__0ec48f6eb8699d8b1a278992cacac9cdf1222205e55b0cbef7a9884214e2175e(
    fn: _aws_cdk_aws_lambda_5443dbc3.IFunction,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c671a567d0ba75d0f4190cd5af886929b29496f1cf04e19c9e296e8f22c1a9ec(
    _scope: _constructs_77d1e7e8.Construct,
    *,
    lifecycle_hook: _aws_cdk_aws_autoscaling_92cc07a7.LifecycleHook,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__595929baac1b303a68bc3d8a29fdbbc7717483018624bebb1e2bc79b3b8ee431(
    queue: _aws_cdk_aws_sqs_48bffef9.IQueue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cda9db7b90b74a064c29a557097496cb5dae0fbede0164b546aff4ab7316c7b2(
    _scope: _constructs_77d1e7e8.Construct,
    *,
    lifecycle_hook: _aws_cdk_aws_autoscaling_92cc07a7.LifecycleHook,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac667e9b66abf6fdae4873c1ff8a967a6eacbc8087ff9b68a4de01492dc47391(
    topic: _aws_cdk_aws_sns_889c7272.ITopic,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49a008743df2d5f69fa67cd5f6ccc728a5b98e83255618de2f3cf578e2a90bc6(
    _scope: _constructs_77d1e7e8.Construct,
    *,
    lifecycle_hook: _aws_cdk_aws_autoscaling_92cc07a7.LifecycleHook,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass
