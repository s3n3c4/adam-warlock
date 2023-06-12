from aws_cdk import (
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_elasticsearch as es,
    aws_iam as iam,
    core
)

class KibanaStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str,vpc: ec2.Vpc, kibanasg, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")
        
        subnets = [subnet.subnet_id for subnet in vpc.private_subnets]

        es_domain = es.CfnDomain(self, 'esdomain',
            domain_name=prj_name+'-'+env_name+'-domain',
            elasticsearch_cluster_config=es.CfnDomain.ElasticsearchClusterConfigProperty(
                dedicated_master_enabled=False,
                instance_count=1,
                instance_type='t2.small.elasticsearch'
            ),
            ebs_options=es.CfnDomain.EBSOptionsProperty(
                ebs_enabled=True,
                volume_type='gp2',
                volume_size=10
            ),
            vpc_options=es.CfnDomain.VPCOptionsProperty(
                security_group_ids=[kibanasg.security_group_id],
                subnet_ids=[subnets.pop()]

            ),
            elasticsearch_version='7.4'
            
        )
        es_domain.access_policies={
            "Version": "2012-10-17",
            "Statement": [
                {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "*"
                },
                "Action": "es:*",
                "Resource": "*"
                }
            ]
        }