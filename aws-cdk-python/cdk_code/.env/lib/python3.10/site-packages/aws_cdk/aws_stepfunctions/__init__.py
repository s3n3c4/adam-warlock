'''
# AWS Step Functions Construct Library

<!--BEGIN STABILITY BANNER-->---


![cfn-resources: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

The `@aws-cdk/aws-stepfunctions` package contains constructs for building
serverless workflows using objects. Use this in conjunction with the
`@aws-cdk/aws-stepfunctions-tasks` package, which contains classes used
to call other AWS services.

Defining a workflow looks like this (for the [Step Functions Job Poller
example](https://docs.aws.amazon.com/step-functions/latest/dg/job-status-poller-sample.html)):

## Example

```python
import aws_cdk.aws_lambda as lambda_

# submit_lambda: lambda.Function
# get_status_lambda: lambda.Function


submit_job = tasks.LambdaInvoke(self, "Submit Job",
    lambda_function=submit_lambda,
    # Lambda's result is in the attribute `Payload`
    output_path="$.Payload"
)

wait_x = sfn.Wait(self, "Wait X Seconds",
    time=sfn.WaitTime.seconds_path("$.waitSeconds")
)

get_status = tasks.LambdaInvoke(self, "Get Job Status",
    lambda_function=get_status_lambda,
    # Pass just the field named "guid" into the Lambda, put the
    # Lambda's result in a field called "status" in the response
    input_path="$.guid",
    output_path="$.Payload"
)

job_failed = sfn.Fail(self, "Job Failed",
    cause="AWS Batch Job Failed",
    error="DescribeJob returned FAILED"
)

final_status = tasks.LambdaInvoke(self, "Get Final Job Status",
    lambda_function=get_status_lambda,
    # Use "guid" field as input
    input_path="$.guid",
    output_path="$.Payload"
)

definition = submit_job.next(wait_x).next(get_status).next(sfn.Choice(self, "Job Complete?").when(sfn.Condition.string_equals("$.status", "FAILED"), job_failed).when(sfn.Condition.string_equals("$.status", "SUCCEEDED"), final_status).otherwise(wait_x))

sfn.StateMachine(self, "StateMachine",
    definition=definition,
    timeout=Duration.minutes(5)
)
```

You can find more sample snippets and learn more about the service integrations
in the `@aws-cdk/aws-stepfunctions-tasks` package.

## State Machine

A `stepfunctions.StateMachine` is a resource that takes a state machine
definition. The definition is specified by its start state, and encompasses
all states reachable from the start state:

```python
start_state = sfn.Pass(self, "StartState")

sfn.StateMachine(self, "StateMachine",
    definition=start_state
)
```

State machines execute using an IAM Role, which will automatically have all
permissions added that are required to make all state machine tasks execute
properly (for example, permissions to invoke any Lambda functions you add to
your workflow). A role will be created by default, but you can supply an
existing one as well.

## Accessing State (the JsonPath class)

Every State Machine execution has [State Machine
Data](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-state-machine-data.html):
a JSON document containing keys and values that is fed into the state machine,
gets modified as the state machine progresses, and finally is produced as output.

You can pass fragments of this State Machine Data into Tasks of the state machine.
To do so, use the static methods on the `JsonPath` class. For example, to pass
the value that's in the data key of `OrderId` to a Lambda function as you invoke
it, use `JsonPath.stringAt('$.OrderId')`, like so:

```python
import aws_cdk.aws_lambda as lambda_

# order_fn: lambda.Function


submit_job = tasks.LambdaInvoke(self, "InvokeOrderProcessor",
    lambda_function=order_fn,
    payload=sfn.TaskInput.from_object({
        "OrderId": sfn.JsonPath.string_at("$.OrderId")
    })
)
```

The following methods are available:

| Method | Purpose |
|--------|---------|
| `JsonPath.stringAt('$.Field')` | reference a field, return the type as a `string`. |
| `JsonPath.listAt('$.Field')` | reference a field, return the type as a list of strings. |
| `JsonPath.numberAt('$.Field')` | reference a field, return the type as a number. Use this for functions that expect a number argument. |
| `JsonPath.objectAt('$.Field')` | reference a field, return the type as an `IResolvable`. Use this for functions that expect an object argument. |
| `JsonPath.entirePayload` | reference the entire data object (equivalent to a path of `$`). |
| `JsonPath.taskToken` | reference the [Task Token](https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html#connect-wait-token), used for integration patterns that need to run for a long time. |

You can also call [intrinsic functions](https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-intrinsic-functions.html) using the methods on `JsonPath`:

| Method | Purpose |
|--------|---------|
| `JsonPath.array(JsonPath.stringAt('$.Field'), ...)` | make an array from other elements. |
| `JsonPath.format('The value is {}.', JsonPath.stringAt('$.Value'))` | insert elements into a format string. |
| `JsonPath.stringToJson(JsonPath.stringAt('$.ObjStr'))` | parse a JSON string to an object |
| `JsonPath.jsonToString(JsonPath.objectAt('$.Obj'))` | stringify an object to a JSON string |

## Amazon States Language

This library comes with a set of classes that model the [Amazon States
Language](https://states-language.net/spec.html). The following State classes
are supported:

* [`Task`](#task)
* [`Pass`](#pass)
* [`Wait`](#wait)
* [`Choice`](#choice)
* [`Parallel`](#parallel)
* [`Succeed`](#succeed)
* [`Fail`](#fail)
* [`Map`](#map)
* [`Custom State`](#custom-state)

An arbitrary JSON object (specified at execution start) is passed from state to
state and transformed during the execution of the workflow. For more
information, see the States Language spec.

### Task

A `Task` represents some work that needs to be done. The exact work to be
done is determine by a class that implements `IStepFunctionsTask`, a collection
of which can be found in the `@aws-cdk/aws-stepfunctions-tasks` module.

The tasks in the `@aws-cdk/aws-stepfunctions-tasks` module support the
[service integration pattern](https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html) that integrates Step Functions with services
directly in the Amazon States language.

### Pass

A `Pass` state passes its input to its output, without performing work.
Pass states are useful when constructing and debugging state machines.

The following example injects some fixed data into the state machine through
the `result` field. The `result` field will be added to the input and the result
will be passed as the state's output.

```python
# Makes the current JSON state { ..., "subObject": { "hello": "world" } }
pass = sfn.Pass(self, "Add Hello World",
    result=sfn.Result.from_object({"hello": "world"}),
    result_path="$.subObject"
)

# Set the next state
next_state = sfn.Pass(self, "NextState")
pass.next(next_state)
```

The `Pass` state also supports passing key-value pairs as input. Values can
be static, or selected from the input with a path.

The following example filters the `greeting` field from the state input
and also injects a field called `otherData`.

```python
pass = sfn.Pass(self, "Filter input and inject data",
    parameters={ # input to the pass state
        "input": sfn.JsonPath.string_at("$.input.greeting"),
        "other_data": "some-extra-stuff"}
)
```

The object specified in `parameters` will be the input of the `Pass` state.
Since neither `Result` nor `ResultPath` are supplied, the `Pass` state copies
its input through to its output.

Learn more about the [Pass state](https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-pass-state.html)

### Wait

A `Wait` state waits for a given number of seconds, or until the current time
hits a particular time. The time to wait may be taken from the execution's JSON
state.

```python
# Wait until it's the time mentioned in the the state object's "triggerTime"
# field.
wait = sfn.Wait(self, "Wait For Trigger Time",
    time=sfn.WaitTime.timestamp_path("$.triggerTime")
)

# Set the next state
start_the_work = sfn.Pass(self, "StartTheWork")
wait.next(start_the_work)
```

### Choice

A `Choice` state can take a different path through the workflow based on the
values in the execution's JSON state:

```python
choice = sfn.Choice(self, "Did it work?")

# Add conditions with .when()
success_state = sfn.Pass(self, "SuccessState")
failure_state = sfn.Pass(self, "FailureState")
choice.when(sfn.Condition.string_equals("$.status", "SUCCESS"), success_state)
choice.when(sfn.Condition.number_greater_than("$.attempts", 5), failure_state)

# Use .otherwise() to indicate what should be done if none of the conditions match
try_again_state = sfn.Pass(self, "TryAgainState")
choice.otherwise(try_again_state)
```

If you want to temporarily branch your workflow based on a condition, but have
all branches come together and continuing as one (similar to how an `if ... then ... else` works in a programming language), use the `.afterwards()` method:

```python
choice = sfn.Choice(self, "What color is it?")
handle_blue_item = sfn.Pass(self, "HandleBlueItem")
handle_red_item = sfn.Pass(self, "HandleRedItem")
handle_other_item_color = sfn.Pass(self, "HanldeOtherItemColor")
choice.when(sfn.Condition.string_equals("$.color", "BLUE"), handle_blue_item)
choice.when(sfn.Condition.string_equals("$.color", "RED"), handle_red_item)
choice.otherwise(handle_other_item_color)

# Use .afterwards() to join all possible paths back together and continue
ship_the_item = sfn.Pass(self, "ShipTheItem")
choice.afterwards().next(ship_the_item)
```

If your `Choice` doesn't have an `otherwise()` and none of the conditions match
the JSON state, a `NoChoiceMatched` error will be thrown. Wrap the state machine
in a `Parallel` state if you want to catch and recover from this.

#### Available Conditions

see [step function comparison operators](https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-choice-state.html#amazon-states-language-choice-state-rules)

* `Condition.isPresent` - matches if a json path is present
* `Condition.isNotPresent` - matches if a json path is not present
* `Condition.isString` - matches if a json path contains a string
* `Condition.isNotString` - matches if a json path is not a string
* `Condition.isNumeric` - matches if a json path is numeric
* `Condition.isNotNumeric` - matches if a json path is not numeric
* `Condition.isBoolean` - matches if a json path is boolean
* `Condition.isNotBoolean` - matches if a json path is not boolean
* `Condition.isTimestamp` - matches if a json path is a timestamp
* `Condition.isNotTimestamp` - matches if a json path is not a timestamp
* `Condition.isNotNull` - matches if a json path is not null
* `Condition.isNull` - matches if a json path is null
* `Condition.booleanEquals` - matches if a boolean field has a given value
* `Condition.booleanEqualsJsonPath` - matches if a boolean field equals a value in a given mapping path
* `Condition.stringEqualsJsonPath` - matches if a string field equals a given mapping path
* `Condition.stringEquals` - matches if a field equals a string value
* `Condition.stringLessThan` - matches if a string field sorts before a given value
* `Condition.stringLessThanJsonPath` - matches if a string field sorts before a value at given mapping path
* `Condition.stringLessThanEquals` - matches if a string field sorts equal to or before a given value
* `Condition.stringLessThanEqualsJsonPath` - matches if a string field sorts equal to or before a given mapping
* `Condition.stringGreaterThan` - matches if a string field sorts after a given value
* `Condition.stringGreaterThanJsonPath` - matches if a string field sorts after a value at a given mapping path
* `Condition.stringGreaterThanEqualsJsonPath` - matches if a string field sorts after or equal to value at a given mapping path
* `Condition.stringGreaterThanEquals` - matches if a string field sorts after or equal to a given value
* `Condition.numberEquals` - matches if a numeric field has the given value
* `Condition.numberEqualsJsonPath` - matches if a numeric field has the value in a given mapping path
* `Condition.numberLessThan` - matches if a numeric field is less than the given value
* `Condition.numberLessThanJsonPath` - matches if a numeric field is less than the value at the given mapping path
* `Condition.numberLessThanEquals` - matches if a numeric field is less than or equal to the given value
* `Condition.numberLessThanEqualsJsonPath` - matches if a numeric field is less than or equal to the numeric value at given mapping path
* `Condition.numberGreaterThan` - matches if a numeric field is greater than the given value
* `Condition.numberGreaterThanJsonPath` - matches if a numeric field is greater than the value at a given mapping path
* `Condition.numberGreaterThanEquals` - matches if a numeric field is greater than or equal to the given value
* `Condition.numberGreaterThanEqualsJsonPath` - matches if a numeric field is greater than or equal to the value at a given mapping path
* `Condition.timestampEquals` - matches if a timestamp field is the same time as the given timestamp
* `Condition.timestampEqualsJsonPath` - matches if a timestamp field is the same time as the timestamp at a given mapping path
* `Condition.timestampLessThan` - matches if a timestamp field is before the given timestamp
* `Condition.timestampLessThanJsonPath` - matches if a timestamp field is before the timestamp at a given mapping path
* `Condition.timestampLessThanEquals` - matches if a timestamp field is before or equal to the given timestamp
* `Condition.timestampLessThanEqualsJsonPath` - matches if a timestamp field is before or equal to the timestamp at a given mapping path
* `Condition.timestampGreaterThan` - matches if a timestamp field is after the timestamp at a given mapping path
* `Condition.timestampGreaterThanJsonPath` - matches if a timestamp field is after the timestamp at a given mapping path
* `Condition.timestampGreaterThanEquals` - matches if a timestamp field is after or equal to the given timestamp
* `Condition.timestampGreaterThanEqualsJsonPath` - matches if a timestamp field is after or equal to the timestamp at a given mapping path
* `Condition.stringMatches` - matches if a field matches a string pattern that can contain a wild card (*) e.g: log-*.txt or *LATEST*. No other characters other than "*" have any special meaning - * can be escaped: \\*

### Parallel

A `Parallel` state executes one or more subworkflows in parallel. It can also
be used to catch and recover from errors in subworkflows.

```python
parallel = sfn.Parallel(self, "Do the work in parallel")

# Add branches to be executed in parallel
ship_item = sfn.Pass(self, "ShipItem")
send_invoice = sfn.Pass(self, "SendInvoice")
restock = sfn.Pass(self, "Restock")
parallel.branch(ship_item)
parallel.branch(send_invoice)
parallel.branch(restock)

# Retry the whole workflow if something goes wrong
parallel.add_retry(max_attempts=1)

# How to recover from errors
send_failure_notification = sfn.Pass(self, "SendFailureNotification")
parallel.add_catch(send_failure_notification)

# What to do in case everything succeeded
close_order = sfn.Pass(self, "CloseOrder")
parallel.next(close_order)
```

### Succeed

Reaching a `Succeed` state terminates the state machine execution with a
successful status.

```python
success = sfn.Succeed(self, "We did it!")
```

### Fail

Reaching a `Fail` state terminates the state machine execution with a
failure status. The fail state should report the reason for the failure.
Failures can be caught by encompassing `Parallel` states.

```python
success = sfn.Fail(self, "Fail",
    error="WorkflowFailure",
    cause="Something went wrong"
)
```

### Map

A `Map` state can be used to run a set of steps for each element of an input array.
A `Map` state will execute the same steps for multiple entries of an array in the state input.

While the `Parallel` state executes multiple branches of steps using the same input, a `Map` state will
execute the same steps for multiple entries of an array in the state input.

```python
map = sfn.Map(self, "Map State",
    max_concurrency=1,
    items_path=sfn.JsonPath.string_at("$.inputForMap")
)
map.iterator(sfn.Pass(self, "Pass State"))
```

### Custom State

It's possible that the high-level constructs for the states or `stepfunctions-tasks` do not have
the states or service integrations you are looking for. The primary reasons for this lack of
functionality are:

* A [service integration](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-service-integrations.html) is available through Amazon States Langauge, but not available as construct
  classes in the CDK.
* The state or state properties are available through Step Functions, but are not configurable
  through constructs

If a feature is not available, a `CustomState` can be used to supply any Amazon States Language
JSON-based object as the state definition.

[Code Snippets](https://docs.aws.amazon.com/step-functions/latest/dg/tutorial-code-snippet.html#tutorial-code-snippet-1) are available and can be plugged in as the state definition.

Custom states can be chained together with any of the other states to create your state machine
definition. You will also need to provide any permissions that are required to the `role` that
the State Machine uses.

The following example uses the `DynamoDB` service integration to insert data into a DynamoDB table.

```python
import aws_cdk.aws_dynamodb as dynamodb


# create a table
table = dynamodb.Table(self, "montable",
    partition_key=dynamodb.Attribute(
        name="id",
        type=dynamodb.AttributeType.STRING
    )
)

final_status = sfn.Pass(self, "final step")

# States language JSON to put an item into DynamoDB
# snippet generated from https://docs.aws.amazon.com/step-functions/latest/dg/tutorial-code-snippet.html#tutorial-code-snippet-1
state_json = {
    "Type": "Task",
    "Resource": "arn:aws:states:::dynamodb:putItem",
    "Parameters": {
        "TableName": table.table_name,
        "Item": {
            "id": {
                "S": "MyEntry"
            }
        }
    },
    "ResultPath": null
}

# custom state which represents a task to insert data into DynamoDB
custom = sfn.CustomState(self, "my custom task",
    state_json=state_json
)

chain = sfn.Chain.start(custom).next(final_status)

sm = sfn.StateMachine(self, "StateMachine",
    definition=chain,
    timeout=Duration.seconds(30)
)

# don't forget permissions. You need to assign them
table.grant_write_data(sm)
```

## Task Chaining

To make defining work flows as convenient (and readable in a top-to-bottom way)
as writing regular programs, it is possible to chain most methods invocations.
In particular, the `.next()` method can be repeated. The result of a series of
`.next()` calls is called a **Chain**, and can be used when defining the jump
targets of `Choice.on` or `Parallel.branch`:

```python
step1 = sfn.Pass(self, "Step1")
step2 = sfn.Pass(self, "Step2")
step3 = sfn.Pass(self, "Step3")
step4 = sfn.Pass(self, "Step4")
step5 = sfn.Pass(self, "Step5")
step6 = sfn.Pass(self, "Step6")
step7 = sfn.Pass(self, "Step7")
step8 = sfn.Pass(self, "Step8")
step9 = sfn.Pass(self, "Step9")
step10 = sfn.Pass(self, "Step10")
choice = sfn.Choice(self, "Choice")
condition1 = sfn.Condition.string_equals("$.status", "SUCCESS")
parallel = sfn.Parallel(self, "Parallel")
finish = sfn.Pass(self, "Finish")

definition = step1.next(step2).next(choice.when(condition1, step3.next(step4).next(step5)).otherwise(step6).afterwards()).next(parallel.branch(step7.next(step8)).branch(step9.next(step10))).next(finish)

sfn.StateMachine(self, "StateMachine",
    definition=definition
)
```

If you don't like the visual look of starting a chain directly off the first
step, you can use `Chain.start`:

```python
step1 = sfn.Pass(self, "Step1")
step2 = sfn.Pass(self, "Step2")
step3 = sfn.Pass(self, "Step3")

definition = sfn.Chain.start(step1).next(step2).next(step3)
```

## State Machine Fragments

It is possible to define reusable (or abstracted) mini-state machines by
defining a construct that implements `IChainable`, which requires you to define
two fields:

* `startState: State`, representing the entry point into this state machine.
* `endStates: INextable[]`, representing the (one or more) states that outgoing
  transitions will be added to if you chain onto the fragment.

Since states will be named after their construct IDs, you may need to prefix the
IDs of states if you plan to instantiate the same state machine fragment
multiples times (otherwise all states in every instantiation would have the same
name).

The class `StateMachineFragment` contains some helper functions (like
`prefixStates()`) to make it easier for you to do this. If you define your state
machine as a subclass of this, it will be convenient to use:

```python
from aws_cdk.core import Stack
from constructs import Construct
import aws_cdk.aws_stepfunctions as sfn

class MyJob(sfn.StateMachineFragment):

    def __init__(self, parent, id, *, jobFlavor):
        super().__init__(parent, id)

        choice = sfn.Choice(self, "Choice").when(sfn.Condition.string_equals("$.branch", "left"), sfn.Pass(self, "Left Branch")).when(sfn.Condition.string_equals("$.branch", "right"), sfn.Pass(self, "Right Branch"))

        # ...

        self.start_state = choice
        self.end_states = choice.afterwards().end_states

class MyStack(Stack):
    def __init__(self, scope, id):
        super().__init__(scope, id)
        # Do 3 different variants of MyJob in parallel
        parallel = sfn.Parallel(self, "All jobs").branch(MyJob(self, "Quick", job_flavor="quick").prefix_states()).branch(MyJob(self, "Medium", job_flavor="medium").prefix_states()).branch(MyJob(self, "Slow", job_flavor="slow").prefix_states())

        sfn.StateMachine(self, "MyStateMachine",
            definition=parallel
        )
```

A few utility functions are available to parse state machine fragments.

* `State.findReachableStates`: Retrieve the list of states reachable from a given state.
* `State.findReachableEndStates`: Retrieve the list of end or terminal states reachable from a given state.

## Activity

**Activities** represent work that is done on some non-Lambda worker pool. The
Step Functions workflow will submit work to this Activity, and a worker pool
that you run yourself, probably on EC2, will pull jobs from the Activity and
submit the results of individual jobs back.

You need the ARN to do so, so if you use Activities be sure to pass the Activity
ARN into your worker pool:

```python
activity = sfn.Activity(self, "Activity")

# Read this CloudFormation Output from your application and use it to poll for work on
# the activity.
CfnOutput(self, "ActivityArn", value=activity.activity_arn)
```

### Activity-Level Permissions

Granting IAM permissions to an activity can be achieved by calling the `grant(principal, actions)` API:

```python
activity = sfn.Activity(self, "Activity")

role = iam.Role(self, "Role",
    assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
)

activity.grant(role, "states:SendTaskSuccess")
```

This will grant the IAM principal the specified actions onto the activity.

## Metrics

`Task` object expose various metrics on the execution of that particular task. For example,
to create an alarm on a particular task failing:

```python
# task: sfn.Task

cloudwatch.Alarm(self, "TaskAlarm",
    metric=task.metric_failed(),
    threshold=1,
    evaluation_periods=1
)
```

There are also metrics on the complete state machine:

```python
# state_machine: sfn.StateMachine

cloudwatch.Alarm(self, "StateMachineAlarm",
    metric=state_machine.metric_failed(),
    threshold=1,
    evaluation_periods=1
)
```

And there are metrics on the capacity of all state machines in your account:

```python
cloudwatch.Alarm(self, "ThrottledAlarm",
    metric=sfn.StateTransitionMetric.metric_throttled_events(),
    threshold=10,
    evaluation_periods=2
)
```

## Error names

Step Functions identifies errors in the Amazon States Language using case-sensitive strings, known as error names.
The Amazon States Language defines a set of built-in strings that name well-known errors, all beginning with the `States.` prefix.

* `States.ALL` - A wildcard that matches any known error name.
* `States.Runtime` - An execution failed due to some exception that could not be processed. Often these are caused by errors at runtime, such as attempting to apply InputPath or OutputPath on a null JSON payload. A `States.Runtime` error is not retriable, and will always cause the execution to fail. A retry or catch on `States.ALL` will NOT catch States.Runtime errors.
* `States.DataLimitExceeded` - A States.DataLimitExceeded exception will be thrown for the following:

  * When the output of a connector is larger than payload size quota.
  * When the output of a state is larger than payload size quota.
  * When, after Parameters processing, the input of a state is larger than the payload size quota.
  * See [the AWS documentation](https://docs.aws.amazon.com/step-functions/latest/dg/limits-overview.html) to learn more about AWS Step Functions Quotas.
* `States.HeartbeatTimeout` - A Task state failed to send a heartbeat for a period longer than the HeartbeatSeconds value.
* `States.Timeout` - A Task state either ran longer than the TimeoutSeconds value, or failed to send a heartbeat for a period longer than the HeartbeatSeconds value.
* `States.TaskFailed`- A Task state failed during the execution. When used in a retry or catch, `States.TaskFailed` acts as a wildcard that matches any known error name except for `States.Timeout`.

## Logging

Enable logging to CloudWatch by passing a logging configuration with a
destination LogGroup:

```python
import aws_cdk.aws_logs as logs


log_group = logs.LogGroup(self, "MyLogGroup")

sfn.StateMachine(self, "MyStateMachine",
    definition=sfn.Chain.start(sfn.Pass(self, "Pass")),
    logs=sfn.LogOptions(
        destination=log_group,
        level=sfn.LogLevel.ALL
    )
)
```

## X-Ray tracing

Enable X-Ray tracing for StateMachine:

```python
sfn.StateMachine(self, "MyStateMachine",
    definition=sfn.Chain.start(sfn.Pass(self, "Pass")),
    tracing_enabled=True
)
```

See [the AWS documentation](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-xray-tracing.html)
to learn more about AWS Step Functions's X-Ray support.

## State Machine Permission Grants

IAM roles, users, or groups which need to be able to work with a State Machine should be granted IAM permissions.

Any object that implements the `IGrantable` interface (has an associated principal) can be granted permissions by calling:

* `stateMachine.grantStartExecution(principal)` - grants the principal the ability to execute the state machine
* `stateMachine.grantRead(principal)` - grants the principal read access
* `stateMachine.grantTaskResponse(principal)` - grants the principal the ability to send task tokens to the state machine
* `stateMachine.grantExecution(principal, actions)` - grants the principal execution-level permissions for the IAM actions specified
* `stateMachine.grant(principal, actions)` - grants the principal state-machine-level permissions for the IAM actions specified

### Start Execution Permission

Grant permission to start an execution of a state machine by calling the `grantStartExecution()` API.

```python
# definition: sfn.IChainable
role = iam.Role(self, "Role",
    assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
)
state_machine = sfn.StateMachine(self, "StateMachine",
    definition=definition
)

# Give role permission to start execution of state machine
state_machine.grant_start_execution(role)
```

The following permission is provided to a service principal by the `grantStartExecution()` API:

* `states:StartExecution` - to state machine

### Read Permissions

Grant `read` access to a state machine by calling the `grantRead()` API.

```python
# definition: sfn.IChainable
role = iam.Role(self, "Role",
    assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
)
state_machine = sfn.StateMachine(self, "StateMachine",
    definition=definition
)

# Give role read access to state machine
state_machine.grant_read(role)
```

The following read permissions are provided to a service principal by the `grantRead()` API:

* `states:ListExecutions` - to state machine
* `states:ListStateMachines` - to state machine
* `states:DescribeExecution` - to executions
* `states:DescribeStateMachineForExecution` - to executions
* `states:GetExecutionHistory` - to executions
* `states:ListActivities` - to `*`
* `states:DescribeStateMachine` - to `*`
* `states:DescribeActivity` - to `*`

### Task Response Permissions

Grant permission to allow task responses to a state machine by calling the `grantTaskResponse()` API:

```python
# definition: sfn.IChainable
role = iam.Role(self, "Role",
    assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
)
state_machine = sfn.StateMachine(self, "StateMachine",
    definition=definition
)

# Give role task response permissions to the state machine
state_machine.grant_task_response(role)
```

The following read permissions are provided to a service principal by the `grantRead()` API:

* `states:SendTaskSuccess` - to state machine
* `states:SendTaskFailure` - to state machine
* `states:SendTaskHeartbeat` - to state machine

### Execution-level Permissions

Grant execution-level permissions to a state machine by calling the `grantExecution()` API:

```python
# definition: sfn.IChainable
role = iam.Role(self, "Role",
    assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
)
state_machine = sfn.StateMachine(self, "StateMachine",
    definition=definition
)

# Give role permission to get execution history of ALL executions for the state machine
state_machine.grant_execution(role, "states:GetExecutionHistory")
```

### Custom Permissions

You can add any set of permissions to a state machine by calling the `grant()` API.

```python
# definition: sfn.IChainable
user = iam.User(self, "MyUser")
state_machine = sfn.StateMachine(self, "StateMachine",
    definition=definition
)

# give user permission to send task success to the state machine
state_machine.grant(user, "states:SendTaskSuccess")
```

## Import

Any Step Functions state machine that has been created outside the stack can be imported
into your CDK stack.

State machines can be imported by their ARN via the `StateMachine.fromStateMachineArn()` API

```python
app = App()
stack = Stack(app, "MyStack")
sfn.StateMachine.from_state_machine_arn(stack, "ImportedStateMachine", "arn:aws:states:us-east-1:123456789012:stateMachine:StateMachine2E01A3A5-N5TJppzoevKQ")
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

import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_9b88bb94
import aws_cdk.aws_iam as _aws_cdk_aws_iam_940a1ce0
import aws_cdk.aws_logs as _aws_cdk_aws_logs_6c4320fb
import aws_cdk.core as _aws_cdk_core_f4b25747
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.ActivityProps",
    jsii_struct_bases=[],
    name_mapping={"activity_name": "activityName"},
)
class ActivityProps:
    def __init__(self, *, activity_name: typing.Optional[builtins.str] = None) -> None:
        '''Properties for defining a new Step Functions Activity.

        :param activity_name: The name for this activity. Default: - If not supplied, a name is generated

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_stepfunctions as stepfunctions
            
            activity_props = stepfunctions.ActivityProps(
                activity_name="activityName"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__584c3351df71821cf953cc2852b5defea4c2bb54fb5de252128f3a3c0bf78d33)
            check_type(argname="argument activity_name", value=activity_name, expected_type=type_hints["activity_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if activity_name is not None:
            self._values["activity_name"] = activity_name

    @builtins.property
    def activity_name(self) -> typing.Optional[builtins.str]:
        '''The name for this activity.

        :default: - If not supplied, a name is generated
        '''
        result = self._values.get("activity_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ActivityProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.AfterwardsOptions",
    jsii_struct_bases=[],
    name_mapping={
        "include_error_handlers": "includeErrorHandlers",
        "include_otherwise": "includeOtherwise",
    },
)
class AfterwardsOptions:
    def __init__(
        self,
        *,
        include_error_handlers: typing.Optional[builtins.bool] = None,
        include_otherwise: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Options for selecting the choice paths.

        :param include_error_handlers: Whether to include error handling states. If this is true, all states which are error handlers (added through 'onError') and states reachable via error handlers will be included as well. Default: false
        :param include_otherwise: Whether to include the default/otherwise transition for the current Choice state. If this is true and the current Choice does not have a default outgoing transition, one will be added included when .next() is called on the chain. Default: false

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_stepfunctions as stepfunctions
            
            afterwards_options = stepfunctions.AfterwardsOptions(
                include_error_handlers=False,
                include_otherwise=False
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d7d0ccf7be9eb2476e244176cdd664c3743097f7a9f26e8a645c14c2f9687a2)
            check_type(argname="argument include_error_handlers", value=include_error_handlers, expected_type=type_hints["include_error_handlers"])
            check_type(argname="argument include_otherwise", value=include_otherwise, expected_type=type_hints["include_otherwise"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if include_error_handlers is not None:
            self._values["include_error_handlers"] = include_error_handlers
        if include_otherwise is not None:
            self._values["include_otherwise"] = include_otherwise

    @builtins.property
    def include_error_handlers(self) -> typing.Optional[builtins.bool]:
        '''Whether to include error handling states.

        If this is true, all states which are error handlers (added through 'onError')
        and states reachable via error handlers will be included as well.

        :default: false
        '''
        result = self._values.get("include_error_handlers")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def include_otherwise(self) -> typing.Optional[builtins.bool]:
        '''Whether to include the default/otherwise transition for the current Choice state.

        If this is true and the current Choice does not have a default outgoing
        transition, one will be added included when .next() is called on the chain.

        :default: false
        '''
        result = self._values.get("include_otherwise")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AfterwardsOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.CatchProps",
    jsii_struct_bases=[],
    name_mapping={"errors": "errors", "result_path": "resultPath"},
)
class CatchProps:
    def __init__(
        self,
        *,
        errors: typing.Optional[typing.Sequence[builtins.str]] = None,
        result_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Error handler details.

        :param errors: Errors to recover from by going to the given state. A list of error strings to retry, which can be either predefined errors (for example Errors.NoChoiceMatched) or a self-defined error. Default: All errors
        :param result_path: JSONPath expression to indicate where to inject the error data. May also be the special value DISCARD, which will cause the error data to be discarded. Default: $

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_stepfunctions as stepfunctions
            
            catch_props = stepfunctions.CatchProps(
                errors=["errors"],
                result_path="resultPath"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f55af4b95f00bfb05c0159df065d2a46b70397d8a8a380607be1cd8e7dce818)
            check_type(argname="argument errors", value=errors, expected_type=type_hints["errors"])
            check_type(argname="argument result_path", value=result_path, expected_type=type_hints["result_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if errors is not None:
            self._values["errors"] = errors
        if result_path is not None:
            self._values["result_path"] = result_path

    @builtins.property
    def errors(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Errors to recover from by going to the given state.

        A list of error strings to retry, which can be either predefined errors
        (for example Errors.NoChoiceMatched) or a self-defined error.

        :default: All errors
        '''
        result = self._values.get("errors")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def result_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to indicate where to inject the error data.

        May also be the special value DISCARD, which will cause the error
        data to be discarded.

        :default: $
        '''
        result = self._values.get("result_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CatchProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_core_f4b25747.IInspectable)
class CfnActivity(
    _aws_cdk_core_f4b25747.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-stepfunctions.CfnActivity",
):
    '''A CloudFormation ``AWS::StepFunctions::Activity``.

    An activity is a task that you write in any programming language and host on any machine that has access to AWS Step Functions . Activities must poll Step Functions using the ``GetActivityTask`` API action and respond using ``SendTask*`` API actions. This function lets Step Functions know the existence of your activity and returns an identifier for use in a state machine and when polling from the activity.

    For information about creating an activity, see `Creating an Activity State Machine <https://docs.aws.amazon.com/step-functions/latest/dg/tutorial-creating-activity-state-machine.html>`_ in the *AWS Step Functions Developer Guide* and `CreateActivity <https://docs.aws.amazon.com/step-functions/latest/apireference/API_CreateActivity.html>`_ in the *AWS Step Functions API Reference* .

    :cloudformationResource: AWS::StepFunctions::Activity
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-activity.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_stepfunctions as stepfunctions
        
        cfn_activity = stepfunctions.CfnActivity(self, "MyCfnActivity",
            name="name",
        
            # the properties below are optional
            tags=[stepfunctions.CfnActivity.TagsEntryProperty(
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
        name: builtins.str,
        tags: typing.Optional[typing.Sequence[typing.Union["CfnActivity.TagsEntryProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Create a new ``AWS::StepFunctions::Activity``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param name: The name of the activity. A name must *not* contain: - white space - brackets ``< > { } [ ]`` - wildcard characters ``? *`` - special characters ``" # % \\ ^ | ~ `` $ & , ; : /` - control characters ( ``U+0000-001F`` , ``U+007F-009F`` ) To enable logging with CloudWatch Logs, the name should only contain 0-9, A-Z, a-z, - and _.
        :param tags: The list of tags to add to a resource. Tags may only contain Unicode letters, digits, white space, or these symbols: ``_ . : / = + - @`` .
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1daf032421a6dc31f1b05b5c3ef5dab91638fa27976f33d7f238fddc02ea0da)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnActivityProps(name=name, tags=tags)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _aws_cdk_core_f4b25747.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26845b59f7fb07c8387baf3a4f9ca72e8695bdc09fd2c245456b6444fb7f456b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3085158330b77db8234e9c4201ba7e05662d1ef0d9dad0740077f41072692184)
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
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> builtins.str:
        '''Returns the name of the activity. For example:.

        ``{ "Fn::GetAtt": ["MyActivity", "Name"] }``

        Returns a value similar to the following:

        ``myActivity``

        For more information about using ``Fn::GetAtt`` , see `Fn::GetAtt <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html>`_ .

        :cloudformationAttribute: Name
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrName"))

    @builtins.property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> _aws_cdk_core_f4b25747.TagManager:
        '''The list of tags to add to a resource.

        Tags may only contain Unicode letters, digits, white space, or these symbols: ``_ . : / = + - @`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-activity.html#cfn-stepfunctions-activity-tags
        '''
        return typing.cast(_aws_cdk_core_f4b25747.TagManager, jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the activity.

        A name must *not* contain:

        - white space
        - brackets ``< > { } [ ]``
        - wildcard characters ``? *``
        - special characters ``" # % \\ ^ | ~ `` $ & , ; : /`
        - control characters ( ``U+0000-001F`` , ``U+007F-009F`` )

        To enable logging with CloudWatch Logs, the name should only contain 0-9, A-Z, a-z, - and _.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-activity.html#cfn-stepfunctions-activity-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3389c4de048d503ef3f8fc6214c87dfbb3d11ac185baa8b112c499202ef3fbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-stepfunctions.CfnActivity.TagsEntryProperty",
        jsii_struct_bases=[],
        name_mapping={"key": "key", "value": "value"},
    )
    class TagsEntryProperty:
        def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
            '''The ``TagsEntry`` property specifies *tags* to identify an activity.

            :param key: The ``key`` for a key-value pair in a tag entry.
            :param value: The ``value`` for a key-value pair in a tag entry.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-activity-tagsentry.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_stepfunctions as stepfunctions
                
                tags_entry_property = stepfunctions.CfnActivity.TagsEntryProperty(
                    key="key",
                    value="value"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__bbe1434fb9bafeef1e62800c16045ab230936ea31431d7f75c6324b98da697d7)
                check_type(argname="argument key", value=key, expected_type=type_hints["key"])
                check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "key": key,
                "value": value,
            }

        @builtins.property
        def key(self) -> builtins.str:
            '''The ``key`` for a key-value pair in a tag entry.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-activity-tagsentry.html#cfn-stepfunctions-activity-tagsentry-key
            '''
            result = self._values.get("key")
            assert result is not None, "Required property 'key' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def value(self) -> builtins.str:
            '''The ``value`` for a key-value pair in a tag entry.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-activity-tagsentry.html#cfn-stepfunctions-activity-tagsentry-value
            '''
            result = self._values.get("value")
            assert result is not None, "Required property 'value' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TagsEntryProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.CfnActivityProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "tags": "tags"},
)
class CfnActivityProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        tags: typing.Optional[typing.Sequence[typing.Union[CfnActivity.TagsEntryProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for defining a ``CfnActivity``.

        :param name: The name of the activity. A name must *not* contain: - white space - brackets ``< > { } [ ]`` - wildcard characters ``? *`` - special characters ``" # % \\ ^ | ~ `` $ & , ; : /` - control characters ( ``U+0000-001F`` , ``U+007F-009F`` ) To enable logging with CloudWatch Logs, the name should only contain 0-9, A-Z, a-z, - and _.
        :param tags: The list of tags to add to a resource. Tags may only contain Unicode letters, digits, white space, or these symbols: ``_ . : / = + - @`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-activity.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_stepfunctions as stepfunctions
            
            cfn_activity_props = stepfunctions.CfnActivityProps(
                name="name",
            
                # the properties below are optional
                tags=[stepfunctions.CfnActivity.TagsEntryProperty(
                    key="key",
                    value="value"
                )]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc121bb17a642c051525e8dbe183eaadaa4afd72e04df8d7d70198aa60a9c603)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the activity.

        A name must *not* contain:

        - white space
        - brackets ``< > { } [ ]``
        - wildcard characters ``? *``
        - special characters ``" # % \\ ^ | ~ `` $ & , ; : /`
        - control characters ( ``U+0000-001F`` , ``U+007F-009F`` )

        To enable logging with CloudWatch Logs, the name should only contain 0-9, A-Z, a-z, - and _.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-activity.html#cfn-stepfunctions-activity-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[CfnActivity.TagsEntryProperty]]:
        '''The list of tags to add to a resource.

        Tags may only contain Unicode letters, digits, white space, or these symbols: ``_ . : / = + - @`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-activity.html#cfn-stepfunctions-activity-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[CfnActivity.TagsEntryProperty]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnActivityProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_core_f4b25747.IInspectable)
class CfnStateMachine(
    _aws_cdk_core_f4b25747.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-stepfunctions.CfnStateMachine",
):
    '''A CloudFormation ``AWS::StepFunctions::StateMachine``.

    Provisions a state machine. A state machine consists of a collection of states that can do work ( ``Task`` states), determine to which states to transition next ( ``Choice`` states), stop an execution with an error ( ``Fail`` states), and so on. State machines are specified using a JSON-based, structured language.

    :cloudformationResource: AWS::StepFunctions::StateMachine
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_stepfunctions as stepfunctions
        
        # definition: Any
        # definition_substitutions: Any
        
        cfn_state_machine = stepfunctions.CfnStateMachine(self, "MyCfnStateMachine",
            role_arn="roleArn",
        
            # the properties below are optional
            definition=definition,
            definition_s3_location=stepfunctions.CfnStateMachine.S3LocationProperty(
                bucket="bucket",
                key="key",
        
                # the properties below are optional
                version="version"
            ),
            definition_string="definitionString",
            definition_substitutions={
                "definition_substitutions_key": definition_substitutions
            },
            logging_configuration=stepfunctions.CfnStateMachine.LoggingConfigurationProperty(
                destinations=[stepfunctions.CfnStateMachine.LogDestinationProperty(
                    cloud_watch_logs_log_group=stepfunctions.CfnStateMachine.CloudWatchLogsLogGroupProperty(
                        log_group_arn="logGroupArn"
                    )
                )],
                include_execution_data=False,
                level="level"
            ),
            state_machine_name="stateMachineName",
            state_machine_type="stateMachineType",
            tags=[stepfunctions.CfnStateMachine.TagsEntryProperty(
                key="key",
                value="value"
            )],
            tracing_configuration=stepfunctions.CfnStateMachine.TracingConfigurationProperty(
                enabled=False
            )
        )
    '''

    def __init__(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        id: builtins.str,
        *,
        role_arn: builtins.str,
        definition: typing.Any = None,
        definition_s3_location: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnStateMachine.S3LocationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        definition_string: typing.Optional[builtins.str] = None,
        definition_substitutions: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Mapping[builtins.str, typing.Any]]] = None,
        logging_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnStateMachine.LoggingConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        state_machine_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union["CfnStateMachine.TagsEntryProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        tracing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnStateMachine.TracingConfigurationProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Create a new ``AWS::StepFunctions::StateMachine``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param role_arn: The Amazon Resource Name (ARN) of the IAM role to use for this state machine.
        :param definition: The Amazon States Language definition of the state machine. The state machine definition must be in JSON or YAML, and the format of the object must match the format of your AWS Step Functions template file. See `Amazon States Language <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html>`_ .
        :param definition_s3_location: The name of the S3 bucket where the state machine definition is stored. The state machine definition must be a JSON or YAML file.
        :param definition_string: The Amazon States Language definition of the state machine. The state machine definition must be in JSON. See `Amazon States Language <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html>`_ .
        :param definition_substitutions: A map (string to string) that specifies the mappings for placeholder variables in the state machine definition. This enables the customer to inject values obtained at runtime, for example from intrinsic functions, in the state machine definition. Variables can be template parameter names, resource logical IDs, resource attributes, or a variable in a key-value map.
        :param logging_configuration: Defines what execution history events are logged and where they are logged. .. epigraph:: By default, the ``level`` is set to ``OFF`` . For more information see `Log Levels <https://docs.aws.amazon.com/step-functions/latest/dg/cloudwatch-log-level.html>`_ in the AWS Step Functions User Guide.
        :param state_machine_name: The name of the state machine. A name must *not* contain: - white space - brackets ``< > { } [ ]`` - wildcard characters ``? *`` - special characters ``" # % \\ ^ | ~ `` $ & , ; : /` - control characters ( ``U+0000-001F`` , ``U+007F-009F`` ) .. epigraph:: If you specify a name, you cannot perform updates that require replacement of this resource. You can perform updates that require no or some interruption. If you must replace the resource, specify a new name.
        :param state_machine_type: Determines whether a ``STANDARD`` or ``EXPRESS`` state machine is created. The default is ``STANDARD`` . You cannot update the ``type`` of a state machine once it has been created. For more information on ``STANDARD`` and ``EXPRESS`` workflows, see `Standard Versus Express Workflows <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-standard-vs-express.html>`_ in the AWS Step Functions Developer Guide.
        :param tags: The list of tags to add to a resource. Tags may only contain Unicode letters, digits, white space, or these symbols: ``_ . : / = + - @`` .
        :param tracing_configuration: Selects whether or not the state machine's AWS X-Ray tracing is enabled.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff90c7e33bb5aba816833afb5965478a908f9d87f25354e1710af5795250019f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnStateMachineProps(
            role_arn=role_arn,
            definition=definition,
            definition_s3_location=definition_s3_location,
            definition_string=definition_string,
            definition_substitutions=definition_substitutions,
            logging_configuration=logging_configuration,
            state_machine_name=state_machine_name,
            state_machine_type=state_machine_type,
            tags=tags,
            tracing_configuration=tracing_configuration,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _aws_cdk_core_f4b25747.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c7ca4899ad3ec27f0be73a426dba404b5088f6a0e09d867df396999b7ac3147)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c464593fee0e40c67626c240fce34cbc7bbb45f5d7412e97a8de0df92804b83c)
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
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> builtins.str:
        '''Returns the name of the state machine. For example:.

        ``{ "Fn::GetAtt": ["MyStateMachine", "Name"] }``

        Returns the name of your state machine:

        ``HelloWorld-StateMachine``

        If you did not specify the name it will be similar to the following:

        ``MyStateMachine-1234abcdefgh``

        For more information about using ``Fn::GetAtt`` , see `Fn::GetAtt <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html>`_ .

        :cloudformationAttribute: Name
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrName"))

    @builtins.property
    @jsii.member(jsii_name="attrStateMachineRevisionId")
    def attr_state_machine_revision_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: StateMachineRevisionId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrStateMachineRevisionId"))

    @builtins.property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> _aws_cdk_core_f4b25747.TagManager:
        '''The list of tags to add to a resource.

        Tags may only contain Unicode letters, digits, white space, or these symbols: ``_ . : / = + - @`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-tags
        '''
        return typing.cast(_aws_cdk_core_f4b25747.TagManager, jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="definition")
    def definition(self) -> typing.Any:
        '''The Amazon States Language definition of the state machine.

        The state machine definition must be in JSON or YAML, and the format of the object must match the format of your AWS Step Functions template file. See `Amazon States Language <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-definition
        '''
        return typing.cast(typing.Any, jsii.get(self, "definition"))

    @definition.setter
    def definition(self, value: typing.Any) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__321835c0ad1b15082dbb2019c7b37a99b421ae4221e1579bfa85c9da9eb88e1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "definition", value)

    @builtins.property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the IAM role to use for this state machine.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-rolearn
        '''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35443f3b6328c55a2e194d6699fd214b4ae70ff1a4543cfd32e27aea85b1b64f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleArn", value)

    @builtins.property
    @jsii.member(jsii_name="definitionS3Location")
    def definition_s3_location(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnStateMachine.S3LocationProperty"]]:
        '''The name of the S3 bucket where the state machine definition is stored.

        The state machine definition must be a JSON or YAML file.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-definitions3location
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnStateMachine.S3LocationProperty"]], jsii.get(self, "definitionS3Location"))

    @definition_s3_location.setter
    def definition_s3_location(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnStateMachine.S3LocationProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c57a09ca865900be7e74a8c4324c2141bf9d98c4391343b788df000ca86ce2b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "definitionS3Location", value)

    @builtins.property
    @jsii.member(jsii_name="definitionString")
    def definition_string(self) -> typing.Optional[builtins.str]:
        '''The Amazon States Language definition of the state machine.

        The state machine definition must be in JSON. See `Amazon States Language <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-definitionstring
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "definitionString"))

    @definition_string.setter
    def definition_string(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__724b2455ade0b5a6ac6149832c60f0c30a2743b6aeeef2d482d3bafe94f7a09d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "definitionString", value)

    @builtins.property
    @jsii.member(jsii_name="definitionSubstitutions")
    def definition_substitutions(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Mapping[builtins.str, typing.Any]]]:
        '''A map (string to string) that specifies the mappings for placeholder variables in the state machine definition.

        This enables the customer to inject values obtained at runtime, for example from intrinsic functions, in the state machine definition. Variables can be template parameter names, resource logical IDs, resource attributes, or a variable in a key-value map.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-definitionsubstitutions
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Mapping[builtins.str, typing.Any]]], jsii.get(self, "definitionSubstitutions"))

    @definition_substitutions.setter
    def definition_substitutions(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Mapping[builtins.str, typing.Any]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d46799eead8268d74deabe7fc9cd05e858775c666ce1c97390bda11ed0d4337c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "definitionSubstitutions", value)

    @builtins.property
    @jsii.member(jsii_name="loggingConfiguration")
    def logging_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnStateMachine.LoggingConfigurationProperty"]]:
        '''Defines what execution history events are logged and where they are logged.

        .. epigraph::

           By default, the ``level`` is set to ``OFF`` . For more information see `Log Levels <https://docs.aws.amazon.com/step-functions/latest/dg/cloudwatch-log-level.html>`_ in the AWS Step Functions User Guide.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-loggingconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnStateMachine.LoggingConfigurationProperty"]], jsii.get(self, "loggingConfiguration"))

    @logging_configuration.setter
    def logging_configuration(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnStateMachine.LoggingConfigurationProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57144e55d1c58655b17e341dfa0e9be6d0f60953765045857da3eb5e8ef32e55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "loggingConfiguration", value)

    @builtins.property
    @jsii.member(jsii_name="stateMachineName")
    def state_machine_name(self) -> typing.Optional[builtins.str]:
        '''The name of the state machine.

        A name must *not* contain:

        - white space
        - brackets ``< > { } [ ]``
        - wildcard characters ``? *``
        - special characters ``" # % \\ ^ | ~ `` $ & , ; : /`
        - control characters ( ``U+0000-001F`` , ``U+007F-009F`` )

        .. epigraph::

           If you specify a name, you cannot perform updates that require replacement of this resource. You can perform updates that require no or some interruption. If you must replace the resource, specify a new name.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-statemachinename
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateMachineName"))

    @state_machine_name.setter
    def state_machine_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee1632fca990d5d684651d1801150322e8522dcb2dad7b373f2475b2d3fb50c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stateMachineName", value)

    @builtins.property
    @jsii.member(jsii_name="stateMachineType")
    def state_machine_type(self) -> typing.Optional[builtins.str]:
        '''Determines whether a ``STANDARD`` or ``EXPRESS`` state machine is created.

        The default is ``STANDARD`` . You cannot update the ``type`` of a state machine once it has been created. For more information on ``STANDARD`` and ``EXPRESS`` workflows, see `Standard Versus Express Workflows <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-standard-vs-express.html>`_ in the AWS Step Functions Developer Guide.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-statemachinetype
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateMachineType"))

    @state_machine_type.setter
    def state_machine_type(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1eafea1651731878943bfa9ece4684df2d7b41c62f328d986893ce759197fa99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stateMachineType", value)

    @builtins.property
    @jsii.member(jsii_name="tracingConfiguration")
    def tracing_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnStateMachine.TracingConfigurationProperty"]]:
        '''Selects whether or not the state machine's AWS X-Ray tracing is enabled.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-tracingconfiguration
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnStateMachine.TracingConfigurationProperty"]], jsii.get(self, "tracingConfiguration"))

    @tracing_configuration.setter
    def tracing_configuration(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnStateMachine.TracingConfigurationProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce9ed5153277e16dfd1e6c26337d96ec20a6b7226f466cb89f6bda4db97b5349)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tracingConfiguration", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-stepfunctions.CfnStateMachine.CloudWatchLogsLogGroupProperty",
        jsii_struct_bases=[],
        name_mapping={"log_group_arn": "logGroupArn"},
    )
    class CloudWatchLogsLogGroupProperty:
        def __init__(
            self,
            *,
            log_group_arn: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Defines a CloudWatch log group.

            .. epigraph::

               For more information see `Standard Versus Express Workflows <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-standard-vs-express.html>`_ in the AWS Step Functions Developer Guide.

            :param log_group_arn: The ARN of the the CloudWatch log group to which you want your logs emitted to. The ARN must end with ``:*``

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-cloudwatchlogsloggroup.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_stepfunctions as stepfunctions
                
                cloud_watch_logs_log_group_property = stepfunctions.CfnStateMachine.CloudWatchLogsLogGroupProperty(
                    log_group_arn="logGroupArn"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__f1ec312887402e839eff6b5f98571af91f35bdf71b3072c402a7d735b686b89c)
                check_type(argname="argument log_group_arn", value=log_group_arn, expected_type=type_hints["log_group_arn"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if log_group_arn is not None:
                self._values["log_group_arn"] = log_group_arn

        @builtins.property
        def log_group_arn(self) -> typing.Optional[builtins.str]:
            '''The ARN of the the CloudWatch log group to which you want your logs emitted to.

            The ARN must end with ``:*``

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-cloudwatchlogsloggroup.html#cfn-stepfunctions-statemachine-cloudwatchlogsloggroup-loggrouparn
            '''
            result = self._values.get("log_group_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CloudWatchLogsLogGroupProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-stepfunctions.CfnStateMachine.LogDestinationProperty",
        jsii_struct_bases=[],
        name_mapping={"cloud_watch_logs_log_group": "cloudWatchLogsLogGroup"},
    )
    class LogDestinationProperty:
        def __init__(
            self,
            *,
            cloud_watch_logs_log_group: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnStateMachine.CloudWatchLogsLogGroupProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''Defines a destination for ``LoggingConfiguration`` .

            .. epigraph::

               For more information on logging with ``EXPRESS`` workflows, see `Logging Express Workflows Using CloudWatch Logs <https://docs.aws.amazon.com/step-functions/latest/dg/cw-logs.html>`_ .

            :param cloud_watch_logs_log_group: An object describing a CloudWatch log group. For more information, see `AWS::Logs::LogGroup <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-loggroup.html>`_ in the AWS CloudFormation User Guide.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-logdestination.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_stepfunctions as stepfunctions
                
                log_destination_property = stepfunctions.CfnStateMachine.LogDestinationProperty(
                    cloud_watch_logs_log_group=stepfunctions.CfnStateMachine.CloudWatchLogsLogGroupProperty(
                        log_group_arn="logGroupArn"
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__13abb8df480e0b4a3f3e0419de964941def29cedd011c0b2b79a7fedbad5d298)
                check_type(argname="argument cloud_watch_logs_log_group", value=cloud_watch_logs_log_group, expected_type=type_hints["cloud_watch_logs_log_group"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if cloud_watch_logs_log_group is not None:
                self._values["cloud_watch_logs_log_group"] = cloud_watch_logs_log_group

        @builtins.property
        def cloud_watch_logs_log_group(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnStateMachine.CloudWatchLogsLogGroupProperty"]]:
            '''An object describing a CloudWatch log group.

            For more information, see `AWS::Logs::LogGroup <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-logs-loggroup.html>`_ in the AWS CloudFormation User Guide.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-logdestination.html#cfn-stepfunctions-statemachine-logdestination-cloudwatchlogsloggroup
            '''
            result = self._values.get("cloud_watch_logs_log_group")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnStateMachine.CloudWatchLogsLogGroupProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LogDestinationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-stepfunctions.CfnStateMachine.LoggingConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "destinations": "destinations",
            "include_execution_data": "includeExecutionData",
            "level": "level",
        },
    )
    class LoggingConfigurationProperty:
        def __init__(
            self,
            *,
            destinations: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnStateMachine.LogDestinationProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
            include_execution_data: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            level: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Defines what execution history events are logged and where they are logged.

            .. epigraph::

               By default, the ``level`` is set to ``OFF`` . For more information see `Log Levels <https://docs.aws.amazon.com/step-functions/latest/dg/cloudwatch-log-level.html>`_ in the AWS Step Functions User Guide.

            :param destinations: An array of objects that describes where your execution history events will be logged. Limited to size 1. Required, if your log level is not set to ``OFF`` .
            :param include_execution_data: Determines whether execution data is included in your log. When set to ``false`` , data is excluded.
            :param level: Defines which category of execution history events are logged.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-loggingconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_stepfunctions as stepfunctions
                
                logging_configuration_property = stepfunctions.CfnStateMachine.LoggingConfigurationProperty(
                    destinations=[stepfunctions.CfnStateMachine.LogDestinationProperty(
                        cloud_watch_logs_log_group=stepfunctions.CfnStateMachine.CloudWatchLogsLogGroupProperty(
                            log_group_arn="logGroupArn"
                        )
                    )],
                    include_execution_data=False,
                    level="level"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__5764fed2df18aeb671ae245f634f006d8c85cf7c760a687539d4533164a573a3)
                check_type(argname="argument destinations", value=destinations, expected_type=type_hints["destinations"])
                check_type(argname="argument include_execution_data", value=include_execution_data, expected_type=type_hints["include_execution_data"])
                check_type(argname="argument level", value=level, expected_type=type_hints["level"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if destinations is not None:
                self._values["destinations"] = destinations
            if include_execution_data is not None:
                self._values["include_execution_data"] = include_execution_data
            if level is not None:
                self._values["level"] = level

        @builtins.property
        def destinations(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnStateMachine.LogDestinationProperty"]]]]:
            '''An array of objects that describes where your execution history events will be logged.

            Limited to size 1. Required, if your log level is not set to ``OFF`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-loggingconfiguration.html#cfn-stepfunctions-statemachine-loggingconfiguration-destinations
            '''
            result = self._values.get("destinations")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnStateMachine.LogDestinationProperty"]]]], result)

        @builtins.property
        def include_execution_data(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''Determines whether execution data is included in your log.

            When set to ``false`` , data is excluded.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-loggingconfiguration.html#cfn-stepfunctions-statemachine-loggingconfiguration-includeexecutiondata
            '''
            result = self._values.get("include_execution_data")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def level(self) -> typing.Optional[builtins.str]:
            '''Defines which category of execution history events are logged.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-loggingconfiguration.html#cfn-stepfunctions-statemachine-loggingconfiguration-level
            '''
            result = self._values.get("level")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LoggingConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-stepfunctions.CfnStateMachine.S3LocationProperty",
        jsii_struct_bases=[],
        name_mapping={"bucket": "bucket", "key": "key", "version": "version"},
    )
    class S3LocationProperty:
        def __init__(
            self,
            *,
            bucket: builtins.str,
            key: builtins.str,
            version: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Defines the S3 bucket location where a state machine definition is stored.

            The state machine definition must be a JSON or YAML file.

            :param bucket: The name of the S3 bucket where the state machine definition JSON or YAML file is stored.
            :param key: The name of the state machine definition file (Amazon S3 object name).
            :param version: For versioning-enabled buckets, a specific version of the state machine definition.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-s3location.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_stepfunctions as stepfunctions
                
                s3_location_property = stepfunctions.CfnStateMachine.S3LocationProperty(
                    bucket="bucket",
                    key="key",
                
                    # the properties below are optional
                    version="version"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__49b1c4b8bc4fe296ed687aa62efe51a9220452c93f09e68b36558eb1c0bd8bf1)
                check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
                check_type(argname="argument key", value=key, expected_type=type_hints["key"])
                check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "bucket": bucket,
                "key": key,
            }
            if version is not None:
                self._values["version"] = version

        @builtins.property
        def bucket(self) -> builtins.str:
            '''The name of the S3 bucket where the state machine definition JSON or YAML file is stored.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-s3location.html#cfn-stepfunctions-statemachine-s3location-bucket
            '''
            result = self._values.get("bucket")
            assert result is not None, "Required property 'bucket' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def key(self) -> builtins.str:
            '''The name of the state machine definition file (Amazon S3 object name).

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-s3location.html#cfn-stepfunctions-statemachine-s3location-key
            '''
            result = self._values.get("key")
            assert result is not None, "Required property 'key' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def version(self) -> typing.Optional[builtins.str]:
            '''For versioning-enabled buckets, a specific version of the state machine definition.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-s3location.html#cfn-stepfunctions-statemachine-s3location-version
            '''
            result = self._values.get("version")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3LocationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-stepfunctions.CfnStateMachine.TagsEntryProperty",
        jsii_struct_bases=[],
        name_mapping={"key": "key", "value": "value"},
    )
    class TagsEntryProperty:
        def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
            '''The ``TagsEntry`` property specifies *tags* to identify a state machine.

            :param key: The ``key`` for a key-value pair in a tag entry.
            :param value: The ``value`` for a key-value pair in a tag entry.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-tagsentry.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_stepfunctions as stepfunctions
                
                tags_entry_property = stepfunctions.CfnStateMachine.TagsEntryProperty(
                    key="key",
                    value="value"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__b268add728e11421a9683c6b4b6d20c9d8bd445b38dc0f1ca24b921af84047d6)
                check_type(argname="argument key", value=key, expected_type=type_hints["key"])
                check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "key": key,
                "value": value,
            }

        @builtins.property
        def key(self) -> builtins.str:
            '''The ``key`` for a key-value pair in a tag entry.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-tagsentry.html#cfn-stepfunctions-statemachine-tagsentry-key
            '''
            result = self._values.get("key")
            assert result is not None, "Required property 'key' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def value(self) -> builtins.str:
            '''The ``value`` for a key-value pair in a tag entry.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-tagsentry.html#cfn-stepfunctions-statemachine-tagsentry-value
            '''
            result = self._values.get("value")
            assert result is not None, "Required property 'value' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TagsEntryProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-stepfunctions.CfnStateMachine.TracingConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"enabled": "enabled"},
    )
    class TracingConfigurationProperty:
        def __init__(
            self,
            *,
            enabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
        ) -> None:
            '''Selects whether or not the state machine's AWS X-Ray tracing is enabled.

            To configure your state machine to send trace data to X-Ray, set ``Enabled`` to ``true`` .

            :param enabled: When set to ``true`` , X-Ray tracing is enabled.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-tracingconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_stepfunctions as stepfunctions
                
                tracing_configuration_property = stepfunctions.CfnStateMachine.TracingConfigurationProperty(
                    enabled=False
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__9adb57c144f02482ad65083eb837116bac324772c7473a8284250f8786509f0b)
                check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if enabled is not None:
                self._values["enabled"] = enabled

        @builtins.property
        def enabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''When set to ``true`` , X-Ray tracing is enabled.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-tracingconfiguration.html#cfn-stepfunctions-statemachine-tracingconfiguration-enabled
            '''
            result = self._values.get("enabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TracingConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.CfnStateMachineProps",
    jsii_struct_bases=[],
    name_mapping={
        "role_arn": "roleArn",
        "definition": "definition",
        "definition_s3_location": "definitionS3Location",
        "definition_string": "definitionString",
        "definition_substitutions": "definitionSubstitutions",
        "logging_configuration": "loggingConfiguration",
        "state_machine_name": "stateMachineName",
        "state_machine_type": "stateMachineType",
        "tags": "tags",
        "tracing_configuration": "tracingConfiguration",
    },
)
class CfnStateMachineProps:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        definition: typing.Any = None,
        definition_s3_location: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnStateMachine.S3LocationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        definition_string: typing.Optional[builtins.str] = None,
        definition_substitutions: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Mapping[builtins.str, typing.Any]]] = None,
        logging_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnStateMachine.LoggingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        state_machine_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[CfnStateMachine.TagsEntryProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        tracing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnStateMachine.TracingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for defining a ``CfnStateMachine``.

        :param role_arn: The Amazon Resource Name (ARN) of the IAM role to use for this state machine.
        :param definition: The Amazon States Language definition of the state machine. The state machine definition must be in JSON or YAML, and the format of the object must match the format of your AWS Step Functions template file. See `Amazon States Language <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html>`_ .
        :param definition_s3_location: The name of the S3 bucket where the state machine definition is stored. The state machine definition must be a JSON or YAML file.
        :param definition_string: The Amazon States Language definition of the state machine. The state machine definition must be in JSON. See `Amazon States Language <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html>`_ .
        :param definition_substitutions: A map (string to string) that specifies the mappings for placeholder variables in the state machine definition. This enables the customer to inject values obtained at runtime, for example from intrinsic functions, in the state machine definition. Variables can be template parameter names, resource logical IDs, resource attributes, or a variable in a key-value map.
        :param logging_configuration: Defines what execution history events are logged and where they are logged. .. epigraph:: By default, the ``level`` is set to ``OFF`` . For more information see `Log Levels <https://docs.aws.amazon.com/step-functions/latest/dg/cloudwatch-log-level.html>`_ in the AWS Step Functions User Guide.
        :param state_machine_name: The name of the state machine. A name must *not* contain: - white space - brackets ``< > { } [ ]`` - wildcard characters ``? *`` - special characters ``" # % \\ ^ | ~ `` $ & , ; : /` - control characters ( ``U+0000-001F`` , ``U+007F-009F`` ) .. epigraph:: If you specify a name, you cannot perform updates that require replacement of this resource. You can perform updates that require no or some interruption. If you must replace the resource, specify a new name.
        :param state_machine_type: Determines whether a ``STANDARD`` or ``EXPRESS`` state machine is created. The default is ``STANDARD`` . You cannot update the ``type`` of a state machine once it has been created. For more information on ``STANDARD`` and ``EXPRESS`` workflows, see `Standard Versus Express Workflows <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-standard-vs-express.html>`_ in the AWS Step Functions Developer Guide.
        :param tags: The list of tags to add to a resource. Tags may only contain Unicode letters, digits, white space, or these symbols: ``_ . : / = + - @`` .
        :param tracing_configuration: Selects whether or not the state machine's AWS X-Ray tracing is enabled.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_stepfunctions as stepfunctions
            
            # definition: Any
            # definition_substitutions: Any
            
            cfn_state_machine_props = stepfunctions.CfnStateMachineProps(
                role_arn="roleArn",
            
                # the properties below are optional
                definition=definition,
                definition_s3_location=stepfunctions.CfnStateMachine.S3LocationProperty(
                    bucket="bucket",
                    key="key",
            
                    # the properties below are optional
                    version="version"
                ),
                definition_string="definitionString",
                definition_substitutions={
                    "definition_substitutions_key": definition_substitutions
                },
                logging_configuration=stepfunctions.CfnStateMachine.LoggingConfigurationProperty(
                    destinations=[stepfunctions.CfnStateMachine.LogDestinationProperty(
                        cloud_watch_logs_log_group=stepfunctions.CfnStateMachine.CloudWatchLogsLogGroupProperty(
                            log_group_arn="logGroupArn"
                        )
                    )],
                    include_execution_data=False,
                    level="level"
                ),
                state_machine_name="stateMachineName",
                state_machine_type="stateMachineType",
                tags=[stepfunctions.CfnStateMachine.TagsEntryProperty(
                    key="key",
                    value="value"
                )],
                tracing_configuration=stepfunctions.CfnStateMachine.TracingConfigurationProperty(
                    enabled=False
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1f366e4958852bcc1ef5b964e760137e591d192eb367ec75d4d35278b47d69a)
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument definition", value=definition, expected_type=type_hints["definition"])
            check_type(argname="argument definition_s3_location", value=definition_s3_location, expected_type=type_hints["definition_s3_location"])
            check_type(argname="argument definition_string", value=definition_string, expected_type=type_hints["definition_string"])
            check_type(argname="argument definition_substitutions", value=definition_substitutions, expected_type=type_hints["definition_substitutions"])
            check_type(argname="argument logging_configuration", value=logging_configuration, expected_type=type_hints["logging_configuration"])
            check_type(argname="argument state_machine_name", value=state_machine_name, expected_type=type_hints["state_machine_name"])
            check_type(argname="argument state_machine_type", value=state_machine_type, expected_type=type_hints["state_machine_type"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument tracing_configuration", value=tracing_configuration, expected_type=type_hints["tracing_configuration"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role_arn": role_arn,
        }
        if definition is not None:
            self._values["definition"] = definition
        if definition_s3_location is not None:
            self._values["definition_s3_location"] = definition_s3_location
        if definition_string is not None:
            self._values["definition_string"] = definition_string
        if definition_substitutions is not None:
            self._values["definition_substitutions"] = definition_substitutions
        if logging_configuration is not None:
            self._values["logging_configuration"] = logging_configuration
        if state_machine_name is not None:
            self._values["state_machine_name"] = state_machine_name
        if state_machine_type is not None:
            self._values["state_machine_type"] = state_machine_type
        if tags is not None:
            self._values["tags"] = tags
        if tracing_configuration is not None:
            self._values["tracing_configuration"] = tracing_configuration

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the IAM role to use for this state machine.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-rolearn
        '''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def definition(self) -> typing.Any:
        '''The Amazon States Language definition of the state machine.

        The state machine definition must be in JSON or YAML, and the format of the object must match the format of your AWS Step Functions template file. See `Amazon States Language <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-definition
        '''
        result = self._values.get("definition")
        return typing.cast(typing.Any, result)

    @builtins.property
    def definition_s3_location(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnStateMachine.S3LocationProperty]]:
        '''The name of the S3 bucket where the state machine definition is stored.

        The state machine definition must be a JSON or YAML file.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-definitions3location
        '''
        result = self._values.get("definition_s3_location")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnStateMachine.S3LocationProperty]], result)

    @builtins.property
    def definition_string(self) -> typing.Optional[builtins.str]:
        '''The Amazon States Language definition of the state machine.

        The state machine definition must be in JSON. See `Amazon States Language <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-definitionstring
        '''
        result = self._values.get("definition_string")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def definition_substitutions(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Mapping[builtins.str, typing.Any]]]:
        '''A map (string to string) that specifies the mappings for placeholder variables in the state machine definition.

        This enables the customer to inject values obtained at runtime, for example from intrinsic functions, in the state machine definition. Variables can be template parameter names, resource logical IDs, resource attributes, or a variable in a key-value map.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-definitionsubstitutions
        '''
        result = self._values.get("definition_substitutions")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Mapping[builtins.str, typing.Any]]], result)

    @builtins.property
    def logging_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnStateMachine.LoggingConfigurationProperty]]:
        '''Defines what execution history events are logged and where they are logged.

        .. epigraph::

           By default, the ``level`` is set to ``OFF`` . For more information see `Log Levels <https://docs.aws.amazon.com/step-functions/latest/dg/cloudwatch-log-level.html>`_ in the AWS Step Functions User Guide.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-loggingconfiguration
        '''
        result = self._values.get("logging_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnStateMachine.LoggingConfigurationProperty]], result)

    @builtins.property
    def state_machine_name(self) -> typing.Optional[builtins.str]:
        '''The name of the state machine.

        A name must *not* contain:

        - white space
        - brackets ``< > { } [ ]``
        - wildcard characters ``? *``
        - special characters ``" # % \\ ^ | ~ `` $ & , ; : /`
        - control characters ( ``U+0000-001F`` , ``U+007F-009F`` )

        .. epigraph::

           If you specify a name, you cannot perform updates that require replacement of this resource. You can perform updates that require no or some interruption. If you must replace the resource, specify a new name.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-statemachinename
        '''
        result = self._values.get("state_machine_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state_machine_type(self) -> typing.Optional[builtins.str]:
        '''Determines whether a ``STANDARD`` or ``EXPRESS`` state machine is created.

        The default is ``STANDARD`` . You cannot update the ``type`` of a state machine once it has been created. For more information on ``STANDARD`` and ``EXPRESS`` workflows, see `Standard Versus Express Workflows <https://docs.aws.amazon.com/step-functions/latest/dg/concepts-standard-vs-express.html>`_ in the AWS Step Functions Developer Guide.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-statemachinetype
        '''
        result = self._values.get("state_machine_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[CfnStateMachine.TagsEntryProperty]]:
        '''The list of tags to add to a resource.

        Tags may only contain Unicode letters, digits, white space, or these symbols: ``_ . : / = + - @`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[CfnStateMachine.TagsEntryProperty]], result)

    @builtins.property
    def tracing_configuration(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnStateMachine.TracingConfigurationProperty]]:
        '''Selects whether or not the state machine's AWS X-Ray tracing is enabled.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html#cfn-stepfunctions-statemachine-tracingconfiguration
        '''
        result = self._values.get("tracing_configuration")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnStateMachine.TracingConfigurationProperty]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnStateMachineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.ChoiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "comment": "comment",
        "input_path": "inputPath",
        "output_path": "outputPath",
    },
)
class ChoiceProps:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a Choice state.

        :param comment: An optional description for this state. Default: No comment
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param output_path: JSONPath expression to select part of the state to be the output to this state. May also be the special value DISCARD, which will cause the effective output to be the empty object {}. Default: $

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_stepfunctions as stepfunctions
            
            choice_props = stepfunctions.ChoiceProps(
                comment="comment",
                input_path="inputPath",
                output_path="outputPath"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ac01f94b0860aca9ab54646b25e9c773e10e8f5407192cd6d25ea68240ead75)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if input_path is not None:
            self._values["input_path"] = input_path
        if output_path is not None:
            self._values["output_path"] = output_path

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the input to this state.

        May also be the special value DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: $
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the output to this state.

        May also be the special value DISCARD, which will cause the effective
        output to be the empty object {}.

        :default: $
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ChoiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Condition(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-stepfunctions.Condition",
):
    '''A Condition for use in a Choice state branch.

    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_lambda as lambda_
        
        # submit_lambda: lambda.Function
        # get_status_lambda: lambda.Function
        
        
        submit_job = tasks.LambdaInvoke(self, "Submit Job",
            lambda_function=submit_lambda,
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload"
        )
        
        wait_x = sfn.Wait(self, "Wait X Seconds",
            time=sfn.WaitTime.seconds_path("$.waitSeconds")
        )
        
        get_status = tasks.LambdaInvoke(self, "Get Job Status",
            lambda_function=get_status_lambda,
            # Pass just the field named "guid" into the Lambda, put the
            # Lambda's result in a field called "status" in the response
            input_path="$.guid",
            output_path="$.Payload"
        )
        
        job_failed = sfn.Fail(self, "Job Failed",
            cause="AWS Batch Job Failed",
            error="DescribeJob returned FAILED"
        )
        
        final_status = tasks.LambdaInvoke(self, "Get Final Job Status",
            lambda_function=get_status_lambda,
            # Use "guid" field as input
            input_path="$.guid",
            output_path="$.Payload"
        )
        
        definition = submit_job.next(wait_x).next(get_status).next(sfn.Choice(self, "Job Complete?").when(sfn.Condition.string_equals("$.status", "FAILED"), job_failed).when(sfn.Condition.string_equals("$.status", "SUCCEEDED"), final_status).otherwise(wait_x))
        
        sfn.StateMachine(self, "StateMachine",
            definition=definition,
            timeout=Duration.minutes(5)
        )
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="and")
    @builtins.classmethod
    def and_(cls, *conditions: "Condition") -> "Condition":
        '''Combine two or more conditions with a logical AND.

        :param conditions: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06fa28bee94a8e66dde9f678596a1b2b8c1b81483f7a6b443c80f59ab422d599)
            check_type(argname="argument conditions", value=conditions, expected_type=typing.Tuple[type_hints["conditions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast("Condition", jsii.sinvoke(cls, "and", [*conditions]))

    @jsii.member(jsii_name="booleanEquals")
    @builtins.classmethod
    def boolean_equals(
        cls,
        variable: builtins.str,
        value: builtins.bool,
    ) -> "Condition":
        '''Matches if a boolean field has the given value.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e08cdcf85b8839197b7eaed0d3b3b67a25f1b6c65489cc06b61bce61f8e35df0)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "booleanEquals", [variable, value]))

    @jsii.member(jsii_name="booleanEqualsJsonPath")
    @builtins.classmethod
    def boolean_equals_json_path(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a boolean field equals to a value at a given mapping path.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24219323ed35aeb740044cc130782b78efbf64045ba4c07bb2a05c1d6ac00648)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "booleanEqualsJsonPath", [variable, value]))

    @jsii.member(jsii_name="isBoolean")
    @builtins.classmethod
    def is_boolean(cls, variable: builtins.str) -> "Condition":
        '''Matches if variable is boolean.

        :param variable: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01c40a33ddab4c378ee37e6d0267afbc79ddad8d3bf70a7d54f9015bfafcbbc3)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
        return typing.cast("Condition", jsii.sinvoke(cls, "isBoolean", [variable]))

    @jsii.member(jsii_name="isNotBoolean")
    @builtins.classmethod
    def is_not_boolean(cls, variable: builtins.str) -> "Condition":
        '''Matches if variable is not boolean.

        :param variable: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29f431beb7641d5f1248823cb3a4986794d36fb00a5d2068750af2386677f73c)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
        return typing.cast("Condition", jsii.sinvoke(cls, "isNotBoolean", [variable]))

    @jsii.member(jsii_name="isNotNull")
    @builtins.classmethod
    def is_not_null(cls, variable: builtins.str) -> "Condition":
        '''Matches if variable is not null.

        :param variable: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd3bc8d7574eb3adafe5678f6ce3cd03388e2007f2f33eaec60ea793282c6d58)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
        return typing.cast("Condition", jsii.sinvoke(cls, "isNotNull", [variable]))

    @jsii.member(jsii_name="isNotNumeric")
    @builtins.classmethod
    def is_not_numeric(cls, variable: builtins.str) -> "Condition":
        '''Matches if variable is not numeric.

        :param variable: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37f5f52f2fd73ef9f7ea91da166f2243bef2b82ae281ee1128e87f1ded3dfc76)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
        return typing.cast("Condition", jsii.sinvoke(cls, "isNotNumeric", [variable]))

    @jsii.member(jsii_name="isNotPresent")
    @builtins.classmethod
    def is_not_present(cls, variable: builtins.str) -> "Condition":
        '''Matches if variable is not present.

        :param variable: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38f3e8d6d585aaa07f0e7d0a14d25b5066f3e25f1df698c1318d92e0459b95fa)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
        return typing.cast("Condition", jsii.sinvoke(cls, "isNotPresent", [variable]))

    @jsii.member(jsii_name="isNotString")
    @builtins.classmethod
    def is_not_string(cls, variable: builtins.str) -> "Condition":
        '''Matches if variable is not a string.

        :param variable: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3865901af3d4f1c3453ca902202c4dd43c56071b23a4f9bb9a3d4c619c7fc743)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
        return typing.cast("Condition", jsii.sinvoke(cls, "isNotString", [variable]))

    @jsii.member(jsii_name="isNotTimestamp")
    @builtins.classmethod
    def is_not_timestamp(cls, variable: builtins.str) -> "Condition":
        '''Matches if variable is not a timestamp.

        :param variable: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__028d007feb2ec2563bd4365fb9e32bd2615bd2d9d871934a6cdb8c5670f83f38)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
        return typing.cast("Condition", jsii.sinvoke(cls, "isNotTimestamp", [variable]))

    @jsii.member(jsii_name="isNull")
    @builtins.classmethod
    def is_null(cls, variable: builtins.str) -> "Condition":
        '''Matches if variable is Null.

        :param variable: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63ef7cdfd2393b60051b09094dcc8d8e9bc5254033c369b022a72201b2997751)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
        return typing.cast("Condition", jsii.sinvoke(cls, "isNull", [variable]))

    @jsii.member(jsii_name="isNumeric")
    @builtins.classmethod
    def is_numeric(cls, variable: builtins.str) -> "Condition":
        '''Matches if variable is numeric.

        :param variable: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2dc6efe6d876559015c0a285483cab48833c6c197922f172dabe3de389b8959)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
        return typing.cast("Condition", jsii.sinvoke(cls, "isNumeric", [variable]))

    @jsii.member(jsii_name="isPresent")
    @builtins.classmethod
    def is_present(cls, variable: builtins.str) -> "Condition":
        '''Matches if variable is present.

        :param variable: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abb32d29c7bae7b58544fcf0eb1041489b11ff4c36e27e45a256f5e85bc25641)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
        return typing.cast("Condition", jsii.sinvoke(cls, "isPresent", [variable]))

    @jsii.member(jsii_name="isString")
    @builtins.classmethod
    def is_string(cls, variable: builtins.str) -> "Condition":
        '''Matches if variable is a string.

        :param variable: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91d62a700a1f92610d7a5b972cc91f02b6177066f50cbbd9e5d1db9c911a12fd)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
        return typing.cast("Condition", jsii.sinvoke(cls, "isString", [variable]))

    @jsii.member(jsii_name="isTimestamp")
    @builtins.classmethod
    def is_timestamp(cls, variable: builtins.str) -> "Condition":
        '''Matches if variable is a timestamp.

        :param variable: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a764190a75bb3860279e68523619998c985f6679e42555299b808244dc33216b)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
        return typing.cast("Condition", jsii.sinvoke(cls, "isTimestamp", [variable]))

    @jsii.member(jsii_name="not")
    @builtins.classmethod
    def not_(cls, condition: "Condition") -> "Condition":
        '''Negate a condition.

        :param condition: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fdbce2eae74ab8cf689e97335a1374fded9679b4fadaac4778f5b5c90c7697e)
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
        return typing.cast("Condition", jsii.sinvoke(cls, "not", [condition]))

    @jsii.member(jsii_name="numberEquals")
    @builtins.classmethod
    def number_equals(cls, variable: builtins.str, value: jsii.Number) -> "Condition":
        '''Matches if a numeric field has the given value.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8c9238ebfebfe1b3cd59b8ab67874c93bf517db63e720cc486819614e094109)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "numberEquals", [variable, value]))

    @jsii.member(jsii_name="numberEqualsJsonPath")
    @builtins.classmethod
    def number_equals_json_path(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a numeric field has the value in a given mapping path.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4dccd17b7d30ea5845ab4b8b80f1bfcd933600692e7c9a28cbf03195bb098a8)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "numberEqualsJsonPath", [variable, value]))

    @jsii.member(jsii_name="numberGreaterThan")
    @builtins.classmethod
    def number_greater_than(
        cls,
        variable: builtins.str,
        value: jsii.Number,
    ) -> "Condition":
        '''Matches if a numeric field is greater than the given value.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56b5448ac5e28537e1fcf38c074217fabe9610b96bef90f97208e83f4ee46c15)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "numberGreaterThan", [variable, value]))

    @jsii.member(jsii_name="numberGreaterThanEquals")
    @builtins.classmethod
    def number_greater_than_equals(
        cls,
        variable: builtins.str,
        value: jsii.Number,
    ) -> "Condition":
        '''Matches if a numeric field is greater than or equal to the given value.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99426e2e1e6dd99d98d3e1642519a629aed11e55112638754befd675f59699fe)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "numberGreaterThanEquals", [variable, value]))

    @jsii.member(jsii_name="numberGreaterThanEqualsJsonPath")
    @builtins.classmethod
    def number_greater_than_equals_json_path(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a numeric field is greater than or equal to the value at a given mapping path.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8928f00081b78a988b441260d48389451e38f7a5f50d2261eb26c64a336987d4)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "numberGreaterThanEqualsJsonPath", [variable, value]))

    @jsii.member(jsii_name="numberGreaterThanJsonPath")
    @builtins.classmethod
    def number_greater_than_json_path(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a numeric field is greater than the value at a given mapping path.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23a1571266826f815b9dec648bfa3b9df15bfdcba8618272c491d7cd63f8f3c6)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "numberGreaterThanJsonPath", [variable, value]))

    @jsii.member(jsii_name="numberLessThan")
    @builtins.classmethod
    def number_less_than(
        cls,
        variable: builtins.str,
        value: jsii.Number,
    ) -> "Condition":
        '''Matches if a numeric field is less than the given value.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2bf141c098364d142fce16016fb59b0ae763f9c08ba76cfb1fcb07047a6581c)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "numberLessThan", [variable, value]))

    @jsii.member(jsii_name="numberLessThanEquals")
    @builtins.classmethod
    def number_less_than_equals(
        cls,
        variable: builtins.str,
        value: jsii.Number,
    ) -> "Condition":
        '''Matches if a numeric field is less than or equal to the given value.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5b39708d63b8d650259dddbcbfd9a8054c0d83e8562eec69d0fec8db11eee39)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "numberLessThanEquals", [variable, value]))

    @jsii.member(jsii_name="numberLessThanEqualsJsonPath")
    @builtins.classmethod
    def number_less_than_equals_json_path(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a numeric field is less than or equal to the numeric value at given mapping path.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__685aae99850c6837c71e9fb83de53cc2913be4cd416ad3262bdb8ab792605ee2)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "numberLessThanEqualsJsonPath", [variable, value]))

    @jsii.member(jsii_name="numberLessThanJsonPath")
    @builtins.classmethod
    def number_less_than_json_path(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a numeric field is less than the value at the given mapping path.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1184c38cb406a885b8e77eea083d8f4f7ab3e55f31b995fcccddc36d35e31a15)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "numberLessThanJsonPath", [variable, value]))

    @jsii.member(jsii_name="or")
    @builtins.classmethod
    def or_(cls, *conditions: "Condition") -> "Condition":
        '''Combine two or more conditions with a logical OR.

        :param conditions: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d28461b310004d88b86e35b984748f50ea00ac8d6a9876feed4774997f087ac1)
            check_type(argname="argument conditions", value=conditions, expected_type=typing.Tuple[type_hints["conditions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast("Condition", jsii.sinvoke(cls, "or", [*conditions]))

    @jsii.member(jsii_name="stringEquals")
    @builtins.classmethod
    def string_equals(cls, variable: builtins.str, value: builtins.str) -> "Condition":
        '''Matches if a string field has the given value.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__140e50c821a3549bdeb3b01e2977c09fb73be78426193bd0a3cbae36b048730b)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "stringEquals", [variable, value]))

    @jsii.member(jsii_name="stringEqualsJsonPath")
    @builtins.classmethod
    def string_equals_json_path(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a string field equals to a value at a given mapping path.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e65c9e81a53480621ba56ac26965ccc6cca25adf8874ac67f8114ca6cf5459bb)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "stringEqualsJsonPath", [variable, value]))

    @jsii.member(jsii_name="stringGreaterThan")
    @builtins.classmethod
    def string_greater_than(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a string field sorts after a given value.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2344fc4ff493996fa6f0a25e52f9fec78c74e90b1879ede68f45be50674422a3)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "stringGreaterThan", [variable, value]))

    @jsii.member(jsii_name="stringGreaterThanEquals")
    @builtins.classmethod
    def string_greater_than_equals(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a string field sorts after or equal to a given value.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cdd833a815898e835edfc0e45a074b0f4520fa4b7a292f7d2e91c90b0fd4586)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "stringGreaterThanEquals", [variable, value]))

    @jsii.member(jsii_name="stringGreaterThanEqualsJsonPath")
    @builtins.classmethod
    def string_greater_than_equals_json_path(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a string field sorts after or equal to value at a given mapping path.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd93977d8ed5727d16ad880cf28a3493d243a690e911dc6a24fee7675a6fd685)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "stringGreaterThanEqualsJsonPath", [variable, value]))

    @jsii.member(jsii_name="stringGreaterThanJsonPath")
    @builtins.classmethod
    def string_greater_than_json_path(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a string field sorts after a value at a given mapping path.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3272fde18528552cc187b9f7b829b329f05e29d6a8895883fa9de73fc12b42e6)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "stringGreaterThanJsonPath", [variable, value]))

    @jsii.member(jsii_name="stringLessThan")
    @builtins.classmethod
    def string_less_than(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a string field sorts before a given value.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e4cad3d1f576720e1778bae47453adc267469f02ac3e3f9a46e6a366698c96a)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "stringLessThan", [variable, value]))

    @jsii.member(jsii_name="stringLessThanEquals")
    @builtins.classmethod
    def string_less_than_equals(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a string field sorts equal to or before a given value.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4786f81a736184b791d61305c172a346426765efe4ec906d23da96f2d65b561f)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "stringLessThanEquals", [variable, value]))

    @jsii.member(jsii_name="stringLessThanEqualsJsonPath")
    @builtins.classmethod
    def string_less_than_equals_json_path(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a string field sorts equal to or before a given mapping.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88e71b46c6af08a584bfc49701401442b025706617f2ca399b86f4abe6e15de4)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "stringLessThanEqualsJsonPath", [variable, value]))

    @jsii.member(jsii_name="stringLessThanJsonPath")
    @builtins.classmethod
    def string_less_than_json_path(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a string field sorts before a given value at a particular mapping.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e855df09fcf7265dd8097c456ab19f594817b53991438e57115aacd34db5ef0)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "stringLessThanJsonPath", [variable, value]))

    @jsii.member(jsii_name="stringMatches")
    @builtins.classmethod
    def string_matches(cls, variable: builtins.str, value: builtins.str) -> "Condition":
        '''Matches if a field matches a string pattern that can contain a wild card (*) e.g: log-*.txt or *LATEST*. No other characters other than "*" have any special meaning - * can be escaped: \\*.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb31f92b094c96f5451b5f6033dacd728484fad15409adf8317266e2281f750e)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "stringMatches", [variable, value]))

    @jsii.member(jsii_name="timestampEquals")
    @builtins.classmethod
    def timestamp_equals(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a timestamp field is the same time as the given timestamp.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce197de7a458936cce0cc36cfd2460ec6b184cb06efb79782cb9a7cbc41a1054)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "timestampEquals", [variable, value]))

    @jsii.member(jsii_name="timestampEqualsJsonPath")
    @builtins.classmethod
    def timestamp_equals_json_path(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a timestamp field is the same time as the timestamp at a given mapping path.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e291271cb939a69116d32cc91ece6eb96654e144c3d14ff121c8f32fbd2067b9)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "timestampEqualsJsonPath", [variable, value]))

    @jsii.member(jsii_name="timestampGreaterThan")
    @builtins.classmethod
    def timestamp_greater_than(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a timestamp field is after the given timestamp.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fa85b90f68b3f93b8e4fe312c52355e3c01610820898d5acea5f389efe000fe)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "timestampGreaterThan", [variable, value]))

    @jsii.member(jsii_name="timestampGreaterThanEquals")
    @builtins.classmethod
    def timestamp_greater_than_equals(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a timestamp field is after or equal to the given timestamp.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d5f7fe5170dafaadd571005d7ec016a3456b8a344083b23ce9a86c49a9ec0cc)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "timestampGreaterThanEquals", [variable, value]))

    @jsii.member(jsii_name="timestampGreaterThanEqualsJsonPath")
    @builtins.classmethod
    def timestamp_greater_than_equals_json_path(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a timestamp field is after or equal to the timestamp at a given mapping path.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd31916ec0216ca0a32d2a026600bc5d924285f6c92a2502575b9fb3a13cc797)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "timestampGreaterThanEqualsJsonPath", [variable, value]))

    @jsii.member(jsii_name="timestampGreaterThanJsonPath")
    @builtins.classmethod
    def timestamp_greater_than_json_path(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a timestamp field is after the timestamp at a given mapping path.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2681634f8150ba4016bd93b0f80b3bc295fbf92a13c522fa66248d7ea25d28c3)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "timestampGreaterThanJsonPath", [variable, value]))

    @jsii.member(jsii_name="timestampLessThan")
    @builtins.classmethod
    def timestamp_less_than(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a timestamp field is before the given timestamp.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__935865d407934ac8a88529a60186b004426b77736e9706a1e4ddabc423d4b230)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "timestampLessThan", [variable, value]))

    @jsii.member(jsii_name="timestampLessThanEquals")
    @builtins.classmethod
    def timestamp_less_than_equals(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a timestamp field is before or equal to the given timestamp.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b50ab4a6fe8e9c2c9fa9ff05fef37611e0107e6dc17e835ec10e6f685696c36)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "timestampLessThanEquals", [variable, value]))

    @jsii.member(jsii_name="timestampLessThanEqualsJsonPath")
    @builtins.classmethod
    def timestamp_less_than_equals_json_path(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a timestamp field is before or equal to the timestamp at a given mapping path.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c5cb0b5cf4b0ddbfb4d3c586cc700f5373eedc7edf8b2d24510bf4a42c96bb0)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "timestampLessThanEqualsJsonPath", [variable, value]))

    @jsii.member(jsii_name="timestampLessThanJsonPath")
    @builtins.classmethod
    def timestamp_less_than_json_path(
        cls,
        variable: builtins.str,
        value: builtins.str,
    ) -> "Condition":
        '''Matches if a timestamp field is before the timestamp at a given mapping path.

        :param variable: -
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__492e2ac4c47110465edbd94c9bc1d3e8c628faa5dfcbcf34e5b050b1c42ea1b1)
            check_type(argname="argument variable", value=variable, expected_type=type_hints["variable"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Condition", jsii.sinvoke(cls, "timestampLessThanJsonPath", [variable, value]))

    @jsii.member(jsii_name="renderCondition")
    @abc.abstractmethod
    def render_condition(self) -> typing.Any:
        '''Render Amazon States Language JSON for the condition.'''
        ...


class _ConditionProxy(Condition):
    @jsii.member(jsii_name="renderCondition")
    def render_condition(self) -> typing.Any:
        '''Render Amazon States Language JSON for the condition.'''
        return typing.cast(typing.Any, jsii.invoke(self, "renderCondition", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Condition).__jsii_proxy_class__ = lambda : _ConditionProxy


class Context(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Context"):
    '''(deprecated) Extract a field from the State Machine Context data.

    :deprecated: replaced by ``JsonPath``

    :see: https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html#wait-token-contextobject
    :stability: deprecated
    '''

    @jsii.member(jsii_name="numberAt")
    @builtins.classmethod
    def number_at(cls, path: builtins.str) -> jsii.Number:
        '''(deprecated) Instead of using a literal number, get the value from a JSON path.

        :param path: -

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc6df616362238df39334aed8314197fb36afc8a3d07502bbfeb5252aa2aa181)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast(jsii.Number, jsii.sinvoke(cls, "numberAt", [path]))

    @jsii.member(jsii_name="stringAt")
    @builtins.classmethod
    def string_at(cls, path: builtins.str) -> builtins.str:
        '''(deprecated) Instead of using a literal string, get the value from a JSON path.

        :param path: -

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c37a205138cda7efd0dd9e16607caa79043b33384d2575c501f01fd0695b6162)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "stringAt", [path]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="entireContext")
    def entire_context(cls) -> builtins.str:
        '''(deprecated) Use the entire context data structure.

        Will be an object at invocation time, but is represented in the CDK
        application as a string.

        :stability: deprecated
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "entireContext"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="taskToken")
    def task_token(cls) -> builtins.str:
        '''(deprecated) Return the Task Token field.

        External actions will need this token to report step completion
        back to StepFunctions using the ``SendTaskSuccess`` or ``SendTaskFailure``
        calls.

        :stability: deprecated
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "taskToken"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.CustomStateProps",
    jsii_struct_bases=[],
    name_mapping={"state_json": "stateJson"},
)
class CustomStateProps:
    def __init__(self, *, state_json: typing.Mapping[builtins.str, typing.Any]) -> None:
        '''Properties for defining a custom state definition.

        :param state_json: Amazon States Language (JSON-based) definition of the state.

        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_dynamodb as dynamodb
            
            
            # create a table
            table = dynamodb.Table(self, "montable",
                partition_key=dynamodb.Attribute(
                    name="id",
                    type=dynamodb.AttributeType.STRING
                )
            )
            
            final_status = sfn.Pass(self, "final step")
            
            # States language JSON to put an item into DynamoDB
            # snippet generated from https://docs.aws.amazon.com/step-functions/latest/dg/tutorial-code-snippet.html#tutorial-code-snippet-1
            state_json = {
                "Type": "Task",
                "Resource": "arn:aws:states:::dynamodb:putItem",
                "Parameters": {
                    "TableName": table.table_name,
                    "Item": {
                        "id": {
                            "S": "MyEntry"
                        }
                    }
                },
                "ResultPath": null
            }
            
            # custom state which represents a task to insert data into DynamoDB
            custom = sfn.CustomState(self, "my custom task",
                state_json=state_json
            )
            
            chain = sfn.Chain.start(custom).next(final_status)
            
            sm = sfn.StateMachine(self, "StateMachine",
                definition=chain,
                timeout=Duration.seconds(30)
            )
            
            # don't forget permissions. You need to assign them
            table.grant_write_data(sm)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47008dcfc587f854ee4c4c8484d56c7fc1f442a411b716570167e9d0fc78404a)
            check_type(argname="argument state_json", value=state_json, expected_type=type_hints["state_json"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "state_json": state_json,
        }

    @builtins.property
    def state_json(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''Amazon States Language (JSON-based) definition of the state.

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html
        '''
        result = self._values.get("state_json")
        assert result is not None, "Required property 'state_json' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomStateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Data(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Data"):
    '''(deprecated) Extract a field from the State Machine data that gets passed around between states.

    :deprecated: replaced by ``JsonPath``

    :stability: deprecated
    '''

    @jsii.member(jsii_name="isJsonPathString")
    @builtins.classmethod
    def is_json_path_string(cls, value: builtins.str) -> builtins.bool:
        '''(deprecated) Determines if the indicated string is an encoded JSON path.

        :param value: string to be evaluated.

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__466992e0508b766c06020ed286de685f37498f173338f4bb07a7764eabd27778)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(builtins.bool, jsii.sinvoke(cls, "isJsonPathString", [value]))

    @jsii.member(jsii_name="listAt")
    @builtins.classmethod
    def list_at(cls, path: builtins.str) -> typing.List[builtins.str]:
        '''(deprecated) Instead of using a literal string list, get the value from a JSON path.

        :param path: -

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e720ecfc18202b38e20c2af0b033d68c13bbaa6734a147ac4f0330324420ef33)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast(typing.List[builtins.str], jsii.sinvoke(cls, "listAt", [path]))

    @jsii.member(jsii_name="numberAt")
    @builtins.classmethod
    def number_at(cls, path: builtins.str) -> jsii.Number:
        '''(deprecated) Instead of using a literal number, get the value from a JSON path.

        :param path: -

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17d2d6b1e33da7249c82522a97ce8460fd91a6788b5040f31cc2731a86e4b69e)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast(jsii.Number, jsii.sinvoke(cls, "numberAt", [path]))

    @jsii.member(jsii_name="stringAt")
    @builtins.classmethod
    def string_at(cls, path: builtins.str) -> builtins.str:
        '''(deprecated) Instead of using a literal string, get the value from a JSON path.

        :param path: -

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80b2171dbfedcd0f337cc62a273889146a3674a6290395ada81aea0089bcb794)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "stringAt", [path]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="entirePayload")
    def entire_payload(cls) -> builtins.str:
        '''(deprecated) Use the entire data structure.

        Will be an object at invocation time, but is represented in the CDK
        application as a string.

        :stability: deprecated
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "entirePayload"))


class Errors(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Errors"):
    '''Predefined error strings Error names in Amazon States Language - https://states-language.net/spec.html#appendix-a Error handling in Step Functions - https://docs.aws.amazon.com/step-functions/latest/dg/concepts-error-handling.html.

    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_stepfunctions as stepfunctions
        
        errors = stepfunctions.Errors()
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.python.classproperty
    @jsii.member(jsii_name="ALL")
    def ALL(cls) -> builtins.str:
        '''Matches any Error.'''
        return typing.cast(builtins.str, jsii.sget(cls, "ALL"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="BRANCH_FAILED")
    def BRANCH_FAILED(cls) -> builtins.str:
        '''A branch of a Parallel state failed.'''
        return typing.cast(builtins.str, jsii.sget(cls, "BRANCH_FAILED"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HEARTBEAT_TIMEOUT")
    def HEARTBEAT_TIMEOUT(cls) -> builtins.str:
        '''A Task State failed to heartbeat for a time longer than the “HeartbeatSeconds” value.'''
        return typing.cast(builtins.str, jsii.sget(cls, "HEARTBEAT_TIMEOUT"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="NO_CHOICE_MATCHED")
    def NO_CHOICE_MATCHED(cls) -> builtins.str:
        '''A Choice state failed to find a match for the condition field extracted from its input.'''
        return typing.cast(builtins.str, jsii.sget(cls, "NO_CHOICE_MATCHED"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PARAMETER_PATH_FAILURE")
    def PARAMETER_PATH_FAILURE(cls) -> builtins.str:
        '''Within a state’s “Parameters” field, the attempt to replace a field whose name ends in “.$” using a Path failed.'''
        return typing.cast(builtins.str, jsii.sget(cls, "PARAMETER_PATH_FAILURE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PERMISSIONS")
    def PERMISSIONS(cls) -> builtins.str:
        '''A Task State failed because it had insufficient privileges to execute the specified code.'''
        return typing.cast(builtins.str, jsii.sget(cls, "PERMISSIONS"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="RESULT_PATH_MATCH_FAILURE")
    def RESULT_PATH_MATCH_FAILURE(cls) -> builtins.str:
        '''A Task State’s “ResultPath” field cannot be applied to the input the state received.'''
        return typing.cast(builtins.str, jsii.sget(cls, "RESULT_PATH_MATCH_FAILURE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="TASKS_FAILED")
    def TASKS_FAILED(cls) -> builtins.str:
        '''A Task State failed during the execution.'''
        return typing.cast(builtins.str, jsii.sget(cls, "TASKS_FAILED"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="TIMEOUT")
    def TIMEOUT(cls) -> builtins.str:
        '''A Task State either ran longer than the “TimeoutSeconds” value, or failed to heartbeat for a time longer than the “HeartbeatSeconds” value.'''
        return typing.cast(builtins.str, jsii.sget(cls, "TIMEOUT"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.FailProps",
    jsii_struct_bases=[],
    name_mapping={"cause": "cause", "comment": "comment", "error": "error"},
)
class FailProps:
    def __init__(
        self,
        *,
        cause: typing.Optional[builtins.str] = None,
        comment: typing.Optional[builtins.str] = None,
        error: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a Fail state.

        :param cause: A description for the cause of the failure. Default: No description
        :param comment: An optional description for this state. Default: No comment
        :param error: Error code used to represent this failure. Default: No error code

        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_lambda as lambda_
            
            # submit_lambda: lambda.Function
            # get_status_lambda: lambda.Function
            
            
            submit_job = tasks.LambdaInvoke(self, "Submit Job",
                lambda_function=submit_lambda,
                # Lambda's result is in the attribute `Payload`
                output_path="$.Payload"
            )
            
            wait_x = sfn.Wait(self, "Wait X Seconds",
                time=sfn.WaitTime.seconds_path("$.waitSeconds")
            )
            
            get_status = tasks.LambdaInvoke(self, "Get Job Status",
                lambda_function=get_status_lambda,
                # Pass just the field named "guid" into the Lambda, put the
                # Lambda's result in a field called "status" in the response
                input_path="$.guid",
                output_path="$.Payload"
            )
            
            job_failed = sfn.Fail(self, "Job Failed",
                cause="AWS Batch Job Failed",
                error="DescribeJob returned FAILED"
            )
            
            final_status = tasks.LambdaInvoke(self, "Get Final Job Status",
                lambda_function=get_status_lambda,
                # Use "guid" field as input
                input_path="$.guid",
                output_path="$.Payload"
            )
            
            definition = submit_job.next(wait_x).next(get_status).next(sfn.Choice(self, "Job Complete?").when(sfn.Condition.string_equals("$.status", "FAILED"), job_failed).when(sfn.Condition.string_equals("$.status", "SUCCEEDED"), final_status).otherwise(wait_x))
            
            sfn.StateMachine(self, "StateMachine",
                definition=definition,
                timeout=Duration.minutes(5)
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f82f2dad8c2c44ee04900835f7a93152954dd2a339b3da1e1ee8e7089d045fb1)
            check_type(argname="argument cause", value=cause, expected_type=type_hints["cause"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument error", value=error, expected_type=type_hints["error"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cause is not None:
            self._values["cause"] = cause
        if comment is not None:
            self._values["comment"] = comment
        if error is not None:
            self._values["error"] = error

    @builtins.property
    def cause(self) -> typing.Optional[builtins.str]:
        '''A description for the cause of the failure.

        :default: No description
        '''
        result = self._values.get("cause")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def error(self) -> typing.Optional[builtins.str]:
        '''Error code used to represent this failure.

        :default: No error code
        '''
        result = self._values.get("error")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FailProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FieldUtils(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-stepfunctions.FieldUtils",
):
    '''Helper functions to work with structures containing fields.'''

    @jsii.member(jsii_name="containsTaskToken")
    @builtins.classmethod
    def contains_task_token(
        cls,
        obj: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> builtins.bool:
        '''Returns whether the given task structure contains the TaskToken field anywhere.

        The field is considered included if the field itself or one of its containing
        fields occurs anywhere in the payload.

        :param obj: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7472ad39e29c280b40db4eab2f3bf9fa554aae258c6c1959684cb3e40a3e9ac4)
            check_type(argname="argument obj", value=obj, expected_type=type_hints["obj"])
        return typing.cast(builtins.bool, jsii.sinvoke(cls, "containsTaskToken", [obj]))

    @jsii.member(jsii_name="findReferencedPaths")
    @builtins.classmethod
    def find_referenced_paths(
        cls,
        obj: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> typing.List[builtins.str]:
        '''Return all JSON paths used in the given structure.

        :param obj: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddd02194b98b807de20c0986b722ea035aa368f507f80a461566ee2a2e9f6378)
            check_type(argname="argument obj", value=obj, expected_type=type_hints["obj"])
        return typing.cast(typing.List[builtins.str], jsii.sinvoke(cls, "findReferencedPaths", [obj]))

    @jsii.member(jsii_name="renderObject")
    @builtins.classmethod
    def render_object(
        cls,
        obj: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Render a JSON structure containing fields to the right StepFunctions structure.

        :param obj: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66c5ea1d3b7b006661c3d7719a887cfab6680bfa9afe2cc3b582e0b0c995a6e0)
            check_type(argname="argument obj", value=obj, expected_type=type_hints["obj"])
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], jsii.sinvoke(cls, "renderObject", [obj]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.FindStateOptions",
    jsii_struct_bases=[],
    name_mapping={"include_error_handlers": "includeErrorHandlers"},
)
class FindStateOptions:
    def __init__(
        self,
        *,
        include_error_handlers: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Options for finding reachable states.

        :param include_error_handlers: Whether or not to follow error-handling transitions. Default: false

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_stepfunctions as stepfunctions
            
            find_state_options = stepfunctions.FindStateOptions(
                include_error_handlers=False
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3bbbdc9dbd3d4e0970819dcfe1b8c1bc7dc4b3479f5e82b17feb628d43e01be)
            check_type(argname="argument include_error_handlers", value=include_error_handlers, expected_type=type_hints["include_error_handlers"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if include_error_handlers is not None:
            self._values["include_error_handlers"] = include_error_handlers

    @builtins.property
    def include_error_handlers(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to follow error-handling transitions.

        :default: false
        '''
        result = self._values.get("include_error_handlers")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FindStateOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-stepfunctions.IActivity")
class IActivity(_aws_cdk_core_f4b25747.IResource, typing_extensions.Protocol):
    '''Represents a Step Functions Activity https://docs.aws.amazon.com/step-functions/latest/dg/concepts-activities.html.'''

    @builtins.property
    @jsii.member(jsii_name="activityArn")
    def activity_arn(self) -> builtins.str:
        '''The ARN of the activity.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="activityName")
    def activity_name(self) -> builtins.str:
        '''The name of the activity.

        :attribute: true
        '''
        ...


class _IActivityProxy(
    jsii.proxy_for(_aws_cdk_core_f4b25747.IResource), # type: ignore[misc]
):
    '''Represents a Step Functions Activity https://docs.aws.amazon.com/step-functions/latest/dg/concepts-activities.html.'''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-stepfunctions.IActivity"

    @builtins.property
    @jsii.member(jsii_name="activityArn")
    def activity_arn(self) -> builtins.str:
        '''The ARN of the activity.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "activityArn"))

    @builtins.property
    @jsii.member(jsii_name="activityName")
    def activity_name(self) -> builtins.str:
        '''The name of the activity.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "activityName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IActivity).__jsii_proxy_class__ = lambda : _IActivityProxy


@jsii.interface(jsii_type="@aws-cdk/aws-stepfunctions.IChainable")
class IChainable(typing_extensions.Protocol):
    '''Interface for objects that can be used in a Chain.'''

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List["INextable"]:
        '''The chainable end state(s) of this chainable.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''Descriptive identifier for this chainable.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> "State":
        '''The start state of this chainable.'''
        ...


class _IChainableProxy:
    '''Interface for objects that can be used in a Chain.'''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-stepfunctions.IChainable"

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List["INextable"]:
        '''The chainable end state(s) of this chainable.'''
        return typing.cast(typing.List["INextable"], jsii.get(self, "endStates"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''Descriptive identifier for this chainable.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> "State":
        '''The start state of this chainable.'''
        return typing.cast("State", jsii.get(self, "startState"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IChainable).__jsii_proxy_class__ = lambda : _IChainableProxy


@jsii.interface(jsii_type="@aws-cdk/aws-stepfunctions.INextable")
class INextable(typing_extensions.Protocol):
    '''Interface for states that can have 'next' states.'''

    @jsii.member(jsii_name="next")
    def next(self, state: IChainable) -> "Chain":
        '''Go to the indicated state after this state.

        :param state: -

        :return: The chain of states built up
        '''
        ...


class _INextableProxy:
    '''Interface for states that can have 'next' states.'''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-stepfunctions.INextable"

    @jsii.member(jsii_name="next")
    def next(self, state: IChainable) -> "Chain":
        '''Go to the indicated state after this state.

        :param state: -

        :return: The chain of states built up
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cd66ae7ffed33d53cb60ef45d1c95defeaa5ca4477ef8e2b9afe15bbcbdac22)
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
        return typing.cast("Chain", jsii.invoke(self, "next", [state]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INextable).__jsii_proxy_class__ = lambda : _INextableProxy


@jsii.interface(jsii_type="@aws-cdk/aws-stepfunctions.IStateMachine")
class IStateMachine(
    _aws_cdk_core_f4b25747.IResource,
    _aws_cdk_aws_iam_940a1ce0.IGrantable,
    typing_extensions.Protocol,
):
    '''A State Machine.'''

    @builtins.property
    @jsii.member(jsii_name="stateMachineArn")
    def state_machine_arn(self) -> builtins.str:
        '''The ARN of the state machine.

        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity custom permissions.

        :param identity: The principal.
        :param actions: The list of desired actions.
        '''
        ...

    @jsii.member(jsii_name="grantExecution")
    def grant_execution(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions for all executions of a state machine.

        :param identity: The principal.
        :param actions: The list of desired actions.
        '''
        ...

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity read permissions for this state machine.

        :param identity: The principal.
        '''
        ...

    @jsii.member(jsii_name="grantStartExecution")
    def grant_start_execution(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions to start an execution of this state machine.

        :param identity: The principal.
        '''
        ...

    @jsii.member(jsii_name="grantStartSyncExecution")
    def grant_start_sync_execution(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions to start a synchronous execution of this state machine.

        :param identity: The principal.
        '''
        ...

    @jsii.member(jsii_name="grantTaskResponse")
    def grant_task_response(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity read permissions for this state machine.

        :param identity: The principal.
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
        '''Return the given named metric for this State Machine's executions.

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

        :default: - sum over 5 minutes
        '''
        ...

    @jsii.member(jsii_name="metricAborted")
    def metric_aborted(
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
        '''Metric for the number of executions that were aborted.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
        '''
        ...

    @jsii.member(jsii_name="metricFailed")
    def metric_failed(
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
        '''Metric for the number of executions that failed.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
        '''
        ...

    @jsii.member(jsii_name="metricStarted")
    def metric_started(
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
        '''Metric for the number of executions that were started.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
        '''
        ...

    @jsii.member(jsii_name="metricSucceeded")
    def metric_succeeded(
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
        '''Metric for the number of executions that succeeded.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
        '''
        ...

    @jsii.member(jsii_name="metricThrottled")
    def metric_throttled(
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
        '''Metric for the number of executions that were throttled.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: sum over 5 minutes
        '''
        ...

    @jsii.member(jsii_name="metricTime")
    def metric_time(
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
        '''Metric for the interval, in milliseconds, between the time the execution starts and the time it closes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
        '''
        ...

    @jsii.member(jsii_name="metricTimedOut")
    def metric_timed_out(
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
        '''Metric for the number of executions that timed out.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
        '''
        ...


class _IStateMachineProxy(
    jsii.proxy_for(_aws_cdk_core_f4b25747.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_iam_940a1ce0.IGrantable), # type: ignore[misc]
):
    '''A State Machine.'''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-stepfunctions.IStateMachine"

    @builtins.property
    @jsii.member(jsii_name="stateMachineArn")
    def state_machine_arn(self) -> builtins.str:
        '''The ARN of the state machine.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "stateMachineArn"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity custom permissions.

        :param identity: The principal.
        :param actions: The list of desired actions.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f83791493be07978d4568471f3c183643331418a1d3495695b63a75c023aa313)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grant", [identity, *actions]))

    @jsii.member(jsii_name="grantExecution")
    def grant_execution(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions for all executions of a state machine.

        :param identity: The principal.
        :param actions: The list of desired actions.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57a722334637b941ba88641e6a95aa8dfda92a28698c1de76e1c1a395c3d1320)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantExecution", [identity, *actions]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity read permissions for this state machine.

        :param identity: The principal.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7541f1db2bd37683f41440acbd42d3c37bd9e7d198b73afac06100152dd64953)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantRead", [identity]))

    @jsii.member(jsii_name="grantStartExecution")
    def grant_start_execution(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions to start an execution of this state machine.

        :param identity: The principal.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0ea8e618e5162ef265b781ff0c6201fb8f39582c8cf5e4a52015f250c9dd94e)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantStartExecution", [identity]))

    @jsii.member(jsii_name="grantStartSyncExecution")
    def grant_start_sync_execution(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions to start a synchronous execution of this state machine.

        :param identity: The principal.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d2f3ed5371fc7db794547514f9190b733da7c96c2065307c83802e74cc19187)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantStartSyncExecution", [identity]))

    @jsii.member(jsii_name="grantTaskResponse")
    def grant_task_response(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity read permissions for this state machine.

        :param identity: The principal.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c963c1e5223549d332c8a816c2b1c94cd470f6c87fcaff397a3391796147820)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantTaskResponse", [identity]))

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
        '''Return the given named metric for this State Machine's executions.

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

        :default: - sum over 5 minutes
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__441797ee9418d63382380590bca8ca858817a4db752fb104833880e2557cd748)
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

    @jsii.member(jsii_name="metricAborted")
    def metric_aborted(
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
        '''Metric for the number of executions that were aborted.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricAborted", [props]))

    @jsii.member(jsii_name="metricFailed")
    def metric_failed(
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
        '''Metric for the number of executions that failed.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricFailed", [props]))

    @jsii.member(jsii_name="metricStarted")
    def metric_started(
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
        '''Metric for the number of executions that were started.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricStarted", [props]))

    @jsii.member(jsii_name="metricSucceeded")
    def metric_succeeded(
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
        '''Metric for the number of executions that succeeded.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricSucceeded", [props]))

    @jsii.member(jsii_name="metricThrottled")
    def metric_throttled(
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
        '''Metric for the number of executions that were throttled.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricThrottled", [props]))

    @jsii.member(jsii_name="metricTime")
    def metric_time(
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
        '''Metric for the interval, in milliseconds, between the time the execution starts and the time it closes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricTime", [props]))

    @jsii.member(jsii_name="metricTimedOut")
    def metric_timed_out(
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
        '''Metric for the number of executions that timed out.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricTimedOut", [props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStateMachine).__jsii_proxy_class__ = lambda : _IStateMachineProxy


@jsii.interface(jsii_type="@aws-cdk/aws-stepfunctions.IStepFunctionsTask")
class IStepFunctionsTask(typing_extensions.Protocol):
    '''(deprecated) Interface for resources that can be used as tasks.

    :deprecated: replaced by ``TaskStateBase``.

    :stability: deprecated
    '''

    @jsii.member(jsii_name="bind")
    def bind(self, task: "Task") -> "StepFunctionsTaskConfig":
        '''(deprecated) Called when the task object is used in a workflow.

        :param task: -

        :stability: deprecated
        '''
        ...


class _IStepFunctionsTaskProxy:
    '''(deprecated) Interface for resources that can be used as tasks.

    :deprecated: replaced by ``TaskStateBase``.

    :stability: deprecated
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-stepfunctions.IStepFunctionsTask"

    @jsii.member(jsii_name="bind")
    def bind(self, task: "Task") -> "StepFunctionsTaskConfig":
        '''(deprecated) Called when the task object is used in a workflow.

        :param task: -

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b6b02e7716ea28280ed50b95f76b7f85fab123cb2420e9df34fb77de5f17d30)
            check_type(argname="argument task", value=task, expected_type=type_hints["task"])
        return typing.cast("StepFunctionsTaskConfig", jsii.invoke(self, "bind", [task]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStepFunctionsTask).__jsii_proxy_class__ = lambda : _IStepFunctionsTaskProxy


@jsii.enum(jsii_type="@aws-cdk/aws-stepfunctions.InputType")
class InputType(enum.Enum):
    '''The type of task input.'''

    TEXT = "TEXT"
    '''Use a literal string This might be a JSON-encoded object, or just text.

    valid JSON text: standalone, quote-delimited strings; objects; arrays; numbers; Boolean values; and null.

    example: ``literal string``
    example: {"json": "encoded"}
    '''
    OBJECT = "OBJECT"
    '''Use an object which may contain Data and Context fields as object values, if desired.

    example:
    {
    literal: 'literal',
    SomeInput: sfn.JsonPath.stringAt('$.someField')
    }

    :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-contextobject.html
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-stepfunctions.IntegrationPattern")
class IntegrationPattern(enum.Enum):
    '''AWS Step Functions integrates with services directly in the Amazon States Language.

    You can control these AWS services using service integration patterns:

    :see: https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html
    :exampleMetadata: infused

    Example::

        # Define a state machine with one Pass state
        child = sfn.StateMachine(self, "ChildStateMachine",
            definition=sfn.Chain.start(sfn.Pass(self, "PassState"))
        )
        
        # Include the state machine in a Task state with callback pattern
        task = tasks.StepFunctionsStartExecution(self, "ChildTask",
            state_machine=child,
            integration_pattern=sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
            input=sfn.TaskInput.from_object({
                "token": sfn.JsonPath.task_token,
                "foo": "bar"
            }),
            name="MyExecutionName"
        )
        
        # Define a second state machine with the Task state above
        sfn.StateMachine(self, "ParentStateMachine",
            definition=task
        )
    '''

    REQUEST_RESPONSE = "REQUEST_RESPONSE"
    '''Step Functions will wait for an HTTP response and then progress to the next state.

    :see: https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html#connect-default
    '''
    RUN_JOB = "RUN_JOB"
    '''Step Functions can wait for a request to complete before progressing to the next state.

    :see: https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html#connect-sync
    '''
    WAIT_FOR_TASK_TOKEN = "WAIT_FOR_TASK_TOKEN"
    '''Callback tasks provide a way to pause a workflow until a task token is returned.

    You must set a task token when using the callback pattern

    :see: https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html#connect-wait-token
    '''


class JsonPath(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-stepfunctions.JsonPath",
):
    '''Extract a field from the State Machine data or context that gets passed around between states.

    :see: https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-paths.html
    :exampleMetadata: infused

    Example::

        # fn: lambda.Function
        
        tasks.LambdaInvoke(self, "Invoke Handler",
            lambda_function=fn,
            result_selector={
                "lambda_output": sfn.JsonPath.string_at("$.Payload"),
                "invoke_request_id": sfn.JsonPath.string_at("$.SdkResponseMetadata.RequestId"),
                "static_value": {
                    "foo": "bar"
                },
                "state_name": sfn.JsonPath.string_at("$.State.Name")
            }
        )
    '''

    @jsii.member(jsii_name="array")
    @builtins.classmethod
    def array(cls, *values: builtins.str) -> builtins.str:
        '''Make an intrinsic States.Array expression.

        Combine any number of string literals or JsonPath expressions into an array.

        Use this function if the value of an array element directly has to come
        from a JSON Path expression (either the State object or the Context object).

        If the array contains object literals whose values come from a JSON path
        expression, you do not need to use this function.

        :param values: -

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-intrinsic-functions.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b60eec9d0633867d222ec9d16d97005745274460045cf11f01e3f694765ec3cf)
            check_type(argname="argument values", value=values, expected_type=typing.Tuple[type_hints["values"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(builtins.str, jsii.sinvoke(cls, "array", [*values]))

    @jsii.member(jsii_name="format")
    @builtins.classmethod
    def format(cls, format_string: builtins.str, *values: builtins.str) -> builtins.str:
        '''Make an intrinsic States.Format expression.

        This can be used to embed JSON Path variables inside a format string.

        For example::

           sfn.JsonPath.format("Hello, my name is {}.", sfn.JsonPath.string_at("$.name"))

        :param format_string: -
        :param values: -

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-intrinsic-functions.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77414a915b6127df4c7e351e8fdec16deeb41cc0cbea5c601e85b939a9c5a8a9)
            check_type(argname="argument format_string", value=format_string, expected_type=type_hints["format_string"])
            check_type(argname="argument values", value=values, expected_type=typing.Tuple[type_hints["values"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(builtins.str, jsii.sinvoke(cls, "format", [format_string, *values]))

    @jsii.member(jsii_name="isEncodedJsonPath")
    @builtins.classmethod
    def is_encoded_json_path(cls, value: builtins.str) -> builtins.bool:
        '''Determines if the indicated string is an encoded JSON path.

        :param value: string to be evaluated.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a4ea9e93d3a9719a0624159e3fc66a0228ac660d4cc7f2f25978ecf07bfbad0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(builtins.bool, jsii.sinvoke(cls, "isEncodedJsonPath", [value]))

    @jsii.member(jsii_name="jsonToString")
    @builtins.classmethod
    def json_to_string(cls, value: typing.Any) -> builtins.str:
        '''Make an intrinsic States.JsonToString expression.

        During the execution of the Step Functions state machine, encode the
        given object into a JSON string.

        For example::

           sfn.JsonPath.json_to_string(sfn.JsonPath.object_at("$.someObject"))

        :param value: -

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-intrinsic-functions.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2ab1f7f44fa9fa5e2471eaad36ec7d72d613cc9f378a0377c6b68d6a8ba8a59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "jsonToString", [value]))

    @jsii.member(jsii_name="listAt")
    @builtins.classmethod
    def list_at(cls, path: builtins.str) -> typing.List[builtins.str]:
        '''Instead of using a literal string list, get the value from a JSON path.

        :param path: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6df36a26e3c7810007dcd0bfd1db214b5e21960e450bd3f7b8ef8cc7dd24044)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast(typing.List[builtins.str], jsii.sinvoke(cls, "listAt", [path]))

    @jsii.member(jsii_name="numberAt")
    @builtins.classmethod
    def number_at(cls, path: builtins.str) -> jsii.Number:
        '''Instead of using a literal number, get the value from a JSON path.

        :param path: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25c9bb3baa05d0415e8ab2560c3ea7dd7a0ee5e54c3f86c28272fbdb2e1e094b)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast(jsii.Number, jsii.sinvoke(cls, "numberAt", [path]))

    @jsii.member(jsii_name="objectAt")
    @builtins.classmethod
    def object_at(cls, path: builtins.str) -> _aws_cdk_core_f4b25747.IResolvable:
        '''Reference a complete (complex) object in a JSON path location.

        :param path: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5799b4c6f1bf4447939ce76961b4c026a26644c564109a7c1c3f91a89f8116f7)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast(_aws_cdk_core_f4b25747.IResolvable, jsii.sinvoke(cls, "objectAt", [path]))

    @jsii.member(jsii_name="stringAt")
    @builtins.classmethod
    def string_at(cls, path: builtins.str) -> builtins.str:
        '''Instead of using a literal string, get the value from a JSON path.

        :param path: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2e6bd7868e6003fa337e98685b6c06613eecf32428ad050e4b7a7f109b2b1bc)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "stringAt", [path]))

    @jsii.member(jsii_name="stringToJson")
    @builtins.classmethod
    def string_to_json(
        cls,
        json_string: builtins.str,
    ) -> _aws_cdk_core_f4b25747.IResolvable:
        '''Make an intrinsic States.StringToJson expression.

        During the execution of the Step Functions state machine, parse the given
        argument as JSON into its object form.

        For example::

           sfn.JsonPath.string_to_json(sfn.JsonPath.string_at("$.someJsonBody"))

        :param json_string: -

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-intrinsic-functions.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c896a93910d194a5666b8796d918ccec322b78905d52ded7558bff3c405dcaa)
            check_type(argname="argument json_string", value=json_string, expected_type=type_hints["json_string"])
        return typing.cast(_aws_cdk_core_f4b25747.IResolvable, jsii.sinvoke(cls, "stringToJson", [json_string]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DISCARD")
    def DISCARD(cls) -> builtins.str:
        '''Special string value to discard state input, output or result.'''
        return typing.cast(builtins.str, jsii.sget(cls, "DISCARD"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="entireContext")
    def entire_context(cls) -> builtins.str:
        '''Use the entire context data structure.

        Will be an object at invocation time, but is represented in the CDK
        application as a string.
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "entireContext"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="entirePayload")
    def entire_payload(cls) -> builtins.str:
        '''Use the entire data structure.

        Will be an object at invocation time, but is represented in the CDK
        application as a string.
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "entirePayload"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="taskToken")
    def task_token(cls) -> builtins.str:
        '''Return the Task Token field.

        External actions will need this token to report step completion
        back to StepFunctions using the ``SendTaskSuccess`` or ``SendTaskFailure``
        calls.
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "taskToken"))


@jsii.enum(jsii_type="@aws-cdk/aws-stepfunctions.LogLevel")
class LogLevel(enum.Enum):
    '''Defines which category of execution history events are logged.

    :default: ERROR

    :see: https://docs.aws.amazon.com/step-functions/latest/dg/cloudwatch-log-level.html
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_logs as logs
        
        
        log_group = logs.LogGroup(self, "MyLogGroup")
        
        sfn.StateMachine(self, "MyStateMachine",
            definition=sfn.Chain.start(sfn.Pass(self, "Pass")),
            logs=sfn.LogOptions(
                destination=log_group,
                level=sfn.LogLevel.ALL
            )
        )
    '''

    OFF = "OFF"
    '''No Logging.'''
    ALL = "ALL"
    '''Log everything.'''
    ERROR = "ERROR"
    '''Log all errors.'''
    FATAL = "FATAL"
    '''Log fatal errors.'''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.LogOptions",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "include_execution_data": "includeExecutionData",
        "level": "level",
    },
)
class LogOptions:
    def __init__(
        self,
        *,
        destination: _aws_cdk_aws_logs_6c4320fb.ILogGroup,
        include_execution_data: typing.Optional[builtins.bool] = None,
        level: typing.Optional[LogLevel] = None,
    ) -> None:
        '''Defines what execution history events are logged and where they are logged.

        :param destination: The log group where the execution history events will be logged.
        :param include_execution_data: Determines whether execution data is included in your log. Default: false
        :param level: Defines which category of execution history events are logged. Default: ERROR

        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_logs as logs
            
            
            log_group = logs.LogGroup(self, "MyLogGroup")
            
            sfn.StateMachine(self, "MyStateMachine",
                definition=sfn.Chain.start(sfn.Pass(self, "Pass")),
                logs=sfn.LogOptions(
                    destination=log_group,
                    level=sfn.LogLevel.ALL
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb6986109f7c3279d658ab4e4a2f828a9d23dbf64a38c1bc29d92ff1f0519d95)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument include_execution_data", value=include_execution_data, expected_type=type_hints["include_execution_data"])
            check_type(argname="argument level", value=level, expected_type=type_hints["level"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
        }
        if include_execution_data is not None:
            self._values["include_execution_data"] = include_execution_data
        if level is not None:
            self._values["level"] = level

    @builtins.property
    def destination(self) -> _aws_cdk_aws_logs_6c4320fb.ILogGroup:
        '''The log group where the execution history events will be logged.'''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(_aws_cdk_aws_logs_6c4320fb.ILogGroup, result)

    @builtins.property
    def include_execution_data(self) -> typing.Optional[builtins.bool]:
        '''Determines whether execution data is included in your log.

        :default: false
        '''
        result = self._values.get("include_execution_data")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def level(self) -> typing.Optional[LogLevel]:
        '''Defines which category of execution history events are logged.

        :default: ERROR
        '''
        result = self._values.get("level")
        return typing.cast(typing.Optional[LogLevel], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LogOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.MapProps",
    jsii_struct_bases=[],
    name_mapping={
        "comment": "comment",
        "input_path": "inputPath",
        "items_path": "itemsPath",
        "max_concurrency": "maxConcurrency",
        "output_path": "outputPath",
        "parameters": "parameters",
        "result_path": "resultPath",
        "result_selector": "resultSelector",
    },
)
class MapProps:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        items_path: typing.Optional[builtins.str] = None,
        max_concurrency: typing.Optional[jsii.Number] = None,
        output_path: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''Properties for defining a Map state.

        :param comment: An optional description for this state. Default: No comment
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param items_path: JSONPath expression to select the array to iterate over. Default: $
        :param max_concurrency: MaxConcurrency. An upper bound on the number of iterations you want running at once. Default: - full concurrency
        :param output_path: JSONPath expression to select part of the state to be the output to this state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: $
        :param parameters: The JSON that you want to override your default iteration input. Default: $
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: $
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None

        :exampleMetadata: infused

        Example::

            map = sfn.Map(self, "Map State",
                max_concurrency=1,
                items_path=sfn.JsonPath.string_at("$.inputForMap")
            )
            map.iterator(sfn.Pass(self, "Pass State"))
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8acc8562ebaf5dc229e8f97fd9bf41e777bd7dac23e5dd66b5485f043e09e766)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument items_path", value=items_path, expected_type=type_hints["items_path"])
            check_type(argname="argument max_concurrency", value=max_concurrency, expected_type=type_hints["max_concurrency"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument result_path", value=result_path, expected_type=type_hints["result_path"])
            check_type(argname="argument result_selector", value=result_selector, expected_type=type_hints["result_selector"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if input_path is not None:
            self._values["input_path"] = input_path
        if items_path is not None:
            self._values["items_path"] = items_path
        if max_concurrency is not None:
            self._values["max_concurrency"] = max_concurrency
        if output_path is not None:
            self._values["output_path"] = output_path
        if parameters is not None:
            self._values["parameters"] = parameters
        if result_path is not None:
            self._values["result_path"] = result_path
        if result_selector is not None:
            self._values["result_selector"] = result_selector

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the input to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: $
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def items_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select the array to iterate over.

        :default: $
        '''
        result = self._values.get("items_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_concurrency(self) -> typing.Optional[jsii.Number]:
        '''MaxConcurrency.

        An upper bound on the number of iterations you want running at once.

        :default: - full concurrency
        '''
        result = self._values.get("max_concurrency")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the output to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        output to be the empty object {}.

        :default: $
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The JSON that you want to override your default iteration input.

        :default: $
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def result_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to indicate where to inject the state's output.

        May also be the special value JsonPath.DISCARD, which will cause the state's
        input to become its output.

        :default: $
        '''
        result = self._values.get("result_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_selector(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The JSON that will replace the state's raw result and become the effective result before ResultPath is applied.

        You can use ResultSelector to create a payload with values that are static
        or selected from the state's raw result.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-resultselector
        '''
        result = self._values.get("result_selector")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MapProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.ParallelProps",
    jsii_struct_bases=[],
    name_mapping={
        "comment": "comment",
        "input_path": "inputPath",
        "output_path": "outputPath",
        "result_path": "resultPath",
        "result_selector": "resultSelector",
    },
)
class ParallelProps:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''Properties for defining a Parallel state.

        :param comment: An optional description for this state. Default: No comment
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param output_path: JSONPath expression to select part of the state to be the output to this state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: $
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: $
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_stepfunctions as stepfunctions
            
            # result_selector: Any
            
            parallel_props = stepfunctions.ParallelProps(
                comment="comment",
                input_path="inputPath",
                output_path="outputPath",
                result_path="resultPath",
                result_selector={
                    "result_selector_key": result_selector
                }
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99937f18894b2be3de863916cec28700fc82180bc5d1b325c775062a15552b52)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument result_path", value=result_path, expected_type=type_hints["result_path"])
            check_type(argname="argument result_selector", value=result_selector, expected_type=type_hints["result_selector"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if input_path is not None:
            self._values["input_path"] = input_path
        if output_path is not None:
            self._values["output_path"] = output_path
        if result_path is not None:
            self._values["result_path"] = result_path
        if result_selector is not None:
            self._values["result_selector"] = result_selector

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the input to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: $
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the output to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        output to be the empty object {}.

        :default: $
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to indicate where to inject the state's output.

        May also be the special value JsonPath.DISCARD, which will cause the state's
        input to become its output.

        :default: $
        '''
        result = self._values.get("result_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_selector(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The JSON that will replace the state's raw result and become the effective result before ResultPath is applied.

        You can use ResultSelector to create a payload with values that are static
        or selected from the state's raw result.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-resultselector
        '''
        result = self._values.get("result_selector")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ParallelProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.PassProps",
    jsii_struct_bases=[],
    name_mapping={
        "comment": "comment",
        "input_path": "inputPath",
        "output_path": "outputPath",
        "parameters": "parameters",
        "result": "result",
        "result_path": "resultPath",
    },
)
class PassProps:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        result: typing.Optional["Result"] = None,
        result_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a Pass state.

        :param comment: An optional description for this state. Default: No comment
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param output_path: JSONPath expression to select part of the state to be the output to this state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: $
        :param parameters: Parameters pass a collection of key-value pairs, either static values or JSONPath expressions that select from the input. Default: No parameters
        :param result: If given, treat as the result of this operation. Can be used to inject or replace the current execution state. Default: No injected result
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: $

        :exampleMetadata: infused

        Example::

            # Makes the current JSON state { ..., "subObject": { "hello": "world" } }
            pass = sfn.Pass(self, "Add Hello World",
                result=sfn.Result.from_object({"hello": "world"}),
                result_path="$.subObject"
            )
            
            # Set the next state
            next_state = sfn.Pass(self, "NextState")
            pass.next(next_state)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f33e2139d06aae3f4b78bed7625415f8324a4f92e786c5587461cf5936552049)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument result", value=result, expected_type=type_hints["result"])
            check_type(argname="argument result_path", value=result_path, expected_type=type_hints["result_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if input_path is not None:
            self._values["input_path"] = input_path
        if output_path is not None:
            self._values["output_path"] = output_path
        if parameters is not None:
            self._values["parameters"] = parameters
        if result is not None:
            self._values["result"] = result
        if result_path is not None:
            self._values["result_path"] = result_path

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the input to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: $
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the output to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        output to be the empty object {}.

        :default: $
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Parameters pass a collection of key-value pairs, either static values or JSONPath expressions that select from the input.

        :default: No parameters

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-parameters
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def result(self) -> typing.Optional["Result"]:
        '''If given, treat as the result of this operation.

        Can be used to inject or replace the current execution state.

        :default: No injected result
        '''
        result = self._values.get("result")
        return typing.cast(typing.Optional["Result"], result)

    @builtins.property
    def result_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to indicate where to inject the state's output.

        May also be the special value JsonPath.DISCARD, which will cause the state's
        input to become its output.

        :default: $
        '''
        result = self._values.get("result_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PassProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Result(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Result"):
    '''The result of a Pass operation.

    :exampleMetadata: infused

    Example::

        # Makes the current JSON state { ..., "subObject": { "hello": "world" } }
        pass = sfn.Pass(self, "Add Hello World",
            result=sfn.Result.from_object({"hello": "world"}),
            result_path="$.subObject"
        )
        
        # Set the next state
        next_state = sfn.Pass(self, "NextState")
        pass.next(next_state)
    '''

    def __init__(self, value: typing.Any) -> None:
        '''
        :param value: result of the Pass operation.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84e36a870933f097185f82839cb19e77f631187d6491abd9a8b9a51183555d0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.create(self.__class__, self, [value])

    @jsii.member(jsii_name="fromArray")
    @builtins.classmethod
    def from_array(cls, value: typing.Sequence[typing.Any]) -> "Result":
        '''The result of the operation is an array.

        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b6993ac932620a29d3c7b062ba7911f6934b7c56e9d4da7abd31372a5b92a97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Result", jsii.sinvoke(cls, "fromArray", [value]))

    @jsii.member(jsii_name="fromBoolean")
    @builtins.classmethod
    def from_boolean(cls, value: builtins.bool) -> "Result":
        '''The result of the operation is a boolean.

        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__780ab2cd306973af0072ec2e462533a5c5cb5441ebe88c90ea5dad8300241774)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Result", jsii.sinvoke(cls, "fromBoolean", [value]))

    @jsii.member(jsii_name="fromNumber")
    @builtins.classmethod
    def from_number(cls, value: jsii.Number) -> "Result":
        '''The result of the operation is a number.

        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de966c949a7816976acc4c595469fca98f0b3b88c73b9046b2b1c7ab2836d87c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Result", jsii.sinvoke(cls, "fromNumber", [value]))

    @jsii.member(jsii_name="fromObject")
    @builtins.classmethod
    def from_object(cls, value: typing.Mapping[builtins.str, typing.Any]) -> "Result":
        '''The result of the operation is an object.

        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__401f8605bf7a4b66793f7882abce3f90dea71592cd856b8f553315d67f1b0a12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Result", jsii.sinvoke(cls, "fromObject", [value]))

    @jsii.member(jsii_name="fromString")
    @builtins.classmethod
    def from_string(cls, value: builtins.str) -> "Result":
        '''The result of the operation is a string.

        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4092efb800bb7cb48441e5ffc5742ee2961e05b7243571b373f234813ef0ad4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Result", jsii.sinvoke(cls, "fromString", [value]))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> typing.Any:
        '''result of the Pass operation.'''
        return typing.cast(typing.Any, jsii.get(self, "value"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.RetryProps",
    jsii_struct_bases=[],
    name_mapping={
        "backoff_rate": "backoffRate",
        "errors": "errors",
        "interval": "interval",
        "max_attempts": "maxAttempts",
    },
)
class RetryProps:
    def __init__(
        self,
        *,
        backoff_rate: typing.Optional[jsii.Number] = None,
        errors: typing.Optional[typing.Sequence[builtins.str]] = None,
        interval: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        max_attempts: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Retry details.

        :param backoff_rate: Multiplication for how much longer the wait interval gets on every retry. Default: 2
        :param errors: Errors to retry. A list of error strings to retry, which can be either predefined errors (for example Errors.NoChoiceMatched) or a self-defined error. Default: All errors
        :param interval: How many seconds to wait initially before retrying. Default: Duration.seconds(1)
        :param max_attempts: How many times to retry this particular error. May be 0 to disable retry for specific errors (in case you have a catch-all retry policy). Default: 3

        :exampleMetadata: infused

        Example::

            parallel = sfn.Parallel(self, "Do the work in parallel")
            
            # Add branches to be executed in parallel
            ship_item = sfn.Pass(self, "ShipItem")
            send_invoice = sfn.Pass(self, "SendInvoice")
            restock = sfn.Pass(self, "Restock")
            parallel.branch(ship_item)
            parallel.branch(send_invoice)
            parallel.branch(restock)
            
            # Retry the whole workflow if something goes wrong
            parallel.add_retry(max_attempts=1)
            
            # How to recover from errors
            send_failure_notification = sfn.Pass(self, "SendFailureNotification")
            parallel.add_catch(send_failure_notification)
            
            # What to do in case everything succeeded
            close_order = sfn.Pass(self, "CloseOrder")
            parallel.next(close_order)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5c198f8a8486dfb6548abbc422bc10f0280143fb9b56f2cb48a86718dff739e)
            check_type(argname="argument backoff_rate", value=backoff_rate, expected_type=type_hints["backoff_rate"])
            check_type(argname="argument errors", value=errors, expected_type=type_hints["errors"])
            check_type(argname="argument interval", value=interval, expected_type=type_hints["interval"])
            check_type(argname="argument max_attempts", value=max_attempts, expected_type=type_hints["max_attempts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if backoff_rate is not None:
            self._values["backoff_rate"] = backoff_rate
        if errors is not None:
            self._values["errors"] = errors
        if interval is not None:
            self._values["interval"] = interval
        if max_attempts is not None:
            self._values["max_attempts"] = max_attempts

    @builtins.property
    def backoff_rate(self) -> typing.Optional[jsii.Number]:
        '''Multiplication for how much longer the wait interval gets on every retry.

        :default: 2
        '''
        result = self._values.get("backoff_rate")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def errors(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Errors to retry.

        A list of error strings to retry, which can be either predefined errors
        (for example Errors.NoChoiceMatched) or a self-defined error.

        :default: All errors
        '''
        result = self._values.get("errors")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def interval(self) -> typing.Optional[_aws_cdk_core_f4b25747.Duration]:
        '''How many seconds to wait initially before retrying.

        :default: Duration.seconds(1)
        '''
        result = self._values.get("interval")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Duration], result)

    @builtins.property
    def max_attempts(self) -> typing.Optional[jsii.Number]:
        '''How many times to retry this particular error.

        May be 0 to disable retry for specific errors (in case you have
        a catch-all retry policy).

        :default: 3
        '''
        result = self._values.get("max_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RetryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-stepfunctions.ServiceIntegrationPattern")
class ServiceIntegrationPattern(enum.Enum):
    '''Three ways to call an integrated service: Request Response, Run a Job and Wait for a Callback with Task Token.

    :default: FIRE_AND_FORGET

    :see:

    https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html

    Here, they are named as FIRE_AND_FORGET, SYNC and WAIT_FOR_TASK_TOKEN respectfully.
    '''

    FIRE_AND_FORGET = "FIRE_AND_FORGET"
    '''Call a service and progress to the next state immediately after the API call completes.'''
    SYNC = "SYNC"
    '''Call a service and wait for a job to complete.'''
    WAIT_FOR_TASK_TOKEN = "WAIT_FOR_TASK_TOKEN"
    '''Call a service with a task token and wait until that token is returned by SendTaskSuccess/SendTaskFailure with payload.'''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.SingleStateOptions",
    jsii_struct_bases=[ParallelProps],
    name_mapping={
        "comment": "comment",
        "input_path": "inputPath",
        "output_path": "outputPath",
        "result_path": "resultPath",
        "result_selector": "resultSelector",
        "prefix_states": "prefixStates",
        "state_id": "stateId",
    },
)
class SingleStateOptions(ParallelProps):
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        prefix_states: typing.Optional[builtins.str] = None,
        state_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Options for creating a single state.

        :param comment: An optional description for this state. Default: No comment
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param output_path: JSONPath expression to select part of the state to be the output to this state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: $
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: $
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param prefix_states: String to prefix all stateIds in the state machine with. Default: stateId
        :param state_id: ID of newly created containing state. Default: Construct ID of the StateMachineFragment

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_stepfunctions as stepfunctions
            
            # result_selector: Any
            
            single_state_options = stepfunctions.SingleStateOptions(
                comment="comment",
                input_path="inputPath",
                output_path="outputPath",
                prefix_states="prefixStates",
                result_path="resultPath",
                result_selector={
                    "result_selector_key": result_selector
                },
                state_id="stateId"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2b217e1b8eb2f635f96c52167c0b1b5e80a7286eb6c943255f8fa17d509d98f)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument result_path", value=result_path, expected_type=type_hints["result_path"])
            check_type(argname="argument result_selector", value=result_selector, expected_type=type_hints["result_selector"])
            check_type(argname="argument prefix_states", value=prefix_states, expected_type=type_hints["prefix_states"])
            check_type(argname="argument state_id", value=state_id, expected_type=type_hints["state_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if input_path is not None:
            self._values["input_path"] = input_path
        if output_path is not None:
            self._values["output_path"] = output_path
        if result_path is not None:
            self._values["result_path"] = result_path
        if result_selector is not None:
            self._values["result_selector"] = result_selector
        if prefix_states is not None:
            self._values["prefix_states"] = prefix_states
        if state_id is not None:
            self._values["state_id"] = state_id

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the input to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: $
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the output to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        output to be the empty object {}.

        :default: $
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to indicate where to inject the state's output.

        May also be the special value JsonPath.DISCARD, which will cause the state's
        input to become its output.

        :default: $
        '''
        result = self._values.get("result_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_selector(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The JSON that will replace the state's raw result and become the effective result before ResultPath is applied.

        You can use ResultSelector to create a payload with values that are static
        or selected from the state's raw result.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-resultselector
        '''
        result = self._values.get("result_selector")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def prefix_states(self) -> typing.Optional[builtins.str]:
        '''String to prefix all stateIds in the state machine with.

        :default: stateId
        '''
        result = self._values.get("prefix_states")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state_id(self) -> typing.Optional[builtins.str]:
        '''ID of newly created containing state.

        :default: Construct ID of the StateMachineFragment
        '''
        result = self._values.get("state_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SingleStateOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IChainable)
class State(
    _aws_cdk_core_f4b25747.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-stepfunctions.State",
):
    '''Base class for all other state classes.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param comment: A comment describing this state. Default: No comment
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param output_path: JSONPath expression to select part of the state to be the output to this state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: $
        :param parameters: Parameters pass a collection of key-value pairs, either static values or JSONPath expressions that select from the input. Default: No parameters
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: $
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1324c4373ebbfce9f2b498f3e3d1e272df7f09bcb4237984663278ab97a4ad2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = StateProps(
            comment=comment,
            input_path=input_path,
            output_path=output_path,
            parameters=parameters,
            result_path=result_path,
            result_selector=result_selector,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="filterNextables")
    @builtins.classmethod
    def filter_nextables(
        cls,
        states: typing.Sequence["State"],
    ) -> typing.List[INextable]:
        '''Return only the states that allow chaining from an array of states.

        :param states: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0095a65aca92976f28d7bee65e227f573bc87e38e2936480033c2675e9bfee5e)
            check_type(argname="argument states", value=states, expected_type=type_hints["states"])
        return typing.cast(typing.List[INextable], jsii.sinvoke(cls, "filterNextables", [states]))

    @jsii.member(jsii_name="findReachableEndStates")
    @builtins.classmethod
    def find_reachable_end_states(
        cls,
        start: "State",
        *,
        include_error_handlers: typing.Optional[builtins.bool] = None,
    ) -> typing.List["State"]:
        '''Find the set of end states states reachable through transitions from the given start state.

        :param start: -
        :param include_error_handlers: Whether or not to follow error-handling transitions. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afab147d1c9e9cde65651d45243f6c8f846b3286b97e2aa17b35e73d5ade622f)
            check_type(argname="argument start", value=start, expected_type=type_hints["start"])
        options = FindStateOptions(include_error_handlers=include_error_handlers)

        return typing.cast(typing.List["State"], jsii.sinvoke(cls, "findReachableEndStates", [start, options]))

    @jsii.member(jsii_name="findReachableStates")
    @builtins.classmethod
    def find_reachable_states(
        cls,
        start: "State",
        *,
        include_error_handlers: typing.Optional[builtins.bool] = None,
    ) -> typing.List["State"]:
        '''Find the set of states reachable through transitions from the given start state.

        This does not retrieve states from within sub-graphs, such as states within a Parallel state's branch.

        :param start: -
        :param include_error_handlers: Whether or not to follow error-handling transitions. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2a80887f8e31f7bda9f516ef55507669a05722be24e4892abe50018fe24f56d)
            check_type(argname="argument start", value=start, expected_type=type_hints["start"])
        options = FindStateOptions(include_error_handlers=include_error_handlers)

        return typing.cast(typing.List["State"], jsii.sinvoke(cls, "findReachableStates", [start, options]))

    @jsii.member(jsii_name="prefixStates")
    @builtins.classmethod
    def prefix_states(
        cls,
        root: _constructs_77d1e7e8.IConstruct,
        prefix: builtins.str,
    ) -> None:
        '''Add a prefix to the stateId of all States found in a construct tree.

        :param root: -
        :param prefix: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5f2737cfc128b5a3fb2016940db8166fe92e7f3a3435debaaf00d5d66cbb2da)
            check_type(argname="argument root", value=root, expected_type=type_hints["root"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
        return typing.cast(None, jsii.sinvoke(cls, "prefixStates", [root, prefix]))

    @jsii.member(jsii_name="addBranch")
    def _add_branch(self, branch: "StateGraph") -> None:
        '''Add a paralle branch to this state.

        :param branch: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2648926708cf1cd8de428b3b40d881953eec01d0a5f923923ed4ccb885979401)
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
        return typing.cast(None, jsii.invoke(self, "addBranch", [branch]))

    @jsii.member(jsii_name="addChoice")
    def _add_choice(self, condition: Condition, next: "State") -> None:
        '''Add a choice branch to this state.

        :param condition: -
        :param next: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3ae445dfe0fd6d27c39e30a27e6947d5e10cddb3c02b12d5649112399f8c040)
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
            check_type(argname="argument next", value=next, expected_type=type_hints["next"])
        return typing.cast(None, jsii.invoke(self, "addChoice", [condition, next]))

    @jsii.member(jsii_name="addIterator")
    def _add_iterator(self, iteration: "StateGraph") -> None:
        '''Add a map iterator to this state.

        :param iteration: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56d3b511d59c66900a63f2d50a18d655b12d305ea2f267a44456a131d62cac6c)
            check_type(argname="argument iteration", value=iteration, expected_type=type_hints["iteration"])
        return typing.cast(None, jsii.invoke(self, "addIterator", [iteration]))

    @jsii.member(jsii_name="addPrefix")
    def add_prefix(self, x: builtins.str) -> None:
        '''Add a prefix to the stateId of this state.

        :param x: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81895af85a8fbc97eb6bce6d3790943fad44aaa28cd120930cba0cced2ecfc44)
            check_type(argname="argument x", value=x, expected_type=type_hints["x"])
        return typing.cast(None, jsii.invoke(self, "addPrefix", [x]))

    @jsii.member(jsii_name="bindToGraph")
    def bind_to_graph(self, graph: "StateGraph") -> None:
        '''Register this state as part of the given graph.

        Don't call this. It will be called automatically when you work
        with states normally.

        :param graph: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ace6d816d5dc40a00a519be1f4efbbd1c47a77265c4d7518d8cc569ab5ac934f)
            check_type(argname="argument graph", value=graph, expected_type=type_hints["graph"])
        return typing.cast(None, jsii.invoke(self, "bindToGraph", [graph]))

    @jsii.member(jsii_name="makeDefault")
    def _make_default(self, def_: "State") -> None:
        '''Make the indicated state the default choice transition of this state.

        :param def_: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79e37f07161e413cdb664dbfed80ea6aaf47635b659d468fcf2a403e21b85203)
            check_type(argname="argument def_", value=def_, expected_type=type_hints["def_"])
        return typing.cast(None, jsii.invoke(self, "makeDefault", [def_]))

    @jsii.member(jsii_name="makeNext")
    def _make_next(self, next: "State") -> None:
        '''Make the indicated state the default transition of this state.

        :param next: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b89fe7dbc98b4d5ec8b7cd25f37ed7f8ffdb7b6050533401d618b487cf675e26)
            check_type(argname="argument next", value=next, expected_type=type_hints["next"])
        return typing.cast(None, jsii.invoke(self, "makeNext", [next]))

    @jsii.member(jsii_name="renderBranches")
    def _render_branches(self) -> typing.Any:
        '''Render parallel branches in ASL JSON format.'''
        return typing.cast(typing.Any, jsii.invoke(self, "renderBranches", []))

    @jsii.member(jsii_name="renderChoices")
    def _render_choices(self) -> typing.Any:
        '''Render the choices in ASL JSON format.'''
        return typing.cast(typing.Any, jsii.invoke(self, "renderChoices", []))

    @jsii.member(jsii_name="renderInputOutput")
    def _render_input_output(self) -> typing.Any:
        '''Render InputPath/Parameters/OutputPath in ASL JSON format.'''
        return typing.cast(typing.Any, jsii.invoke(self, "renderInputOutput", []))

    @jsii.member(jsii_name="renderIterator")
    def _render_iterator(self) -> typing.Any:
        '''Render map iterator in ASL JSON format.'''
        return typing.cast(typing.Any, jsii.invoke(self, "renderIterator", []))

    @jsii.member(jsii_name="renderNextEnd")
    def _render_next_end(self) -> typing.Any:
        '''Render the default next state in ASL JSON format.'''
        return typing.cast(typing.Any, jsii.invoke(self, "renderNextEnd", []))

    @jsii.member(jsii_name="renderResultSelector")
    def _render_result_selector(self) -> typing.Any:
        '''Render ResultSelector in ASL JSON format.'''
        return typing.cast(typing.Any, jsii.invoke(self, "renderResultSelector", []))

    @jsii.member(jsii_name="renderRetryCatch")
    def _render_retry_catch(self) -> typing.Any:
        '''Render error recovery options in ASL JSON format.'''
        return typing.cast(typing.Any, jsii.invoke(self, "renderRetryCatch", []))

    @jsii.member(jsii_name="toStateJson")
    @abc.abstractmethod
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        '''Render the state as JSON.'''
        ...

    @jsii.member(jsii_name="whenBoundToGraph")
    def _when_bound_to_graph(self, graph: "StateGraph") -> None:
        '''Called whenever this state is bound to a graph.

        Can be overridden by subclasses.

        :param graph: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5770480781a9875ed1b9f1dd86b443e60e095369fed9f46cf6660624ea030315)
            check_type(argname="argument graph", value=graph, expected_type=type_hints["graph"])
        return typing.cast(None, jsii.invoke(self, "whenBoundToGraph", [graph]))

    @builtins.property
    @jsii.member(jsii_name="branches")
    def _branches(self) -> typing.List["StateGraph"]:
        return typing.cast(typing.List["StateGraph"], jsii.get(self, "branches"))

    @builtins.property
    @jsii.member(jsii_name="endStates")
    @abc.abstractmethod
    def end_states(self) -> typing.List[INextable]:
        '''Continuable states of this Chainable.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''Descriptive identifier for this chainable.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> "State":
        '''First state of this Chainable.'''
        return typing.cast("State", jsii.get(self, "startState"))

    @builtins.property
    @jsii.member(jsii_name="stateId")
    def state_id(self) -> builtins.str:
        '''Tokenized string that evaluates to the state's ID.'''
        return typing.cast(builtins.str, jsii.get(self, "stateId"))

    @builtins.property
    @jsii.member(jsii_name="comment")
    def _comment(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "comment"))

    @builtins.property
    @jsii.member(jsii_name="inputPath")
    def _input_path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inputPath"))

    @builtins.property
    @jsii.member(jsii_name="outputPath")
    def _output_path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputPath"))

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def _parameters(self) -> typing.Optional[typing.Mapping[typing.Any, typing.Any]]:
        return typing.cast(typing.Optional[typing.Mapping[typing.Any, typing.Any]], jsii.get(self, "parameters"))

    @builtins.property
    @jsii.member(jsii_name="resultPath")
    def _result_path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resultPath"))

    @builtins.property
    @jsii.member(jsii_name="resultSelector")
    def _result_selector(
        self,
    ) -> typing.Optional[typing.Mapping[typing.Any, typing.Any]]:
        return typing.cast(typing.Optional[typing.Mapping[typing.Any, typing.Any]], jsii.get(self, "resultSelector"))

    @builtins.property
    @jsii.member(jsii_name="defaultChoice")
    def _default_choice(self) -> typing.Optional["State"]:
        return typing.cast(typing.Optional["State"], jsii.get(self, "defaultChoice"))

    @_default_choice.setter
    def _default_choice(self, value: typing.Optional["State"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68c864b1a1022adea13e327e3dfe6ee14f8776c996fe5de825dec343d4b3c0c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultChoice", value)

    @builtins.property
    @jsii.member(jsii_name="iteration")
    def _iteration(self) -> typing.Optional["StateGraph"]:
        return typing.cast(typing.Optional["StateGraph"], jsii.get(self, "iteration"))

    @_iteration.setter
    def _iteration(self, value: typing.Optional["StateGraph"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e2d7c0832632f09eb081be9d7f33bcf8e005ee9cbcd3f7d1f42088428db4fc6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iteration", value)


class _StateProxy(State):
    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        '''Render the state as JSON.'''
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toStateJson", []))

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[INextable]:
        '''Continuable states of this Chainable.'''
        return typing.cast(typing.List[INextable], jsii.get(self, "endStates"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, State).__jsii_proxy_class__ = lambda : _StateProxy


class StateGraph(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-stepfunctions.StateGraph",
):
    '''A collection of connected states.

    A StateGraph is used to keep track of all states that are connected (have
    transitions between them). It does not include the substatemachines in
    a Parallel's branches: those are their own StateGraphs, but the graphs
    themselves have a hierarchical relationship as well.

    By assigning states to a definitive StateGraph, we verify that no state
    machines are constructed. In particular:

    - Every state object can only ever be in 1 StateGraph, and not inadvertently
      be used in two graphs.
    - Every stateId must be unique across all states in the entire state
      machine.

    All policy statements in all states in all substatemachines are bubbled so
    that the top-level StateMachine instantiation can read them all and add
    them to the IAM Role.

    You do not need to instantiate this class; it is used internally.

    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_stepfunctions as stepfunctions
        
        # state: stepfunctions.State
        
        state_graph = stepfunctions.StateGraph(state, "graphDescription")
    '''

    def __init__(self, start_state: State, graph_description: builtins.str) -> None:
        '''
        :param start_state: state that gets executed when the state machine is launched.
        :param graph_description: description of the state machine.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52d04a194c6077acd690671a313b18491aa25ba9721cb1ca0bc4c466e5b930cf)
            check_type(argname="argument start_state", value=start_state, expected_type=type_hints["start_state"])
            check_type(argname="argument graph_description", value=graph_description, expected_type=type_hints["graph_description"])
        jsii.create(self.__class__, self, [start_state, graph_description])

    @jsii.member(jsii_name="registerPolicyStatement")
    def register_policy_statement(
        self,
        statement: _aws_cdk_aws_iam_940a1ce0.PolicyStatement,
    ) -> None:
        '''Register a Policy Statement used by states in this graph.

        :param statement: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcf2a6b4e0d9e0a752eda4c67bd6fa98d7a06020e9d1ef0176698f17f96481b9)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(None, jsii.invoke(self, "registerPolicyStatement", [statement]))

    @jsii.member(jsii_name="registerState")
    def register_state(self, state: State) -> None:
        '''Register a state as part of this graph.

        Called by State.bindToGraph().

        :param state: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73f974e547b59888319d5df78dd33d1f247c9044544bebb182ee02a00918355e)
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
        return typing.cast(None, jsii.invoke(self, "registerState", [state]))

    @jsii.member(jsii_name="registerSuperGraph")
    def register_super_graph(self, graph: "StateGraph") -> None:
        '''Register this graph as a child of the given graph.

        Resource changes will be bubbled up to the given graph.

        :param graph: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a024abf47ab365824d3d6c42b5acc397a27cdc10e501bb07f56f6b0f695d1a7)
            check_type(argname="argument graph", value=graph, expected_type=type_hints["graph"])
        return typing.cast(None, jsii.invoke(self, "registerSuperGraph", [graph]))

    @jsii.member(jsii_name="toGraphJson")
    def to_graph_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        '''Return the Amazon States Language JSON for this graph.'''
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toGraphJson", []))

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''Return a string description of this graph.'''
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))

    @builtins.property
    @jsii.member(jsii_name="policyStatements")
    def policy_statements(
        self,
    ) -> typing.List[_aws_cdk_aws_iam_940a1ce0.PolicyStatement]:
        '''The accumulated policy statements.'''
        return typing.cast(typing.List[_aws_cdk_aws_iam_940a1ce0.PolicyStatement], jsii.get(self, "policyStatements"))

    @builtins.property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> State:
        '''state that gets executed when the state machine is launched.'''
        return typing.cast(State, jsii.get(self, "startState"))

    @builtins.property
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> typing.Optional[_aws_cdk_core_f4b25747.Duration]:
        '''Set a timeout to render into the graph JSON.

        Read/write. Only makes sense on the top-level graph, subgraphs
        do not support this feature.

        :default: No timeout
        '''
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Duration], jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: typing.Optional[_aws_cdk_core_f4b25747.Duration]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fbd6d1a83723a4743db754ed314898b4e96f07c3d18edfc30a0ae16bc328434)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeout", value)


@jsii.implements(IStateMachine)
class StateMachine(
    _aws_cdk_core_f4b25747.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-stepfunctions.StateMachine",
):
    '''Define a StepFunctions State Machine.

    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_stepfunctions as stepfunctions
        
        
        pipeline = codepipeline.Pipeline(self, "MyPipeline")
        input_artifact = codepipeline.Artifact()
        start_state = stepfunctions.Pass(self, "StartState")
        simple_state_machine = stepfunctions.StateMachine(self, "SimpleStateMachine",
            definition=start_state
        )
        step_function_action = codepipeline_actions.StepFunctionInvokeAction(
            action_name="Invoke",
            state_machine=simple_state_machine,
            state_machine_input=codepipeline_actions.StateMachineInput.file_path(input_artifact.at_path("assets/input.json"))
        )
        pipeline.add_stage(
            stage_name="StepFunctions",
            actions=[step_function_action]
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        definition: IChainable,
        logs: typing.Optional[typing.Union[LogOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        state_machine_type: typing.Optional["StateMachineType"] = None,
        timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        tracing_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param definition: Definition for this state machine.
        :param logs: Defines what execution history events are logged and where they are logged. Default: No logging
        :param role: The execution role for the state machine service. Default: A role is automatically created
        :param state_machine_name: A name for the state machine. Default: A name is automatically generated
        :param state_machine_type: Type of the state machine. Default: StateMachineType.STANDARD
        :param timeout: Maximum run time for this state machine. Default: No timeout
        :param tracing_enabled: Specifies whether Amazon X-Ray tracing is enabled for this state machine. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa2b76a9f1c214e2b5dfd0d9938d0f24129c6c78807a855e5049f844950a7108)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = StateMachineProps(
            definition=definition,
            logs=logs,
            role=role,
            state_machine_name=state_machine_name,
            state_machine_type=state_machine_type,
            timeout=timeout,
            tracing_enabled=tracing_enabled,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromStateMachineArn")
    @builtins.classmethod
    def from_state_machine_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        state_machine_arn: builtins.str,
    ) -> IStateMachine:
        '''Import a state machine.

        :param scope: -
        :param id: -
        :param state_machine_arn: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__036ef4a09a1f46631e7ad98aa525a45fed4789dcba1c9da87216e8f05168daa4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument state_machine_arn", value=state_machine_arn, expected_type=type_hints["state_machine_arn"])
        return typing.cast(IStateMachine, jsii.sinvoke(cls, "fromStateMachineArn", [scope, id, state_machine_arn]))

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(
        self,
        statement: _aws_cdk_aws_iam_940a1ce0.PolicyStatement,
    ) -> None:
        '''Add the given statement to the role's policy.

        :param statement: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba11e2574014096ea81cfeafd6f9ff9a13fe3dc7a0eab8f3cff881e5c47fb88c)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(None, jsii.invoke(self, "addToRolePolicy", [statement]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity custom permissions.

        :param identity: -
        :param actions: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__045d975b096fa0ab2140263c4c10eef65beb6f3cc58f5b63f611a50a931189ab)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grant", [identity, *actions]))

    @jsii.member(jsii_name="grantExecution")
    def grant_execution(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions on all executions of the state machine.

        :param identity: -
        :param actions: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e11380059dcaec588e06b52a6b43226e3de7061a68e8b20f052047fa4b030f2d)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantExecution", [identity, *actions]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions to read results from state machine.

        :param identity: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b3b84479c006f84a1827b5e70aab95e4b264d1c1637d36ee020ef0888570d43)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantRead", [identity]))

    @jsii.member(jsii_name="grantStartExecution")
    def grant_start_execution(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions to start an execution of this state machine.

        :param identity: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5897c343f0a2d050b170764fd94383a464776a7e51e25b73810e325123f70fc3)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantStartExecution", [identity]))

    @jsii.member(jsii_name="grantStartSyncExecution")
    def grant_start_sync_execution(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions to start a synchronous execution of this state machine.

        :param identity: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f9e02893f19aa89e377536c3462748257fcd4c285d9618ad11540db8a6c66f0)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantStartSyncExecution", [identity]))

    @jsii.member(jsii_name="grantTaskResponse")
    def grant_task_response(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity task response permissions on a state machine.

        :param identity: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd7c3ab1fbb36436c58ae7a73baaf7988e85acd0482628c34af38935f4b707af)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantTaskResponse", [identity]))

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
        '''Return the given named metric for this State Machine's executions.

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

        :default: - sum over 5 minutes
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2516d4e02c0e5db16ddccebb82fd3344b5845ceb75ebfa653ee2dfde0b431381)
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

    @jsii.member(jsii_name="metricAborted")
    def metric_aborted(
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
        '''Metric for the number of executions that were aborted.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricAborted", [props]))

    @jsii.member(jsii_name="metricFailed")
    def metric_failed(
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
        '''Metric for the number of executions that failed.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricFailed", [props]))

    @jsii.member(jsii_name="metricStarted")
    def metric_started(
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
        '''Metric for the number of executions that were started.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricStarted", [props]))

    @jsii.member(jsii_name="metricSucceeded")
    def metric_succeeded(
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
        '''Metric for the number of executions that succeeded.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricSucceeded", [props]))

    @jsii.member(jsii_name="metricThrottled")
    def metric_throttled(
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
        '''Metric for the number of executions that were throttled.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricThrottled", [props]))

    @jsii.member(jsii_name="metricTime")
    def metric_time(
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
        '''Metric for the interval, in milliseconds, between the time the execution starts and the time it closes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - average over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricTime", [props]))

    @jsii.member(jsii_name="metricTimedOut")
    def metric_timed_out(
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
        '''Metric for the number of executions that timed out.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricTimedOut", [props]))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_940a1ce0.IPrincipal:
        '''The principal this state machine is running as.'''
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_940a1ce0.IRole:
        '''Execution role of this state machine.'''
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.IRole, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="stateMachineArn")
    def state_machine_arn(self) -> builtins.str:
        '''The ARN of the state machine.'''
        return typing.cast(builtins.str, jsii.get(self, "stateMachineArn"))

    @builtins.property
    @jsii.member(jsii_name="stateMachineName")
    def state_machine_name(self) -> builtins.str:
        '''The name of the state machine.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "stateMachineName"))

    @builtins.property
    @jsii.member(jsii_name="stateMachineType")
    def state_machine_type(self) -> "StateMachineType":
        '''Type of the state machine.

        :attribute: true
        '''
        return typing.cast("StateMachineType", jsii.get(self, "stateMachineType"))


@jsii.implements(IChainable)
class StateMachineFragment(
    _aws_cdk_core_f4b25747.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-stepfunctions.StateMachineFragment",
):
    '''Base class for reusable state machine fragments.

    :exampleMetadata: nofixture infused

    Example::

        from aws_cdk.core import Stack
        from constructs import Construct
        import aws_cdk.aws_stepfunctions as sfn
        
        class MyJob(sfn.StateMachineFragment):
        
            def __init__(self, parent, id, *, jobFlavor):
                super().__init__(parent, id)
        
                choice = sfn.Choice(self, "Choice").when(sfn.Condition.string_equals("$.branch", "left"), sfn.Pass(self, "Left Branch")).when(sfn.Condition.string_equals("$.branch", "right"), sfn.Pass(self, "Right Branch"))
        
                # ...
        
                self.start_state = choice
                self.end_states = choice.afterwards().end_states
        
        class MyStack(Stack):
            def __init__(self, scope, id):
                super().__init__(scope, id)
                # Do 3 different variants of MyJob in parallel
                parallel = sfn.Parallel(self, "All jobs").branch(MyJob(self, "Quick", job_flavor="quick").prefix_states()).branch(MyJob(self, "Medium", job_flavor="medium").prefix_states()).branch(MyJob(self, "Slow", job_flavor="slow").prefix_states())
        
                sfn.StateMachine(self, "MyStateMachine",
                    definition=parallel
                )
    '''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82f8f54457926267586136ac5ebfd8f23426751808582096335230670af75fa1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="next")
    def next(self, next: IChainable) -> "Chain":
        '''Continue normal execution with the given state.

        :param next: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab36f6add0210cbbc2419ec9c5c832001a23b70a6f60b8cb3131e3aa13cc3faa)
            check_type(argname="argument next", value=next, expected_type=type_hints["next"])
        return typing.cast("Chain", jsii.invoke(self, "next", [next]))

    @jsii.member(jsii_name="prefixStates")
    def prefix_states(
        self,
        prefix: typing.Optional[builtins.str] = None,
    ) -> "StateMachineFragment":
        '''Prefix the IDs of all states in this state machine fragment.

        Use this to avoid multiple copies of the state machine all having the
        same state IDs.

        :param prefix: The prefix to add. Will use construct ID by default.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e999c21d8a64713b883d01847b987411810d8b83e307749ff5d162ce7c1a30a)
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
        return typing.cast("StateMachineFragment", jsii.invoke(self, "prefixStates", [prefix]))

    @jsii.member(jsii_name="toSingleState")
    def to_single_state(
        self,
        *,
        prefix_states: typing.Optional[builtins.str] = None,
        state_id: typing.Optional[builtins.str] = None,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> "Parallel":
        '''Wrap all states in this state machine fragment up into a single state.

        This can be used to add retry or error handling onto this state
        machine fragment.

        Be aware that this changes the result of the inner state machine
        to be an array with the result of the state machine in it. Adjust
        your paths accordingly. For example, change 'outputPath' to
        '$[0]'.

        :param prefix_states: String to prefix all stateIds in the state machine with. Default: stateId
        :param state_id: ID of newly created containing state. Default: Construct ID of the StateMachineFragment
        :param comment: An optional description for this state. Default: No comment
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param output_path: JSONPath expression to select part of the state to be the output to this state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: $
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: $
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        '''
        options = SingleStateOptions(
            prefix_states=prefix_states,
            state_id=state_id,
            comment=comment,
            input_path=input_path,
            output_path=output_path,
            result_path=result_path,
            result_selector=result_selector,
        )

        return typing.cast("Parallel", jsii.invoke(self, "toSingleState", [options]))

    @builtins.property
    @jsii.member(jsii_name="endStates")
    @abc.abstractmethod
    def end_states(self) -> typing.List[INextable]:
        '''The states to chain onto if this fragment is used.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''Descriptive identifier for this chainable.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="startState")
    @abc.abstractmethod
    def start_state(self) -> State:
        '''The start state of this state machine fragment.'''
        ...


class _StateMachineFragmentProxy(StateMachineFragment):
    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[INextable]:
        '''The states to chain onto if this fragment is used.'''
        return typing.cast(typing.List[INextable], jsii.get(self, "endStates"))

    @builtins.property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> State:
        '''The start state of this state machine fragment.'''
        return typing.cast(State, jsii.get(self, "startState"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, StateMachineFragment).__jsii_proxy_class__ = lambda : _StateMachineFragmentProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.StateMachineProps",
    jsii_struct_bases=[],
    name_mapping={
        "definition": "definition",
        "logs": "logs",
        "role": "role",
        "state_machine_name": "stateMachineName",
        "state_machine_type": "stateMachineType",
        "timeout": "timeout",
        "tracing_enabled": "tracingEnabled",
    },
)
class StateMachineProps:
    def __init__(
        self,
        *,
        definition: IChainable,
        logs: typing.Optional[typing.Union[LogOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        state_machine_type: typing.Optional["StateMachineType"] = None,
        timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        tracing_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Properties for defining a State Machine.

        :param definition: Definition for this state machine.
        :param logs: Defines what execution history events are logged and where they are logged. Default: No logging
        :param role: The execution role for the state machine service. Default: A role is automatically created
        :param state_machine_name: A name for the state machine. Default: A name is automatically generated
        :param state_machine_type: Type of the state machine. Default: StateMachineType.STANDARD
        :param timeout: Maximum run time for this state machine. Default: No timeout
        :param tracing_enabled: Specifies whether Amazon X-Ray tracing is enabled for this state machine. Default: false

        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_stepfunctions as stepfunctions
            
            
            pipeline = codepipeline.Pipeline(self, "MyPipeline")
            input_artifact = codepipeline.Artifact()
            start_state = stepfunctions.Pass(self, "StartState")
            simple_state_machine = stepfunctions.StateMachine(self, "SimpleStateMachine",
                definition=start_state
            )
            step_function_action = codepipeline_actions.StepFunctionInvokeAction(
                action_name="Invoke",
                state_machine=simple_state_machine,
                state_machine_input=codepipeline_actions.StateMachineInput.file_path(input_artifact.at_path("assets/input.json"))
            )
            pipeline.add_stage(
                stage_name="StepFunctions",
                actions=[step_function_action]
            )
        '''
        if isinstance(logs, dict):
            logs = LogOptions(**logs)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31e7681fbcb1dc57bcd1417ea5a7c1e72bca234d37e39bca573be4895b1b9ac8)
            check_type(argname="argument definition", value=definition, expected_type=type_hints["definition"])
            check_type(argname="argument logs", value=logs, expected_type=type_hints["logs"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument state_machine_name", value=state_machine_name, expected_type=type_hints["state_machine_name"])
            check_type(argname="argument state_machine_type", value=state_machine_type, expected_type=type_hints["state_machine_type"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument tracing_enabled", value=tracing_enabled, expected_type=type_hints["tracing_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "definition": definition,
        }
        if logs is not None:
            self._values["logs"] = logs
        if role is not None:
            self._values["role"] = role
        if state_machine_name is not None:
            self._values["state_machine_name"] = state_machine_name
        if state_machine_type is not None:
            self._values["state_machine_type"] = state_machine_type
        if timeout is not None:
            self._values["timeout"] = timeout
        if tracing_enabled is not None:
            self._values["tracing_enabled"] = tracing_enabled

    @builtins.property
    def definition(self) -> IChainable:
        '''Definition for this state machine.'''
        result = self._values.get("definition")
        assert result is not None, "Required property 'definition' is missing"
        return typing.cast(IChainable, result)

    @builtins.property
    def logs(self) -> typing.Optional[LogOptions]:
        '''Defines what execution history events are logged and where they are logged.

        :default: No logging
        '''
        result = self._values.get("logs")
        return typing.cast(typing.Optional[LogOptions], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole]:
        '''The execution role for the state machine service.

        :default: A role is automatically created
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole], result)

    @builtins.property
    def state_machine_name(self) -> typing.Optional[builtins.str]:
        '''A name for the state machine.

        :default: A name is automatically generated
        '''
        result = self._values.get("state_machine_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state_machine_type(self) -> typing.Optional["StateMachineType"]:
        '''Type of the state machine.

        :default: StateMachineType.STANDARD
        '''
        result = self._values.get("state_machine_type")
        return typing.cast(typing.Optional["StateMachineType"], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_core_f4b25747.Duration]:
        '''Maximum run time for this state machine.

        :default: No timeout
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Duration], result)

    @builtins.property
    def tracing_enabled(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether Amazon X-Ray tracing is enabled for this state machine.

        :default: false
        '''
        result = self._values.get("tracing_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StateMachineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-stepfunctions.StateMachineType")
class StateMachineType(enum.Enum):
    '''Two types of state machines are available in AWS Step Functions: EXPRESS AND STANDARD.

    :default: STANDARD

    :see: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-standard-vs-express.html
    :exampleMetadata: infused

    Example::

        state_machine_definition = stepfunctions.Pass(self, "PassState")
        
        state_machine = stepfunctions.StateMachine(self, "StateMachine",
            definition=state_machine_definition,
            state_machine_type=stepfunctions.StateMachineType.EXPRESS
        )
        
        apigateway.StepFunctionsRestApi(self, "StepFunctionsRestApi",
            deploy=True,
            state_machine=state_machine
        )
    '''

    EXPRESS = "EXPRESS"
    '''Express Workflows are ideal for high-volume, event processing workloads.'''
    STANDARD = "STANDARD"
    '''Standard Workflows are ideal for long-running, durable, and auditable workflows.'''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.StateProps",
    jsii_struct_bases=[],
    name_mapping={
        "comment": "comment",
        "input_path": "inputPath",
        "output_path": "outputPath",
        "parameters": "parameters",
        "result_path": "resultPath",
        "result_selector": "resultSelector",
    },
)
class StateProps:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''Properties shared by all states.

        :param comment: A comment describing this state. Default: No comment
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param output_path: JSONPath expression to select part of the state to be the output to this state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: $
        :param parameters: Parameters pass a collection of key-value pairs, either static values or JSONPath expressions that select from the input. Default: No parameters
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: $
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_stepfunctions as stepfunctions
            
            # parameters: Any
            # result_selector: Any
            
            state_props = stepfunctions.StateProps(
                comment="comment",
                input_path="inputPath",
                output_path="outputPath",
                parameters={
                    "parameters_key": parameters
                },
                result_path="resultPath",
                result_selector={
                    "result_selector_key": result_selector
                }
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fb82d029e32a00db384b778ad4a241a484db6650bdf28af605bc8031f38b985)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument result_path", value=result_path, expected_type=type_hints["result_path"])
            check_type(argname="argument result_selector", value=result_selector, expected_type=type_hints["result_selector"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if input_path is not None:
            self._values["input_path"] = input_path
        if output_path is not None:
            self._values["output_path"] = output_path
        if parameters is not None:
            self._values["parameters"] = parameters
        if result_path is not None:
            self._values["result_path"] = result_path
        if result_selector is not None:
            self._values["result_selector"] = result_selector

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''A comment describing this state.

        :default: No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the input to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: $
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the output to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        output to be the empty object {}.

        :default: $
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Parameters pass a collection of key-value pairs, either static values or JSONPath expressions that select from the input.

        :default: No parameters

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-parameters
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def result_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to indicate where to inject the state's output.

        May also be the special value JsonPath.DISCARD, which will cause the state's
        input to become its output.

        :default: $
        '''
        result = self._values.get("result_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_selector(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The JSON that will replace the state's raw result and become the effective result before ResultPath is applied.

        You can use ResultSelector to create a payload with values that are static
        or selected from the state's raw result.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-resultselector
        '''
        result = self._values.get("result_selector")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StateTransitionMetric(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-stepfunctions.StateTransitionMetric",
):
    '''Metrics on the rate limiting performed on state machine execution.

    These rate limits are shared across all state machines.

    :exampleMetadata: infused

    Example::

        cloudwatch.Alarm(self, "ThrottledAlarm",
            metric=sfn.StateTransitionMetric.metric_throttled_events(),
            threshold=10,
            evaluation_periods=2
        )
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="metric")
    @builtins.classmethod
    def metric(
        cls,
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
        '''Return the given named metric for the service's state transition metrics.

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

        :default: average over 5 minutes
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2136396d66f46f27d420217821413cefbcf8d871be2cf680e71ddc3bee7649a)
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.sinvoke(cls, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricConsumedCapacity")
    @builtins.classmethod
    def metric_consumed_capacity(
        cls,
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
        '''Metric for the number of available state transitions per second.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: average over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.sinvoke(cls, "metricConsumedCapacity", [props]))

    @jsii.member(jsii_name="metricProvisionedBucketSize")
    @builtins.classmethod
    def metric_provisioned_bucket_size(
        cls,
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
        '''Metric for the number of available state transitions.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: average over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.sinvoke(cls, "metricProvisionedBucketSize", [props]))

    @jsii.member(jsii_name="metricProvisionedRefillRate")
    @builtins.classmethod
    def metric_provisioned_refill_rate(
        cls,
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
        '''Metric for the provisioned steady-state execution rate.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: average over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.sinvoke(cls, "metricProvisionedRefillRate", [props]))

    @jsii.member(jsii_name="metricThrottledEvents")
    @builtins.classmethod
    def metric_throttled_events(
        cls,
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
        '''Metric for the number of throttled state transitions.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.sinvoke(cls, "metricThrottledEvents", [props]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.StepFunctionsTaskConfig",
    jsii_struct_bases=[],
    name_mapping={
        "resource_arn": "resourceArn",
        "heartbeat": "heartbeat",
        "metric_dimensions": "metricDimensions",
        "metric_prefix_plural": "metricPrefixPlural",
        "metric_prefix_singular": "metricPrefixSingular",
        "parameters": "parameters",
        "policy_statements": "policyStatements",
    },
)
class StepFunctionsTaskConfig:
    def __init__(
        self,
        *,
        resource_arn: builtins.str,
        heartbeat: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        metric_dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        metric_prefix_plural: typing.Optional[builtins.str] = None,
        metric_prefix_singular: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_940a1ce0.PolicyStatement]] = None,
    ) -> None:
        '''(deprecated) Properties that define what kind of task should be created.

        :param resource_arn: (deprecated) The resource that represents the work to be executed. Either the ARN of a Lambda Function or Activity, or a special ARN.
        :param heartbeat: (deprecated) Maximum time between heart beats. If the time between heart beats takes longer than this, a 'Timeout' error is raised. This is only relevant when using an Activity type as resource. Default: No heart beat timeout
        :param metric_dimensions: (deprecated) The dimensions to attach to metrics. Default: No metrics
        :param metric_prefix_plural: (deprecated) Prefix for plural metric names of activity actions. Default: No such metrics
        :param metric_prefix_singular: (deprecated) Prefix for singular metric names of activity actions. Default: No such metrics
        :param parameters: (deprecated) Parameters pass a collection of key-value pairs, either static values or JSONPath expressions that select from the input. The meaning of these parameters is task-dependent. Its values will be merged with the ``parameters`` property which is configured directly on the Task state. Default: No parameters
        :param policy_statements: (deprecated) Additional policy statements to add to the execution role. Default: No policy roles

        :deprecated: used by ``IStepFunctionsTask``. ``IStepFunctionsTask`` is deprecated and replaced by ``TaskStateBase``.

        :stability: deprecated
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_iam as iam
            import aws_cdk.aws_stepfunctions as stepfunctions
            import aws_cdk.core as cdk
            
            # metric_dimensions: Any
            # parameters: Any
            # policy_statement: iam.PolicyStatement
            
            step_functions_task_config = stepfunctions.StepFunctionsTaskConfig(
                resource_arn="resourceArn",
            
                # the properties below are optional
                heartbeat=cdk.Duration.minutes(30),
                metric_dimensions={
                    "metric_dimensions_key": metric_dimensions
                },
                metric_prefix_plural="metricPrefixPlural",
                metric_prefix_singular="metricPrefixSingular",
                parameters={
                    "parameters_key": parameters
                },
                policy_statements=[policy_statement]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3ab6a65494e211de3e3d62f380384415385d3c528bc760a44378d1284d042cc)
            check_type(argname="argument resource_arn", value=resource_arn, expected_type=type_hints["resource_arn"])
            check_type(argname="argument heartbeat", value=heartbeat, expected_type=type_hints["heartbeat"])
            check_type(argname="argument metric_dimensions", value=metric_dimensions, expected_type=type_hints["metric_dimensions"])
            check_type(argname="argument metric_prefix_plural", value=metric_prefix_plural, expected_type=type_hints["metric_prefix_plural"])
            check_type(argname="argument metric_prefix_singular", value=metric_prefix_singular, expected_type=type_hints["metric_prefix_singular"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument policy_statements", value=policy_statements, expected_type=type_hints["policy_statements"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "resource_arn": resource_arn,
        }
        if heartbeat is not None:
            self._values["heartbeat"] = heartbeat
        if metric_dimensions is not None:
            self._values["metric_dimensions"] = metric_dimensions
        if metric_prefix_plural is not None:
            self._values["metric_prefix_plural"] = metric_prefix_plural
        if metric_prefix_singular is not None:
            self._values["metric_prefix_singular"] = metric_prefix_singular
        if parameters is not None:
            self._values["parameters"] = parameters
        if policy_statements is not None:
            self._values["policy_statements"] = policy_statements

    @builtins.property
    def resource_arn(self) -> builtins.str:
        '''(deprecated) The resource that represents the work to be executed.

        Either the ARN of a Lambda Function or Activity, or a special
        ARN.

        :stability: deprecated
        '''
        result = self._values.get("resource_arn")
        assert result is not None, "Required property 'resource_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def heartbeat(self) -> typing.Optional[_aws_cdk_core_f4b25747.Duration]:
        '''(deprecated) Maximum time between heart beats.

        If the time between heart beats takes longer than this, a 'Timeout' error is raised.

        This is only relevant when using an Activity type as resource.

        :default: No heart beat timeout

        :stability: deprecated
        '''
        result = self._values.get("heartbeat")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Duration], result)

    @builtins.property
    def metric_dimensions(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(deprecated) The dimensions to attach to metrics.

        :default: No metrics

        :stability: deprecated
        '''
        result = self._values.get("metric_dimensions")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def metric_prefix_plural(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Prefix for plural metric names of activity actions.

        :default: No such metrics

        :stability: deprecated
        '''
        result = self._values.get("metric_prefix_plural")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metric_prefix_singular(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Prefix for singular metric names of activity actions.

        :default: No such metrics

        :stability: deprecated
        '''
        result = self._values.get("metric_prefix_singular")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(deprecated) Parameters pass a collection of key-value pairs, either static values or JSONPath expressions that select from the input.

        The meaning of these parameters is task-dependent.

        Its values will be merged with the ``parameters`` property which is configured directly
        on the Task state.

        :default: No parameters

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-parameters
        :stability: deprecated
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def policy_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_940a1ce0.PolicyStatement]]:
        '''(deprecated) Additional policy statements to add to the execution role.

        :default: No policy roles

        :stability: deprecated
        '''
        result = self._values.get("policy_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_940a1ce0.PolicyStatement]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StepFunctionsTaskConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Succeed(
    State,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-stepfunctions.Succeed",
):
    '''Define a Succeed state in the state machine.

    Reaching a Succeed state terminates the state execution in success.

    :exampleMetadata: infused

    Example::

        success = sfn.Succeed(self, "We did it!")
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param comment: An optional description for this state. Default: No comment
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param output_path: JSONPath expression to select part of the state to be the output to this state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: $
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a3fee51501956a060589c278503bcde0b7db3618b7b2f9ab9b0ad9633ac8a0f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SucceedProps(
            comment=comment, input_path=input_path, output_path=output_path
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        '''Return the Amazon States Language object for this state.'''
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toStateJson", []))

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[INextable]:
        '''Continuable states of this Chainable.'''
        return typing.cast(typing.List[INextable], jsii.get(self, "endStates"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.SucceedProps",
    jsii_struct_bases=[],
    name_mapping={
        "comment": "comment",
        "input_path": "inputPath",
        "output_path": "outputPath",
    },
)
class SucceedProps:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a Succeed state.

        :param comment: An optional description for this state. Default: No comment
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param output_path: JSONPath expression to select part of the state to be the output to this state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: $

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_stepfunctions as stepfunctions
            
            succeed_props = stepfunctions.SucceedProps(
                comment="comment",
                input_path="inputPath",
                output_path="outputPath"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f0ef64196b7ec0cc54dff745229d134361a002896d7f9caf6eb18e9ee47fd5e)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if input_path is not None:
            self._values["input_path"] = input_path
        if output_path is not None:
            self._values["output_path"] = output_path

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the input to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: $
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the output to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        output to be the empty object {}.

        :default: $
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SucceedProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(INextable)
class Task(State, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Task"):
    '''(deprecated) Define a Task state in the state machine.

    Reaching a Task state causes some work to be executed, represented by the
    Task's resource property. Task constructs represent a generic Amazon
    States Language Task.

    For some resource types, more specific subclasses of Task may be available
    which are more convenient to use.

    :deprecated: - replaced by service integration specific classes (i.e. LambdaInvoke, SnsPublish)

    :stability: deprecated
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_stepfunctions as stepfunctions
        import aws_cdk.core as cdk
        
        # parameters: Any
        # step_functions_task: stepfunctions.IStepFunctionsTask
        
        task = stepfunctions.Task(self, "MyTask",
            task=step_functions_task,
        
            # the properties below are optional
            comment="comment",
            input_path="inputPath",
            output_path="outputPath",
            parameters={
                "parameters_key": parameters
            },
            result_path="resultPath",
            timeout=cdk.Duration.minutes(30)
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        task: IStepFunctionsTask,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        result_path: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param task: (deprecated) Actual task to be invoked in this workflow.
        :param comment: (deprecated) An optional description for this state. Default: No comment
        :param input_path: (deprecated) JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param output_path: (deprecated) JSONPath expression to select part of the state to be the output to this state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: $
        :param parameters: (deprecated) Parameters to invoke the task with. It is not recommended to use this field. The object that is passed in the ``task`` property will take care of returning the right values for the ``Parameters`` field in the Step Functions definition. The various classes that implement ``IStepFunctionsTask`` will take a properties which make sense for the task type. For example, for ``InvokeFunction`` the field that populates the ``parameters`` field will be called ``payload``, and for the ``PublishToTopic`` the ``parameters`` field will be populated via a combination of the referenced topic, subject and message. If passed anyway, the keys in this map will override the parameters returned by the task object. Default: - Use the parameters implied by the ``task`` property
        :param result_path: (deprecated) JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: $
        :param timeout: (deprecated) Maximum run time of this state. If the state takes longer than this amount of time to complete, a 'Timeout' error is raised. Default: 60

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26687ca06c1d1db93110592b07dbd68a53c8ea0ed0394d01b39e56742ff9c7ad)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TaskProps(
            task=task,
            comment=comment,
            input_path=input_path,
            output_path=output_path,
            parameters=parameters,
            result_path=result_path,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addCatch")
    def add_catch(
        self,
        handler: IChainable,
        *,
        errors: typing.Optional[typing.Sequence[builtins.str]] = None,
        result_path: typing.Optional[builtins.str] = None,
    ) -> "Task":
        '''(deprecated) Add a recovery handler for this state.

        When a particular error occurs, execution will continue at the error
        handler instead of failing the state machine execution.

        :param handler: -
        :param errors: Errors to recover from by going to the given state. A list of error strings to retry, which can be either predefined errors (for example Errors.NoChoiceMatched) or a self-defined error. Default: All errors
        :param result_path: JSONPath expression to indicate where to inject the error data. May also be the special value DISCARD, which will cause the error data to be discarded. Default: $

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c320de101ad653e731fe0c9f306f3f921b337d3b7e048a970ff82d93493a7985)
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
        props = CatchProps(errors=errors, result_path=result_path)

        return typing.cast("Task", jsii.invoke(self, "addCatch", [handler, props]))

    @jsii.member(jsii_name="addRetry")
    def add_retry(
        self,
        *,
        backoff_rate: typing.Optional[jsii.Number] = None,
        errors: typing.Optional[typing.Sequence[builtins.str]] = None,
        interval: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        max_attempts: typing.Optional[jsii.Number] = None,
    ) -> "Task":
        '''(deprecated) Add retry configuration for this state.

        This controls if and how the execution will be retried if a particular
        error occurs.

        :param backoff_rate: Multiplication for how much longer the wait interval gets on every retry. Default: 2
        :param errors: Errors to retry. A list of error strings to retry, which can be either predefined errors (for example Errors.NoChoiceMatched) or a self-defined error. Default: All errors
        :param interval: How many seconds to wait initially before retrying. Default: Duration.seconds(1)
        :param max_attempts: How many times to retry this particular error. May be 0 to disable retry for specific errors (in case you have a catch-all retry policy). Default: 3

        :stability: deprecated
        '''
        props = RetryProps(
            backoff_rate=backoff_rate,
            errors=errors,
            interval=interval,
            max_attempts=max_attempts,
        )

        return typing.cast("Task", jsii.invoke(self, "addRetry", [props]))

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
        '''(deprecated) Return the given named metric for this Task.

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

        :default: sum over 5 minutes

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0bff55910b6829f6e895d73efa6cd042cf6828348101a6f2b2f198d470fa569)
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

    @jsii.member(jsii_name="metricFailed")
    def metric_failed(
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
        '''(deprecated) Metric for the number of times this activity fails.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: sum over 5 minutes

        :stability: deprecated
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricFailed", [props]))

    @jsii.member(jsii_name="metricHeartbeatTimedOut")
    def metric_heartbeat_timed_out(
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
        '''(deprecated) Metric for the number of times the heartbeat times out for this activity.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: sum over 5 minutes

        :stability: deprecated
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricHeartbeatTimedOut", [props]))

    @jsii.member(jsii_name="metricRunTime")
    def metric_run_time(
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
        '''(deprecated) The interval, in milliseconds, between the time the Task starts and the time it closes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: average over 5 minutes

        :stability: deprecated
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricRunTime", [props]))

    @jsii.member(jsii_name="metricScheduled")
    def metric_scheduled(
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
        '''(deprecated) Metric for the number of times this activity is scheduled.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: sum over 5 minutes

        :stability: deprecated
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricScheduled", [props]))

    @jsii.member(jsii_name="metricScheduleTime")
    def metric_schedule_time(
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
        '''(deprecated) The interval, in milliseconds, for which the activity stays in the schedule state.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: average over 5 minutes

        :stability: deprecated
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricScheduleTime", [props]))

    @jsii.member(jsii_name="metricStarted")
    def metric_started(
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
        '''(deprecated) Metric for the number of times this activity is started.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: sum over 5 minutes

        :stability: deprecated
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricStarted", [props]))

    @jsii.member(jsii_name="metricSucceeded")
    def metric_succeeded(
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
        '''(deprecated) Metric for the number of times this activity succeeds.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: sum over 5 minutes

        :stability: deprecated
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricSucceeded", [props]))

    @jsii.member(jsii_name="metricTime")
    def metric_time(
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
        '''(deprecated) The interval, in milliseconds, between the time the activity is scheduled and the time it closes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: average over 5 minutes

        :stability: deprecated
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricTime", [props]))

    @jsii.member(jsii_name="metricTimedOut")
    def metric_timed_out(
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
        '''(deprecated) Metric for the number of times this activity times out.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: sum over 5 minutes

        :stability: deprecated
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricTimedOut", [props]))

    @jsii.member(jsii_name="next")
    def next(self, next: IChainable) -> "Chain":
        '''(deprecated) Continue normal execution with the given state.

        :param next: -

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df5d91235929ec66350172358fab2d5d876742452b29597ef26519096d6dd957)
            check_type(argname="argument next", value=next, expected_type=type_hints["next"])
        return typing.cast("Chain", jsii.invoke(self, "next", [next]))

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        '''(deprecated) Return the Amazon States Language object for this state.

        :stability: deprecated
        '''
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toStateJson", []))

    @jsii.member(jsii_name="whenBoundToGraph")
    def _when_bound_to_graph(self, graph: StateGraph) -> None:
        '''(deprecated) Called whenever this state is bound to a graph.

        Can be overridden by subclasses.

        :param graph: -

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f94e8631be4a4e5b23f10fd0083b60ee3eaf1f6fad577ffacda0b6ee181092c4)
            check_type(argname="argument graph", value=graph, expected_type=type_hints["graph"])
        return typing.cast(None, jsii.invoke(self, "whenBoundToGraph", [graph]))

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[INextable]:
        '''(deprecated) Continuable states of this Chainable.

        :stability: deprecated
        '''
        return typing.cast(typing.List[INextable], jsii.get(self, "endStates"))


class TaskInput(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-stepfunctions.TaskInput",
):
    '''Type union for task classes that accept multiple types of payload.

    :exampleMetadata: infused

    Example::

        # fn: lambda.Function
        
        tasks.LambdaInvoke(self, "Invoke with callback",
            lambda_function=fn,
            integration_pattern=sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
            payload=sfn.TaskInput.from_object({
                "token": sfn.JsonPath.task_token,
                "input": sfn.JsonPath.string_at("$.someField")
            })
        )
    '''

    @jsii.member(jsii_name="fromContextAt")
    @builtins.classmethod
    def from_context_at(cls, path: builtins.str) -> "TaskInput":
        '''(deprecated) Use a part of the task context as task input.

        Use this when you want to use a subobject or string from
        the current task context as complete payload
        to a task.

        :param path: -

        :deprecated: Use ``fromJsonPathAt``.

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62307ad7b715ba18acb03a3877987fe2ec4577e919c7b11b4486b2e0a3e42951)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast("TaskInput", jsii.sinvoke(cls, "fromContextAt", [path]))

    @jsii.member(jsii_name="fromDataAt")
    @builtins.classmethod
    def from_data_at(cls, path: builtins.str) -> "TaskInput":
        '''(deprecated) Use a part of the execution data as task input.

        Use this when you want to use a subobject or string from
        the current state machine execution as complete payload
        to a task.

        :param path: -

        :deprecated: Use ``fromJsonPathAt``.

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1aab6ed420836da4f48b9a8886ed3e99108dd3e59b9753d355408a3f54d8d98c)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast("TaskInput", jsii.sinvoke(cls, "fromDataAt", [path]))

    @jsii.member(jsii_name="fromJsonPathAt")
    @builtins.classmethod
    def from_json_path_at(cls, path: builtins.str) -> "TaskInput":
        '''Use a part of the execution data or task context as task input.

        Use this when you want to use a subobject or string from
        the current state machine execution or the current task context
        as complete payload to a task.

        :param path: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d7965027d24e2c871290ecc451ffdb0354415922c0995e450d4631975cb7baf)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast("TaskInput", jsii.sinvoke(cls, "fromJsonPathAt", [path]))

    @jsii.member(jsii_name="fromObject")
    @builtins.classmethod
    def from_object(cls, obj: typing.Mapping[builtins.str, typing.Any]) -> "TaskInput":
        '''Use an object as task input.

        This object may contain JSON path fields as object values, if desired.

        :param obj: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ff25ea3abad7f3022ea7be75920807aa05a38330790c444b1a3b852f3b95b17)
            check_type(argname="argument obj", value=obj, expected_type=type_hints["obj"])
        return typing.cast("TaskInput", jsii.sinvoke(cls, "fromObject", [obj]))

    @jsii.member(jsii_name="fromText")
    @builtins.classmethod
    def from_text(cls, text: builtins.str) -> "TaskInput":
        '''Use a literal string as task input.

        This might be a JSON-encoded object, or just a text.

        :param text: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a16a24a6c36aaa11ea75f533346c3821564968ca9c00067a47c6c78cd9421fb4)
            check_type(argname="argument text", value=text, expected_type=type_hints["text"])
        return typing.cast("TaskInput", jsii.sinvoke(cls, "fromText", [text]))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> InputType:
        '''type of task input.'''
        return typing.cast(InputType, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> typing.Any:
        '''payload for the corresponding input type.

        It can be a JSON-encoded object, context, data, etc.
        '''
        return typing.cast(typing.Any, jsii.get(self, "value"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.TaskMetricsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "metric_dimensions": "metricDimensions",
        "metric_prefix_plural": "metricPrefixPlural",
        "metric_prefix_singular": "metricPrefixSingular",
    },
)
class TaskMetricsConfig:
    def __init__(
        self,
        *,
        metric_dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        metric_prefix_plural: typing.Optional[builtins.str] = None,
        metric_prefix_singular: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Task Metrics.

        :param metric_dimensions: The dimensions to attach to metrics. Default: - No metrics
        :param metric_prefix_plural: Prefix for plural metric names of activity actions. Default: - No such metrics
        :param metric_prefix_singular: Prefix for singular metric names of activity actions. Default: - No such metrics

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_stepfunctions as stepfunctions
            
            # metric_dimensions: Any
            
            task_metrics_config = stepfunctions.TaskMetricsConfig(
                metric_dimensions={
                    "metric_dimensions_key": metric_dimensions
                },
                metric_prefix_plural="metricPrefixPlural",
                metric_prefix_singular="metricPrefixSingular"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__108b830836ef9861875250e04ce0894a43717bf7fd1ae7a9325c971e60f4ceab)
            check_type(argname="argument metric_dimensions", value=metric_dimensions, expected_type=type_hints["metric_dimensions"])
            check_type(argname="argument metric_prefix_plural", value=metric_prefix_plural, expected_type=type_hints["metric_prefix_plural"])
            check_type(argname="argument metric_prefix_singular", value=metric_prefix_singular, expected_type=type_hints["metric_prefix_singular"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if metric_dimensions is not None:
            self._values["metric_dimensions"] = metric_dimensions
        if metric_prefix_plural is not None:
            self._values["metric_prefix_plural"] = metric_prefix_plural
        if metric_prefix_singular is not None:
            self._values["metric_prefix_singular"] = metric_prefix_singular

    @builtins.property
    def metric_dimensions(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The dimensions to attach to metrics.

        :default: - No metrics
        '''
        result = self._values.get("metric_dimensions")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def metric_prefix_plural(self) -> typing.Optional[builtins.str]:
        '''Prefix for plural metric names of activity actions.

        :default: - No such metrics
        '''
        result = self._values.get("metric_prefix_plural")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metric_prefix_singular(self) -> typing.Optional[builtins.str]:
        '''Prefix for singular metric names of activity actions.

        :default: - No such metrics
        '''
        result = self._values.get("metric_prefix_singular")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TaskMetricsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.TaskProps",
    jsii_struct_bases=[],
    name_mapping={
        "task": "task",
        "comment": "comment",
        "input_path": "inputPath",
        "output_path": "outputPath",
        "parameters": "parameters",
        "result_path": "resultPath",
        "timeout": "timeout",
    },
)
class TaskProps:
    def __init__(
        self,
        *,
        task: IStepFunctionsTask,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        result_path: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    ) -> None:
        '''(deprecated) Props that are common to all tasks.

        :param task: (deprecated) Actual task to be invoked in this workflow.
        :param comment: (deprecated) An optional description for this state. Default: No comment
        :param input_path: (deprecated) JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param output_path: (deprecated) JSONPath expression to select part of the state to be the output to this state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: $
        :param parameters: (deprecated) Parameters to invoke the task with. It is not recommended to use this field. The object that is passed in the ``task`` property will take care of returning the right values for the ``Parameters`` field in the Step Functions definition. The various classes that implement ``IStepFunctionsTask`` will take a properties which make sense for the task type. For example, for ``InvokeFunction`` the field that populates the ``parameters`` field will be called ``payload``, and for the ``PublishToTopic`` the ``parameters`` field will be populated via a combination of the referenced topic, subject and message. If passed anyway, the keys in this map will override the parameters returned by the task object. Default: - Use the parameters implied by the ``task`` property
        :param result_path: (deprecated) JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: $
        :param timeout: (deprecated) Maximum run time of this state. If the state takes longer than this amount of time to complete, a 'Timeout' error is raised. Default: 60

        :deprecated: - replaced by service integration specific classes (i.e. LambdaInvoke, SnsPublish)

        :stability: deprecated
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_stepfunctions as stepfunctions
            import aws_cdk.core as cdk
            
            # parameters: Any
            # step_functions_task: stepfunctions.IStepFunctionsTask
            
            task_props = stepfunctions.TaskProps(
                task=step_functions_task,
            
                # the properties below are optional
                comment="comment",
                input_path="inputPath",
                output_path="outputPath",
                parameters={
                    "parameters_key": parameters
                },
                result_path="resultPath",
                timeout=cdk.Duration.minutes(30)
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8392990ee9aa926cb3e15f74a39e3c4ece180acd66c00f1f4616b26b451f3871)
            check_type(argname="argument task", value=task, expected_type=type_hints["task"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument result_path", value=result_path, expected_type=type_hints["result_path"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "task": task,
        }
        if comment is not None:
            self._values["comment"] = comment
        if input_path is not None:
            self._values["input_path"] = input_path
        if output_path is not None:
            self._values["output_path"] = output_path
        if parameters is not None:
            self._values["parameters"] = parameters
        if result_path is not None:
            self._values["result_path"] = result_path
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def task(self) -> IStepFunctionsTask:
        '''(deprecated) Actual task to be invoked in this workflow.

        :stability: deprecated
        '''
        result = self._values.get("task")
        assert result is not None, "Required property 'task' is missing"
        return typing.cast(IStepFunctionsTask, result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''(deprecated) An optional description for this state.

        :default: No comment

        :stability: deprecated
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''(deprecated) JSONPath expression to select part of the state to be the input to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: $

        :stability: deprecated
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''(deprecated) JSONPath expression to select part of the state to be the output to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        output to be the empty object {}.

        :default: $

        :stability: deprecated
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(deprecated) Parameters to invoke the task with.

        It is not recommended to use this field. The object that is passed in
        the ``task`` property will take care of returning the right values for the
        ``Parameters`` field in the Step Functions definition.

        The various classes that implement ``IStepFunctionsTask`` will take a
        properties which make sense for the task type. For example, for
        ``InvokeFunction`` the field that populates the ``parameters`` field will be
        called ``payload``, and for the ``PublishToTopic`` the ``parameters`` field
        will be populated via a combination of the referenced topic, subject and
        message.

        If passed anyway, the keys in this map will override the parameters
        returned by the task object.

        :default: - Use the parameters implied by the ``task`` property

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-parameters
        :stability: deprecated
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def result_path(self) -> typing.Optional[builtins.str]:
        '''(deprecated) JSONPath expression to indicate where to inject the state's output.

        May also be the special value JsonPath.DISCARD, which will cause the state's
        input to become its output.

        :default: $

        :stability: deprecated
        '''
        result = self._values.get("result_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_core_f4b25747.Duration]:
        '''(deprecated) Maximum run time of this state.

        If the state takes longer than this amount of time to complete, a 'Timeout' error is raised.

        :default: 60

        :stability: deprecated
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TaskProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(INextable)
class TaskStateBase(
    State,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-stepfunctions.TaskStateBase",
):
    '''Define a Task state in the state machine.

    Reaching a Task state causes some work to be executed, represented by the
    Task's resource property. Task constructs represent a generic Amazon
    States Language Task.

    For some resource types, more specific subclasses of Task may be available
    which are more convenient to use.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        comment: typing.Optional[builtins.str] = None,
        heartbeat: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param comment: An optional description for this state. Default: - No comment
        :param heartbeat: Timeout for the heartbeat. Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param timeout: Timeout for the state machine. Default: - None
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c035eaad4cfaa5e12f5859b94ec63b167e3e27e13061fe9b451d3a382a93998)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TaskStateBaseProps(
            comment=comment,
            heartbeat=heartbeat,
            input_path=input_path,
            integration_pattern=integration_pattern,
            output_path=output_path,
            result_path=result_path,
            result_selector=result_selector,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addCatch")
    def add_catch(
        self,
        handler: IChainable,
        *,
        errors: typing.Optional[typing.Sequence[builtins.str]] = None,
        result_path: typing.Optional[builtins.str] = None,
    ) -> "TaskStateBase":
        '''Add a recovery handler for this state.

        When a particular error occurs, execution will continue at the error
        handler instead of failing the state machine execution.

        :param handler: -
        :param errors: Errors to recover from by going to the given state. A list of error strings to retry, which can be either predefined errors (for example Errors.NoChoiceMatched) or a self-defined error. Default: All errors
        :param result_path: JSONPath expression to indicate where to inject the error data. May also be the special value DISCARD, which will cause the error data to be discarded. Default: $
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92c346551ec95902de89e8242188887669cdec538f40a26dc53c62b292f169bb)
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
        props = CatchProps(errors=errors, result_path=result_path)

        return typing.cast("TaskStateBase", jsii.invoke(self, "addCatch", [handler, props]))

    @jsii.member(jsii_name="addRetry")
    def add_retry(
        self,
        *,
        backoff_rate: typing.Optional[jsii.Number] = None,
        errors: typing.Optional[typing.Sequence[builtins.str]] = None,
        interval: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        max_attempts: typing.Optional[jsii.Number] = None,
    ) -> "TaskStateBase":
        '''Add retry configuration for this state.

        This controls if and how the execution will be retried if a particular
        error occurs.

        :param backoff_rate: Multiplication for how much longer the wait interval gets on every retry. Default: 2
        :param errors: Errors to retry. A list of error strings to retry, which can be either predefined errors (for example Errors.NoChoiceMatched) or a self-defined error. Default: All errors
        :param interval: How many seconds to wait initially before retrying. Default: Duration.seconds(1)
        :param max_attempts: How many times to retry this particular error. May be 0 to disable retry for specific errors (in case you have a catch-all retry policy). Default: 3
        '''
        props = RetryProps(
            backoff_rate=backoff_rate,
            errors=errors,
            interval=interval,
            max_attempts=max_attempts,
        )

        return typing.cast("TaskStateBase", jsii.invoke(self, "addRetry", [props]))

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
        '''Return the given named metric for this Task.

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

        :default: - sum over 5 minutes
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ed0e391b213542ae166175ab94c8177b017b96bd6c3f393c49da75c1bae5102)
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

    @jsii.member(jsii_name="metricFailed")
    def metric_failed(
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
        '''Metric for the number of times this activity fails.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricFailed", [props]))

    @jsii.member(jsii_name="metricHeartbeatTimedOut")
    def metric_heartbeat_timed_out(
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
        '''Metric for the number of times the heartbeat times out for this activity.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricHeartbeatTimedOut", [props]))

    @jsii.member(jsii_name="metricRunTime")
    def metric_run_time(
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
        '''The interval, in milliseconds, between the time the Task starts and the time it closes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - average over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricRunTime", [props]))

    @jsii.member(jsii_name="metricScheduled")
    def metric_scheduled(
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
        '''Metric for the number of times this activity is scheduled.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricScheduled", [props]))

    @jsii.member(jsii_name="metricScheduleTime")
    def metric_schedule_time(
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
        '''The interval, in milliseconds, for which the activity stays in the schedule state.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - average over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricScheduleTime", [props]))

    @jsii.member(jsii_name="metricStarted")
    def metric_started(
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
        '''Metric for the number of times this activity is started.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricStarted", [props]))

    @jsii.member(jsii_name="metricSucceeded")
    def metric_succeeded(
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
        '''Metric for the number of times this activity succeeds.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricSucceeded", [props]))

    @jsii.member(jsii_name="metricTime")
    def metric_time(
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
        '''The interval, in milliseconds, between the time the activity is scheduled and the time it closes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - average over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricTime", [props]))

    @jsii.member(jsii_name="metricTimedOut")
    def metric_timed_out(
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
        '''Metric for the number of times this activity times out.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricTimedOut", [props]))

    @jsii.member(jsii_name="next")
    def next(self, next: IChainable) -> "Chain":
        '''Continue normal execution with the given state.

        :param next: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d370c709c8b030c72e433536c8c128fea1dc5a3dedb6cd249d1876e85f323370)
            check_type(argname="argument next", value=next, expected_type=type_hints["next"])
        return typing.cast("Chain", jsii.invoke(self, "next", [next]))

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        '''Return the Amazon States Language object for this state.'''
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toStateJson", []))

    @jsii.member(jsii_name="whenBoundToGraph")
    def _when_bound_to_graph(self, graph: StateGraph) -> None:
        '''Called whenever this state is bound to a graph.

        Can be overridden by subclasses.

        :param graph: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0261e83cce662127de2b44eb1b9c7af0d860b23d7ede17127aa3f6a564279e11)
            check_type(argname="argument graph", value=graph, expected_type=type_hints["graph"])
        return typing.cast(None, jsii.invoke(self, "whenBoundToGraph", [graph]))

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[INextable]:
        '''Continuable states of this Chainable.'''
        return typing.cast(typing.List[INextable], jsii.get(self, "endStates"))

    @builtins.property
    @jsii.member(jsii_name="taskMetrics")
    @abc.abstractmethod
    def _task_metrics(self) -> typing.Optional[TaskMetricsConfig]:
        ...

    @builtins.property
    @jsii.member(jsii_name="taskPolicies")
    @abc.abstractmethod
    def _task_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_940a1ce0.PolicyStatement]]:
        ...


class _TaskStateBaseProxy(
    TaskStateBase,
    jsii.proxy_for(State), # type: ignore[misc]
):
    @builtins.property
    @jsii.member(jsii_name="taskMetrics")
    def _task_metrics(self) -> typing.Optional[TaskMetricsConfig]:
        return typing.cast(typing.Optional[TaskMetricsConfig], jsii.get(self, "taskMetrics"))

    @builtins.property
    @jsii.member(jsii_name="taskPolicies")
    def _task_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_940a1ce0.PolicyStatement]]:
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_940a1ce0.PolicyStatement]], jsii.get(self, "taskPolicies"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, TaskStateBase).__jsii_proxy_class__ = lambda : _TaskStateBaseProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.TaskStateBaseProps",
    jsii_struct_bases=[],
    name_mapping={
        "comment": "comment",
        "heartbeat": "heartbeat",
        "input_path": "inputPath",
        "integration_pattern": "integrationPattern",
        "output_path": "outputPath",
        "result_path": "resultPath",
        "result_selector": "resultSelector",
        "timeout": "timeout",
    },
)
class TaskStateBaseProps:
    def __init__(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        heartbeat: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        input_path: typing.Optional[builtins.str] = None,
        integration_pattern: typing.Optional[IntegrationPattern] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    ) -> None:
        '''Props that are common to all tasks.

        :param comment: An optional description for this state. Default: - No comment
        :param heartbeat: Timeout for the heartbeat. Default: - None
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: - The entire task input (JSON path '$')
        :param integration_pattern: AWS Step Functions integrates with services directly in the Amazon States Language. You can control these AWS services using service integration patterns Default: - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks. ``IntegrationPattern.RUN_JOB`` for the following exceptions: ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.
        :param output_path: JSONPath expression to select select a portion of the state output to pass to the next state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: - The entire JSON node determined by the state input, the task result, and resultPath is passed to the next state (JSON path '$')
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: - Replaces the entire input with the result (JSON path '$')
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        :param timeout: Timeout for the state machine. Default: - None

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_stepfunctions as stepfunctions
            import aws_cdk.core as cdk
            
            # result_selector: Any
            
            task_state_base_props = stepfunctions.TaskStateBaseProps(
                comment="comment",
                heartbeat=cdk.Duration.minutes(30),
                input_path="inputPath",
                integration_pattern=stepfunctions.IntegrationPattern.REQUEST_RESPONSE,
                output_path="outputPath",
                result_path="resultPath",
                result_selector={
                    "result_selector_key": result_selector
                },
                timeout=cdk.Duration.minutes(30)
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__307c9672697e5ee153cbf77ce951ef6efcd1d84024758198f001f86957f346f4)
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument heartbeat", value=heartbeat, expected_type=type_hints["heartbeat"])
            check_type(argname="argument input_path", value=input_path, expected_type=type_hints["input_path"])
            check_type(argname="argument integration_pattern", value=integration_pattern, expected_type=type_hints["integration_pattern"])
            check_type(argname="argument output_path", value=output_path, expected_type=type_hints["output_path"])
            check_type(argname="argument result_path", value=result_path, expected_type=type_hints["result_path"])
            check_type(argname="argument result_selector", value=result_selector, expected_type=type_hints["result_selector"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if comment is not None:
            self._values["comment"] = comment
        if heartbeat is not None:
            self._values["heartbeat"] = heartbeat
        if input_path is not None:
            self._values["input_path"] = input_path
        if integration_pattern is not None:
            self._values["integration_pattern"] = integration_pattern
        if output_path is not None:
            self._values["output_path"] = output_path
        if result_path is not None:
            self._values["result_path"] = result_path
        if result_selector is not None:
            self._values["result_selector"] = result_selector
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: - No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def heartbeat(self) -> typing.Optional[_aws_cdk_core_f4b25747.Duration]:
        '''Timeout for the heartbeat.

        :default: - None
        '''
        result = self._values.get("heartbeat")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Duration], result)

    @builtins.property
    def input_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select part of the state to be the input to this state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        input to be the empty object {}.

        :default: - The entire task input (JSON path '$')
        '''
        result = self._values.get("input_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integration_pattern(self) -> typing.Optional[IntegrationPattern]:
        '''AWS Step Functions integrates with services directly in the Amazon States Language.

        You can control these AWS services using service integration patterns

        :default:

        - ``IntegrationPattern.REQUEST_RESPONSE`` for most tasks.
        ``IntegrationPattern.RUN_JOB`` for the following exceptions:
        ``BatchSubmitJob``, ``EmrAddStep``, ``EmrCreateCluster``, ``EmrTerminationCluster``, and ``EmrContainersStartJobRun``.

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html#connect-wait-token
        '''
        result = self._values.get("integration_pattern")
        return typing.cast(typing.Optional[IntegrationPattern], result)

    @builtins.property
    def output_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to select select a portion of the state output to pass to the next state.

        May also be the special value JsonPath.DISCARD, which will cause the effective
        output to be the empty object {}.

        :default:

        - The entire JSON node determined by the state input, the task result,
        and resultPath is passed to the next state (JSON path '$')
        '''
        result = self._values.get("output_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_path(self) -> typing.Optional[builtins.str]:
        '''JSONPath expression to indicate where to inject the state's output.

        May also be the special value JsonPath.DISCARD, which will cause the state's
        input to become its output.

        :default: - Replaces the entire input with the result (JSON path '$')
        '''
        result = self._values.get("result_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def result_selector(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''The JSON that will replace the state's raw result and become the effective result before ResultPath is applied.

        You can use ResultSelector to create a payload with values that are static
        or selected from the state's raw result.

        :default: - None

        :see: https://docs.aws.amazon.com/step-functions/latest/dg/input-output-inputpath-params.html#input-output-resultselector
        '''
        result = self._values.get("result_selector")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_core_f4b25747.Duration]:
        '''Timeout for the state machine.

        :default: - None
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TaskStateBaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(INextable)
class Wait(State, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Wait"):
    '''Define a Wait state in the state machine.

    A Wait state can be used to delay execution of the state machine for a while.

    :exampleMetadata: infused

    Example::

        convert_to_seconds = tasks.EvaluateExpression(self, "Convert to seconds",
            expression="$.waitMilliseconds / 1000",
            result_path="$.waitSeconds"
        )
        
        create_message = tasks.EvaluateExpression(self, "Create message",
            # Note: this is a string inside a string.
            expression="`Now waiting ${$.waitSeconds} seconds...`",
            runtime=lambda_.Runtime.NODEJS_14_X,
            result_path="$.message"
        )
        
        publish_message = tasks.SnsPublish(self, "Publish message",
            topic=sns.Topic(self, "cool-topic"),
            message=sfn.TaskInput.from_json_path_at("$.message"),
            result_path="$.sns"
        )
        
        wait = sfn.Wait(self, "Wait",
            time=sfn.WaitTime.seconds_path("$.waitSeconds")
        )
        
        sfn.StateMachine(self, "StateMachine",
            definition=convert_to_seconds.next(create_message).next(publish_message).next(wait)
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        time: "WaitTime",
        comment: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param time: Wait duration.
        :param comment: An optional description for this state. Default: No comment
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b0fdf5cf3bd8cc9616c029aa5e24348b697e2fe7de0f4b5f1e347f22777ed98)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WaitProps(time=time, comment=comment)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="next")
    def next(self, next: IChainable) -> "Chain":
        '''Continue normal execution with the given state.

        :param next: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d15de7a8d772f18e46645533f27397c34d11c65e901796aa2516b935c472dcea)
            check_type(argname="argument next", value=next, expected_type=type_hints["next"])
        return typing.cast("Chain", jsii.invoke(self, "next", [next]))

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        '''Return the Amazon States Language object for this state.'''
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toStateJson", []))

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[INextable]:
        '''Continuable states of this Chainable.'''
        return typing.cast(typing.List[INextable], jsii.get(self, "endStates"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-stepfunctions.WaitProps",
    jsii_struct_bases=[],
    name_mapping={"time": "time", "comment": "comment"},
)
class WaitProps:
    def __init__(
        self,
        *,
        time: "WaitTime",
        comment: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a Wait state.

        :param time: Wait duration.
        :param comment: An optional description for this state. Default: No comment

        :exampleMetadata: infused

        Example::

            convert_to_seconds = tasks.EvaluateExpression(self, "Convert to seconds",
                expression="$.waitMilliseconds / 1000",
                result_path="$.waitSeconds"
            )
            
            create_message = tasks.EvaluateExpression(self, "Create message",
                # Note: this is a string inside a string.
                expression="`Now waiting ${$.waitSeconds} seconds...`",
                runtime=lambda_.Runtime.NODEJS_14_X,
                result_path="$.message"
            )
            
            publish_message = tasks.SnsPublish(self, "Publish message",
                topic=sns.Topic(self, "cool-topic"),
                message=sfn.TaskInput.from_json_path_at("$.message"),
                result_path="$.sns"
            )
            
            wait = sfn.Wait(self, "Wait",
                time=sfn.WaitTime.seconds_path("$.waitSeconds")
            )
            
            sfn.StateMachine(self, "StateMachine",
                definition=convert_to_seconds.next(create_message).next(publish_message).next(wait)
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbc20849d2fe5c9da93b194d0874127b021b59f2b1c03721308ab0e326f0f8ce)
            check_type(argname="argument time", value=time, expected_type=type_hints["time"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "time": time,
        }
        if comment is not None:
            self._values["comment"] = comment

    @builtins.property
    def time(self) -> "WaitTime":
        '''Wait duration.'''
        result = self._values.get("time")
        assert result is not None, "Required property 'time' is missing"
        return typing.cast("WaitTime", result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An optional description for this state.

        :default: No comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WaitProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WaitTime(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-stepfunctions.WaitTime",
):
    '''Represents the Wait state which delays a state machine from continuing for a specified time.

    :see: https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-wait-state.html
    :exampleMetadata: infused

    Example::

        convert_to_seconds = tasks.EvaluateExpression(self, "Convert to seconds",
            expression="$.waitMilliseconds / 1000",
            result_path="$.waitSeconds"
        )
        
        create_message = tasks.EvaluateExpression(self, "Create message",
            # Note: this is a string inside a string.
            expression="`Now waiting ${$.waitSeconds} seconds...`",
            runtime=lambda_.Runtime.NODEJS_14_X,
            result_path="$.message"
        )
        
        publish_message = tasks.SnsPublish(self, "Publish message",
            topic=sns.Topic(self, "cool-topic"),
            message=sfn.TaskInput.from_json_path_at("$.message"),
            result_path="$.sns"
        )
        
        wait = sfn.Wait(self, "Wait",
            time=sfn.WaitTime.seconds_path("$.waitSeconds")
        )
        
        sfn.StateMachine(self, "StateMachine",
            definition=convert_to_seconds.next(create_message).next(publish_message).next(wait)
        )
    '''

    @jsii.member(jsii_name="duration")
    @builtins.classmethod
    def duration(cls, duration: _aws_cdk_core_f4b25747.Duration) -> "WaitTime":
        '''Wait a fixed amount of time.

        :param duration: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__678de0d0079eccc17c18a14c227ef1d30c694f4f4e849f7a76f2c4ead220aaf6)
            check_type(argname="argument duration", value=duration, expected_type=type_hints["duration"])
        return typing.cast("WaitTime", jsii.sinvoke(cls, "duration", [duration]))

    @jsii.member(jsii_name="secondsPath")
    @builtins.classmethod
    def seconds_path(cls, path: builtins.str) -> "WaitTime":
        '''Wait for a number of seconds stored in the state object.

        Example value: ``$.waitSeconds``

        :param path: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36881edc51a2abd08730456318e532bd50d68265d54d161d9c404233b5db675c)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast("WaitTime", jsii.sinvoke(cls, "secondsPath", [path]))

    @jsii.member(jsii_name="timestamp")
    @builtins.classmethod
    def timestamp(cls, timestamp: builtins.str) -> "WaitTime":
        '''Wait until the given ISO8601 timestamp.

        Example value: ``2016-03-14T01:59:00Z``

        :param timestamp: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de0d4462740a555c5da2dcab1a4a96c2d99a9fe82b8be6b748a70d612b0c31bc)
            check_type(argname="argument timestamp", value=timestamp, expected_type=type_hints["timestamp"])
        return typing.cast("WaitTime", jsii.sinvoke(cls, "timestamp", [timestamp]))

    @jsii.member(jsii_name="timestampPath")
    @builtins.classmethod
    def timestamp_path(cls, path: builtins.str) -> "WaitTime":
        '''Wait until a timestamp found in the state object.

        Example value: ``$.waitTimestamp``

        :param path: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70aeb14efa21330bf2d196bd40fef4dd6e07bb52d13c73e971f9e691ef051e7f)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast("WaitTime", jsii.sinvoke(cls, "timestampPath", [path]))


@jsii.implements(IActivity)
class Activity(
    _aws_cdk_core_f4b25747.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-stepfunctions.Activity",
):
    '''Define a new Step Functions Activity.

    :exampleMetadata: infused

    Example::

        activity = sfn.Activity(self, "Activity")
        
        # Read this CloudFormation Output from your application and use it to poll for work on
        # the activity.
        CfnOutput(self, "ActivityArn", value=activity.activity_arn)
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        activity_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param activity_name: The name for this activity. Default: - If not supplied, a name is generated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__331914dc8ebad71ff98ae773cbd599690e1d7904b70fc9ab7e08bff34cd2c232)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ActivityProps(activity_name=activity_name)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromActivityArn")
    @builtins.classmethod
    def from_activity_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        activity_arn: builtins.str,
    ) -> IActivity:
        '''Construct an Activity from an existing Activity ARN.

        :param scope: -
        :param id: -
        :param activity_arn: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__292efbbb82d78225a3380396debc048ad7c236c4b5f7c9744f34784562350d6d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument activity_arn", value=activity_arn, expected_type=type_hints["activity_arn"])
        return typing.cast(IActivity, jsii.sinvoke(cls, "fromActivityArn", [scope, id, activity_arn]))

    @jsii.member(jsii_name="fromActivityName")
    @builtins.classmethod
    def from_activity_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        activity_name: builtins.str,
    ) -> IActivity:
        '''Construct an Activity from an existing Activity Name.

        :param scope: -
        :param id: -
        :param activity_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02763cd57267bf7f6a6b134658bf2ac0024bb62797f88a863a4d2c4eb3106f29)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument activity_name", value=activity_name, expected_type=type_hints["activity_name"])
        return typing.cast(IActivity, jsii.sinvoke(cls, "fromActivityName", [scope, id, activity_name]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions on this Activity.

        :param identity: The principal.
        :param actions: The list of desired actions.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d1a97ff5bf7a80c80abb0b1c55ed1cb32f69e70e56b308f7cc0435d4ddb35f0)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grant", [identity, *actions]))

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
        '''Return the given named metric for this Activity.

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

        :default: sum over 5 minutes
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecd3d237ff1248ee16242119757c6379cd2c9b806377d27550337396d8a0274f)
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

    @jsii.member(jsii_name="metricFailed")
    def metric_failed(
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
        '''Metric for the number of times this activity fails.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricFailed", [props]))

    @jsii.member(jsii_name="metricHeartbeatTimedOut")
    def metric_heartbeat_timed_out(
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
        '''Metric for the number of times the heartbeat times out for this activity.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricHeartbeatTimedOut", [props]))

    @jsii.member(jsii_name="metricRunTime")
    def metric_run_time(
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
        '''The interval, in milliseconds, between the time the activity starts and the time it closes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: average over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricRunTime", [props]))

    @jsii.member(jsii_name="metricScheduled")
    def metric_scheduled(
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
        '''Metric for the number of times this activity is scheduled.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricScheduled", [props]))

    @jsii.member(jsii_name="metricScheduleTime")
    def metric_schedule_time(
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
        '''The interval, in milliseconds, for which the activity stays in the schedule state.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: average over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricScheduleTime", [props]))

    @jsii.member(jsii_name="metricStarted")
    def metric_started(
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
        '''Metric for the number of times this activity is started.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricStarted", [props]))

    @jsii.member(jsii_name="metricSucceeded")
    def metric_succeeded(
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
        '''Metric for the number of times this activity succeeds.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricSucceeded", [props]))

    @jsii.member(jsii_name="metricTime")
    def metric_time(
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
        '''The interval, in milliseconds, between the time the activity is scheduled and the time it closes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: average over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricTime", [props]))

    @jsii.member(jsii_name="metricTimedOut")
    def metric_timed_out(
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
        '''Metric for the number of times this activity times out.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: sum over 5 minutes
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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricTimedOut", [props]))

    @builtins.property
    @jsii.member(jsii_name="activityArn")
    def activity_arn(self) -> builtins.str:
        '''The ARN of the activity.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "activityArn"))

    @builtins.property
    @jsii.member(jsii_name="activityName")
    def activity_name(self) -> builtins.str:
        '''The name of the activity.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "activityName"))


@jsii.implements(IChainable)
class Chain(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Chain"):
    '''A collection of states to chain onto.

    A Chain has a start and zero or more chainable ends. If there are
    zero ends, calling next() on the Chain will fail.

    :exampleMetadata: infused

    Example::

        # Define a state machine with one Pass state
        child = sfn.StateMachine(self, "ChildStateMachine",
            definition=sfn.Chain.start(sfn.Pass(self, "PassState"))
        )
        
        # Include the state machine in a Task state with callback pattern
        task = tasks.StepFunctionsStartExecution(self, "ChildTask",
            state_machine=child,
            integration_pattern=sfn.IntegrationPattern.WAIT_FOR_TASK_TOKEN,
            input=sfn.TaskInput.from_object({
                "token": sfn.JsonPath.task_token,
                "foo": "bar"
            }),
            name="MyExecutionName"
        )
        
        # Define a second state machine with the Task state above
        sfn.StateMachine(self, "ParentStateMachine",
            definition=task
        )
    '''

    @jsii.member(jsii_name="custom")
    @builtins.classmethod
    def custom(
        cls,
        start_state: State,
        end_states: typing.Sequence[INextable],
        last_added: IChainable,
    ) -> "Chain":
        '''Make a Chain with specific start and end states, and a last-added Chainable.

        :param start_state: -
        :param end_states: -
        :param last_added: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__822895a97fed65b61a96072c38017b2213aea423992c3394f2ad787fb2bb8096)
            check_type(argname="argument start_state", value=start_state, expected_type=type_hints["start_state"])
            check_type(argname="argument end_states", value=end_states, expected_type=type_hints["end_states"])
            check_type(argname="argument last_added", value=last_added, expected_type=type_hints["last_added"])
        return typing.cast("Chain", jsii.sinvoke(cls, "custom", [start_state, end_states, last_added]))

    @jsii.member(jsii_name="sequence")
    @builtins.classmethod
    def sequence(cls, start: IChainable, next: IChainable) -> "Chain":
        '''Make a Chain with the start from one chain and the ends from another.

        :param start: -
        :param next: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a707399f78c9415fdc8c3e4d5eeaa2df4537420598870aebea65141091b0334)
            check_type(argname="argument start", value=start, expected_type=type_hints["start"])
            check_type(argname="argument next", value=next, expected_type=type_hints["next"])
        return typing.cast("Chain", jsii.sinvoke(cls, "sequence", [start, next]))

    @jsii.member(jsii_name="start")
    @builtins.classmethod
    def start(cls, state: IChainable) -> "Chain":
        '''Begin a new Chain from one chainable.

        :param state: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e46f3eb6aaa9352c718987e98090b3b9fabe7949282ef7df717d7cd6727e0c9b)
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
        return typing.cast("Chain", jsii.sinvoke(cls, "start", [state]))

    @jsii.member(jsii_name="next")
    def next(self, next: IChainable) -> "Chain":
        '''Continue normal execution with the given state.

        :param next: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5e38e8298515bb8c86487c100d8dc32628e1e013765cd19ac49a31a087ac219)
            check_type(argname="argument next", value=next, expected_type=type_hints["next"])
        return typing.cast("Chain", jsii.invoke(self, "next", [next]))

    @jsii.member(jsii_name="toSingleState")
    def to_single_state(
        self,
        id: builtins.str,
        *,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> "Parallel":
        '''Return a single state that encompasses all states in the chain.

        This can be used to add error handling to a sequence of states.

        Be aware that this changes the result of the inner state machine
        to be an array with the result of the state machine in it. Adjust
        your paths accordingly. For example, change 'outputPath' to
        '$[0]'.

        :param id: -
        :param comment: An optional description for this state. Default: No comment
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param output_path: JSONPath expression to select part of the state to be the output to this state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: $
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: $
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6326969138cd78e63eb7912ec4498438274fa32fb4ada6c5c56a65bfa3b64e88)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ParallelProps(
            comment=comment,
            input_path=input_path,
            output_path=output_path,
            result_path=result_path,
            result_selector=result_selector,
        )

        return typing.cast("Parallel", jsii.invoke(self, "toSingleState", [id, props]))

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[INextable]:
        '''The chainable end state(s) of this chain.'''
        return typing.cast(typing.List[INextable], jsii.get(self, "endStates"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''Identify this Chain.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="startState")
    def start_state(self) -> State:
        '''The start state of this chain.'''
        return typing.cast(State, jsii.get(self, "startState"))


class Choice(
    State,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-stepfunctions.Choice",
):
    '''Define a Choice in the state machine.

    A choice state can be used to make decisions based on the execution
    state.

    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_lambda as lambda_
        
        # submit_lambda: lambda.Function
        # get_status_lambda: lambda.Function
        
        
        submit_job = tasks.LambdaInvoke(self, "Submit Job",
            lambda_function=submit_lambda,
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload"
        )
        
        wait_x = sfn.Wait(self, "Wait X Seconds",
            time=sfn.WaitTime.seconds_path("$.waitSeconds")
        )
        
        get_status = tasks.LambdaInvoke(self, "Get Job Status",
            lambda_function=get_status_lambda,
            # Pass just the field named "guid" into the Lambda, put the
            # Lambda's result in a field called "status" in the response
            input_path="$.guid",
            output_path="$.Payload"
        )
        
        job_failed = sfn.Fail(self, "Job Failed",
            cause="AWS Batch Job Failed",
            error="DescribeJob returned FAILED"
        )
        
        final_status = tasks.LambdaInvoke(self, "Get Final Job Status",
            lambda_function=get_status_lambda,
            # Use "guid" field as input
            input_path="$.guid",
            output_path="$.Payload"
        )
        
        definition = submit_job.next(wait_x).next(get_status).next(sfn.Choice(self, "Job Complete?").when(sfn.Condition.string_equals("$.status", "FAILED"), job_failed).when(sfn.Condition.string_equals("$.status", "SUCCEEDED"), final_status).otherwise(wait_x))
        
        sfn.StateMachine(self, "StateMachine",
            definition=definition,
            timeout=Duration.minutes(5)
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param comment: An optional description for this state. Default: No comment
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param output_path: JSONPath expression to select part of the state to be the output to this state. May also be the special value DISCARD, which will cause the effective output to be the empty object {}. Default: $
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae8e962a8a63254ccdf241046449d65a87d800c7169e19739dd3d80c9e0adce9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ChoiceProps(
            comment=comment, input_path=input_path, output_path=output_path
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="afterwards")
    def afterwards(
        self,
        *,
        include_error_handlers: typing.Optional[builtins.bool] = None,
        include_otherwise: typing.Optional[builtins.bool] = None,
    ) -> Chain:
        '''Return a Chain that contains all reachable end states from this Choice.

        Use this to combine all possible choice paths back.

        :param include_error_handlers: Whether to include error handling states. If this is true, all states which are error handlers (added through 'onError') and states reachable via error handlers will be included as well. Default: false
        :param include_otherwise: Whether to include the default/otherwise transition for the current Choice state. If this is true and the current Choice does not have a default outgoing transition, one will be added included when .next() is called on the chain. Default: false
        '''
        options = AfterwardsOptions(
            include_error_handlers=include_error_handlers,
            include_otherwise=include_otherwise,
        )

        return typing.cast(Chain, jsii.invoke(self, "afterwards", [options]))

    @jsii.member(jsii_name="otherwise")
    def otherwise(self, def_: IChainable) -> "Choice":
        '''If none of the given conditions match, continue execution with the given state.

        If no conditions match and no otherwise() has been given, an execution
        error will be raised.

        :param def_: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d08d00f2cf8dc628de31a48cd53985b4fe3acab43d8a243ae68cb61efd0f92bd)
            check_type(argname="argument def_", value=def_, expected_type=type_hints["def_"])
        return typing.cast("Choice", jsii.invoke(self, "otherwise", [def_]))

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        '''Return the Amazon States Language object for this state.'''
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toStateJson", []))

    @jsii.member(jsii_name="when")
    def when(self, condition: Condition, next: IChainable) -> "Choice":
        '''If the given condition matches, continue execution with the given state.

        :param condition: -
        :param next: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21714eb93437720e076e1fce6674a312cfffe5203f6c7af7f0c98f346f71de33)
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
            check_type(argname="argument next", value=next, expected_type=type_hints["next"])
        return typing.cast("Choice", jsii.invoke(self, "when", [condition, next]))

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[INextable]:
        '''Continuable states of this Chainable.'''
        return typing.cast(typing.List[INextable], jsii.get(self, "endStates"))


@jsii.implements(IChainable, INextable)
class CustomState(
    State,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-stepfunctions.CustomState",
):
    '''State defined by supplying Amazon States Language (ASL) in the state machine.

    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_dynamodb as dynamodb
        
        
        # create a table
        table = dynamodb.Table(self, "montable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        final_status = sfn.Pass(self, "final step")
        
        # States language JSON to put an item into DynamoDB
        # snippet generated from https://docs.aws.amazon.com/step-functions/latest/dg/tutorial-code-snippet.html#tutorial-code-snippet-1
        state_json = {
            "Type": "Task",
            "Resource": "arn:aws:states:::dynamodb:putItem",
            "Parameters": {
                "TableName": table.table_name,
                "Item": {
                    "id": {
                        "S": "MyEntry"
                    }
                }
            },
            "ResultPath": null
        }
        
        # custom state which represents a task to insert data into DynamoDB
        custom = sfn.CustomState(self, "my custom task",
            state_json=state_json
        )
        
        chain = sfn.Chain.start(custom).next(final_status)
        
        sm = sfn.StateMachine(self, "StateMachine",
            definition=chain,
            timeout=Duration.seconds(30)
        )
        
        # don't forget permissions. You need to assign them
        table.grant_write_data(sm)
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        state_json: typing.Mapping[builtins.str, typing.Any],
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param state_json: Amazon States Language (JSON-based) definition of the state.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdf73075438ababf63fc26082692154d02e4ae381e3aed0b67d05ff092bea3e0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CustomStateProps(state_json=state_json)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="next")
    def next(self, next: IChainable) -> Chain:
        '''Continue normal execution with the given state.

        :param next: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed2d020e66c427ffad63a719bf8d94b5f0f0e49df92b3bb6baf8e40fd2a4f9b6)
            check_type(argname="argument next", value=next, expected_type=type_hints["next"])
        return typing.cast(Chain, jsii.invoke(self, "next", [next]))

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        '''Returns the Amazon States Language object for this state.'''
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toStateJson", []))

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[INextable]:
        '''Continuable states of this Chainable.'''
        return typing.cast(typing.List[INextable], jsii.get(self, "endStates"))


class Fail(State, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Fail"):
    '''Define a Fail state in the state machine.

    Reaching a Fail state terminates the state execution in failure.

    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_lambda as lambda_
        
        # submit_lambda: lambda.Function
        # get_status_lambda: lambda.Function
        
        
        submit_job = tasks.LambdaInvoke(self, "Submit Job",
            lambda_function=submit_lambda,
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload"
        )
        
        wait_x = sfn.Wait(self, "Wait X Seconds",
            time=sfn.WaitTime.seconds_path("$.waitSeconds")
        )
        
        get_status = tasks.LambdaInvoke(self, "Get Job Status",
            lambda_function=get_status_lambda,
            # Pass just the field named "guid" into the Lambda, put the
            # Lambda's result in a field called "status" in the response
            input_path="$.guid",
            output_path="$.Payload"
        )
        
        job_failed = sfn.Fail(self, "Job Failed",
            cause="AWS Batch Job Failed",
            error="DescribeJob returned FAILED"
        )
        
        final_status = tasks.LambdaInvoke(self, "Get Final Job Status",
            lambda_function=get_status_lambda,
            # Use "guid" field as input
            input_path="$.guid",
            output_path="$.Payload"
        )
        
        definition = submit_job.next(wait_x).next(get_status).next(sfn.Choice(self, "Job Complete?").when(sfn.Condition.string_equals("$.status", "FAILED"), job_failed).when(sfn.Condition.string_equals("$.status", "SUCCEEDED"), final_status).otherwise(wait_x))
        
        sfn.StateMachine(self, "StateMachine",
            definition=definition,
            timeout=Duration.minutes(5)
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cause: typing.Optional[builtins.str] = None,
        comment: typing.Optional[builtins.str] = None,
        error: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cause: A description for the cause of the failure. Default: No description
        :param comment: An optional description for this state. Default: No comment
        :param error: Error code used to represent this failure. Default: No error code
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44d368bdd4e9e7daf66152acddb0cd74184a357fd1eaffed2defdfbbd853018b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FailProps(cause=cause, comment=comment, error=error)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        '''Return the Amazon States Language object for this state.'''
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toStateJson", []))

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[INextable]:
        '''Continuable states of this Chainable.'''
        return typing.cast(typing.List[INextable], jsii.get(self, "endStates"))


@jsii.implements(INextable)
class Map(State, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Map"):
    '''Define a Map state in the state machine.

    A ``Map`` state can be used to run a set of steps for each element of an input array.
    A Map state will execute the same steps for multiple entries of an array in the state input.

    While the Parallel state executes multiple branches of steps using the same input, a Map state
    will execute the same steps for multiple entries of an array in the state input.

    :see: https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-map-state.html
    :exampleMetadata: infused

    Example::

        map = sfn.Map(self, "Map State",
            max_concurrency=1,
            items_path=sfn.JsonPath.string_at("$.inputForMap")
        )
        map.iterator(sfn.Pass(self, "Pass State"))
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        items_path: typing.Optional[builtins.str] = None,
        max_concurrency: typing.Optional[jsii.Number] = None,
        output_path: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param comment: An optional description for this state. Default: No comment
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param items_path: JSONPath expression to select the array to iterate over. Default: $
        :param max_concurrency: MaxConcurrency. An upper bound on the number of iterations you want running at once. Default: - full concurrency
        :param output_path: JSONPath expression to select part of the state to be the output to this state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: $
        :param parameters: The JSON that you want to override your default iteration input. Default: $
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: $
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e6235dea37838b2d99a56b075ebb42e489029b8c7e7e0e9e3f2b59ecdb54124)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MapProps(
            comment=comment,
            input_path=input_path,
            items_path=items_path,
            max_concurrency=max_concurrency,
            output_path=output_path,
            parameters=parameters,
            result_path=result_path,
            result_selector=result_selector,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addCatch")
    def add_catch(
        self,
        handler: IChainable,
        *,
        errors: typing.Optional[typing.Sequence[builtins.str]] = None,
        result_path: typing.Optional[builtins.str] = None,
    ) -> "Map":
        '''Add a recovery handler for this state.

        When a particular error occurs, execution will continue at the error
        handler instead of failing the state machine execution.

        :param handler: -
        :param errors: Errors to recover from by going to the given state. A list of error strings to retry, which can be either predefined errors (for example Errors.NoChoiceMatched) or a self-defined error. Default: All errors
        :param result_path: JSONPath expression to indicate where to inject the error data. May also be the special value DISCARD, which will cause the error data to be discarded. Default: $
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56259cb2b8607b1718ac094744f7021d830cf1a9fec6117bdc3b05ffbfc9464e)
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
        props = CatchProps(errors=errors, result_path=result_path)

        return typing.cast("Map", jsii.invoke(self, "addCatch", [handler, props]))

    @jsii.member(jsii_name="addRetry")
    def add_retry(
        self,
        *,
        backoff_rate: typing.Optional[jsii.Number] = None,
        errors: typing.Optional[typing.Sequence[builtins.str]] = None,
        interval: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        max_attempts: typing.Optional[jsii.Number] = None,
    ) -> "Map":
        '''Add retry configuration for this state.

        This controls if and how the execution will be retried if a particular
        error occurs.

        :param backoff_rate: Multiplication for how much longer the wait interval gets on every retry. Default: 2
        :param errors: Errors to retry. A list of error strings to retry, which can be either predefined errors (for example Errors.NoChoiceMatched) or a self-defined error. Default: All errors
        :param interval: How many seconds to wait initially before retrying. Default: Duration.seconds(1)
        :param max_attempts: How many times to retry this particular error. May be 0 to disable retry for specific errors (in case you have a catch-all retry policy). Default: 3
        '''
        props = RetryProps(
            backoff_rate=backoff_rate,
            errors=errors,
            interval=interval,
            max_attempts=max_attempts,
        )

        return typing.cast("Map", jsii.invoke(self, "addRetry", [props]))

    @jsii.member(jsii_name="iterator")
    def iterator(self, iterator: IChainable) -> "Map":
        '''Define iterator state machine in Map.

        :param iterator: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96b5e01c70471b6657eb375f12fb6d9fc6f4e9704ccba0acbf8e45fb2e4b6b39)
            check_type(argname="argument iterator", value=iterator, expected_type=type_hints["iterator"])
        return typing.cast("Map", jsii.invoke(self, "iterator", [iterator]))

    @jsii.member(jsii_name="next")
    def next(self, next: IChainable) -> Chain:
        '''Continue normal execution with the given state.

        :param next: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b25949969dfd2a8cdb1a4b406df8098109d566af0a74af47f7cfbde0bd8a9d68)
            check_type(argname="argument next", value=next, expected_type=type_hints["next"])
        return typing.cast(Chain, jsii.invoke(self, "next", [next]))

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        '''Return the Amazon States Language object for this state.'''
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toStateJson", []))

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[builtins.str]:
        '''Validate this state.'''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "validate", []))

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[INextable]:
        '''Continuable states of this Chainable.'''
        return typing.cast(typing.List[INextable], jsii.get(self, "endStates"))


@jsii.implements(INextable)
class Parallel(
    State,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-stepfunctions.Parallel",
):
    '''Define a Parallel state in the state machine.

    A Parallel state can be used to run one or more state machines at the same
    time.

    The Result of a Parallel state is an array of the results of its substatemachines.

    :exampleMetadata: nofixture infused

    Example::

        from aws_cdk.core import Stack
        from constructs import Construct
        import aws_cdk.aws_stepfunctions as sfn
        
        class MyJob(sfn.StateMachineFragment):
        
            def __init__(self, parent, id, *, jobFlavor):
                super().__init__(parent, id)
        
                choice = sfn.Choice(self, "Choice").when(sfn.Condition.string_equals("$.branch", "left"), sfn.Pass(self, "Left Branch")).when(sfn.Condition.string_equals("$.branch", "right"), sfn.Pass(self, "Right Branch"))
        
                # ...
        
                self.start_state = choice
                self.end_states = choice.afterwards().end_states
        
        class MyStack(Stack):
            def __init__(self, scope, id):
                super().__init__(scope, id)
                # Do 3 different variants of MyJob in parallel
                parallel = sfn.Parallel(self, "All jobs").branch(MyJob(self, "Quick", job_flavor="quick").prefix_states()).branch(MyJob(self, "Medium", job_flavor="medium").prefix_states()).branch(MyJob(self, "Slow", job_flavor="slow").prefix_states())
        
                sfn.StateMachine(self, "MyStateMachine",
                    definition=parallel
                )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
        result_path: typing.Optional[builtins.str] = None,
        result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param comment: An optional description for this state. Default: No comment
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param output_path: JSONPath expression to select part of the state to be the output to this state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: $
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: $
        :param result_selector: The JSON that will replace the state's raw result and become the effective result before ResultPath is applied. You can use ResultSelector to create a payload with values that are static or selected from the state's raw result. Default: - None
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5acb3644c98a16194318a6f938596c71c96b2933cfaad5a284aefb8aadd1b32c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ParallelProps(
            comment=comment,
            input_path=input_path,
            output_path=output_path,
            result_path=result_path,
            result_selector=result_selector,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addCatch")
    def add_catch(
        self,
        handler: IChainable,
        *,
        errors: typing.Optional[typing.Sequence[builtins.str]] = None,
        result_path: typing.Optional[builtins.str] = None,
    ) -> "Parallel":
        '''Add a recovery handler for this state.

        When a particular error occurs, execution will continue at the error
        handler instead of failing the state machine execution.

        :param handler: -
        :param errors: Errors to recover from by going to the given state. A list of error strings to retry, which can be either predefined errors (for example Errors.NoChoiceMatched) or a self-defined error. Default: All errors
        :param result_path: JSONPath expression to indicate where to inject the error data. May also be the special value DISCARD, which will cause the error data to be discarded. Default: $
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76af50cf1b4bf1c270e7e409b5436867f2439ecd1b43934076dce7f62175b320)
            check_type(argname="argument handler", value=handler, expected_type=type_hints["handler"])
        props = CatchProps(errors=errors, result_path=result_path)

        return typing.cast("Parallel", jsii.invoke(self, "addCatch", [handler, props]))

    @jsii.member(jsii_name="addRetry")
    def add_retry(
        self,
        *,
        backoff_rate: typing.Optional[jsii.Number] = None,
        errors: typing.Optional[typing.Sequence[builtins.str]] = None,
        interval: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        max_attempts: typing.Optional[jsii.Number] = None,
    ) -> "Parallel":
        '''Add retry configuration for this state.

        This controls if and how the execution will be retried if a particular
        error occurs.

        :param backoff_rate: Multiplication for how much longer the wait interval gets on every retry. Default: 2
        :param errors: Errors to retry. A list of error strings to retry, which can be either predefined errors (for example Errors.NoChoiceMatched) or a self-defined error. Default: All errors
        :param interval: How many seconds to wait initially before retrying. Default: Duration.seconds(1)
        :param max_attempts: How many times to retry this particular error. May be 0 to disable retry for specific errors (in case you have a catch-all retry policy). Default: 3
        '''
        props = RetryProps(
            backoff_rate=backoff_rate,
            errors=errors,
            interval=interval,
            max_attempts=max_attempts,
        )

        return typing.cast("Parallel", jsii.invoke(self, "addRetry", [props]))

    @jsii.member(jsii_name="bindToGraph")
    def bind_to_graph(self, graph: StateGraph) -> None:
        '''Overwrites State.bindToGraph. Adds branches to the Parallel state here so that any necessary prefixes are appended first.

        :param graph: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2b7e228632b7817982a8f2ce72bc64ad977459233dcf4bddc8ba9de9e1f07b3)
            check_type(argname="argument graph", value=graph, expected_type=type_hints["graph"])
        return typing.cast(None, jsii.invoke(self, "bindToGraph", [graph]))

    @jsii.member(jsii_name="branch")
    def branch(self, *branches: IChainable) -> "Parallel":
        '''Define one or more branches to run in parallel.

        :param branches: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b59203d3b787dd87e1effb815faf87767f49ab0ed7f05ebc149fae5a9e24a57)
            check_type(argname="argument branches", value=branches, expected_type=typing.Tuple[type_hints["branches"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast("Parallel", jsii.invoke(self, "branch", [*branches]))

    @jsii.member(jsii_name="next")
    def next(self, next: IChainable) -> Chain:
        '''Continue normal execution with the given state.

        :param next: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ab166a9f8bf802e952c670ffeafc101a6fe90a17fc5a7a4606f5da1d03429f9)
            check_type(argname="argument next", value=next, expected_type=type_hints["next"])
        return typing.cast(Chain, jsii.invoke(self, "next", [next]))

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        '''Return the Amazon States Language object for this state.'''
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toStateJson", []))

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[builtins.str]:
        '''Validate this state.'''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "validate", []))

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[INextable]:
        '''Continuable states of this Chainable.'''
        return typing.cast(typing.List[INextable], jsii.get(self, "endStates"))


@jsii.implements(INextable)
class Pass(State, metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-stepfunctions.Pass"):
    '''Define a Pass in the state machine.

    A Pass state can be used to transform the current execution's state.

    :exampleMetadata: infused

    Example::

        choice = sfn.Choice(self, "Did it work?")
        
        # Add conditions with .when()
        success_state = sfn.Pass(self, "SuccessState")
        failure_state = sfn.Pass(self, "FailureState")
        choice.when(sfn.Condition.string_equals("$.status", "SUCCESS"), success_state)
        choice.when(sfn.Condition.number_greater_than("$.attempts", 5), failure_state)
        
        # Use .otherwise() to indicate what should be done if none of the conditions match
        try_again_state = sfn.Pass(self, "TryAgainState")
        choice.otherwise(try_again_state)
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        comment: typing.Optional[builtins.str] = None,
        input_path: typing.Optional[builtins.str] = None,
        output_path: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        result: typing.Optional[Result] = None,
        result_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param comment: An optional description for this state. Default: No comment
        :param input_path: JSONPath expression to select part of the state to be the input to this state. May also be the special value JsonPath.DISCARD, which will cause the effective input to be the empty object {}. Default: $
        :param output_path: JSONPath expression to select part of the state to be the output to this state. May also be the special value JsonPath.DISCARD, which will cause the effective output to be the empty object {}. Default: $
        :param parameters: Parameters pass a collection of key-value pairs, either static values or JSONPath expressions that select from the input. Default: No parameters
        :param result: If given, treat as the result of this operation. Can be used to inject or replace the current execution state. Default: No injected result
        :param result_path: JSONPath expression to indicate where to inject the state's output. May also be the special value JsonPath.DISCARD, which will cause the state's input to become its output. Default: $
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea1af4c8f19dbcfff56e69de6f46cf028d1459a78fe7c25a851515855ddb4fac)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PassProps(
            comment=comment,
            input_path=input_path,
            output_path=output_path,
            parameters=parameters,
            result=result,
            result_path=result_path,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="next")
    def next(self, next: IChainable) -> Chain:
        '''Continue normal execution with the given state.

        :param next: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6746058a8497d5e3501a16b0ebf2cf161abf858fe966b7393a0646b1ca494ff6)
            check_type(argname="argument next", value=next, expected_type=type_hints["next"])
        return typing.cast(Chain, jsii.invoke(self, "next", [next]))

    @jsii.member(jsii_name="toStateJson")
    def to_state_json(self) -> typing.Mapping[typing.Any, typing.Any]:
        '''Return the Amazon States Language object for this state.'''
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.invoke(self, "toStateJson", []))

    @builtins.property
    @jsii.member(jsii_name="endStates")
    def end_states(self) -> typing.List[INextable]:
        '''Continuable states of this Chainable.'''
        return typing.cast(typing.List[INextable], jsii.get(self, "endStates"))


__all__ = [
    "Activity",
    "ActivityProps",
    "AfterwardsOptions",
    "CatchProps",
    "CfnActivity",
    "CfnActivityProps",
    "CfnStateMachine",
    "CfnStateMachineProps",
    "Chain",
    "Choice",
    "ChoiceProps",
    "Condition",
    "Context",
    "CustomState",
    "CustomStateProps",
    "Data",
    "Errors",
    "Fail",
    "FailProps",
    "FieldUtils",
    "FindStateOptions",
    "IActivity",
    "IChainable",
    "INextable",
    "IStateMachine",
    "IStepFunctionsTask",
    "InputType",
    "IntegrationPattern",
    "JsonPath",
    "LogLevel",
    "LogOptions",
    "Map",
    "MapProps",
    "Parallel",
    "ParallelProps",
    "Pass",
    "PassProps",
    "Result",
    "RetryProps",
    "ServiceIntegrationPattern",
    "SingleStateOptions",
    "State",
    "StateGraph",
    "StateMachine",
    "StateMachineFragment",
    "StateMachineProps",
    "StateMachineType",
    "StateProps",
    "StateTransitionMetric",
    "StepFunctionsTaskConfig",
    "Succeed",
    "SucceedProps",
    "Task",
    "TaskInput",
    "TaskMetricsConfig",
    "TaskProps",
    "TaskStateBase",
    "TaskStateBaseProps",
    "Wait",
    "WaitProps",
    "WaitTime",
]

publication.publish()

def _typecheckingstub__584c3351df71821cf953cc2852b5defea4c2bb54fb5de252128f3a3c0bf78d33(
    *,
    activity_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d7d0ccf7be9eb2476e244176cdd664c3743097f7a9f26e8a645c14c2f9687a2(
    *,
    include_error_handlers: typing.Optional[builtins.bool] = None,
    include_otherwise: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f55af4b95f00bfb05c0159df065d2a46b70397d8a8a380607be1cd8e7dce818(
    *,
    errors: typing.Optional[typing.Sequence[builtins.str]] = None,
    result_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1daf032421a6dc31f1b05b5c3ef5dab91638fa27976f33d7f238fddc02ea0da(
    scope: _aws_cdk_core_f4b25747.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    tags: typing.Optional[typing.Sequence[typing.Union[CfnActivity.TagsEntryProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26845b59f7fb07c8387baf3a4f9ca72e8695bdc09fd2c245456b6444fb7f456b(
    inspector: _aws_cdk_core_f4b25747.TreeInspector,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3085158330b77db8234e9c4201ba7e05662d1ef0d9dad0740077f41072692184(
    props: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3389c4de048d503ef3f8fc6214c87dfbb3d11ac185baa8b112c499202ef3fbd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbe1434fb9bafeef1e62800c16045ab230936ea31431d7f75c6324b98da697d7(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc121bb17a642c051525e8dbe183eaadaa4afd72e04df8d7d70198aa60a9c603(
    *,
    name: builtins.str,
    tags: typing.Optional[typing.Sequence[typing.Union[CfnActivity.TagsEntryProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff90c7e33bb5aba816833afb5965478a908f9d87f25354e1710af5795250019f(
    scope: _aws_cdk_core_f4b25747.Construct,
    id: builtins.str,
    *,
    role_arn: builtins.str,
    definition: typing.Any = None,
    definition_s3_location: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnStateMachine.S3LocationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    definition_string: typing.Optional[builtins.str] = None,
    definition_substitutions: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Mapping[builtins.str, typing.Any]]] = None,
    logging_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnStateMachine.LoggingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    state_machine_type: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[CfnStateMachine.TagsEntryProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    tracing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnStateMachine.TracingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c7ca4899ad3ec27f0be73a426dba404b5088f6a0e09d867df396999b7ac3147(
    inspector: _aws_cdk_core_f4b25747.TreeInspector,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c464593fee0e40c67626c240fce34cbc7bbb45f5d7412e97a8de0df92804b83c(
    props: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__321835c0ad1b15082dbb2019c7b37a99b421ae4221e1579bfa85c9da9eb88e1c(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35443f3b6328c55a2e194d6699fd214b4ae70ff1a4543cfd32e27aea85b1b64f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c57a09ca865900be7e74a8c4324c2141bf9d98c4391343b788df000ca86ce2b0(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnStateMachine.S3LocationProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__724b2455ade0b5a6ac6149832c60f0c30a2743b6aeeef2d482d3bafe94f7a09d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d46799eead8268d74deabe7fc9cd05e858775c666ce1c97390bda11ed0d4337c(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Mapping[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57144e55d1c58655b17e341dfa0e9be6d0f60953765045857da3eb5e8ef32e55(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnStateMachine.LoggingConfigurationProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee1632fca990d5d684651d1801150322e8522dcb2dad7b373f2475b2d3fb50c8(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1eafea1651731878943bfa9ece4684df2d7b41c62f328d986893ce759197fa99(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce9ed5153277e16dfd1e6c26337d96ec20a6b7226f466cb89f6bda4db97b5349(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnStateMachine.TracingConfigurationProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1ec312887402e839eff6b5f98571af91f35bdf71b3072c402a7d735b686b89c(
    *,
    log_group_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13abb8df480e0b4a3f3e0419de964941def29cedd011c0b2b79a7fedbad5d298(
    *,
    cloud_watch_logs_log_group: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnStateMachine.CloudWatchLogsLogGroupProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5764fed2df18aeb671ae245f634f006d8c85cf7c760a687539d4533164a573a3(
    *,
    destinations: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnStateMachine.LogDestinationProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    include_execution_data: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    level: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49b1c4b8bc4fe296ed687aa62efe51a9220452c93f09e68b36558eb1c0bd8bf1(
    *,
    bucket: builtins.str,
    key: builtins.str,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b268add728e11421a9683c6b4b6d20c9d8bd445b38dc0f1ca24b921af84047d6(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9adb57c144f02482ad65083eb837116bac324772c7473a8284250f8786509f0b(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1f366e4958852bcc1ef5b964e760137e591d192eb367ec75d4d35278b47d69a(
    *,
    role_arn: builtins.str,
    definition: typing.Any = None,
    definition_s3_location: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnStateMachine.S3LocationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    definition_string: typing.Optional[builtins.str] = None,
    definition_substitutions: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Mapping[builtins.str, typing.Any]]] = None,
    logging_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnStateMachine.LoggingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    state_machine_type: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[CfnStateMachine.TagsEntryProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    tracing_configuration: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnStateMachine.TracingConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ac01f94b0860aca9ab54646b25e9c773e10e8f5407192cd6d25ea68240ead75(
    *,
    comment: typing.Optional[builtins.str] = None,
    input_path: typing.Optional[builtins.str] = None,
    output_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06fa28bee94a8e66dde9f678596a1b2b8c1b81483f7a6b443c80f59ab422d599(
    *conditions: Condition,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e08cdcf85b8839197b7eaed0d3b3b67a25f1b6c65489cc06b61bce61f8e35df0(
    variable: builtins.str,
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24219323ed35aeb740044cc130782b78efbf64045ba4c07bb2a05c1d6ac00648(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01c40a33ddab4c378ee37e6d0267afbc79ddad8d3bf70a7d54f9015bfafcbbc3(
    variable: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29f431beb7641d5f1248823cb3a4986794d36fb00a5d2068750af2386677f73c(
    variable: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd3bc8d7574eb3adafe5678f6ce3cd03388e2007f2f33eaec60ea793282c6d58(
    variable: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37f5f52f2fd73ef9f7ea91da166f2243bef2b82ae281ee1128e87f1ded3dfc76(
    variable: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38f3e8d6d585aaa07f0e7d0a14d25b5066f3e25f1df698c1318d92e0459b95fa(
    variable: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3865901af3d4f1c3453ca902202c4dd43c56071b23a4f9bb9a3d4c619c7fc743(
    variable: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__028d007feb2ec2563bd4365fb9e32bd2615bd2d9d871934a6cdb8c5670f83f38(
    variable: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63ef7cdfd2393b60051b09094dcc8d8e9bc5254033c369b022a72201b2997751(
    variable: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2dc6efe6d876559015c0a285483cab48833c6c197922f172dabe3de389b8959(
    variable: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abb32d29c7bae7b58544fcf0eb1041489b11ff4c36e27e45a256f5e85bc25641(
    variable: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91d62a700a1f92610d7a5b972cc91f02b6177066f50cbbd9e5d1db9c911a12fd(
    variable: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a764190a75bb3860279e68523619998c985f6679e42555299b808244dc33216b(
    variable: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fdbce2eae74ab8cf689e97335a1374fded9679b4fadaac4778f5b5c90c7697e(
    condition: Condition,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8c9238ebfebfe1b3cd59b8ab67874c93bf517db63e720cc486819614e094109(
    variable: builtins.str,
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4dccd17b7d30ea5845ab4b8b80f1bfcd933600692e7c9a28cbf03195bb098a8(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56b5448ac5e28537e1fcf38c074217fabe9610b96bef90f97208e83f4ee46c15(
    variable: builtins.str,
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99426e2e1e6dd99d98d3e1642519a629aed11e55112638754befd675f59699fe(
    variable: builtins.str,
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8928f00081b78a988b441260d48389451e38f7a5f50d2261eb26c64a336987d4(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23a1571266826f815b9dec648bfa3b9df15bfdcba8618272c491d7cd63f8f3c6(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2bf141c098364d142fce16016fb59b0ae763f9c08ba76cfb1fcb07047a6581c(
    variable: builtins.str,
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5b39708d63b8d650259dddbcbfd9a8054c0d83e8562eec69d0fec8db11eee39(
    variable: builtins.str,
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__685aae99850c6837c71e9fb83de53cc2913be4cd416ad3262bdb8ab792605ee2(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1184c38cb406a885b8e77eea083d8f4f7ab3e55f31b995fcccddc36d35e31a15(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d28461b310004d88b86e35b984748f50ea00ac8d6a9876feed4774997f087ac1(
    *conditions: Condition,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__140e50c821a3549bdeb3b01e2977c09fb73be78426193bd0a3cbae36b048730b(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e65c9e81a53480621ba56ac26965ccc6cca25adf8874ac67f8114ca6cf5459bb(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2344fc4ff493996fa6f0a25e52f9fec78c74e90b1879ede68f45be50674422a3(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cdd833a815898e835edfc0e45a074b0f4520fa4b7a292f7d2e91c90b0fd4586(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd93977d8ed5727d16ad880cf28a3493d243a690e911dc6a24fee7675a6fd685(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3272fde18528552cc187b9f7b829b329f05e29d6a8895883fa9de73fc12b42e6(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e4cad3d1f576720e1778bae47453adc267469f02ac3e3f9a46e6a366698c96a(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4786f81a736184b791d61305c172a346426765efe4ec906d23da96f2d65b561f(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88e71b46c6af08a584bfc49701401442b025706617f2ca399b86f4abe6e15de4(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e855df09fcf7265dd8097c456ab19f594817b53991438e57115aacd34db5ef0(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb31f92b094c96f5451b5f6033dacd728484fad15409adf8317266e2281f750e(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce197de7a458936cce0cc36cfd2460ec6b184cb06efb79782cb9a7cbc41a1054(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e291271cb939a69116d32cc91ece6eb96654e144c3d14ff121c8f32fbd2067b9(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fa85b90f68b3f93b8e4fe312c52355e3c01610820898d5acea5f389efe000fe(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d5f7fe5170dafaadd571005d7ec016a3456b8a344083b23ce9a86c49a9ec0cc(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd31916ec0216ca0a32d2a026600bc5d924285f6c92a2502575b9fb3a13cc797(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2681634f8150ba4016bd93b0f80b3bc295fbf92a13c522fa66248d7ea25d28c3(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__935865d407934ac8a88529a60186b004426b77736e9706a1e4ddabc423d4b230(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b50ab4a6fe8e9c2c9fa9ff05fef37611e0107e6dc17e835ec10e6f685696c36(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c5cb0b5cf4b0ddbfb4d3c586cc700f5373eedc7edf8b2d24510bf4a42c96bb0(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__492e2ac4c47110465edbd94c9bc1d3e8c628faa5dfcbcf34e5b050b1c42ea1b1(
    variable: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc6df616362238df39334aed8314197fb36afc8a3d07502bbfeb5252aa2aa181(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c37a205138cda7efd0dd9e16607caa79043b33384d2575c501f01fd0695b6162(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47008dcfc587f854ee4c4c8484d56c7fc1f442a411b716570167e9d0fc78404a(
    *,
    state_json: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__466992e0508b766c06020ed286de685f37498f173338f4bb07a7764eabd27778(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e720ecfc18202b38e20c2af0b033d68c13bbaa6734a147ac4f0330324420ef33(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17d2d6b1e33da7249c82522a97ce8460fd91a6788b5040f31cc2731a86e4b69e(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80b2171dbfedcd0f337cc62a273889146a3674a6290395ada81aea0089bcb794(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f82f2dad8c2c44ee04900835f7a93152954dd2a339b3da1e1ee8e7089d045fb1(
    *,
    cause: typing.Optional[builtins.str] = None,
    comment: typing.Optional[builtins.str] = None,
    error: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7472ad39e29c280b40db4eab2f3bf9fa554aae258c6c1959684cb3e40a3e9ac4(
    obj: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddd02194b98b807de20c0986b722ea035aa368f507f80a461566ee2a2e9f6378(
    obj: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66c5ea1d3b7b006661c3d7719a887cfab6680bfa9afe2cc3b582e0b0c995a6e0(
    obj: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3bbbdc9dbd3d4e0970819dcfe1b8c1bc7dc4b3479f5e82b17feb628d43e01be(
    *,
    include_error_handlers: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cd66ae7ffed33d53cb60ef45d1c95defeaa5ca4477ef8e2b9afe15bbcbdac22(
    state: IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f83791493be07978d4568471f3c183643331418a1d3495695b63a75c023aa313(
    identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57a722334637b941ba88641e6a95aa8dfda92a28698c1de76e1c1a395c3d1320(
    identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7541f1db2bd37683f41440acbd42d3c37bd9e7d198b73afac06100152dd64953(
    identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0ea8e618e5162ef265b781ff0c6201fb8f39582c8cf5e4a52015f250c9dd94e(
    identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d2f3ed5371fc7db794547514f9190b733da7c96c2065307c83802e74cc19187(
    identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c963c1e5223549d332c8a816c2b1c94cd470f6c87fcaff397a3391796147820(
    identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__441797ee9418d63382380590bca8ca858817a4db752fb104833880e2557cd748(
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

def _typecheckingstub__8b6b02e7716ea28280ed50b95f76b7f85fab123cb2420e9df34fb77de5f17d30(
    task: Task,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b60eec9d0633867d222ec9d16d97005745274460045cf11f01e3f694765ec3cf(
    *values: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77414a915b6127df4c7e351e8fdec16deeb41cc0cbea5c601e85b939a9c5a8a9(
    format_string: builtins.str,
    *values: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a4ea9e93d3a9719a0624159e3fc66a0228ac660d4cc7f2f25978ecf07bfbad0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2ab1f7f44fa9fa5e2471eaad36ec7d72d613cc9f378a0377c6b68d6a8ba8a59(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6df36a26e3c7810007dcd0bfd1db214b5e21960e450bd3f7b8ef8cc7dd24044(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25c9bb3baa05d0415e8ab2560c3ea7dd7a0ee5e54c3f86c28272fbdb2e1e094b(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5799b4c6f1bf4447939ce76961b4c026a26644c564109a7c1c3f91a89f8116f7(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2e6bd7868e6003fa337e98685b6c06613eecf32428ad050e4b7a7f109b2b1bc(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c896a93910d194a5666b8796d918ccec322b78905d52ded7558bff3c405dcaa(
    json_string: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb6986109f7c3279d658ab4e4a2f828a9d23dbf64a38c1bc29d92ff1f0519d95(
    *,
    destination: _aws_cdk_aws_logs_6c4320fb.ILogGroup,
    include_execution_data: typing.Optional[builtins.bool] = None,
    level: typing.Optional[LogLevel] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8acc8562ebaf5dc229e8f97fd9bf41e777bd7dac23e5dd66b5485f043e09e766(
    *,
    comment: typing.Optional[builtins.str] = None,
    input_path: typing.Optional[builtins.str] = None,
    items_path: typing.Optional[builtins.str] = None,
    max_concurrency: typing.Optional[jsii.Number] = None,
    output_path: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99937f18894b2be3de863916cec28700fc82180bc5d1b325c775062a15552b52(
    *,
    comment: typing.Optional[builtins.str] = None,
    input_path: typing.Optional[builtins.str] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f33e2139d06aae3f4b78bed7625415f8324a4f92e786c5587461cf5936552049(
    *,
    comment: typing.Optional[builtins.str] = None,
    input_path: typing.Optional[builtins.str] = None,
    output_path: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    result: typing.Optional[Result] = None,
    result_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84e36a870933f097185f82839cb19e77f631187d6491abd9a8b9a51183555d0a(
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b6993ac932620a29d3c7b062ba7911f6934b7c56e9d4da7abd31372a5b92a97(
    value: typing.Sequence[typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__780ab2cd306973af0072ec2e462533a5c5cb5441ebe88c90ea5dad8300241774(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de966c949a7816976acc4c595469fca98f0b3b88c73b9046b2b1c7ab2836d87c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__401f8605bf7a4b66793f7882abce3f90dea71592cd856b8f553315d67f1b0a12(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4092efb800bb7cb48441e5ffc5742ee2961e05b7243571b373f234813ef0ad4f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5c198f8a8486dfb6548abbc422bc10f0280143fb9b56f2cb48a86718dff739e(
    *,
    backoff_rate: typing.Optional[jsii.Number] = None,
    errors: typing.Optional[typing.Sequence[builtins.str]] = None,
    interval: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    max_attempts: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2b217e1b8eb2f635f96c52167c0b1b5e80a7286eb6c943255f8fa17d509d98f(
    *,
    comment: typing.Optional[builtins.str] = None,
    input_path: typing.Optional[builtins.str] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    prefix_states: typing.Optional[builtins.str] = None,
    state_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1324c4373ebbfce9f2b498f3e3d1e272df7f09bcb4237984663278ab97a4ad2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    comment: typing.Optional[builtins.str] = None,
    input_path: typing.Optional[builtins.str] = None,
    output_path: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0095a65aca92976f28d7bee65e227f573bc87e38e2936480033c2675e9bfee5e(
    states: typing.Sequence[State],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afab147d1c9e9cde65651d45243f6c8f846b3286b97e2aa17b35e73d5ade622f(
    start: State,
    *,
    include_error_handlers: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2a80887f8e31f7bda9f516ef55507669a05722be24e4892abe50018fe24f56d(
    start: State,
    *,
    include_error_handlers: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5f2737cfc128b5a3fb2016940db8166fe92e7f3a3435debaaf00d5d66cbb2da(
    root: _constructs_77d1e7e8.IConstruct,
    prefix: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2648926708cf1cd8de428b3b40d881953eec01d0a5f923923ed4ccb885979401(
    branch: StateGraph,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3ae445dfe0fd6d27c39e30a27e6947d5e10cddb3c02b12d5649112399f8c040(
    condition: Condition,
    next: State,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56d3b511d59c66900a63f2d50a18d655b12d305ea2f267a44456a131d62cac6c(
    iteration: StateGraph,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81895af85a8fbc97eb6bce6d3790943fad44aaa28cd120930cba0cced2ecfc44(
    x: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ace6d816d5dc40a00a519be1f4efbbd1c47a77265c4d7518d8cc569ab5ac934f(
    graph: StateGraph,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79e37f07161e413cdb664dbfed80ea6aaf47635b659d468fcf2a403e21b85203(
    def_: State,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b89fe7dbc98b4d5ec8b7cd25f37ed7f8ffdb7b6050533401d618b487cf675e26(
    next: State,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5770480781a9875ed1b9f1dd86b443e60e095369fed9f46cf6660624ea030315(
    graph: StateGraph,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68c864b1a1022adea13e327e3dfe6ee14f8776c996fe5de825dec343d4b3c0c6(
    value: typing.Optional[State],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e2d7c0832632f09eb081be9d7f33bcf8e005ee9cbcd3f7d1f42088428db4fc6(
    value: typing.Optional[StateGraph],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52d04a194c6077acd690671a313b18491aa25ba9721cb1ca0bc4c466e5b930cf(
    start_state: State,
    graph_description: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcf2a6b4e0d9e0a752eda4c67bd6fa98d7a06020e9d1ef0176698f17f96481b9(
    statement: _aws_cdk_aws_iam_940a1ce0.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73f974e547b59888319d5df78dd33d1f247c9044544bebb182ee02a00918355e(
    state: State,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a024abf47ab365824d3d6c42b5acc397a27cdc10e501bb07f56f6b0f695d1a7(
    graph: StateGraph,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fbd6d1a83723a4743db754ed314898b4e96f07c3d18edfc30a0ae16bc328434(
    value: typing.Optional[_aws_cdk_core_f4b25747.Duration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa2b76a9f1c214e2b5dfd0d9938d0f24129c6c78807a855e5049f844950a7108(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    definition: IChainable,
    logs: typing.Optional[typing.Union[LogOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    state_machine_type: typing.Optional[StateMachineType] = None,
    timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    tracing_enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__036ef4a09a1f46631e7ad98aa525a45fed4789dcba1c9da87216e8f05168daa4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    state_machine_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba11e2574014096ea81cfeafd6f9ff9a13fe3dc7a0eab8f3cff881e5c47fb88c(
    statement: _aws_cdk_aws_iam_940a1ce0.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__045d975b096fa0ab2140263c4c10eef65beb6f3cc58f5b63f611a50a931189ab(
    identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e11380059dcaec588e06b52a6b43226e3de7061a68e8b20f052047fa4b030f2d(
    identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b3b84479c006f84a1827b5e70aab95e4b264d1c1637d36ee020ef0888570d43(
    identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5897c343f0a2d050b170764fd94383a464776a7e51e25b73810e325123f70fc3(
    identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f9e02893f19aa89e377536c3462748257fcd4c285d9618ad11540db8a6c66f0(
    identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd7c3ab1fbb36436c58ae7a73baaf7988e85acd0482628c34af38935f4b707af(
    identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2516d4e02c0e5db16ddccebb82fd3344b5845ceb75ebfa653ee2dfde0b431381(
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

def _typecheckingstub__82f8f54457926267586136ac5ebfd8f23426751808582096335230670af75fa1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab36f6add0210cbbc2419ec9c5c832001a23b70a6f60b8cb3131e3aa13cc3faa(
    next: IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e999c21d8a64713b883d01847b987411810d8b83e307749ff5d162ce7c1a30a(
    prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31e7681fbcb1dc57bcd1417ea5a7c1e72bca234d37e39bca573be4895b1b9ac8(
    *,
    definition: IChainable,
    logs: typing.Optional[typing.Union[LogOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    state_machine_name: typing.Optional[builtins.str] = None,
    state_machine_type: typing.Optional[StateMachineType] = None,
    timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    tracing_enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fb82d029e32a00db384b778ad4a241a484db6650bdf28af605bc8031f38b985(
    *,
    comment: typing.Optional[builtins.str] = None,
    input_path: typing.Optional[builtins.str] = None,
    output_path: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2136396d66f46f27d420217821413cefbcf8d871be2cf680e71ddc3bee7649a(
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

def _typecheckingstub__b3ab6a65494e211de3e3d62f380384415385d3c528bc760a44378d1284d042cc(
    *,
    resource_arn: builtins.str,
    heartbeat: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    metric_dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    metric_prefix_plural: typing.Optional[builtins.str] = None,
    metric_prefix_singular: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    policy_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_940a1ce0.PolicyStatement]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a3fee51501956a060589c278503bcde0b7db3618b7b2f9ab9b0ad9633ac8a0f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    comment: typing.Optional[builtins.str] = None,
    input_path: typing.Optional[builtins.str] = None,
    output_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f0ef64196b7ec0cc54dff745229d134361a002896d7f9caf6eb18e9ee47fd5e(
    *,
    comment: typing.Optional[builtins.str] = None,
    input_path: typing.Optional[builtins.str] = None,
    output_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26687ca06c1d1db93110592b07dbd68a53c8ea0ed0394d01b39e56742ff9c7ad(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    task: IStepFunctionsTask,
    comment: typing.Optional[builtins.str] = None,
    input_path: typing.Optional[builtins.str] = None,
    output_path: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    result_path: typing.Optional[builtins.str] = None,
    timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c320de101ad653e731fe0c9f306f3f921b337d3b7e048a970ff82d93493a7985(
    handler: IChainable,
    *,
    errors: typing.Optional[typing.Sequence[builtins.str]] = None,
    result_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0bff55910b6829f6e895d73efa6cd042cf6828348101a6f2b2f198d470fa569(
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

def _typecheckingstub__df5d91235929ec66350172358fab2d5d876742452b29597ef26519096d6dd957(
    next: IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f94e8631be4a4e5b23f10fd0083b60ee3eaf1f6fad577ffacda0b6ee181092c4(
    graph: StateGraph,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62307ad7b715ba18acb03a3877987fe2ec4577e919c7b11b4486b2e0a3e42951(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1aab6ed420836da4f48b9a8886ed3e99108dd3e59b9753d355408a3f54d8d98c(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d7965027d24e2c871290ecc451ffdb0354415922c0995e450d4631975cb7baf(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ff25ea3abad7f3022ea7be75920807aa05a38330790c444b1a3b852f3b95b17(
    obj: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a16a24a6c36aaa11ea75f533346c3821564968ca9c00067a47c6c78cd9421fb4(
    text: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__108b830836ef9861875250e04ce0894a43717bf7fd1ae7a9325c971e60f4ceab(
    *,
    metric_dimensions: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    metric_prefix_plural: typing.Optional[builtins.str] = None,
    metric_prefix_singular: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8392990ee9aa926cb3e15f74a39e3c4ece180acd66c00f1f4616b26b451f3871(
    *,
    task: IStepFunctionsTask,
    comment: typing.Optional[builtins.str] = None,
    input_path: typing.Optional[builtins.str] = None,
    output_path: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    result_path: typing.Optional[builtins.str] = None,
    timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c035eaad4cfaa5e12f5859b94ec63b167e3e27e13061fe9b451d3a382a93998(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    comment: typing.Optional[builtins.str] = None,
    heartbeat: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92c346551ec95902de89e8242188887669cdec538f40a26dc53c62b292f169bb(
    handler: IChainable,
    *,
    errors: typing.Optional[typing.Sequence[builtins.str]] = None,
    result_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ed0e391b213542ae166175ab94c8177b017b96bd6c3f393c49da75c1bae5102(
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

def _typecheckingstub__d370c709c8b030c72e433536c8c128fea1dc5a3dedb6cd249d1876e85f323370(
    next: IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0261e83cce662127de2b44eb1b9c7af0d860b23d7ede17127aa3f6a564279e11(
    graph: StateGraph,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__307c9672697e5ee153cbf77ce951ef6efcd1d84024758198f001f86957f346f4(
    *,
    comment: typing.Optional[builtins.str] = None,
    heartbeat: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    input_path: typing.Optional[builtins.str] = None,
    integration_pattern: typing.Optional[IntegrationPattern] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b0fdf5cf3bd8cc9616c029aa5e24348b697e2fe7de0f4b5f1e347f22777ed98(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    time: WaitTime,
    comment: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d15de7a8d772f18e46645533f27397c34d11c65e901796aa2516b935c472dcea(
    next: IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbc20849d2fe5c9da93b194d0874127b021b59f2b1c03721308ab0e326f0f8ce(
    *,
    time: WaitTime,
    comment: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__678de0d0079eccc17c18a14c227ef1d30c694f4f4e849f7a76f2c4ead220aaf6(
    duration: _aws_cdk_core_f4b25747.Duration,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36881edc51a2abd08730456318e532bd50d68265d54d161d9c404233b5db675c(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de0d4462740a555c5da2dcab1a4a96c2d99a9fe82b8be6b748a70d612b0c31bc(
    timestamp: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70aeb14efa21330bf2d196bd40fef4dd6e07bb52d13c73e971f9e691ef051e7f(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__331914dc8ebad71ff98ae773cbd599690e1d7904b70fc9ab7e08bff34cd2c232(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    activity_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__292efbbb82d78225a3380396debc048ad7c236c4b5f7c9744f34784562350d6d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    activity_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02763cd57267bf7f6a6b134658bf2ac0024bb62797f88a863a4d2c4eb3106f29(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    activity_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d1a97ff5bf7a80c80abb0b1c55ed1cb32f69e70e56b308f7cc0435d4ddb35f0(
    identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecd3d237ff1248ee16242119757c6379cd2c9b806377d27550337396d8a0274f(
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

def _typecheckingstub__822895a97fed65b61a96072c38017b2213aea423992c3394f2ad787fb2bb8096(
    start_state: State,
    end_states: typing.Sequence[INextable],
    last_added: IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a707399f78c9415fdc8c3e4d5eeaa2df4537420598870aebea65141091b0334(
    start: IChainable,
    next: IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e46f3eb6aaa9352c718987e98090b3b9fabe7949282ef7df717d7cd6727e0c9b(
    state: IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5e38e8298515bb8c86487c100d8dc32628e1e013765cd19ac49a31a087ac219(
    next: IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6326969138cd78e63eb7912ec4498438274fa32fb4ada6c5c56a65bfa3b64e88(
    id: builtins.str,
    *,
    comment: typing.Optional[builtins.str] = None,
    input_path: typing.Optional[builtins.str] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae8e962a8a63254ccdf241046449d65a87d800c7169e19739dd3d80c9e0adce9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    comment: typing.Optional[builtins.str] = None,
    input_path: typing.Optional[builtins.str] = None,
    output_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d08d00f2cf8dc628de31a48cd53985b4fe3acab43d8a243ae68cb61efd0f92bd(
    def_: IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21714eb93437720e076e1fce6674a312cfffe5203f6c7af7f0c98f346f71de33(
    condition: Condition,
    next: IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdf73075438ababf63fc26082692154d02e4ae381e3aed0b67d05ff092bea3e0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    state_json: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed2d020e66c427ffad63a719bf8d94b5f0f0e49df92b3bb6baf8e40fd2a4f9b6(
    next: IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44d368bdd4e9e7daf66152acddb0cd74184a357fd1eaffed2defdfbbd853018b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cause: typing.Optional[builtins.str] = None,
    comment: typing.Optional[builtins.str] = None,
    error: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e6235dea37838b2d99a56b075ebb42e489029b8c7e7e0e9e3f2b59ecdb54124(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    comment: typing.Optional[builtins.str] = None,
    input_path: typing.Optional[builtins.str] = None,
    items_path: typing.Optional[builtins.str] = None,
    max_concurrency: typing.Optional[jsii.Number] = None,
    output_path: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56259cb2b8607b1718ac094744f7021d830cf1a9fec6117bdc3b05ffbfc9464e(
    handler: IChainable,
    *,
    errors: typing.Optional[typing.Sequence[builtins.str]] = None,
    result_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96b5e01c70471b6657eb375f12fb6d9fc6f4e9704ccba0acbf8e45fb2e4b6b39(
    iterator: IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b25949969dfd2a8cdb1a4b406df8098109d566af0a74af47f7cfbde0bd8a9d68(
    next: IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5acb3644c98a16194318a6f938596c71c96b2933cfaad5a284aefb8aadd1b32c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    comment: typing.Optional[builtins.str] = None,
    input_path: typing.Optional[builtins.str] = None,
    output_path: typing.Optional[builtins.str] = None,
    result_path: typing.Optional[builtins.str] = None,
    result_selector: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76af50cf1b4bf1c270e7e409b5436867f2439ecd1b43934076dce7f62175b320(
    handler: IChainable,
    *,
    errors: typing.Optional[typing.Sequence[builtins.str]] = None,
    result_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2b7e228632b7817982a8f2ce72bc64ad977459233dcf4bddc8ba9de9e1f07b3(
    graph: StateGraph,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b59203d3b787dd87e1effb815faf87767f49ab0ed7f05ebc149fae5a9e24a57(
    *branches: IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ab166a9f8bf802e952c670ffeafc101a6fe90a17fc5a7a4606f5da1d03429f9(
    next: IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea1af4c8f19dbcfff56e69de6f46cf028d1459a78fe7c25a851515855ddb4fac(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    comment: typing.Optional[builtins.str] = None,
    input_path: typing.Optional[builtins.str] = None,
    output_path: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    result: typing.Optional[Result] = None,
    result_path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6746058a8497d5e3501a16b0ebf2cf161abf858fe966b7393a0646b1ca494ff6(
    next: IChainable,
) -> None:
    """Type checking stubs"""
    pass
