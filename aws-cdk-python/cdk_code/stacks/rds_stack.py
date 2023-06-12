from aws_cdk import (
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_kms as kms,
    aws_ssm as ssm,
    aws_secretsmanager as sm,
    core
) 
import json

class RDSStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc,lambdasg: ec2.SecurityGroup, bastionsg: ec2.SecurityGroup, kmskey, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        json_template={'username':'admin'}
        db_creds = sm.Secret(self,'db-secret',
            secret_name=env_name+'/rds-secret',
            generate_secret_string=sm.SecretStringGenerator(
                include_space=False,
                password_length=12,
                generate_string_key='password',
                exclude_punctuation=True,
                secret_string_template=json.dumps(json_template)
            )
        )
        db_mysql = rds.DatabaseCluster(self,'mysql',
            default_database_name=prj_name+env_name,
            engine=rds.DatabaseClusterEngine.AURORA_MYSQL,
            engine_version="5.7.12",
            master_user=rds.Login(username='admin', password=db_creds.secret_value_from_json('password')),
            instance_props=rds.InstanceProps(
                vpc=vpc,
                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED),
                instance_type=ec2.InstanceType(instance_type_identifier="t3.small")
            ),
            instances=1,
            parameter_group=rds.ClusterParameterGroup.from_parameter_group_name(
                self,'pg-dev',
                parameter_group_name='default.aurora-mysql5.7'
            ),
            kms_key=kmskey,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        db_mysql.connections.allow_default_port_from(lambdasg, "Access from Lambda functions")
        db_mysql.connections.allow_default_port_from(bastionsg,"Allow from bastion host")

        #SSM Parameter
        ssm.StringParameter(self, 'db-host',
            parameter_name='/'+env_name+'/db-host',
            string_value=db_mysql.cluster_endpoint.hostname
        )

        ssm.StringParameter(self,'db-name',
            parameter_name='/'+env_name+'/db-name',
            string_value=prj_name+env_name
        )

