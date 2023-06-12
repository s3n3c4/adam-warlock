from aws_cdk import (
    aws_kms as kms,
    aws_ssm as ssm,
    core
) 

class KMSStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        self.kms_rds = kms.Key(self, 'rdskey',
            description="{}-key-rds".format(prj_name),
            enable_key_rotation=True
        )
        self.kms_rds.add_alias(
            alias_name='alias/{}-key-rds'.format(prj_name)
        )

        #Create SSM parameter
        ssm.StringParameter(self, 'rdskey-param',
            string_value=self.kms_rds.key_id,
            parameter_name='/'+env_name+'/rds-kms-key'
        )