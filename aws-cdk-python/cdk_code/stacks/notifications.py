from aws_cdk import (
    aws_lambda as lb,
    aws_events as events,
    aws_events_targets as targets,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    core,
)


class NotificationStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        lambda_function = lb.Function(self, 'notificationlambda',
            runtime=lb.Runtime.PYTHON_3_8,
            code=lb.Code.asset('lambda'),
            handler='hello.handler'
        )

        cw_rule = events.Rule(self,'cwrule',
            schedule=events.Schedule.cron(
                minute='0',
                hour='5',
                month = '*',
                week_day='*',
                year = '*'
            )
        )
        cw_rule.add_target(targets.LambdaFunction(lambda_function))

        lambda_topic = sns.Topic(self,'lambdatopic',
            topic_name='serverless-lambda-topic'
        )
        lambda_topic.add_subscription(subs.LambdaSubscription(lambda_function))

        