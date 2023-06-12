'''
# Amazon Kinesis Data Firehose Construct Library

<!--BEGIN STABILITY BANNER-->---


![cfn-resources: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

> All classes with the `Cfn` prefix in this module ([CFN Resources](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_lib)) are always stable and safe to use.

![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

[Amazon Kinesis Data Firehose](https://docs.aws.amazon.com/firehose/latest/dev/what-is-this-service.html)
is a service for fully-managed delivery of real-time streaming data to storage services
such as Amazon S3, Amazon Redshift, Amazon Elasticsearch, Splunk, or any custom HTTP
endpoint or third-party services such as Datadog, Dynatrace, LogicMonitor, MongoDB, New
Relic, and Sumo Logic.

Kinesis Data Firehose delivery streams are distinguished from Kinesis data streams in
their models of consumtpion. Whereas consumers read from a data stream by actively pulling
data from the stream, a delivery stream pushes data to its destination on a regular
cadence. This means that data streams are intended to have consumers that do on-demand
processing, like AWS Lambda or Amazon EC2. On the other hand, delivery streams are
intended to have destinations that are sources for offline processing and analytics, such
as Amazon S3 and Amazon Redshift.

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk)
project. It allows you to define Kinesis Data Firehose delivery streams.

## Defining a Delivery Stream

In order to define a Delivery Stream, you must specify a destination. An S3 bucket can be
used as a destination. More supported destinations are covered [below](#destinations).

```python
bucket = s3.Bucket(self, "Bucket")
firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[destinations.S3Bucket(bucket)]
)
```

The above example defines the following resources:

* An S3 bucket
* A Kinesis Data Firehose delivery stream with Direct PUT as the source and CloudWatch
  error logging turned on.
* An IAM role which gives the delivery stream permission to write to the S3 bucket.

## Sources

There are two main methods of sourcing input data: Kinesis Data Streams and via a "direct
put".

See: [Sending Data to a Delivery Stream](https://docs.aws.amazon.com/firehose/latest/dev/basic-write.html)
in the *Kinesis Data Firehose Developer Guide*.

### Kinesis Data Stream

A delivery stream can read directly from a Kinesis data stream as a consumer of the data
stream. Configure this behaviour by providing a data stream in the `sourceStream`
property when constructing a delivery stream:

```python
# destination: firehose.IDestination

source_stream = kinesis.Stream(self, "Source Stream")
firehose.DeliveryStream(self, "Delivery Stream",
    source_stream=source_stream,
    destinations=[destination]
)
```

### Direct Put

Data must be provided via "direct put", ie., by using a `PutRecord` or `PutRecordBatch` API call. There are a number of ways of doing
so, such as:

* Kinesis Agent: a standalone Java application that monitors and delivers files while
  handling file rotation, checkpointing, and retries. See: [Writing to Kinesis Data Firehose Using Kinesis Agent](https://docs.aws.amazon.com/firehose/latest/dev/writing-with-agents.html)
  in the *Kinesis Data Firehose Developer Guide*.
* AWS SDK: a general purpose solution that allows you to deliver data to a delivery stream
  from anywhere using Java, .NET, Node.js, Python, or Ruby. See: [Writing to Kinesis Data Firehose Using the AWS SDK](https://docs.aws.amazon.com/firehose/latest/dev/writing-with-sdk.html)
  in the *Kinesis Data Firehose Developer Guide*.
* CloudWatch Logs: subscribe to a log group and receive filtered log events directly into
  a delivery stream. See: [logs-destinations](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-logs-destinations-readme.html).
* Eventbridge: add an event rule target to send events to a delivery stream based on the
  rule filtering. See: [events-targets](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-events-targets-readme.html).
* SNS: add a subscription to send all notifications from the topic to a delivery
  stream. See: [sns-subscriptions](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-sns-subscriptions-readme.html).
* IoT: add an action to an IoT rule to send various IoT information to a delivery stream

## Destinations

The following destinations are supported. See [kinesisfirehose-destinations](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-kinesisfirehose-destinations-readme.html)
for the implementations of these destinations.

### S3

Defining a delivery stream with an S3 bucket destination:

```python
# bucket: s3.Bucket

s3_destination = destinations.S3Bucket(bucket)

firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[s3_destination]
)
```

The S3 destination also supports custom dynamic prefixes. `prefix` will be used for files
successfully delivered to S3. `errorOutputPrefix` will be added to failed records before
writing them to S3.

```python
# bucket: s3.Bucket

s3_destination = destinations.S3Bucket(bucket,
    data_output_prefix="myFirehose/DeliveredYear=!{timestamp:yyyy}/anyMonth/rand=!{firehose:random-string}",
    error_output_prefix="myFirehoseFailures/!{firehose:error-output-type}/!{timestamp:yyyy}/anyMonth/!{timestamp:dd}"
)
```

See: [Custom S3 Prefixes](https://docs.aws.amazon.com/firehose/latest/dev/s3-prefixes.html) in the *Kinesis Data Firehose Developer Guide*.

## Server-side Encryption

Enabling server-side encryption (SSE) requires Kinesis Data Firehose to encrypt all data
sent to delivery stream when it is stored at rest. This means that data is encrypted
before being written to the service's internal storage layer and decrypted after it is
received from the internal storage layer. The service manages keys and cryptographic
operations so that sources and destinations do not need to, as the data is encrypted and
decrypted at the boundaries of the service (ie., before the data is delivered to a
destination). By default, delivery streams do not have SSE enabled.

The Key Management Service (KMS) Customer Managed Key (CMK) used for SSE can either be
AWS-owned or customer-managed. AWS-owned CMKs are keys that an AWS service (in this case
Kinesis Data Firehose) owns and manages for use in multiple AWS accounts. As a customer,
you cannot view, use, track, or manage these keys, and you are not charged for their
use. On the other hand, customer-managed CMKs are keys that are created and owned within
your account and managed entirely by you. As a customer, you are responsible for managing
access, rotation, aliases, and deletion for these keys, and you are changed for their
use. See: [Customer master keys](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#master_keys)
in the *KMS Developer Guide*.

```python
# destination: firehose.IDestination
# SSE with an customer-managed CMK that is explicitly specified
# key: kms.Key


# SSE with an AWS-owned CMK
firehose.DeliveryStream(self, "Delivery Stream AWS Owned",
    encryption=firehose.StreamEncryption.AWS_OWNED,
    destinations=[destination]
)
# SSE with an customer-managed CMK that is created automatically by the CDK
firehose.DeliveryStream(self, "Delivery Stream Implicit Customer Managed",
    encryption=firehose.StreamEncryption.CUSTOMER_MANAGED,
    destinations=[destination]
)
firehose.DeliveryStream(self, "Delivery Stream Explicit Customer Managed",
    encryption_key=key,
    destinations=[destination]
)
```

See: [Data Protection](https://docs.aws.amazon.com/firehose/latest/dev/encryption.html) in
the *Kinesis Data Firehose Developer Guide*.

## Monitoring

Kinesis Data Firehose is integrated with CloudWatch, so you can monitor the performance of
your delivery streams via logs and metrics.

### Logs

Kinesis Data Firehose will send logs to CloudWatch when data transformation or data
delivery fails. The CDK will enable logging by default and create a CloudWatch LogGroup
and LogStream for your Delivery Stream.

You can provide a specific log group to specify where the CDK will create the log streams
where log events will be sent:

```python
import aws_cdk.aws_logs as logs
# bucket: s3.Bucket

# destination: firehose.IDestination


log_group = logs.LogGroup(self, "Log Group")
destination = destinations.S3Bucket(bucket,
    log_group=log_group
)
firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[destination]
)
```

Logging can also be disabled:

```python
# bucket: s3.Bucket

destination = destinations.S3Bucket(bucket,
    logging=False
)
firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[destination]
)
```

See: [Monitoring using CloudWatch Logs](https://docs.aws.amazon.com/firehose/latest/dev/monitoring-with-cloudwatch-logs.html)
in the *Kinesis Data Firehose Developer Guide*.

### Metrics

Kinesis Data Firehose sends metrics to CloudWatch so that you can collect and analyze the
performance of the delivery stream, including data delivery, data ingestion, data
transformation, format conversion, API usage, encryption, and resource usage. You can then
use CloudWatch alarms to alert you, for example, when data freshness (the age of the
oldest record in the delivery stream) exceeds the buffering limit (indicating that data is
not being delivered to your destination), or when the rate of incoming records exceeds the
limit of records per second (indicating data is flowing into your delivery stream faster
than it is configured to process).

CDK provides methods for accessing delivery stream metrics with default configuration,
such as `metricIncomingBytes`, and `metricIncomingRecords` (see [`IDeliveryStream`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesisfirehose.IDeliveryStream.html)
for a full list). CDK also provides a generic `metric` method that can be used to produce
metric configurations for any metric provided by Kinesis Data Firehose; the configurations
are pre-populated with the correct dimensions for the delivery stream.

```python
import aws_cdk.aws_cloudwatch as cloudwatch
# delivery_stream: firehose.DeliveryStream


# Alarm that triggers when the per-second average of incoming bytes exceeds 90% of the current service limit
incoming_bytes_percent_of_limit = cloudwatch.MathExpression(
    expression="incomingBytes / 300 / bytePerSecLimit",
    using_metrics={
        "incoming_bytes": delivery_stream.metric_incoming_bytes(statistic=cloudwatch.Statistic.SUM),
        "byte_per_sec_limit": delivery_stream.metric("BytesPerSecondLimit")
    }
)

cloudwatch.Alarm(self, "Alarm",
    metric=incoming_bytes_percent_of_limit,
    threshold=0.9,
    evaluation_periods=3
)
```

See: [Monitoring Using CloudWatch Metrics](https://docs.aws.amazon.com/firehose/latest/dev/monitoring-with-cloudwatch-metrics.html)
in the *Kinesis Data Firehose Developer Guide*.

## Compression

Your data can automatically be compressed when it is delivered to S3 as either a final or
an intermediary/backup destination. Supported compression formats are: gzip, Snappy,
Hadoop-compatible Snappy, and ZIP, except for Redshift destinations, where Snappy
(regardless of Hadoop-compatibility) and ZIP are not supported. By default, data is
delivered to S3 without compression.

```python
# Compress data delivered to S3 using Snappy
# bucket: s3.Bucket

s3_destination = destinations.S3Bucket(bucket,
    compression=destinations.Compression.SNAPPY
)
firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[s3_destination]
)
```

## Buffering

Incoming data is buffered before it is delivered to the specified destination. The
delivery stream will wait until the amount of incoming data has exceeded some threshold
(the "buffer size") or until the time since the last data delivery occurred exceeds some
threshold (the "buffer interval"), whichever happens first. You can configure these
thresholds based on the capabilities of the destination and your use-case. By default, the
buffer size is 5 MiB and the buffer interval is 5 minutes.

```python
# Increase the buffer interval and size to 10 minutes and 8 MiB, respectively
# bucket: s3.Bucket

destination = destinations.S3Bucket(bucket,
    buffering_interval=Duration.minutes(10),
    buffering_size=Size.mebibytes(8)
)
firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[destination]
)
```

See: [Data Delivery Frequency](https://docs.aws.amazon.com/firehose/latest/dev/basic-deliver.html#frequency)
in the *Kinesis Data Firehose Developer Guide*.

## Destination Encryption

Your data can be automatically encrypted when it is delivered to S3 as a final or
an intermediary/backup destination. Kinesis Data Firehose supports Amazon S3 server-side
encryption with AWS Key Management Service (AWS KMS) for encrypting delivered data
in Amazon S3. You can choose to not encrypt the data or to encrypt with a key from
the list of AWS KMS keys that you own. For more information, see [Protecting Data
Using Server-Side Encryption with AWS KMS–Managed Keys (SSE-KMS)](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingKMSEncryption.html). Data is not encrypted by default.

```python
# bucket: s3.Bucket
# key: kms.Key

destination = destinations.S3Bucket(bucket,
    encryption_key=key
)
firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[destination]
)
```

## Backup

A delivery stream can be configured to backup data to S3 that it attempted to deliver to
the configured destination. Backed up data can be all the data that the delivery stream
attempted to deliver or just data that it failed to deliver (Redshift and S3 destinations
can only backup all data). CDK can create a new S3 bucket where it will back up data or
you can provide a bucket where data will be backed up. You can also provide a prefix under
which your backed-up data will be placed within the bucket. By default, source data is not
backed up to S3.

```python
# Enable backup of all source records (to an S3 bucket created by CDK).
# bucket: s3.Bucket
# Explicitly provide an S3 bucket to which all source records will be backed up.
# backup_bucket: s3.Bucket

firehose.DeliveryStream(self, "Delivery Stream Backup All",
    destinations=[
        destinations.S3Bucket(bucket,
            s3_backup=destinations.DestinationS3BackupProps(
                mode=destinations.BackupMode.ALL
            )
        )
    ]
)
firehose.DeliveryStream(self, "Delivery Stream Backup All Explicit Bucket",
    destinations=[
        destinations.S3Bucket(bucket,
            s3_backup=destinations.DestinationS3BackupProps(
                bucket=backup_bucket
            )
        )
    ]
)
# Explicitly provide an S3 prefix under which all source records will be backed up.
firehose.DeliveryStream(self, "Delivery Stream Backup All Explicit Prefix",
    destinations=[
        destinations.S3Bucket(bucket,
            s3_backup=destinations.DestinationS3BackupProps(
                mode=destinations.BackupMode.ALL,
                data_output_prefix="mybackup"
            )
        )
    ]
)
```

If any Data Processing or Transformation is configured on your Delivery Stream, the source
records will be backed up in their original format.

## Data Processing/Transformation

Data can be transformed before being delivered to destinations. There are two types of
data processing for delivery streams: record transformation with AWS Lambda, and record
format conversion using a schema stored in an AWS Glue table. If both types of data
processing are configured, then the Lambda transformation is performed first. By default,
no data processing occurs. This construct library currently only supports data
transformation with AWS Lambda. See [#15501](https://github.com/aws/aws-cdk/issues/15501)
to track the status of adding support for record format conversion.

### Data transformation with AWS Lambda

To transform the data, Kinesis Data Firehose will call a Lambda function that you provide
and deliver the data returned in place of the source record. The function must return a
result that contains records in a specific format, including the following fields:

* `recordId` -- the ID of the input record that corresponds the results.
* `result` -- the status of the transformation of the record: "Ok" (success), "Dropped"
  (not processed intentionally), or "ProcessingFailed" (not processed due to an error).
* `data` -- the transformed data, Base64-encoded.

The data is buffered up to 1 minute and up to 3 MiB by default before being sent to the
function, but can be configured using `bufferInterval` and `bufferSize` in the processor
configuration (see: [Buffering](#buffering)). If the function invocation fails due to a
network timeout or because of hitting an invocation limit, the invocation is retried 3
times by default, but can be configured using `retries` in the processor configuration.

```python
# bucket: s3.Bucket
# Provide a Lambda function that will transform records before delivery, with custom
# buffering and retry configuration
lambda_function = lambda_.Function(self, "Processor",
    runtime=lambda_.Runtime.NODEJS_14_X,
    handler="index.handler",
    code=lambda_.Code.from_asset(path.join(__dirname, "process-records"))
)
lambda_processor = firehose.LambdaFunctionProcessor(lambda_function,
    buffer_interval=Duration.minutes(5),
    buffer_size=Size.mebibytes(5),
    retries=5
)
s3_destination = destinations.S3Bucket(bucket,
    processor=lambda_processor
)
firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[s3_destination]
)
```

```python
import path as path
import aws_cdk.aws_kinesisfirehose as firehose
import aws_cdk.aws_kms as kms
import aws_cdk.aws_lambda_nodejs as lambdanodejs
import aws_cdk.aws_logs as logs
import aws_cdk.aws_s3 as s3
import aws_cdk.core as cdk
import aws_cdk.aws_kinesisfirehose_destinations as destinations

app = cdk.App()

stack = cdk.Stack(app, "aws-cdk-firehose-delivery-stream-s3-all-properties")

bucket = s3.Bucket(stack, "Bucket",
    removal_policy=cdk.RemovalPolicy.DESTROY,
    auto_delete_objects=True
)

backup_bucket = s3.Bucket(stack, "BackupBucket",
    removal_policy=cdk.RemovalPolicy.DESTROY,
    auto_delete_objects=True
)
log_group = logs.LogGroup(stack, "LogGroup",
    removal_policy=cdk.RemovalPolicy.DESTROY
)

data_processor_function = lambdanodejs.NodejsFunction(stack, "DataProcessorFunction",
    entry=path.join(__dirname, "lambda-data-processor.js"),
    timeout=cdk.Duration.minutes(1)
)

processor = firehose.LambdaFunctionProcessor(data_processor_function,
    buffer_interval=cdk.Duration.seconds(60),
    buffer_size=cdk.Size.mebibytes(1),
    retries=1
)

key = kms.Key(stack, "Key",
    removal_policy=cdk.RemovalPolicy.DESTROY
)

backup_key = kms.Key(stack, "BackupKey",
    removal_policy=cdk.RemovalPolicy.DESTROY
)

firehose.DeliveryStream(stack, "Delivery Stream",
    destinations=[destinations.S3Bucket(bucket,
        logging=True,
        log_group=log_group,
        processor=processor,
        compression=destinations.Compression.GZIP,
        data_output_prefix="regularPrefix",
        error_output_prefix="errorPrefix",
        buffering_interval=cdk.Duration.seconds(60),
        buffering_size=cdk.Size.mebibytes(1),
        encryption_key=key,
        s3_backup=destinations.DestinationS3BackupProps(
            mode=destinations.BackupMode.ALL,
            bucket=backup_bucket,
            compression=destinations.Compression.ZIP,
            data_output_prefix="backupPrefix",
            error_output_prefix="backupErrorPrefix",
            buffering_interval=cdk.Duration.seconds(60),
            buffering_size=cdk.Size.mebibytes(1),
            encryption_key=backup_key
        )
    )]
)

app.synth()
```

!cdk-integ pragma:ignore-assets

```python
import path as path
import aws_cdk.aws_kinesisfirehose as firehose
import aws_cdk.aws_kms as kms
import aws_cdk.aws_lambda_nodejs as lambdanodejs
import aws_cdk.aws_logs as logs
import aws_cdk.aws_s3 as s3
import aws_cdk.core as cdk
import aws_cdk.aws_kinesisfirehose_destinations as destinations

app = cdk.App()

stack = cdk.Stack(app, "aws-cdk-firehose-delivery-stream-s3-all-properties")

bucket = s3.Bucket(stack, "Bucket",
    removal_policy=cdk.RemovalPolicy.DESTROY,
    auto_delete_objects=True
)

backup_bucket = s3.Bucket(stack, "BackupBucket",
    removal_policy=cdk.RemovalPolicy.DESTROY,
    auto_delete_objects=True
)
log_group = logs.LogGroup(stack, "LogGroup",
    removal_policy=cdk.RemovalPolicy.DESTROY
)

data_processor_function = lambdanodejs.NodejsFunction(stack, "DataProcessorFunction",
    entry=path.join(__dirname, "lambda-data-processor.js"),
    timeout=cdk.Duration.minutes(1)
)

processor = firehose.LambdaFunctionProcessor(data_processor_function,
    buffer_interval=cdk.Duration.seconds(60),
    buffer_size=cdk.Size.mebibytes(1),
    retries=1
)

key = kms.Key(stack, "Key",
    removal_policy=cdk.RemovalPolicy.DESTROY
)

backup_key = kms.Key(stack, "BackupKey",
    removal_policy=cdk.RemovalPolicy.DESTROY
)

firehose.DeliveryStream(stack, "Delivery Stream",
    destinations=[destinations.S3Bucket(bucket,
        logging=True,
        log_group=log_group,
        processor=processor,
        compression=destinations.Compression.GZIP,
        data_output_prefix="regularPrefix",
        error_output_prefix="errorPrefix",
        buffering_interval=cdk.Duration.seconds(60),
        buffering_size=cdk.Size.mebibytes(1),
        encryption_key=key,
        s3_backup=destinations.DestinationS3BackupProps(
            mode=destinations.BackupMode.ALL,
            bucket=backup_bucket,
            compression=destinations.Compression.ZIP,
            data_output_prefix="backupPrefix",
            error_output_prefix="backupErrorPrefix",
            buffering_interval=cdk.Duration.seconds(60),
            buffering_size=cdk.Size.mebibytes(1),
            encryption_key=backup_key
        )
    )]
)

app.synth()
```

See: [Data Transformation](https://docs.aws.amazon.com/firehose/latest/dev/data-transformation.html)
in the *Kinesis Data Firehose Developer Guide*.

## Specifying an IAM role

The DeliveryStream class automatically creates IAM service roles with all the minimum
necessary permissions for Kinesis Data Firehose to access the resources referenced by your
delivery stream. One service role is created for the delivery stream that allows Kinesis
Data Firehose to read from a Kinesis data stream (if one is configured as the delivery
stream source) and for server-side encryption. Another service role is created for each
destination, which gives Kinesis Data Firehose write access to the destination resource,
as well as the ability to invoke data transformers and read schemas for record format
conversion. If you wish, you may specify your own IAM role for either the delivery stream
or the destination service role, or both. It must have the correct trust policy (it must
allow Kinesis Data Firehose to assume it) or delivery stream creation or data delivery
will fail. Other required permissions to destination resources, encryption keys, etc.,
will be provided automatically.

```python
# Specify the roles created above when defining the destination and delivery stream.
# bucket: s3.Bucket
# Create service roles for the delivery stream and destination.
# These can be used for other purposes and granted access to different resources.
# They must include the Kinesis Data Firehose service principal in their trust policies.
# Two separate roles are shown below, but the same role can be used for both purposes.
delivery_stream_role = iam.Role(self, "Delivery Stream Role",
    assumed_by=iam.ServicePrincipal("firehose.amazonaws.com")
)
destination_role = iam.Role(self, "Destination Role",
    assumed_by=iam.ServicePrincipal("firehose.amazonaws.com")
)
destination = destinations.S3Bucket(bucket, role=destination_role)
firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[destination],
    role=delivery_stream_role
)
```

See [Controlling Access](https://docs.aws.amazon.com/firehose/latest/dev/controlling-access.html)
in the *Kinesis Data Firehose Developer Guide*.

## Granting application access to a delivery stream

IAM roles, users or groups which need to be able to work with delivery streams should be
granted IAM permissions.

Any object that implements the `IGrantable` interface (ie., has an associated principal)
can be granted permissions to a delivery stream by calling:

* `grantPutRecords(principal)` - grants the principal the ability to put records onto the
  delivery stream
* `grant(principal, ...actions)` - grants the principal permission to a custom set of
  actions

```python
# Give the role permissions to write data to the delivery stream
# delivery_stream: firehose.DeliveryStream
lambda_role = iam.Role(self, "Role",
    assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
)
delivery_stream.grant_put_records(lambda_role)
```

The following write permissions are provided to a service principal by the `grantPutRecords()` method:

* `firehose:PutRecord`
* `firehose:PutRecordBatch`

## Granting a delivery stream access to a resource

Conversely to the above, Kinesis Data Firehose requires permissions in order for delivery
streams to interact with resources that you own. For example, if an S3 bucket is specified
as a destination of a delivery stream, the delivery stream must be granted permissions to
put and get objects from the bucket. When using the built-in AWS service destinations
found in the `@aws-cdk/aws-kinesisfirehose-destinations` module, the CDK grants the
permissions automatically. However, custom or third-party destinations may require custom
permissions. In this case, use the delivery stream as an `IGrantable`, as follows:

```python
# delivery_stream: firehose.DeliveryStream
fn = lambda_.Function(self, "Function",
    code=lambda_.Code.from_inline("exports.handler = (event) => {}"),
    runtime=lambda_.Runtime.NODEJS_14_X,
    handler="index.handler"
)
fn.grant_invoke(delivery_stream)
```

## Multiple destinations

Though the delivery stream allows specifying an array of destinations, only one
destination per delivery stream is currently allowed. This limitation is enforced at CDK
synthesis time and will throw an error.
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

import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_9b88bb94
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_67de8e8d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_940a1ce0
import aws_cdk.aws_kinesis as _aws_cdk_aws_kinesis_0674c215
import aws_cdk.aws_kms as _aws_cdk_aws_kms_e491a92b
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_5443dbc3
import aws_cdk.core as _aws_cdk_core_f4b25747
import constructs as _constructs_77d1e7e8


@jsii.implements(_aws_cdk_core_f4b25747.IInspectable)
class CfnDeliveryStream(
    _aws_cdk_core_f4b25747.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream",
):
    '''A CloudFormation ``AWS::KinesisFirehose::DeliveryStream``.

    The ``AWS::KinesisFirehose::DeliveryStream`` resource specifies an Amazon Kinesis Data Firehose (Kinesis Data Firehose) delivery stream that delivers real-time streaming data to an Amazon Simple Storage Service (Amazon S3), Amazon Redshift, or Amazon Elasticsearch Service (Amazon ES) destination. For more information, see `Creating an Amazon Kinesis Data Firehose Delivery Stream <https://docs.aws.amazon.com/firehose/latest/dev/basic-create.html>`_ in the *Amazon Kinesis Data Firehose Developer Guide* .

    :cloudformationResource: AWS::KinesisFirehose::DeliveryStream
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_kinesisfirehose as kinesisfirehose
        
        cfn_delivery_stream = kinesisfirehose.CfnDeliveryStream(self, "MyCfnDeliveryStream",
            amazon_open_search_serverless_destination_configuration=kinesisfirehose.CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty(
                index_name="indexName",
                role_arn="roleArn",
                s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                    bucket_arn="bucketArn",
                    role_arn="roleArn",
        
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    compression_format="compressionFormat",
                    encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                        kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                            awskms_key_arn="awskmsKeyArn"
                        ),
                        no_encryption_config="noEncryptionConfig"
                    ),
                    error_output_prefix="errorOutputPrefix",
                    prefix="prefix"
                ),
        
                # the properties below are optional
                buffering_hints=kinesisfirehose.CfnDeliveryStream.AmazonOpenSearchServerlessBufferingHintsProperty(
                    interval_in_seconds=123,
                    size_in_mBs=123
                ),
                cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                    enabled=False,
                    log_group_name="logGroupName",
                    log_stream_name="logStreamName"
                ),
                collection_endpoint="collectionEndpoint",
                processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                    enabled=False,
                    processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                        type="type",
        
                        # the properties below are optional
                        parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                            parameter_name="parameterName",
                            parameter_value="parameterValue"
                        )]
                    )]
                ),
                retry_options=kinesisfirehose.CfnDeliveryStream.AmazonOpenSearchServerlessRetryOptionsProperty(
                    duration_in_seconds=123
                ),
                s3_backup_mode="s3BackupMode",
                vpc_configuration=kinesisfirehose.CfnDeliveryStream.VpcConfigurationProperty(
                    role_arn="roleArn",
                    security_group_ids=["securityGroupIds"],
                    subnet_ids=["subnetIds"]
                )
            ),
            amazonopensearchservice_destination_configuration=kinesisfirehose.CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty(
                index_name="indexName",
                role_arn="roleArn",
                s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                    bucket_arn="bucketArn",
                    role_arn="roleArn",
        
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    compression_format="compressionFormat",
                    encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                        kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                            awskms_key_arn="awskmsKeyArn"
                        ),
                        no_encryption_config="noEncryptionConfig"
                    ),
                    error_output_prefix="errorOutputPrefix",
                    prefix="prefix"
                ),
        
                # the properties below are optional
                buffering_hints=kinesisfirehose.CfnDeliveryStream.AmazonopensearchserviceBufferingHintsProperty(
                    interval_in_seconds=123,
                    size_in_mBs=123
                ),
                cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                    enabled=False,
                    log_group_name="logGroupName",
                    log_stream_name="logStreamName"
                ),
                cluster_endpoint="clusterEndpoint",
                document_id_options=kinesisfirehose.CfnDeliveryStream.DocumentIdOptionsProperty(
                    default_document_id_format="defaultDocumentIdFormat"
                ),
                domain_arn="domainArn",
                index_rotation_period="indexRotationPeriod",
                processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                    enabled=False,
                    processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                        type="type",
        
                        # the properties below are optional
                        parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                            parameter_name="parameterName",
                            parameter_value="parameterValue"
                        )]
                    )]
                ),
                retry_options=kinesisfirehose.CfnDeliveryStream.AmazonopensearchserviceRetryOptionsProperty(
                    duration_in_seconds=123
                ),
                s3_backup_mode="s3BackupMode",
                type_name="typeName",
                vpc_configuration=kinesisfirehose.CfnDeliveryStream.VpcConfigurationProperty(
                    role_arn="roleArn",
                    security_group_ids=["securityGroupIds"],
                    subnet_ids=["subnetIds"]
                )
            ),
            delivery_stream_encryption_configuration_input=kinesisfirehose.CfnDeliveryStream.DeliveryStreamEncryptionConfigurationInputProperty(
                key_type="keyType",
        
                # the properties below are optional
                key_arn="keyArn"
            ),
            delivery_stream_name="deliveryStreamName",
            delivery_stream_type="deliveryStreamType",
            elasticsearch_destination_configuration=kinesisfirehose.CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty(
                index_name="indexName",
                role_arn="roleArn",
                s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                    bucket_arn="bucketArn",
                    role_arn="roleArn",
        
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    compression_format="compressionFormat",
                    encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                        kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                            awskms_key_arn="awskmsKeyArn"
                        ),
                        no_encryption_config="noEncryptionConfig"
                    ),
                    error_output_prefix="errorOutputPrefix",
                    prefix="prefix"
                ),
        
                # the properties below are optional
                buffering_hints=kinesisfirehose.CfnDeliveryStream.ElasticsearchBufferingHintsProperty(
                    interval_in_seconds=123,
                    size_in_mBs=123
                ),
                cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                    enabled=False,
                    log_group_name="logGroupName",
                    log_stream_name="logStreamName"
                ),
                cluster_endpoint="clusterEndpoint",
                document_id_options=kinesisfirehose.CfnDeliveryStream.DocumentIdOptionsProperty(
                    default_document_id_format="defaultDocumentIdFormat"
                ),
                domain_arn="domainArn",
                index_rotation_period="indexRotationPeriod",
                processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                    enabled=False,
                    processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                        type="type",
        
                        # the properties below are optional
                        parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                            parameter_name="parameterName",
                            parameter_value="parameterValue"
                        )]
                    )]
                ),
                retry_options=kinesisfirehose.CfnDeliveryStream.ElasticsearchRetryOptionsProperty(
                    duration_in_seconds=123
                ),
                s3_backup_mode="s3BackupMode",
                type_name="typeName",
                vpc_configuration=kinesisfirehose.CfnDeliveryStream.VpcConfigurationProperty(
                    role_arn="roleArn",
                    security_group_ids=["securityGroupIds"],
                    subnet_ids=["subnetIds"]
                )
            ),
            extended_s3_destination_configuration=kinesisfirehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(
                bucket_arn="bucketArn",
                role_arn="roleArn",
        
                # the properties below are optional
                buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                    interval_in_seconds=123,
                    size_in_mBs=123
                ),
                cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                    enabled=False,
                    log_group_name="logGroupName",
                    log_stream_name="logStreamName"
                ),
                compression_format="compressionFormat",
                data_format_conversion_configuration=kinesisfirehose.CfnDeliveryStream.DataFormatConversionConfigurationProperty(
                    enabled=False,
                    input_format_configuration=kinesisfirehose.CfnDeliveryStream.InputFormatConfigurationProperty(
                        deserializer=kinesisfirehose.CfnDeliveryStream.DeserializerProperty(
                            hive_json_ser_de=kinesisfirehose.CfnDeliveryStream.HiveJsonSerDeProperty(
                                timestamp_formats=["timestampFormats"]
                            ),
                            open_xJson_ser_de=kinesisfirehose.CfnDeliveryStream.OpenXJsonSerDeProperty(
                                case_insensitive=False,
                                column_to_json_key_mappings={
                                    "column_to_json_key_mappings_key": "columnToJsonKeyMappings"
                                },
                                convert_dots_in_json_keys_to_underscores=False
                            )
                        )
                    ),
                    output_format_configuration=kinesisfirehose.CfnDeliveryStream.OutputFormatConfigurationProperty(
                        serializer=kinesisfirehose.CfnDeliveryStream.SerializerProperty(
                            orc_ser_de=kinesisfirehose.CfnDeliveryStream.OrcSerDeProperty(
                                block_size_bytes=123,
                                bloom_filter_columns=["bloomFilterColumns"],
                                bloom_filter_false_positive_probability=123,
                                compression="compression",
                                dictionary_key_threshold=123,
                                enable_padding=False,
                                format_version="formatVersion",
                                padding_tolerance=123,
                                row_index_stride=123,
                                stripe_size_bytes=123
                            ),
                            parquet_ser_de=kinesisfirehose.CfnDeliveryStream.ParquetSerDeProperty(
                                block_size_bytes=123,
                                compression="compression",
                                enable_dictionary_compression=False,
                                max_padding_bytes=123,
                                page_size_bytes=123,
                                writer_version="writerVersion"
                            )
                        )
                    ),
                    schema_configuration=kinesisfirehose.CfnDeliveryStream.SchemaConfigurationProperty(
                        catalog_id="catalogId",
                        database_name="databaseName",
                        region="region",
                        role_arn="roleArn",
                        table_name="tableName",
                        version_id="versionId"
                    )
                ),
                dynamic_partitioning_configuration=kinesisfirehose.CfnDeliveryStream.DynamicPartitioningConfigurationProperty(
                    enabled=False,
                    retry_options=kinesisfirehose.CfnDeliveryStream.RetryOptionsProperty(
                        duration_in_seconds=123
                    )
                ),
                encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                    kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                        awskms_key_arn="awskmsKeyArn"
                    ),
                    no_encryption_config="noEncryptionConfig"
                ),
                error_output_prefix="errorOutputPrefix",
                prefix="prefix",
                processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                    enabled=False,
                    processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                        type="type",
        
                        # the properties below are optional
                        parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                            parameter_name="parameterName",
                            parameter_value="parameterValue"
                        )]
                    )]
                ),
                s3_backup_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                    bucket_arn="bucketArn",
                    role_arn="roleArn",
        
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    compression_format="compressionFormat",
                    encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                        kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                            awskms_key_arn="awskmsKeyArn"
                        ),
                        no_encryption_config="noEncryptionConfig"
                    ),
                    error_output_prefix="errorOutputPrefix",
                    prefix="prefix"
                ),
                s3_backup_mode="s3BackupMode"
            ),
            http_endpoint_destination_configuration=kinesisfirehose.CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty(
                endpoint_configuration=kinesisfirehose.CfnDeliveryStream.HttpEndpointConfigurationProperty(
                    url="url",
        
                    # the properties below are optional
                    access_key="accessKey",
                    name="name"
                ),
                s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                    bucket_arn="bucketArn",
                    role_arn="roleArn",
        
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    compression_format="compressionFormat",
                    encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                        kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                            awskms_key_arn="awskmsKeyArn"
                        ),
                        no_encryption_config="noEncryptionConfig"
                    ),
                    error_output_prefix="errorOutputPrefix",
                    prefix="prefix"
                ),
        
                # the properties below are optional
                buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                    interval_in_seconds=123,
                    size_in_mBs=123
                ),
                cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                    enabled=False,
                    log_group_name="logGroupName",
                    log_stream_name="logStreamName"
                ),
                processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                    enabled=False,
                    processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                        type="type",
        
                        # the properties below are optional
                        parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                            parameter_name="parameterName",
                            parameter_value="parameterValue"
                        )]
                    )]
                ),
                request_configuration=kinesisfirehose.CfnDeliveryStream.HttpEndpointRequestConfigurationProperty(
                    common_attributes=[kinesisfirehose.CfnDeliveryStream.HttpEndpointCommonAttributeProperty(
                        attribute_name="attributeName",
                        attribute_value="attributeValue"
                    )],
                    content_encoding="contentEncoding"
                ),
                retry_options=kinesisfirehose.CfnDeliveryStream.RetryOptionsProperty(
                    duration_in_seconds=123
                ),
                role_arn="roleArn",
                s3_backup_mode="s3BackupMode"
            ),
            kinesis_stream_source_configuration=kinesisfirehose.CfnDeliveryStream.KinesisStreamSourceConfigurationProperty(
                kinesis_stream_arn="kinesisStreamArn",
                role_arn="roleArn"
            ),
            redshift_destination_configuration=kinesisfirehose.CfnDeliveryStream.RedshiftDestinationConfigurationProperty(
                cluster_jdbcurl="clusterJdbcurl",
                copy_command=kinesisfirehose.CfnDeliveryStream.CopyCommandProperty(
                    data_table_name="dataTableName",
        
                    # the properties below are optional
                    copy_options="copyOptions",
                    data_table_columns="dataTableColumns"
                ),
                password="password",
                role_arn="roleArn",
                s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                    bucket_arn="bucketArn",
                    role_arn="roleArn",
        
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    compression_format="compressionFormat",
                    encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                        kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                            awskms_key_arn="awskmsKeyArn"
                        ),
                        no_encryption_config="noEncryptionConfig"
                    ),
                    error_output_prefix="errorOutputPrefix",
                    prefix="prefix"
                ),
                username="username",
        
                # the properties below are optional
                cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                    enabled=False,
                    log_group_name="logGroupName",
                    log_stream_name="logStreamName"
                ),
                processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                    enabled=False,
                    processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                        type="type",
        
                        # the properties below are optional
                        parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                            parameter_name="parameterName",
                            parameter_value="parameterValue"
                        )]
                    )]
                ),
                retry_options=kinesisfirehose.CfnDeliveryStream.RedshiftRetryOptionsProperty(
                    duration_in_seconds=123
                ),
                s3_backup_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                    bucket_arn="bucketArn",
                    role_arn="roleArn",
        
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    compression_format="compressionFormat",
                    encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                        kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                            awskms_key_arn="awskmsKeyArn"
                        ),
                        no_encryption_config="noEncryptionConfig"
                    ),
                    error_output_prefix="errorOutputPrefix",
                    prefix="prefix"
                ),
                s3_backup_mode="s3BackupMode"
            ),
            s3_destination_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                bucket_arn="bucketArn",
                role_arn="roleArn",
        
                # the properties below are optional
                buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                    interval_in_seconds=123,
                    size_in_mBs=123
                ),
                cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                    enabled=False,
                    log_group_name="logGroupName",
                    log_stream_name="logStreamName"
                ),
                compression_format="compressionFormat",
                encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                    kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                        awskms_key_arn="awskmsKeyArn"
                    ),
                    no_encryption_config="noEncryptionConfig"
                ),
                error_output_prefix="errorOutputPrefix",
                prefix="prefix"
            ),
            splunk_destination_configuration=kinesisfirehose.CfnDeliveryStream.SplunkDestinationConfigurationProperty(
                hec_endpoint="hecEndpoint",
                hec_endpoint_type="hecEndpointType",
                hec_token="hecToken",
                s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                    bucket_arn="bucketArn",
                    role_arn="roleArn",
        
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    compression_format="compressionFormat",
                    encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                        kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                            awskms_key_arn="awskmsKeyArn"
                        ),
                        no_encryption_config="noEncryptionConfig"
                    ),
                    error_output_prefix="errorOutputPrefix",
                    prefix="prefix"
                ),
        
                # the properties below are optional
                cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                    enabled=False,
                    log_group_name="logGroupName",
                    log_stream_name="logStreamName"
                ),
                hec_acknowledgment_timeout_in_seconds=123,
                processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                    enabled=False,
                    processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                        type="type",
        
                        # the properties below are optional
                        parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                            parameter_name="parameterName",
                            parameter_value="parameterValue"
                        )]
                    )]
                ),
                retry_options=kinesisfirehose.CfnDeliveryStream.SplunkRetryOptionsProperty(
                    duration_in_seconds=123
                ),
                s3_backup_mode="s3BackupMode"
            ),
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        id: builtins.str,
        *,
        amazon_open_search_serverless_destination_configuration: typing.Optional[typing.Union[typing.Union["CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty", typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]] = None,
        amazonopensearchservice_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        delivery_stream_encryption_configuration_input: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.DeliveryStreamEncryptionConfigurationInputProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        delivery_stream_name: typing.Optional[builtins.str] = None,
        delivery_stream_type: typing.Optional[builtins.str] = None,
        elasticsearch_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        extended_s3_destination_configuration: typing.Optional[typing.Union[typing.Union["CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty", typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]] = None,
        http_endpoint_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        kinesis_stream_source_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.KinesisStreamSourceConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        redshift_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.RedshiftDestinationConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        s3_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.S3DestinationConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        splunk_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.SplunkDestinationConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Create a new ``AWS::KinesisFirehose::DeliveryStream``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param amazon_open_search_serverless_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.AmazonOpenSearchServerlessDestinationConfiguration``.
        :param amazonopensearchservice_destination_configuration: The destination in Amazon OpenSearch Service. You can specify only one destination.
        :param delivery_stream_encryption_configuration_input: Specifies the type and Amazon Resource Name (ARN) of the CMK to use for Server-Side Encryption (SSE).
        :param delivery_stream_name: The name of the delivery stream.
        :param delivery_stream_type: The delivery stream type. This can be one of the following values:. - ``DirectPut`` : Provider applications access the delivery stream directly. - ``KinesisStreamAsSource`` : The delivery stream uses a Kinesis data stream as a source.
        :param elasticsearch_destination_configuration: An Amazon ES destination for the delivery stream. Conditional. You must specify only one destination configuration. If you change the delivery stream destination from an Amazon ES destination to an Amazon S3 or Amazon Redshift destination, update requires `some interruptions <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-some-interrupt>`_ .
        :param extended_s3_destination_configuration: An Amazon S3 destination for the delivery stream. Conditional. You must specify only one destination configuration. If you change the delivery stream destination from an Amazon Extended S3 destination to an Amazon ES destination, update requires `some interruptions <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-some-interrupt>`_ .
        :param http_endpoint_destination_configuration: Enables configuring Kinesis Firehose to deliver data to any HTTP endpoint destination. You can specify only one destination.
        :param kinesis_stream_source_configuration: When a Kinesis stream is used as the source for the delivery stream, a `KinesisStreamSourceConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration.html>`_ containing the Kinesis stream ARN and the role ARN for the source stream.
        :param redshift_destination_configuration: An Amazon Redshift destination for the delivery stream. Conditional. You must specify only one destination configuration. If you change the delivery stream destination from an Amazon Redshift destination to an Amazon ES destination, update requires `some interruptions <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-some-interrupt>`_ .
        :param s3_destination_configuration: The ``S3DestinationConfiguration`` property type specifies an Amazon Simple Storage Service (Amazon S3) destination to which Amazon Kinesis Data Firehose (Kinesis Data Firehose) delivers data. Conditional. You must specify only one destination configuration. If you change the delivery stream destination from an Amazon S3 destination to an Amazon ES destination, update requires `some interruptions <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-some-interrupt>`_ .
        :param splunk_destination_configuration: The configuration of a destination in Splunk for the delivery stream.
        :param tags: A set of tags to assign to the delivery stream. A tag is a key-value pair that you can define and assign to AWS resources. Tags are metadata. For example, you can add friendly names and descriptions or other types of information that can help you distinguish the delivery stream. For more information about tags, see `Using Cost Allocation Tags <https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html>`_ in the AWS Billing and Cost Management User Guide. You can specify up to 50 tags when creating a delivery stream.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f2187cf1658462c5e90fadcbc2c886b0e2eb15da7b6830258a92c4e7bc6c9cd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnDeliveryStreamProps(
            amazon_open_search_serverless_destination_configuration=amazon_open_search_serverless_destination_configuration,
            amazonopensearchservice_destination_configuration=amazonopensearchservice_destination_configuration,
            delivery_stream_encryption_configuration_input=delivery_stream_encryption_configuration_input,
            delivery_stream_name=delivery_stream_name,
            delivery_stream_type=delivery_stream_type,
            elasticsearch_destination_configuration=elasticsearch_destination_configuration,
            extended_s3_destination_configuration=extended_s3_destination_configuration,
            http_endpoint_destination_configuration=http_endpoint_destination_configuration,
            kinesis_stream_source_configuration=kinesis_stream_source_configuration,
            redshift_destination_configuration=redshift_destination_configuration,
            s3_destination_configuration=s3_destination_configuration,
            splunk_destination_configuration=splunk_destination_configuration,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _aws_cdk_core_f4b25747.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__282c33338d43e4451c857de390778cff23d9290b0da72cc0c8b05dcc958faa78)
            check_type(argname="argument inspector", value=inspector, expected_type=type_hints["inspector"])
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18aeb7fdc6b4d29db25a7b6de6bb11f72301b791bb4911491da0f7d46514fe14)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the delivery stream, such as ``arn:aws:firehose:us-east-2:123456789012:deliverystream/delivery-stream-name`` .

        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> _aws_cdk_core_f4b25747.TagManager:
        '''A set of tags to assign to the delivery stream.

        A tag is a key-value pair that you can define and assign to AWS resources. Tags are metadata. For example, you can add friendly names and descriptions or other types of information that can help you distinguish the delivery stream. For more information about tags, see `Using Cost Allocation Tags <https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html>`_ in the AWS Billing and Cost Management User Guide.

        You can specify up to 50 tags when creating a delivery stream.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-tags
        '''
        return typing.cast(_aws_cdk_core_f4b25747.TagManager, jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="amazonOpenSearchServerlessDestinationConfiguration")
    def amazon_open_search_serverless_destination_configuration(
        self,
    ) -> typing.Optional[typing.Union["CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty", _aws_cdk_core_f4b25747.IResolvable]]:
        '''``AWS::KinesisFirehose::DeliveryStream.AmazonOpenSearchServerlessDestinationConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union["CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty", _aws_cdk_core_f4b25747.IResolvable]], jsii.get(self, "amazonOpenSearchServerlessDestinationConfiguration"))

    @amazon_open_search_serverless_destination_configuration.setter
    def amazon_open_search_serverless_destination_configuration(
        self,
        value: typing.Optional[typing.Union["CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty", _aws_cdk_core_f4b25747.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c86801ae154426393a7642134f4b7977aef011768f1b940a6908f3681972dfee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "amazonOpenSearchServerlessDestinationConfiguration", value)

    @builtins.property
    @jsii.member(jsii_name="amazonopensearchserviceDestinationConfiguration")
    def amazonopensearchservice_destination_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty"]]:
        '''The destination in Amazon OpenSearch Service.

        You can specify only one destination.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty"]], jsii.get(self, "amazonopensearchserviceDestinationConfiguration"))

    @amazonopensearchservice_destination_configuration.setter
    def amazonopensearchservice_destination_configuration(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aadd4c1646bbf6fbae612f0d7d5986a7f194cbe3eb3b54465db6f4dae5aee215)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "amazonopensearchserviceDestinationConfiguration", value)

    @builtins.property
    @jsii.member(jsii_name="deliveryStreamEncryptionConfigurationInput")
    def delivery_stream_encryption_configuration_input(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.DeliveryStreamEncryptionConfigurationInputProperty"]]:
        '''Specifies the type and Amazon Resource Name (ARN) of the CMK to use for Server-Side Encryption (SSE).

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamencryptionconfigurationinput
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.DeliveryStreamEncryptionConfigurationInputProperty"]], jsii.get(self, "deliveryStreamEncryptionConfigurationInput"))

    @delivery_stream_encryption_configuration_input.setter
    def delivery_stream_encryption_configuration_input(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.DeliveryStreamEncryptionConfigurationInputProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__512f499adc93e5ff99f5ecc6e0607d51d002deb7a9e624bb8862d27c3d82d36d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deliveryStreamEncryptionConfigurationInput", value)

    @builtins.property
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> typing.Optional[builtins.str]:
        '''The name of the delivery stream.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deliveryStreamName"))

    @delivery_stream_name.setter
    def delivery_stream_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a86cc9ee22ead48b5c6a0f606dc7770db92d964761118370464e0e4253429e2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deliveryStreamName", value)

    @builtins.property
    @jsii.member(jsii_name="deliveryStreamType")
    def delivery_stream_type(self) -> typing.Optional[builtins.str]:
        '''The delivery stream type. This can be one of the following values:.

        - ``DirectPut`` : Provider applications access the delivery stream directly.
        - ``KinesisStreamAsSource`` : The delivery stream uses a Kinesis data stream as a source.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamtype
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deliveryStreamType"))

    @delivery_stream_type.setter
    def delivery_stream_type(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cab54e5dae0eba2a6f80e6243d420cbfae0b019590fff25d1102b2932f4ed34d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deliveryStreamType", value)

    @builtins.property
    @jsii.member(jsii_name="elasticsearchDestinationConfiguration")
    def elasticsearch_destination_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty"]]:
        '''An Amazon ES destination for the delivery stream.

        Conditional. You must specify only one destination configuration.

        If you change the delivery stream destination from an Amazon ES destination to an Amazon S3 or Amazon Redshift destination, update requires `some interruptions <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-some-interrupt>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty"]], jsii.get(self, "elasticsearchDestinationConfiguration"))

    @elasticsearch_destination_configuration.setter
    def elasticsearch_destination_configuration(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9091a685c5780955cd975c89e7d8f1752333b9cb67fb425eb69d23b06aa4650b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "elasticsearchDestinationConfiguration", value)

    @builtins.property
    @jsii.member(jsii_name="extendedS3DestinationConfiguration")
    def extended_s3_destination_configuration(
        self,
    ) -> typing.Optional[typing.Union["CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty", _aws_cdk_core_f4b25747.IResolvable]]:
        '''An Amazon S3 destination for the delivery stream.

        Conditional. You must specify only one destination configuration.

        If you change the delivery stream destination from an Amazon Extended S3 destination to an Amazon ES destination, update requires `some interruptions <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-some-interrupt>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union["CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty", _aws_cdk_core_f4b25747.IResolvable]], jsii.get(self, "extendedS3DestinationConfiguration"))

    @extended_s3_destination_configuration.setter
    def extended_s3_destination_configuration(
        self,
        value: typing.Optional[typing.Union["CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty", _aws_cdk_core_f4b25747.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01e9be6255aaeb234aef44cbd19630c37c8553fc9e040d49e403d069d39e5378)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extendedS3DestinationConfiguration", value)

    @builtins.property
    @jsii.member(jsii_name="httpEndpointDestinationConfiguration")
    def http_endpoint_destination_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty"]]:
        '''Enables configuring Kinesis Firehose to deliver data to any HTTP endpoint destination.

        You can specify only one destination.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty"]], jsii.get(self, "httpEndpointDestinationConfiguration"))

    @http_endpoint_destination_configuration.setter
    def http_endpoint_destination_configuration(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e03b31573a12a040ea3ca2b8278eddfff1c8165b6f3cc7e2a717128fac66872)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpEndpointDestinationConfiguration", value)

    @builtins.property
    @jsii.member(jsii_name="kinesisStreamSourceConfiguration")
    def kinesis_stream_source_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.KinesisStreamSourceConfigurationProperty"]]:
        '''When a Kinesis stream is used as the source for the delivery stream, a `KinesisStreamSourceConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration.html>`_ containing the Kinesis stream ARN and the role ARN for the source stream.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.KinesisStreamSourceConfigurationProperty"]], jsii.get(self, "kinesisStreamSourceConfiguration"))

    @kinesis_stream_source_configuration.setter
    def kinesis_stream_source_configuration(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.KinesisStreamSourceConfigurationProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1347cbf71c0f028bf61ae6e99295e21f7f03b46543f7a3bb6dda9e7ddce340a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kinesisStreamSourceConfiguration", value)

    @builtins.property
    @jsii.member(jsii_name="redshiftDestinationConfiguration")
    def redshift_destination_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.RedshiftDestinationConfigurationProperty"]]:
        '''An Amazon Redshift destination for the delivery stream.

        Conditional. You must specify only one destination configuration.

        If you change the delivery stream destination from an Amazon Redshift destination to an Amazon ES destination, update requires `some interruptions <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-some-interrupt>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.RedshiftDestinationConfigurationProperty"]], jsii.get(self, "redshiftDestinationConfiguration"))

    @redshift_destination_configuration.setter
    def redshift_destination_configuration(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.RedshiftDestinationConfigurationProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__570fdb34d4a0a174da721cfa15838f8a19e32d5c7fe0dbab48eff7df88a0d832)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redshiftDestinationConfiguration", value)

    @builtins.property
    @jsii.member(jsii_name="s3DestinationConfiguration")
    def s3_destination_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]]:
        '''The ``S3DestinationConfiguration`` property type specifies an Amazon Simple Storage Service (Amazon S3) destination to which Amazon Kinesis Data Firehose (Kinesis Data Firehose) delivers data.

        Conditional. You must specify only one destination configuration.

        If you change the delivery stream destination from an Amazon S3 destination to an Amazon ES destination, update requires `some interruptions <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-some-interrupt>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]], jsii.get(self, "s3DestinationConfiguration"))

    @s3_destination_configuration.setter
    def s3_destination_configuration(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e881ed7d8b9e0e3d4c0871f011670de6b2c8fc3871264ebd22894da1e4f10e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "s3DestinationConfiguration", value)

    @builtins.property
    @jsii.member(jsii_name="splunkDestinationConfiguration")
    def splunk_destination_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.SplunkDestinationConfigurationProperty"]]:
        '''The configuration of a destination in Splunk for the delivery stream.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.SplunkDestinationConfigurationProperty"]], jsii.get(self, "splunkDestinationConfiguration"))

    @splunk_destination_configuration.setter
    def splunk_destination_configuration(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.SplunkDestinationConfigurationProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6b80da4a2ead1bbb6b84bf692e97c17c8bc4e15120edaed6416e28b07eb093e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "splunkDestinationConfiguration", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.AmazonOpenSearchServerlessBufferingHintsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "interval_in_seconds": "intervalInSeconds",
            "size_in_m_bs": "sizeInMBs",
        },
    )
    class AmazonOpenSearchServerlessBufferingHintsProperty:
        def __init__(
            self,
            *,
            interval_in_seconds: typing.Optional[jsii.Number] = None,
            size_in_m_bs: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param interval_in_seconds: ``CfnDeliveryStream.AmazonOpenSearchServerlessBufferingHintsProperty.IntervalInSeconds``.
            :param size_in_m_bs: ``CfnDeliveryStream.AmazonOpenSearchServerlessBufferingHintsProperty.SizeInMBs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserverlessbufferinghints.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                amazon_open_search_serverless_buffering_hints_property = kinesisfirehose.CfnDeliveryStream.AmazonOpenSearchServerlessBufferingHintsProperty(
                    interval_in_seconds=123,
                    size_in_mBs=123
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__6318755922ed8fd8ca972992bc8ddb35826f97088ce3d5406f14b7470fc26596)
                check_type(argname="argument interval_in_seconds", value=interval_in_seconds, expected_type=type_hints["interval_in_seconds"])
                check_type(argname="argument size_in_m_bs", value=size_in_m_bs, expected_type=type_hints["size_in_m_bs"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if interval_in_seconds is not None:
                self._values["interval_in_seconds"] = interval_in_seconds
            if size_in_m_bs is not None:
                self._values["size_in_m_bs"] = size_in_m_bs

        @builtins.property
        def interval_in_seconds(self) -> typing.Optional[jsii.Number]:
            '''``CfnDeliveryStream.AmazonOpenSearchServerlessBufferingHintsProperty.IntervalInSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserverlessbufferinghints.html#cfn-kinesisfirehose-deliverystream-amazonopensearchserverlessbufferinghints-intervalinseconds
            '''
            result = self._values.get("interval_in_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def size_in_m_bs(self) -> typing.Optional[jsii.Number]:
            '''``CfnDeliveryStream.AmazonOpenSearchServerlessBufferingHintsProperty.SizeInMBs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserverlessbufferinghints.html#cfn-kinesisfirehose-deliverystream-amazonopensearchserverlessbufferinghints-sizeinmbs
            '''
            result = self._values.get("size_in_m_bs")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AmazonOpenSearchServerlessBufferingHintsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "index_name": "indexName",
            "role_arn": "roleArn",
            "s3_configuration": "s3Configuration",
            "buffering_hints": "bufferingHints",
            "cloud_watch_logging_options": "cloudWatchLoggingOptions",
            "collection_endpoint": "collectionEndpoint",
            "processing_configuration": "processingConfiguration",
            "retry_options": "retryOptions",
            "s3_backup_mode": "s3BackupMode",
            "vpc_configuration": "vpcConfiguration",
        },
    )
    class AmazonOpenSearchServerlessDestinationConfigurationProperty:
        def __init__(
            self,
            *,
            index_name: builtins.str,
            role_arn: builtins.str,
            s3_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.S3DestinationConfigurationProperty", typing.Dict[builtins.str, typing.Any]]],
            buffering_hints: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.AmazonOpenSearchServerlessBufferingHintsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            cloud_watch_logging_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.CloudWatchLoggingOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            collection_endpoint: typing.Optional[builtins.str] = None,
            processing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.ProcessingConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            retry_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.AmazonOpenSearchServerlessRetryOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            s3_backup_mode: typing.Optional[builtins.str] = None,
            vpc_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.VpcConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''
            :param index_name: ``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.IndexName``.
            :param role_arn: ``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.RoleARN``.
            :param s3_configuration: ``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.S3Configuration``.
            :param buffering_hints: ``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.BufferingHints``.
            :param cloud_watch_logging_options: ``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.CloudWatchLoggingOptions``.
            :param collection_endpoint: ``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.CollectionEndpoint``.
            :param processing_configuration: ``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.ProcessingConfiguration``.
            :param retry_options: ``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.RetryOptions``.
            :param s3_backup_mode: ``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.S3BackupMode``.
            :param vpc_configuration: ``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.VpcConfiguration``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                amazon_open_search_serverless_destination_configuration_property = kinesisfirehose.CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty(
                    index_name="indexName",
                    role_arn="roleArn",
                    s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
                
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
                
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.AmazonOpenSearchServerlessBufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    collection_endpoint="collectionEndpoint",
                    processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                        enabled=False,
                        processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                            type="type",
                
                            # the properties below are optional
                            parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                parameter_name="parameterName",
                                parameter_value="parameterValue"
                            )]
                        )]
                    ),
                    retry_options=kinesisfirehose.CfnDeliveryStream.AmazonOpenSearchServerlessRetryOptionsProperty(
                        duration_in_seconds=123
                    ),
                    s3_backup_mode="s3BackupMode",
                    vpc_configuration=kinesisfirehose.CfnDeliveryStream.VpcConfigurationProperty(
                        role_arn="roleArn",
                        security_group_ids=["securityGroupIds"],
                        subnet_ids=["subnetIds"]
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__191d5f8f456326076b875e4ab295682afcc3800957839cc391ff21194affdbc3)
                check_type(argname="argument index_name", value=index_name, expected_type=type_hints["index_name"])
                check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
                check_type(argname="argument s3_configuration", value=s3_configuration, expected_type=type_hints["s3_configuration"])
                check_type(argname="argument buffering_hints", value=buffering_hints, expected_type=type_hints["buffering_hints"])
                check_type(argname="argument cloud_watch_logging_options", value=cloud_watch_logging_options, expected_type=type_hints["cloud_watch_logging_options"])
                check_type(argname="argument collection_endpoint", value=collection_endpoint, expected_type=type_hints["collection_endpoint"])
                check_type(argname="argument processing_configuration", value=processing_configuration, expected_type=type_hints["processing_configuration"])
                check_type(argname="argument retry_options", value=retry_options, expected_type=type_hints["retry_options"])
                check_type(argname="argument s3_backup_mode", value=s3_backup_mode, expected_type=type_hints["s3_backup_mode"])
                check_type(argname="argument vpc_configuration", value=vpc_configuration, expected_type=type_hints["vpc_configuration"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "index_name": index_name,
                "role_arn": role_arn,
                "s3_configuration": s3_configuration,
            }
            if buffering_hints is not None:
                self._values["buffering_hints"] = buffering_hints
            if cloud_watch_logging_options is not None:
                self._values["cloud_watch_logging_options"] = cloud_watch_logging_options
            if collection_endpoint is not None:
                self._values["collection_endpoint"] = collection_endpoint
            if processing_configuration is not None:
                self._values["processing_configuration"] = processing_configuration
            if retry_options is not None:
                self._values["retry_options"] = retry_options
            if s3_backup_mode is not None:
                self._values["s3_backup_mode"] = s3_backup_mode
            if vpc_configuration is not None:
                self._values["vpc_configuration"] = vpc_configuration

        @builtins.property
        def index_name(self) -> builtins.str:
            '''``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.IndexName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration-indexname
            '''
            result = self._values.get("index_name")
            assert result is not None, "Required property 'index_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.RoleARN``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def s3_configuration(
            self,
        ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]:
            '''``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.S3Configuration``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration-s3configuration
            '''
            result = self._values.get("s3_configuration")
            assert result is not None, "Required property 's3_configuration' is missing"
            return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"], result)

        @builtins.property
        def buffering_hints(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.AmazonOpenSearchServerlessBufferingHintsProperty"]]:
            '''``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.BufferingHints``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration-bufferinghints
            '''
            result = self._values.get("buffering_hints")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.AmazonOpenSearchServerlessBufferingHintsProperty"]], result)

        @builtins.property
        def cloud_watch_logging_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]:
            '''``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.CloudWatchLoggingOptions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration-cloudwatchloggingoptions
            '''
            result = self._values.get("cloud_watch_logging_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]], result)

        @builtins.property
        def collection_endpoint(self) -> typing.Optional[builtins.str]:
            '''``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.CollectionEndpoint``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration-collectionendpoint
            '''
            result = self._values.get("collection_endpoint")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def processing_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]]:
            '''``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.ProcessingConfiguration``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration-processingconfiguration
            '''
            result = self._values.get("processing_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]], result)

        @builtins.property
        def retry_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.AmazonOpenSearchServerlessRetryOptionsProperty"]]:
            '''``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.RetryOptions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration-retryoptions
            '''
            result = self._values.get("retry_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.AmazonOpenSearchServerlessRetryOptionsProperty"]], result)

        @builtins.property
        def s3_backup_mode(self) -> typing.Optional[builtins.str]:
            '''``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.S3BackupMode``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration-s3backupmode
            '''
            result = self._values.get("s3_backup_mode")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def vpc_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.VpcConfigurationProperty"]]:
            '''``CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty.VpcConfiguration``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration-vpcconfiguration
            '''
            result = self._values.get("vpc_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.VpcConfigurationProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AmazonOpenSearchServerlessDestinationConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.AmazonOpenSearchServerlessRetryOptionsProperty",
        jsii_struct_bases=[],
        name_mapping={"duration_in_seconds": "durationInSeconds"},
    )
    class AmazonOpenSearchServerlessRetryOptionsProperty:
        def __init__(
            self,
            *,
            duration_in_seconds: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param duration_in_seconds: ``CfnDeliveryStream.AmazonOpenSearchServerlessRetryOptionsProperty.DurationInSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserverlessretryoptions.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                amazon_open_search_serverless_retry_options_property = kinesisfirehose.CfnDeliveryStream.AmazonOpenSearchServerlessRetryOptionsProperty(
                    duration_in_seconds=123
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__be4eede9b5b29e156fdf4c2b916ba55616d3680e33a7ad306b1e5a9234523d91)
                check_type(argname="argument duration_in_seconds", value=duration_in_seconds, expected_type=type_hints["duration_in_seconds"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if duration_in_seconds is not None:
                self._values["duration_in_seconds"] = duration_in_seconds

        @builtins.property
        def duration_in_seconds(self) -> typing.Optional[jsii.Number]:
            '''``CfnDeliveryStream.AmazonOpenSearchServerlessRetryOptionsProperty.DurationInSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserverlessretryoptions.html#cfn-kinesisfirehose-deliverystream-amazonopensearchserverlessretryoptions-durationinseconds
            '''
            result = self._values.get("duration_in_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AmazonOpenSearchServerlessRetryOptionsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.AmazonopensearchserviceBufferingHintsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "interval_in_seconds": "intervalInSeconds",
            "size_in_m_bs": "sizeInMBs",
        },
    )
    class AmazonopensearchserviceBufferingHintsProperty:
        def __init__(
            self,
            *,
            interval_in_seconds: typing.Optional[jsii.Number] = None,
            size_in_m_bs: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''Describes the buffering to perform before delivering data to the Amazon OpenSearch Service destination.

            :param interval_in_seconds: Buffer incoming data for the specified period of time, in seconds, before delivering it to the destination. The default value is 300 (5 minutes).
            :param size_in_m_bs: Buffer incoming data to the specified size, in MBs, before delivering it to the destination. The default value is 5. We recommend setting this parameter to a value greater than the amount of data you typically ingest into the delivery stream in 10 seconds. For example, if you typically ingest data at 1 MB/sec, the value should be 10 MB or higher.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicebufferinghints.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                amazonopensearchservice_buffering_hints_property = kinesisfirehose.CfnDeliveryStream.AmazonopensearchserviceBufferingHintsProperty(
                    interval_in_seconds=123,
                    size_in_mBs=123
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__2f2b3c67b90885c6ef3156c108da39a36f93645866a62a34ccc191692d34a129)
                check_type(argname="argument interval_in_seconds", value=interval_in_seconds, expected_type=type_hints["interval_in_seconds"])
                check_type(argname="argument size_in_m_bs", value=size_in_m_bs, expected_type=type_hints["size_in_m_bs"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if interval_in_seconds is not None:
                self._values["interval_in_seconds"] = interval_in_seconds
            if size_in_m_bs is not None:
                self._values["size_in_m_bs"] = size_in_m_bs

        @builtins.property
        def interval_in_seconds(self) -> typing.Optional[jsii.Number]:
            '''Buffer incoming data for the specified period of time, in seconds, before delivering it to the destination.

            The default value is 300 (5 minutes).

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicebufferinghints.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicebufferinghints-intervalinseconds
            '''
            result = self._values.get("interval_in_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def size_in_m_bs(self) -> typing.Optional[jsii.Number]:
            '''Buffer incoming data to the specified size, in MBs, before delivering it to the destination.

            The default value is 5. We recommend setting this parameter to a value greater than the amount of data you typically ingest into the delivery stream in 10 seconds. For example, if you typically ingest data at 1 MB/sec, the value should be 10 MB or higher.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicebufferinghints.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicebufferinghints-sizeinmbs
            '''
            result = self._values.get("size_in_m_bs")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AmazonopensearchserviceBufferingHintsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "index_name": "indexName",
            "role_arn": "roleArn",
            "s3_configuration": "s3Configuration",
            "buffering_hints": "bufferingHints",
            "cloud_watch_logging_options": "cloudWatchLoggingOptions",
            "cluster_endpoint": "clusterEndpoint",
            "document_id_options": "documentIdOptions",
            "domain_arn": "domainArn",
            "index_rotation_period": "indexRotationPeriod",
            "processing_configuration": "processingConfiguration",
            "retry_options": "retryOptions",
            "s3_backup_mode": "s3BackupMode",
            "type_name": "typeName",
            "vpc_configuration": "vpcConfiguration",
        },
    )
    class AmazonopensearchserviceDestinationConfigurationProperty:
        def __init__(
            self,
            *,
            index_name: builtins.str,
            role_arn: builtins.str,
            s3_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.S3DestinationConfigurationProperty", typing.Dict[builtins.str, typing.Any]]],
            buffering_hints: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.AmazonopensearchserviceBufferingHintsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            cloud_watch_logging_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.CloudWatchLoggingOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            cluster_endpoint: typing.Optional[builtins.str] = None,
            document_id_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.DocumentIdOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            domain_arn: typing.Optional[builtins.str] = None,
            index_rotation_period: typing.Optional[builtins.str] = None,
            processing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.ProcessingConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            retry_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.AmazonopensearchserviceRetryOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            s3_backup_mode: typing.Optional[builtins.str] = None,
            type_name: typing.Optional[builtins.str] = None,
            vpc_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.VpcConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''Describes the configuration of a destination in Amazon OpenSearch Service.

            :param index_name: The Amazon OpenSearch Service index name.
            :param role_arn: The Amazon Resource Name (ARN) of the IAM role to be assumed by Kinesis Data Firehose for calling the Amazon OpenSearch Service Configuration API and for indexing documents.
            :param s3_configuration: Describes the configuration of a destination in Amazon S3.
            :param buffering_hints: The buffering options. If no value is specified, the default values for AmazonopensearchserviceBufferingHints are used.
            :param cloud_watch_logging_options: Describes the Amazon CloudWatch logging options for your delivery stream.
            :param cluster_endpoint: The endpoint to use when communicating with the cluster. Specify either this ClusterEndpoint or the DomainARN field.
            :param document_id_options: ``CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty.DocumentIdOptions``.
            :param domain_arn: The ARN of the Amazon OpenSearch Service domain.
            :param index_rotation_period: The Amazon OpenSearch Service index rotation period. Index rotation appends a timestamp to the IndexName to facilitate the expiration of old data.
            :param processing_configuration: Describes a data processing configuration.
            :param retry_options: The retry behavior in case Kinesis Data Firehose is unable to deliver documents to Amazon OpenSearch Service. The default value is 300 (5 minutes).
            :param s3_backup_mode: Defines how documents should be delivered to Amazon S3.
            :param type_name: The Amazon OpenSearch Service type name.
            :param vpc_configuration: The details of the VPC of the Amazon OpenSearch Service destination.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                amazonopensearchservice_destination_configuration_property = kinesisfirehose.CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty(
                    index_name="indexName",
                    role_arn="roleArn",
                    s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
                
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
                
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.AmazonopensearchserviceBufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    cluster_endpoint="clusterEndpoint",
                    document_id_options=kinesisfirehose.CfnDeliveryStream.DocumentIdOptionsProperty(
                        default_document_id_format="defaultDocumentIdFormat"
                    ),
                    domain_arn="domainArn",
                    index_rotation_period="indexRotationPeriod",
                    processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                        enabled=False,
                        processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                            type="type",
                
                            # the properties below are optional
                            parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                parameter_name="parameterName",
                                parameter_value="parameterValue"
                            )]
                        )]
                    ),
                    retry_options=kinesisfirehose.CfnDeliveryStream.AmazonopensearchserviceRetryOptionsProperty(
                        duration_in_seconds=123
                    ),
                    s3_backup_mode="s3BackupMode",
                    type_name="typeName",
                    vpc_configuration=kinesisfirehose.CfnDeliveryStream.VpcConfigurationProperty(
                        role_arn="roleArn",
                        security_group_ids=["securityGroupIds"],
                        subnet_ids=["subnetIds"]
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__ad314ac58d6049ce5236a0e8b5dc52c811c3978af58e70e435d9062aa86c415a)
                check_type(argname="argument index_name", value=index_name, expected_type=type_hints["index_name"])
                check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
                check_type(argname="argument s3_configuration", value=s3_configuration, expected_type=type_hints["s3_configuration"])
                check_type(argname="argument buffering_hints", value=buffering_hints, expected_type=type_hints["buffering_hints"])
                check_type(argname="argument cloud_watch_logging_options", value=cloud_watch_logging_options, expected_type=type_hints["cloud_watch_logging_options"])
                check_type(argname="argument cluster_endpoint", value=cluster_endpoint, expected_type=type_hints["cluster_endpoint"])
                check_type(argname="argument document_id_options", value=document_id_options, expected_type=type_hints["document_id_options"])
                check_type(argname="argument domain_arn", value=domain_arn, expected_type=type_hints["domain_arn"])
                check_type(argname="argument index_rotation_period", value=index_rotation_period, expected_type=type_hints["index_rotation_period"])
                check_type(argname="argument processing_configuration", value=processing_configuration, expected_type=type_hints["processing_configuration"])
                check_type(argname="argument retry_options", value=retry_options, expected_type=type_hints["retry_options"])
                check_type(argname="argument s3_backup_mode", value=s3_backup_mode, expected_type=type_hints["s3_backup_mode"])
                check_type(argname="argument type_name", value=type_name, expected_type=type_hints["type_name"])
                check_type(argname="argument vpc_configuration", value=vpc_configuration, expected_type=type_hints["vpc_configuration"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "index_name": index_name,
                "role_arn": role_arn,
                "s3_configuration": s3_configuration,
            }
            if buffering_hints is not None:
                self._values["buffering_hints"] = buffering_hints
            if cloud_watch_logging_options is not None:
                self._values["cloud_watch_logging_options"] = cloud_watch_logging_options
            if cluster_endpoint is not None:
                self._values["cluster_endpoint"] = cluster_endpoint
            if document_id_options is not None:
                self._values["document_id_options"] = document_id_options
            if domain_arn is not None:
                self._values["domain_arn"] = domain_arn
            if index_rotation_period is not None:
                self._values["index_rotation_period"] = index_rotation_period
            if processing_configuration is not None:
                self._values["processing_configuration"] = processing_configuration
            if retry_options is not None:
                self._values["retry_options"] = retry_options
            if s3_backup_mode is not None:
                self._values["s3_backup_mode"] = s3_backup_mode
            if type_name is not None:
                self._values["type_name"] = type_name
            if vpc_configuration is not None:
                self._values["vpc_configuration"] = vpc_configuration

        @builtins.property
        def index_name(self) -> builtins.str:
            '''The Amazon OpenSearch Service index name.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration-indexname
            '''
            result = self._values.get("index_name")
            assert result is not None, "Required property 'index_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''The Amazon Resource Name (ARN) of the IAM role to be assumed by Kinesis Data Firehose for calling the Amazon OpenSearch Service Configuration API and for indexing documents.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def s3_configuration(
            self,
        ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]:
            '''Describes the configuration of a destination in Amazon S3.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration-s3configuration
            '''
            result = self._values.get("s3_configuration")
            assert result is not None, "Required property 's3_configuration' is missing"
            return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"], result)

        @builtins.property
        def buffering_hints(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.AmazonopensearchserviceBufferingHintsProperty"]]:
            '''The buffering options.

            If no value is specified, the default values for AmazonopensearchserviceBufferingHints are used.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration-bufferinghints
            '''
            result = self._values.get("buffering_hints")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.AmazonopensearchserviceBufferingHintsProperty"]], result)

        @builtins.property
        def cloud_watch_logging_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]:
            '''Describes the Amazon CloudWatch logging options for your delivery stream.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration-cloudwatchloggingoptions
            '''
            result = self._values.get("cloud_watch_logging_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]], result)

        @builtins.property
        def cluster_endpoint(self) -> typing.Optional[builtins.str]:
            '''The endpoint to use when communicating with the cluster.

            Specify either this ClusterEndpoint or the DomainARN field.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration-clusterendpoint
            '''
            result = self._values.get("cluster_endpoint")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def document_id_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.DocumentIdOptionsProperty"]]:
            '''``CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty.DocumentIdOptions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration-documentidoptions
            '''
            result = self._values.get("document_id_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.DocumentIdOptionsProperty"]], result)

        @builtins.property
        def domain_arn(self) -> typing.Optional[builtins.str]:
            '''The ARN of the Amazon OpenSearch Service domain.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration-domainarn
            '''
            result = self._values.get("domain_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def index_rotation_period(self) -> typing.Optional[builtins.str]:
            '''The Amazon OpenSearch Service index rotation period.

            Index rotation appends a timestamp to the IndexName to facilitate the expiration of old data.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration-indexrotationperiod
            '''
            result = self._values.get("index_rotation_period")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def processing_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]]:
            '''Describes a data processing configuration.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration-processingconfiguration
            '''
            result = self._values.get("processing_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]], result)

        @builtins.property
        def retry_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.AmazonopensearchserviceRetryOptionsProperty"]]:
            '''The retry behavior in case Kinesis Data Firehose is unable to deliver documents to Amazon OpenSearch Service.

            The default value is 300 (5 minutes).

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration-retryoptions
            '''
            result = self._values.get("retry_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.AmazonopensearchserviceRetryOptionsProperty"]], result)

        @builtins.property
        def s3_backup_mode(self) -> typing.Optional[builtins.str]:
            '''Defines how documents should be delivered to Amazon S3.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration-s3backupmode
            '''
            result = self._values.get("s3_backup_mode")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def type_name(self) -> typing.Optional[builtins.str]:
            '''The Amazon OpenSearch Service type name.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration-typename
            '''
            result = self._values.get("type_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def vpc_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.VpcConfigurationProperty"]]:
            '''The details of the VPC of the Amazon OpenSearch Service destination.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration-vpcconfiguration
            '''
            result = self._values.get("vpc_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.VpcConfigurationProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AmazonopensearchserviceDestinationConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.AmazonopensearchserviceRetryOptionsProperty",
        jsii_struct_bases=[],
        name_mapping={"duration_in_seconds": "durationInSeconds"},
    )
    class AmazonopensearchserviceRetryOptionsProperty:
        def __init__(
            self,
            *,
            duration_in_seconds: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''Configures retry behavior in case Kinesis Data Firehose is unable to deliver documents to Amazon OpenSearch Service.

            :param duration_in_seconds: After an initial failure to deliver to Amazon OpenSearch Service, the total amount of time during which Kinesis Data Firehose retries delivery (including the first attempt). After this time has elapsed, the failed documents are written to Amazon S3. Default value is 300 seconds (5 minutes). A value of 0 (zero) results in no retries.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserviceretryoptions.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                amazonopensearchservice_retry_options_property = kinesisfirehose.CfnDeliveryStream.AmazonopensearchserviceRetryOptionsProperty(
                    duration_in_seconds=123
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__230dd3485a7e2596998fc0170f5a7cfe8e1953f937ed1e2c9228ce7ef42e3b43)
                check_type(argname="argument duration_in_seconds", value=duration_in_seconds, expected_type=type_hints["duration_in_seconds"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if duration_in_seconds is not None:
                self._values["duration_in_seconds"] = duration_in_seconds

        @builtins.property
        def duration_in_seconds(self) -> typing.Optional[jsii.Number]:
            '''After an initial failure to deliver to Amazon OpenSearch Service, the total amount of time during which Kinesis Data Firehose retries delivery (including the first attempt).

            After this time has elapsed, the failed documents are written to Amazon S3. Default value is 300 seconds (5 minutes). A value of 0 (zero) results in no retries.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-amazonopensearchserviceretryoptions.html#cfn-kinesisfirehose-deliverystream-amazonopensearchserviceretryoptions-durationinseconds
            '''
            result = self._values.get("duration_in_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AmazonopensearchserviceRetryOptionsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "interval_in_seconds": "intervalInSeconds",
            "size_in_m_bs": "sizeInMBs",
        },
    )
    class BufferingHintsProperty:
        def __init__(
            self,
            *,
            interval_in_seconds: typing.Optional[jsii.Number] = None,
            size_in_m_bs: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''The ``BufferingHints`` property type specifies how Amazon Kinesis Data Firehose (Kinesis Data Firehose) buffers incoming data before delivering it to the destination.

            The first buffer condition that is satisfied triggers Kinesis Data Firehose to deliver the data.

            :param interval_in_seconds: The length of time, in seconds, that Kinesis Data Firehose buffers incoming data before delivering it to the destination. For valid values, see the ``IntervalInSeconds`` content for the `BufferingHints <https://docs.aws.amazon.com/firehose/latest/APIReference/API_BufferingHints.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .
            :param size_in_m_bs: The size of the buffer, in MBs, that Kinesis Data Firehose uses for incoming data before delivering it to the destination. For valid values, see the ``SizeInMBs`` content for the `BufferingHints <https://docs.aws.amazon.com/firehose/latest/APIReference/API_BufferingHints.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-bufferinghints.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                buffering_hints_property = kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                    interval_in_seconds=123,
                    size_in_mBs=123
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__3eac0f9fad5da142f5ee5fd379e0a09ab57bd4bca2bb92205bf66efc858d7629)
                check_type(argname="argument interval_in_seconds", value=interval_in_seconds, expected_type=type_hints["interval_in_seconds"])
                check_type(argname="argument size_in_m_bs", value=size_in_m_bs, expected_type=type_hints["size_in_m_bs"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if interval_in_seconds is not None:
                self._values["interval_in_seconds"] = interval_in_seconds
            if size_in_m_bs is not None:
                self._values["size_in_m_bs"] = size_in_m_bs

        @builtins.property
        def interval_in_seconds(self) -> typing.Optional[jsii.Number]:
            '''The length of time, in seconds, that Kinesis Data Firehose buffers incoming data before delivering it to the destination.

            For valid values, see the ``IntervalInSeconds`` content for the `BufferingHints <https://docs.aws.amazon.com/firehose/latest/APIReference/API_BufferingHints.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-bufferinghints.html#cfn-kinesisfirehose-deliverystream-bufferinghints-intervalinseconds
            '''
            result = self._values.get("interval_in_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def size_in_m_bs(self) -> typing.Optional[jsii.Number]:
            '''The size of the buffer, in MBs, that Kinesis Data Firehose uses for incoming data before delivering it to the destination.

            For valid values, see the ``SizeInMBs`` content for the `BufferingHints <https://docs.aws.amazon.com/firehose/latest/APIReference/API_BufferingHints.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-bufferinghints.html#cfn-kinesisfirehose-deliverystream-bufferinghints-sizeinmbs
            '''
            result = self._values.get("size_in_m_bs")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BufferingHintsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "enabled": "enabled",
            "log_group_name": "logGroupName",
            "log_stream_name": "logStreamName",
        },
    )
    class CloudWatchLoggingOptionsProperty:
        def __init__(
            self,
            *,
            enabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            log_group_name: typing.Optional[builtins.str] = None,
            log_stream_name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The ``CloudWatchLoggingOptions`` property type specifies Amazon CloudWatch Logs (CloudWatch Logs) logging options that Amazon Kinesis Data Firehose (Kinesis Data Firehose) uses for the delivery stream.

            :param enabled: Indicates whether CloudWatch Logs logging is enabled.
            :param log_group_name: The name of the CloudWatch Logs log group that contains the log stream that Kinesis Data Firehose will use. Conditional. If you enable logging, you must specify this property.
            :param log_stream_name: The name of the CloudWatch Logs log stream that Kinesis Data Firehose uses to send logs about data delivery. Conditional. If you enable logging, you must specify this property.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-cloudwatchloggingoptions.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                cloud_watch_logging_options_property = kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                    enabled=False,
                    log_group_name="logGroupName",
                    log_stream_name="logStreamName"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__47b3cddd4a74f65c11eaaca2bb5076e207151acc94509338c126f3ad29e04b5c)
                check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
                check_type(argname="argument log_group_name", value=log_group_name, expected_type=type_hints["log_group_name"])
                check_type(argname="argument log_stream_name", value=log_stream_name, expected_type=type_hints["log_stream_name"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if enabled is not None:
                self._values["enabled"] = enabled
            if log_group_name is not None:
                self._values["log_group_name"] = log_group_name
            if log_stream_name is not None:
                self._values["log_stream_name"] = log_stream_name

        @builtins.property
        def enabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''Indicates whether CloudWatch Logs logging is enabled.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-cloudwatchloggingoptions.html#cfn-kinesisfirehose-deliverystream-cloudwatchloggingoptions-enabled
            '''
            result = self._values.get("enabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def log_group_name(self) -> typing.Optional[builtins.str]:
            '''The name of the CloudWatch Logs log group that contains the log stream that Kinesis Data Firehose will use.

            Conditional. If you enable logging, you must specify this property.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-cloudwatchloggingoptions.html#cfn-kinesisfirehose-deliverystream-cloudwatchloggingoptions-loggroupname
            '''
            result = self._values.get("log_group_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def log_stream_name(self) -> typing.Optional[builtins.str]:
            '''The name of the CloudWatch Logs log stream that Kinesis Data Firehose uses to send logs about data delivery.

            Conditional. If you enable logging, you must specify this property.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-cloudwatchloggingoptions.html#cfn-kinesisfirehose-deliverystream-cloudwatchloggingoptions-logstreamname
            '''
            result = self._values.get("log_stream_name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CloudWatchLoggingOptionsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.CopyCommandProperty",
        jsii_struct_bases=[],
        name_mapping={
            "data_table_name": "dataTableName",
            "copy_options": "copyOptions",
            "data_table_columns": "dataTableColumns",
        },
    )
    class CopyCommandProperty:
        def __init__(
            self,
            *,
            data_table_name: builtins.str,
            copy_options: typing.Optional[builtins.str] = None,
            data_table_columns: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The ``CopyCommand`` property type configures the Amazon Redshift ``COPY`` command that Amazon Kinesis Data Firehose (Kinesis Data Firehose) uses to load data into an Amazon Redshift cluster from an Amazon S3 bucket.

            :param data_table_name: The name of the target table. The table must already exist in the database.
            :param copy_options: Parameters to use with the Amazon Redshift ``COPY`` command. For examples, see the ``CopyOptions`` content for the `CopyCommand <https://docs.aws.amazon.com/firehose/latest/APIReference/API_CopyCommand.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .
            :param data_table_columns: A comma-separated list of column names.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-copycommand.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                copy_command_property = kinesisfirehose.CfnDeliveryStream.CopyCommandProperty(
                    data_table_name="dataTableName",
                
                    # the properties below are optional
                    copy_options="copyOptions",
                    data_table_columns="dataTableColumns"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__b8494ac7d53df40dbd76bfaf8c23ce596870c07736c6bdede0f1e9c311ec1aea)
                check_type(argname="argument data_table_name", value=data_table_name, expected_type=type_hints["data_table_name"])
                check_type(argname="argument copy_options", value=copy_options, expected_type=type_hints["copy_options"])
                check_type(argname="argument data_table_columns", value=data_table_columns, expected_type=type_hints["data_table_columns"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "data_table_name": data_table_name,
            }
            if copy_options is not None:
                self._values["copy_options"] = copy_options
            if data_table_columns is not None:
                self._values["data_table_columns"] = data_table_columns

        @builtins.property
        def data_table_name(self) -> builtins.str:
            '''The name of the target table.

            The table must already exist in the database.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-copycommand.html#cfn-kinesisfirehose-deliverystream-copycommand-datatablename
            '''
            result = self._values.get("data_table_name")
            assert result is not None, "Required property 'data_table_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def copy_options(self) -> typing.Optional[builtins.str]:
            '''Parameters to use with the Amazon Redshift ``COPY`` command.

            For examples, see the ``CopyOptions`` content for the `CopyCommand <https://docs.aws.amazon.com/firehose/latest/APIReference/API_CopyCommand.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-copycommand.html#cfn-kinesisfirehose-deliverystream-copycommand-copyoptions
            '''
            result = self._values.get("copy_options")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def data_table_columns(self) -> typing.Optional[builtins.str]:
            '''A comma-separated list of column names.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-copycommand.html#cfn-kinesisfirehose-deliverystream-copycommand-datatablecolumns
            '''
            result = self._values.get("data_table_columns")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CopyCommandProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.DataFormatConversionConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "enabled": "enabled",
            "input_format_configuration": "inputFormatConfiguration",
            "output_format_configuration": "outputFormatConfiguration",
            "schema_configuration": "schemaConfiguration",
        },
    )
    class DataFormatConversionConfigurationProperty:
        def __init__(
            self,
            *,
            enabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            input_format_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.InputFormatConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            output_format_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.OutputFormatConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            schema_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.SchemaConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''Specifies that you want Kinesis Data Firehose to convert data from the JSON format to the Parquet or ORC format before writing it to Amazon S3.

            Kinesis Data Firehose uses the serializer and deserializer that you specify, in addition to the column information from the AWS Glue table, to deserialize your input data from JSON and then serialize it to the Parquet or ORC format. For more information, see `Kinesis Data Firehose Record Format Conversion <https://docs.aws.amazon.com/firehose/latest/dev/record-format-conversion.html>`_ .

            :param enabled: Defaults to ``true`` . Set it to ``false`` if you want to disable format conversion while preserving the configuration details.
            :param input_format_configuration: Specifies the deserializer that you want Kinesis Data Firehose to use to convert the format of your data from JSON. This parameter is required if ``Enabled`` is set to true.
            :param output_format_configuration: Specifies the serializer that you want Kinesis Data Firehose to use to convert the format of your data to the Parquet or ORC format. This parameter is required if ``Enabled`` is set to true.
            :param schema_configuration: Specifies the AWS Glue Data Catalog table that contains the column information. This parameter is required if ``Enabled`` is set to true.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                data_format_conversion_configuration_property = kinesisfirehose.CfnDeliveryStream.DataFormatConversionConfigurationProperty(
                    enabled=False,
                    input_format_configuration=kinesisfirehose.CfnDeliveryStream.InputFormatConfigurationProperty(
                        deserializer=kinesisfirehose.CfnDeliveryStream.DeserializerProperty(
                            hive_json_ser_de=kinesisfirehose.CfnDeliveryStream.HiveJsonSerDeProperty(
                                timestamp_formats=["timestampFormats"]
                            ),
                            open_xJson_ser_de=kinesisfirehose.CfnDeliveryStream.OpenXJsonSerDeProperty(
                                case_insensitive=False,
                                column_to_json_key_mappings={
                                    "column_to_json_key_mappings_key": "columnToJsonKeyMappings"
                                },
                                convert_dots_in_json_keys_to_underscores=False
                            )
                        )
                    ),
                    output_format_configuration=kinesisfirehose.CfnDeliveryStream.OutputFormatConfigurationProperty(
                        serializer=kinesisfirehose.CfnDeliveryStream.SerializerProperty(
                            orc_ser_de=kinesisfirehose.CfnDeliveryStream.OrcSerDeProperty(
                                block_size_bytes=123,
                                bloom_filter_columns=["bloomFilterColumns"],
                                bloom_filter_false_positive_probability=123,
                                compression="compression",
                                dictionary_key_threshold=123,
                                enable_padding=False,
                                format_version="formatVersion",
                                padding_tolerance=123,
                                row_index_stride=123,
                                stripe_size_bytes=123
                            ),
                            parquet_ser_de=kinesisfirehose.CfnDeliveryStream.ParquetSerDeProperty(
                                block_size_bytes=123,
                                compression="compression",
                                enable_dictionary_compression=False,
                                max_padding_bytes=123,
                                page_size_bytes=123,
                                writer_version="writerVersion"
                            )
                        )
                    ),
                    schema_configuration=kinesisfirehose.CfnDeliveryStream.SchemaConfigurationProperty(
                        catalog_id="catalogId",
                        database_name="databaseName",
                        region="region",
                        role_arn="roleArn",
                        table_name="tableName",
                        version_id="versionId"
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__18050cc8b274a82529d91064182ad7a96ce39fd20eea16d8355bea41ebd5ee30)
                check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
                check_type(argname="argument input_format_configuration", value=input_format_configuration, expected_type=type_hints["input_format_configuration"])
                check_type(argname="argument output_format_configuration", value=output_format_configuration, expected_type=type_hints["output_format_configuration"])
                check_type(argname="argument schema_configuration", value=schema_configuration, expected_type=type_hints["schema_configuration"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if enabled is not None:
                self._values["enabled"] = enabled
            if input_format_configuration is not None:
                self._values["input_format_configuration"] = input_format_configuration
            if output_format_configuration is not None:
                self._values["output_format_configuration"] = output_format_configuration
            if schema_configuration is not None:
                self._values["schema_configuration"] = schema_configuration

        @builtins.property
        def enabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''Defaults to ``true`` .

            Set it to ``false`` if you want to disable format conversion while preserving the configuration details.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html#cfn-kinesisfirehose-deliverystream-dataformatconversionconfiguration-enabled
            '''
            result = self._values.get("enabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def input_format_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.InputFormatConfigurationProperty"]]:
            '''Specifies the deserializer that you want Kinesis Data Firehose to use to convert the format of your data from JSON.

            This parameter is required if ``Enabled`` is set to true.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html#cfn-kinesisfirehose-deliverystream-dataformatconversionconfiguration-inputformatconfiguration
            '''
            result = self._values.get("input_format_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.InputFormatConfigurationProperty"]], result)

        @builtins.property
        def output_format_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.OutputFormatConfigurationProperty"]]:
            '''Specifies the serializer that you want Kinesis Data Firehose to use to convert the format of your data to the Parquet or ORC format.

            This parameter is required if ``Enabled`` is set to true.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html#cfn-kinesisfirehose-deliverystream-dataformatconversionconfiguration-outputformatconfiguration
            '''
            result = self._values.get("output_format_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.OutputFormatConfigurationProperty"]], result)

        @builtins.property
        def schema_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.SchemaConfigurationProperty"]]:
            '''Specifies the AWS Glue Data Catalog table that contains the column information.

            This parameter is required if ``Enabled`` is set to true.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dataformatconversionconfiguration.html#cfn-kinesisfirehose-deliverystream-dataformatconversionconfiguration-schemaconfiguration
            '''
            result = self._values.get("schema_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.SchemaConfigurationProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DataFormatConversionConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.DeliveryStreamEncryptionConfigurationInputProperty",
        jsii_struct_bases=[],
        name_mapping={"key_type": "keyType", "key_arn": "keyArn"},
    )
    class DeliveryStreamEncryptionConfigurationInputProperty:
        def __init__(
            self,
            *,
            key_type: builtins.str,
            key_arn: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Specifies the type and Amazon Resource Name (ARN) of the CMK to use for Server-Side Encryption (SSE).

            :param key_type: Indicates the type of customer master key (CMK) to use for encryption. The default setting is ``AWS_OWNED_CMK`` . For more information about CMKs, see `Customer Master Keys (CMKs) <https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#master_keys>`_ . You can use a CMK of type CUSTOMER_MANAGED_CMK to encrypt up to 500 delivery streams. .. epigraph:: To encrypt your delivery stream, use symmetric CMKs. Kinesis Data Firehose doesn't support asymmetric CMKs. For information about symmetric and asymmetric CMKs, see `About Symmetric and Asymmetric CMKs <https://docs.aws.amazon.com/kms/latest/developerguide/symm-asymm-concepts.html>`_ in the AWS Key Management Service developer guide.
            :param key_arn: If you set ``KeyType`` to ``CUSTOMER_MANAGED_CMK`` , you must specify the Amazon Resource Name (ARN) of the CMK. If you set ``KeyType`` to ``AWS _OWNED_CMK`` , Kinesis Data Firehose uses a service-account CMK.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-deliverystreamencryptionconfigurationinput.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                delivery_stream_encryption_configuration_input_property = kinesisfirehose.CfnDeliveryStream.DeliveryStreamEncryptionConfigurationInputProperty(
                    key_type="keyType",
                
                    # the properties below are optional
                    key_arn="keyArn"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__fa17125c6fdc739bce158647575c0a8d3b0aa54ceabe4bc9ec6ea52f44e7cfd4)
                check_type(argname="argument key_type", value=key_type, expected_type=type_hints["key_type"])
                check_type(argname="argument key_arn", value=key_arn, expected_type=type_hints["key_arn"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "key_type": key_type,
            }
            if key_arn is not None:
                self._values["key_arn"] = key_arn

        @builtins.property
        def key_type(self) -> builtins.str:
            '''Indicates the type of customer master key (CMK) to use for encryption.

            The default setting is ``AWS_OWNED_CMK`` . For more information about CMKs, see `Customer Master Keys (CMKs) <https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#master_keys>`_ .

            You can use a CMK of type CUSTOMER_MANAGED_CMK to encrypt up to 500 delivery streams.
            .. epigraph::

               To encrypt your delivery stream, use symmetric CMKs. Kinesis Data Firehose doesn't support asymmetric CMKs. For information about symmetric and asymmetric CMKs, see `About Symmetric and Asymmetric CMKs <https://docs.aws.amazon.com/kms/latest/developerguide/symm-asymm-concepts.html>`_ in the AWS Key Management Service developer guide.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-deliverystreamencryptionconfigurationinput.html#cfn-kinesisfirehose-deliverystream-deliverystreamencryptionconfigurationinput-keytype
            '''
            result = self._values.get("key_type")
            assert result is not None, "Required property 'key_type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def key_arn(self) -> typing.Optional[builtins.str]:
            '''If you set ``KeyType`` to ``CUSTOMER_MANAGED_CMK`` , you must specify the Amazon Resource Name (ARN) of the CMK.

            If you set ``KeyType`` to ``AWS _OWNED_CMK`` , Kinesis Data Firehose uses a service-account CMK.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-deliverystreamencryptionconfigurationinput.html#cfn-kinesisfirehose-deliverystream-deliverystreamencryptionconfigurationinput-keyarn
            '''
            result = self._values.get("key_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DeliveryStreamEncryptionConfigurationInputProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.DeserializerProperty",
        jsii_struct_bases=[],
        name_mapping={
            "hive_json_ser_de": "hiveJsonSerDe",
            "open_x_json_ser_de": "openXJsonSerDe",
        },
    )
    class DeserializerProperty:
        def __init__(
            self,
            *,
            hive_json_ser_de: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.HiveJsonSerDeProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            open_x_json_ser_de: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.OpenXJsonSerDeProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''The deserializer you want Kinesis Data Firehose to use for converting the input data from JSON.

            Kinesis Data Firehose then serializes the data to its final format using the ``Serializer`` . Kinesis Data Firehose supports two types of deserializers: the `Apache Hive JSON SerDe <https://docs.aws.amazon.com/https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL#LanguageManualDDL-JSON>`_ and the `OpenX JSON SerDe <https://docs.aws.amazon.com/https://github.com/rcongiu/Hive-JSON-Serde>`_ .

            :param hive_json_ser_de: The native Hive / HCatalog JsonSerDe. Used by Kinesis Data Firehose for deserializing data, which means converting it from the JSON format in preparation for serializing it to the Parquet or ORC format. This is one of two deserializers you can choose, depending on which one offers the functionality you need. The other option is the OpenX SerDe.
            :param open_x_json_ser_de: The OpenX SerDe. Used by Kinesis Data Firehose for deserializing data, which means converting it from the JSON format in preparation for serializing it to the Parquet or ORC format. This is one of two deserializers you can choose, depending on which one offers the functionality you need. The other option is the native Hive / HCatalog JsonSerDe.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-deserializer.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                deserializer_property = kinesisfirehose.CfnDeliveryStream.DeserializerProperty(
                    hive_json_ser_de=kinesisfirehose.CfnDeliveryStream.HiveJsonSerDeProperty(
                        timestamp_formats=["timestampFormats"]
                    ),
                    open_xJson_ser_de=kinesisfirehose.CfnDeliveryStream.OpenXJsonSerDeProperty(
                        case_insensitive=False,
                        column_to_json_key_mappings={
                            "column_to_json_key_mappings_key": "columnToJsonKeyMappings"
                        },
                        convert_dots_in_json_keys_to_underscores=False
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__fc601a7de36b01aab527f525b17ec0b11adbf4d1f9616e1eb3d75466c39cfb3f)
                check_type(argname="argument hive_json_ser_de", value=hive_json_ser_de, expected_type=type_hints["hive_json_ser_de"])
                check_type(argname="argument open_x_json_ser_de", value=open_x_json_ser_de, expected_type=type_hints["open_x_json_ser_de"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if hive_json_ser_de is not None:
                self._values["hive_json_ser_de"] = hive_json_ser_de
            if open_x_json_ser_de is not None:
                self._values["open_x_json_ser_de"] = open_x_json_ser_de

        @builtins.property
        def hive_json_ser_de(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.HiveJsonSerDeProperty"]]:
            '''The native Hive / HCatalog JsonSerDe.

            Used by Kinesis Data Firehose for deserializing data, which means converting it from the JSON format in preparation for serializing it to the Parquet or ORC format. This is one of two deserializers you can choose, depending on which one offers the functionality you need. The other option is the OpenX SerDe.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-deserializer.html#cfn-kinesisfirehose-deliverystream-deserializer-hivejsonserde
            '''
            result = self._values.get("hive_json_ser_de")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.HiveJsonSerDeProperty"]], result)

        @builtins.property
        def open_x_json_ser_de(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.OpenXJsonSerDeProperty"]]:
            '''The OpenX SerDe.

            Used by Kinesis Data Firehose for deserializing data, which means converting it from the JSON format in preparation for serializing it to the Parquet or ORC format. This is one of two deserializers you can choose, depending on which one offers the functionality you need. The other option is the native Hive / HCatalog JsonSerDe.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-deserializer.html#cfn-kinesisfirehose-deliverystream-deserializer-openxjsonserde
            '''
            result = self._values.get("open_x_json_ser_de")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.OpenXJsonSerDeProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DeserializerProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.DocumentIdOptionsProperty",
        jsii_struct_bases=[],
        name_mapping={"default_document_id_format": "defaultDocumentIdFormat"},
    )
    class DocumentIdOptionsProperty:
        def __init__(self, *, default_document_id_format: builtins.str) -> None:
            '''
            :param default_document_id_format: ``CfnDeliveryStream.DocumentIdOptionsProperty.DefaultDocumentIdFormat``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-documentidoptions.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                document_id_options_property = kinesisfirehose.CfnDeliveryStream.DocumentIdOptionsProperty(
                    default_document_id_format="defaultDocumentIdFormat"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__a7089f940c747386ebd5931ebb7e25c49e14a6b154c607182c4c56984041f230)
                check_type(argname="argument default_document_id_format", value=default_document_id_format, expected_type=type_hints["default_document_id_format"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "default_document_id_format": default_document_id_format,
            }

        @builtins.property
        def default_document_id_format(self) -> builtins.str:
            '''``CfnDeliveryStream.DocumentIdOptionsProperty.DefaultDocumentIdFormat``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-documentidoptions.html#cfn-kinesisfirehose-deliverystream-documentidoptions-defaultdocumentidformat
            '''
            result = self._values.get("default_document_id_format")
            assert result is not None, "Required property 'default_document_id_format' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DocumentIdOptionsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.DynamicPartitioningConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"enabled": "enabled", "retry_options": "retryOptions"},
    )
    class DynamicPartitioningConfigurationProperty:
        def __init__(
            self,
            *,
            enabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            retry_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.RetryOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''The ``DynamicPartitioningConfiguration`` property type specifies the configuration of the dynamic partitioning mechanism that creates targeted data sets from the streaming data by partitioning it based on partition keys.

            :param enabled: Specifies whether dynamic partitioning is enabled for this Kinesis Data Firehose delivery stream.
            :param retry_options: Specifies the retry behavior in case Kinesis Data Firehose is unable to deliver data to an Amazon S3 prefix.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dynamicpartitioningconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                dynamic_partitioning_configuration_property = kinesisfirehose.CfnDeliveryStream.DynamicPartitioningConfigurationProperty(
                    enabled=False,
                    retry_options=kinesisfirehose.CfnDeliveryStream.RetryOptionsProperty(
                        duration_in_seconds=123
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__81ac24502669ae2c4e24b378d84fe9466baeeaaa59bb08e9266706b5855a0546)
                check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
                check_type(argname="argument retry_options", value=retry_options, expected_type=type_hints["retry_options"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if enabled is not None:
                self._values["enabled"] = enabled
            if retry_options is not None:
                self._values["retry_options"] = retry_options

        @builtins.property
        def enabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''Specifies whether dynamic partitioning is enabled for this Kinesis Data Firehose delivery stream.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dynamicpartitioningconfiguration.html#cfn-kinesisfirehose-deliverystream-dynamicpartitioningconfiguration-enabled
            '''
            result = self._values.get("enabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def retry_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.RetryOptionsProperty"]]:
            '''Specifies the retry behavior in case Kinesis Data Firehose is unable to deliver data to an Amazon S3 prefix.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-dynamicpartitioningconfiguration.html#cfn-kinesisfirehose-deliverystream-dynamicpartitioningconfiguration-retryoptions
            '''
            result = self._values.get("retry_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.RetryOptionsProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DynamicPartitioningConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ElasticsearchBufferingHintsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "interval_in_seconds": "intervalInSeconds",
            "size_in_m_bs": "sizeInMBs",
        },
    )
    class ElasticsearchBufferingHintsProperty:
        def __init__(
            self,
            *,
            interval_in_seconds: typing.Optional[jsii.Number] = None,
            size_in_m_bs: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''The ``ElasticsearchBufferingHints`` property type specifies how Amazon Kinesis Data Firehose (Kinesis Data Firehose) buffers incoming data while delivering it to the destination.

            The first buffer condition that is satisfied triggers Kinesis Data Firehose to deliver the data.

            ElasticsearchBufferingHints is the property type for the ``BufferingHints`` property of the `Amazon Kinesis Data Firehose DeliveryStream ElasticsearchDestinationConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html>`_ property type.

            :param interval_in_seconds: The length of time, in seconds, that Kinesis Data Firehose buffers incoming data before delivering it to the destination. For valid values, see the ``IntervalInSeconds`` content for the `BufferingHints <https://docs.aws.amazon.com/firehose/latest/APIReference/API_BufferingHints.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .
            :param size_in_m_bs: The size of the buffer, in MBs, that Kinesis Data Firehose uses for incoming data before delivering it to the destination. For valid values, see the ``SizeInMBs`` content for the `BufferingHints <https://docs.aws.amazon.com/firehose/latest/APIReference/API_BufferingHints.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchbufferinghints.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                elasticsearch_buffering_hints_property = kinesisfirehose.CfnDeliveryStream.ElasticsearchBufferingHintsProperty(
                    interval_in_seconds=123,
                    size_in_mBs=123
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__303c94776acc87657b62c87eef4858f83570ddbba0b57ad9e6465a88cce2d1a8)
                check_type(argname="argument interval_in_seconds", value=interval_in_seconds, expected_type=type_hints["interval_in_seconds"])
                check_type(argname="argument size_in_m_bs", value=size_in_m_bs, expected_type=type_hints["size_in_m_bs"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if interval_in_seconds is not None:
                self._values["interval_in_seconds"] = interval_in_seconds
            if size_in_m_bs is not None:
                self._values["size_in_m_bs"] = size_in_m_bs

        @builtins.property
        def interval_in_seconds(self) -> typing.Optional[jsii.Number]:
            '''The length of time, in seconds, that Kinesis Data Firehose buffers incoming data before delivering it to the destination.

            For valid values, see the ``IntervalInSeconds`` content for the `BufferingHints <https://docs.aws.amazon.com/firehose/latest/APIReference/API_BufferingHints.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchbufferinghints.html#cfn-kinesisfirehose-deliverystream-elasticsearchbufferinghints-intervalinseconds
            '''
            result = self._values.get("interval_in_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def size_in_m_bs(self) -> typing.Optional[jsii.Number]:
            '''The size of the buffer, in MBs, that Kinesis Data Firehose uses for incoming data before delivering it to the destination.

            For valid values, see the ``SizeInMBs`` content for the `BufferingHints <https://docs.aws.amazon.com/firehose/latest/APIReference/API_BufferingHints.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchbufferinghints.html#cfn-kinesisfirehose-deliverystream-elasticsearchbufferinghints-sizeinmbs
            '''
            result = self._values.get("size_in_m_bs")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ElasticsearchBufferingHintsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "index_name": "indexName",
            "role_arn": "roleArn",
            "s3_configuration": "s3Configuration",
            "buffering_hints": "bufferingHints",
            "cloud_watch_logging_options": "cloudWatchLoggingOptions",
            "cluster_endpoint": "clusterEndpoint",
            "document_id_options": "documentIdOptions",
            "domain_arn": "domainArn",
            "index_rotation_period": "indexRotationPeriod",
            "processing_configuration": "processingConfiguration",
            "retry_options": "retryOptions",
            "s3_backup_mode": "s3BackupMode",
            "type_name": "typeName",
            "vpc_configuration": "vpcConfiguration",
        },
    )
    class ElasticsearchDestinationConfigurationProperty:
        def __init__(
            self,
            *,
            index_name: builtins.str,
            role_arn: builtins.str,
            s3_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.S3DestinationConfigurationProperty", typing.Dict[builtins.str, typing.Any]]],
            buffering_hints: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.ElasticsearchBufferingHintsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            cloud_watch_logging_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.CloudWatchLoggingOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            cluster_endpoint: typing.Optional[builtins.str] = None,
            document_id_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.DocumentIdOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            domain_arn: typing.Optional[builtins.str] = None,
            index_rotation_period: typing.Optional[builtins.str] = None,
            processing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.ProcessingConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            retry_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.ElasticsearchRetryOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            s3_backup_mode: typing.Optional[builtins.str] = None,
            type_name: typing.Optional[builtins.str] = None,
            vpc_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.VpcConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''The ``ElasticsearchDestinationConfiguration`` property type specifies an Amazon Elasticsearch Service (Amazon ES) domain that Amazon Kinesis Data Firehose (Kinesis Data Firehose) delivers data to.

            :param index_name: The name of the Elasticsearch index to which Kinesis Data Firehose adds data for indexing.
            :param role_arn: The Amazon Resource Name (ARN) of the IAM role to be assumed by Kinesis Data Firehose for calling the Amazon ES Configuration API and for indexing documents. For more information, see `Controlling Access with Amazon Kinesis Data Firehose <https://docs.aws.amazon.com/firehose/latest/dev/controlling-access.html>`_ .
            :param s3_configuration: The S3 bucket where Kinesis Data Firehose backs up incoming data.
            :param buffering_hints: Configures how Kinesis Data Firehose buffers incoming data while delivering it to the Amazon ES domain.
            :param cloud_watch_logging_options: The Amazon CloudWatch Logs logging options for the delivery stream.
            :param cluster_endpoint: The endpoint to use when communicating with the cluster. Specify either this ``ClusterEndpoint`` or the ``DomainARN`` field.
            :param document_id_options: ``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.DocumentIdOptions``.
            :param domain_arn: The ARN of the Amazon ES domain. The IAM role must have permissions for ``DescribeElasticsearchDomain`` , ``DescribeElasticsearchDomains`` , and ``DescribeElasticsearchDomainConfig`` after assuming the role specified in *RoleARN* . Specify either ``ClusterEndpoint`` or ``DomainARN`` .
            :param index_rotation_period: The frequency of Elasticsearch index rotation. If you enable index rotation, Kinesis Data Firehose appends a portion of the UTC arrival timestamp to the specified index name, and rotates the appended timestamp accordingly. For more information, see `Index Rotation for the Amazon ES Destination <https://docs.aws.amazon.com/firehose/latest/dev/basic-deliver.html#es-index-rotation>`_ in the *Amazon Kinesis Data Firehose Developer Guide* .
            :param processing_configuration: The data processing configuration for the Kinesis Data Firehose delivery stream.
            :param retry_options: The retry behavior when Kinesis Data Firehose is unable to deliver data to Amazon ES.
            :param s3_backup_mode: The condition under which Kinesis Data Firehose delivers data to Amazon Simple Storage Service (Amazon S3). You can send Amazon S3 all documents (all data) or only the documents that Kinesis Data Firehose could not deliver to the Amazon ES destination. For more information and valid values, see the ``S3BackupMode`` content for the `ElasticsearchDestinationConfiguration <https://docs.aws.amazon.com/firehose/latest/APIReference/API_ElasticsearchDestinationConfiguration.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .
            :param type_name: The Elasticsearch type name that Amazon ES adds to documents when indexing data.
            :param vpc_configuration: The details of the VPC of the Amazon ES destination.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                elasticsearch_destination_configuration_property = kinesisfirehose.CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty(
                    index_name="indexName",
                    role_arn="roleArn",
                    s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
                
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
                
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.ElasticsearchBufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    cluster_endpoint="clusterEndpoint",
                    document_id_options=kinesisfirehose.CfnDeliveryStream.DocumentIdOptionsProperty(
                        default_document_id_format="defaultDocumentIdFormat"
                    ),
                    domain_arn="domainArn",
                    index_rotation_period="indexRotationPeriod",
                    processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                        enabled=False,
                        processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                            type="type",
                
                            # the properties below are optional
                            parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                parameter_name="parameterName",
                                parameter_value="parameterValue"
                            )]
                        )]
                    ),
                    retry_options=kinesisfirehose.CfnDeliveryStream.ElasticsearchRetryOptionsProperty(
                        duration_in_seconds=123
                    ),
                    s3_backup_mode="s3BackupMode",
                    type_name="typeName",
                    vpc_configuration=kinesisfirehose.CfnDeliveryStream.VpcConfigurationProperty(
                        role_arn="roleArn",
                        security_group_ids=["securityGroupIds"],
                        subnet_ids=["subnetIds"]
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__187cfbaba4670b2ab9fe0c31707acb35032074e2a60cbf96e8bb6b67a4328d6d)
                check_type(argname="argument index_name", value=index_name, expected_type=type_hints["index_name"])
                check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
                check_type(argname="argument s3_configuration", value=s3_configuration, expected_type=type_hints["s3_configuration"])
                check_type(argname="argument buffering_hints", value=buffering_hints, expected_type=type_hints["buffering_hints"])
                check_type(argname="argument cloud_watch_logging_options", value=cloud_watch_logging_options, expected_type=type_hints["cloud_watch_logging_options"])
                check_type(argname="argument cluster_endpoint", value=cluster_endpoint, expected_type=type_hints["cluster_endpoint"])
                check_type(argname="argument document_id_options", value=document_id_options, expected_type=type_hints["document_id_options"])
                check_type(argname="argument domain_arn", value=domain_arn, expected_type=type_hints["domain_arn"])
                check_type(argname="argument index_rotation_period", value=index_rotation_period, expected_type=type_hints["index_rotation_period"])
                check_type(argname="argument processing_configuration", value=processing_configuration, expected_type=type_hints["processing_configuration"])
                check_type(argname="argument retry_options", value=retry_options, expected_type=type_hints["retry_options"])
                check_type(argname="argument s3_backup_mode", value=s3_backup_mode, expected_type=type_hints["s3_backup_mode"])
                check_type(argname="argument type_name", value=type_name, expected_type=type_hints["type_name"])
                check_type(argname="argument vpc_configuration", value=vpc_configuration, expected_type=type_hints["vpc_configuration"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "index_name": index_name,
                "role_arn": role_arn,
                "s3_configuration": s3_configuration,
            }
            if buffering_hints is not None:
                self._values["buffering_hints"] = buffering_hints
            if cloud_watch_logging_options is not None:
                self._values["cloud_watch_logging_options"] = cloud_watch_logging_options
            if cluster_endpoint is not None:
                self._values["cluster_endpoint"] = cluster_endpoint
            if document_id_options is not None:
                self._values["document_id_options"] = document_id_options
            if domain_arn is not None:
                self._values["domain_arn"] = domain_arn
            if index_rotation_period is not None:
                self._values["index_rotation_period"] = index_rotation_period
            if processing_configuration is not None:
                self._values["processing_configuration"] = processing_configuration
            if retry_options is not None:
                self._values["retry_options"] = retry_options
            if s3_backup_mode is not None:
                self._values["s3_backup_mode"] = s3_backup_mode
            if type_name is not None:
                self._values["type_name"] = type_name
            if vpc_configuration is not None:
                self._values["vpc_configuration"] = vpc_configuration

        @builtins.property
        def index_name(self) -> builtins.str:
            '''The name of the Elasticsearch index to which Kinesis Data Firehose adds data for indexing.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-indexname
            '''
            result = self._values.get("index_name")
            assert result is not None, "Required property 'index_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''The Amazon Resource Name (ARN) of the IAM role to be assumed by Kinesis Data Firehose for calling the Amazon ES Configuration API and for indexing documents.

            For more information, see `Controlling Access with Amazon Kinesis Data Firehose <https://docs.aws.amazon.com/firehose/latest/dev/controlling-access.html>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def s3_configuration(
            self,
        ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]:
            '''The S3 bucket where Kinesis Data Firehose backs up incoming data.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-s3configuration
            '''
            result = self._values.get("s3_configuration")
            assert result is not None, "Required property 's3_configuration' is missing"
            return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"], result)

        @builtins.property
        def buffering_hints(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ElasticsearchBufferingHintsProperty"]]:
            '''Configures how Kinesis Data Firehose buffers incoming data while delivering it to the Amazon ES domain.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-bufferinghints
            '''
            result = self._values.get("buffering_hints")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ElasticsearchBufferingHintsProperty"]], result)

        @builtins.property
        def cloud_watch_logging_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]:
            '''The Amazon CloudWatch Logs logging options for the delivery stream.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-cloudwatchloggingoptions
            '''
            result = self._values.get("cloud_watch_logging_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]], result)

        @builtins.property
        def cluster_endpoint(self) -> typing.Optional[builtins.str]:
            '''The endpoint to use when communicating with the cluster.

            Specify either this ``ClusterEndpoint`` or the ``DomainARN`` field.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-clusterendpoint
            '''
            result = self._values.get("cluster_endpoint")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def document_id_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.DocumentIdOptionsProperty"]]:
            '''``CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty.DocumentIdOptions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-documentidoptions
            '''
            result = self._values.get("document_id_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.DocumentIdOptionsProperty"]], result)

        @builtins.property
        def domain_arn(self) -> typing.Optional[builtins.str]:
            '''The ARN of the Amazon ES domain.

            The IAM role must have permissions for ``DescribeElasticsearchDomain`` , ``DescribeElasticsearchDomains`` , and ``DescribeElasticsearchDomainConfig`` after assuming the role specified in *RoleARN* .

            Specify either ``ClusterEndpoint`` or ``DomainARN`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-domainarn
            '''
            result = self._values.get("domain_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def index_rotation_period(self) -> typing.Optional[builtins.str]:
            '''The frequency of Elasticsearch index rotation.

            If you enable index rotation, Kinesis Data Firehose appends a portion of the UTC arrival timestamp to the specified index name, and rotates the appended timestamp accordingly. For more information, see `Index Rotation for the Amazon ES Destination <https://docs.aws.amazon.com/firehose/latest/dev/basic-deliver.html#es-index-rotation>`_ in the *Amazon Kinesis Data Firehose Developer Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-indexrotationperiod
            '''
            result = self._values.get("index_rotation_period")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def processing_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]]:
            '''The data processing configuration for the Kinesis Data Firehose delivery stream.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-processingconfiguration
            '''
            result = self._values.get("processing_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]], result)

        @builtins.property
        def retry_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ElasticsearchRetryOptionsProperty"]]:
            '''The retry behavior when Kinesis Data Firehose is unable to deliver data to Amazon ES.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-retryoptions
            '''
            result = self._values.get("retry_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ElasticsearchRetryOptionsProperty"]], result)

        @builtins.property
        def s3_backup_mode(self) -> typing.Optional[builtins.str]:
            '''The condition under which Kinesis Data Firehose delivers data to Amazon Simple Storage Service (Amazon S3).

            You can send Amazon S3 all documents (all data) or only the documents that Kinesis Data Firehose could not deliver to the Amazon ES destination. For more information and valid values, see the ``S3BackupMode`` content for the `ElasticsearchDestinationConfiguration <https://docs.aws.amazon.com/firehose/latest/APIReference/API_ElasticsearchDestinationConfiguration.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-s3backupmode
            '''
            result = self._values.get("s3_backup_mode")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def type_name(self) -> typing.Optional[builtins.str]:
            '''The Elasticsearch type name that Amazon ES adds to documents when indexing data.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-typename
            '''
            result = self._values.get("type_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def vpc_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.VpcConfigurationProperty"]]:
            '''The details of the VPC of the Amazon ES destination.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration-vpcconfiguration
            '''
            result = self._values.get("vpc_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.VpcConfigurationProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ElasticsearchDestinationConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ElasticsearchRetryOptionsProperty",
        jsii_struct_bases=[],
        name_mapping={"duration_in_seconds": "durationInSeconds"},
    )
    class ElasticsearchRetryOptionsProperty:
        def __init__(
            self,
            *,
            duration_in_seconds: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''The ``ElasticsearchRetryOptions`` property type configures the retry behavior for when Amazon Kinesis Data Firehose (Kinesis Data Firehose) can't deliver data to Amazon Elasticsearch Service (Amazon ES).

            :param duration_in_seconds: After an initial failure to deliver to Amazon ES, the total amount of time during which Kinesis Data Firehose re-attempts delivery (including the first attempt). If Kinesis Data Firehose can't deliver the data within the specified time, it writes the data to the backup S3 bucket. For valid values, see the ``DurationInSeconds`` content for the `ElasticsearchRetryOptions <https://docs.aws.amazon.com/firehose/latest/APIReference/API_ElasticsearchRetryOptions.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchretryoptions.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                elasticsearch_retry_options_property = kinesisfirehose.CfnDeliveryStream.ElasticsearchRetryOptionsProperty(
                    duration_in_seconds=123
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__2d1aac060826908279ff8f9ac0ea30bbd9e78821b9442b69ebf81487fdd43e8e)
                check_type(argname="argument duration_in_seconds", value=duration_in_seconds, expected_type=type_hints["duration_in_seconds"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if duration_in_seconds is not None:
                self._values["duration_in_seconds"] = duration_in_seconds

        @builtins.property
        def duration_in_seconds(self) -> typing.Optional[jsii.Number]:
            '''After an initial failure to deliver to Amazon ES, the total amount of time during which Kinesis Data Firehose re-attempts delivery (including the first attempt).

            If Kinesis Data Firehose can't deliver the data within the specified time, it writes the data to the backup S3 bucket. For valid values, see the ``DurationInSeconds`` content for the `ElasticsearchRetryOptions <https://docs.aws.amazon.com/firehose/latest/APIReference/API_ElasticsearchRetryOptions.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-elasticsearchretryoptions.html#cfn-kinesisfirehose-deliverystream-elasticsearchretryoptions-durationinseconds
            '''
            result = self._values.get("duration_in_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ElasticsearchRetryOptionsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "kms_encryption_config": "kmsEncryptionConfig",
            "no_encryption_config": "noEncryptionConfig",
        },
    )
    class EncryptionConfigurationProperty:
        def __init__(
            self,
            *,
            kms_encryption_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.KMSEncryptionConfigProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            no_encryption_config: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The ``EncryptionConfiguration`` property type specifies the encryption settings that Amazon Kinesis Data Firehose (Kinesis Data Firehose) uses when delivering data to Amazon Simple Storage Service (Amazon S3).

            :param kms_encryption_config: The AWS Key Management Service ( AWS KMS) encryption key that Amazon S3 uses to encrypt your data.
            :param no_encryption_config: Disables encryption. For valid values, see the ``NoEncryptionConfig`` content for the `EncryptionConfiguration <https://docs.aws.amazon.com/firehose/latest/APIReference/API_EncryptionConfiguration.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-encryptionconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                encryption_configuration_property = kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                    kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                        awskms_key_arn="awskmsKeyArn"
                    ),
                    no_encryption_config="noEncryptionConfig"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__9a1bc04cb5074ea81a4788e9e8f3c3a8e64d6a437346e0089a65bc413df5f8ce)
                check_type(argname="argument kms_encryption_config", value=kms_encryption_config, expected_type=type_hints["kms_encryption_config"])
                check_type(argname="argument no_encryption_config", value=no_encryption_config, expected_type=type_hints["no_encryption_config"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if kms_encryption_config is not None:
                self._values["kms_encryption_config"] = kms_encryption_config
            if no_encryption_config is not None:
                self._values["no_encryption_config"] = no_encryption_config

        @builtins.property
        def kms_encryption_config(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.KMSEncryptionConfigProperty"]]:
            '''The AWS Key Management Service ( AWS KMS) encryption key that Amazon S3 uses to encrypt your data.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-encryptionconfiguration.html#cfn-kinesisfirehose-deliverystream-encryptionconfiguration-kmsencryptionconfig
            '''
            result = self._values.get("kms_encryption_config")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.KMSEncryptionConfigProperty"]], result)

        @builtins.property
        def no_encryption_config(self) -> typing.Optional[builtins.str]:
            '''Disables encryption.

            For valid values, see the ``NoEncryptionConfig`` content for the `EncryptionConfiguration <https://docs.aws.amazon.com/firehose/latest/APIReference/API_EncryptionConfiguration.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-encryptionconfiguration.html#cfn-kinesisfirehose-deliverystream-encryptionconfiguration-noencryptionconfig
            '''
            result = self._values.get("no_encryption_config")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EncryptionConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "bucket_arn": "bucketArn",
            "role_arn": "roleArn",
            "buffering_hints": "bufferingHints",
            "cloud_watch_logging_options": "cloudWatchLoggingOptions",
            "compression_format": "compressionFormat",
            "data_format_conversion_configuration": "dataFormatConversionConfiguration",
            "dynamic_partitioning_configuration": "dynamicPartitioningConfiguration",
            "encryption_configuration": "encryptionConfiguration",
            "error_output_prefix": "errorOutputPrefix",
            "prefix": "prefix",
            "processing_configuration": "processingConfiguration",
            "s3_backup_configuration": "s3BackupConfiguration",
            "s3_backup_mode": "s3BackupMode",
        },
    )
    class ExtendedS3DestinationConfigurationProperty:
        def __init__(
            self,
            *,
            bucket_arn: builtins.str,
            role_arn: builtins.str,
            buffering_hints: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.BufferingHintsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            cloud_watch_logging_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.CloudWatchLoggingOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            compression_format: typing.Optional[builtins.str] = None,
            data_format_conversion_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.DataFormatConversionConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            dynamic_partitioning_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.DynamicPartitioningConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            encryption_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.EncryptionConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            error_output_prefix: typing.Optional[builtins.str] = None,
            prefix: typing.Optional[builtins.str] = None,
            processing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.ProcessingConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            s3_backup_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.S3DestinationConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            s3_backup_mode: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The ``ExtendedS3DestinationConfiguration`` property type configures an Amazon S3 destination for an Amazon Kinesis Data Firehose delivery stream.

            :param bucket_arn: The Amazon Resource Name (ARN) of the Amazon S3 bucket. For constraints, see `ExtendedS3DestinationConfiguration <https://docs.aws.amazon.com/firehose/latest/APIReference/API_ExtendedS3DestinationConfiguration.html>`_ in the *Amazon Kinesis Data Firehose API Reference* .
            :param role_arn: The Amazon Resource Name (ARN) of the AWS credentials. For constraints, see `ExtendedS3DestinationConfiguration <https://docs.aws.amazon.com/firehose/latest/APIReference/API_ExtendedS3DestinationConfiguration.html>`_ in the *Amazon Kinesis Data Firehose API Reference* .
            :param buffering_hints: The buffering option.
            :param cloud_watch_logging_options: The Amazon CloudWatch logging options for your delivery stream.
            :param compression_format: The compression format. If no value is specified, the default is ``UNCOMPRESSED`` .
            :param data_format_conversion_configuration: The serializer, deserializer, and schema for converting data from the JSON format to the Parquet or ORC format before writing it to Amazon S3.
            :param dynamic_partitioning_configuration: The configuration of the dynamic partitioning mechanism that creates targeted data sets from the streaming data by partitioning it based on partition keys.
            :param encryption_configuration: The encryption configuration for the Kinesis Data Firehose delivery stream. The default value is ``NoEncryption`` .
            :param error_output_prefix: A prefix that Kinesis Data Firehose evaluates and adds to failed records before writing them to S3. This prefix appears immediately following the bucket name. For information about how to specify this prefix, see `Custom Prefixes for Amazon S3 Objects <https://docs.aws.amazon.com/firehose/latest/dev/s3-prefixes.html>`_ .
            :param prefix: The ``YYYY/MM/DD/HH`` time format prefix is automatically used for delivered Amazon S3 files. For more information, see `ExtendedS3DestinationConfiguration <https://docs.aws.amazon.com/firehose/latest/APIReference/API_ExtendedS3DestinationConfiguration.html>`_ in the *Amazon Kinesis Data Firehose API Reference* .
            :param processing_configuration: The data processing configuration for the Kinesis Data Firehose delivery stream.
            :param s3_backup_configuration: The configuration for backup in Amazon S3.
            :param s3_backup_mode: The Amazon S3 backup mode. After you create a delivery stream, you can update it to enable Amazon S3 backup if it is disabled. If backup is enabled, you can't update the delivery stream to disable it.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                extended_s3_destination_configuration_property = kinesisfirehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(
                    bucket_arn="bucketArn",
                    role_arn="roleArn",
                
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    compression_format="compressionFormat",
                    data_format_conversion_configuration=kinesisfirehose.CfnDeliveryStream.DataFormatConversionConfigurationProperty(
                        enabled=False,
                        input_format_configuration=kinesisfirehose.CfnDeliveryStream.InputFormatConfigurationProperty(
                            deserializer=kinesisfirehose.CfnDeliveryStream.DeserializerProperty(
                                hive_json_ser_de=kinesisfirehose.CfnDeliveryStream.HiveJsonSerDeProperty(
                                    timestamp_formats=["timestampFormats"]
                                ),
                                open_xJson_ser_de=kinesisfirehose.CfnDeliveryStream.OpenXJsonSerDeProperty(
                                    case_insensitive=False,
                                    column_to_json_key_mappings={
                                        "column_to_json_key_mappings_key": "columnToJsonKeyMappings"
                                    },
                                    convert_dots_in_json_keys_to_underscores=False
                                )
                            )
                        ),
                        output_format_configuration=kinesisfirehose.CfnDeliveryStream.OutputFormatConfigurationProperty(
                            serializer=kinesisfirehose.CfnDeliveryStream.SerializerProperty(
                                orc_ser_de=kinesisfirehose.CfnDeliveryStream.OrcSerDeProperty(
                                    block_size_bytes=123,
                                    bloom_filter_columns=["bloomFilterColumns"],
                                    bloom_filter_false_positive_probability=123,
                                    compression="compression",
                                    dictionary_key_threshold=123,
                                    enable_padding=False,
                                    format_version="formatVersion",
                                    padding_tolerance=123,
                                    row_index_stride=123,
                                    stripe_size_bytes=123
                                ),
                                parquet_ser_de=kinesisfirehose.CfnDeliveryStream.ParquetSerDeProperty(
                                    block_size_bytes=123,
                                    compression="compression",
                                    enable_dictionary_compression=False,
                                    max_padding_bytes=123,
                                    page_size_bytes=123,
                                    writer_version="writerVersion"
                                )
                            )
                        ),
                        schema_configuration=kinesisfirehose.CfnDeliveryStream.SchemaConfigurationProperty(
                            catalog_id="catalogId",
                            database_name="databaseName",
                            region="region",
                            role_arn="roleArn",
                            table_name="tableName",
                            version_id="versionId"
                        )
                    ),
                    dynamic_partitioning_configuration=kinesisfirehose.CfnDeliveryStream.DynamicPartitioningConfigurationProperty(
                        enabled=False,
                        retry_options=kinesisfirehose.CfnDeliveryStream.RetryOptionsProperty(
                            duration_in_seconds=123
                        )
                    ),
                    encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                        kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                            awskms_key_arn="awskmsKeyArn"
                        ),
                        no_encryption_config="noEncryptionConfig"
                    ),
                    error_output_prefix="errorOutputPrefix",
                    prefix="prefix",
                    processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                        enabled=False,
                        processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                            type="type",
                
                            # the properties below are optional
                            parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                parameter_name="parameterName",
                                parameter_value="parameterValue"
                            )]
                        )]
                    ),
                    s3_backup_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
                
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
                    s3_backup_mode="s3BackupMode"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__f9e236c6cfc95ca860d610c22bbf1113f923621ee37e3c8f9370c87c038cd9fc)
                check_type(argname="argument bucket_arn", value=bucket_arn, expected_type=type_hints["bucket_arn"])
                check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
                check_type(argname="argument buffering_hints", value=buffering_hints, expected_type=type_hints["buffering_hints"])
                check_type(argname="argument cloud_watch_logging_options", value=cloud_watch_logging_options, expected_type=type_hints["cloud_watch_logging_options"])
                check_type(argname="argument compression_format", value=compression_format, expected_type=type_hints["compression_format"])
                check_type(argname="argument data_format_conversion_configuration", value=data_format_conversion_configuration, expected_type=type_hints["data_format_conversion_configuration"])
                check_type(argname="argument dynamic_partitioning_configuration", value=dynamic_partitioning_configuration, expected_type=type_hints["dynamic_partitioning_configuration"])
                check_type(argname="argument encryption_configuration", value=encryption_configuration, expected_type=type_hints["encryption_configuration"])
                check_type(argname="argument error_output_prefix", value=error_output_prefix, expected_type=type_hints["error_output_prefix"])
                check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
                check_type(argname="argument processing_configuration", value=processing_configuration, expected_type=type_hints["processing_configuration"])
                check_type(argname="argument s3_backup_configuration", value=s3_backup_configuration, expected_type=type_hints["s3_backup_configuration"])
                check_type(argname="argument s3_backup_mode", value=s3_backup_mode, expected_type=type_hints["s3_backup_mode"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "bucket_arn": bucket_arn,
                "role_arn": role_arn,
            }
            if buffering_hints is not None:
                self._values["buffering_hints"] = buffering_hints
            if cloud_watch_logging_options is not None:
                self._values["cloud_watch_logging_options"] = cloud_watch_logging_options
            if compression_format is not None:
                self._values["compression_format"] = compression_format
            if data_format_conversion_configuration is not None:
                self._values["data_format_conversion_configuration"] = data_format_conversion_configuration
            if dynamic_partitioning_configuration is not None:
                self._values["dynamic_partitioning_configuration"] = dynamic_partitioning_configuration
            if encryption_configuration is not None:
                self._values["encryption_configuration"] = encryption_configuration
            if error_output_prefix is not None:
                self._values["error_output_prefix"] = error_output_prefix
            if prefix is not None:
                self._values["prefix"] = prefix
            if processing_configuration is not None:
                self._values["processing_configuration"] = processing_configuration
            if s3_backup_configuration is not None:
                self._values["s3_backup_configuration"] = s3_backup_configuration
            if s3_backup_mode is not None:
                self._values["s3_backup_mode"] = s3_backup_mode

        @builtins.property
        def bucket_arn(self) -> builtins.str:
            '''The Amazon Resource Name (ARN) of the Amazon S3 bucket.

            For constraints, see `ExtendedS3DestinationConfiguration <https://docs.aws.amazon.com/firehose/latest/APIReference/API_ExtendedS3DestinationConfiguration.html>`_ in the *Amazon Kinesis Data Firehose API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-bucketarn
            '''
            result = self._values.get("bucket_arn")
            assert result is not None, "Required property 'bucket_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''The Amazon Resource Name (ARN) of the AWS credentials.

            For constraints, see `ExtendedS3DestinationConfiguration <https://docs.aws.amazon.com/firehose/latest/APIReference/API_ExtendedS3DestinationConfiguration.html>`_ in the *Amazon Kinesis Data Firehose API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def buffering_hints(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.BufferingHintsProperty"]]:
            '''The buffering option.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-bufferinghints
            '''
            result = self._values.get("buffering_hints")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.BufferingHintsProperty"]], result)

        @builtins.property
        def cloud_watch_logging_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]:
            '''The Amazon CloudWatch logging options for your delivery stream.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-cloudwatchloggingoptions
            '''
            result = self._values.get("cloud_watch_logging_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]], result)

        @builtins.property
        def compression_format(self) -> typing.Optional[builtins.str]:
            '''The compression format.

            If no value is specified, the default is ``UNCOMPRESSED`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-compressionformat
            '''
            result = self._values.get("compression_format")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def data_format_conversion_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.DataFormatConversionConfigurationProperty"]]:
            '''The serializer, deserializer, and schema for converting data from the JSON format to the Parquet or ORC format before writing it to Amazon S3.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-dataformatconversionconfiguration
            '''
            result = self._values.get("data_format_conversion_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.DataFormatConversionConfigurationProperty"]], result)

        @builtins.property
        def dynamic_partitioning_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.DynamicPartitioningConfigurationProperty"]]:
            '''The configuration of the dynamic partitioning mechanism that creates targeted data sets from the streaming data by partitioning it based on partition keys.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-dynamicpartitioningconfiguration
            '''
            result = self._values.get("dynamic_partitioning_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.DynamicPartitioningConfigurationProperty"]], result)

        @builtins.property
        def encryption_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.EncryptionConfigurationProperty"]]:
            '''The encryption configuration for the Kinesis Data Firehose delivery stream.

            The default value is ``NoEncryption`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-encryptionconfiguration
            '''
            result = self._values.get("encryption_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.EncryptionConfigurationProperty"]], result)

        @builtins.property
        def error_output_prefix(self) -> typing.Optional[builtins.str]:
            '''A prefix that Kinesis Data Firehose evaluates and adds to failed records before writing them to S3.

            This prefix appears immediately following the bucket name. For information about how to specify this prefix, see `Custom Prefixes for Amazon S3 Objects <https://docs.aws.amazon.com/firehose/latest/dev/s3-prefixes.html>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-erroroutputprefix
            '''
            result = self._values.get("error_output_prefix")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def prefix(self) -> typing.Optional[builtins.str]:
            '''The ``YYYY/MM/DD/HH`` time format prefix is automatically used for delivered Amazon S3 files.

            For more information, see `ExtendedS3DestinationConfiguration <https://docs.aws.amazon.com/firehose/latest/APIReference/API_ExtendedS3DestinationConfiguration.html>`_ in the *Amazon Kinesis Data Firehose API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-prefix
            '''
            result = self._values.get("prefix")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def processing_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]]:
            '''The data processing configuration for the Kinesis Data Firehose delivery stream.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-processingconfiguration
            '''
            result = self._values.get("processing_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]], result)

        @builtins.property
        def s3_backup_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]]:
            '''The configuration for backup in Amazon S3.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-s3backupconfiguration
            '''
            result = self._values.get("s3_backup_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]], result)

        @builtins.property
        def s3_backup_mode(self) -> typing.Optional[builtins.str]:
            '''The Amazon S3 backup mode.

            After you create a delivery stream, you can update it to enable Amazon S3 backup if it is disabled. If backup is enabled, you can't update the delivery stream to disable it.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-extendeds3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration-s3backupmode
            '''
            result = self._values.get("s3_backup_mode")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ExtendedS3DestinationConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.HiveJsonSerDeProperty",
        jsii_struct_bases=[],
        name_mapping={"timestamp_formats": "timestampFormats"},
    )
    class HiveJsonSerDeProperty:
        def __init__(
            self,
            *,
            timestamp_formats: typing.Optional[typing.Sequence[builtins.str]] = None,
        ) -> None:
            '''The native Hive / HCatalog JsonSerDe.

            Used by Kinesis Data Firehose for deserializing data, which means converting it from the JSON format in preparation for serializing it to the Parquet or ORC format. This is one of two deserializers you can choose, depending on which one offers the functionality you need. The other option is the OpenX SerDe.

            :param timestamp_formats: Indicates how you want Kinesis Data Firehose to parse the date and timestamps that may be present in your input data JSON. To specify these format strings, follow the pattern syntax of JodaTime's DateTimeFormat format strings. For more information, see `Class DateTimeFormat <https://docs.aws.amazon.com/https://www.joda.org/joda-time/apidocs/org/joda/time/format/DateTimeFormat.html>`_ . You can also use the special value ``millis`` to parse timestamps in epoch milliseconds. If you don't specify a format, Kinesis Data Firehose uses ``java.sql.Timestamp::valueOf`` by default.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-hivejsonserde.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                hive_json_ser_de_property = kinesisfirehose.CfnDeliveryStream.HiveJsonSerDeProperty(
                    timestamp_formats=["timestampFormats"]
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__eb6d8ccd84cae002fb7f2ec5e8998185c5210eb594ac7f8a91a358d0a6646565)
                check_type(argname="argument timestamp_formats", value=timestamp_formats, expected_type=type_hints["timestamp_formats"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if timestamp_formats is not None:
                self._values["timestamp_formats"] = timestamp_formats

        @builtins.property
        def timestamp_formats(self) -> typing.Optional[typing.List[builtins.str]]:
            '''Indicates how you want Kinesis Data Firehose to parse the date and timestamps that may be present in your input data JSON.

            To specify these format strings, follow the pattern syntax of JodaTime's DateTimeFormat format strings. For more information, see `Class DateTimeFormat <https://docs.aws.amazon.com/https://www.joda.org/joda-time/apidocs/org/joda/time/format/DateTimeFormat.html>`_ . You can also use the special value ``millis`` to parse timestamps in epoch milliseconds. If you don't specify a format, Kinesis Data Firehose uses ``java.sql.Timestamp::valueOf`` by default.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-hivejsonserde.html#cfn-kinesisfirehose-deliverystream-hivejsonserde-timestampformats
            '''
            result = self._values.get("timestamp_formats")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "HiveJsonSerDeProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.HttpEndpointCommonAttributeProperty",
        jsii_struct_bases=[],
        name_mapping={
            "attribute_name": "attributeName",
            "attribute_value": "attributeValue",
        },
    )
    class HttpEndpointCommonAttributeProperty:
        def __init__(
            self,
            *,
            attribute_name: builtins.str,
            attribute_value: builtins.str,
        ) -> None:
            '''Describes the metadata that's delivered to the specified HTTP endpoint destination.

            Kinesis Firehose supports any custom HTTP endpoint or HTTP endpoints owned by supported third-party service providers, including Datadog, MongoDB, and New Relic.

            :param attribute_name: The name of the HTTP endpoint common attribute.
            :param attribute_value: The value of the HTTP endpoint common attribute.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointcommonattribute.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                http_endpoint_common_attribute_property = kinesisfirehose.CfnDeliveryStream.HttpEndpointCommonAttributeProperty(
                    attribute_name="attributeName",
                    attribute_value="attributeValue"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__a675429428249fe3aa5c328a4ec1d4b582e7c67b5bbbe376b8cc6a0429ebdb55)
                check_type(argname="argument attribute_name", value=attribute_name, expected_type=type_hints["attribute_name"])
                check_type(argname="argument attribute_value", value=attribute_value, expected_type=type_hints["attribute_value"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "attribute_name": attribute_name,
                "attribute_value": attribute_value,
            }

        @builtins.property
        def attribute_name(self) -> builtins.str:
            '''The name of the HTTP endpoint common attribute.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointcommonattribute.html#cfn-kinesisfirehose-deliverystream-httpendpointcommonattribute-attributename
            '''
            result = self._values.get("attribute_name")
            assert result is not None, "Required property 'attribute_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def attribute_value(self) -> builtins.str:
            '''The value of the HTTP endpoint common attribute.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointcommonattribute.html#cfn-kinesisfirehose-deliverystream-httpendpointcommonattribute-attributevalue
            '''
            result = self._values.get("attribute_value")
            assert result is not None, "Required property 'attribute_value' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "HttpEndpointCommonAttributeProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.HttpEndpointConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"url": "url", "access_key": "accessKey", "name": "name"},
    )
    class HttpEndpointConfigurationProperty:
        def __init__(
            self,
            *,
            url: builtins.str,
            access_key: typing.Optional[builtins.str] = None,
            name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Describes the configuration of the HTTP endpoint to which Kinesis Firehose delivers data.

            Kinesis Firehose supports any custom HTTP endpoint or HTTP endpoints owned by supported third-party service providers, including Datadog, MongoDB, and New Relic.

            :param url: The URL of the HTTP endpoint selected as the destination.
            :param access_key: The access key required for Kinesis Firehose to authenticate with the HTTP endpoint selected as the destination.
            :param name: The name of the HTTP endpoint selected as the destination.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                http_endpoint_configuration_property = kinesisfirehose.CfnDeliveryStream.HttpEndpointConfigurationProperty(
                    url="url",
                
                    # the properties below are optional
                    access_key="accessKey",
                    name="name"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__ed3b58828f3f0c612428b99223fd34b0dc3548b65791514791fd8c424c49438f)
                check_type(argname="argument url", value=url, expected_type=type_hints["url"])
                check_type(argname="argument access_key", value=access_key, expected_type=type_hints["access_key"])
                check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "url": url,
            }
            if access_key is not None:
                self._values["access_key"] = access_key
            if name is not None:
                self._values["name"] = name

        @builtins.property
        def url(self) -> builtins.str:
            '''The URL of the HTTP endpoint selected as the destination.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointconfiguration.html#cfn-kinesisfirehose-deliverystream-httpendpointconfiguration-url
            '''
            result = self._values.get("url")
            assert result is not None, "Required property 'url' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def access_key(self) -> typing.Optional[builtins.str]:
            '''The access key required for Kinesis Firehose to authenticate with the HTTP endpoint selected as the destination.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointconfiguration.html#cfn-kinesisfirehose-deliverystream-httpendpointconfiguration-accesskey
            '''
            result = self._values.get("access_key")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''The name of the HTTP endpoint selected as the destination.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointconfiguration.html#cfn-kinesisfirehose-deliverystream-httpendpointconfiguration-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "HttpEndpointConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "endpoint_configuration": "endpointConfiguration",
            "s3_configuration": "s3Configuration",
            "buffering_hints": "bufferingHints",
            "cloud_watch_logging_options": "cloudWatchLoggingOptions",
            "processing_configuration": "processingConfiguration",
            "request_configuration": "requestConfiguration",
            "retry_options": "retryOptions",
            "role_arn": "roleArn",
            "s3_backup_mode": "s3BackupMode",
        },
    )
    class HttpEndpointDestinationConfigurationProperty:
        def __init__(
            self,
            *,
            endpoint_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.HttpEndpointConfigurationProperty", typing.Dict[builtins.str, typing.Any]]],
            s3_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.S3DestinationConfigurationProperty", typing.Dict[builtins.str, typing.Any]]],
            buffering_hints: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.BufferingHintsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            cloud_watch_logging_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.CloudWatchLoggingOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            processing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.ProcessingConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            request_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.HttpEndpointRequestConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            retry_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.RetryOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            role_arn: typing.Optional[builtins.str] = None,
            s3_backup_mode: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Describes the configuration of the HTTP endpoint destination.

            Kinesis Firehose supports any custom HTTP endpoint or HTTP endpoints owned by supported third-party service providers, including Datadog, MongoDB, and New Relic.

            :param endpoint_configuration: The configuration of the HTTP endpoint selected as the destination.
            :param s3_configuration: Describes the configuration of a destination in Amazon S3.
            :param buffering_hints: The buffering options that can be used before data is delivered to the specified destination. Kinesis Data Firehose treats these options as hints, and it might choose to use more optimal values. The SizeInMBs and IntervalInSeconds parameters are optional. However, if you specify a value for one of them, you must also provide a value for the other.
            :param cloud_watch_logging_options: Describes the Amazon CloudWatch logging options for your delivery stream.
            :param processing_configuration: Describes the data processing configuration.
            :param request_configuration: The configuration of the request sent to the HTTP endpoint specified as the destination.
            :param retry_options: Describes the retry behavior in case Kinesis Data Firehose is unable to deliver data to the specified HTTP endpoint destination, or if it doesn't receive a valid acknowledgment of receipt from the specified HTTP endpoint destination.
            :param role_arn: Kinesis Data Firehose uses this IAM role for all the permissions that the delivery stream needs.
            :param s3_backup_mode: Describes the S3 bucket backup options for the data that Kinesis Data Firehose delivers to the HTTP endpoint destination. You can back up all documents (AllData) or only the documents that Kinesis Data Firehose could not deliver to the specified HTTP endpoint destination (FailedDataOnly).

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                http_endpoint_destination_configuration_property = kinesisfirehose.CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty(
                    endpoint_configuration=kinesisfirehose.CfnDeliveryStream.HttpEndpointConfigurationProperty(
                        url="url",
                
                        # the properties below are optional
                        access_key="accessKey",
                        name="name"
                    ),
                    s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
                
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
                
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                        enabled=False,
                        processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                            type="type",
                
                            # the properties below are optional
                            parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                parameter_name="parameterName",
                                parameter_value="parameterValue"
                            )]
                        )]
                    ),
                    request_configuration=kinesisfirehose.CfnDeliveryStream.HttpEndpointRequestConfigurationProperty(
                        common_attributes=[kinesisfirehose.CfnDeliveryStream.HttpEndpointCommonAttributeProperty(
                            attribute_name="attributeName",
                            attribute_value="attributeValue"
                        )],
                        content_encoding="contentEncoding"
                    ),
                    retry_options=kinesisfirehose.CfnDeliveryStream.RetryOptionsProperty(
                        duration_in_seconds=123
                    ),
                    role_arn="roleArn",
                    s3_backup_mode="s3BackupMode"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__9da2769580ecd94e106f2765e1983fec915eeb9be0b44a009159785fd2e7533d)
                check_type(argname="argument endpoint_configuration", value=endpoint_configuration, expected_type=type_hints["endpoint_configuration"])
                check_type(argname="argument s3_configuration", value=s3_configuration, expected_type=type_hints["s3_configuration"])
                check_type(argname="argument buffering_hints", value=buffering_hints, expected_type=type_hints["buffering_hints"])
                check_type(argname="argument cloud_watch_logging_options", value=cloud_watch_logging_options, expected_type=type_hints["cloud_watch_logging_options"])
                check_type(argname="argument processing_configuration", value=processing_configuration, expected_type=type_hints["processing_configuration"])
                check_type(argname="argument request_configuration", value=request_configuration, expected_type=type_hints["request_configuration"])
                check_type(argname="argument retry_options", value=retry_options, expected_type=type_hints["retry_options"])
                check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
                check_type(argname="argument s3_backup_mode", value=s3_backup_mode, expected_type=type_hints["s3_backup_mode"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "endpoint_configuration": endpoint_configuration,
                "s3_configuration": s3_configuration,
            }
            if buffering_hints is not None:
                self._values["buffering_hints"] = buffering_hints
            if cloud_watch_logging_options is not None:
                self._values["cloud_watch_logging_options"] = cloud_watch_logging_options
            if processing_configuration is not None:
                self._values["processing_configuration"] = processing_configuration
            if request_configuration is not None:
                self._values["request_configuration"] = request_configuration
            if retry_options is not None:
                self._values["retry_options"] = retry_options
            if role_arn is not None:
                self._values["role_arn"] = role_arn
            if s3_backup_mode is not None:
                self._values["s3_backup_mode"] = s3_backup_mode

        @builtins.property
        def endpoint_configuration(
            self,
        ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.HttpEndpointConfigurationProperty"]:
            '''The configuration of the HTTP endpoint selected as the destination.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration-endpointconfiguration
            '''
            result = self._values.get("endpoint_configuration")
            assert result is not None, "Required property 'endpoint_configuration' is missing"
            return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.HttpEndpointConfigurationProperty"], result)

        @builtins.property
        def s3_configuration(
            self,
        ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]:
            '''Describes the configuration of a destination in Amazon S3.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration-s3configuration
            '''
            result = self._values.get("s3_configuration")
            assert result is not None, "Required property 's3_configuration' is missing"
            return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"], result)

        @builtins.property
        def buffering_hints(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.BufferingHintsProperty"]]:
            '''The buffering options that can be used before data is delivered to the specified destination.

            Kinesis Data Firehose treats these options as hints, and it might choose to use more optimal values. The SizeInMBs and IntervalInSeconds parameters are optional. However, if you specify a value for one of them, you must also provide a value for the other.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration-bufferinghints
            '''
            result = self._values.get("buffering_hints")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.BufferingHintsProperty"]], result)

        @builtins.property
        def cloud_watch_logging_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]:
            '''Describes the Amazon CloudWatch logging options for your delivery stream.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration-cloudwatchloggingoptions
            '''
            result = self._values.get("cloud_watch_logging_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]], result)

        @builtins.property
        def processing_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]]:
            '''Describes the data processing configuration.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration-processingconfiguration
            '''
            result = self._values.get("processing_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]], result)

        @builtins.property
        def request_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.HttpEndpointRequestConfigurationProperty"]]:
            '''The configuration of the request sent to the HTTP endpoint specified as the destination.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration-requestconfiguration
            '''
            result = self._values.get("request_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.HttpEndpointRequestConfigurationProperty"]], result)

        @builtins.property
        def retry_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.RetryOptionsProperty"]]:
            '''Describes the retry behavior in case Kinesis Data Firehose is unable to deliver data to the specified HTTP endpoint destination, or if it doesn't receive a valid acknowledgment of receipt from the specified HTTP endpoint destination.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration-retryoptions
            '''
            result = self._values.get("retry_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.RetryOptionsProperty"]], result)

        @builtins.property
        def role_arn(self) -> typing.Optional[builtins.str]:
            '''Kinesis Data Firehose uses this IAM role for all the permissions that the delivery stream needs.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration-rolearn
            '''
            result = self._values.get("role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def s3_backup_mode(self) -> typing.Optional[builtins.str]:
            '''Describes the S3 bucket backup options for the data that Kinesis Data Firehose delivers to the HTTP endpoint destination.

            You can back up all documents (AllData) or only the documents that Kinesis Data Firehose could not deliver to the specified HTTP endpoint destination (FailedDataOnly).

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration-s3backupmode
            '''
            result = self._values.get("s3_backup_mode")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "HttpEndpointDestinationConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.HttpEndpointRequestConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "common_attributes": "commonAttributes",
            "content_encoding": "contentEncoding",
        },
    )
    class HttpEndpointRequestConfigurationProperty:
        def __init__(
            self,
            *,
            common_attributes: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.HttpEndpointCommonAttributeProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
            content_encoding: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The configuration of the HTTP endpoint request.

            Kinesis Firehose supports any custom HTTP endpoint or HTTP endpoints owned by supported third-party service providers, including Datadog, MongoDB, and New Relic.

            :param common_attributes: Describes the metadata sent to the HTTP endpoint destination.
            :param content_encoding: Kinesis Data Firehose uses the content encoding to compress the body of a request before sending the request to the destination. For more information, see Content-Encoding in MDN Web Docs, the official Mozilla documentation.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointrequestconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                http_endpoint_request_configuration_property = kinesisfirehose.CfnDeliveryStream.HttpEndpointRequestConfigurationProperty(
                    common_attributes=[kinesisfirehose.CfnDeliveryStream.HttpEndpointCommonAttributeProperty(
                        attribute_name="attributeName",
                        attribute_value="attributeValue"
                    )],
                    content_encoding="contentEncoding"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__e8bcf30a55195d84f5779f2205689a586d95041d755b927e402e42d7c05e5517)
                check_type(argname="argument common_attributes", value=common_attributes, expected_type=type_hints["common_attributes"])
                check_type(argname="argument content_encoding", value=content_encoding, expected_type=type_hints["content_encoding"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if common_attributes is not None:
                self._values["common_attributes"] = common_attributes
            if content_encoding is not None:
                self._values["content_encoding"] = content_encoding

        @builtins.property
        def common_attributes(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.HttpEndpointCommonAttributeProperty"]]]]:
            '''Describes the metadata sent to the HTTP endpoint destination.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointrequestconfiguration.html#cfn-kinesisfirehose-deliverystream-httpendpointrequestconfiguration-commonattributes
            '''
            result = self._values.get("common_attributes")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.HttpEndpointCommonAttributeProperty"]]]], result)

        @builtins.property
        def content_encoding(self) -> typing.Optional[builtins.str]:
            '''Kinesis Data Firehose uses the content encoding to compress the body of a request before sending the request to the destination.

            For more information, see Content-Encoding in MDN Web Docs, the official Mozilla documentation.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-httpendpointrequestconfiguration.html#cfn-kinesisfirehose-deliverystream-httpendpointrequestconfiguration-contentencoding
            '''
            result = self._values.get("content_encoding")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "HttpEndpointRequestConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.InputFormatConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"deserializer": "deserializer"},
    )
    class InputFormatConfigurationProperty:
        def __init__(
            self,
            *,
            deserializer: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.DeserializerProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''Specifies the deserializer you want to use to convert the format of the input data.

            This parameter is required if ``Enabled`` is set to true.

            :param deserializer: Specifies which deserializer to use. You can choose either the Apache Hive JSON SerDe or the OpenX JSON SerDe. If both are non-null, the server rejects the request.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-inputformatconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                input_format_configuration_property = kinesisfirehose.CfnDeliveryStream.InputFormatConfigurationProperty(
                    deserializer=kinesisfirehose.CfnDeliveryStream.DeserializerProperty(
                        hive_json_ser_de=kinesisfirehose.CfnDeliveryStream.HiveJsonSerDeProperty(
                            timestamp_formats=["timestampFormats"]
                        ),
                        open_xJson_ser_de=kinesisfirehose.CfnDeliveryStream.OpenXJsonSerDeProperty(
                            case_insensitive=False,
                            column_to_json_key_mappings={
                                "column_to_json_key_mappings_key": "columnToJsonKeyMappings"
                            },
                            convert_dots_in_json_keys_to_underscores=False
                        )
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__abf568cc06c48e619bb8dc5dd2bba9a52bd57785b7679099a09474b33ececfae)
                check_type(argname="argument deserializer", value=deserializer, expected_type=type_hints["deserializer"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if deserializer is not None:
                self._values["deserializer"] = deserializer

        @builtins.property
        def deserializer(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.DeserializerProperty"]]:
            '''Specifies which deserializer to use.

            You can choose either the Apache Hive JSON SerDe or the OpenX JSON SerDe. If both are non-null, the server rejects the request.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-inputformatconfiguration.html#cfn-kinesisfirehose-deliverystream-inputformatconfiguration-deserializer
            '''
            result = self._values.get("deserializer")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.DeserializerProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "InputFormatConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty",
        jsii_struct_bases=[],
        name_mapping={"awskms_key_arn": "awskmsKeyArn"},
    )
    class KMSEncryptionConfigProperty:
        def __init__(self, *, awskms_key_arn: builtins.str) -> None:
            '''The ``KMSEncryptionConfig`` property type specifies the AWS Key Management Service ( AWS KMS) encryption key that Amazon Simple Storage Service (Amazon S3) uses to encrypt data delivered by the Amazon Kinesis Data Firehose (Kinesis Data Firehose) stream.

            :param awskms_key_arn: The Amazon Resource Name (ARN) of the AWS KMS encryption key that Amazon S3 uses to encrypt data delivered by the Kinesis Data Firehose stream. The key must belong to the same region as the destination S3 bucket.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kmsencryptionconfig.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                k_mSEncryption_config_property = kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                    awskms_key_arn="awskmsKeyArn"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__806a0ffe3fcdb9b58fca1024de724f2c20b40277a7e069981163196045cb57d5)
                check_type(argname="argument awskms_key_arn", value=awskms_key_arn, expected_type=type_hints["awskms_key_arn"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "awskms_key_arn": awskms_key_arn,
            }

        @builtins.property
        def awskms_key_arn(self) -> builtins.str:
            '''The Amazon Resource Name (ARN) of the AWS KMS encryption key that Amazon S3 uses to encrypt data delivered by the Kinesis Data Firehose stream.

            The key must belong to the same region as the destination S3 bucket.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kmsencryptionconfig.html#cfn-kinesisfirehose-deliverystream-kmsencryptionconfig-awskmskeyarn
            '''
            result = self._values.get("awskms_key_arn")
            assert result is not None, "Required property 'awskms_key_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "KMSEncryptionConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.KinesisStreamSourceConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"kinesis_stream_arn": "kinesisStreamArn", "role_arn": "roleArn"},
    )
    class KinesisStreamSourceConfigurationProperty:
        def __init__(
            self,
            *,
            kinesis_stream_arn: builtins.str,
            role_arn: builtins.str,
        ) -> None:
            '''The ``KinesisStreamSourceConfiguration`` property type specifies the stream and role Amazon Resource Names (ARNs) for a Kinesis stream used as the source for a delivery stream.

            :param kinesis_stream_arn: The ARN of the source Kinesis data stream.
            :param role_arn: The ARN of the role that provides access to the source Kinesis data stream.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                kinesis_stream_source_configuration_property = kinesisfirehose.CfnDeliveryStream.KinesisStreamSourceConfigurationProperty(
                    kinesis_stream_arn="kinesisStreamArn",
                    role_arn="roleArn"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__b558e16c3ed7bafe3284085610adc8a5035c9b2f00873a7996ae2b34ed4eed64)
                check_type(argname="argument kinesis_stream_arn", value=kinesis_stream_arn, expected_type=type_hints["kinesis_stream_arn"])
                check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "kinesis_stream_arn": kinesis_stream_arn,
                "role_arn": role_arn,
            }

        @builtins.property
        def kinesis_stream_arn(self) -> builtins.str:
            '''The ARN of the source Kinesis data stream.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration-kinesisstreamarn
            '''
            result = self._values.get("kinesis_stream_arn")
            assert result is not None, "Required property 'kinesis_stream_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''The ARN of the role that provides access to the source Kinesis data stream.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "KinesisStreamSourceConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.OpenXJsonSerDeProperty",
        jsii_struct_bases=[],
        name_mapping={
            "case_insensitive": "caseInsensitive",
            "column_to_json_key_mappings": "columnToJsonKeyMappings",
            "convert_dots_in_json_keys_to_underscores": "convertDotsInJsonKeysToUnderscores",
        },
    )
    class OpenXJsonSerDeProperty:
        def __init__(
            self,
            *,
            case_insensitive: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            column_to_json_key_mappings: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
            convert_dots_in_json_keys_to_underscores: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
        ) -> None:
            '''The OpenX SerDe.

            Used by Kinesis Data Firehose for deserializing data, which means converting it from the JSON format in preparation for serializing it to the Parquet or ORC format. This is one of two deserializers you can choose, depending on which one offers the functionality you need. The other option is the native Hive / HCatalog JsonSerDe.

            :param case_insensitive: When set to ``true`` , which is the default, Kinesis Data Firehose converts JSON keys to lowercase before deserializing them.
            :param column_to_json_key_mappings: Maps column names to JSON keys that aren't identical to the column names. This is useful when the JSON contains keys that are Hive keywords. For example, ``timestamp`` is a Hive keyword. If you have a JSON key named ``timestamp`` , set this parameter to ``{"ts": "timestamp"}`` to map this key to a column named ``ts`` .
            :param convert_dots_in_json_keys_to_underscores: When set to ``true`` , specifies that the names of the keys include dots and that you want Kinesis Data Firehose to replace them with underscores. This is useful because Apache Hive does not allow dots in column names. For example, if the JSON contains a key whose name is "a.b", you can define the column name to be "a_b" when using this option. The default is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-openxjsonserde.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                open_xJson_ser_de_property = kinesisfirehose.CfnDeliveryStream.OpenXJsonSerDeProperty(
                    case_insensitive=False,
                    column_to_json_key_mappings={
                        "column_to_json_key_mappings_key": "columnToJsonKeyMappings"
                    },
                    convert_dots_in_json_keys_to_underscores=False
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__3551efb35a233856fbede638ac90c11ed2820a5f93a0427d1c77390470a28b94)
                check_type(argname="argument case_insensitive", value=case_insensitive, expected_type=type_hints["case_insensitive"])
                check_type(argname="argument column_to_json_key_mappings", value=column_to_json_key_mappings, expected_type=type_hints["column_to_json_key_mappings"])
                check_type(argname="argument convert_dots_in_json_keys_to_underscores", value=convert_dots_in_json_keys_to_underscores, expected_type=type_hints["convert_dots_in_json_keys_to_underscores"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if case_insensitive is not None:
                self._values["case_insensitive"] = case_insensitive
            if column_to_json_key_mappings is not None:
                self._values["column_to_json_key_mappings"] = column_to_json_key_mappings
            if convert_dots_in_json_keys_to_underscores is not None:
                self._values["convert_dots_in_json_keys_to_underscores"] = convert_dots_in_json_keys_to_underscores

        @builtins.property
        def case_insensitive(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''When set to ``true`` , which is the default, Kinesis Data Firehose converts JSON keys to lowercase before deserializing them.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-openxjsonserde.html#cfn-kinesisfirehose-deliverystream-openxjsonserde-caseinsensitive
            '''
            result = self._values.get("case_insensitive")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def column_to_json_key_mappings(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
            '''Maps column names to JSON keys that aren't identical to the column names.

            This is useful when the JSON contains keys that are Hive keywords. For example, ``timestamp`` is a Hive keyword. If you have a JSON key named ``timestamp`` , set this parameter to ``{"ts": "timestamp"}`` to map this key to a column named ``ts`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-openxjsonserde.html#cfn-kinesisfirehose-deliverystream-openxjsonserde-columntojsonkeymappings
            '''
            result = self._values.get("column_to_json_key_mappings")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

        @builtins.property
        def convert_dots_in_json_keys_to_underscores(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''When set to ``true`` , specifies that the names of the keys include dots and that you want Kinesis Data Firehose to replace them with underscores.

            This is useful because Apache Hive does not allow dots in column names. For example, if the JSON contains a key whose name is "a.b", you can define the column name to be "a_b" when using this option.

            The default is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-openxjsonserde.html#cfn-kinesisfirehose-deliverystream-openxjsonserde-convertdotsinjsonkeystounderscores
            '''
            result = self._values.get("convert_dots_in_json_keys_to_underscores")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OpenXJsonSerDeProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.OrcSerDeProperty",
        jsii_struct_bases=[],
        name_mapping={
            "block_size_bytes": "blockSizeBytes",
            "bloom_filter_columns": "bloomFilterColumns",
            "bloom_filter_false_positive_probability": "bloomFilterFalsePositiveProbability",
            "compression": "compression",
            "dictionary_key_threshold": "dictionaryKeyThreshold",
            "enable_padding": "enablePadding",
            "format_version": "formatVersion",
            "padding_tolerance": "paddingTolerance",
            "row_index_stride": "rowIndexStride",
            "stripe_size_bytes": "stripeSizeBytes",
        },
    )
    class OrcSerDeProperty:
        def __init__(
            self,
            *,
            block_size_bytes: typing.Optional[jsii.Number] = None,
            bloom_filter_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
            bloom_filter_false_positive_probability: typing.Optional[jsii.Number] = None,
            compression: typing.Optional[builtins.str] = None,
            dictionary_key_threshold: typing.Optional[jsii.Number] = None,
            enable_padding: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            format_version: typing.Optional[builtins.str] = None,
            padding_tolerance: typing.Optional[jsii.Number] = None,
            row_index_stride: typing.Optional[jsii.Number] = None,
            stripe_size_bytes: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''A serializer to use for converting data to the ORC format before storing it in Amazon S3.

            For more information, see `Apache ORC <https://docs.aws.amazon.com/https://orc.apache.org/docs/>`_ .

            :param block_size_bytes: The Hadoop Distributed File System (HDFS) block size. This is useful if you intend to copy the data from Amazon S3 to HDFS before querying. The default is 256 MiB and the minimum is 64 MiB. Kinesis Data Firehose uses this value for padding calculations.
            :param bloom_filter_columns: The column names for which you want Kinesis Data Firehose to create bloom filters. The default is ``null`` .
            :param bloom_filter_false_positive_probability: The Bloom filter false positive probability (FPP). The lower the FPP, the bigger the Bloom filter. The default value is 0.05, the minimum is 0, and the maximum is 1.
            :param compression: The compression code to use over data blocks. The default is ``SNAPPY`` .
            :param dictionary_key_threshold: Represents the fraction of the total number of non-null rows. To turn off dictionary encoding, set this fraction to a number that is less than the number of distinct keys in a dictionary. To always use dictionary encoding, set this threshold to 1.
            :param enable_padding: Set this to ``true`` to indicate that you want stripes to be padded to the HDFS block boundaries. This is useful if you intend to copy the data from Amazon S3 to HDFS before querying. The default is ``false`` .
            :param format_version: The version of the file to write. The possible values are ``V0_11`` and ``V0_12`` . The default is ``V0_12`` .
            :param padding_tolerance: A number between 0 and 1 that defines the tolerance for block padding as a decimal fraction of stripe size. The default value is 0.05, which means 5 percent of stripe size. For the default values of 64 MiB ORC stripes and 256 MiB HDFS blocks, the default block padding tolerance of 5 percent reserves a maximum of 3.2 MiB for padding within the 256 MiB block. In such a case, if the available size within the block is more than 3.2 MiB, a new, smaller stripe is inserted to fit within that space. This ensures that no stripe crosses block boundaries and causes remote reads within a node-local task. Kinesis Data Firehose ignores this parameter when ``EnablePadding`` is ``false`` .
            :param row_index_stride: The number of rows between index entries. The default is 10,000 and the minimum is 1,000.
            :param stripe_size_bytes: The number of bytes in each stripe. The default is 64 MiB and the minimum is 8 MiB.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                orc_ser_de_property = kinesisfirehose.CfnDeliveryStream.OrcSerDeProperty(
                    block_size_bytes=123,
                    bloom_filter_columns=["bloomFilterColumns"],
                    bloom_filter_false_positive_probability=123,
                    compression="compression",
                    dictionary_key_threshold=123,
                    enable_padding=False,
                    format_version="formatVersion",
                    padding_tolerance=123,
                    row_index_stride=123,
                    stripe_size_bytes=123
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__08c892834827695bd4b65d6348cc7d06760ba7b2d3c7b1641fac41c6c484f039)
                check_type(argname="argument block_size_bytes", value=block_size_bytes, expected_type=type_hints["block_size_bytes"])
                check_type(argname="argument bloom_filter_columns", value=bloom_filter_columns, expected_type=type_hints["bloom_filter_columns"])
                check_type(argname="argument bloom_filter_false_positive_probability", value=bloom_filter_false_positive_probability, expected_type=type_hints["bloom_filter_false_positive_probability"])
                check_type(argname="argument compression", value=compression, expected_type=type_hints["compression"])
                check_type(argname="argument dictionary_key_threshold", value=dictionary_key_threshold, expected_type=type_hints["dictionary_key_threshold"])
                check_type(argname="argument enable_padding", value=enable_padding, expected_type=type_hints["enable_padding"])
                check_type(argname="argument format_version", value=format_version, expected_type=type_hints["format_version"])
                check_type(argname="argument padding_tolerance", value=padding_tolerance, expected_type=type_hints["padding_tolerance"])
                check_type(argname="argument row_index_stride", value=row_index_stride, expected_type=type_hints["row_index_stride"])
                check_type(argname="argument stripe_size_bytes", value=stripe_size_bytes, expected_type=type_hints["stripe_size_bytes"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if block_size_bytes is not None:
                self._values["block_size_bytes"] = block_size_bytes
            if bloom_filter_columns is not None:
                self._values["bloom_filter_columns"] = bloom_filter_columns
            if bloom_filter_false_positive_probability is not None:
                self._values["bloom_filter_false_positive_probability"] = bloom_filter_false_positive_probability
            if compression is not None:
                self._values["compression"] = compression
            if dictionary_key_threshold is not None:
                self._values["dictionary_key_threshold"] = dictionary_key_threshold
            if enable_padding is not None:
                self._values["enable_padding"] = enable_padding
            if format_version is not None:
                self._values["format_version"] = format_version
            if padding_tolerance is not None:
                self._values["padding_tolerance"] = padding_tolerance
            if row_index_stride is not None:
                self._values["row_index_stride"] = row_index_stride
            if stripe_size_bytes is not None:
                self._values["stripe_size_bytes"] = stripe_size_bytes

        @builtins.property
        def block_size_bytes(self) -> typing.Optional[jsii.Number]:
            '''The Hadoop Distributed File System (HDFS) block size.

            This is useful if you intend to copy the data from Amazon S3 to HDFS before querying. The default is 256 MiB and the minimum is 64 MiB. Kinesis Data Firehose uses this value for padding calculations.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-blocksizebytes
            '''
            result = self._values.get("block_size_bytes")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def bloom_filter_columns(self) -> typing.Optional[typing.List[builtins.str]]:
            '''The column names for which you want Kinesis Data Firehose to create bloom filters.

            The default is ``null`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-bloomfiltercolumns
            '''
            result = self._values.get("bloom_filter_columns")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def bloom_filter_false_positive_probability(
            self,
        ) -> typing.Optional[jsii.Number]:
            '''The Bloom filter false positive probability (FPP).

            The lower the FPP, the bigger the Bloom filter. The default value is 0.05, the minimum is 0, and the maximum is 1.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-bloomfilterfalsepositiveprobability
            '''
            result = self._values.get("bloom_filter_false_positive_probability")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def compression(self) -> typing.Optional[builtins.str]:
            '''The compression code to use over data blocks.

            The default is ``SNAPPY`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-compression
            '''
            result = self._values.get("compression")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def dictionary_key_threshold(self) -> typing.Optional[jsii.Number]:
            '''Represents the fraction of the total number of non-null rows.

            To turn off dictionary encoding, set this fraction to a number that is less than the number of distinct keys in a dictionary. To always use dictionary encoding, set this threshold to 1.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-dictionarykeythreshold
            '''
            result = self._values.get("dictionary_key_threshold")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def enable_padding(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''Set this to ``true`` to indicate that you want stripes to be padded to the HDFS block boundaries.

            This is useful if you intend to copy the data from Amazon S3 to HDFS before querying. The default is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-enablepadding
            '''
            result = self._values.get("enable_padding")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def format_version(self) -> typing.Optional[builtins.str]:
            '''The version of the file to write.

            The possible values are ``V0_11`` and ``V0_12`` . The default is ``V0_12`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-formatversion
            '''
            result = self._values.get("format_version")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def padding_tolerance(self) -> typing.Optional[jsii.Number]:
            '''A number between 0 and 1 that defines the tolerance for block padding as a decimal fraction of stripe size.

            The default value is 0.05, which means 5 percent of stripe size.

            For the default values of 64 MiB ORC stripes and 256 MiB HDFS blocks, the default block padding tolerance of 5 percent reserves a maximum of 3.2 MiB for padding within the 256 MiB block. In such a case, if the available size within the block is more than 3.2 MiB, a new, smaller stripe is inserted to fit within that space. This ensures that no stripe crosses block boundaries and causes remote reads within a node-local task.

            Kinesis Data Firehose ignores this parameter when ``EnablePadding`` is ``false`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-paddingtolerance
            '''
            result = self._values.get("padding_tolerance")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def row_index_stride(self) -> typing.Optional[jsii.Number]:
            '''The number of rows between index entries.

            The default is 10,000 and the minimum is 1,000.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-rowindexstride
            '''
            result = self._values.get("row_index_stride")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def stripe_size_bytes(self) -> typing.Optional[jsii.Number]:
            '''The number of bytes in each stripe.

            The default is 64 MiB and the minimum is 8 MiB.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-orcserde.html#cfn-kinesisfirehose-deliverystream-orcserde-stripesizebytes
            '''
            result = self._values.get("stripe_size_bytes")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OrcSerDeProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.OutputFormatConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"serializer": "serializer"},
    )
    class OutputFormatConfigurationProperty:
        def __init__(
            self,
            *,
            serializer: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.SerializerProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''Specifies the serializer that you want Kinesis Data Firehose to use to convert the format of your data before it writes it to Amazon S3.

            This parameter is required if ``Enabled`` is set to true.

            :param serializer: Specifies which serializer to use. You can choose either the ORC SerDe or the Parquet SerDe. If both are non-null, the server rejects the request.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-outputformatconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                output_format_configuration_property = kinesisfirehose.CfnDeliveryStream.OutputFormatConfigurationProperty(
                    serializer=kinesisfirehose.CfnDeliveryStream.SerializerProperty(
                        orc_ser_de=kinesisfirehose.CfnDeliveryStream.OrcSerDeProperty(
                            block_size_bytes=123,
                            bloom_filter_columns=["bloomFilterColumns"],
                            bloom_filter_false_positive_probability=123,
                            compression="compression",
                            dictionary_key_threshold=123,
                            enable_padding=False,
                            format_version="formatVersion",
                            padding_tolerance=123,
                            row_index_stride=123,
                            stripe_size_bytes=123
                        ),
                        parquet_ser_de=kinesisfirehose.CfnDeliveryStream.ParquetSerDeProperty(
                            block_size_bytes=123,
                            compression="compression",
                            enable_dictionary_compression=False,
                            max_padding_bytes=123,
                            page_size_bytes=123,
                            writer_version="writerVersion"
                        )
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__82e7bd19f3542137c87726835a971526bafee10f70b07746eb0dbb527f00033d)
                check_type(argname="argument serializer", value=serializer, expected_type=type_hints["serializer"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if serializer is not None:
                self._values["serializer"] = serializer

        @builtins.property
        def serializer(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.SerializerProperty"]]:
            '''Specifies which serializer to use.

            You can choose either the ORC SerDe or the Parquet SerDe. If both are non-null, the server rejects the request.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-outputformatconfiguration.html#cfn-kinesisfirehose-deliverystream-outputformatconfiguration-serializer
            '''
            result = self._values.get("serializer")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.SerializerProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OutputFormatConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ParquetSerDeProperty",
        jsii_struct_bases=[],
        name_mapping={
            "block_size_bytes": "blockSizeBytes",
            "compression": "compression",
            "enable_dictionary_compression": "enableDictionaryCompression",
            "max_padding_bytes": "maxPaddingBytes",
            "page_size_bytes": "pageSizeBytes",
            "writer_version": "writerVersion",
        },
    )
    class ParquetSerDeProperty:
        def __init__(
            self,
            *,
            block_size_bytes: typing.Optional[jsii.Number] = None,
            compression: typing.Optional[builtins.str] = None,
            enable_dictionary_compression: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            max_padding_bytes: typing.Optional[jsii.Number] = None,
            page_size_bytes: typing.Optional[jsii.Number] = None,
            writer_version: typing.Optional[builtins.str] = None,
        ) -> None:
            '''A serializer to use for converting data to the Parquet format before storing it in Amazon S3.

            For more information, see `Apache Parquet <https://docs.aws.amazon.com/https://parquet.apache.org/documentation/latest/>`_ .

            :param block_size_bytes: The Hadoop Distributed File System (HDFS) block size. This is useful if you intend to copy the data from Amazon S3 to HDFS before querying. The default is 256 MiB and the minimum is 64 MiB. Kinesis Data Firehose uses this value for padding calculations.
            :param compression: The compression code to use over data blocks. The possible values are ``UNCOMPRESSED`` , ``SNAPPY`` , and ``GZIP`` , with the default being ``SNAPPY`` . Use ``SNAPPY`` for higher decompression speed. Use ``GZIP`` if the compression ratio is more important than speed.
            :param enable_dictionary_compression: Indicates whether to enable dictionary compression.
            :param max_padding_bytes: The maximum amount of padding to apply. This is useful if you intend to copy the data from Amazon S3 to HDFS before querying. The default is 0.
            :param page_size_bytes: The Parquet page size. Column chunks are divided into pages. A page is conceptually an indivisible unit (in terms of compression and encoding). The minimum value is 64 KiB and the default is 1 MiB.
            :param writer_version: Indicates the version of row format to output. The possible values are ``V1`` and ``V2`` . The default is ``V1`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                parquet_ser_de_property = kinesisfirehose.CfnDeliveryStream.ParquetSerDeProperty(
                    block_size_bytes=123,
                    compression="compression",
                    enable_dictionary_compression=False,
                    max_padding_bytes=123,
                    page_size_bytes=123,
                    writer_version="writerVersion"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__552a9736b420f2f67862d21044c477b62849204fb4bcf6f864b093129f25bf9f)
                check_type(argname="argument block_size_bytes", value=block_size_bytes, expected_type=type_hints["block_size_bytes"])
                check_type(argname="argument compression", value=compression, expected_type=type_hints["compression"])
                check_type(argname="argument enable_dictionary_compression", value=enable_dictionary_compression, expected_type=type_hints["enable_dictionary_compression"])
                check_type(argname="argument max_padding_bytes", value=max_padding_bytes, expected_type=type_hints["max_padding_bytes"])
                check_type(argname="argument page_size_bytes", value=page_size_bytes, expected_type=type_hints["page_size_bytes"])
                check_type(argname="argument writer_version", value=writer_version, expected_type=type_hints["writer_version"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if block_size_bytes is not None:
                self._values["block_size_bytes"] = block_size_bytes
            if compression is not None:
                self._values["compression"] = compression
            if enable_dictionary_compression is not None:
                self._values["enable_dictionary_compression"] = enable_dictionary_compression
            if max_padding_bytes is not None:
                self._values["max_padding_bytes"] = max_padding_bytes
            if page_size_bytes is not None:
                self._values["page_size_bytes"] = page_size_bytes
            if writer_version is not None:
                self._values["writer_version"] = writer_version

        @builtins.property
        def block_size_bytes(self) -> typing.Optional[jsii.Number]:
            '''The Hadoop Distributed File System (HDFS) block size.

            This is useful if you intend to copy the data from Amazon S3 to HDFS before querying. The default is 256 MiB and the minimum is 64 MiB. Kinesis Data Firehose uses this value for padding calculations.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-blocksizebytes
            '''
            result = self._values.get("block_size_bytes")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def compression(self) -> typing.Optional[builtins.str]:
            '''The compression code to use over data blocks.

            The possible values are ``UNCOMPRESSED`` , ``SNAPPY`` , and ``GZIP`` , with the default being ``SNAPPY`` . Use ``SNAPPY`` for higher decompression speed. Use ``GZIP`` if the compression ratio is more important than speed.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-compression
            '''
            result = self._values.get("compression")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def enable_dictionary_compression(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''Indicates whether to enable dictionary compression.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-enabledictionarycompression
            '''
            result = self._values.get("enable_dictionary_compression")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def max_padding_bytes(self) -> typing.Optional[jsii.Number]:
            '''The maximum amount of padding to apply.

            This is useful if you intend to copy the data from Amazon S3 to HDFS before querying. The default is 0.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-maxpaddingbytes
            '''
            result = self._values.get("max_padding_bytes")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def page_size_bytes(self) -> typing.Optional[jsii.Number]:
            '''The Parquet page size.

            Column chunks are divided into pages. A page is conceptually an indivisible unit (in terms of compression and encoding). The minimum value is 64 KiB and the default is 1 MiB.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-pagesizebytes
            '''
            result = self._values.get("page_size_bytes")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def writer_version(self) -> typing.Optional[builtins.str]:
            '''Indicates the version of row format to output.

            The possible values are ``V1`` and ``V2`` . The default is ``V1`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-parquetserde.html#cfn-kinesisfirehose-deliverystream-parquetserde-writerversion
            '''
            result = self._values.get("writer_version")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ParquetSerDeProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"enabled": "enabled", "processors": "processors"},
    )
    class ProcessingConfigurationProperty:
        def __init__(
            self,
            *,
            enabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            processors: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.ProcessorProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
        ) -> None:
            '''The ``ProcessingConfiguration`` property configures data processing for an Amazon Kinesis Data Firehose delivery stream.

            :param enabled: Indicates whether data processing is enabled (true) or disabled (false).
            :param processors: The data processors.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processingconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                processing_configuration_property = kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                    enabled=False,
                    processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                        type="type",
                
                        # the properties below are optional
                        parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                            parameter_name="parameterName",
                            parameter_value="parameterValue"
                        )]
                    )]
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__d84d0741dab57ac754c89146652cdd4c4c129982af06fdb7d14d8ed08352fbef)
                check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
                check_type(argname="argument processors", value=processors, expected_type=type_hints["processors"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if enabled is not None:
                self._values["enabled"] = enabled
            if processors is not None:
                self._values["processors"] = processors

        @builtins.property
        def enabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''Indicates whether data processing is enabled (true) or disabled (false).

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processingconfiguration.html#cfn-kinesisfirehose-deliverystream-processingconfiguration-enabled
            '''
            result = self._values.get("enabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def processors(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessorProperty"]]]]:
            '''The data processors.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processingconfiguration.html#cfn-kinesisfirehose-deliverystream-processingconfiguration-processors
            '''
            result = self._values.get("processors")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessorProperty"]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ProcessingConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty",
        jsii_struct_bases=[],
        name_mapping={
            "parameter_name": "parameterName",
            "parameter_value": "parameterValue",
        },
    )
    class ProcessorParameterProperty:
        def __init__(
            self,
            *,
            parameter_name: builtins.str,
            parameter_value: builtins.str,
        ) -> None:
            '''The ``ProcessorParameter`` property specifies a processor parameter in a data processor for an Amazon Kinesis Data Firehose delivery stream.

            :param parameter_name: The name of the parameter. Currently the following default values are supported: 3 for ``NumberOfRetries`` and 60 for the ``BufferIntervalInSeconds`` . The ``BufferSizeInMBs`` ranges between 0.2 MB and up to 3MB. The default buffering hint is 1MB for all destinations, except Splunk. For Splunk, the default buffering hint is 256 KB.
            :param parameter_value: The parameter value.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processorparameter.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                processor_parameter_property = kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                    parameter_name="parameterName",
                    parameter_value="parameterValue"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__8c8b732be31b6e4628fa34d08f2376d9c6854b2be212583e866a51bdbdfc4402)
                check_type(argname="argument parameter_name", value=parameter_name, expected_type=type_hints["parameter_name"])
                check_type(argname="argument parameter_value", value=parameter_value, expected_type=type_hints["parameter_value"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "parameter_name": parameter_name,
                "parameter_value": parameter_value,
            }

        @builtins.property
        def parameter_name(self) -> builtins.str:
            '''The name of the parameter.

            Currently the following default values are supported: 3 for ``NumberOfRetries`` and 60 for the ``BufferIntervalInSeconds`` . The ``BufferSizeInMBs`` ranges between 0.2 MB and up to 3MB. The default buffering hint is 1MB for all destinations, except Splunk. For Splunk, the default buffering hint is 256 KB.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processorparameter.html#cfn-kinesisfirehose-deliverystream-processorparameter-parametername
            '''
            result = self._values.get("parameter_name")
            assert result is not None, "Required property 'parameter_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def parameter_value(self) -> builtins.str:
            '''The parameter value.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processorparameter.html#cfn-kinesisfirehose-deliverystream-processorparameter-parametervalue
            '''
            result = self._values.get("parameter_value")
            assert result is not None, "Required property 'parameter_value' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ProcessorParameterProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.ProcessorProperty",
        jsii_struct_bases=[],
        name_mapping={"type": "type", "parameters": "parameters"},
    )
    class ProcessorProperty:
        def __init__(
            self,
            *,
            type: builtins.str,
            parameters: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.ProcessorParameterProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
        ) -> None:
            '''The ``Processor`` property specifies a data processor for an Amazon Kinesis Data Firehose delivery stream.

            :param type: The type of processor. Valid values: ``Lambda`` .
            :param parameters: The processor parameters.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processor.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                processor_property = kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                    type="type",
                
                    # the properties below are optional
                    parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                        parameter_name="parameterName",
                        parameter_value="parameterValue"
                    )]
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__b7caf8713e44d471484486d33e703ae24cddc63555d3bcd7f1f2ed9a054663e1)
                check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "type": type,
            }
            if parameters is not None:
                self._values["parameters"] = parameters

        @builtins.property
        def type(self) -> builtins.str:
            '''The type of processor.

            Valid values: ``Lambda`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processor.html#cfn-kinesisfirehose-deliverystream-processor-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def parameters(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessorParameterProperty"]]]]:
            '''The processor parameters.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processor.html#cfn-kinesisfirehose-deliverystream-processor-parameters
            '''
            result = self._values.get("parameters")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessorParameterProperty"]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ProcessorProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.RedshiftDestinationConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "cluster_jdbcurl": "clusterJdbcurl",
            "copy_command": "copyCommand",
            "password": "password",
            "role_arn": "roleArn",
            "s3_configuration": "s3Configuration",
            "username": "username",
            "cloud_watch_logging_options": "cloudWatchLoggingOptions",
            "processing_configuration": "processingConfiguration",
            "retry_options": "retryOptions",
            "s3_backup_configuration": "s3BackupConfiguration",
            "s3_backup_mode": "s3BackupMode",
        },
    )
    class RedshiftDestinationConfigurationProperty:
        def __init__(
            self,
            *,
            cluster_jdbcurl: builtins.str,
            copy_command: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.CopyCommandProperty", typing.Dict[builtins.str, typing.Any]]],
            password: builtins.str,
            role_arn: builtins.str,
            s3_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.S3DestinationConfigurationProperty", typing.Dict[builtins.str, typing.Any]]],
            username: builtins.str,
            cloud_watch_logging_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.CloudWatchLoggingOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            processing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.ProcessingConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            retry_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.RedshiftRetryOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            s3_backup_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.S3DestinationConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            s3_backup_mode: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The ``RedshiftDestinationConfiguration`` property type specifies an Amazon Redshift cluster to which Amazon Kinesis Data Firehose (Kinesis Data Firehose) delivers data.

            :param cluster_jdbcurl: The connection string that Kinesis Data Firehose uses to connect to the Amazon Redshift cluster.
            :param copy_command: Configures the Amazon Redshift ``COPY`` command that Kinesis Data Firehose uses to load data into the cluster from the Amazon S3 bucket.
            :param password: The password for the Amazon Redshift user that you specified in the ``Username`` property.
            :param role_arn: The ARN of the AWS Identity and Access Management (IAM) role that grants Kinesis Data Firehose access to your Amazon S3 bucket and AWS KMS (if you enable data encryption). For more information, see `Grant Kinesis Data Firehose Access to an Amazon Redshift Destination <https://docs.aws.amazon.com/firehose/latest/dev/controlling-access.html#using-iam-rs>`_ in the *Amazon Kinesis Data Firehose Developer Guide* .
            :param s3_configuration: The S3 bucket where Kinesis Data Firehose first delivers data. After the data is in the bucket, Kinesis Data Firehose uses the ``COPY`` command to load the data into the Amazon Redshift cluster. For the Amazon S3 bucket's compression format, don't specify ``SNAPPY`` or ``ZIP`` because the Amazon Redshift ``COPY`` command doesn't support them.
            :param username: The Amazon Redshift user that has permission to access the Amazon Redshift cluster. This user must have ``INSERT`` privileges for copying data from the Amazon S3 bucket to the cluster.
            :param cloud_watch_logging_options: The CloudWatch logging options for your delivery stream.
            :param processing_configuration: The data processing configuration for the Kinesis Data Firehose delivery stream.
            :param retry_options: The retry behavior in case Kinesis Data Firehose is unable to deliver documents to Amazon Redshift. Default value is 3600 (60 minutes).
            :param s3_backup_configuration: The configuration for backup in Amazon S3.
            :param s3_backup_mode: The Amazon S3 backup mode. After you create a delivery stream, you can update it to enable Amazon S3 backup if it is disabled. If backup is enabled, you can't update the delivery stream to disable it.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                redshift_destination_configuration_property = kinesisfirehose.CfnDeliveryStream.RedshiftDestinationConfigurationProperty(
                    cluster_jdbcurl="clusterJdbcurl",
                    copy_command=kinesisfirehose.CfnDeliveryStream.CopyCommandProperty(
                        data_table_name="dataTableName",
                
                        # the properties below are optional
                        copy_options="copyOptions",
                        data_table_columns="dataTableColumns"
                    ),
                    password="password",
                    role_arn="roleArn",
                    s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
                
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
                    username="username",
                
                    # the properties below are optional
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                        enabled=False,
                        processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                            type="type",
                
                            # the properties below are optional
                            parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                parameter_name="parameterName",
                                parameter_value="parameterValue"
                            )]
                        )]
                    ),
                    retry_options=kinesisfirehose.CfnDeliveryStream.RedshiftRetryOptionsProperty(
                        duration_in_seconds=123
                    ),
                    s3_backup_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
                
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
                    s3_backup_mode="s3BackupMode"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__05398f5801a7e6c32361f8637f10bf9deec3962bc82c4443d41ed9d07c3a16f3)
                check_type(argname="argument cluster_jdbcurl", value=cluster_jdbcurl, expected_type=type_hints["cluster_jdbcurl"])
                check_type(argname="argument copy_command", value=copy_command, expected_type=type_hints["copy_command"])
                check_type(argname="argument password", value=password, expected_type=type_hints["password"])
                check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
                check_type(argname="argument s3_configuration", value=s3_configuration, expected_type=type_hints["s3_configuration"])
                check_type(argname="argument username", value=username, expected_type=type_hints["username"])
                check_type(argname="argument cloud_watch_logging_options", value=cloud_watch_logging_options, expected_type=type_hints["cloud_watch_logging_options"])
                check_type(argname="argument processing_configuration", value=processing_configuration, expected_type=type_hints["processing_configuration"])
                check_type(argname="argument retry_options", value=retry_options, expected_type=type_hints["retry_options"])
                check_type(argname="argument s3_backup_configuration", value=s3_backup_configuration, expected_type=type_hints["s3_backup_configuration"])
                check_type(argname="argument s3_backup_mode", value=s3_backup_mode, expected_type=type_hints["s3_backup_mode"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "cluster_jdbcurl": cluster_jdbcurl,
                "copy_command": copy_command,
                "password": password,
                "role_arn": role_arn,
                "s3_configuration": s3_configuration,
                "username": username,
            }
            if cloud_watch_logging_options is not None:
                self._values["cloud_watch_logging_options"] = cloud_watch_logging_options
            if processing_configuration is not None:
                self._values["processing_configuration"] = processing_configuration
            if retry_options is not None:
                self._values["retry_options"] = retry_options
            if s3_backup_configuration is not None:
                self._values["s3_backup_configuration"] = s3_backup_configuration
            if s3_backup_mode is not None:
                self._values["s3_backup_mode"] = s3_backup_mode

        @builtins.property
        def cluster_jdbcurl(self) -> builtins.str:
            '''The connection string that Kinesis Data Firehose uses to connect to the Amazon Redshift cluster.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-clusterjdbcurl
            '''
            result = self._values.get("cluster_jdbcurl")
            assert result is not None, "Required property 'cluster_jdbcurl' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def copy_command(
            self,
        ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CopyCommandProperty"]:
            '''Configures the Amazon Redshift ``COPY`` command that Kinesis Data Firehose uses to load data into the cluster from the Amazon S3 bucket.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-copycommand
            '''
            result = self._values.get("copy_command")
            assert result is not None, "Required property 'copy_command' is missing"
            return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CopyCommandProperty"], result)

        @builtins.property
        def password(self) -> builtins.str:
            '''The password for the Amazon Redshift user that you specified in the ``Username`` property.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-password
            '''
            result = self._values.get("password")
            assert result is not None, "Required property 'password' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''The ARN of the AWS Identity and Access Management (IAM) role that grants Kinesis Data Firehose access to your Amazon S3 bucket and AWS KMS (if you enable data encryption).

            For more information, see `Grant Kinesis Data Firehose Access to an Amazon Redshift Destination <https://docs.aws.amazon.com/firehose/latest/dev/controlling-access.html#using-iam-rs>`_ in the *Amazon Kinesis Data Firehose Developer Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def s3_configuration(
            self,
        ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]:
            '''The S3 bucket where Kinesis Data Firehose first delivers data.

            After the data is in the bucket, Kinesis Data Firehose uses the ``COPY`` command to load the data into the Amazon Redshift cluster. For the Amazon S3 bucket's compression format, don't specify ``SNAPPY`` or ``ZIP`` because the Amazon Redshift ``COPY`` command doesn't support them.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-s3configuration
            '''
            result = self._values.get("s3_configuration")
            assert result is not None, "Required property 's3_configuration' is missing"
            return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"], result)

        @builtins.property
        def username(self) -> builtins.str:
            '''The Amazon Redshift user that has permission to access the Amazon Redshift cluster.

            This user must have ``INSERT`` privileges for copying data from the Amazon S3 bucket to the cluster.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-username
            '''
            result = self._values.get("username")
            assert result is not None, "Required property 'username' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def cloud_watch_logging_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]:
            '''The CloudWatch logging options for your delivery stream.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-cloudwatchloggingoptions
            '''
            result = self._values.get("cloud_watch_logging_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]], result)

        @builtins.property
        def processing_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]]:
            '''The data processing configuration for the Kinesis Data Firehose delivery stream.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-processingconfiguration
            '''
            result = self._values.get("processing_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]], result)

        @builtins.property
        def retry_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.RedshiftRetryOptionsProperty"]]:
            '''The retry behavior in case Kinesis Data Firehose is unable to deliver documents to Amazon Redshift.

            Default value is 3600 (60 minutes).

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-retryoptions
            '''
            result = self._values.get("retry_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.RedshiftRetryOptionsProperty"]], result)

        @builtins.property
        def s3_backup_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]]:
            '''The configuration for backup in Amazon S3.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-s3backupconfiguration
            '''
            result = self._values.get("s3_backup_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]], result)

        @builtins.property
        def s3_backup_mode(self) -> typing.Optional[builtins.str]:
            '''The Amazon S3 backup mode.

            After you create a delivery stream, you can update it to enable Amazon S3 backup if it is disabled. If backup is enabled, you can't update the delivery stream to disable it.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration-s3backupmode
            '''
            result = self._values.get("s3_backup_mode")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RedshiftDestinationConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.RedshiftRetryOptionsProperty",
        jsii_struct_bases=[],
        name_mapping={"duration_in_seconds": "durationInSeconds"},
    )
    class RedshiftRetryOptionsProperty:
        def __init__(
            self,
            *,
            duration_in_seconds: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''Configures retry behavior in case Kinesis Data Firehose is unable to deliver documents to Amazon Redshift.

            :param duration_in_seconds: The length of time during which Kinesis Data Firehose retries delivery after a failure, starting from the initial request and including the first attempt. The default value is 3600 seconds (60 minutes). Kinesis Data Firehose does not retry if the value of ``DurationInSeconds`` is 0 (zero) or if the first delivery attempt takes longer than the current value.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftretryoptions.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                redshift_retry_options_property = kinesisfirehose.CfnDeliveryStream.RedshiftRetryOptionsProperty(
                    duration_in_seconds=123
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__e823bc3f086f79db3696fea5dd9ce50270c45f10b499d901a11a31fe512c102f)
                check_type(argname="argument duration_in_seconds", value=duration_in_seconds, expected_type=type_hints["duration_in_seconds"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if duration_in_seconds is not None:
                self._values["duration_in_seconds"] = duration_in_seconds

        @builtins.property
        def duration_in_seconds(self) -> typing.Optional[jsii.Number]:
            '''The length of time during which Kinesis Data Firehose retries delivery after a failure, starting from the initial request and including the first attempt.

            The default value is 3600 seconds (60 minutes). Kinesis Data Firehose does not retry if the value of ``DurationInSeconds`` is 0 (zero) or if the first delivery attempt takes longer than the current value.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-redshiftretryoptions.html#cfn-kinesisfirehose-deliverystream-redshiftretryoptions-durationinseconds
            '''
            result = self._values.get("duration_in_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RedshiftRetryOptionsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.RetryOptionsProperty",
        jsii_struct_bases=[],
        name_mapping={"duration_in_seconds": "durationInSeconds"},
    )
    class RetryOptionsProperty:
        def __init__(
            self,
            *,
            duration_in_seconds: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''Describes the retry behavior in case Kinesis Data Firehose is unable to deliver data to the specified HTTP endpoint destination, or if it doesn't receive a valid acknowledgment of receipt from the specified HTTP endpoint destination.

            Kinesis Firehose supports any custom HTTP endpoint or HTTP endpoints owned by supported third-party service providers, including Datadog, MongoDB, and New Relic.

            :param duration_in_seconds: The total amount of time that Kinesis Data Firehose spends on retries. This duration starts after the initial attempt to send data to the custom destination via HTTPS endpoint fails. It doesn't include the periods during which Kinesis Data Firehose waits for acknowledgment from the specified destination after each attempt.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-retryoptions.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                retry_options_property = kinesisfirehose.CfnDeliveryStream.RetryOptionsProperty(
                    duration_in_seconds=123
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__be620df4c1a415bc8ccf4d71d31c7000e344f78ab27b480feec242b390b16d58)
                check_type(argname="argument duration_in_seconds", value=duration_in_seconds, expected_type=type_hints["duration_in_seconds"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if duration_in_seconds is not None:
                self._values["duration_in_seconds"] = duration_in_seconds

        @builtins.property
        def duration_in_seconds(self) -> typing.Optional[jsii.Number]:
            '''The total amount of time that Kinesis Data Firehose spends on retries.

            This duration starts after the initial attempt to send data to the custom destination via HTTPS endpoint fails. It doesn't include the periods during which Kinesis Data Firehose waits for acknowledgment from the specified destination after each attempt.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-retryoptions.html#cfn-kinesisfirehose-deliverystream-retryoptions-durationinseconds
            '''
            result = self._values.get("duration_in_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RetryOptionsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "bucket_arn": "bucketArn",
            "role_arn": "roleArn",
            "buffering_hints": "bufferingHints",
            "cloud_watch_logging_options": "cloudWatchLoggingOptions",
            "compression_format": "compressionFormat",
            "encryption_configuration": "encryptionConfiguration",
            "error_output_prefix": "errorOutputPrefix",
            "prefix": "prefix",
        },
    )
    class S3DestinationConfigurationProperty:
        def __init__(
            self,
            *,
            bucket_arn: builtins.str,
            role_arn: builtins.str,
            buffering_hints: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.BufferingHintsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            cloud_watch_logging_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.CloudWatchLoggingOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            compression_format: typing.Optional[builtins.str] = None,
            encryption_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.EncryptionConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            error_output_prefix: typing.Optional[builtins.str] = None,
            prefix: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The ``S3DestinationConfiguration`` property type specifies an Amazon Simple Storage Service (Amazon S3) destination to which Amazon Kinesis Data Firehose (Kinesis Data Firehose) delivers data.

            :param bucket_arn: The Amazon Resource Name (ARN) of the Amazon S3 bucket to send data to.
            :param role_arn: The ARN of an AWS Identity and Access Management (IAM) role that grants Kinesis Data Firehose access to your Amazon S3 bucket and AWS KMS (if you enable data encryption). For more information, see `Grant Kinesis Data Firehose Access to an Amazon S3 Destination <https://docs.aws.amazon.com/firehose/latest/dev/controlling-access.html#using-iam-s3>`_ in the *Amazon Kinesis Data Firehose Developer Guide* .
            :param buffering_hints: Configures how Kinesis Data Firehose buffers incoming data while delivering it to the Amazon S3 bucket.
            :param cloud_watch_logging_options: The CloudWatch logging options for your delivery stream.
            :param compression_format: The type of compression that Kinesis Data Firehose uses to compress the data that it delivers to the Amazon S3 bucket. For valid values, see the ``CompressionFormat`` content for the `S3DestinationConfiguration <https://docs.aws.amazon.com/firehose/latest/APIReference/API_S3DestinationConfiguration.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .
            :param encryption_configuration: Configures Amazon Simple Storage Service (Amazon S3) server-side encryption. Kinesis Data Firehose uses AWS Key Management Service ( AWS KMS) to encrypt the data that it delivers to your Amazon S3 bucket.
            :param error_output_prefix: A prefix that Kinesis Data Firehose evaluates and adds to failed records before writing them to S3. This prefix appears immediately following the bucket name. For information about how to specify this prefix, see `Custom Prefixes for Amazon S3 Objects <https://docs.aws.amazon.com/firehose/latest/dev/s3-prefixes.html>`_ .
            :param prefix: A prefix that Kinesis Data Firehose adds to the files that it delivers to the Amazon S3 bucket. The prefix helps you identify the files that Kinesis Data Firehose delivered.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                s3_destination_configuration_property = kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                    bucket_arn="bucketArn",
                    role_arn="roleArn",
                
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    compression_format="compressionFormat",
                    encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                        kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                            awskms_key_arn="awskmsKeyArn"
                        ),
                        no_encryption_config="noEncryptionConfig"
                    ),
                    error_output_prefix="errorOutputPrefix",
                    prefix="prefix"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__6dc2094cec300f6dfe615a78ee1d7550b6c5b8eb4c40acd2a9cdb54351eb0e64)
                check_type(argname="argument bucket_arn", value=bucket_arn, expected_type=type_hints["bucket_arn"])
                check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
                check_type(argname="argument buffering_hints", value=buffering_hints, expected_type=type_hints["buffering_hints"])
                check_type(argname="argument cloud_watch_logging_options", value=cloud_watch_logging_options, expected_type=type_hints["cloud_watch_logging_options"])
                check_type(argname="argument compression_format", value=compression_format, expected_type=type_hints["compression_format"])
                check_type(argname="argument encryption_configuration", value=encryption_configuration, expected_type=type_hints["encryption_configuration"])
                check_type(argname="argument error_output_prefix", value=error_output_prefix, expected_type=type_hints["error_output_prefix"])
                check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "bucket_arn": bucket_arn,
                "role_arn": role_arn,
            }
            if buffering_hints is not None:
                self._values["buffering_hints"] = buffering_hints
            if cloud_watch_logging_options is not None:
                self._values["cloud_watch_logging_options"] = cloud_watch_logging_options
            if compression_format is not None:
                self._values["compression_format"] = compression_format
            if encryption_configuration is not None:
                self._values["encryption_configuration"] = encryption_configuration
            if error_output_prefix is not None:
                self._values["error_output_prefix"] = error_output_prefix
            if prefix is not None:
                self._values["prefix"] = prefix

        @builtins.property
        def bucket_arn(self) -> builtins.str:
            '''The Amazon Resource Name (ARN) of the Amazon S3 bucket to send data to.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-bucketarn
            '''
            result = self._values.get("bucket_arn")
            assert result is not None, "Required property 'bucket_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''The ARN of an AWS Identity and Access Management (IAM) role that grants Kinesis Data Firehose access to your Amazon S3 bucket and AWS KMS (if you enable data encryption).

            For more information, see `Grant Kinesis Data Firehose Access to an Amazon S3 Destination <https://docs.aws.amazon.com/firehose/latest/dev/controlling-access.html#using-iam-s3>`_ in the *Amazon Kinesis Data Firehose Developer Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def buffering_hints(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.BufferingHintsProperty"]]:
            '''Configures how Kinesis Data Firehose buffers incoming data while delivering it to the Amazon S3 bucket.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-bufferinghints
            '''
            result = self._values.get("buffering_hints")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.BufferingHintsProperty"]], result)

        @builtins.property
        def cloud_watch_logging_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]:
            '''The CloudWatch logging options for your delivery stream.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-cloudwatchloggingoptions
            '''
            result = self._values.get("cloud_watch_logging_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]], result)

        @builtins.property
        def compression_format(self) -> typing.Optional[builtins.str]:
            '''The type of compression that Kinesis Data Firehose uses to compress the data that it delivers to the Amazon S3 bucket.

            For valid values, see the ``CompressionFormat`` content for the `S3DestinationConfiguration <https://docs.aws.amazon.com/firehose/latest/APIReference/API_S3DestinationConfiguration.html>`_ data type in the *Amazon Kinesis Data Firehose API Reference* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-compressionformat
            '''
            result = self._values.get("compression_format")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def encryption_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.EncryptionConfigurationProperty"]]:
            '''Configures Amazon Simple Storage Service (Amazon S3) server-side encryption.

            Kinesis Data Firehose uses AWS Key Management Service ( AWS KMS) to encrypt the data that it delivers to your Amazon S3 bucket.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-encryptionconfiguration
            '''
            result = self._values.get("encryption_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.EncryptionConfigurationProperty"]], result)

        @builtins.property
        def error_output_prefix(self) -> typing.Optional[builtins.str]:
            '''A prefix that Kinesis Data Firehose evaluates and adds to failed records before writing them to S3.

            This prefix appears immediately following the bucket name. For information about how to specify this prefix, see `Custom Prefixes for Amazon S3 Objects <https://docs.aws.amazon.com/firehose/latest/dev/s3-prefixes.html>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-erroroutputprefix
            '''
            result = self._values.get("error_output_prefix")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def prefix(self) -> typing.Optional[builtins.str]:
            '''A prefix that Kinesis Data Firehose adds to the files that it delivers to the Amazon S3 bucket.

            The prefix helps you identify the files that Kinesis Data Firehose delivered.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-s3destinationconfiguration.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration-prefix
            '''
            result = self._values.get("prefix")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3DestinationConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.SchemaConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "catalog_id": "catalogId",
            "database_name": "databaseName",
            "region": "region",
            "role_arn": "roleArn",
            "table_name": "tableName",
            "version_id": "versionId",
        },
    )
    class SchemaConfigurationProperty:
        def __init__(
            self,
            *,
            catalog_id: typing.Optional[builtins.str] = None,
            database_name: typing.Optional[builtins.str] = None,
            region: typing.Optional[builtins.str] = None,
            role_arn: typing.Optional[builtins.str] = None,
            table_name: typing.Optional[builtins.str] = None,
            version_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Specifies the schema to which you want Kinesis Data Firehose to configure your data before it writes it to Amazon S3.

            This parameter is required if ``Enabled`` is set to true.

            :param catalog_id: The ID of the AWS Glue Data Catalog. If you don't supply this, the AWS account ID is used by default.
            :param database_name: Specifies the name of the AWS Glue database that contains the schema for the output data. .. epigraph:: If the ``SchemaConfiguration`` request parameter is used as part of invoking the ``CreateDeliveryStream`` API, then the ``DatabaseName`` property is required and its value must be specified.
            :param region: If you don't specify an AWS Region, the default is the current Region.
            :param role_arn: The role that Kinesis Data Firehose can use to access AWS Glue. This role must be in the same account you use for Kinesis Data Firehose. Cross-account roles aren't allowed. .. epigraph:: If the ``SchemaConfiguration`` request parameter is used as part of invoking the ``CreateDeliveryStream`` API, then the ``RoleARN`` property is required and its value must be specified.
            :param table_name: Specifies the AWS Glue table that contains the column information that constitutes your data schema. .. epigraph:: If the ``SchemaConfiguration`` request parameter is used as part of invoking the ``CreateDeliveryStream`` API, then the ``TableName`` property is required and its value must be specified.
            :param version_id: Specifies the table version for the output data schema. If you don't specify this version ID, or if you set it to ``LATEST`` , Kinesis Data Firehose uses the most recent version. This means that any updates to the table are automatically picked up.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                schema_configuration_property = kinesisfirehose.CfnDeliveryStream.SchemaConfigurationProperty(
                    catalog_id="catalogId",
                    database_name="databaseName",
                    region="region",
                    role_arn="roleArn",
                    table_name="tableName",
                    version_id="versionId"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__a14899683d146d767ed75ed1da35ea99fbf62704b76619410beb64dd48892959)
                check_type(argname="argument catalog_id", value=catalog_id, expected_type=type_hints["catalog_id"])
                check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
                check_type(argname="argument region", value=region, expected_type=type_hints["region"])
                check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
                check_type(argname="argument table_name", value=table_name, expected_type=type_hints["table_name"])
                check_type(argname="argument version_id", value=version_id, expected_type=type_hints["version_id"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if catalog_id is not None:
                self._values["catalog_id"] = catalog_id
            if database_name is not None:
                self._values["database_name"] = database_name
            if region is not None:
                self._values["region"] = region
            if role_arn is not None:
                self._values["role_arn"] = role_arn
            if table_name is not None:
                self._values["table_name"] = table_name
            if version_id is not None:
                self._values["version_id"] = version_id

        @builtins.property
        def catalog_id(self) -> typing.Optional[builtins.str]:
            '''The ID of the AWS Glue Data Catalog.

            If you don't supply this, the AWS account ID is used by default.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-catalogid
            '''
            result = self._values.get("catalog_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def database_name(self) -> typing.Optional[builtins.str]:
            '''Specifies the name of the AWS Glue database that contains the schema for the output data.

            .. epigraph::

               If the ``SchemaConfiguration`` request parameter is used as part of invoking the ``CreateDeliveryStream`` API, then the ``DatabaseName`` property is required and its value must be specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-databasename
            '''
            result = self._values.get("database_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def region(self) -> typing.Optional[builtins.str]:
            '''If you don't specify an AWS Region, the default is the current Region.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-region
            '''
            result = self._values.get("region")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def role_arn(self) -> typing.Optional[builtins.str]:
            '''The role that Kinesis Data Firehose can use to access AWS Glue.

            This role must be in the same account you use for Kinesis Data Firehose. Cross-account roles aren't allowed.
            .. epigraph::

               If the ``SchemaConfiguration`` request parameter is used as part of invoking the ``CreateDeliveryStream`` API, then the ``RoleARN`` property is required and its value must be specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-rolearn
            '''
            result = self._values.get("role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def table_name(self) -> typing.Optional[builtins.str]:
            '''Specifies the AWS Glue table that contains the column information that constitutes your data schema.

            .. epigraph::

               If the ``SchemaConfiguration`` request parameter is used as part of invoking the ``CreateDeliveryStream`` API, then the ``TableName`` property is required and its value must be specified.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-tablename
            '''
            result = self._values.get("table_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def version_id(self) -> typing.Optional[builtins.str]:
            '''Specifies the table version for the output data schema.

            If you don't specify this version ID, or if you set it to ``LATEST`` , Kinesis Data Firehose uses the most recent version. This means that any updates to the table are automatically picked up.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-schemaconfiguration.html#cfn-kinesisfirehose-deliverystream-schemaconfiguration-versionid
            '''
            result = self._values.get("version_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SchemaConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.SerializerProperty",
        jsii_struct_bases=[],
        name_mapping={"orc_ser_de": "orcSerDe", "parquet_ser_de": "parquetSerDe"},
    )
    class SerializerProperty:
        def __init__(
            self,
            *,
            orc_ser_de: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.OrcSerDeProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            parquet_ser_de: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.ParquetSerDeProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''The serializer that you want Kinesis Data Firehose to use to convert data to the target format before writing it to Amazon S3.

            Kinesis Data Firehose supports two types of serializers: the `ORC SerDe <https://docs.aws.amazon.com/https://hive.apache.org/javadocs/r1.2.2/api/org/apache/hadoop/hive/ql/io/orc/OrcSerde.html>`_ and the `Parquet SerDe <https://docs.aws.amazon.com/https://hive.apache.org/javadocs/r1.2.2/api/org/apache/hadoop/hive/ql/io/parquet/serde/ParquetHiveSerDe.html>`_ .

            :param orc_ser_de: A serializer to use for converting data to the ORC format before storing it in Amazon S3. For more information, see `Apache ORC <https://docs.aws.amazon.com/https://orc.apache.org/docs/>`_ .
            :param parquet_ser_de: A serializer to use for converting data to the Parquet format before storing it in Amazon S3. For more information, see `Apache Parquet <https://docs.aws.amazon.com/https://parquet.apache.org/documentation/latest/>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-serializer.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                serializer_property = kinesisfirehose.CfnDeliveryStream.SerializerProperty(
                    orc_ser_de=kinesisfirehose.CfnDeliveryStream.OrcSerDeProperty(
                        block_size_bytes=123,
                        bloom_filter_columns=["bloomFilterColumns"],
                        bloom_filter_false_positive_probability=123,
                        compression="compression",
                        dictionary_key_threshold=123,
                        enable_padding=False,
                        format_version="formatVersion",
                        padding_tolerance=123,
                        row_index_stride=123,
                        stripe_size_bytes=123
                    ),
                    parquet_ser_de=kinesisfirehose.CfnDeliveryStream.ParquetSerDeProperty(
                        block_size_bytes=123,
                        compression="compression",
                        enable_dictionary_compression=False,
                        max_padding_bytes=123,
                        page_size_bytes=123,
                        writer_version="writerVersion"
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__1766376bdbee6d374c3bc231dab3f0cd0f7b7145a1f92e9dbc34c7643e0e48e1)
                check_type(argname="argument orc_ser_de", value=orc_ser_de, expected_type=type_hints["orc_ser_de"])
                check_type(argname="argument parquet_ser_de", value=parquet_ser_de, expected_type=type_hints["parquet_ser_de"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if orc_ser_de is not None:
                self._values["orc_ser_de"] = orc_ser_de
            if parquet_ser_de is not None:
                self._values["parquet_ser_de"] = parquet_ser_de

        @builtins.property
        def orc_ser_de(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.OrcSerDeProperty"]]:
            '''A serializer to use for converting data to the ORC format before storing it in Amazon S3.

            For more information, see `Apache ORC <https://docs.aws.amazon.com/https://orc.apache.org/docs/>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-serializer.html#cfn-kinesisfirehose-deliverystream-serializer-orcserde
            '''
            result = self._values.get("orc_ser_de")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.OrcSerDeProperty"]], result)

        @builtins.property
        def parquet_ser_de(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ParquetSerDeProperty"]]:
            '''A serializer to use for converting data to the Parquet format before storing it in Amazon S3.

            For more information, see `Apache Parquet <https://docs.aws.amazon.com/https://parquet.apache.org/documentation/latest/>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-serializer.html#cfn-kinesisfirehose-deliverystream-serializer-parquetserde
            '''
            result = self._values.get("parquet_ser_de")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ParquetSerDeProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SerializerProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.SplunkDestinationConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "hec_endpoint": "hecEndpoint",
            "hec_endpoint_type": "hecEndpointType",
            "hec_token": "hecToken",
            "s3_configuration": "s3Configuration",
            "cloud_watch_logging_options": "cloudWatchLoggingOptions",
            "hec_acknowledgment_timeout_in_seconds": "hecAcknowledgmentTimeoutInSeconds",
            "processing_configuration": "processingConfiguration",
            "retry_options": "retryOptions",
            "s3_backup_mode": "s3BackupMode",
        },
    )
    class SplunkDestinationConfigurationProperty:
        def __init__(
            self,
            *,
            hec_endpoint: builtins.str,
            hec_endpoint_type: builtins.str,
            hec_token: builtins.str,
            s3_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.S3DestinationConfigurationProperty", typing.Dict[builtins.str, typing.Any]]],
            cloud_watch_logging_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.CloudWatchLoggingOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            hec_acknowledgment_timeout_in_seconds: typing.Optional[jsii.Number] = None,
            processing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.ProcessingConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            retry_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnDeliveryStream.SplunkRetryOptionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            s3_backup_mode: typing.Optional[builtins.str] = None,
        ) -> None:
            '''The ``SplunkDestinationConfiguration`` property type specifies the configuration of a destination in Splunk for a Kinesis Data Firehose delivery stream.

            :param hec_endpoint: The HTTP Event Collector (HEC) endpoint to which Kinesis Data Firehose sends your data.
            :param hec_endpoint_type: This type can be either ``Raw`` or ``Event`` .
            :param hec_token: This is a GUID that you obtain from your Splunk cluster when you create a new HEC endpoint.
            :param s3_configuration: The configuration for the backup Amazon S3 location.
            :param cloud_watch_logging_options: The Amazon CloudWatch logging options for your delivery stream.
            :param hec_acknowledgment_timeout_in_seconds: The amount of time that Kinesis Data Firehose waits to receive an acknowledgment from Splunk after it sends it data. At the end of the timeout period, Kinesis Data Firehose either tries to send the data again or considers it an error, based on your retry settings.
            :param processing_configuration: The data processing configuration.
            :param retry_options: The retry behavior in case Kinesis Data Firehose is unable to deliver data to Splunk, or if it doesn't receive an acknowledgment of receipt from Splunk.
            :param s3_backup_mode: Defines how documents should be delivered to Amazon S3. When set to ``FailedEventsOnly`` , Kinesis Data Firehose writes any data that could not be indexed to the configured Amazon S3 destination. When set to ``AllEvents`` , Kinesis Data Firehose delivers all incoming records to Amazon S3, and also writes failed documents to Amazon S3. The default value is ``FailedEventsOnly`` . You can update this backup mode from ``FailedEventsOnly`` to ``AllEvents`` . You can't update it from ``AllEvents`` to ``FailedEventsOnly`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                splunk_destination_configuration_property = kinesisfirehose.CfnDeliveryStream.SplunkDestinationConfigurationProperty(
                    hec_endpoint="hecEndpoint",
                    hec_endpoint_type="hecEndpointType",
                    hec_token="hecToken",
                    s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
                
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
                
                    # the properties below are optional
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    hec_acknowledgment_timeout_in_seconds=123,
                    processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                        enabled=False,
                        processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                            type="type",
                
                            # the properties below are optional
                            parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                parameter_name="parameterName",
                                parameter_value="parameterValue"
                            )]
                        )]
                    ),
                    retry_options=kinesisfirehose.CfnDeliveryStream.SplunkRetryOptionsProperty(
                        duration_in_seconds=123
                    ),
                    s3_backup_mode="s3BackupMode"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__a58a257e3c4b0cfd57a396f205706890c84f6239b23ee5486563e297297b9186)
                check_type(argname="argument hec_endpoint", value=hec_endpoint, expected_type=type_hints["hec_endpoint"])
                check_type(argname="argument hec_endpoint_type", value=hec_endpoint_type, expected_type=type_hints["hec_endpoint_type"])
                check_type(argname="argument hec_token", value=hec_token, expected_type=type_hints["hec_token"])
                check_type(argname="argument s3_configuration", value=s3_configuration, expected_type=type_hints["s3_configuration"])
                check_type(argname="argument cloud_watch_logging_options", value=cloud_watch_logging_options, expected_type=type_hints["cloud_watch_logging_options"])
                check_type(argname="argument hec_acknowledgment_timeout_in_seconds", value=hec_acknowledgment_timeout_in_seconds, expected_type=type_hints["hec_acknowledgment_timeout_in_seconds"])
                check_type(argname="argument processing_configuration", value=processing_configuration, expected_type=type_hints["processing_configuration"])
                check_type(argname="argument retry_options", value=retry_options, expected_type=type_hints["retry_options"])
                check_type(argname="argument s3_backup_mode", value=s3_backup_mode, expected_type=type_hints["s3_backup_mode"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "hec_endpoint": hec_endpoint,
                "hec_endpoint_type": hec_endpoint_type,
                "hec_token": hec_token,
                "s3_configuration": s3_configuration,
            }
            if cloud_watch_logging_options is not None:
                self._values["cloud_watch_logging_options"] = cloud_watch_logging_options
            if hec_acknowledgment_timeout_in_seconds is not None:
                self._values["hec_acknowledgment_timeout_in_seconds"] = hec_acknowledgment_timeout_in_seconds
            if processing_configuration is not None:
                self._values["processing_configuration"] = processing_configuration
            if retry_options is not None:
                self._values["retry_options"] = retry_options
            if s3_backup_mode is not None:
                self._values["s3_backup_mode"] = s3_backup_mode

        @builtins.property
        def hec_endpoint(self) -> builtins.str:
            '''The HTTP Event Collector (HEC) endpoint to which Kinesis Data Firehose sends your data.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hecendpoint
            '''
            result = self._values.get("hec_endpoint")
            assert result is not None, "Required property 'hec_endpoint' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def hec_endpoint_type(self) -> builtins.str:
            '''This type can be either ``Raw`` or ``Event`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hecendpointtype
            '''
            result = self._values.get("hec_endpoint_type")
            assert result is not None, "Required property 'hec_endpoint_type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def hec_token(self) -> builtins.str:
            '''This is a GUID that you obtain from your Splunk cluster when you create a new HEC endpoint.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hectoken
            '''
            result = self._values.get("hec_token")
            assert result is not None, "Required property 'hec_token' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def s3_configuration(
            self,
        ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"]:
            '''The configuration for the backup Amazon S3 location.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-s3configuration
            '''
            result = self._values.get("s3_configuration")
            assert result is not None, "Required property 's3_configuration' is missing"
            return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.S3DestinationConfigurationProperty"], result)

        @builtins.property
        def cloud_watch_logging_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]]:
            '''The Amazon CloudWatch logging options for your delivery stream.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-cloudwatchloggingoptions
            '''
            result = self._values.get("cloud_watch_logging_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.CloudWatchLoggingOptionsProperty"]], result)

        @builtins.property
        def hec_acknowledgment_timeout_in_seconds(self) -> typing.Optional[jsii.Number]:
            '''The amount of time that Kinesis Data Firehose waits to receive an acknowledgment from Splunk after it sends it data.

            At the end of the timeout period, Kinesis Data Firehose either tries to send the data again or considers it an error, based on your retry settings.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-hecacknowledgmenttimeoutinseconds
            '''
            result = self._values.get("hec_acknowledgment_timeout_in_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def processing_configuration(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]]:
            '''The data processing configuration.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-processingconfiguration
            '''
            result = self._values.get("processing_configuration")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.ProcessingConfigurationProperty"]], result)

        @builtins.property
        def retry_options(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.SplunkRetryOptionsProperty"]]:
            '''The retry behavior in case Kinesis Data Firehose is unable to deliver data to Splunk, or if it doesn't receive an acknowledgment of receipt from Splunk.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-retryoptions
            '''
            result = self._values.get("retry_options")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnDeliveryStream.SplunkRetryOptionsProperty"]], result)

        @builtins.property
        def s3_backup_mode(self) -> typing.Optional[builtins.str]:
            '''Defines how documents should be delivered to Amazon S3.

            When set to ``FailedEventsOnly`` , Kinesis Data Firehose writes any data that could not be indexed to the configured Amazon S3 destination. When set to ``AllEvents`` , Kinesis Data Firehose delivers all incoming records to Amazon S3, and also writes failed documents to Amazon S3. The default value is ``FailedEventsOnly`` .

            You can update this backup mode from ``FailedEventsOnly`` to ``AllEvents`` . You can't update it from ``AllEvents`` to ``FailedEventsOnly`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkdestinationconfiguration.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration-s3backupmode
            '''
            result = self._values.get("s3_backup_mode")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SplunkDestinationConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.SplunkRetryOptionsProperty",
        jsii_struct_bases=[],
        name_mapping={"duration_in_seconds": "durationInSeconds"},
    )
    class SplunkRetryOptionsProperty:
        def __init__(
            self,
            *,
            duration_in_seconds: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''The ``SplunkRetryOptions`` property type specifies retry behavior in case Kinesis Data Firehose is unable to deliver documents to Splunk or if it doesn't receive an acknowledgment from Splunk.

            :param duration_in_seconds: The total amount of time that Kinesis Data Firehose spends on retries. This duration starts after the initial attempt to send data to Splunk fails. It doesn't include the periods during which Kinesis Data Firehose waits for acknowledgment from Splunk after each attempt.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkretryoptions.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                splunk_retry_options_property = kinesisfirehose.CfnDeliveryStream.SplunkRetryOptionsProperty(
                    duration_in_seconds=123
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__c88c4e28642aa8d9fbafce93e773a6ebb10c6dbf117e663e1975ac09ee7905d0)
                check_type(argname="argument duration_in_seconds", value=duration_in_seconds, expected_type=type_hints["duration_in_seconds"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if duration_in_seconds is not None:
                self._values["duration_in_seconds"] = duration_in_seconds

        @builtins.property
        def duration_in_seconds(self) -> typing.Optional[jsii.Number]:
            '''The total amount of time that Kinesis Data Firehose spends on retries.

            This duration starts after the initial attempt to send data to Splunk fails. It doesn't include the periods during which Kinesis Data Firehose waits for acknowledgment from Splunk after each attempt.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-splunkretryoptions.html#cfn-kinesisfirehose-deliverystream-splunkretryoptions-durationinseconds
            '''
            result = self._values.get("duration_in_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SplunkRetryOptionsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStream.VpcConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "role_arn": "roleArn",
            "security_group_ids": "securityGroupIds",
            "subnet_ids": "subnetIds",
        },
    )
    class VpcConfigurationProperty:
        def __init__(
            self,
            *,
            role_arn: builtins.str,
            security_group_ids: typing.Sequence[builtins.str],
            subnet_ids: typing.Sequence[builtins.str],
        ) -> None:
            '''The details of the VPC of the Amazon ES destination.

            :param role_arn: The ARN of the IAM role that you want the delivery stream to use to create endpoints in the destination VPC. You can use your existing Kinesis Data Firehose delivery role or you can specify a new role. In either case, make sure that the role trusts the Kinesis Data Firehose service principal and that it grants the following permissions: - ``ec2:DescribeVpcs`` - ``ec2:DescribeVpcAttribute`` - ``ec2:DescribeSubnets`` - ``ec2:DescribeSecurityGroups`` - ``ec2:DescribeNetworkInterfaces`` - ``ec2:CreateNetworkInterface`` - ``ec2:CreateNetworkInterfacePermission`` - ``ec2:DeleteNetworkInterface`` If you revoke these permissions after you create the delivery stream, Kinesis Data Firehose can't scale out by creating more ENIs when necessary. You might therefore see a degradation in performance.
            :param security_group_ids: The IDs of the security groups that you want Kinesis Data Firehose to use when it creates ENIs in the VPC of the Amazon ES destination. You can use the same security group that the Amazon ES domain uses or different ones. If you specify different security groups here, ensure that they allow outbound HTTPS traffic to the Amazon ES domain's security group. Also ensure that the Amazon ES domain's security group allows HTTPS traffic from the security groups specified here. If you use the same security group for both your delivery stream and the Amazon ES domain, make sure the security group inbound rule allows HTTPS traffic.
            :param subnet_ids: The IDs of the subnets that Kinesis Data Firehose uses to create ENIs in the VPC of the Amazon ES destination. Make sure that the routing tables and inbound and outbound rules allow traffic to flow from the subnets whose IDs are specified here to the subnets that have the destination Amazon ES endpoints. Kinesis Data Firehose creates at least one ENI in each of the subnets that are specified here. Do not delete or modify these ENIs. The number of ENIs that Kinesis Data Firehose creates in the subnets specified here scales up and down automatically based on throughput. To enable Kinesis Data Firehose to scale up the number of ENIs to match throughput, ensure that you have sufficient quota. To help you calculate the quota you need, assume that Kinesis Data Firehose can create up to three ENIs for this delivery stream for each of the subnets specified here.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-vpcconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_kinesisfirehose as kinesisfirehose
                
                vpc_configuration_property = kinesisfirehose.CfnDeliveryStream.VpcConfigurationProperty(
                    role_arn="roleArn",
                    security_group_ids=["securityGroupIds"],
                    subnet_ids=["subnetIds"]
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__a21370b5b0c74765f64ec9a14f7ab5477c93d5817f1ee56a39e611363b6e54db)
                check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
                check_type(argname="argument security_group_ids", value=security_group_ids, expected_type=type_hints["security_group_ids"])
                check_type(argname="argument subnet_ids", value=subnet_ids, expected_type=type_hints["subnet_ids"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "role_arn": role_arn,
                "security_group_ids": security_group_ids,
                "subnet_ids": subnet_ids,
            }

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''The ARN of the IAM role that you want the delivery stream to use to create endpoints in the destination VPC.

            You can use your existing Kinesis Data Firehose delivery role or you can specify a new role. In either case, make sure that the role trusts the Kinesis Data Firehose service principal and that it grants the following permissions:

            - ``ec2:DescribeVpcs``
            - ``ec2:DescribeVpcAttribute``
            - ``ec2:DescribeSubnets``
            - ``ec2:DescribeSecurityGroups``
            - ``ec2:DescribeNetworkInterfaces``
            - ``ec2:CreateNetworkInterface``
            - ``ec2:CreateNetworkInterfacePermission``
            - ``ec2:DeleteNetworkInterface``

            If you revoke these permissions after you create the delivery stream, Kinesis Data Firehose can't scale out by creating more ENIs when necessary. You might therefore see a degradation in performance.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-vpcconfiguration.html#cfn-kinesisfirehose-deliverystream-vpcconfiguration-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def security_group_ids(self) -> typing.List[builtins.str]:
            '''The IDs of the security groups that you want Kinesis Data Firehose to use when it creates ENIs in the VPC of the Amazon ES destination.

            You can use the same security group that the Amazon ES domain uses or different ones. If you specify different security groups here, ensure that they allow outbound HTTPS traffic to the Amazon ES domain's security group. Also ensure that the Amazon ES domain's security group allows HTTPS traffic from the security groups specified here. If you use the same security group for both your delivery stream and the Amazon ES domain, make sure the security group inbound rule allows HTTPS traffic.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-vpcconfiguration.html#cfn-kinesisfirehose-deliverystream-vpcconfiguration-securitygroupids
            '''
            result = self._values.get("security_group_ids")
            assert result is not None, "Required property 'security_group_ids' is missing"
            return typing.cast(typing.List[builtins.str], result)

        @builtins.property
        def subnet_ids(self) -> typing.List[builtins.str]:
            '''The IDs of the subnets that Kinesis Data Firehose uses to create ENIs in the VPC of the Amazon ES destination.

            Make sure that the routing tables and inbound and outbound rules allow traffic to flow from the subnets whose IDs are specified here to the subnets that have the destination Amazon ES endpoints. Kinesis Data Firehose creates at least one ENI in each of the subnets that are specified here. Do not delete or modify these ENIs.

            The number of ENIs that Kinesis Data Firehose creates in the subnets specified here scales up and down automatically based on throughput. To enable Kinesis Data Firehose to scale up the number of ENIs to match throughput, ensure that you have sufficient quota. To help you calculate the quota you need, assume that Kinesis Data Firehose can create up to three ENIs for this delivery stream for each of the subnets specified here.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-vpcconfiguration.html#cfn-kinesisfirehose-deliverystream-vpcconfiguration-subnetids
            '''
            result = self._values.get("subnet_ids")
            assert result is not None, "Required property 'subnet_ids' is missing"
            return typing.cast(typing.List[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "VpcConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose.CfnDeliveryStreamProps",
    jsii_struct_bases=[],
    name_mapping={
        "amazon_open_search_serverless_destination_configuration": "amazonOpenSearchServerlessDestinationConfiguration",
        "amazonopensearchservice_destination_configuration": "amazonopensearchserviceDestinationConfiguration",
        "delivery_stream_encryption_configuration_input": "deliveryStreamEncryptionConfigurationInput",
        "delivery_stream_name": "deliveryStreamName",
        "delivery_stream_type": "deliveryStreamType",
        "elasticsearch_destination_configuration": "elasticsearchDestinationConfiguration",
        "extended_s3_destination_configuration": "extendedS3DestinationConfiguration",
        "http_endpoint_destination_configuration": "httpEndpointDestinationConfiguration",
        "kinesis_stream_source_configuration": "kinesisStreamSourceConfiguration",
        "redshift_destination_configuration": "redshiftDestinationConfiguration",
        "s3_destination_configuration": "s3DestinationConfiguration",
        "splunk_destination_configuration": "splunkDestinationConfiguration",
        "tags": "tags",
    },
)
class CfnDeliveryStreamProps:
    def __init__(
        self,
        *,
        amazon_open_search_serverless_destination_configuration: typing.Optional[typing.Union[typing.Union[CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]] = None,
        amazonopensearchservice_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        delivery_stream_encryption_configuration_input: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.DeliveryStreamEncryptionConfigurationInputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        delivery_stream_name: typing.Optional[builtins.str] = None,
        delivery_stream_type: typing.Optional[builtins.str] = None,
        elasticsearch_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        extended_s3_destination_configuration: typing.Optional[typing.Union[typing.Union[CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]] = None,
        http_endpoint_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        kinesis_stream_source_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.KinesisStreamSourceConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        redshift_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.RedshiftDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        s3_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.S3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        splunk_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.SplunkDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for defining a ``CfnDeliveryStream``.

        :param amazon_open_search_serverless_destination_configuration: ``AWS::KinesisFirehose::DeliveryStream.AmazonOpenSearchServerlessDestinationConfiguration``.
        :param amazonopensearchservice_destination_configuration: The destination in Amazon OpenSearch Service. You can specify only one destination.
        :param delivery_stream_encryption_configuration_input: Specifies the type and Amazon Resource Name (ARN) of the CMK to use for Server-Side Encryption (SSE).
        :param delivery_stream_name: The name of the delivery stream.
        :param delivery_stream_type: The delivery stream type. This can be one of the following values:. - ``DirectPut`` : Provider applications access the delivery stream directly. - ``KinesisStreamAsSource`` : The delivery stream uses a Kinesis data stream as a source.
        :param elasticsearch_destination_configuration: An Amazon ES destination for the delivery stream. Conditional. You must specify only one destination configuration. If you change the delivery stream destination from an Amazon ES destination to an Amazon S3 or Amazon Redshift destination, update requires `some interruptions <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-some-interrupt>`_ .
        :param extended_s3_destination_configuration: An Amazon S3 destination for the delivery stream. Conditional. You must specify only one destination configuration. If you change the delivery stream destination from an Amazon Extended S3 destination to an Amazon ES destination, update requires `some interruptions <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-some-interrupt>`_ .
        :param http_endpoint_destination_configuration: Enables configuring Kinesis Firehose to deliver data to any HTTP endpoint destination. You can specify only one destination.
        :param kinesis_stream_source_configuration: When a Kinesis stream is used as the source for the delivery stream, a `KinesisStreamSourceConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration.html>`_ containing the Kinesis stream ARN and the role ARN for the source stream.
        :param redshift_destination_configuration: An Amazon Redshift destination for the delivery stream. Conditional. You must specify only one destination configuration. If you change the delivery stream destination from an Amazon Redshift destination to an Amazon ES destination, update requires `some interruptions <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-some-interrupt>`_ .
        :param s3_destination_configuration: The ``S3DestinationConfiguration`` property type specifies an Amazon Simple Storage Service (Amazon S3) destination to which Amazon Kinesis Data Firehose (Kinesis Data Firehose) delivers data. Conditional. You must specify only one destination configuration. If you change the delivery stream destination from an Amazon S3 destination to an Amazon ES destination, update requires `some interruptions <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-some-interrupt>`_ .
        :param splunk_destination_configuration: The configuration of a destination in Splunk for the delivery stream.
        :param tags: A set of tags to assign to the delivery stream. A tag is a key-value pair that you can define and assign to AWS resources. Tags are metadata. For example, you can add friendly names and descriptions or other types of information that can help you distinguish the delivery stream. For more information about tags, see `Using Cost Allocation Tags <https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html>`_ in the AWS Billing and Cost Management User Guide. You can specify up to 50 tags when creating a delivery stream.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_kinesisfirehose as kinesisfirehose
            
            cfn_delivery_stream_props = kinesisfirehose.CfnDeliveryStreamProps(
                amazon_open_search_serverless_destination_configuration=kinesisfirehose.CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty(
                    index_name="indexName",
                    role_arn="roleArn",
                    s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
            
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
            
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.AmazonOpenSearchServerlessBufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    collection_endpoint="collectionEndpoint",
                    processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                        enabled=False,
                        processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                            type="type",
            
                            # the properties below are optional
                            parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                parameter_name="parameterName",
                                parameter_value="parameterValue"
                            )]
                        )]
                    ),
                    retry_options=kinesisfirehose.CfnDeliveryStream.AmazonOpenSearchServerlessRetryOptionsProperty(
                        duration_in_seconds=123
                    ),
                    s3_backup_mode="s3BackupMode",
                    vpc_configuration=kinesisfirehose.CfnDeliveryStream.VpcConfigurationProperty(
                        role_arn="roleArn",
                        security_group_ids=["securityGroupIds"],
                        subnet_ids=["subnetIds"]
                    )
                ),
                amazonopensearchservice_destination_configuration=kinesisfirehose.CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty(
                    index_name="indexName",
                    role_arn="roleArn",
                    s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
            
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
            
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.AmazonopensearchserviceBufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    cluster_endpoint="clusterEndpoint",
                    document_id_options=kinesisfirehose.CfnDeliveryStream.DocumentIdOptionsProperty(
                        default_document_id_format="defaultDocumentIdFormat"
                    ),
                    domain_arn="domainArn",
                    index_rotation_period="indexRotationPeriod",
                    processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                        enabled=False,
                        processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                            type="type",
            
                            # the properties below are optional
                            parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                parameter_name="parameterName",
                                parameter_value="parameterValue"
                            )]
                        )]
                    ),
                    retry_options=kinesisfirehose.CfnDeliveryStream.AmazonopensearchserviceRetryOptionsProperty(
                        duration_in_seconds=123
                    ),
                    s3_backup_mode="s3BackupMode",
                    type_name="typeName",
                    vpc_configuration=kinesisfirehose.CfnDeliveryStream.VpcConfigurationProperty(
                        role_arn="roleArn",
                        security_group_ids=["securityGroupIds"],
                        subnet_ids=["subnetIds"]
                    )
                ),
                delivery_stream_encryption_configuration_input=kinesisfirehose.CfnDeliveryStream.DeliveryStreamEncryptionConfigurationInputProperty(
                    key_type="keyType",
            
                    # the properties below are optional
                    key_arn="keyArn"
                ),
                delivery_stream_name="deliveryStreamName",
                delivery_stream_type="deliveryStreamType",
                elasticsearch_destination_configuration=kinesisfirehose.CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty(
                    index_name="indexName",
                    role_arn="roleArn",
                    s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
            
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
            
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.ElasticsearchBufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    cluster_endpoint="clusterEndpoint",
                    document_id_options=kinesisfirehose.CfnDeliveryStream.DocumentIdOptionsProperty(
                        default_document_id_format="defaultDocumentIdFormat"
                    ),
                    domain_arn="domainArn",
                    index_rotation_period="indexRotationPeriod",
                    processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                        enabled=False,
                        processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                            type="type",
            
                            # the properties below are optional
                            parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                parameter_name="parameterName",
                                parameter_value="parameterValue"
                            )]
                        )]
                    ),
                    retry_options=kinesisfirehose.CfnDeliveryStream.ElasticsearchRetryOptionsProperty(
                        duration_in_seconds=123
                    ),
                    s3_backup_mode="s3BackupMode",
                    type_name="typeName",
                    vpc_configuration=kinesisfirehose.CfnDeliveryStream.VpcConfigurationProperty(
                        role_arn="roleArn",
                        security_group_ids=["securityGroupIds"],
                        subnet_ids=["subnetIds"]
                    )
                ),
                extended_s3_destination_configuration=kinesisfirehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(
                    bucket_arn="bucketArn",
                    role_arn="roleArn",
            
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    compression_format="compressionFormat",
                    data_format_conversion_configuration=kinesisfirehose.CfnDeliveryStream.DataFormatConversionConfigurationProperty(
                        enabled=False,
                        input_format_configuration=kinesisfirehose.CfnDeliveryStream.InputFormatConfigurationProperty(
                            deserializer=kinesisfirehose.CfnDeliveryStream.DeserializerProperty(
                                hive_json_ser_de=kinesisfirehose.CfnDeliveryStream.HiveJsonSerDeProperty(
                                    timestamp_formats=["timestampFormats"]
                                ),
                                open_xJson_ser_de=kinesisfirehose.CfnDeliveryStream.OpenXJsonSerDeProperty(
                                    case_insensitive=False,
                                    column_to_json_key_mappings={
                                        "column_to_json_key_mappings_key": "columnToJsonKeyMappings"
                                    },
                                    convert_dots_in_json_keys_to_underscores=False
                                )
                            )
                        ),
                        output_format_configuration=kinesisfirehose.CfnDeliveryStream.OutputFormatConfigurationProperty(
                            serializer=kinesisfirehose.CfnDeliveryStream.SerializerProperty(
                                orc_ser_de=kinesisfirehose.CfnDeliveryStream.OrcSerDeProperty(
                                    block_size_bytes=123,
                                    bloom_filter_columns=["bloomFilterColumns"],
                                    bloom_filter_false_positive_probability=123,
                                    compression="compression",
                                    dictionary_key_threshold=123,
                                    enable_padding=False,
                                    format_version="formatVersion",
                                    padding_tolerance=123,
                                    row_index_stride=123,
                                    stripe_size_bytes=123
                                ),
                                parquet_ser_de=kinesisfirehose.CfnDeliveryStream.ParquetSerDeProperty(
                                    block_size_bytes=123,
                                    compression="compression",
                                    enable_dictionary_compression=False,
                                    max_padding_bytes=123,
                                    page_size_bytes=123,
                                    writer_version="writerVersion"
                                )
                            )
                        ),
                        schema_configuration=kinesisfirehose.CfnDeliveryStream.SchemaConfigurationProperty(
                            catalog_id="catalogId",
                            database_name="databaseName",
                            region="region",
                            role_arn="roleArn",
                            table_name="tableName",
                            version_id="versionId"
                        )
                    ),
                    dynamic_partitioning_configuration=kinesisfirehose.CfnDeliveryStream.DynamicPartitioningConfigurationProperty(
                        enabled=False,
                        retry_options=kinesisfirehose.CfnDeliveryStream.RetryOptionsProperty(
                            duration_in_seconds=123
                        )
                    ),
                    encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                        kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                            awskms_key_arn="awskmsKeyArn"
                        ),
                        no_encryption_config="noEncryptionConfig"
                    ),
                    error_output_prefix="errorOutputPrefix",
                    prefix="prefix",
                    processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                        enabled=False,
                        processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                            type="type",
            
                            # the properties below are optional
                            parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                parameter_name="parameterName",
                                parameter_value="parameterValue"
                            )]
                        )]
                    ),
                    s3_backup_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
            
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
                    s3_backup_mode="s3BackupMode"
                ),
                http_endpoint_destination_configuration=kinesisfirehose.CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty(
                    endpoint_configuration=kinesisfirehose.CfnDeliveryStream.HttpEndpointConfigurationProperty(
                        url="url",
            
                        # the properties below are optional
                        access_key="accessKey",
                        name="name"
                    ),
                    s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
            
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
            
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                        enabled=False,
                        processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                            type="type",
            
                            # the properties below are optional
                            parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                parameter_name="parameterName",
                                parameter_value="parameterValue"
                            )]
                        )]
                    ),
                    request_configuration=kinesisfirehose.CfnDeliveryStream.HttpEndpointRequestConfigurationProperty(
                        common_attributes=[kinesisfirehose.CfnDeliveryStream.HttpEndpointCommonAttributeProperty(
                            attribute_name="attributeName",
                            attribute_value="attributeValue"
                        )],
                        content_encoding="contentEncoding"
                    ),
                    retry_options=kinesisfirehose.CfnDeliveryStream.RetryOptionsProperty(
                        duration_in_seconds=123
                    ),
                    role_arn="roleArn",
                    s3_backup_mode="s3BackupMode"
                ),
                kinesis_stream_source_configuration=kinesisfirehose.CfnDeliveryStream.KinesisStreamSourceConfigurationProperty(
                    kinesis_stream_arn="kinesisStreamArn",
                    role_arn="roleArn"
                ),
                redshift_destination_configuration=kinesisfirehose.CfnDeliveryStream.RedshiftDestinationConfigurationProperty(
                    cluster_jdbcurl="clusterJdbcurl",
                    copy_command=kinesisfirehose.CfnDeliveryStream.CopyCommandProperty(
                        data_table_name="dataTableName",
            
                        # the properties below are optional
                        copy_options="copyOptions",
                        data_table_columns="dataTableColumns"
                    ),
                    password="password",
                    role_arn="roleArn",
                    s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
            
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
                    username="username",
            
                    # the properties below are optional
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                        enabled=False,
                        processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                            type="type",
            
                            # the properties below are optional
                            parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                parameter_name="parameterName",
                                parameter_value="parameterValue"
                            )]
                        )]
                    ),
                    retry_options=kinesisfirehose.CfnDeliveryStream.RedshiftRetryOptionsProperty(
                        duration_in_seconds=123
                    ),
                    s3_backup_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
            
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
                    s3_backup_mode="s3BackupMode"
                ),
                s3_destination_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                    bucket_arn="bucketArn",
                    role_arn="roleArn",
            
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    compression_format="compressionFormat",
                    encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                        kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                            awskms_key_arn="awskmsKeyArn"
                        ),
                        no_encryption_config="noEncryptionConfig"
                    ),
                    error_output_prefix="errorOutputPrefix",
                    prefix="prefix"
                ),
                splunk_destination_configuration=kinesisfirehose.CfnDeliveryStream.SplunkDestinationConfigurationProperty(
                    hec_endpoint="hecEndpoint",
                    hec_endpoint_type="hecEndpointType",
                    hec_token="hecToken",
                    s3_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
            
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
            
                    # the properties below are optional
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    hec_acknowledgment_timeout_in_seconds=123,
                    processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                        enabled=False,
                        processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                            type="type",
            
                            # the properties below are optional
                            parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                parameter_name="parameterName",
                                parameter_value="parameterValue"
                            )]
                        )]
                    ),
                    retry_options=kinesisfirehose.CfnDeliveryStream.SplunkRetryOptionsProperty(
                        duration_in_seconds=123
                    ),
                    s3_backup_mode="s3BackupMode"
                ),
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78fe85fc7f8702fa6acf4b2d6850582a03c47a40dfadab1895cacf75ace36a2f)
            check_type(argname="argument amazon_open_search_serverless_destination_configuration", value=amazon_open_search_serverless_destination_configuration, expected_type=type_hints["amazon_open_search_serverless_destination_configuration"])
            check_type(argname="argument amazonopensearchservice_destination_configuration", value=amazonopensearchservice_destination_configuration, expected_type=type_hints["amazonopensearchservice_destination_configuration"])
            check_type(argname="argument delivery_stream_encryption_configuration_input", value=delivery_stream_encryption_configuration_input, expected_type=type_hints["delivery_stream_encryption_configuration_input"])
            check_type(argname="argument delivery_stream_name", value=delivery_stream_name, expected_type=type_hints["delivery_stream_name"])
            check_type(argname="argument delivery_stream_type", value=delivery_stream_type, expected_type=type_hints["delivery_stream_type"])
            check_type(argname="argument elasticsearch_destination_configuration", value=elasticsearch_destination_configuration, expected_type=type_hints["elasticsearch_destination_configuration"])
            check_type(argname="argument extended_s3_destination_configuration", value=extended_s3_destination_configuration, expected_type=type_hints["extended_s3_destination_configuration"])
            check_type(argname="argument http_endpoint_destination_configuration", value=http_endpoint_destination_configuration, expected_type=type_hints["http_endpoint_destination_configuration"])
            check_type(argname="argument kinesis_stream_source_configuration", value=kinesis_stream_source_configuration, expected_type=type_hints["kinesis_stream_source_configuration"])
            check_type(argname="argument redshift_destination_configuration", value=redshift_destination_configuration, expected_type=type_hints["redshift_destination_configuration"])
            check_type(argname="argument s3_destination_configuration", value=s3_destination_configuration, expected_type=type_hints["s3_destination_configuration"])
            check_type(argname="argument splunk_destination_configuration", value=splunk_destination_configuration, expected_type=type_hints["splunk_destination_configuration"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if amazon_open_search_serverless_destination_configuration is not None:
            self._values["amazon_open_search_serverless_destination_configuration"] = amazon_open_search_serverless_destination_configuration
        if amazonopensearchservice_destination_configuration is not None:
            self._values["amazonopensearchservice_destination_configuration"] = amazonopensearchservice_destination_configuration
        if delivery_stream_encryption_configuration_input is not None:
            self._values["delivery_stream_encryption_configuration_input"] = delivery_stream_encryption_configuration_input
        if delivery_stream_name is not None:
            self._values["delivery_stream_name"] = delivery_stream_name
        if delivery_stream_type is not None:
            self._values["delivery_stream_type"] = delivery_stream_type
        if elasticsearch_destination_configuration is not None:
            self._values["elasticsearch_destination_configuration"] = elasticsearch_destination_configuration
        if extended_s3_destination_configuration is not None:
            self._values["extended_s3_destination_configuration"] = extended_s3_destination_configuration
        if http_endpoint_destination_configuration is not None:
            self._values["http_endpoint_destination_configuration"] = http_endpoint_destination_configuration
        if kinesis_stream_source_configuration is not None:
            self._values["kinesis_stream_source_configuration"] = kinesis_stream_source_configuration
        if redshift_destination_configuration is not None:
            self._values["redshift_destination_configuration"] = redshift_destination_configuration
        if s3_destination_configuration is not None:
            self._values["s3_destination_configuration"] = s3_destination_configuration
        if splunk_destination_configuration is not None:
            self._values["splunk_destination_configuration"] = splunk_destination_configuration
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def amazon_open_search_serverless_destination_configuration(
        self,
    ) -> typing.Optional[typing.Union[CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty, _aws_cdk_core_f4b25747.IResolvable]]:
        '''``AWS::KinesisFirehose::DeliveryStream.AmazonOpenSearchServerlessDestinationConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-amazonopensearchserverlessdestinationconfiguration
        '''
        result = self._values.get("amazon_open_search_serverless_destination_configuration")
        return typing.cast(typing.Optional[typing.Union[CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty, _aws_cdk_core_f4b25747.IResolvable]], result)

    @builtins.property
    def amazonopensearchservice_destination_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty]]:
        '''The destination in Amazon OpenSearch Service.

        You can specify only one destination.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-amazonopensearchservicedestinationconfiguration
        '''
        result = self._values.get("amazonopensearchservice_destination_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty]], result)

    @builtins.property
    def delivery_stream_encryption_configuration_input(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.DeliveryStreamEncryptionConfigurationInputProperty]]:
        '''Specifies the type and Amazon Resource Name (ARN) of the CMK to use for Server-Side Encryption (SSE).

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamencryptionconfigurationinput
        '''
        result = self._values.get("delivery_stream_encryption_configuration_input")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.DeliveryStreamEncryptionConfigurationInputProperty]], result)

    @builtins.property
    def delivery_stream_name(self) -> typing.Optional[builtins.str]:
        '''The name of the delivery stream.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamname
        '''
        result = self._values.get("delivery_stream_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delivery_stream_type(self) -> typing.Optional[builtins.str]:
        '''The delivery stream type. This can be one of the following values:.

        - ``DirectPut`` : Provider applications access the delivery stream directly.
        - ``KinesisStreamAsSource`` : The delivery stream uses a Kinesis data stream as a source.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-deliverystreamtype
        '''
        result = self._values.get("delivery_stream_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def elasticsearch_destination_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty]]:
        '''An Amazon ES destination for the delivery stream.

        Conditional. You must specify only one destination configuration.

        If you change the delivery stream destination from an Amazon ES destination to an Amazon S3 or Amazon Redshift destination, update requires `some interruptions <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-some-interrupt>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-elasticsearchdestinationconfiguration
        '''
        result = self._values.get("elasticsearch_destination_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty]], result)

    @builtins.property
    def extended_s3_destination_configuration(
        self,
    ) -> typing.Optional[typing.Union[CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty, _aws_cdk_core_f4b25747.IResolvable]]:
        '''An Amazon S3 destination for the delivery stream.

        Conditional. You must specify only one destination configuration.

        If you change the delivery stream destination from an Amazon Extended S3 destination to an Amazon ES destination, update requires `some interruptions <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-some-interrupt>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-extendeds3destinationconfiguration
        '''
        result = self._values.get("extended_s3_destination_configuration")
        return typing.cast(typing.Optional[typing.Union[CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty, _aws_cdk_core_f4b25747.IResolvable]], result)

    @builtins.property
    def http_endpoint_destination_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty]]:
        '''Enables configuring Kinesis Firehose to deliver data to any HTTP endpoint destination.

        You can specify only one destination.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-httpendpointdestinationconfiguration
        '''
        result = self._values.get("http_endpoint_destination_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty]], result)

    @builtins.property
    def kinesis_stream_source_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.KinesisStreamSourceConfigurationProperty]]:
        '''When a Kinesis stream is used as the source for the delivery stream, a `KinesisStreamSourceConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration.html>`_ containing the Kinesis stream ARN and the role ARN for the source stream.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-kinesisstreamsourceconfiguration
        '''
        result = self._values.get("kinesis_stream_source_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.KinesisStreamSourceConfigurationProperty]], result)

    @builtins.property
    def redshift_destination_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.RedshiftDestinationConfigurationProperty]]:
        '''An Amazon Redshift destination for the delivery stream.

        Conditional. You must specify only one destination configuration.

        If you change the delivery stream destination from an Amazon Redshift destination to an Amazon ES destination, update requires `some interruptions <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-some-interrupt>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-redshiftdestinationconfiguration
        '''
        result = self._values.get("redshift_destination_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.RedshiftDestinationConfigurationProperty]], result)

    @builtins.property
    def s3_destination_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.S3DestinationConfigurationProperty]]:
        '''The ``S3DestinationConfiguration`` property type specifies an Amazon Simple Storage Service (Amazon S3) destination to which Amazon Kinesis Data Firehose (Kinesis Data Firehose) delivers data.

        Conditional. You must specify only one destination configuration.

        If you change the delivery stream destination from an Amazon S3 destination to an Amazon ES destination, update requires `some interruptions <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-some-interrupt>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-s3destinationconfiguration
        '''
        result = self._values.get("s3_destination_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.S3DestinationConfigurationProperty]], result)

    @builtins.property
    def splunk_destination_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.SplunkDestinationConfigurationProperty]]:
        '''The configuration of a destination in Splunk for the delivery stream.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-splunkdestinationconfiguration
        '''
        result = self._values.get("splunk_destination_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.SplunkDestinationConfigurationProperty]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_core_f4b25747.CfnTag]]:
        '''A set of tags to assign to the delivery stream.

        A tag is a key-value pair that you can define and assign to AWS resources. Tags are metadata. For example, you can add friendly names and descriptions or other types of information that can help you distinguish the delivery stream. For more information about tags, see `Using Cost Allocation Tags <https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html>`_ in the AWS Billing and Cost Management User Guide.

        You can specify up to 50 tags when creating a delivery stream.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesisfirehose-deliverystream.html#cfn-kinesisfirehose-deliverystream-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_core_f4b25747.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDeliveryStreamProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose.DataProcessorBindOptions",
    jsii_struct_bases=[],
    name_mapping={"role": "role"},
)
class DataProcessorBindOptions:
    def __init__(self, *, role: _aws_cdk_aws_iam_940a1ce0.IRole) -> None:
        '''(experimental) Options when binding a DataProcessor to a delivery stream destination.

        :param role: (experimental) The IAM role assumed by Kinesis Data Firehose to write to the destination that this DataProcessor will bind to.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_iam as iam
            import aws_cdk.aws_kinesisfirehose as kinesisfirehose
            
            # role: iam.Role
            
            data_processor_bind_options = kinesisfirehose.DataProcessorBindOptions(
                role=role
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5991b79bb62866419e3049c10f52358c8b79ec8798f1d765a2243221da18418)
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role": role,
        }

    @builtins.property
    def role(self) -> _aws_cdk_aws_iam_940a1ce0.IRole:
        '''(experimental) The IAM role assumed by Kinesis Data Firehose to write to the destination that this DataProcessor will bind to.

        :stability: experimental
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.IRole, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataProcessorBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose.DataProcessorConfig",
    jsii_struct_bases=[],
    name_mapping={
        "processor_identifier": "processorIdentifier",
        "processor_type": "processorType",
    },
)
class DataProcessorConfig:
    def __init__(
        self,
        *,
        processor_identifier: typing.Union["DataProcessorIdentifier", typing.Dict[builtins.str, typing.Any]],
        processor_type: builtins.str,
    ) -> None:
        '''(experimental) The full configuration of a data processor.

        :param processor_identifier: (experimental) The key-value pair that identifies the underlying processor resource.
        :param processor_type: (experimental) The type of the underlying processor resource. Must be an accepted value in ``CfnDeliveryStream.ProcessorProperty.Type``.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_kinesisfirehose as kinesisfirehose
            
            data_processor_config = kinesisfirehose.DataProcessorConfig(
                processor_identifier=kinesisfirehose.DataProcessorIdentifier(
                    parameter_name="parameterName",
                    parameter_value="parameterValue"
                ),
                processor_type="processorType"
            )
        '''
        if isinstance(processor_identifier, dict):
            processor_identifier = DataProcessorIdentifier(**processor_identifier)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3f2f0047367717fb36fb6a891f032cf51e0748e53fc66f3675d36abf3390219)
            check_type(argname="argument processor_identifier", value=processor_identifier, expected_type=type_hints["processor_identifier"])
            check_type(argname="argument processor_type", value=processor_type, expected_type=type_hints["processor_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "processor_identifier": processor_identifier,
            "processor_type": processor_type,
        }

    @builtins.property
    def processor_identifier(self) -> "DataProcessorIdentifier":
        '''(experimental) The key-value pair that identifies the underlying processor resource.

        :stability: experimental
        '''
        result = self._values.get("processor_identifier")
        assert result is not None, "Required property 'processor_identifier' is missing"
        return typing.cast("DataProcessorIdentifier", result)

    @builtins.property
    def processor_type(self) -> builtins.str:
        '''(experimental) The type of the underlying processor resource.

        Must be an accepted value in ``CfnDeliveryStream.ProcessorProperty.Type``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processor.html#cfn-kinesisfirehose-deliverystream-processor-type
        :stability: experimental

        Example::

            "Lambda"
        '''
        result = self._values.get("processor_type")
        assert result is not None, "Required property 'processor_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataProcessorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose.DataProcessorIdentifier",
    jsii_struct_bases=[],
    name_mapping={
        "parameter_name": "parameterName",
        "parameter_value": "parameterValue",
    },
)
class DataProcessorIdentifier:
    def __init__(
        self,
        *,
        parameter_name: builtins.str,
        parameter_value: builtins.str,
    ) -> None:
        '''(experimental) The key-value pair that identifies the underlying processor resource.

        :param parameter_name: (experimental) The parameter name that corresponds to the processor resource's identifier. Must be an accepted value in ``CfnDeliveryStream.ProcessoryParameterProperty.ParameterName``.
        :param parameter_value: (experimental) The identifier of the underlying processor resource.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processorparameter.html
        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_kinesisfirehose as kinesisfirehose
            
            data_processor_identifier = kinesisfirehose.DataProcessorIdentifier(
                parameter_name="parameterName",
                parameter_value="parameterValue"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c62b61e71ca36a86b485c108e45a2befa13ca0ff42e8cbfa745f4c40ffefc2a5)
            check_type(argname="argument parameter_name", value=parameter_name, expected_type=type_hints["parameter_name"])
            check_type(argname="argument parameter_value", value=parameter_value, expected_type=type_hints["parameter_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "parameter_name": parameter_name,
            "parameter_value": parameter_value,
        }

    @builtins.property
    def parameter_name(self) -> builtins.str:
        '''(experimental) The parameter name that corresponds to the processor resource's identifier.

        Must be an accepted value in ``CfnDeliveryStream.ProcessoryParameterProperty.ParameterName``.

        :stability: experimental
        '''
        result = self._values.get("parameter_name")
        assert result is not None, "Required property 'parameter_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter_value(self) -> builtins.str:
        '''(experimental) The identifier of the underlying processor resource.

        :stability: experimental
        '''
        result = self._values.get("parameter_value")
        assert result is not None, "Required property 'parameter_value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataProcessorIdentifier(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose.DataProcessorProps",
    jsii_struct_bases=[],
    name_mapping={
        "buffer_interval": "bufferInterval",
        "buffer_size": "bufferSize",
        "retries": "retries",
    },
)
class DataProcessorProps:
    def __init__(
        self,
        *,
        buffer_interval: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        buffer_size: typing.Optional[_aws_cdk_core_f4b25747.Size] = None,
        retries: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Configure the data processor.

        :param buffer_interval: (experimental) The length of time Kinesis Data Firehose will buffer incoming data before calling the processor. s Default: Duration.minutes(1)
        :param buffer_size: (experimental) The amount of incoming data Kinesis Data Firehose will buffer before calling the processor. Default: Size.mebibytes(3)
        :param retries: (experimental) The number of times Kinesis Data Firehose will retry the processor invocation after a failure due to network timeout or invocation limits. Default: 3

        :stability: experimental
        :exampleMetadata: lit=../aws-kinesisfirehose-destinations/test/integ.s3-bucket.lit.ts infused

        Example::

            import path as path
            import aws_cdk.aws_kinesisfirehose as firehose
            import aws_cdk.aws_kms as kms
            import aws_cdk.aws_lambda_nodejs as lambdanodejs
            import aws_cdk.aws_logs as logs
            import aws_cdk.aws_s3 as s3
            import aws_cdk.core as cdk
            import aws_cdk.aws_kinesisfirehose_destinations as destinations
            
            app = cdk.App()
            
            stack = cdk.Stack(app, "aws-cdk-firehose-delivery-stream-s3-all-properties")
            
            bucket = s3.Bucket(stack, "Bucket",
                removal_policy=cdk.RemovalPolicy.DESTROY,
                auto_delete_objects=True
            )
            
            backup_bucket = s3.Bucket(stack, "BackupBucket",
                removal_policy=cdk.RemovalPolicy.DESTROY,
                auto_delete_objects=True
            )
            log_group = logs.LogGroup(stack, "LogGroup",
                removal_policy=cdk.RemovalPolicy.DESTROY
            )
            
            data_processor_function = lambdanodejs.NodejsFunction(stack, "DataProcessorFunction",
                entry=path.join(__dirname, "lambda-data-processor.js"),
                timeout=cdk.Duration.minutes(1)
            )
            
            processor = firehose.LambdaFunctionProcessor(data_processor_function,
                buffer_interval=cdk.Duration.seconds(60),
                buffer_size=cdk.Size.mebibytes(1),
                retries=1
            )
            
            key = kms.Key(stack, "Key",
                removal_policy=cdk.RemovalPolicy.DESTROY
            )
            
            backup_key = kms.Key(stack, "BackupKey",
                removal_policy=cdk.RemovalPolicy.DESTROY
            )
            
            firehose.DeliveryStream(stack, "Delivery Stream",
                destinations=[destinations.S3Bucket(bucket,
                    logging=True,
                    log_group=log_group,
                    processor=processor,
                    compression=destinations.Compression.GZIP,
                    data_output_prefix="regularPrefix",
                    error_output_prefix="errorPrefix",
                    buffering_interval=cdk.Duration.seconds(60),
                    buffering_size=cdk.Size.mebibytes(1),
                    encryption_key=key,
                    s3_backup=destinations.DestinationS3BackupProps(
                        mode=destinations.BackupMode.ALL,
                        bucket=backup_bucket,
                        compression=destinations.Compression.ZIP,
                        data_output_prefix="backupPrefix",
                        error_output_prefix="backupErrorPrefix",
                        buffering_interval=cdk.Duration.seconds(60),
                        buffering_size=cdk.Size.mebibytes(1),
                        encryption_key=backup_key
                    )
                )]
            )
            
            app.synth()
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__326d7b3a20befe27b15d80e056ca11ec0f092bc0263109a4f7ae33e511facdf5)
            check_type(argname="argument buffer_interval", value=buffer_interval, expected_type=type_hints["buffer_interval"])
            check_type(argname="argument buffer_size", value=buffer_size, expected_type=type_hints["buffer_size"])
            check_type(argname="argument retries", value=retries, expected_type=type_hints["retries"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if buffer_interval is not None:
            self._values["buffer_interval"] = buffer_interval
        if buffer_size is not None:
            self._values["buffer_size"] = buffer_size
        if retries is not None:
            self._values["retries"] = retries

    @builtins.property
    def buffer_interval(self) -> typing.Optional[_aws_cdk_core_f4b25747.Duration]:
        '''(experimental) The length of time Kinesis Data Firehose will buffer incoming data before calling the processor.

        s

        :default: Duration.minutes(1)

        :stability: experimental
        '''
        result = self._values.get("buffer_interval")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Duration], result)

    @builtins.property
    def buffer_size(self) -> typing.Optional[_aws_cdk_core_f4b25747.Size]:
        '''(experimental) The amount of incoming data Kinesis Data Firehose will buffer before calling the processor.

        :default: Size.mebibytes(3)

        :stability: experimental
        '''
        result = self._values.get("buffer_size")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Size], result)

    @builtins.property
    def retries(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of times Kinesis Data Firehose will retry the processor invocation after a failure due to network timeout or invocation limits.

        :default: 3

        :stability: experimental
        '''
        result = self._values.get("retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataProcessorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose.DeliveryStreamAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "delivery_stream_arn": "deliveryStreamArn",
        "delivery_stream_name": "deliveryStreamName",
        "role": "role",
    },
)
class DeliveryStreamAttributes:
    def __init__(
        self,
        *,
        delivery_stream_arn: typing.Optional[builtins.str] = None,
        delivery_stream_name: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    ) -> None:
        '''(experimental) A full specification of a delivery stream that can be used to import it fluently into the CDK application.

        :param delivery_stream_arn: (experimental) The ARN of the delivery stream. At least one of deliveryStreamArn and deliveryStreamName must be provided. Default: - derived from ``deliveryStreamName``.
        :param delivery_stream_name: (experimental) The name of the delivery stream. At least one of deliveryStreamName and deliveryStreamArn must be provided. Default: - derived from ``deliveryStreamArn``.
        :param role: (experimental) The IAM role associated with this delivery stream. Assumed by Kinesis Data Firehose to read from sources and encrypt data server-side. Default: - the imported stream cannot be granted access to other resources as an ``iam.IGrantable``.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_iam as iam
            import aws_cdk.aws_kinesisfirehose as kinesisfirehose
            
            # role: iam.Role
            
            delivery_stream_attributes = kinesisfirehose.DeliveryStreamAttributes(
                delivery_stream_arn="deliveryStreamArn",
                delivery_stream_name="deliveryStreamName",
                role=role
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a3f59a2d368279099b3af6994cb0e2ba7543329d2e0ca9428227c573d63b55d)
            check_type(argname="argument delivery_stream_arn", value=delivery_stream_arn, expected_type=type_hints["delivery_stream_arn"])
            check_type(argname="argument delivery_stream_name", value=delivery_stream_name, expected_type=type_hints["delivery_stream_name"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if delivery_stream_arn is not None:
            self._values["delivery_stream_arn"] = delivery_stream_arn
        if delivery_stream_name is not None:
            self._values["delivery_stream_name"] = delivery_stream_name
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def delivery_stream_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the delivery stream.

        At least one of deliveryStreamArn and deliveryStreamName must be provided.

        :default: - derived from ``deliveryStreamName``.

        :stability: experimental
        '''
        result = self._values.get("delivery_stream_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delivery_stream_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the delivery stream.

        At least one of deliveryStreamName and deliveryStreamArn  must be provided.

        :default: - derived from ``deliveryStreamArn``.

        :stability: experimental
        '''
        result = self._values.get("delivery_stream_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole]:
        '''(experimental) The IAM role associated with this delivery stream.

        Assumed by Kinesis Data Firehose to read from sources and encrypt data server-side.

        :default: - the imported stream cannot be granted access to other resources as an ``iam.IGrantable``.

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeliveryStreamAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose.DeliveryStreamProps",
    jsii_struct_bases=[],
    name_mapping={
        "destinations": "destinations",
        "delivery_stream_name": "deliveryStreamName",
        "encryption": "encryption",
        "encryption_key": "encryptionKey",
        "role": "role",
        "source_stream": "sourceStream",
    },
)
class DeliveryStreamProps:
    def __init__(
        self,
        *,
        destinations: typing.Sequence["IDestination"],
        delivery_stream_name: typing.Optional[builtins.str] = None,
        encryption: typing.Optional["StreamEncryption"] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
        source_stream: typing.Optional[_aws_cdk_aws_kinesis_0674c215.IStream] = None,
    ) -> None:
        '''(experimental) Properties for a new delivery stream.

        :param destinations: (experimental) The destinations that this delivery stream will deliver data to. Only a singleton array is supported at this time.
        :param delivery_stream_name: (experimental) A name for the delivery stream. Default: - a name is generated by CloudFormation.
        :param encryption: (experimental) Indicates the type of customer master key (CMK) to use for server-side encryption, if any. Default: StreamEncryption.UNENCRYPTED - unless ``encryptionKey`` is provided, in which case this will be implicitly set to ``StreamEncryption.CUSTOMER_MANAGED``
        :param encryption_key: (experimental) Customer managed key to server-side encrypt data in the stream. Default: - no KMS key will be used; if ``encryption`` is set to ``CUSTOMER_MANAGED``, a KMS key will be created for you
        :param role: (experimental) The IAM role associated with this delivery stream. Assumed by Kinesis Data Firehose to read from sources and encrypt data server-side. Default: - a role will be created with default permissions.
        :param source_stream: (experimental) The Kinesis data stream to use as a source for this delivery stream. Default: - data must be written to the delivery stream via a direct put.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # bucket: s3.Bucket
            # Provide a Lambda function that will transform records before delivery, with custom
            # buffering and retry configuration
            lambda_function = lambda_.Function(self, "Processor",
                runtime=lambda_.Runtime.NODEJS_14_X,
                handler="index.handler",
                code=lambda_.Code.from_asset(path.join(__dirname, "process-records"))
            )
            lambda_processor = firehose.LambdaFunctionProcessor(lambda_function,
                buffer_interval=Duration.minutes(5),
                buffer_size=Size.mebibytes(5),
                retries=5
            )
            s3_destination = destinations.S3Bucket(bucket,
                processor=lambda_processor
            )
            firehose.DeliveryStream(self, "Delivery Stream",
                destinations=[s3_destination]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29c9d9445e0c324d1f43d9979f2ce42695925446cdcbb7270e0efd30c8041f52)
            check_type(argname="argument destinations", value=destinations, expected_type=type_hints["destinations"])
            check_type(argname="argument delivery_stream_name", value=delivery_stream_name, expected_type=type_hints["delivery_stream_name"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument source_stream", value=source_stream, expected_type=type_hints["source_stream"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destinations": destinations,
        }
        if delivery_stream_name is not None:
            self._values["delivery_stream_name"] = delivery_stream_name
        if encryption is not None:
            self._values["encryption"] = encryption
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if role is not None:
            self._values["role"] = role
        if source_stream is not None:
            self._values["source_stream"] = source_stream

    @builtins.property
    def destinations(self) -> typing.List["IDestination"]:
        '''(experimental) The destinations that this delivery stream will deliver data to.

        Only a singleton array is supported at this time.

        :stability: experimental
        '''
        result = self._values.get("destinations")
        assert result is not None, "Required property 'destinations' is missing"
        return typing.cast(typing.List["IDestination"], result)

    @builtins.property
    def delivery_stream_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the delivery stream.

        :default: - a name is generated by CloudFormation.

        :stability: experimental
        '''
        result = self._values.get("delivery_stream_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption(self) -> typing.Optional["StreamEncryption"]:
        '''(experimental) Indicates the type of customer master key (CMK) to use for server-side encryption, if any.

        :default: StreamEncryption.UNENCRYPTED - unless ``encryptionKey`` is provided, in which case this will be implicitly set to ``StreamEncryption.CUSTOMER_MANAGED``

        :stability: experimental
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional["StreamEncryption"], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey]:
        '''(experimental) Customer managed key to server-side encrypt data in the stream.

        :default: - no KMS key will be used; if ``encryption`` is set to ``CUSTOMER_MANAGED``, a KMS key will be created for you

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole]:
        '''(experimental) The IAM role associated with this delivery stream.

        Assumed by Kinesis Data Firehose to read from sources and encrypt data server-side.

        :default: - a role will be created with default permissions.

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole], result)

    @builtins.property
    def source_stream(self) -> typing.Optional[_aws_cdk_aws_kinesis_0674c215.IStream]:
        '''(experimental) The Kinesis data stream to use as a source for this delivery stream.

        :default: - data must be written to the delivery stream via a direct put.

        :stability: experimental
        '''
        result = self._values.get("source_stream")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesis_0674c215.IStream], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeliveryStreamProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose.DestinationBindOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class DestinationBindOptions:
    def __init__(self) -> None:
        '''(experimental) Options when binding a destination to a delivery stream.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_kinesisfirehose as kinesisfirehose
            
            destination_bind_options = kinesisfirehose.DestinationBindOptions()
        '''
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DestinationBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose.DestinationConfig",
    jsii_struct_bases=[],
    name_mapping={
        "dependables": "dependables",
        "extended_s3_destination_configuration": "extendedS3DestinationConfiguration",
    },
)
class DestinationConfig:
    def __init__(
        self,
        *,
        dependables: typing.Optional[typing.Sequence[_aws_cdk_core_f4b25747.IDependable]] = None,
        extended_s3_destination_configuration: typing.Optional[typing.Union[CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) A Kinesis Data Firehose delivery stream destination configuration.

        :param dependables: (experimental) Any resources that were created by the destination when binding it to the stack that must be deployed before the delivery stream is deployed. Default: []
        :param extended_s3_destination_configuration: (experimental) S3 destination configuration properties. Default: - S3 destination is not used.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_kinesisfirehose as kinesisfirehose
            import aws_cdk.core as cdk
            
            # dependable: cdk.IDependable
            
            destination_config = kinesisfirehose.DestinationConfig(
                dependables=[dependable],
                extended_s3_destination_configuration=kinesisfirehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(
                    bucket_arn="bucketArn",
                    role_arn="roleArn",
            
                    # the properties below are optional
                    buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    compression_format="compressionFormat",
                    data_format_conversion_configuration=kinesisfirehose.CfnDeliveryStream.DataFormatConversionConfigurationProperty(
                        enabled=False,
                        input_format_configuration=kinesisfirehose.CfnDeliveryStream.InputFormatConfigurationProperty(
                            deserializer=kinesisfirehose.CfnDeliveryStream.DeserializerProperty(
                                hive_json_ser_de=kinesisfirehose.CfnDeliveryStream.HiveJsonSerDeProperty(
                                    timestamp_formats=["timestampFormats"]
                                ),
                                open_xJson_ser_de=kinesisfirehose.CfnDeliveryStream.OpenXJsonSerDeProperty(
                                    case_insensitive=False,
                                    column_to_json_key_mappings={
                                        "column_to_json_key_mappings_key": "columnToJsonKeyMappings"
                                    },
                                    convert_dots_in_json_keys_to_underscores=False
                                )
                            )
                        ),
                        output_format_configuration=kinesisfirehose.CfnDeliveryStream.OutputFormatConfigurationProperty(
                            serializer=kinesisfirehose.CfnDeliveryStream.SerializerProperty(
                                orc_ser_de=kinesisfirehose.CfnDeliveryStream.OrcSerDeProperty(
                                    block_size_bytes=123,
                                    bloom_filter_columns=["bloomFilterColumns"],
                                    bloom_filter_false_positive_probability=123,
                                    compression="compression",
                                    dictionary_key_threshold=123,
                                    enable_padding=False,
                                    format_version="formatVersion",
                                    padding_tolerance=123,
                                    row_index_stride=123,
                                    stripe_size_bytes=123
                                ),
                                parquet_ser_de=kinesisfirehose.CfnDeliveryStream.ParquetSerDeProperty(
                                    block_size_bytes=123,
                                    compression="compression",
                                    enable_dictionary_compression=False,
                                    max_padding_bytes=123,
                                    page_size_bytes=123,
                                    writer_version="writerVersion"
                                )
                            )
                        ),
                        schema_configuration=kinesisfirehose.CfnDeliveryStream.SchemaConfigurationProperty(
                            catalog_id="catalogId",
                            database_name="databaseName",
                            region="region",
                            role_arn="roleArn",
                            table_name="tableName",
                            version_id="versionId"
                        )
                    ),
                    dynamic_partitioning_configuration=kinesisfirehose.CfnDeliveryStream.DynamicPartitioningConfigurationProperty(
                        enabled=False,
                        retry_options=kinesisfirehose.CfnDeliveryStream.RetryOptionsProperty(
                            duration_in_seconds=123
                        )
                    ),
                    encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                        kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                            awskms_key_arn="awskmsKeyArn"
                        ),
                        no_encryption_config="noEncryptionConfig"
                    ),
                    error_output_prefix="errorOutputPrefix",
                    prefix="prefix",
                    processing_configuration=kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                        enabled=False,
                        processors=[kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                            type="type",
            
                            # the properties below are optional
                            parameters=[kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                parameter_name="parameterName",
                                parameter_value="parameterValue"
                            )]
                        )]
                    ),
                    s3_backup_configuration=kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
            
                        # the properties below are optional
                        buffering_hints=kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=kinesisfirehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                            kms_encryption_config=kinesisfirehose.CfnDeliveryStream.KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
                    s3_backup_mode="s3BackupMode"
                )
            )
        '''
        if isinstance(extended_s3_destination_configuration, dict):
            extended_s3_destination_configuration = CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(**extended_s3_destination_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__653b027613132ac0d51d8afbcef72a5247d605875d802e45a2c9d307b696ab72)
            check_type(argname="argument dependables", value=dependables, expected_type=type_hints["dependables"])
            check_type(argname="argument extended_s3_destination_configuration", value=extended_s3_destination_configuration, expected_type=type_hints["extended_s3_destination_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if dependables is not None:
            self._values["dependables"] = dependables
        if extended_s3_destination_configuration is not None:
            self._values["extended_s3_destination_configuration"] = extended_s3_destination_configuration

    @builtins.property
    def dependables(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_core_f4b25747.IDependable]]:
        '''(experimental) Any resources that were created by the destination when binding it to the stack that must be deployed before the delivery stream is deployed.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("dependables")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_core_f4b25747.IDependable]], result)

    @builtins.property
    def extended_s3_destination_configuration(
        self,
    ) -> typing.Optional[CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty]:
        '''(experimental) S3 destination configuration properties.

        :default: - S3 destination is not used.

        :stability: experimental
        '''
        result = self._values.get("extended_s3_destination_configuration")
        return typing.cast(typing.Optional[CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DestinationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-kinesisfirehose.IDataProcessor")
class IDataProcessor(typing_extensions.Protocol):
    '''(experimental) A data processor that Kinesis Data Firehose will call to transform records before delivering data.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> DataProcessorProps:
        '''(experimental) The constructor props of the DataProcessor.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.Construct,
        *,
        role: _aws_cdk_aws_iam_940a1ce0.IRole,
    ) -> DataProcessorConfig:
        '''(experimental) Binds this processor to a destination of a delivery stream.

        Implementers should use this method to grant processor invocation permissions to the provided stream and return the
        necessary configuration to register as a processor.

        :param scope: -
        :param role: (experimental) The IAM role assumed by Kinesis Data Firehose to write to the destination that this DataProcessor will bind to.

        :stability: experimental
        '''
        ...


class _IDataProcessorProxy:
    '''(experimental) A data processor that Kinesis Data Firehose will call to transform records before delivering data.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-kinesisfirehose.IDataProcessor"

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> DataProcessorProps:
        '''(experimental) The constructor props of the DataProcessor.

        :stability: experimental
        '''
        return typing.cast(DataProcessorProps, jsii.get(self, "props"))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _constructs_77d1e7e8.Construct,
        *,
        role: _aws_cdk_aws_iam_940a1ce0.IRole,
    ) -> DataProcessorConfig:
        '''(experimental) Binds this processor to a destination of a delivery stream.

        Implementers should use this method to grant processor invocation permissions to the provided stream and return the
        necessary configuration to register as a processor.

        :param scope: -
        :param role: (experimental) The IAM role assumed by Kinesis Data Firehose to write to the destination that this DataProcessor will bind to.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bd041f81d160855ef90388192ecda7755543fea68c640ac34ba218b7b0e9cd2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        options = DataProcessorBindOptions(role=role)

        return typing.cast(DataProcessorConfig, jsii.invoke(self, "bind", [scope, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDataProcessor).__jsii_proxy_class__ = lambda : _IDataProcessorProxy


@jsii.interface(jsii_type="@aws-cdk/aws-kinesisfirehose.IDeliveryStream")
class IDeliveryStream(
    _aws_cdk_core_f4b25747.IResource,
    _aws_cdk_aws_iam_940a1ce0.IGrantable,
    _aws_cdk_aws_ec2_67de8e8d.IConnectable,
    typing_extensions.Protocol,
):
    '''(experimental) Represents a Kinesis Data Firehose delivery stream.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="deliveryStreamArn")
    def delivery_stream_arn(self) -> builtins.str:
        '''(experimental) The ARN of the delivery stream.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> builtins.str:
        '''(experimental) The name of the delivery stream.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``actions``.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantPutRecords")
    def grant_put_records(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``firehose:PutRecord`` and ``firehose:PutRecordBatch`` actions on this delivery stream.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Return the given named metric for this delivery stream.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricBackupToS3Bytes")
    def metric_backup_to_s3_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Metric for the number of bytes delivered to Amazon S3 for backup over the specified time period.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricBackupToS3DataFreshness")
    def metric_backup_to_s3_data_freshness(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Metric for the age (from getting into Kinesis Data Firehose to now) of the oldest record in Kinesis Data Firehose.

        Any record older than this age has been delivered to the Amazon S3 bucket for backup.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricBackupToS3Records")
    def metric_backup_to_s3_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Metric for the number of records delivered to Amazon S3 for backup over the specified time period.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricIncomingBytes")
    def metric_incoming_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Metric for the number of bytes ingested successfully into the delivery stream over the specified time period after throttling.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricIncomingRecords")
    def metric_incoming_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Metric for the number of records ingested successfully into the delivery stream over the specified time period after throttling.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        ...


class _IDeliveryStreamProxy(
    jsii.proxy_for(_aws_cdk_core_f4b25747.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_iam_940a1ce0.IGrantable), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_ec2_67de8e8d.IConnectable), # type: ignore[misc]
):
    '''(experimental) Represents a Kinesis Data Firehose delivery stream.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-kinesisfirehose.IDeliveryStream"

    @builtins.property
    @jsii.member(jsii_name="deliveryStreamArn")
    def delivery_stream_arn(self) -> builtins.str:
        '''(experimental) The ARN of the delivery stream.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "deliveryStreamArn"))

    @builtins.property
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> builtins.str:
        '''(experimental) The name of the delivery stream.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "deliveryStreamName"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``actions``.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e15ed13078fe1a336d5a52075a4bd98e7c5aa857e4a45df7f919cc2137e7f04)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantPutRecords")
    def grant_put_records(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``firehose:PutRecord`` and ``firehose:PutRecordBatch`` actions on this delivery stream.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c2ed2467fe75d2072416e82499bc0f66a4681fea0f4a7833d77dc1c94192ddb)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantPutRecords", [grantee]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Return the given named metric for this delivery stream.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6897ac9c60f77b5216bd1559a7bb66b7b149231967ae7162772a9f3e6800f57e)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_9b88bb94.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricBackupToS3Bytes")
    def metric_backup_to_s3_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Metric for the number of bytes delivered to Amazon S3 for backup over the specified time period.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_9b88bb94.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricBackupToS3Bytes", [props]))

    @jsii.member(jsii_name="metricBackupToS3DataFreshness")
    def metric_backup_to_s3_data_freshness(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Metric for the age (from getting into Kinesis Data Firehose to now) of the oldest record in Kinesis Data Firehose.

        Any record older than this age has been delivered to the Amazon S3 bucket for backup.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_9b88bb94.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricBackupToS3DataFreshness", [props]))

    @jsii.member(jsii_name="metricBackupToS3Records")
    def metric_backup_to_s3_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Metric for the number of records delivered to Amazon S3 for backup over the specified time period.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_9b88bb94.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricBackupToS3Records", [props]))

    @jsii.member(jsii_name="metricIncomingBytes")
    def metric_incoming_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Metric for the number of bytes ingested successfully into the delivery stream over the specified time period after throttling.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_9b88bb94.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricIncomingBytes", [props]))

    @jsii.member(jsii_name="metricIncomingRecords")
    def metric_incoming_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Metric for the number of records ingested successfully into the delivery stream over the specified time period after throttling.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_9b88bb94.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricIncomingRecords", [props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDeliveryStream).__jsii_proxy_class__ = lambda : _IDeliveryStreamProxy


@jsii.interface(jsii_type="@aws-cdk/aws-kinesisfirehose.IDestination")
class IDestination(typing_extensions.Protocol):
    '''(experimental) A Kinesis Data Firehose delivery stream destination.

    :stability: experimental
    '''

    @jsii.member(jsii_name="bind")
    def bind(self, scope: _constructs_77d1e7e8.Construct) -> DestinationConfig:
        '''(experimental) Binds this destination to the Kinesis Data Firehose delivery stream.

        Implementers should use this method to bind resources to the stack and initialize values using the provided stream.

        :param scope: -

        :stability: experimental
        '''
        ...


class _IDestinationProxy:
    '''(experimental) A Kinesis Data Firehose delivery stream destination.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-kinesisfirehose.IDestination"

    @jsii.member(jsii_name="bind")
    def bind(self, scope: _constructs_77d1e7e8.Construct) -> DestinationConfig:
        '''(experimental) Binds this destination to the Kinesis Data Firehose delivery stream.

        Implementers should use this method to bind resources to the stack and initialize values using the provided stream.

        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__caefefd1b18f1a4144b31ca5be27836de6a913f0517de411738c8caca897ac2e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        options = DestinationBindOptions()

        return typing.cast(DestinationConfig, jsii.invoke(self, "bind", [scope, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDestination).__jsii_proxy_class__ = lambda : _IDestinationProxy


@jsii.implements(IDataProcessor)
class LambdaFunctionProcessor(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-kinesisfirehose.LambdaFunctionProcessor",
):
    '''(experimental) Use an AWS Lambda function to transform records.

    :stability: experimental
    :exampleMetadata: lit=../aws-kinesisfirehose-destinations/test/integ.s3-bucket.lit.ts infused

    Example::

        import path as path
        import aws_cdk.aws_kinesisfirehose as firehose
        import aws_cdk.aws_kms as kms
        import aws_cdk.aws_lambda_nodejs as lambdanodejs
        import aws_cdk.aws_logs as logs
        import aws_cdk.aws_s3 as s3
        import aws_cdk.core as cdk
        import aws_cdk.aws_kinesisfirehose_destinations as destinations
        
        app = cdk.App()
        
        stack = cdk.Stack(app, "aws-cdk-firehose-delivery-stream-s3-all-properties")
        
        bucket = s3.Bucket(stack, "Bucket",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        backup_bucket = s3.Bucket(stack, "BackupBucket",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        log_group = logs.LogGroup(stack, "LogGroup",
            removal_policy=cdk.RemovalPolicy.DESTROY
        )
        
        data_processor_function = lambdanodejs.NodejsFunction(stack, "DataProcessorFunction",
            entry=path.join(__dirname, "lambda-data-processor.js"),
            timeout=cdk.Duration.minutes(1)
        )
        
        processor = firehose.LambdaFunctionProcessor(data_processor_function,
            buffer_interval=cdk.Duration.seconds(60),
            buffer_size=cdk.Size.mebibytes(1),
            retries=1
        )
        
        key = kms.Key(stack, "Key",
            removal_policy=cdk.RemovalPolicy.DESTROY
        )
        
        backup_key = kms.Key(stack, "BackupKey",
            removal_policy=cdk.RemovalPolicy.DESTROY
        )
        
        firehose.DeliveryStream(stack, "Delivery Stream",
            destinations=[destinations.S3Bucket(bucket,
                logging=True,
                log_group=log_group,
                processor=processor,
                compression=destinations.Compression.GZIP,
                data_output_prefix="regularPrefix",
                error_output_prefix="errorPrefix",
                buffering_interval=cdk.Duration.seconds(60),
                buffering_size=cdk.Size.mebibytes(1),
                encryption_key=key,
                s3_backup=destinations.DestinationS3BackupProps(
                    mode=destinations.BackupMode.ALL,
                    bucket=backup_bucket,
                    compression=destinations.Compression.ZIP,
                    data_output_prefix="backupPrefix",
                    error_output_prefix="backupErrorPrefix",
                    buffering_interval=cdk.Duration.seconds(60),
                    buffering_size=cdk.Size.mebibytes(1),
                    encryption_key=backup_key
                )
            )]
        )
        
        app.synth()
    '''

    def __init__(
        self,
        lambda_function: _aws_cdk_aws_lambda_5443dbc3.IFunction,
        *,
        buffer_interval: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        buffer_size: typing.Optional[_aws_cdk_core_f4b25747.Size] = None,
        retries: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param lambda_function: -
        :param buffer_interval: (experimental) The length of time Kinesis Data Firehose will buffer incoming data before calling the processor. s Default: Duration.minutes(1)
        :param buffer_size: (experimental) The amount of incoming data Kinesis Data Firehose will buffer before calling the processor. Default: Size.mebibytes(3)
        :param retries: (experimental) The number of times Kinesis Data Firehose will retry the processor invocation after a failure due to network timeout or invocation limits. Default: 3

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa052d54be2857f86a75f126cc5ad2cadea9a41f2af703dc22597d3b3c5ba544)
            check_type(argname="argument lambda_function", value=lambda_function, expected_type=type_hints["lambda_function"])
        props = DataProcessorProps(
            buffer_interval=buffer_interval, buffer_size=buffer_size, retries=retries
        )

        jsii.create(self.__class__, self, [lambda_function, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _constructs_77d1e7e8.Construct,
        *,
        role: _aws_cdk_aws_iam_940a1ce0.IRole,
    ) -> DataProcessorConfig:
        '''(experimental) Binds this processor to a destination of a delivery stream.

        Implementers should use this method to grant processor invocation permissions to the provided stream and return the
        necessary configuration to register as a processor.

        :param _scope: -
        :param role: (experimental) The IAM role assumed by Kinesis Data Firehose to write to the destination that this DataProcessor will bind to.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__972a390eebecb4081c9cc5528145672b5558c56c2a0b40cd57aacec4ee79f78a)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        options = DataProcessorBindOptions(role=role)

        return typing.cast(DataProcessorConfig, jsii.invoke(self, "bind", [_scope, options]))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> DataProcessorProps:
        '''(experimental) The constructor props of the LambdaFunctionProcessor.

        :stability: experimental
        '''
        return typing.cast(DataProcessorProps, jsii.get(self, "props"))


@jsii.enum(jsii_type="@aws-cdk/aws-kinesisfirehose.StreamEncryption")
class StreamEncryption(enum.Enum):
    '''(experimental) Options for server-side encryption of a delivery stream.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # destination: firehose.IDestination
        # SSE with an customer-managed CMK that is explicitly specified
        # key: kms.Key
        
        
        # SSE with an AWS-owned CMK
        firehose.DeliveryStream(self, "Delivery Stream AWS Owned",
            encryption=firehose.StreamEncryption.AWS_OWNED,
            destinations=[destination]
        )
        # SSE with an customer-managed CMK that is created automatically by the CDK
        firehose.DeliveryStream(self, "Delivery Stream Implicit Customer Managed",
            encryption=firehose.StreamEncryption.CUSTOMER_MANAGED,
            destinations=[destination]
        )
        firehose.DeliveryStream(self, "Delivery Stream Explicit Customer Managed",
            encryption_key=key,
            destinations=[destination]
        )
    '''

    UNENCRYPTED = "UNENCRYPTED"
    '''(experimental) Data in the stream is stored unencrypted.

    :stability: experimental
    '''
    CUSTOMER_MANAGED = "CUSTOMER_MANAGED"
    '''(experimental) Data in the stream is stored encrypted by a KMS key managed by the customer.

    :stability: experimental
    '''
    AWS_OWNED = "AWS_OWNED"
    '''(experimental) Data in the stream is stored encrypted by a KMS key owned by AWS and managed for use in multiple AWS accounts.

    :stability: experimental
    '''


@jsii.implements(IDeliveryStream)
class DeliveryStream(
    _aws_cdk_core_f4b25747.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-kinesisfirehose.DeliveryStream",
):
    '''(experimental) Create a Kinesis Data Firehose delivery stream.

    :stability: experimental
    :resource: AWS::KinesisFirehose::DeliveryStream
    :exampleMetadata: infused

    Example::

        # bucket: s3.Bucket
        # Provide a Lambda function that will transform records before delivery, with custom
        # buffering and retry configuration
        lambda_function = lambda_.Function(self, "Processor",
            runtime=lambda_.Runtime.NODEJS_14_X,
            handler="index.handler",
            code=lambda_.Code.from_asset(path.join(__dirname, "process-records"))
        )
        lambda_processor = firehose.LambdaFunctionProcessor(lambda_function,
            buffer_interval=Duration.minutes(5),
            buffer_size=Size.mebibytes(5),
            retries=5
        )
        s3_destination = destinations.S3Bucket(bucket,
            processor=lambda_processor
        )
        firehose.DeliveryStream(self, "Delivery Stream",
            destinations=[s3_destination]
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        destinations: typing.Sequence[IDestination],
        delivery_stream_name: typing.Optional[builtins.str] = None,
        encryption: typing.Optional[StreamEncryption] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
        source_stream: typing.Optional[_aws_cdk_aws_kinesis_0674c215.IStream] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param destinations: (experimental) The destinations that this delivery stream will deliver data to. Only a singleton array is supported at this time.
        :param delivery_stream_name: (experimental) A name for the delivery stream. Default: - a name is generated by CloudFormation.
        :param encryption: (experimental) Indicates the type of customer master key (CMK) to use for server-side encryption, if any. Default: StreamEncryption.UNENCRYPTED - unless ``encryptionKey`` is provided, in which case this will be implicitly set to ``StreamEncryption.CUSTOMER_MANAGED``
        :param encryption_key: (experimental) Customer managed key to server-side encrypt data in the stream. Default: - no KMS key will be used; if ``encryption`` is set to ``CUSTOMER_MANAGED``, a KMS key will be created for you
        :param role: (experimental) The IAM role associated with this delivery stream. Assumed by Kinesis Data Firehose to read from sources and encrypt data server-side. Default: - a role will be created with default permissions.
        :param source_stream: (experimental) The Kinesis data stream to use as a source for this delivery stream. Default: - data must be written to the delivery stream via a direct put.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81840636ff21243f57c80a1d6f7b7b5382052cce9150f4eeba6b40264cd011c6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DeliveryStreamProps(
            destinations=destinations,
            delivery_stream_name=delivery_stream_name,
            encryption=encryption,
            encryption_key=encryption_key,
            role=role,
            source_stream=source_stream,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromDeliveryStreamArn")
    @builtins.classmethod
    def from_delivery_stream_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        delivery_stream_arn: builtins.str,
    ) -> IDeliveryStream:
        '''(experimental) Import an existing delivery stream from its ARN.

        :param scope: -
        :param id: -
        :param delivery_stream_arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fad5a2ac4dc240b8765afcef4c0fccaf92919e9adaaae9723ba09521790ac53)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument delivery_stream_arn", value=delivery_stream_arn, expected_type=type_hints["delivery_stream_arn"])
        return typing.cast(IDeliveryStream, jsii.sinvoke(cls, "fromDeliveryStreamArn", [scope, id, delivery_stream_arn]))

    @jsii.member(jsii_name="fromDeliveryStreamAttributes")
    @builtins.classmethod
    def from_delivery_stream_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        delivery_stream_arn: typing.Optional[builtins.str] = None,
        delivery_stream_name: typing.Optional[builtins.str] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    ) -> IDeliveryStream:
        '''(experimental) Import an existing delivery stream from its attributes.

        :param scope: -
        :param id: -
        :param delivery_stream_arn: (experimental) The ARN of the delivery stream. At least one of deliveryStreamArn and deliveryStreamName must be provided. Default: - derived from ``deliveryStreamName``.
        :param delivery_stream_name: (experimental) The name of the delivery stream. At least one of deliveryStreamName and deliveryStreamArn must be provided. Default: - derived from ``deliveryStreamArn``.
        :param role: (experimental) The IAM role associated with this delivery stream. Assumed by Kinesis Data Firehose to read from sources and encrypt data server-side. Default: - the imported stream cannot be granted access to other resources as an ``iam.IGrantable``.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26fb1e3b474a707c11c1a5fe005df4ee2bafc43804ce82745741ee64591a9498)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = DeliveryStreamAttributes(
            delivery_stream_arn=delivery_stream_arn,
            delivery_stream_name=delivery_stream_name,
            role=role,
        )

        return typing.cast(IDeliveryStream, jsii.sinvoke(cls, "fromDeliveryStreamAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="fromDeliveryStreamName")
    @builtins.classmethod
    def from_delivery_stream_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        delivery_stream_name: builtins.str,
    ) -> IDeliveryStream:
        '''(experimental) Import an existing delivery stream from its name.

        :param scope: -
        :param id: -
        :param delivery_stream_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11163b84c39b9be434d5324323302bae10134cc3abd5b13a6e03654223510624)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument delivery_stream_name", value=delivery_stream_name, expected_type=type_hints["delivery_stream_name"])
        return typing.cast(IDeliveryStream, jsii.sinvoke(cls, "fromDeliveryStreamName", [scope, id, delivery_stream_name]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``actions``.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b99f0b1c677f164021df650e2f47c89378a177178e9e24423b02aaffccc5167)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantPutRecords")
    def grant_put_records(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``firehose:PutRecord`` and ``firehose:PutRecordBatch`` actions on this delivery stream.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4a2a8d596a52e802d6d8de2750a985eb4b8df79968df1a4202e7bedecaf5152)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantPutRecords", [grantee]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Return the given named metric for this delivery stream.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__facc5db01d38c6caf95dbc9959d6e983a6d3590766bc3338cbabd2c37b663aa1)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_9b88bb94.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricBackupToS3Bytes")
    def metric_backup_to_s3_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Metric for the number of bytes delivered to Amazon S3 for backup over the specified time period.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_9b88bb94.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricBackupToS3Bytes", [props]))

    @jsii.member(jsii_name="metricBackupToS3DataFreshness")
    def metric_backup_to_s3_data_freshness(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Metric for the age (from getting into Kinesis Data Firehose to now) of the oldest record in Kinesis Data Firehose.

        Any record older than this age has been delivered to the Amazon S3 bucket for backup.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_9b88bb94.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricBackupToS3DataFreshness", [props]))

    @jsii.member(jsii_name="metricBackupToS3Records")
    def metric_backup_to_s3_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Metric for the number of records delivered to Amazon S3 for backup over the specified time period.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_9b88bb94.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricBackupToS3Records", [props]))

    @jsii.member(jsii_name="metricIncomingBytes")
    def metric_incoming_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Metric for the number of bytes ingested successfully into the delivery stream over the specified time period after throttling.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_9b88bb94.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricIncomingBytes", [props]))

    @jsii.member(jsii_name="metricIncomingRecords")
    def metric_incoming_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_9b88bb94.Metric:
        '''(experimental) Metric for the number of records ingested successfully into the delivery stream over the specified time period after throttling.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_9b88bb94.MetricOptions(
            account=account,
            color=color,
            dimensions=dimensions,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricIncomingRecords", [props]))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_67de8e8d.Connections:
        '''(experimental) Network connections between Kinesis Data Firehose and other resources, i.e. Redshift cluster.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_67de8e8d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="deliveryStreamArn")
    def delivery_stream_arn(self) -> builtins.str:
        '''(experimental) The ARN of the delivery stream.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "deliveryStreamArn"))

    @builtins.property
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> builtins.str:
        '''(experimental) The name of the delivery stream.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "deliveryStreamName"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_940a1ce0.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.IPrincipal, jsii.get(self, "grantPrincipal"))


__all__ = [
    "CfnDeliveryStream",
    "CfnDeliveryStreamProps",
    "DataProcessorBindOptions",
    "DataProcessorConfig",
    "DataProcessorIdentifier",
    "DataProcessorProps",
    "DeliveryStream",
    "DeliveryStreamAttributes",
    "DeliveryStreamProps",
    "DestinationBindOptions",
    "DestinationConfig",
    "IDataProcessor",
    "IDeliveryStream",
    "IDestination",
    "LambdaFunctionProcessor",
    "StreamEncryption",
]

publication.publish()

def _typecheckingstub__7f2187cf1658462c5e90fadcbc2c886b0e2eb15da7b6830258a92c4e7bc6c9cd(
    scope: _aws_cdk_core_f4b25747.Construct,
    id: builtins.str,
    *,
    amazon_open_search_serverless_destination_configuration: typing.Optional[typing.Union[typing.Union[CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]] = None,
    amazonopensearchservice_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    delivery_stream_encryption_configuration_input: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.DeliveryStreamEncryptionConfigurationInputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    delivery_stream_name: typing.Optional[builtins.str] = None,
    delivery_stream_type: typing.Optional[builtins.str] = None,
    elasticsearch_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    extended_s3_destination_configuration: typing.Optional[typing.Union[typing.Union[CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]] = None,
    http_endpoint_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    kinesis_stream_source_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.KinesisStreamSourceConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    redshift_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.RedshiftDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    s3_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.S3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    splunk_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.SplunkDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__282c33338d43e4451c857de390778cff23d9290b0da72cc0c8b05dcc958faa78(
    inspector: _aws_cdk_core_f4b25747.TreeInspector,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18aeb7fdc6b4d29db25a7b6de6bb11f72301b791bb4911491da0f7d46514fe14(
    props: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c86801ae154426393a7642134f4b7977aef011768f1b940a6908f3681972dfee(
    value: typing.Optional[typing.Union[CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty, _aws_cdk_core_f4b25747.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aadd4c1646bbf6fbae612f0d7d5986a7f194cbe3eb3b54465db6f4dae5aee215(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__512f499adc93e5ff99f5ecc6e0607d51d002deb7a9e624bb8862d27c3d82d36d(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.DeliveryStreamEncryptionConfigurationInputProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a86cc9ee22ead48b5c6a0f606dc7770db92d964761118370464e0e4253429e2c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cab54e5dae0eba2a6f80e6243d420cbfae0b019590fff25d1102b2932f4ed34d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9091a685c5780955cd975c89e7d8f1752333b9cb67fb425eb69d23b06aa4650b(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01e9be6255aaeb234aef44cbd19630c37c8553fc9e040d49e403d069d39e5378(
    value: typing.Optional[typing.Union[CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty, _aws_cdk_core_f4b25747.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e03b31573a12a040ea3ca2b8278eddfff1c8165b6f3cc7e2a717128fac66872(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1347cbf71c0f028bf61ae6e99295e21f7f03b46543f7a3bb6dda9e7ddce340a6(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.KinesisStreamSourceConfigurationProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__570fdb34d4a0a174da721cfa15838f8a19e32d5c7fe0dbab48eff7df88a0d832(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.RedshiftDestinationConfigurationProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e881ed7d8b9e0e3d4c0871f011670de6b2c8fc3871264ebd22894da1e4f10e0(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.S3DestinationConfigurationProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6b80da4a2ead1bbb6b84bf692e97c17c8bc4e15120edaed6416e28b07eb093e(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnDeliveryStream.SplunkDestinationConfigurationProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6318755922ed8fd8ca972992bc8ddb35826f97088ce3d5406f14b7470fc26596(
    *,
    interval_in_seconds: typing.Optional[jsii.Number] = None,
    size_in_m_bs: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__191d5f8f456326076b875e4ab295682afcc3800957839cc391ff21194affdbc3(
    *,
    index_name: builtins.str,
    role_arn: builtins.str,
    s3_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.S3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]],
    buffering_hints: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.AmazonOpenSearchServerlessBufferingHintsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    cloud_watch_logging_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.CloudWatchLoggingOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    collection_endpoint: typing.Optional[builtins.str] = None,
    processing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.ProcessingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    retry_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.AmazonOpenSearchServerlessRetryOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    s3_backup_mode: typing.Optional[builtins.str] = None,
    vpc_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.VpcConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be4eede9b5b29e156fdf4c2b916ba55616d3680e33a7ad306b1e5a9234523d91(
    *,
    duration_in_seconds: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f2b3c67b90885c6ef3156c108da39a36f93645866a62a34ccc191692d34a129(
    *,
    interval_in_seconds: typing.Optional[jsii.Number] = None,
    size_in_m_bs: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad314ac58d6049ce5236a0e8b5dc52c811c3978af58e70e435d9062aa86c415a(
    *,
    index_name: builtins.str,
    role_arn: builtins.str,
    s3_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.S3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]],
    buffering_hints: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.AmazonopensearchserviceBufferingHintsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    cloud_watch_logging_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.CloudWatchLoggingOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    cluster_endpoint: typing.Optional[builtins.str] = None,
    document_id_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.DocumentIdOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    domain_arn: typing.Optional[builtins.str] = None,
    index_rotation_period: typing.Optional[builtins.str] = None,
    processing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.ProcessingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    retry_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.AmazonopensearchserviceRetryOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    s3_backup_mode: typing.Optional[builtins.str] = None,
    type_name: typing.Optional[builtins.str] = None,
    vpc_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.VpcConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__230dd3485a7e2596998fc0170f5a7cfe8e1953f937ed1e2c9228ce7ef42e3b43(
    *,
    duration_in_seconds: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3eac0f9fad5da142f5ee5fd379e0a09ab57bd4bca2bb92205bf66efc858d7629(
    *,
    interval_in_seconds: typing.Optional[jsii.Number] = None,
    size_in_m_bs: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47b3cddd4a74f65c11eaaca2bb5076e207151acc94509338c126f3ad29e04b5c(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    log_group_name: typing.Optional[builtins.str] = None,
    log_stream_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8494ac7d53df40dbd76bfaf8c23ce596870c07736c6bdede0f1e9c311ec1aea(
    *,
    data_table_name: builtins.str,
    copy_options: typing.Optional[builtins.str] = None,
    data_table_columns: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18050cc8b274a82529d91064182ad7a96ce39fd20eea16d8355bea41ebd5ee30(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    input_format_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.InputFormatConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    output_format_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.OutputFormatConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    schema_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.SchemaConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa17125c6fdc739bce158647575c0a8d3b0aa54ceabe4bc9ec6ea52f44e7cfd4(
    *,
    key_type: builtins.str,
    key_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc601a7de36b01aab527f525b17ec0b11adbf4d1f9616e1eb3d75466c39cfb3f(
    *,
    hive_json_ser_de: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.HiveJsonSerDeProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    open_x_json_ser_de: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.OpenXJsonSerDeProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7089f940c747386ebd5931ebb7e25c49e14a6b154c607182c4c56984041f230(
    *,
    default_document_id_format: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81ac24502669ae2c4e24b378d84fe9466baeeaaa59bb08e9266706b5855a0546(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    retry_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.RetryOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__303c94776acc87657b62c87eef4858f83570ddbba0b57ad9e6465a88cce2d1a8(
    *,
    interval_in_seconds: typing.Optional[jsii.Number] = None,
    size_in_m_bs: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__187cfbaba4670b2ab9fe0c31707acb35032074e2a60cbf96e8bb6b67a4328d6d(
    *,
    index_name: builtins.str,
    role_arn: builtins.str,
    s3_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.S3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]],
    buffering_hints: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.ElasticsearchBufferingHintsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    cloud_watch_logging_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.CloudWatchLoggingOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    cluster_endpoint: typing.Optional[builtins.str] = None,
    document_id_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.DocumentIdOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    domain_arn: typing.Optional[builtins.str] = None,
    index_rotation_period: typing.Optional[builtins.str] = None,
    processing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.ProcessingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    retry_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.ElasticsearchRetryOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    s3_backup_mode: typing.Optional[builtins.str] = None,
    type_name: typing.Optional[builtins.str] = None,
    vpc_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.VpcConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d1aac060826908279ff8f9ac0ea30bbd9e78821b9442b69ebf81487fdd43e8e(
    *,
    duration_in_seconds: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a1bc04cb5074ea81a4788e9e8f3c3a8e64d6a437346e0089a65bc413df5f8ce(
    *,
    kms_encryption_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.KMSEncryptionConfigProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    no_encryption_config: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9e236c6cfc95ca860d610c22bbf1113f923621ee37e3c8f9370c87c038cd9fc(
    *,
    bucket_arn: builtins.str,
    role_arn: builtins.str,
    buffering_hints: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.BufferingHintsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    cloud_watch_logging_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.CloudWatchLoggingOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    compression_format: typing.Optional[builtins.str] = None,
    data_format_conversion_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.DataFormatConversionConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    dynamic_partitioning_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.DynamicPartitioningConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    encryption_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.EncryptionConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    error_output_prefix: typing.Optional[builtins.str] = None,
    prefix: typing.Optional[builtins.str] = None,
    processing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.ProcessingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    s3_backup_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.S3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    s3_backup_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb6d8ccd84cae002fb7f2ec5e8998185c5210eb594ac7f8a91a358d0a6646565(
    *,
    timestamp_formats: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a675429428249fe3aa5c328a4ec1d4b582e7c67b5bbbe376b8cc6a0429ebdb55(
    *,
    attribute_name: builtins.str,
    attribute_value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed3b58828f3f0c612428b99223fd34b0dc3548b65791514791fd8c424c49438f(
    *,
    url: builtins.str,
    access_key: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9da2769580ecd94e106f2765e1983fec915eeb9be0b44a009159785fd2e7533d(
    *,
    endpoint_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.HttpEndpointConfigurationProperty, typing.Dict[builtins.str, typing.Any]]],
    s3_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.S3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]],
    buffering_hints: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.BufferingHintsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    cloud_watch_logging_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.CloudWatchLoggingOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    processing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.ProcessingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    request_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.HttpEndpointRequestConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    retry_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.RetryOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    role_arn: typing.Optional[builtins.str] = None,
    s3_backup_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8bcf30a55195d84f5779f2205689a586d95041d755b927e402e42d7c05e5517(
    *,
    common_attributes: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.HttpEndpointCommonAttributeProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    content_encoding: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abf568cc06c48e619bb8dc5dd2bba9a52bd57785b7679099a09474b33ececfae(
    *,
    deserializer: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.DeserializerProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__806a0ffe3fcdb9b58fca1024de724f2c20b40277a7e069981163196045cb57d5(
    *,
    awskms_key_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b558e16c3ed7bafe3284085610adc8a5035c9b2f00873a7996ae2b34ed4eed64(
    *,
    kinesis_stream_arn: builtins.str,
    role_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3551efb35a233856fbede638ac90c11ed2820a5f93a0427d1c77390470a28b94(
    *,
    case_insensitive: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    column_to_json_key_mappings: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    convert_dots_in_json_keys_to_underscores: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08c892834827695bd4b65d6348cc7d06760ba7b2d3c7b1641fac41c6c484f039(
    *,
    block_size_bytes: typing.Optional[jsii.Number] = None,
    bloom_filter_columns: typing.Optional[typing.Sequence[builtins.str]] = None,
    bloom_filter_false_positive_probability: typing.Optional[jsii.Number] = None,
    compression: typing.Optional[builtins.str] = None,
    dictionary_key_threshold: typing.Optional[jsii.Number] = None,
    enable_padding: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    format_version: typing.Optional[builtins.str] = None,
    padding_tolerance: typing.Optional[jsii.Number] = None,
    row_index_stride: typing.Optional[jsii.Number] = None,
    stripe_size_bytes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82e7bd19f3542137c87726835a971526bafee10f70b07746eb0dbb527f00033d(
    *,
    serializer: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.SerializerProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__552a9736b420f2f67862d21044c477b62849204fb4bcf6f864b093129f25bf9f(
    *,
    block_size_bytes: typing.Optional[jsii.Number] = None,
    compression: typing.Optional[builtins.str] = None,
    enable_dictionary_compression: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    max_padding_bytes: typing.Optional[jsii.Number] = None,
    page_size_bytes: typing.Optional[jsii.Number] = None,
    writer_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d84d0741dab57ac754c89146652cdd4c4c129982af06fdb7d14d8ed08352fbef(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    processors: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.ProcessorProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c8b732be31b6e4628fa34d08f2376d9c6854b2be212583e866a51bdbdfc4402(
    *,
    parameter_name: builtins.str,
    parameter_value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7caf8713e44d471484486d33e703ae24cddc63555d3bcd7f1f2ed9a054663e1(
    *,
    type: builtins.str,
    parameters: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.ProcessorParameterProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05398f5801a7e6c32361f8637f10bf9deec3962bc82c4443d41ed9d07c3a16f3(
    *,
    cluster_jdbcurl: builtins.str,
    copy_command: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.CopyCommandProperty, typing.Dict[builtins.str, typing.Any]]],
    password: builtins.str,
    role_arn: builtins.str,
    s3_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.S3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]],
    username: builtins.str,
    cloud_watch_logging_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.CloudWatchLoggingOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    processing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.ProcessingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    retry_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.RedshiftRetryOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    s3_backup_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.S3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    s3_backup_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e823bc3f086f79db3696fea5dd9ce50270c45f10b499d901a11a31fe512c102f(
    *,
    duration_in_seconds: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be620df4c1a415bc8ccf4d71d31c7000e344f78ab27b480feec242b390b16d58(
    *,
    duration_in_seconds: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dc2094cec300f6dfe615a78ee1d7550b6c5b8eb4c40acd2a9cdb54351eb0e64(
    *,
    bucket_arn: builtins.str,
    role_arn: builtins.str,
    buffering_hints: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.BufferingHintsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    cloud_watch_logging_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.CloudWatchLoggingOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    compression_format: typing.Optional[builtins.str] = None,
    encryption_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.EncryptionConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    error_output_prefix: typing.Optional[builtins.str] = None,
    prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a14899683d146d767ed75ed1da35ea99fbf62704b76619410beb64dd48892959(
    *,
    catalog_id: typing.Optional[builtins.str] = None,
    database_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    role_arn: typing.Optional[builtins.str] = None,
    table_name: typing.Optional[builtins.str] = None,
    version_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1766376bdbee6d374c3bc231dab3f0cd0f7b7145a1f92e9dbc34c7643e0e48e1(
    *,
    orc_ser_de: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.OrcSerDeProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    parquet_ser_de: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.ParquetSerDeProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a58a257e3c4b0cfd57a396f205706890c84f6239b23ee5486563e297297b9186(
    *,
    hec_endpoint: builtins.str,
    hec_endpoint_type: builtins.str,
    hec_token: builtins.str,
    s3_configuration: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.S3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]],
    cloud_watch_logging_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.CloudWatchLoggingOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    hec_acknowledgment_timeout_in_seconds: typing.Optional[jsii.Number] = None,
    processing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.ProcessingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    retry_options: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.SplunkRetryOptionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    s3_backup_mode: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c88c4e28642aa8d9fbafce93e773a6ebb10c6dbf117e663e1975ac09ee7905d0(
    *,
    duration_in_seconds: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a21370b5b0c74765f64ec9a14f7ab5477c93d5817f1ee56a39e611363b6e54db(
    *,
    role_arn: builtins.str,
    security_group_ids: typing.Sequence[builtins.str],
    subnet_ids: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78fe85fc7f8702fa6acf4b2d6850582a03c47a40dfadab1895cacf75ace36a2f(
    *,
    amazon_open_search_serverless_destination_configuration: typing.Optional[typing.Union[typing.Union[CfnDeliveryStream.AmazonOpenSearchServerlessDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]] = None,
    amazonopensearchservice_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.AmazonopensearchserviceDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    delivery_stream_encryption_configuration_input: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.DeliveryStreamEncryptionConfigurationInputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    delivery_stream_name: typing.Optional[builtins.str] = None,
    delivery_stream_type: typing.Optional[builtins.str] = None,
    elasticsearch_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.ElasticsearchDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    extended_s3_destination_configuration: typing.Optional[typing.Union[typing.Union[CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]] = None,
    http_endpoint_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.HttpEndpointDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    kinesis_stream_source_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.KinesisStreamSourceConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    redshift_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.RedshiftDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    s3_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.S3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    splunk_destination_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnDeliveryStream.SplunkDestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5991b79bb62866419e3049c10f52358c8b79ec8798f1d765a2243221da18418(
    *,
    role: _aws_cdk_aws_iam_940a1ce0.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3f2f0047367717fb36fb6a891f032cf51e0748e53fc66f3675d36abf3390219(
    *,
    processor_identifier: typing.Union[DataProcessorIdentifier, typing.Dict[builtins.str, typing.Any]],
    processor_type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c62b61e71ca36a86b485c108e45a2befa13ca0ff42e8cbfa745f4c40ffefc2a5(
    *,
    parameter_name: builtins.str,
    parameter_value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__326d7b3a20befe27b15d80e056ca11ec0f092bc0263109a4f7ae33e511facdf5(
    *,
    buffer_interval: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    buffer_size: typing.Optional[_aws_cdk_core_f4b25747.Size] = None,
    retries: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a3f59a2d368279099b3af6994cb0e2ba7543329d2e0ca9428227c573d63b55d(
    *,
    delivery_stream_arn: typing.Optional[builtins.str] = None,
    delivery_stream_name: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29c9d9445e0c324d1f43d9979f2ce42695925446cdcbb7270e0efd30c8041f52(
    *,
    destinations: typing.Sequence[IDestination],
    delivery_stream_name: typing.Optional[builtins.str] = None,
    encryption: typing.Optional[StreamEncryption] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    source_stream: typing.Optional[_aws_cdk_aws_kinesis_0674c215.IStream] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__653b027613132ac0d51d8afbcef72a5247d605875d802e45a2c9d307b696ab72(
    *,
    dependables: typing.Optional[typing.Sequence[_aws_cdk_core_f4b25747.IDependable]] = None,
    extended_s3_destination_configuration: typing.Optional[typing.Union[CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bd041f81d160855ef90388192ecda7755543fea68c640ac34ba218b7b0e9cd2(
    scope: _constructs_77d1e7e8.Construct,
    *,
    role: _aws_cdk_aws_iam_940a1ce0.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e15ed13078fe1a336d5a52075a4bd98e7c5aa857e4a45df7f919cc2137e7f04(
    grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c2ed2467fe75d2072416e82499bc0f66a4681fea0f4a7833d77dc1c94192ddb(
    grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6897ac9c60f77b5216bd1559a7bb66b7b149231967ae7162772a9f3e6800f57e(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caefefd1b18f1a4144b31ca5be27836de6a913f0517de411738c8caca897ac2e(
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa052d54be2857f86a75f126cc5ad2cadea9a41f2af703dc22597d3b3c5ba544(
    lambda_function: _aws_cdk_aws_lambda_5443dbc3.IFunction,
    *,
    buffer_interval: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    buffer_size: typing.Optional[_aws_cdk_core_f4b25747.Size] = None,
    retries: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__972a390eebecb4081c9cc5528145672b5558c56c2a0b40cd57aacec4ee79f78a(
    _scope: _constructs_77d1e7e8.Construct,
    *,
    role: _aws_cdk_aws_iam_940a1ce0.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81840636ff21243f57c80a1d6f7b7b5382052cce9150f4eeba6b40264cd011c6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    destinations: typing.Sequence[IDestination],
    delivery_stream_name: typing.Optional[builtins.str] = None,
    encryption: typing.Optional[StreamEncryption] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    source_stream: typing.Optional[_aws_cdk_aws_kinesis_0674c215.IStream] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fad5a2ac4dc240b8765afcef4c0fccaf92919e9adaaae9723ba09521790ac53(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    delivery_stream_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26fb1e3b474a707c11c1a5fe005df4ee2bafc43804ce82745741ee64591a9498(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    delivery_stream_arn: typing.Optional[builtins.str] = None,
    delivery_stream_name: typing.Optional[builtins.str] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11163b84c39b9be434d5324323302bae10134cc3abd5b13a6e03654223510624(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    delivery_stream_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b99f0b1c677f164021df650e2f47c89378a177178e9e24423b02aaffccc5167(
    grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4a2a8d596a52e802d6d8de2750a985eb4b8df79968df1a4202e7bedecaf5152(
    grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__facc5db01d38c6caf95dbc9959d6e983a6d3590766bc3338cbabd2c37b663aa1(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_9b88bb94.Unit] = None,
) -> None:
    """Type checking stubs"""
    pass
