from aws_cdk import (
    aws_cloudtrail as cloudtrail,
    aws_ssm as ssm,
    core
) 

class CloudTrailStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, s3bucket,  **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        trail = cloudtrail.Trail(self, 'cloudtrail-id',
            bucket=s3bucket,
            trail_name=prj_name+'-'+env_name+'-trail',

        )
        #trail.add_s3_event_selector(data_resource_values=[])

