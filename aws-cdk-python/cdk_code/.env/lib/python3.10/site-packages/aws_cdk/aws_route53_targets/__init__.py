'''
# Route53 Alias Record Targets for the CDK Route53 Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

This library contains Route53 Alias Record targets for:

* API Gateway custom domains

  ```python
  import aws_cdk.aws_apigateway as apigw

  # zone: route53.HostedZone
  # rest_api: apigw.LambdaRestApi


  route53.ARecord(self, "AliasRecord",
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.ApiGateway(rest_api))
  )
  ```
* API Gateway V2 custom domains

  ```python
  import aws_cdk.aws_apigatewayv2 as apigwv2

  # zone: route53.HostedZone
  # domain_name: apigwv2.DomainName


  route53.ARecord(self, "AliasRecord",
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.ApiGatewayv2DomainProperties(domain_name.regional_domain_name, domain_name.regional_hosted_zone_id))
  )
  ```
* CloudFront distributions

  ```python
  import aws_cdk.aws_cloudfront as cloudfront

  # zone: route53.HostedZone
  # distribution: cloudfront.CloudFrontWebDistribution


  route53.ARecord(self, "AliasRecord",
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(distribution))
  )
  ```
* ELBv2 load balancers

  ```python
  import aws_cdk.aws_elasticloadbalancingv2 as elbv2

  # zone: route53.HostedZone
  # lb: elbv2.ApplicationLoadBalancer


  route53.ARecord(self, "AliasRecord",
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(lb))
  )
  ```
* Classic load balancers

  ```python
  import aws_cdk.aws_elasticloadbalancing as elb

  # zone: route53.HostedZone
  # lb: elb.LoadBalancer


  route53.ARecord(self, "AliasRecord",
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.ClassicLoadBalancerTarget(lb))
  )
  ```

**Important:** Based on [AWS documentation](https://aws.amazon.com/de/premiumsupport/knowledge-center/alias-resource-record-set-route53-cli/), all alias record in Route 53 that points to a Elastic Load Balancer will always include *dualstack* for the DNSName to resolve IPv4/IPv6 addresses (without *dualstack* IPv6 will not resolve).

For example, if the Amazon-provided DNS for the load balancer is `ALB-xxxxxxx.us-west-2.elb.amazonaws.com`, CDK will create alias target in Route 53 will be `dualstack.ALB-xxxxxxx.us-west-2.elb.amazonaws.com`.

* GlobalAccelerator

  ```python
  import aws_cdk.aws_globalaccelerator as globalaccelerator

  # zone: route53.HostedZone
  # accelerator: globalaccelerator.Accelerator


  route53.ARecord(self, "AliasRecord",
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.GlobalAcceleratorTarget(accelerator))
  )
  ```

**Important:** If you use GlobalAcceleratorDomainTarget, passing a string rather than an instance of IAccelerator, ensure that the string is a valid domain name of an existing Global Accelerator instance.
See [the documentation on DNS addressing](https://docs.aws.amazon.com/global-accelerator/latest/dg/dns-addressing-custom-domains.dns-addressing.html) with Global Accelerator for more info.

* InterfaceVpcEndpoints

**Important:** Based on the CFN docs for VPCEndpoints - [see here](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html#aws-resource-ec2-vpcendpoint-return-values) - the attributes returned for DnsEntries in CloudFormation is a combination of the hosted zone ID and the DNS name. The entries are ordered as follows: regional public DNS, zonal public DNS, private DNS, and wildcard DNS. This order is not enforced for AWS Marketplace services, and therefore this CDK construct is ONLY guaranteed to work with non-marketplace services.

```python
import aws_cdk.aws_ec2 as ec2

# zone: route53.HostedZone
# interface_vpc_endpoint: ec2.InterfaceVpcEndpoint


route53.ARecord(self, "AliasRecord",
    zone=zone,
    target=route53.RecordTarget.from_alias(targets.InterfaceVpcEndpointTarget(interface_vpc_endpoint))
)
```

* S3 Bucket Website:

**Important:** The Bucket name must strictly match the full DNS name.
See [the Developer Guide](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/getting-started.html) for more info.

```python
import aws_cdk.aws_s3 as s3


record_name = "www"
domain_name = "example.com"

bucket_website = s3.Bucket(self, "BucketWebsite",
    bucket_name=[record_name, domain_name].join("."),  # www.example.com
    public_read_access=True,
    website_index_document="index.html"
)

zone = route53.HostedZone.from_lookup(self, "Zone", domain_name=domain_name) # example.com

route53.ARecord(self, "AliasRecord",
    zone=zone,
    record_name=record_name,  # www
    target=route53.RecordTarget.from_alias(targets.BucketWebsiteTarget(bucket_website))
)
```

* User pool domain

  ```python
  import aws_cdk.aws_cognito as cognito

  # zone: route53.HostedZone
  # domain: cognito.UserPoolDomain

  route53.ARecord(self, "AliasRecord",
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.UserPoolDomainTarget(domain))
  )
  ```
* Route 53 record

  ```python
  # zone: route53.HostedZone
  # record: route53.ARecord

  route53.ARecord(self, "AliasRecord",
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.Route53RecordTarget(record))
  )
  ```
* Elastic Beanstalk environment:

**Important:** Only supports Elastic Beanstalk environments created after 2016 that have a regional endpoint.

```python
# zone: route53.HostedZone
# ebs_environment_url: str


route53.ARecord(self, "AliasRecord",
    zone=zone,
    target=route53.RecordTarget.from_alias(targets.ElasticBeanstalkEnvironmentEndpointTarget(ebs_environment_url))
)
```

See the documentation of `@aws-cdk/aws-route53` for more information.
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

import aws_cdk.aws_apigateway as _aws_cdk_aws_apigateway_f01c2838
import aws_cdk.aws_cloudfront as _aws_cdk_aws_cloudfront_d69ac3eb
import aws_cdk.aws_cognito as _aws_cdk_aws_cognito_371ee794
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_67de8e8d
import aws_cdk.aws_elasticloadbalancing as _aws_cdk_aws_elasticloadbalancing_976be337
import aws_cdk.aws_elasticloadbalancingv2 as _aws_cdk_aws_elasticloadbalancingv2_e93c784f
import aws_cdk.aws_globalaccelerator as _aws_cdk_aws_globalaccelerator_190af6ad
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_f47b29d4
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_55f001a5
import aws_cdk.core as _aws_cdk_core_f4b25747


@jsii.implements(_aws_cdk_aws_route53_f47b29d4.IAliasRecordTarget)
class ApiGatewayDomain(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53-targets.ApiGatewayDomain",
):
    '''Defines an API Gateway domain name as the alias target.

    Use the ``ApiGateway`` class if you wish to map the alias to an REST API with a
    domain name defined through the ``RestApiProps.domainName`` prop.

    :exampleMetadata: infused

    Example::

        # hosted_zone_for_example_com: Any
        # domain_name: apigateway.DomainName
        
        import aws_cdk.aws_route53 as route53
        import aws_cdk.aws_route53_targets as targets
        
        
        route53.ARecord(self, "CustomDomainAliasRecord",
            zone=hosted_zone_for_example_com,
            target=route53.RecordTarget.from_alias(targets.ApiGatewayDomain(domain_name))
        )
    '''

    def __init__(
        self,
        domain_name: _aws_cdk_aws_apigateway_f01c2838.IDomainName,
    ) -> None:
        '''
        :param domain_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__637eb605afedf7f104280d147fd0f2af6db495458f3f784d7c7ff1c65a3dfce5)
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
        jsii.create(self.__class__, self, [domain_name])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
        _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
    ) -> _aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig:
        '''Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fd126cfc11eced49ced8135e154b632d5cfb82331170cf4136bb5a2455e3246)
            check_type(argname="argument _record", value=_record, expected_type=type_hints["_record"])
            check_type(argname="argument _zone", value=_zone, expected_type=type_hints["_zone"])
        return typing.cast(_aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig, jsii.invoke(self, "bind", [_record, _zone]))


@jsii.implements(_aws_cdk_aws_route53_f47b29d4.IAliasRecordTarget)
class ApiGatewayv2DomainProperties(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53-targets.ApiGatewayv2DomainProperties",
):
    '''Defines an API Gateway V2 domain name as the alias target.

    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_apigatewayv2 as apigwv2
        
        # zone: route53.HostedZone
        # domain_name: apigwv2.DomainName
        
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(targets.ApiGatewayv2DomainProperties(domain_name.regional_domain_name, domain_name.regional_hosted_zone_id))
        )
    '''

    def __init__(
        self,
        regional_domain_name: builtins.str,
        regional_hosted_zone_id: builtins.str,
    ) -> None:
        '''
        :param regional_domain_name: the domain name associated with the regional endpoint for this custom domain name.
        :param regional_hosted_zone_id: the region-specific Amazon Route 53 Hosted Zone ID of the regional endpoint.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__258cb2f27d8911dd5dc536c186f9b0526bbc6b6c09710c7b4dfc38510fb05c28)
            check_type(argname="argument regional_domain_name", value=regional_domain_name, expected_type=type_hints["regional_domain_name"])
            check_type(argname="argument regional_hosted_zone_id", value=regional_hosted_zone_id, expected_type=type_hints["regional_hosted_zone_id"])
        jsii.create(self.__class__, self, [regional_domain_name, regional_hosted_zone_id])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
        _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
    ) -> _aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig:
        '''Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53e1100e5d00af3b6b9b9a3fabca62a81c35e0b51bf962996ebc76bb17b75a80)
            check_type(argname="argument _record", value=_record, expected_type=type_hints["_record"])
            check_type(argname="argument _zone", value=_zone, expected_type=type_hints["_zone"])
        return typing.cast(_aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig, jsii.invoke(self, "bind", [_record, _zone]))


@jsii.implements(_aws_cdk_aws_route53_f47b29d4.IAliasRecordTarget)
class BucketWebsiteTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53-targets.BucketWebsiteTarget",
):
    '''Use a S3 as an alias record target.

    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_s3 as s3
        
        
        record_name = "www"
        domain_name = "example.com"
        
        bucket_website = s3.Bucket(self, "BucketWebsite",
            bucket_name=[record_name, domain_name].join("."),  # www.example.com
            public_read_access=True,
            website_index_document="index.html"
        )
        
        zone = route53.HostedZone.from_lookup(self, "Zone", domain_name=domain_name) # example.com
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            record_name=record_name,  # www
            target=route53.RecordTarget.from_alias(targets.BucketWebsiteTarget(bucket_website))
        )
    '''

    def __init__(self, bucket: _aws_cdk_aws_s3_55f001a5.IBucket) -> None:
        '''
        :param bucket: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__187fb75639ed98652dbf46b38db0d1434714d809c72abeb480511e904840c1b8)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
        jsii.create(self.__class__, self, [bucket])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
        _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
    ) -> _aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig:
        '''Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de1abd8049fcd85daa10b03576e2e8dc76f3b964616c17f0a03b2e57a716636f)
            check_type(argname="argument _record", value=_record, expected_type=type_hints["_record"])
            check_type(argname="argument _zone", value=_zone, expected_type=type_hints["_zone"])
        return typing.cast(_aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig, jsii.invoke(self, "bind", [_record, _zone]))


@jsii.implements(_aws_cdk_aws_route53_f47b29d4.IAliasRecordTarget)
class ClassicLoadBalancerTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53-targets.ClassicLoadBalancerTarget",
):
    '''Use a classic ELB as an alias record target.

    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_elasticloadbalancing as elb
        
        # zone: route53.HostedZone
        # lb: elb.LoadBalancer
        
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(targets.ClassicLoadBalancerTarget(lb))
        )
    '''

    def __init__(
        self,
        load_balancer: _aws_cdk_aws_elasticloadbalancing_976be337.LoadBalancer,
    ) -> None:
        '''
        :param load_balancer: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28a42d5738ec466c9ca4ba4ae00fa353985f7d67050d0ec56b2562436556a04a)
            check_type(argname="argument load_balancer", value=load_balancer, expected_type=type_hints["load_balancer"])
        jsii.create(self.__class__, self, [load_balancer])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
        _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
    ) -> _aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig:
        '''Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__614be9ac666450bb347144818f52fe1c53c0443327b57e7a1418d346bca4de97)
            check_type(argname="argument _record", value=_record, expected_type=type_hints["_record"])
            check_type(argname="argument _zone", value=_zone, expected_type=type_hints["_zone"])
        return typing.cast(_aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig, jsii.invoke(self, "bind", [_record, _zone]))


@jsii.implements(_aws_cdk_aws_route53_f47b29d4.IAliasRecordTarget)
class CloudFrontTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53-targets.CloudFrontTarget",
):
    '''Use a CloudFront Distribution as an alias record target.

    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_cloudfront as cloudfront
        
        # my_zone: route53.HostedZone
        # distribution: cloudfront.CloudFrontWebDistribution
        
        route53.AaaaRecord(self, "Alias",
            zone=my_zone,
            target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(distribution))
        )
    '''

    def __init__(
        self,
        distribution: _aws_cdk_aws_cloudfront_d69ac3eb.IDistribution,
    ) -> None:
        '''
        :param distribution: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4531db4d5c5aaf4d7a55e8586642124432854caa85ef985b548ae00e5f2fa34)
            check_type(argname="argument distribution", value=distribution, expected_type=type_hints["distribution"])
        jsii.create(self.__class__, self, [distribution])

    @jsii.member(jsii_name="getHostedZoneId")
    @builtins.classmethod
    def get_hosted_zone_id(
        cls,
        scope: _aws_cdk_core_f4b25747.IConstruct,
    ) -> builtins.str:
        '''Get the hosted zone id for the current scope.

        :param scope: - scope in which this resource is defined.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__377b54a1699a2ed5e4120c6b4649a7792b225d7d879cdc6d1a201ce27176370a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "getHostedZoneId", [scope]))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
        _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
    ) -> _aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig:
        '''Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38c2bcc7cae110fcfb776be507688a03b9fe3ef46d568e220e6ae10efe5741aa)
            check_type(argname="argument _record", value=_record, expected_type=type_hints["_record"])
            check_type(argname="argument _zone", value=_zone, expected_type=type_hints["_zone"])
        return typing.cast(_aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig, jsii.invoke(self, "bind", [_record, _zone]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CLOUDFRONT_ZONE_ID")
    def CLOUDFRONT_ZONE_ID(cls) -> builtins.str:
        '''The hosted zone Id if using an alias record in Route53.

        This value never changes.
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUDFRONT_ZONE_ID"))


@jsii.implements(_aws_cdk_aws_route53_f47b29d4.IAliasRecordTarget)
class ElasticBeanstalkEnvironmentEndpointTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53-targets.ElasticBeanstalkEnvironmentEndpointTarget",
):
    '''Use an Elastic Beanstalk environment URL as an alias record target. E.g. mysampleenvironment.xyz.us-east-1.elasticbeanstalk.com or mycustomcnameprefix.us-east-1.elasticbeanstalk.com.

    Only supports Elastic Beanstalk environments created after 2016 that have a regional endpoint.

    :exampleMetadata: infused

    Example::

        # zone: route53.HostedZone
        # ebs_environment_url: str
        
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(targets.ElasticBeanstalkEnvironmentEndpointTarget(ebs_environment_url))
        )
    '''

    def __init__(self, environment_endpoint: builtins.str) -> None:
        '''
        :param environment_endpoint: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89d6c662dfba7f46eba701ba007c8491f42b88543917e56d108e85ca74286a28)
            check_type(argname="argument environment_endpoint", value=environment_endpoint, expected_type=type_hints["environment_endpoint"])
        jsii.create(self.__class__, self, [environment_endpoint])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
        _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
    ) -> _aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig:
        '''Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6deb012b10893eeca9cf31356a0a1ca8fb94b9519d5ecbe630d31cf883c4f88e)
            check_type(argname="argument _record", value=_record, expected_type=type_hints["_record"])
            check_type(argname="argument _zone", value=_zone, expected_type=type_hints["_zone"])
        return typing.cast(_aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig, jsii.invoke(self, "bind", [_record, _zone]))


@jsii.implements(_aws_cdk_aws_route53_f47b29d4.IAliasRecordTarget)
class GlobalAcceleratorDomainTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53-targets.GlobalAcceleratorDomainTarget",
):
    '''Use a Global Accelerator domain name as an alias record target.

    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_route53_targets as route53_targets
        
        global_accelerator_domain_target = route53_targets.GlobalAcceleratorDomainTarget("acceleratorDomainName")
    '''

    def __init__(self, accelerator_domain_name: builtins.str) -> None:
        '''Create an Alias Target for a Global Accelerator domain name.

        :param accelerator_domain_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9acfedf5658714e151f97e045b6b19bfc6d217d5115318425996bbd88459f78)
            check_type(argname="argument accelerator_domain_name", value=accelerator_domain_name, expected_type=type_hints["accelerator_domain_name"])
        jsii.create(self.__class__, self, [accelerator_domain_name])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
        _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
    ) -> _aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig:
        '''Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e727e326354cee3bc04a6fb122ed4549b025bb464fecb2e51b246148f5c69fdb)
            check_type(argname="argument _record", value=_record, expected_type=type_hints["_record"])
            check_type(argname="argument _zone", value=_zone, expected_type=type_hints["_zone"])
        return typing.cast(_aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig, jsii.invoke(self, "bind", [_record, _zone]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="GLOBAL_ACCELERATOR_ZONE_ID")
    def GLOBAL_ACCELERATOR_ZONE_ID(cls) -> builtins.str:
        '''The hosted zone Id if using an alias record in Route53.

        This value never changes.
        Ref: https://docs.aws.amazon.com/general/latest/gr/global_accelerator.html
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "GLOBAL_ACCELERATOR_ZONE_ID"))


class GlobalAcceleratorTarget(
    GlobalAcceleratorDomainTarget,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53-targets.GlobalAcceleratorTarget",
):
    '''Use a Global Accelerator instance domain name as an alias record target.

    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_globalaccelerator as globalaccelerator
        
        # zone: route53.HostedZone
        # accelerator: globalaccelerator.Accelerator
        
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(targets.GlobalAcceleratorTarget(accelerator))
        )
    '''

    def __init__(
        self,
        accelerator: _aws_cdk_aws_globalaccelerator_190af6ad.IAccelerator,
    ) -> None:
        '''Create an Alias Target for a Global Accelerator instance.

        :param accelerator: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32d545bdb338d25795ea0c555853b22e67ac209f200d23f910c5c03a468d6ad1)
            check_type(argname="argument accelerator", value=accelerator, expected_type=type_hints["accelerator"])
        jsii.create(self.__class__, self, [accelerator])


@jsii.implements(_aws_cdk_aws_route53_f47b29d4.IAliasRecordTarget)
class InterfaceVpcEndpointTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53-targets.InterfaceVpcEndpointTarget",
):
    '''Set an InterfaceVpcEndpoint as a target for an ARecord.

    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_ec2 as ec2
        
        # zone: route53.HostedZone
        # interface_vpc_endpoint: ec2.InterfaceVpcEndpoint
        
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(targets.InterfaceVpcEndpointTarget(interface_vpc_endpoint))
        )
    '''

    def __init__(
        self,
        vpc_endpoint: _aws_cdk_aws_ec2_67de8e8d.IInterfaceVpcEndpoint,
    ) -> None:
        '''
        :param vpc_endpoint: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0a154759de04441525c089076a4ee4767622be84d20bb251b02a76413dd6006)
            check_type(argname="argument vpc_endpoint", value=vpc_endpoint, expected_type=type_hints["vpc_endpoint"])
        jsii.create(self.__class__, self, [vpc_endpoint])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
        _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
    ) -> _aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig:
        '''Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cf5f4163dd19d9f85333dbc8b73b95692fcedf6f0642acbe768a19fc4ef924f)
            check_type(argname="argument _record", value=_record, expected_type=type_hints["_record"])
            check_type(argname="argument _zone", value=_zone, expected_type=type_hints["_zone"])
        return typing.cast(_aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig, jsii.invoke(self, "bind", [_record, _zone]))


@jsii.implements(_aws_cdk_aws_route53_f47b29d4.IAliasRecordTarget)
class LoadBalancerTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53-targets.LoadBalancerTarget",
):
    '''Use an ELBv2 as an alias record target.

    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_elasticloadbalancingv2 as elbv2
        
        # zone: route53.HostedZone
        # lb: elbv2.ApplicationLoadBalancer
        
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(lb))
        )
    '''

    def __init__(
        self,
        load_balancer: _aws_cdk_aws_elasticloadbalancingv2_e93c784f.ILoadBalancerV2,
    ) -> None:
        '''
        :param load_balancer: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56a85bee528e3acde0f80fa322915d4274c92e7a537e9db024a3eaf9d9f44482)
            check_type(argname="argument load_balancer", value=load_balancer, expected_type=type_hints["load_balancer"])
        jsii.create(self.__class__, self, [load_balancer])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
        _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
    ) -> _aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig:
        '''Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58370c6dffcc0c3773a00431aee71b00055bb96a006b942ae44945174e5036b1)
            check_type(argname="argument _record", value=_record, expected_type=type_hints["_record"])
            check_type(argname="argument _zone", value=_zone, expected_type=type_hints["_zone"])
        return typing.cast(_aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig, jsii.invoke(self, "bind", [_record, _zone]))


@jsii.implements(_aws_cdk_aws_route53_f47b29d4.IAliasRecordTarget)
class Route53RecordTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53-targets.Route53RecordTarget",
):
    '''Use another Route 53 record as an alias record target.

    :exampleMetadata: infused

    Example::

        # zone: route53.HostedZone
        # record: route53.ARecord
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(targets.Route53RecordTarget(record))
        )
    '''

    def __init__(self, record: _aws_cdk_aws_route53_f47b29d4.IRecordSet) -> None:
        '''
        :param record: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b56cfa6afa5d535fe00cf17a9e74cbaea44ba83246e5fb9e83dfe42f0e0fbb5c)
            check_type(argname="argument record", value=record, expected_type=type_hints["record"])
        jsii.create(self.__class__, self, [record])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
        zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
    ) -> _aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig:
        '''Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param zone: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e813c9486bc6c59a280ed49eddec49917ae59111445a8a7ffe2ebaf80d81b8b1)
            check_type(argname="argument _record", value=_record, expected_type=type_hints["_record"])
            check_type(argname="argument zone", value=zone, expected_type=type_hints["zone"])
        return typing.cast(_aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig, jsii.invoke(self, "bind", [_record, zone]))


@jsii.implements(_aws_cdk_aws_route53_f47b29d4.IAliasRecordTarget)
class UserPoolDomainTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53-targets.UserPoolDomainTarget",
):
    '''Use a user pool domain as an alias record target.

    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_cognito as cognito
        
        # zone: route53.HostedZone
        # domain: cognito.UserPoolDomain
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(targets.UserPoolDomainTarget(domain))
        )
    '''

    def __init__(self, domain: _aws_cdk_aws_cognito_371ee794.UserPoolDomain) -> None:
        '''
        :param domain: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67db88193c6f22cdc65081596bb8b1a3035f6e592b912cf2e6ec0e691302add9)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
        jsii.create(self.__class__, self, [domain])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
        _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
    ) -> _aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig:
        '''Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__471ff1f50bb55305b91467dbb85842a7bdbd125568446b6bf785139bf0a2a40f)
            check_type(argname="argument _record", value=_record, expected_type=type_hints["_record"])
            check_type(argname="argument _zone", value=_zone, expected_type=type_hints["_zone"])
        return typing.cast(_aws_cdk_aws_route53_f47b29d4.AliasRecordTargetConfig, jsii.invoke(self, "bind", [_record, _zone]))


class ApiGateway(
    ApiGatewayDomain,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53-targets.ApiGateway",
):
    '''Defines an API Gateway REST API as the alias target. Requires that the domain name will be defined through ``RestApiProps.domainName``.

    You can direct the alias to any ``apigateway.DomainName`` resource through the
    ``ApiGatewayDomain`` class.

    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_route53 as route53
        import aws_cdk.aws_route53_targets as targets
        
        # api: apigateway.RestApi
        # hosted_zone_for_example_com: Any
        
        
        route53.ARecord(self, "CustomDomainAliasRecord",
            zone=hosted_zone_for_example_com,
            target=route53.RecordTarget.from_alias(targets.ApiGateway(api))
        )
    '''

    def __init__(self, api: _aws_cdk_aws_apigateway_f01c2838.RestApiBase) -> None:
        '''
        :param api: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ba6f60980ae17107f66cfad2d94ec9b06b95ecb61e5c01b7bac57bfe16a4a3e)
            check_type(argname="argument api", value=api, expected_type=type_hints["api"])
        jsii.create(self.__class__, self, [api])


__all__ = [
    "ApiGateway",
    "ApiGatewayDomain",
    "ApiGatewayv2DomainProperties",
    "BucketWebsiteTarget",
    "ClassicLoadBalancerTarget",
    "CloudFrontTarget",
    "ElasticBeanstalkEnvironmentEndpointTarget",
    "GlobalAcceleratorDomainTarget",
    "GlobalAcceleratorTarget",
    "InterfaceVpcEndpointTarget",
    "LoadBalancerTarget",
    "Route53RecordTarget",
    "UserPoolDomainTarget",
]

publication.publish()

def _typecheckingstub__637eb605afedf7f104280d147fd0f2af6db495458f3f784d7c7ff1c65a3dfce5(
    domain_name: _aws_cdk_aws_apigateway_f01c2838.IDomainName,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fd126cfc11eced49ced8135e154b632d5cfb82331170cf4136bb5a2455e3246(
    _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
    _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__258cb2f27d8911dd5dc536c186f9b0526bbc6b6c09710c7b4dfc38510fb05c28(
    regional_domain_name: builtins.str,
    regional_hosted_zone_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53e1100e5d00af3b6b9b9a3fabca62a81c35e0b51bf962996ebc76bb17b75a80(
    _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
    _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__187fb75639ed98652dbf46b38db0d1434714d809c72abeb480511e904840c1b8(
    bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de1abd8049fcd85daa10b03576e2e8dc76f3b964616c17f0a03b2e57a716636f(
    _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
    _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28a42d5738ec466c9ca4ba4ae00fa353985f7d67050d0ec56b2562436556a04a(
    load_balancer: _aws_cdk_aws_elasticloadbalancing_976be337.LoadBalancer,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__614be9ac666450bb347144818f52fe1c53c0443327b57e7a1418d346bca4de97(
    _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
    _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4531db4d5c5aaf4d7a55e8586642124432854caa85ef985b548ae00e5f2fa34(
    distribution: _aws_cdk_aws_cloudfront_d69ac3eb.IDistribution,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__377b54a1699a2ed5e4120c6b4649a7792b225d7d879cdc6d1a201ce27176370a(
    scope: _aws_cdk_core_f4b25747.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38c2bcc7cae110fcfb776be507688a03b9fe3ef46d568e220e6ae10efe5741aa(
    _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
    _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89d6c662dfba7f46eba701ba007c8491f42b88543917e56d108e85ca74286a28(
    environment_endpoint: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6deb012b10893eeca9cf31356a0a1ca8fb94b9519d5ecbe630d31cf883c4f88e(
    _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
    _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9acfedf5658714e151f97e045b6b19bfc6d217d5115318425996bbd88459f78(
    accelerator_domain_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e727e326354cee3bc04a6fb122ed4549b025bb464fecb2e51b246148f5c69fdb(
    _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
    _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32d545bdb338d25795ea0c555853b22e67ac209f200d23f910c5c03a468d6ad1(
    accelerator: _aws_cdk_aws_globalaccelerator_190af6ad.IAccelerator,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0a154759de04441525c089076a4ee4767622be84d20bb251b02a76413dd6006(
    vpc_endpoint: _aws_cdk_aws_ec2_67de8e8d.IInterfaceVpcEndpoint,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cf5f4163dd19d9f85333dbc8b73b95692fcedf6f0642acbe768a19fc4ef924f(
    _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
    _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56a85bee528e3acde0f80fa322915d4274c92e7a537e9db024a3eaf9d9f44482(
    load_balancer: _aws_cdk_aws_elasticloadbalancingv2_e93c784f.ILoadBalancerV2,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58370c6dffcc0c3773a00431aee71b00055bb96a006b942ae44945174e5036b1(
    _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
    _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b56cfa6afa5d535fe00cf17a9e74cbaea44ba83246e5fb9e83dfe42f0e0fbb5c(
    record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e813c9486bc6c59a280ed49eddec49917ae59111445a8a7ffe2ebaf80d81b8b1(
    _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
    zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67db88193c6f22cdc65081596bb8b1a3035f6e592b912cf2e6ec0e691302add9(
    domain: _aws_cdk_aws_cognito_371ee794.UserPoolDomain,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__471ff1f50bb55305b91467dbb85842a7bdbd125568446b6bf785139bf0a2a40f(
    _record: _aws_cdk_aws_route53_f47b29d4.IRecordSet,
    _zone: typing.Optional[_aws_cdk_aws_route53_f47b29d4.IHostedZone] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ba6f60980ae17107f66cfad2d94ec9b06b95ecb61e5c01b7bac57bfe16a4a3e(
    api: _aws_cdk_aws_apigateway_f01c2838.RestApiBase,
) -> None:
    """Type checking stubs"""
    pass
