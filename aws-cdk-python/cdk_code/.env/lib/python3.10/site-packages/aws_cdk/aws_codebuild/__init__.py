'''
# AWS CodeBuild Construct Library

<!--BEGIN STABILITY BANNER-->---


![cfn-resources: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

AWS CodeBuild is a fully managed continuous integration service that compiles
source code, runs tests, and produces software packages that are ready to
deploy. With CodeBuild, you don’t need to provision, manage, and scale your own
build servers. CodeBuild scales continuously and processes multiple builds
concurrently, so your builds are not left waiting in a queue. You can get
started quickly by using prepackaged build environments, or you can create
custom build environments that use your own build tools. With CodeBuild, you are
charged by the minute for the compute resources you use.

## Installation

Install the module:

```console
$ npm i @aws-cdk/aws-codebuild
```

Import it into your code:

```python
import aws_cdk.aws_codebuild as codebuild
```

The `codebuild.Project` construct represents a build project resource. See the
reference documentation for a comprehensive list of initialization properties,
methods and attributes.

## Source

Build projects are usually associated with a *source*, which is specified via
the `source` property which accepts a class that extends the `Source`
abstract base class.
The default is to have no source associated with the build project;
the `buildSpec` option is required in that case.

Here's a CodeBuild project with no source which simply prints `Hello, CodeBuild!`:

```python
codebuild.Project(self, "MyProject",
    build_spec=codebuild.BuildSpec.from_object({
        "version": "0.2",
        "phases": {
            "build": {
                "commands": ["echo \"Hello, CodeBuild!\""
                ]
            }
        }
    })
)
```

### `CodeCommitSource`

Use an AWS CodeCommit repository as the source of this build:

```python
import aws_cdk.aws_codecommit as codecommit


repository = codecommit.Repository(self, "MyRepo", repository_name="foo")
codebuild.Project(self, "MyFirstCodeCommitProject",
    source=codebuild.Source.code_commit(repository=repository)
)
```

### `S3Source`

Create a CodeBuild project with an S3 bucket as the source:

```python
bucket = s3.Bucket(self, "MyBucket")

codebuild.Project(self, "MyProject",
    source=codebuild.Source.s3(
        bucket=bucket,
        path="path/to/file.zip"
    )
)
```

The CodeBuild role will be granted to read just the given path from the given `bucket`.

### `GitHubSource` and `GitHubEnterpriseSource`

These source types can be used to build code from a GitHub repository.
Example:

```python
git_hub_source = codebuild.Source.git_hub(
    owner="awslabs",
    repo="aws-cdk",
    webhook=True,  # optional, default: true if `webhookFilters` were provided, false otherwise
    webhook_triggers_batch_build=True,  # optional, default is false
    webhook_filters=[
        codebuild.FilterGroup.in_event_of(codebuild.EventAction.PUSH).and_branch_is("master").and_commit_message_is("the commit message")
    ]
)
```

To provide GitHub credentials, please either go to AWS CodeBuild Console to connect
or call `ImportSourceCredentials` to persist your personal access token.
Example:

```console
aws codebuild import-source-credentials --server-type GITHUB --auth-type PERSONAL_ACCESS_TOKEN --token <token_value>
```

### `BitBucketSource`

This source type can be used to build code from a BitBucket repository.

```python
bb_source = codebuild.Source.bit_bucket(
    owner="owner",
    repo="repo"
)
```

### For all Git sources

For all Git sources, you can fetch submodules while cloing git repo.

```python
git_hub_source = codebuild.Source.git_hub(
    owner="awslabs",
    repo="aws-cdk",
    fetch_submodules=True
)
```

## Artifacts

CodeBuild Projects can produce Artifacts and upload them to S3. For example:

```python
# bucket: s3.Bucket


project = codebuild.Project(self, "MyProject",
    build_spec=codebuild.BuildSpec.from_object({
        "version": "0.2"
    }),
    artifacts=codebuild.Artifacts.s3(
        bucket=bucket,
        include_build_id=False,
        package_zip=True,
        path="another/path",
        identifier="AddArtifact1"
    )
)
```

If you'd prefer your buildspec to be rendered as YAML in the template,
use the `fromObjectToYaml()` method instead of `fromObject()`.

Because we've not set the `name` property, this example will set the
`overrideArtifactName` parameter, and produce an artifact named as defined in
the Buildspec file, uploaded to an S3 bucket (`bucket`). The path will be
`another/path` and the artifact will be a zipfile.

## CodePipeline

To add a CodeBuild Project as an Action to CodePipeline,
use the `PipelineProject` class instead of `Project`.
It's a simple class that doesn't allow you to specify `sources`,
`secondarySources`, `artifacts` or `secondaryArtifacts`,
as these are handled by setting input and output CodePipeline `Artifact` instances on the Action,
instead of setting them on the Project.

```python
project = codebuild.PipelineProject(self, "Project")
```

For more details, see the readme of the `@aws-cdk/@aws-codepipeline-actions` package.

## Caching

You can save time when your project builds by using a cache. A cache can store reusable pieces of your build environment and use them across multiple builds. Your build project can use one of two types of caching: Amazon S3 or local. In general, S3 caching is a good option for small and intermediate build artifacts that are more expensive to build than to download. Local caching is a good option for large intermediate build artifacts because the cache is immediately available on the build host.

### S3 Caching

With S3 caching, the cache is stored in an S3 bucket which is available
regardless from what CodeBuild instance gets selected to run your CodeBuild job
on. When using S3 caching, you must also add in a `cache` section to your
buildspec which indicates the files to be cached:

```python
# my_caching_bucket: s3.Bucket


codebuild.Project(self, "Project",
    source=codebuild.Source.bit_bucket(
        owner="awslabs",
        repo="aws-cdk"
    ),

    cache=codebuild.Cache.bucket(my_caching_bucket),

    # BuildSpec with a 'cache' section necessary for S3 caching. This can
    # also come from 'buildspec.yml' in your source.
    build_spec=codebuild.BuildSpec.from_object({
        "version": "0.2",
        "phases": {
            "build": {
                "commands": ["..."]
            }
        },
        "cache": {
            "paths": ["/root/cachedir/**/*"
            ]
        }
    })
)
```

Note that two different CodeBuild Projects using the same S3 bucket will *not*
share their cache: each Project will get a unique file in the S3 bucket to store
the cache in.

### Local Caching

With local caching, the cache is stored on the codebuild instance itself. This
is simple, cheap and fast, but CodeBuild cannot guarantee a reuse of instance
and hence cannot guarantee cache hits. For example, when a build starts and
caches files locally, if two subsequent builds start at the same time afterwards
only one of those builds would get the cache. Three different cache modes are
supported, which can be turned on individually.

* `LocalCacheMode.SOURCE` caches Git metadata for primary and secondary sources.
* `LocalCacheMode.DOCKER_LAYER` caches existing Docker layers.
* `LocalCacheMode.CUSTOM` caches directories you specify in the buildspec file.

```python
codebuild.Project(self, "Project",
    source=codebuild.Source.git_hub_enterprise(
        https_clone_url="https://my-github-enterprise.com/owner/repo"
    ),

    # Enable Docker AND custom caching
    cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER, codebuild.LocalCacheMode.CUSTOM),

    # BuildSpec with a 'cache' section necessary for 'CUSTOM' caching. This can
    # also come from 'buildspec.yml' in your source.
    build_spec=codebuild.BuildSpec.from_object({
        "version": "0.2",
        "phases": {
            "build": {
                "commands": ["..."]
            }
        },
        "cache": {
            "paths": ["/root/cachedir/**/*"
            ]
        }
    })
)
```

## Environment

By default, projects use a small instance with an Ubuntu 18.04 image. You
can use the `environment` property to customize the build environment:

* `buildImage` defines the Docker image used. See [Images](#images) below for
  details on how to define build images.
* `certificate` defines the location of a PEM encoded certificate to import.
* `computeType` defines the instance type used for the build.
* `privileged` can be set to `true` to allow privileged access.
* `environmentVariables` can be set at this level (and also at the project
  level).

## Images

The CodeBuild library supports both Linux and Windows images via the
`LinuxBuildImage` (or `LinuxArmBuildImage`), and `WindowsBuildImage` classes, respectively.

You can specify one of the predefined Windows/Linux images by using one
of the constants such as `WindowsBuildImage.WIN_SERVER_CORE_2019_BASE`,
`WindowsBuildImage.WINDOWS_BASE_2_0`, `LinuxBuildImage.STANDARD_2_0`, or
`LinuxArmBuildImage.AMAZON_LINUX_2_ARM`.

Alternatively, you can specify a custom image using one of the static methods on
`LinuxBuildImage`:

* `LinuxBuildImage.fromDockerRegistry(image[, { secretsManagerCredentials }])` to reference an image in any public or private Docker registry.
* `LinuxBuildImage.fromEcrRepository(repo[, tag])` to reference an image available in an
  ECR repository.
* `LinuxBuildImage.fromAsset(parent, id, props)` to use an image created from a
  local asset.
* `LinuxBuildImage.fromCodeBuildImageId(id)` to reference a pre-defined, CodeBuild-provided Docker image.

or one of the corresponding methods on `WindowsBuildImage`:

* `WindowsBuildImage.fromDockerRegistry(image[, { secretsManagerCredentials }, imageType])`
* `WindowsBuildImage.fromEcrRepository(repo[, tag, imageType])`
* `WindowsBuildImage.fromAsset(parent, id, props, [, imageType])`

or one of the corresponding methods on `LinuxArmBuildImage`:

* `LinuxArmBuildImage.fromEcrRepository(repo[, tag])`

Note that the `WindowsBuildImage` version of the static methods accepts an optional parameter of type `WindowsImageType`,
which can be either `WindowsImageType.STANDARD`, the default, or `WindowsImageType.SERVER_2019`:

```python
# ecr_repository: ecr.Repository


codebuild.Project(self, "Project",
    environment=codebuild.BuildEnvironment(
        build_image=codebuild.WindowsBuildImage.from_ecr_repository(ecr_repository, "v1.0", codebuild.WindowsImageType.SERVER_2019),
        # optional certificate to include in the build image
        certificate=codebuild.BuildEnvironmentCertificate(
            bucket=s3.Bucket.from_bucket_name(self, "Bucket", "my-bucket"),
            object_key="path/to/cert.pem"
        )
    )
)
```

The following example shows how to define an image from a Docker asset:

```python
environment=codebuild.BuildEnvironment(
    build_image=codebuild.LinuxBuildImage.from_asset(self, "MyImage",
        directory=path.join(__dirname, "demo-image")
    )
)
```

The following example shows how to define an image from an ECR repository:

```python
environment=codebuild.BuildEnvironment(
    build_image=codebuild.LinuxBuildImage.from_ecr_repository(ecr_repository, "v1.0")
)
```

The following example shows how to define an image from a private docker registry:

```python
environment=codebuild.BuildEnvironment(
    build_image=codebuild.LinuxBuildImage.from_docker_registry("my-registry/my-repo",
        secrets_manager_credentials=secrets
    )
)
```

### GPU images

The class `LinuxGpuBuildImage` contains constants for working with
[AWS Deep Learning Container images](https://aws.amazon.com/releasenotes/available-deep-learning-containers-images):

```python
codebuild.Project(self, "Project",
    environment=codebuild.BuildEnvironment(
        build_image=codebuild.LinuxGpuBuildImage.DLC_TENSORFLOW_2_1_0_INFERENCE
    )
)
```

One complication is that the repositories for the DLC images are in
different accounts in different AWS regions.
In most cases, the CDK will handle providing the correct account for you;
in rare cases (for example, deploying to new regions)
where our information might be out of date,
you can always specify the account
(along with the repository name and tag)
explicitly using the `awsDeepLearningContainersImage` method:

```python
codebuild.Project(self, "Project",
    environment=codebuild.BuildEnvironment(
        build_image=codebuild.LinuxGpuBuildImage.aws_deep_learning_containers_image("tensorflow-inference", "2.1.0-gpu-py36-cu101-ubuntu18.04", "123456789012")
    )
)
```

Alternatively, you can reference an image available in an ECR repository using the `LinuxGpuBuildImage.fromEcrRepository(repo[, tag])` method.

## Logs

CodeBuild lets you specify an S3 Bucket, CloudWatch Log Group or both to receive logs from your projects.

By default, logs will go to cloudwatch.

### CloudWatch Logs Example

```python
codebuild.Project(self, "Project",
    logging=codebuild.LoggingOptions(
        cloud_watch=codebuild.CloudWatchLoggingOptions(
            log_group=logs.LogGroup(self, "MyLogGroup")
        )
    )
)
```

### S3 Logs Example

```python
codebuild.Project(self, "Project",
    logging=codebuild.LoggingOptions(
        s3=codebuild.S3LoggingOptions(
            bucket=s3.Bucket(self, "LogBucket")
        )
    )
)
```

## Credentials

CodeBuild allows you to store credentials used when communicating with various sources,
like GitHub:

```python
codebuild.GitHubSourceCredentials(self, "CodeBuildGitHubCreds",
    access_token=SecretValue.secrets_manager("my-token")
)
```

and BitBucket:

```python
codebuild.BitBucketSourceCredentials(self, "CodeBuildBitBucketCreds",
    username=SecretValue.secrets_manager("my-bitbucket-creds", json_field="username"),
    password=SecretValue.secrets_manager("my-bitbucket-creds", json_field="password")
)
```

**Note**: the credentials are global to a given account in a given region -
they are not defined per CodeBuild project.
CodeBuild only allows storing a single credential of a given type
(GitHub, GitHub Enterprise or BitBucket)
in a given account in a given region -
any attempt to save more than one will result in an error.
You can use the [`list-source-credentials` AWS CLI operation](https://docs.aws.amazon.com/cli/latest/reference/codebuild/list-source-credentials.html)
to inspect what credentials are stored in your account.

## Test reports

You can specify a test report in your buildspec:

```python
project = codebuild.Project(self, "Project",
    build_spec=codebuild.BuildSpec.from_object({
        # ...
        "reports": {
            "my_report": {
                "files": "**/*",
                "base-directory": "build/test-results"
            }
        }
    })
)
```

This will create a new test report group,
with the name `<ProjectName>-myReport`.

The project's role in the CDK will always be granted permissions to create and use report groups
with names starting with the project's name;
if you'd rather not have those permissions added,
you can opt out of it when creating the project:

```python
# source: codebuild.Source


project = codebuild.Project(self, "Project",
    source=source,
    grant_report_group_permissions=False
)
```

Alternatively, you can specify an ARN of an existing resource group,
instead of a simple name, in your buildspec:

```python
# source: codebuild.Source


# create a new ReportGroup
report_group = codebuild.ReportGroup(self, "ReportGroup")

project = codebuild.Project(self, "Project",
    source=source,
    build_spec=codebuild.BuildSpec.from_object({
        # ...
        "reports": {
            "report_group.report_group_arn": {
                "files": "**/*",
                "base-directory": "build/test-results"
            }
        }
    })
)
```

If you do that, you need to grant the project's role permissions to write reports to that report group:

```python
# project: codebuild.Project
# report_group: codebuild.ReportGroup


report_group.grant_write(project)
```

For more information on the test reports feature,
see the [AWS CodeBuild documentation](https://docs.aws.amazon.com/codebuild/latest/userguide/test-reporting.html).

## Events

CodeBuild projects can be used either as a source for events or be triggered
by events via an event rule.

### Using Project as an event target

The `@aws-cdk/aws-events-targets.CodeBuildProject` allows using an AWS CodeBuild
project as a AWS CloudWatch event rule target:

```python
# start build when a commit is pushed
import aws_cdk.aws_codecommit as codecommit
import aws_cdk.aws_events_targets as targets

# code_commit_repository: codecommit.Repository
# project: codebuild.Project


code_commit_repository.on_commit("OnCommit",
    target=targets.CodeBuildProject(project)
)
```

### Using Project as an event source

To define Amazon CloudWatch event rules for build projects, use one of the `onXxx`
methods:

```python
import aws_cdk.aws_events_targets as targets
# fn: lambda.Function
# project: codebuild.Project


rule = project.on_state_change("BuildStateChange",
    target=targets.LambdaFunction(fn)
)
```

## CodeStar Notifications

To define CodeStar Notification rules for Projects, use one of the `notifyOnXxx()` methods.
They are very similar to `onXxx()` methods for CloudWatch events:

```python
import aws_cdk.aws_chatbot as chatbot

# project: codebuild.Project


target = chatbot.SlackChannelConfiguration(self, "MySlackChannel",
    slack_channel_configuration_name="YOUR_CHANNEL_NAME",
    slack_workspace_id="YOUR_SLACK_WORKSPACE_ID",
    slack_channel_id="YOUR_SLACK_CHANNEL_ID"
)

rule = project.notify_on_build_succeeded("NotifyOnBuildSucceeded", target)
```

## Secondary sources and artifacts

CodeBuild Projects can get their sources from multiple places, and produce
multiple outputs. For example:

```python
import aws_cdk.aws_codecommit as codecommit
# repo: codecommit.Repository
# bucket: s3.Bucket


project = codebuild.Project(self, "MyProject",
    secondary_sources=[
        codebuild.Source.code_commit(
            identifier="source2",
            repository=repo
        )
    ],
    secondary_artifacts=[
        codebuild.Artifacts.s3(
            identifier="artifact2",
            bucket=bucket,
            path="some/path",
            name="file.zip"
        )
    ]
)
```

Note that the `identifier` property is required for both secondary sources and
artifacts.

The contents of the secondary source is available to the build under the
directory specified by the `CODEBUILD_SRC_DIR_<identifier>` environment variable
(so, `CODEBUILD_SRC_DIR_source2` in the above case).

The secondary artifacts have their own section in the buildspec, under the
regular `artifacts` one. Each secondary artifact has its own section, beginning
with their identifier.

So, a buildspec for the above Project could look something like this:

```python
project = codebuild.Project(self, "MyProject",
    # secondary sources and artifacts as above...
    build_spec=codebuild.BuildSpec.from_object({
        "version": "0.2",
        "phases": {
            "build": {
                "commands": ["cd $CODEBUILD_SRC_DIR_source2", "touch output2.txt"
                ]
            }
        },
        "artifacts": {
            "secondary-artifacts": {
                "artifact2": {
                    "base-directory": "$CODEBUILD_SRC_DIR_source2",
                    "files": ["output2.txt"
                    ]
                }
            }
        }
    })
)
```

### Definition of VPC configuration in CodeBuild Project

Typically, resources in an VPC are not accessible by AWS CodeBuild. To enable
access, you must provide additional VPC-specific configuration information as
part of your CodeBuild project configuration. This includes the VPC ID, the
VPC subnet IDs, and the VPC security group IDs. VPC-enabled builds are then
able to access resources inside your VPC.

For further Information see https://docs.aws.amazon.com/codebuild/latest/userguide/vpc-support.html

**Use Cases**
VPC connectivity from AWS CodeBuild builds makes it possible to:

* Run integration tests from your build against data in an Amazon RDS database that's isolated on a private subnet.
* Query data in an Amazon ElastiCache cluster directly from tests.
* Interact with internal web services hosted on Amazon EC2, Amazon ECS, or services that use internal Elastic Load Balancing.
* Retrieve dependencies from self-hosted, internal artifact repositories, such as PyPI for Python, Maven for Java, and npm for Node.js.
* Access objects in an Amazon S3 bucket configured to allow access through an Amazon VPC endpoint only.
* Query external web services that require fixed IP addresses through the Elastic IP address of the NAT gateway or NAT instance associated with your subnet(s).

Your builds can access any resource that's hosted in your VPC.

**Enable Amazon VPC Access in your CodeBuild Projects**

Pass the VPC when defining your Project, then make sure to
give the CodeBuild's security group the right permissions
to access the resources that it needs by using the
`connections` object.

For example:

```python
# load_balancer: elbv2.ApplicationLoadBalancer


vpc = ec2.Vpc(self, "MyVPC")
project = codebuild.Project(self, "MyProject",
    vpc=vpc,
    build_spec=codebuild.BuildSpec.from_object({})
)

project.connections.allow_to(load_balancer, ec2.Port.tcp(443))
```

## Project File System Location EFS

Add support for CodeBuild to build on AWS EFS file system mounts using
the new ProjectFileSystemLocation.
The `fileSystemLocations` property which accepts a list `ProjectFileSystemLocation`
as represented by the interface `IFileSystemLocations`.
The only supported file system type is `EFS`.

For example:

```python
codebuild.Project(self, "MyProject",
    build_spec=codebuild.BuildSpec.from_object({
        "version": "0.2"
    }),
    file_system_locations=[
        codebuild.FileSystemLocation.efs(
            identifier="myidentifier2",
            location="myclodation.mydnsroot.com:/loc",
            mount_point="/media",
            mount_options="opts"
        )
    ]
)
```

Here's a CodeBuild project with a simple example that creates a project mounted on AWS EFS:

[Minimal Example](./test/integ.project-file-system-location.ts)

## Batch builds

To enable batch builds you should call `enableBatchBuilds()` on the project instance.

It returns an object containing the batch service role that was created,
or `undefined` if batch builds could not be enabled, for example if the project was imported.

```python
# source: codebuild.Source


project = codebuild.Project(self, "MyProject", source=source)

if project.enable_batch_builds():
    print("Batch builds were enabled")
```

## Timeouts

There are two types of timeouts that can be set when creating your Project.
The `timeout` property can be used to set an upper limit on how long your Project is able to run without being marked as completed.
The default is 60 minutes.
An example of overriding the default follows.

```python
codebuild.Project(self, "MyProject",
    timeout=Duration.minutes(90)
)
```

The `queuedTimeout` property can be used to set an upper limit on how your Project remains queued to run.
There is no default value for this property.
As an example, to allow your Project to queue for up to thirty (30) minutes before the build fails,
use the following code.

```python
codebuild.Project(self, "MyProject",
    queued_timeout=Duration.minutes(30)
)
```

## Limiting concurrency

By default if a new build is triggered it will be run even if there is a previous build already in progress.
It is possible to limit the maximum concurrent builds to value between 1 and the account specific maximum limit.
By default there is no explicit limit.

```python
codebuild.Project(self, "MyProject",
    concurrent_build_limit=1
)
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

import aws_cdk.assets as _aws_cdk_assets_b1c45fb6
import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_9b88bb94
import aws_cdk.aws_codecommit as _aws_cdk_aws_codecommit_692dd32c
import aws_cdk.aws_codestarnotifications as _aws_cdk_aws_codestarnotifications_391e8ded
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_67de8e8d
import aws_cdk.aws_ecr as _aws_cdk_aws_ecr_093ed842
import aws_cdk.aws_ecr_assets as _aws_cdk_aws_ecr_assets_ef09b699
import aws_cdk.aws_events as _aws_cdk_aws_events_efcdfa54
import aws_cdk.aws_iam as _aws_cdk_aws_iam_940a1ce0
import aws_cdk.aws_kms as _aws_cdk_aws_kms_e491a92b
import aws_cdk.aws_logs as _aws_cdk_aws_logs_6c4320fb
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_55f001a5
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_72af8d6f
import aws_cdk.core as _aws_cdk_core_f4b25747
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.ArtifactsConfig",
    jsii_struct_bases=[],
    name_mapping={"artifacts_property": "artifactsProperty"},
)
class ArtifactsConfig:
    def __init__(
        self,
        *,
        artifacts_property: typing.Union["CfnProject.ArtifactsProperty", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''The type returned from {@link IArtifacts#bind}.

        :param artifacts_property: The low-level CloudFormation artifacts property.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            
            artifacts_config = codebuild.ArtifactsConfig(
                artifacts_property=codebuild.CfnProject.ArtifactsProperty(
                    type="type",
            
                    # the properties below are optional
                    artifact_identifier="artifactIdentifier",
                    encryption_disabled=False,
                    location="location",
                    name="name",
                    namespace_type="namespaceType",
                    override_artifact_name=False,
                    packaging="packaging",
                    path="path"
                )
            )
        '''
        if isinstance(artifacts_property, dict):
            artifacts_property = CfnProject.ArtifactsProperty(**artifacts_property)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__783137bdef1219c8299fa73812cbf2775c0bf2cc1b0cc2626a3e150604cba15b)
            check_type(argname="argument artifacts_property", value=artifacts_property, expected_type=type_hints["artifacts_property"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "artifacts_property": artifacts_property,
        }

    @builtins.property
    def artifacts_property(self) -> "CfnProject.ArtifactsProperty":
        '''The low-level CloudFormation artifacts property.'''
        result = self._values.get("artifacts_property")
        assert result is not None, "Required property 'artifacts_property' is missing"
        return typing.cast("CfnProject.ArtifactsProperty", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ArtifactsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.ArtifactsProps",
    jsii_struct_bases=[],
    name_mapping={"identifier": "identifier"},
)
class ArtifactsProps:
    def __init__(self, *, identifier: typing.Optional[builtins.str] = None) -> None:
        '''Properties common to all Artifacts classes.

        :param identifier: The artifact identifier. This property is required on secondary artifacts.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            
            artifacts_props = codebuild.ArtifactsProps(
                identifier="identifier"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__543fb0dbe6d57644358928fa5ebe91fdc920f03017a7f6270527f5abcdfc47b4)
            check_type(argname="argument identifier", value=identifier, expected_type=type_hints["identifier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if identifier is not None:
            self._values["identifier"] = identifier

    @builtins.property
    def identifier(self) -> typing.Optional[builtins.str]:
        '''The artifact identifier.

        This property is required on secondary artifacts.
        '''
        result = self._values.get("identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ArtifactsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.BatchBuildConfig",
    jsii_struct_bases=[],
    name_mapping={"role": "role"},
)
class BatchBuildConfig:
    def __init__(self, *, role: _aws_cdk_aws_iam_940a1ce0.IRole) -> None:
        '''The type returned from {@link IProject#enableBatchBuilds}.

        :param role: The IAM batch service Role of this Project.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            import aws_cdk.aws_iam as iam
            
            # role: iam.Role
            
            batch_build_config = codebuild.BatchBuildConfig(
                role=role
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d7a2f7d03343489b38924ea0ca66ba76a8839905b1ba2cb3a9592d8021f0fde)
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role": role,
        }

    @builtins.property
    def role(self) -> _aws_cdk_aws_iam_940a1ce0.IRole:
        '''The IAM batch service Role of this Project.'''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.IRole, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchBuildConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.BindToCodePipelineOptions",
    jsii_struct_bases=[],
    name_mapping={"artifact_bucket": "artifactBucket"},
)
class BindToCodePipelineOptions:
    def __init__(self, *, artifact_bucket: _aws_cdk_aws_s3_55f001a5.IBucket) -> None:
        '''The extra options passed to the {@link IProject.bindToCodePipeline} method.

        :param artifact_bucket: The artifact bucket that will be used by the action that invokes this project.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            import aws_cdk.aws_s3 as s3
            
            # bucket: s3.Bucket
            
            bind_to_code_pipeline_options = codebuild.BindToCodePipelineOptions(
                artifact_bucket=bucket
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af4009f097ceffdb1f2e6e5f212ee08efef9ba1a835db5316773e5ea5f9902bd)
            check_type(argname="argument artifact_bucket", value=artifact_bucket, expected_type=type_hints["artifact_bucket"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "artifact_bucket": artifact_bucket,
        }

    @builtins.property
    def artifact_bucket(self) -> _aws_cdk_aws_s3_55f001a5.IBucket:
        '''The artifact bucket that will be used by the action that invokes this project.'''
        result = self._values.get("artifact_bucket")
        assert result is not None, "Required property 'artifact_bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_55f001a5.IBucket, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BindToCodePipelineOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BitBucketSourceCredentials(
    _aws_cdk_core_f4b25747.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.BitBucketSourceCredentials",
):
    '''The source credentials used when contacting the BitBucket API.

    **Note**: CodeBuild only allows a single credential for BitBucket
    to be saved in a given AWS account in a given region -
    any attempt to add more than one will result in an error.

    :resource: AWS::CodeBuild::SourceCredential
    :exampleMetadata: infused

    Example::

        codebuild.BitBucketSourceCredentials(self, "CodeBuildBitBucketCreds",
            username=SecretValue.secrets_manager("my-bitbucket-creds", json_field="username"),
            password=SecretValue.secrets_manager("my-bitbucket-creds", json_field="password")
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        password: _aws_cdk_core_f4b25747.SecretValue,
        username: _aws_cdk_core_f4b25747.SecretValue,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param password: Your BitBucket application password.
        :param username: Your BitBucket username.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f370aa69c6c21518dd8fe5baa560143728d59934aa6c1ae749e5f3a4b9da55e3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BitBucketSourceCredentialsProps(password=password, username=username)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.BitBucketSourceCredentialsProps",
    jsii_struct_bases=[],
    name_mapping={"password": "password", "username": "username"},
)
class BitBucketSourceCredentialsProps:
    def __init__(
        self,
        *,
        password: _aws_cdk_core_f4b25747.SecretValue,
        username: _aws_cdk_core_f4b25747.SecretValue,
    ) -> None:
        '''Construction properties of {@link BitBucketSourceCredentials}.

        :param password: Your BitBucket application password.
        :param username: Your BitBucket username.

        :exampleMetadata: infused

        Example::

            codebuild.BitBucketSourceCredentials(self, "CodeBuildBitBucketCreds",
                username=SecretValue.secrets_manager("my-bitbucket-creds", json_field="username"),
                password=SecretValue.secrets_manager("my-bitbucket-creds", json_field="password")
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc76d3d1ab66ce79293ed2ec33f38421ed1cdaa7bd3ab6e681bcd2629b5b69f6)
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "password": password,
            "username": username,
        }

    @builtins.property
    def password(self) -> _aws_cdk_core_f4b25747.SecretValue:
        '''Your BitBucket application password.'''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(_aws_cdk_core_f4b25747.SecretValue, result)

    @builtins.property
    def username(self) -> _aws_cdk_core_f4b25747.SecretValue:
        '''Your BitBucket username.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(_aws_cdk_core_f4b25747.SecretValue, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BitBucketSourceCredentialsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.BucketCacheOptions",
    jsii_struct_bases=[],
    name_mapping={"prefix": "prefix"},
)
class BucketCacheOptions:
    def __init__(self, *, prefix: typing.Optional[builtins.str] = None) -> None:
        '''
        :param prefix: The prefix to use to store the cache in the bucket.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            
            bucket_cache_options = codebuild.BucketCacheOptions(
                prefix="prefix"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ef86c7b56412e30a9ec34e29c484de4e82b900da98a1cc36d17b5baf51839e3)
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''The prefix to use to store the cache in the bucket.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BucketCacheOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.BuildEnvironment",
    jsii_struct_bases=[],
    name_mapping={
        "build_image": "buildImage",
        "certificate": "certificate",
        "compute_type": "computeType",
        "environment_variables": "environmentVariables",
        "privileged": "privileged",
    },
)
class BuildEnvironment:
    def __init__(
        self,
        *,
        build_image: typing.Optional["IBuildImage"] = None,
        certificate: typing.Optional[typing.Union["BuildEnvironmentCertificate", typing.Dict[builtins.str, typing.Any]]] = None,
        compute_type: typing.Optional["ComputeType"] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union["BuildEnvironmentVariable", typing.Dict[builtins.str, typing.Any]]]] = None,
        privileged: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param build_image: The image used for the builds. Default: LinuxBuildImage.STANDARD_1_0
        :param certificate: The location of the PEM-encoded certificate for the build project. Default: - No external certificate is added to the project
        :param compute_type: The type of compute to use for this build. See the {@link ComputeType} enum for the possible values. Default: taken from {@link #buildImage#defaultComputeType}
        :param environment_variables: The environment variables that your builds can use.
        :param privileged: Indicates how the project builds Docker images. Specify true to enable running the Docker daemon inside a Docker container. This value must be set to true only if this build project will be used to build Docker images, and the specified build environment image is not one provided by AWS CodeBuild with Docker support. Otherwise, all associated builds that attempt to interact with the Docker daemon will fail. Default: false

        :exampleMetadata: infused

        Example::

            # vpc: ec2.Vpc
            # my_security_group: ec2.SecurityGroup
            
            pipelines.CodePipeline(self, "Pipeline",
                # Standard CodePipeline properties
                synth=pipelines.ShellStep("Synth",
                    input=pipelines.CodePipelineSource.connection("my-org/my-app", "main",
                        connection_arn="arn:aws:codestar-connections:us-east-1:222222222222:connection/7d2469ff-514a-4e4f-9003-5ca4a43cdc41"
                    ),
                    commands=["npm ci", "npm run build", "npx cdk synth"
                    ]
                ),
            
                # Defaults for all CodeBuild projects
                code_build_defaults=pipelines.CodeBuildOptions(
                    # Prepend commands and configuration to all projects
                    partial_build_spec=codebuild.BuildSpec.from_object({
                        "version": "0.2"
                    }),
            
                    # Control the build environment
                    build_environment=codebuild.BuildEnvironment(
                        compute_type=codebuild.ComputeType.LARGE
                    ),
            
                    # Control Elastic Network Interface creation
                    vpc=vpc,
                    subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
                    security_groups=[my_security_group],
            
                    # Additional policy statements for the execution role
                    role_policy=[
                        iam.PolicyStatement()
                    ]
                ),
            
                synth_code_build_defaults=pipelines.CodeBuildOptions(),
                asset_publishing_code_build_defaults=pipelines.CodeBuildOptions(),
                self_mutation_code_build_defaults=pipelines.CodeBuildOptions()
            )
        '''
        if isinstance(certificate, dict):
            certificate = BuildEnvironmentCertificate(**certificate)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed1939e3af93484f8a479f8ad5736852f71e3adc35322c91a62e83ee6b429dc8)
            check_type(argname="argument build_image", value=build_image, expected_type=type_hints["build_image"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument compute_type", value=compute_type, expected_type=type_hints["compute_type"])
            check_type(argname="argument environment_variables", value=environment_variables, expected_type=type_hints["environment_variables"])
            check_type(argname="argument privileged", value=privileged, expected_type=type_hints["privileged"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if build_image is not None:
            self._values["build_image"] = build_image
        if certificate is not None:
            self._values["certificate"] = certificate
        if compute_type is not None:
            self._values["compute_type"] = compute_type
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if privileged is not None:
            self._values["privileged"] = privileged

    @builtins.property
    def build_image(self) -> typing.Optional["IBuildImage"]:
        '''The image used for the builds.

        :default: LinuxBuildImage.STANDARD_1_0
        '''
        result = self._values.get("build_image")
        return typing.cast(typing.Optional["IBuildImage"], result)

    @builtins.property
    def certificate(self) -> typing.Optional["BuildEnvironmentCertificate"]:
        '''The location of the PEM-encoded certificate for the build project.

        :default: - No external certificate is added to the project
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional["BuildEnvironmentCertificate"], result)

    @builtins.property
    def compute_type(self) -> typing.Optional["ComputeType"]:
        '''The type of compute to use for this build.

        See the {@link ComputeType} enum for the possible values.

        :default: taken from {@link #buildImage#defaultComputeType}
        '''
        result = self._values.get("compute_type")
        return typing.cast(typing.Optional["ComputeType"], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, "BuildEnvironmentVariable"]]:
        '''The environment variables that your builds can use.'''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "BuildEnvironmentVariable"]], result)

    @builtins.property
    def privileged(self) -> typing.Optional[builtins.bool]:
        '''Indicates how the project builds Docker images.

        Specify true to enable
        running the Docker daemon inside a Docker container. This value must be
        set to true only if this build project will be used to build Docker
        images, and the specified build environment image is not one provided by
        AWS CodeBuild with Docker support. Otherwise, all associated builds that
        attempt to interact with the Docker daemon will fail.

        :default: false
        '''
        result = self._values.get("privileged")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildEnvironment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.BuildEnvironmentCertificate",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "object_key": "objectKey"},
)
class BuildEnvironmentCertificate:
    def __init__(
        self,
        *,
        bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
        object_key: builtins.str,
    ) -> None:
        '''Location of a PEM certificate on S3.

        :param bucket: The bucket where the certificate is.
        :param object_key: The full path and name of the key file.

        :exampleMetadata: infused

        Example::

            # ecr_repository: ecr.Repository
            
            
            codebuild.Project(self, "Project",
                environment=codebuild.BuildEnvironment(
                    build_image=codebuild.WindowsBuildImage.from_ecr_repository(ecr_repository, "v1.0", codebuild.WindowsImageType.SERVER_2019),
                    # optional certificate to include in the build image
                    certificate=codebuild.BuildEnvironmentCertificate(
                        bucket=s3.Bucket.from_bucket_name(self, "Bucket", "my-bucket"),
                        object_key="path/to/cert.pem"
                    )
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c8df7f26ec8e9badf3c1e1bc83532e47fb7441fa8152a0415550c4b33f4405e)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument object_key", value=object_key, expected_type=type_hints["object_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
            "object_key": object_key,
        }

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_55f001a5.IBucket:
        '''The bucket where the certificate is.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_55f001a5.IBucket, result)

    @builtins.property
    def object_key(self) -> builtins.str:
        '''The full path and name of the key file.'''
        result = self._values.get("object_key")
        assert result is not None, "Required property 'object_key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildEnvironmentCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.BuildEnvironmentVariable",
    jsii_struct_bases=[],
    name_mapping={"value": "value", "type": "type"},
)
class BuildEnvironmentVariable:
    def __init__(
        self,
        *,
        value: typing.Any,
        type: typing.Optional["BuildEnvironmentVariableType"] = None,
    ) -> None:
        '''
        :param value: The value of the environment variable. For plain-text variables (the default), this is the literal value of variable. For SSM parameter variables, pass the name of the parameter here (``parameterName`` property of ``IParameter``). For SecretsManager variables secrets, pass either the secret name (``secretName`` property of ``ISecret``) or the secret ARN (``secretArn`` property of ``ISecret``) here, along with optional SecretsManager qualifiers separated by ':', like the JSON key, or the version or stage (see https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec.env.secrets-manager for details).
        :param type: The type of environment variable. Default: PlainText

        :exampleMetadata: infused

        Example::

            # later:
            # project: codebuild.PipelineProject
            source_output = codepipeline.Artifact()
            build_action = codepipeline_actions.CodeBuildAction(
                action_name="Build1",
                input=source_output,
                project=codebuild.PipelineProject(self, "Project",
                    build_spec=codebuild.BuildSpec.from_object({
                        "version": "0.2",
                        "env": {
                            "exported-variables": ["MY_VAR"
                            ]
                        },
                        "phases": {
                            "build": {
                                "commands": "export MY_VAR=\"some value\""
                            }
                        }
                    })
                ),
                variables_namespace="MyNamespace"
            )
            codepipeline_actions.CodeBuildAction(
                action_name="CodeBuild",
                project=project,
                input=source_output,
                environment_variables={
                    "MyVar": codebuild.BuildEnvironmentVariable(
                        value=build_action.variable("MY_VAR")
                    )
                }
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9b1d8664991b60ade51b64d6c6f11f5d40b655c9ab44a07207821ecc2571742)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "value": value,
        }
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def value(self) -> typing.Any:
        '''The value of the environment variable.

        For plain-text variables (the default), this is the literal value of variable.
        For SSM parameter variables, pass the name of the parameter here (``parameterName`` property of ``IParameter``).
        For SecretsManager variables secrets, pass either the secret name (``secretName`` property of ``ISecret``)
        or the secret ARN (``secretArn`` property of ``ISecret``) here,
        along with optional SecretsManager qualifiers separated by ':', like the JSON key, or the version or stage
        (see https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec.env.secrets-manager for details).
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(typing.Any, result)

    @builtins.property
    def type(self) -> typing.Optional["BuildEnvironmentVariableType"]:
        '''The type of environment variable.

        :default: PlainText
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional["BuildEnvironmentVariableType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildEnvironmentVariable(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-codebuild.BuildEnvironmentVariableType")
class BuildEnvironmentVariableType(enum.Enum):
    '''
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_codebuild as codebuild
        
        
        codebuild_project = codebuild.Project(self, "Project",
            project_name="MyTestProject",
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "build": {
                        "commands": ["echo \"Hello, CodeBuild!\""
                        ]
                    }
                }
            })
        )
        
        task = tasks.CodeBuildStartBuild(self, "Task",
            project=codebuild_project,
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
            environment_variables_override={
                "ZONE": codebuild.BuildEnvironmentVariable(
                    type=codebuild.BuildEnvironmentVariableType.PLAINTEXT,
                    value=sfn.JsonPath.string_at("$.envVariables.zone")
                )
            }
        )
    '''

    PLAINTEXT = "PLAINTEXT"
    '''An environment variable in plaintext format.'''
    PARAMETER_STORE = "PARAMETER_STORE"
    '''An environment variable stored in Systems Manager Parameter Store.'''
    SECRETS_MANAGER = "SECRETS_MANAGER"
    '''An environment variable stored in AWS Secrets Manager.'''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.BuildImageBindOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class BuildImageBindOptions:
    def __init__(self) -> None:
        '''Optional arguments to {@link IBuildImage.binder} - currently empty.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            
            build_image_bind_options = codebuild.BuildImageBindOptions()
        '''
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildImageBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.BuildImageConfig",
    jsii_struct_bases=[],
    name_mapping={},
)
class BuildImageConfig:
    def __init__(self) -> None:
        '''The return type from {@link IBuildImage.binder} - currently empty.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            
            build_image_config = codebuild.BuildImageConfig()
        '''
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildImageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BuildSpec(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-codebuild.BuildSpec",
):
    '''BuildSpec for CodeBuild projects.

    :exampleMetadata: infused

    Example::

        # later:
        # project: codebuild.PipelineProject
        source_output = codepipeline.Artifact()
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="Build1",
            input=source_output,
            project=codebuild.PipelineProject(self, "Project",
                build_spec=codebuild.BuildSpec.from_object({
                    "version": "0.2",
                    "env": {
                        "exported-variables": ["MY_VAR"
                        ]
                    },
                    "phases": {
                        "build": {
                            "commands": "export MY_VAR=\"some value\""
                        }
                    }
                })
            ),
            variables_namespace="MyNamespace"
        )
        codepipeline_actions.CodeBuildAction(
            action_name="CodeBuild",
            project=project,
            input=source_output,
            environment_variables={
                "MyVar": codebuild.BuildEnvironmentVariable(
                    value=build_action.variable("MY_VAR")
                )
            }
        )
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromObject")
    @builtins.classmethod
    def from_object(
        cls,
        value: typing.Mapping[builtins.str, typing.Any],
    ) -> "BuildSpec":
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__118f00606d61b3311a987f2e6085927a009ccbc074c4bf2c29338e814f03f27d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("BuildSpec", jsii.sinvoke(cls, "fromObject", [value]))

    @jsii.member(jsii_name="fromObjectToYaml")
    @builtins.classmethod
    def from_object_to_yaml(
        cls,
        value: typing.Mapping[builtins.str, typing.Any],
    ) -> "BuildSpec":
        '''Create a buildspec from an object that will be rendered as YAML in the resulting CloudFormation template.

        :param value: the object containing the buildspec that will be rendered as YAML.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a81b7cbd7c4ee1bf82cd3918f7aaf6188813a759ce5cfd92f43055c2869b601b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("BuildSpec", jsii.sinvoke(cls, "fromObjectToYaml", [value]))

    @jsii.member(jsii_name="fromSourceFilename")
    @builtins.classmethod
    def from_source_filename(cls, filename: builtins.str) -> "BuildSpec":
        '''Use a file from the source as buildspec.

        Use this if you want to use a file different from 'buildspec.yml'`

        :param filename: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__896c395e9727365976920c9afac46f4ac53dc1b7839589cc3c2c9bd45a15202d)
            check_type(argname="argument filename", value=filename, expected_type=type_hints["filename"])
        return typing.cast("BuildSpec", jsii.sinvoke(cls, "fromSourceFilename", [filename]))

    @jsii.member(jsii_name="toBuildSpec")
    @abc.abstractmethod
    def to_build_spec(self) -> builtins.str:
        '''Render the represented BuildSpec.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="isImmediate")
    @abc.abstractmethod
    def is_immediate(self) -> builtins.bool:
        '''Whether the buildspec is directly available or deferred until build-time.'''
        ...


class _BuildSpecProxy(BuildSpec):
    @jsii.member(jsii_name="toBuildSpec")
    def to_build_spec(self) -> builtins.str:
        '''Render the represented BuildSpec.'''
        return typing.cast(builtins.str, jsii.invoke(self, "toBuildSpec", []))

    @builtins.property
    @jsii.member(jsii_name="isImmediate")
    def is_immediate(self) -> builtins.bool:
        '''Whether the buildspec is directly available or deferred until build-time.'''
        return typing.cast(builtins.bool, jsii.get(self, "isImmediate"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BuildSpec).__jsii_proxy_class__ = lambda : _BuildSpecProxy


class Cache(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-codebuild.Cache"):
    '''Cache options for CodeBuild Project.

    A cache can store reusable pieces of your build environment and use them across multiple builds.

    :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-caching.html
    :exampleMetadata: infused

    Example::

        # my_caching_bucket: s3.Bucket
        
        
        codebuild.Project(self, "Project",
            source=codebuild.Source.bit_bucket(
                owner="awslabs",
                repo="aws-cdk"
            ),
        
            cache=codebuild.Cache.bucket(my_caching_bucket),
        
            # BuildSpec with a 'cache' section necessary for S3 caching. This can
            # also come from 'buildspec.yml' in your source.
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "build": {
                        "commands": ["..."]
                    }
                },
                "cache": {
                    "paths": ["/root/cachedir/**/*"
                    ]
                }
            })
        )
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="bucket")
    @builtins.classmethod
    def bucket(
        cls,
        bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
        *,
        prefix: typing.Optional[builtins.str] = None,
    ) -> "Cache":
        '''Create an S3 caching strategy.

        :param bucket: the S3 bucket to use for caching.
        :param prefix: The prefix to use to store the cache in the bucket.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a690d23d363dd3a701ea1a18a91365177cc6d0f01d2e8874ee417d74d465eaf)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
        options = BucketCacheOptions(prefix=prefix)

        return typing.cast("Cache", jsii.sinvoke(cls, "bucket", [bucket, options]))

    @jsii.member(jsii_name="local")
    @builtins.classmethod
    def local(cls, *modes: "LocalCacheMode") -> "Cache":
        '''Create a local caching strategy.

        :param modes: the mode(s) to enable for local caching.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acbfc2e273c01ece9511679ce81d636c3a5d6a50de39f37c49c734c4eab76ad8)
            check_type(argname="argument modes", value=modes, expected_type=typing.Tuple[type_hints["modes"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast("Cache", jsii.sinvoke(cls, "local", [*modes]))

    @jsii.member(jsii_name="none")
    @builtins.classmethod
    def none(cls) -> "Cache":
        return typing.cast("Cache", jsii.sinvoke(cls, "none", []))


class _CacheProxy(Cache):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Cache).__jsii_proxy_class__ = lambda : _CacheProxy


@jsii.implements(_aws_cdk_core_f4b25747.IInspectable)
class CfnProject(
    _aws_cdk_core_f4b25747.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.CfnProject",
):
    '''A CloudFormation ``AWS::CodeBuild::Project``.

    The ``AWS::CodeBuild::Project`` resource configures how AWS CodeBuild builds your source code. For example, it tells CodeBuild where to get the source code and which build environment to use.
    .. epigraph::

       To unset or remove a project value via CFN, explicitly provide the attribute with value as empty input.

    :cloudformationResource: AWS::CodeBuild::Project
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_codebuild as codebuild
        
        cfn_project = codebuild.CfnProject(self, "MyCfnProject",
            artifacts=codebuild.CfnProject.ArtifactsProperty(
                type="type",
        
                # the properties below are optional
                artifact_identifier="artifactIdentifier",
                encryption_disabled=False,
                location="location",
                name="name",
                namespace_type="namespaceType",
                override_artifact_name=False,
                packaging="packaging",
                path="path"
            ),
            environment=codebuild.CfnProject.EnvironmentProperty(
                compute_type="computeType",
                image="image",
                type="type",
        
                # the properties below are optional
                certificate="certificate",
                environment_variables=[codebuild.CfnProject.EnvironmentVariableProperty(
                    name="name",
                    value="value",
        
                    # the properties below are optional
                    type="type"
                )],
                image_pull_credentials_type="imagePullCredentialsType",
                privileged_mode=False,
                registry_credential=codebuild.CfnProject.RegistryCredentialProperty(
                    credential="credential",
                    credential_provider="credentialProvider"
                )
            ),
            service_role="serviceRole",
            source=codebuild.CfnProject.SourceProperty(
                type="type",
        
                # the properties below are optional
                auth=codebuild.CfnProject.SourceAuthProperty(
                    type="type",
        
                    # the properties below are optional
                    resource="resource"
                ),
                build_spec="buildSpec",
                build_status_config=codebuild.CfnProject.BuildStatusConfigProperty(
                    context="context",
                    target_url="targetUrl"
                ),
                git_clone_depth=123,
                git_submodules_config=codebuild.CfnProject.GitSubmodulesConfigProperty(
                    fetch_submodules=False
                ),
                insecure_ssl=False,
                location="location",
                report_build_status=False,
                source_identifier="sourceIdentifier"
            ),
        
            # the properties below are optional
            badge_enabled=False,
            build_batch_config=codebuild.CfnProject.ProjectBuildBatchConfigProperty(
                batch_report_mode="batchReportMode",
                combine_artifacts=False,
                restrictions=codebuild.CfnProject.BatchRestrictionsProperty(
                    compute_types_allowed=["computeTypesAllowed"],
                    maximum_builds_allowed=123
                ),
                service_role="serviceRole",
                timeout_in_mins=123
            ),
            cache=codebuild.CfnProject.ProjectCacheProperty(
                type="type",
        
                # the properties below are optional
                location="location",
                modes=["modes"]
            ),
            concurrent_build_limit=123,
            description="description",
            encryption_key="encryptionKey",
            file_system_locations=[codebuild.CfnProject.ProjectFileSystemLocationProperty(
                identifier="identifier",
                location="location",
                mount_point="mountPoint",
                type="type",
        
                # the properties below are optional
                mount_options="mountOptions"
            )],
            logs_config=codebuild.CfnProject.LogsConfigProperty(
                cloud_watch_logs=codebuild.CfnProject.CloudWatchLogsConfigProperty(
                    status="status",
        
                    # the properties below are optional
                    group_name="groupName",
                    stream_name="streamName"
                ),
                s3_logs=codebuild.CfnProject.S3LogsConfigProperty(
                    status="status",
        
                    # the properties below are optional
                    encryption_disabled=False,
                    location="location"
                )
            ),
            name="name",
            queued_timeout_in_minutes=123,
            resource_access_role="resourceAccessRole",
            secondary_artifacts=[codebuild.CfnProject.ArtifactsProperty(
                type="type",
        
                # the properties below are optional
                artifact_identifier="artifactIdentifier",
                encryption_disabled=False,
                location="location",
                name="name",
                namespace_type="namespaceType",
                override_artifact_name=False,
                packaging="packaging",
                path="path"
            )],
            secondary_sources=[codebuild.CfnProject.SourceProperty(
                type="type",
        
                # the properties below are optional
                auth=codebuild.CfnProject.SourceAuthProperty(
                    type="type",
        
                    # the properties below are optional
                    resource="resource"
                ),
                build_spec="buildSpec",
                build_status_config=codebuild.CfnProject.BuildStatusConfigProperty(
                    context="context",
                    target_url="targetUrl"
                ),
                git_clone_depth=123,
                git_submodules_config=codebuild.CfnProject.GitSubmodulesConfigProperty(
                    fetch_submodules=False
                ),
                insecure_ssl=False,
                location="location",
                report_build_status=False,
                source_identifier="sourceIdentifier"
            )],
            secondary_source_versions=[codebuild.CfnProject.ProjectSourceVersionProperty(
                source_identifier="sourceIdentifier",
        
                # the properties below are optional
                source_version="sourceVersion"
            )],
            source_version="sourceVersion",
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            timeout_in_minutes=123,
            triggers=codebuild.CfnProject.ProjectTriggersProperty(
                build_type="buildType",
                filter_groups=[[codebuild.CfnProject.WebhookFilterProperty(
                    pattern="pattern",
                    type="type",
        
                    # the properties below are optional
                    exclude_matched_pattern=False
                )]],
                webhook=False
            ),
            visibility="visibility",
            vpc_config=codebuild.CfnProject.VpcConfigProperty(
                security_group_ids=["securityGroupIds"],
                subnets=["subnets"],
                vpc_id="vpcId"
            )
        )
    '''

    def __init__(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        id: builtins.str,
        *,
        artifacts: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnProject.ArtifactsProperty", typing.Dict[builtins.str, typing.Any]]],
        environment: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnProject.EnvironmentProperty", typing.Dict[builtins.str, typing.Any]]],
        service_role: builtins.str,
        source: typing.Union[typing.Union["CfnProject.SourceProperty", typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable],
        badge_enabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
        build_batch_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnProject.ProjectBuildBatchConfigProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        cache: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnProject.ProjectCacheProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        concurrent_build_limit: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[builtins.str] = None,
        file_system_locations: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnProject.ProjectFileSystemLocationProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
        logs_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnProject.LogsConfigProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        name: typing.Optional[builtins.str] = None,
        queued_timeout_in_minutes: typing.Optional[jsii.Number] = None,
        resource_access_role: typing.Optional[builtins.str] = None,
        secondary_artifacts: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnProject.ArtifactsProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
        secondary_sources: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[typing.Union["CfnProject.SourceProperty", typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]]]] = None,
        secondary_source_versions: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnProject.ProjectSourceVersionProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
        source_version: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
        timeout_in_minutes: typing.Optional[jsii.Number] = None,
        triggers: typing.Optional[typing.Union[typing.Union["CfnProject.ProjectTriggersProperty", typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]] = None,
        visibility: typing.Optional[builtins.str] = None,
        vpc_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnProject.VpcConfigProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Create a new ``AWS::CodeBuild::Project``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param artifacts: ``Artifacts`` is a property of the `AWS::CodeBuild::Project <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html>`_ resource that specifies output settings for artifacts generated by an AWS CodeBuild build.
        :param environment: The build environment settings for the project, such as the environment type or the environment variables to use for the build environment.
        :param service_role: The ARN of the IAM role that enables AWS CodeBuild to interact with dependent AWS services on behalf of the AWS account.
        :param source: The source code settings for the project, such as the source code's repository type and location.
        :param badge_enabled: Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge. For more information, see `Build Badges Sample <https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-badges.html>`_ in the *AWS CodeBuild User Guide* . .. epigraph:: Including build badges with your project is currently not supported if the source type is CodePipeline. If you specify ``CODEPIPELINE`` for the ``Source`` property, do not specify the ``BadgeEnabled`` property.
        :param build_batch_config: A ``ProjectBuildBatchConfig`` object that defines the batch build options for the project.
        :param cache: Settings that AWS CodeBuild uses to store and reuse build dependencies.
        :param concurrent_build_limit: The maximum number of concurrent builds that are allowed for this project. New builds are only started if the current number of builds is less than or equal to this limit. If the current build count meets this limit, new builds are throttled and are not run.
        :param description: A description that makes the build project easy to identify.
        :param encryption_key: The AWS Key Management Service customer master key (CMK) to be used for encrypting the build output artifacts. .. epigraph:: You can use a cross-account KMS key to encrypt the build output artifacts if your service role has permission to that key. You can specify either the Amazon Resource Name (ARN) of the CMK or, if available, the CMK's alias (using the format ``alias/<alias-name>`` ). If you don't specify a value, CodeBuild uses the managed CMK for Amazon Simple Storage Service (Amazon S3).
        :param file_system_locations: An array of ``ProjectFileSystemLocation`` objects for a CodeBuild build project. A ``ProjectFileSystemLocation`` object specifies the ``identifier`` , ``location`` , ``mountOptions`` , ``mountPoint`` , and ``type`` of a file system created using Amazon Elastic File System.
        :param logs_config: Information about logs for the build project. A project can create logs in CloudWatch Logs, an S3 bucket, or both.
        :param name: The name of the build project. The name must be unique across all of the projects in your AWS account .
        :param queued_timeout_in_minutes: The number of minutes a build is allowed to be queued before it times out.
        :param resource_access_role: The ARN of the IAM role that enables CodeBuild to access the CloudWatch Logs and Amazon S3 artifacts for the project's builds.
        :param secondary_artifacts: A list of ``Artifacts`` objects. Each artifacts object specifies output settings that the project generates during a build.
        :param secondary_sources: An array of ``ProjectSource`` objects.
        :param secondary_source_versions: An array of ``ProjectSourceVersion`` objects. If ``secondarySourceVersions`` is specified at the build level, then they take over these ``secondarySourceVersions`` (at the project level).
        :param source_version: A version of the build input to be built for this project. If not specified, the latest version is used. If specified, it must be one of: - For CodeCommit: the commit ID, branch, or Git tag to use. - For GitHub: the commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build. If a pull request ID is specified, it must use the format ``pr/pull-request-ID`` (for example ``pr/25`` ). If a branch name is specified, the branch's HEAD commit ID is used. If not specified, the default branch's HEAD commit ID is used. - For Bitbucket: the commit ID, branch name, or tag name that corresponds to the version of the source code you want to build. If a branch name is specified, the branch's HEAD commit ID is used. If not specified, the default branch's HEAD commit ID is used. - For Amazon S3: the version ID of the object that represents the build input ZIP file to use. If ``sourceVersion`` is specified at the build level, then that version takes precedence over this ``sourceVersion`` (at the project level). For more information, see `Source Version Sample with CodeBuild <https://docs.aws.amazon.com/codebuild/latest/userguide/sample-source-version.html>`_ in the *AWS CodeBuild User Guide* .
        :param tags: An arbitrary set of tags (key-value pairs) for the AWS CodeBuild project. These tags are available for use by AWS services that support AWS CodeBuild build project tags.
        :param timeout_in_minutes: How long, in minutes, from 5 to 480 (8 hours), for AWS CodeBuild to wait before timing out any related build that did not get marked as completed. The default is 60 minutes.
        :param triggers: For an existing AWS CodeBuild build project that has its source code stored in a GitHub repository, enables AWS CodeBuild to begin automatically rebuilding the source code every time a code change is pushed to the repository.
        :param visibility: Specifies the visibility of the project's builds. Possible values are:. - **PUBLIC_READ** - The project builds are visible to the public. - **PRIVATE** - The project builds are not visible to the public.
        :param vpc_config: ``VpcConfig`` specifies settings that enable AWS CodeBuild to access resources in an Amazon VPC. For more information, see `Use AWS CodeBuild with Amazon Virtual Private Cloud <https://docs.aws.amazon.com/codebuild/latest/userguide/vpc-support.html>`_ in the *AWS CodeBuild User Guide* .
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4640761b9219e0ae5cbbf0bdc474c00b8dd392f786e95a3d8a8cef4f7716a7f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnProjectProps(
            artifacts=artifacts,
            environment=environment,
            service_role=service_role,
            source=source,
            badge_enabled=badge_enabled,
            build_batch_config=build_batch_config,
            cache=cache,
            concurrent_build_limit=concurrent_build_limit,
            description=description,
            encryption_key=encryption_key,
            file_system_locations=file_system_locations,
            logs_config=logs_config,
            name=name,
            queued_timeout_in_minutes=queued_timeout_in_minutes,
            resource_access_role=resource_access_role,
            secondary_artifacts=secondary_artifacts,
            secondary_sources=secondary_sources,
            secondary_source_versions=secondary_source_versions,
            source_version=source_version,
            tags=tags,
            timeout_in_minutes=timeout_in_minutes,
            triggers=triggers,
            visibility=visibility,
            vpc_config=vpc_config,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _aws_cdk_core_f4b25747.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a06132306bff654e679074014a28ac1f606760095358445b8e9bcc53efe271c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8c7914ea84c5e3ad0150d14fc636b09bf92184ec677393e2fb4ce69023e2ae4)
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
        '''The ARN of the AWS CodeBuild project, such as ``arn:aws:codebuild:us-west-2:123456789012:project/myProjectName`` .

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
        '''An arbitrary set of tags (key-value pairs) for the AWS CodeBuild project.

        These tags are available for use by AWS services that support AWS CodeBuild build project tags.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-tags
        '''
        return typing.cast(_aws_cdk_core_f4b25747.TagManager, jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="artifacts")
    def artifacts(
        self,
    ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ArtifactsProperty"]:
        '''``Artifacts`` is a property of the `AWS::CodeBuild::Project <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html>`_ resource that specifies output settings for artifacts generated by an AWS CodeBuild build.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-artifacts
        '''
        return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ArtifactsProperty"], jsii.get(self, "artifacts"))

    @artifacts.setter
    def artifacts(
        self,
        value: typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ArtifactsProperty"],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c55c256ad359fcb0982b272da4db3560f3746767047d09c16073cb119581754d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "artifacts", value)

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(
        self,
    ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.EnvironmentProperty"]:
        '''The build environment settings for the project, such as the environment type or the environment variables to use for the build environment.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-environment
        '''
        return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.EnvironmentProperty"], jsii.get(self, "environment"))

    @environment.setter
    def environment(
        self,
        value: typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.EnvironmentProperty"],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f029191340d240e7cc5678773f76b63f06de56238b92cc309d84f99948ecc4ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environment", value)

    @builtins.property
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> builtins.str:
        '''The ARN of the IAM role that enables AWS CodeBuild to interact with dependent AWS services on behalf of the AWS account.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-servicerole
        '''
        return typing.cast(builtins.str, jsii.get(self, "serviceRole"))

    @service_role.setter
    def service_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a9134f80fbb1f6c7c3e6be01e699060665a696ae31b28c948bcc938c1e77494)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceRole", value)

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(
        self,
    ) -> typing.Union["CfnProject.SourceProperty", _aws_cdk_core_f4b25747.IResolvable]:
        '''The source code settings for the project, such as the source code's repository type and location.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-source
        '''
        return typing.cast(typing.Union["CfnProject.SourceProperty", _aws_cdk_core_f4b25747.IResolvable], jsii.get(self, "source"))

    @source.setter
    def source(
        self,
        value: typing.Union["CfnProject.SourceProperty", _aws_cdk_core_f4b25747.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d416158b8bd0647974cdfc8f7de578714e9e9e3f639676ddaa4a9e0838025d21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value)

    @builtins.property
    @jsii.member(jsii_name="badgeEnabled")
    def badge_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
        '''Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge.

        For more information, see `Build Badges Sample <https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-badges.html>`_ in the *AWS CodeBuild User Guide* .
        .. epigraph::

           Including build badges with your project is currently not supported if the source type is CodePipeline. If you specify ``CODEPIPELINE`` for the ``Source`` property, do not specify the ``BadgeEnabled`` property.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-badgeenabled
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], jsii.get(self, "badgeEnabled"))

    @badge_enabled.setter
    def badge_enabled(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bae52acb00f614cf7323bb3a2c04c0838f471f99af99920226cc46a1edeb9807)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "badgeEnabled", value)

    @builtins.property
    @jsii.member(jsii_name="buildBatchConfig")
    def build_batch_config(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ProjectBuildBatchConfigProperty"]]:
        '''A ``ProjectBuildBatchConfig`` object that defines the batch build options for the project.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-buildbatchconfig
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ProjectBuildBatchConfigProperty"]], jsii.get(self, "buildBatchConfig"))

    @build_batch_config.setter
    def build_batch_config(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ProjectBuildBatchConfigProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9c6b0cbd674e4abeadbe277365d8f69f02729897853285e04c984b4429fa79a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "buildBatchConfig", value)

    @builtins.property
    @jsii.member(jsii_name="cache")
    def cache(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ProjectCacheProperty"]]:
        '''Settings that AWS CodeBuild uses to store and reuse build dependencies.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-cache
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ProjectCacheProperty"]], jsii.get(self, "cache"))

    @cache.setter
    def cache(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ProjectCacheProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11b11ad399f0c44e1ae18a14725c1cd70d493fab019f28f2bc168121648fd1ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cache", value)

    @builtins.property
    @jsii.member(jsii_name="concurrentBuildLimit")
    def concurrent_build_limit(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of concurrent builds that are allowed for this project.

        New builds are only started if the current number of builds is less than or equal to this limit. If the current build count meets this limit, new builds are throttled and are not run.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-concurrentbuildlimit
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "concurrentBuildLimit"))

    @concurrent_build_limit.setter
    def concurrent_build_limit(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5203be9ce9df0e12c8e36eb7f4d6ee39860c05c6e4ce4f44d016444246e0a81b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "concurrentBuildLimit", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''A description that makes the build project easy to identify.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70de0d42e0806f2db82cae8edba3eb8e65265388aafc19056626962094c09dc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[builtins.str]:
        '''The AWS Key Management Service customer master key (CMK) to be used for encrypting the build output artifacts.

        .. epigraph::

           You can use a cross-account KMS key to encrypt the build output artifacts if your service role has permission to that key.

        You can specify either the Amazon Resource Name (ARN) of the CMK or, if available, the CMK's alias (using the format ``alias/<alias-name>`` ). If you don't specify a value, CodeBuild uses the managed CMK for Amazon Simple Storage Service (Amazon S3).

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-encryptionkey
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionKey"))

    @encryption_key.setter
    def encryption_key(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4e64d554e0f7c4ff3839123012965e5631538c0a9ebafc015e62eabb5a3d07b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionKey", value)

    @builtins.property
    @jsii.member(jsii_name="fileSystemLocations")
    def file_system_locations(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ProjectFileSystemLocationProperty"]]]]:
        '''An array of ``ProjectFileSystemLocation`` objects for a CodeBuild build project.

        A ``ProjectFileSystemLocation`` object specifies the ``identifier`` , ``location`` , ``mountOptions`` , ``mountPoint`` , and ``type`` of a file system created using Amazon Elastic File System.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-filesystemlocations
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ProjectFileSystemLocationProperty"]]]], jsii.get(self, "fileSystemLocations"))

    @file_system_locations.setter
    def file_system_locations(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ProjectFileSystemLocationProperty"]]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58d8654761501bdea77af688fe80754a3c5cb919af8a06732ec2946f29ae21ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fileSystemLocations", value)

    @builtins.property
    @jsii.member(jsii_name="logsConfig")
    def logs_config(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.LogsConfigProperty"]]:
        '''Information about logs for the build project.

        A project can create logs in CloudWatch Logs, an S3 bucket, or both.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-logsconfig
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.LogsConfigProperty"]], jsii.get(self, "logsConfig"))

    @logs_config.setter
    def logs_config(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.LogsConfigProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b95ef485b0fbbc4d8b02c58f147da30c011ac1d75dc27c26c573353cee4a3cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logsConfig", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the build project.

        The name must be unique across all of the projects in your AWS account .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02366a2811452aa694d57d58d427375b7aa3202f77674464fb5f4c851aefca82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="queuedTimeoutInMinutes")
    def queued_timeout_in_minutes(self) -> typing.Optional[jsii.Number]:
        '''The number of minutes a build is allowed to be queued before it times out.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-queuedtimeoutinminutes
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "queuedTimeoutInMinutes"))

    @queued_timeout_in_minutes.setter
    def queued_timeout_in_minutes(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8916c820c6a5cb1afb76e917cbab84c56d729b94a49d61efcea653704305ab68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queuedTimeoutInMinutes", value)

    @builtins.property
    @jsii.member(jsii_name="resourceAccessRole")
    def resource_access_role(self) -> typing.Optional[builtins.str]:
        '''The ARN of the IAM role that enables CodeBuild to access the CloudWatch Logs and Amazon S3 artifacts for the project's builds.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-resourceaccessrole
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceAccessRole"))

    @resource_access_role.setter
    def resource_access_role(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ffc3243ca8f0c717d9205a79466595bdd9bbf7af722a819fe45e18ff45c52bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceAccessRole", value)

    @builtins.property
    @jsii.member(jsii_name="secondaryArtifacts")
    def secondary_artifacts(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ArtifactsProperty"]]]]:
        '''A list of ``Artifacts`` objects.

        Each artifacts object specifies output settings that the project generates during a build.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-secondaryartifacts
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ArtifactsProperty"]]]], jsii.get(self, "secondaryArtifacts"))

    @secondary_artifacts.setter
    def secondary_artifacts(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ArtifactsProperty"]]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__803d0393b0f998fc86dd49c05ba56c5d052380dbae7818c8e50efc712b45d763)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secondaryArtifacts", value)

    @builtins.property
    @jsii.member(jsii_name="secondarySources")
    def secondary_sources(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union["CfnProject.SourceProperty", _aws_cdk_core_f4b25747.IResolvable]]]]:
        '''An array of ``ProjectSource`` objects.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-secondarysources
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union["CfnProject.SourceProperty", _aws_cdk_core_f4b25747.IResolvable]]]], jsii.get(self, "secondarySources"))

    @secondary_sources.setter
    def secondary_sources(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union["CfnProject.SourceProperty", _aws_cdk_core_f4b25747.IResolvable]]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de34a8da11b179e3121bff13c58007ab7980257eb31c0c7b79dbc2fc6aed5e3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secondarySources", value)

    @builtins.property
    @jsii.member(jsii_name="secondarySourceVersions")
    def secondary_source_versions(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ProjectSourceVersionProperty"]]]]:
        '''An array of ``ProjectSourceVersion`` objects.

        If ``secondarySourceVersions`` is specified at the build level, then they take over these ``secondarySourceVersions`` (at the project level).

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-secondarysourceversions
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ProjectSourceVersionProperty"]]]], jsii.get(self, "secondarySourceVersions"))

    @secondary_source_versions.setter
    def secondary_source_versions(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.ProjectSourceVersionProperty"]]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d20a5dbd795c6414478f5a6f55922f13c9fb45bc4e1b0b8fb211354aa202e1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secondarySourceVersions", value)

    @builtins.property
    @jsii.member(jsii_name="sourceVersion")
    def source_version(self) -> typing.Optional[builtins.str]:
        '''A version of the build input to be built for this project.

        If not specified, the latest version is used. If specified, it must be one of:

        - For CodeCommit: the commit ID, branch, or Git tag to use.
        - For GitHub: the commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build. If a pull request ID is specified, it must use the format ``pr/pull-request-ID`` (for example ``pr/25`` ). If a branch name is specified, the branch's HEAD commit ID is used. If not specified, the default branch's HEAD commit ID is used.
        - For Bitbucket: the commit ID, branch name, or tag name that corresponds to the version of the source code you want to build. If a branch name is specified, the branch's HEAD commit ID is used. If not specified, the default branch's HEAD commit ID is used.
        - For Amazon S3: the version ID of the object that represents the build input ZIP file to use.

        If ``sourceVersion`` is specified at the build level, then that version takes precedence over this ``sourceVersion`` (at the project level).

        For more information, see `Source Version Sample with CodeBuild <https://docs.aws.amazon.com/codebuild/latest/userguide/sample-source-version.html>`_ in the *AWS CodeBuild User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-sourceversion
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceVersion"))

    @source_version.setter
    def source_version(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93da05b250d2d46cbc24ece2a515e46f14f555aaedddb625bb67dd405acaaacd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceVersion", value)

    @builtins.property
    @jsii.member(jsii_name="timeoutInMinutes")
    def timeout_in_minutes(self) -> typing.Optional[jsii.Number]:
        '''How long, in minutes, from 5 to 480 (8 hours), for AWS CodeBuild to wait before timing out any related build that did not get marked as completed.

        The default is 60 minutes.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-timeoutinminutes
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutInMinutes"))

    @timeout_in_minutes.setter
    def timeout_in_minutes(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3944d824c436ffe2d088a7b50a91faa328ea65e8dfa376a4b372490fe00a966)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeoutInMinutes", value)

    @builtins.property
    @jsii.member(jsii_name="triggers")
    def triggers(
        self,
    ) -> typing.Optional[typing.Union["CfnProject.ProjectTriggersProperty", _aws_cdk_core_f4b25747.IResolvable]]:
        '''For an existing AWS CodeBuild build project that has its source code stored in a GitHub repository, enables AWS CodeBuild to begin automatically rebuilding the source code every time a code change is pushed to the repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-triggers
        '''
        return typing.cast(typing.Optional[typing.Union["CfnProject.ProjectTriggersProperty", _aws_cdk_core_f4b25747.IResolvable]], jsii.get(self, "triggers"))

    @triggers.setter
    def triggers(
        self,
        value: typing.Optional[typing.Union["CfnProject.ProjectTriggersProperty", _aws_cdk_core_f4b25747.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__362053508828bf50e0e52654852a731a8f9a33909a21054042d9d0f6a1594c92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggers", value)

    @builtins.property
    @jsii.member(jsii_name="visibility")
    def visibility(self) -> typing.Optional[builtins.str]:
        '''Specifies the visibility of the project's builds. Possible values are:.

        - **PUBLIC_READ** - The project builds are visible to the public.
        - **PRIVATE** - The project builds are not visible to the public.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-visibility
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "visibility"))

    @visibility.setter
    def visibility(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d2de9c0a3d90f90e52edfc4de31dbddfa80e7359c9108ac37497d0718678434)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "visibility", value)

    @builtins.property
    @jsii.member(jsii_name="vpcConfig")
    def vpc_config(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.VpcConfigProperty"]]:
        '''``VpcConfig`` specifies settings that enable AWS CodeBuild to access resources in an Amazon VPC.

        For more information, see `Use AWS CodeBuild with Amazon Virtual Private Cloud <https://docs.aws.amazon.com/codebuild/latest/userguide/vpc-support.html>`_ in the *AWS CodeBuild User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-vpcconfig
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.VpcConfigProperty"]], jsii.get(self, "vpcConfig"))

    @vpc_config.setter
    def vpc_config(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.VpcConfigProperty"]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c65229ca137d90a18456c8c453c33bf6a268312d0699b4fa94e5de9623787a3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcConfig", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.ArtifactsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "type": "type",
            "artifact_identifier": "artifactIdentifier",
            "encryption_disabled": "encryptionDisabled",
            "location": "location",
            "name": "name",
            "namespace_type": "namespaceType",
            "override_artifact_name": "overrideArtifactName",
            "packaging": "packaging",
            "path": "path",
        },
    )
    class ArtifactsProperty:
        def __init__(
            self,
            *,
            type: builtins.str,
            artifact_identifier: typing.Optional[builtins.str] = None,
            encryption_disabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            location: typing.Optional[builtins.str] = None,
            name: typing.Optional[builtins.str] = None,
            namespace_type: typing.Optional[builtins.str] = None,
            override_artifact_name: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            packaging: typing.Optional[builtins.str] = None,
            path: typing.Optional[builtins.str] = None,
        ) -> None:
            '''``Artifacts`` is a property of the `AWS::CodeBuild::Project <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html>`_ resource that specifies output settings for artifacts generated by an AWS CodeBuild build.

            :param type: The type of build output artifact. Valid values include:. - ``CODEPIPELINE`` : The build project has build output generated through CodePipeline. .. epigraph:: The ``CODEPIPELINE`` type is not supported for ``secondaryArtifacts`` . - ``NO_ARTIFACTS`` : The build project does not produce any build output. - ``S3`` : The build project stores build output in Amazon S3.
            :param artifact_identifier: An identifier for this artifact definition.
            :param encryption_disabled: Set to true if you do not want your output artifacts encrypted. This option is valid only if your artifacts type is Amazon Simple Storage Service (Amazon S3). If this is set with another artifacts type, an ``invalidInputException`` is thrown.
            :param location: Information about the build output artifact location:. - If ``type`` is set to ``CODEPIPELINE`` , AWS CodePipeline ignores this value if specified. This is because CodePipeline manages its build output locations instead of CodeBuild . - If ``type`` is set to ``NO_ARTIFACTS`` , this value is ignored if specified, because no build output is produced. - If ``type`` is set to ``S3`` , this is the name of the output bucket. If you specify ``CODEPIPELINE`` or ``NO_ARTIFACTS`` for the ``Type`` property, don't specify this property. For all of the other types, you must specify this property.
            :param name: Along with ``path`` and ``namespaceType`` , the pattern that AWS CodeBuild uses to name and store the output artifact:. - If ``type`` is set to ``CODEPIPELINE`` , AWS CodePipeline ignores this value if specified. This is because CodePipeline manages its build output names instead of AWS CodeBuild . - If ``type`` is set to ``NO_ARTIFACTS`` , this value is ignored if specified, because no build output is produced. - If ``type`` is set to ``S3`` , this is the name of the output artifact object. If you set the name to be a forward slash ("/"), the artifact is stored in the root of the output bucket. For example: - If ``path`` is set to ``MyArtifacts`` , ``namespaceType`` is set to ``BUILD_ID`` , and ``name`` is set to ``MyArtifact.zip`` , then the output artifact is stored in ``MyArtifacts/ *build-ID* /MyArtifact.zip`` . - If ``path`` is empty, ``namespaceType`` is set to ``NONE`` , and ``name`` is set to " ``/`` ", the output artifact is stored in the root of the output bucket. - If ``path`` is set to ``MyArtifacts`` , ``namespaceType`` is set to ``BUILD_ID`` , and ``name`` is set to " ``/`` ", the output artifact is stored in ``MyArtifacts/ *build-ID*`` . If you specify ``CODEPIPELINE`` or ``NO_ARTIFACTS`` for the ``Type`` property, don't specify this property. For all of the other types, you must specify this property.
            :param namespace_type: Along with ``path`` and ``name`` , the pattern that AWS CodeBuild uses to determine the name and location to store the output artifact: - If ``type`` is set to ``CODEPIPELINE`` , CodePipeline ignores this value if specified. This is because CodePipeline manages its build output names instead of AWS CodeBuild . - If ``type`` is set to ``NO_ARTIFACTS`` , this value is ignored if specified, because no build output is produced. - If ``type`` is set to ``S3`` , valid values include: - ``BUILD_ID`` : Include the build ID in the location of the build output artifact. - ``NONE`` : Do not include the build ID. This is the default if ``namespaceType`` is not specified. For example, if ``path`` is set to ``MyArtifacts`` , ``namespaceType`` is set to ``BUILD_ID`` , and ``name`` is set to ``MyArtifact.zip`` , the output artifact is stored in ``MyArtifacts/<build-ID>/MyArtifact.zip`` .
            :param override_artifact_name: If set to true a name specified in the buildspec file overrides the artifact name. The name specified in a buildspec file is calculated at build time and uses the Shell command language. For example, you can append a date and time to your artifact name so that it is always unique.
            :param packaging: The type of build output artifact to create:. - If ``type`` is set to ``CODEPIPELINE`` , CodePipeline ignores this value if specified. This is because CodePipeline manages its build output artifacts instead of AWS CodeBuild . - If ``type`` is set to ``NO_ARTIFACTS`` , this value is ignored if specified, because no build output is produced. - If ``type`` is set to ``S3`` , valid values include: - ``NONE`` : AWS CodeBuild creates in the output bucket a folder that contains the build output. This is the default if ``packaging`` is not specified. - ``ZIP`` : AWS CodeBuild creates in the output bucket a ZIP file that contains the build output.
            :param path: Along with ``namespaceType`` and ``name`` , the pattern that AWS CodeBuild uses to name and store the output artifact:. - If ``type`` is set to ``CODEPIPELINE`` , CodePipeline ignores this value if specified. This is because CodePipeline manages its build output names instead of AWS CodeBuild . - If ``type`` is set to ``NO_ARTIFACTS`` , this value is ignored if specified, because no build output is produced. - If ``type`` is set to ``S3`` , this is the path to the output artifact. If ``path`` is not specified, ``path`` is not used. For example, if ``path`` is set to ``MyArtifacts`` , ``namespaceType`` is set to ``NONE`` , and ``name`` is set to ``MyArtifact.zip`` , the output artifact is stored in the output bucket at ``MyArtifacts/MyArtifact.zip`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                artifacts_property = codebuild.CfnProject.ArtifactsProperty(
                    type="type",
                
                    # the properties below are optional
                    artifact_identifier="artifactIdentifier",
                    encryption_disabled=False,
                    location="location",
                    name="name",
                    namespace_type="namespaceType",
                    override_artifact_name=False,
                    packaging="packaging",
                    path="path"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__10e69701b846bc22f6f84739811e2bcf19aca7d43025a4d3790ed5078db67ba6)
                check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                check_type(argname="argument artifact_identifier", value=artifact_identifier, expected_type=type_hints["artifact_identifier"])
                check_type(argname="argument encryption_disabled", value=encryption_disabled, expected_type=type_hints["encryption_disabled"])
                check_type(argname="argument location", value=location, expected_type=type_hints["location"])
                check_type(argname="argument name", value=name, expected_type=type_hints["name"])
                check_type(argname="argument namespace_type", value=namespace_type, expected_type=type_hints["namespace_type"])
                check_type(argname="argument override_artifact_name", value=override_artifact_name, expected_type=type_hints["override_artifact_name"])
                check_type(argname="argument packaging", value=packaging, expected_type=type_hints["packaging"])
                check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "type": type,
            }
            if artifact_identifier is not None:
                self._values["artifact_identifier"] = artifact_identifier
            if encryption_disabled is not None:
                self._values["encryption_disabled"] = encryption_disabled
            if location is not None:
                self._values["location"] = location
            if name is not None:
                self._values["name"] = name
            if namespace_type is not None:
                self._values["namespace_type"] = namespace_type
            if override_artifact_name is not None:
                self._values["override_artifact_name"] = override_artifact_name
            if packaging is not None:
                self._values["packaging"] = packaging
            if path is not None:
                self._values["path"] = path

        @builtins.property
        def type(self) -> builtins.str:
            '''The type of build output artifact. Valid values include:.

            - ``CODEPIPELINE`` : The build project has build output generated through CodePipeline.

            .. epigraph::

               The ``CODEPIPELINE`` type is not supported for ``secondaryArtifacts`` .

            - ``NO_ARTIFACTS`` : The build project does not produce any build output.
            - ``S3`` : The build project stores build output in Amazon S3.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def artifact_identifier(self) -> typing.Optional[builtins.str]:
            '''An identifier for this artifact definition.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-artifactidentifier
            '''
            result = self._values.get("artifact_identifier")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def encryption_disabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''Set to true if you do not want your output artifacts encrypted.

            This option is valid only if your artifacts type is Amazon Simple Storage Service (Amazon S3). If this is set with another artifacts type, an ``invalidInputException`` is thrown.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-encryptiondisabled
            '''
            result = self._values.get("encryption_disabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def location(self) -> typing.Optional[builtins.str]:
            '''Information about the build output artifact location:.

            - If ``type`` is set to ``CODEPIPELINE`` , AWS CodePipeline ignores this value if specified. This is because CodePipeline manages its build output locations instead of CodeBuild .
            - If ``type`` is set to ``NO_ARTIFACTS`` , this value is ignored if specified, because no build output is produced.
            - If ``type`` is set to ``S3`` , this is the name of the output bucket.

            If you specify ``CODEPIPELINE`` or ``NO_ARTIFACTS`` for the ``Type`` property, don't specify this property. For all of the other types, you must specify this property.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-location
            '''
            result = self._values.get("location")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def name(self) -> typing.Optional[builtins.str]:
            '''Along with ``path`` and ``namespaceType`` , the pattern that AWS CodeBuild uses to name and store the output artifact:.

            - If ``type`` is set to ``CODEPIPELINE`` , AWS CodePipeline ignores this value if specified. This is because CodePipeline manages its build output names instead of AWS CodeBuild .
            - If ``type`` is set to ``NO_ARTIFACTS`` , this value is ignored if specified, because no build output is produced.
            - If ``type`` is set to ``S3`` , this is the name of the output artifact object. If you set the name to be a forward slash ("/"), the artifact is stored in the root of the output bucket.

            For example:

            - If ``path`` is set to ``MyArtifacts`` , ``namespaceType`` is set to ``BUILD_ID`` , and ``name`` is set to ``MyArtifact.zip`` , then the output artifact is stored in ``MyArtifacts/ *build-ID* /MyArtifact.zip`` .
            - If ``path`` is empty, ``namespaceType`` is set to ``NONE`` , and ``name`` is set to " ``/`` ", the output artifact is stored in the root of the output bucket.
            - If ``path`` is set to ``MyArtifacts`` , ``namespaceType`` is set to ``BUILD_ID`` , and ``name`` is set to " ``/`` ", the output artifact is stored in ``MyArtifacts/ *build-ID*`` .

            If you specify ``CODEPIPELINE`` or ``NO_ARTIFACTS`` for the ``Type`` property, don't specify this property. For all of the other types, you must specify this property.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-name
            '''
            result = self._values.get("name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def namespace_type(self) -> typing.Optional[builtins.str]:
            '''Along with ``path`` and ``name`` , the pattern that AWS CodeBuild uses to determine the name and location to store the output artifact:  - If ``type`` is set to ``CODEPIPELINE`` , CodePipeline ignores this value if specified.

            This is because CodePipeline manages its build output names instead of AWS CodeBuild .

            - If ``type`` is set to ``NO_ARTIFACTS`` , this value is ignored if specified, because no build output is produced.
            - If ``type`` is set to ``S3`` , valid values include:
            - ``BUILD_ID`` : Include the build ID in the location of the build output artifact.
            - ``NONE`` : Do not include the build ID. This is the default if ``namespaceType`` is not specified.

            For example, if ``path`` is set to ``MyArtifacts`` , ``namespaceType`` is set to ``BUILD_ID`` , and ``name`` is set to ``MyArtifact.zip`` , the output artifact is stored in ``MyArtifacts/<build-ID>/MyArtifact.zip`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-namespacetype
            '''
            result = self._values.get("namespace_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def override_artifact_name(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''If set to true a name specified in the buildspec file overrides the artifact name.

            The name specified in a buildspec file is calculated at build time and uses the Shell command language. For example, you can append a date and time to your artifact name so that it is always unique.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-overrideartifactname
            '''
            result = self._values.get("override_artifact_name")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def packaging(self) -> typing.Optional[builtins.str]:
            '''The type of build output artifact to create:.

            - If ``type`` is set to ``CODEPIPELINE`` , CodePipeline ignores this value if specified. This is because CodePipeline manages its build output artifacts instead of AWS CodeBuild .
            - If ``type`` is set to ``NO_ARTIFACTS`` , this value is ignored if specified, because no build output is produced.
            - If ``type`` is set to ``S3`` , valid values include:
            - ``NONE`` : AWS CodeBuild creates in the output bucket a folder that contains the build output. This is the default if ``packaging`` is not specified.
            - ``ZIP`` : AWS CodeBuild creates in the output bucket a ZIP file that contains the build output.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-packaging
            '''
            result = self._values.get("packaging")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def path(self) -> typing.Optional[builtins.str]:
            '''Along with ``namespaceType`` and ``name`` , the pattern that AWS CodeBuild uses to name and store the output artifact:.

            - If ``type`` is set to ``CODEPIPELINE`` , CodePipeline ignores this value if specified. This is because CodePipeline manages its build output names instead of AWS CodeBuild .
            - If ``type`` is set to ``NO_ARTIFACTS`` , this value is ignored if specified, because no build output is produced.
            - If ``type`` is set to ``S3`` , this is the path to the output artifact. If ``path`` is not specified, ``path`` is not used.

            For example, if ``path`` is set to ``MyArtifacts`` , ``namespaceType`` is set to ``NONE`` , and ``name`` is set to ``MyArtifact.zip`` , the output artifact is stored in the output bucket at ``MyArtifacts/MyArtifact.zip`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-artifacts.html#cfn-codebuild-project-artifacts-path
            '''
            result = self._values.get("path")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ArtifactsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.BatchRestrictionsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "compute_types_allowed": "computeTypesAllowed",
            "maximum_builds_allowed": "maximumBuildsAllowed",
        },
    )
    class BatchRestrictionsProperty:
        def __init__(
            self,
            *,
            compute_types_allowed: typing.Optional[typing.Sequence[builtins.str]] = None,
            maximum_builds_allowed: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''Specifies restrictions for the batch build.

            :param compute_types_allowed: An array of strings that specify the compute types that are allowed for the batch build. See `Build environment compute types <https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-compute-types.html>`_ in the *AWS CodeBuild User Guide* for these values.
            :param maximum_builds_allowed: Specifies the maximum number of builds allowed.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-batchrestrictions.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                batch_restrictions_property = codebuild.CfnProject.BatchRestrictionsProperty(
                    compute_types_allowed=["computeTypesAllowed"],
                    maximum_builds_allowed=123
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__eb6bc6e2fab27920e1a924cd2cf8893f0c2978c2cf77f98d7fcde7351ebb7342)
                check_type(argname="argument compute_types_allowed", value=compute_types_allowed, expected_type=type_hints["compute_types_allowed"])
                check_type(argname="argument maximum_builds_allowed", value=maximum_builds_allowed, expected_type=type_hints["maximum_builds_allowed"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if compute_types_allowed is not None:
                self._values["compute_types_allowed"] = compute_types_allowed
            if maximum_builds_allowed is not None:
                self._values["maximum_builds_allowed"] = maximum_builds_allowed

        @builtins.property
        def compute_types_allowed(self) -> typing.Optional[typing.List[builtins.str]]:
            '''An array of strings that specify the compute types that are allowed for the batch build.

            See `Build environment compute types <https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-compute-types.html>`_ in the *AWS CodeBuild User Guide* for these values.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-batchrestrictions.html#cfn-codebuild-project-batchrestrictions-computetypesallowed
            '''
            result = self._values.get("compute_types_allowed")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def maximum_builds_allowed(self) -> typing.Optional[jsii.Number]:
            '''Specifies the maximum number of builds allowed.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-batchrestrictions.html#cfn-codebuild-project-batchrestrictions-maximumbuildsallowed
            '''
            result = self._values.get("maximum_builds_allowed")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BatchRestrictionsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.BuildStatusConfigProperty",
        jsii_struct_bases=[],
        name_mapping={"context": "context", "target_url": "targetUrl"},
    )
    class BuildStatusConfigProperty:
        def __init__(
            self,
            *,
            context: typing.Optional[builtins.str] = None,
            target_url: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Contains information that defines how the AWS CodeBuild build project reports the build status to the source provider.

            :param context: Specifies the context of the build status CodeBuild sends to the source provider. The usage of this parameter depends on the source provider. - **Bitbucket** - This parameter is used for the ``name`` parameter in the Bitbucket commit status. For more information, see `build <https://docs.aws.amazon.com/https://developer.atlassian.com/bitbucket/api/2/reference/resource/repositories/%7Bworkspace%7D/%7Brepo_slug%7D/commit/%7Bnode%7D/statuses/build>`_ in the Bitbucket API documentation. - **GitHub/GitHub Enterprise Server** - This parameter is used for the ``context`` parameter in the GitHub commit status. For more information, see `Create a commit status <https://docs.aws.amazon.com/https://developer.github.com/v3/repos/statuses/#create-a-commit-status>`_ in the GitHub developer guide.
            :param target_url: Specifies the target url of the build status CodeBuild sends to the source provider. The usage of this parameter depends on the source provider. - **Bitbucket** - This parameter is used for the ``url`` parameter in the Bitbucket commit status. For more information, see `build <https://docs.aws.amazon.com/https://developer.atlassian.com/bitbucket/api/2/reference/resource/repositories/%7Bworkspace%7D/%7Brepo_slug%7D/commit/%7Bnode%7D/statuses/build>`_ in the Bitbucket API documentation. - **GitHub/GitHub Enterprise Server** - This parameter is used for the ``target_url`` parameter in the GitHub commit status. For more information, see `Create a commit status <https://docs.aws.amazon.com/https://developer.github.com/v3/repos/statuses/#create-a-commit-status>`_ in the GitHub developer guide.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-buildstatusconfig.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                build_status_config_property = codebuild.CfnProject.BuildStatusConfigProperty(
                    context="context",
                    target_url="targetUrl"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__aba374d9d8bf98b487019c75e76750090f342d19b7c9ca16aca58d2d3d7d0fe7)
                check_type(argname="argument context", value=context, expected_type=type_hints["context"])
                check_type(argname="argument target_url", value=target_url, expected_type=type_hints["target_url"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if context is not None:
                self._values["context"] = context
            if target_url is not None:
                self._values["target_url"] = target_url

        @builtins.property
        def context(self) -> typing.Optional[builtins.str]:
            '''Specifies the context of the build status CodeBuild sends to the source provider.

            The usage of this parameter depends on the source provider.

            - **Bitbucket** - This parameter is used for the ``name`` parameter in the Bitbucket commit status. For more information, see `build <https://docs.aws.amazon.com/https://developer.atlassian.com/bitbucket/api/2/reference/resource/repositories/%7Bworkspace%7D/%7Brepo_slug%7D/commit/%7Bnode%7D/statuses/build>`_ in the Bitbucket API documentation.
            - **GitHub/GitHub Enterprise Server** - This parameter is used for the ``context`` parameter in the GitHub commit status. For more information, see `Create a commit status <https://docs.aws.amazon.com/https://developer.github.com/v3/repos/statuses/#create-a-commit-status>`_ in the GitHub developer guide.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-buildstatusconfig.html#cfn-codebuild-project-buildstatusconfig-context
            '''
            result = self._values.get("context")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def target_url(self) -> typing.Optional[builtins.str]:
            '''Specifies the target url of the build status CodeBuild sends to the source provider.

            The usage of this parameter depends on the source provider.

            - **Bitbucket** - This parameter is used for the ``url`` parameter in the Bitbucket commit status. For more information, see `build <https://docs.aws.amazon.com/https://developer.atlassian.com/bitbucket/api/2/reference/resource/repositories/%7Bworkspace%7D/%7Brepo_slug%7D/commit/%7Bnode%7D/statuses/build>`_ in the Bitbucket API documentation.
            - **GitHub/GitHub Enterprise Server** - This parameter is used for the ``target_url`` parameter in the GitHub commit status. For more information, see `Create a commit status <https://docs.aws.amazon.com/https://developer.github.com/v3/repos/statuses/#create-a-commit-status>`_ in the GitHub developer guide.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-buildstatusconfig.html#cfn-codebuild-project-buildstatusconfig-targeturl
            '''
            result = self._values.get("target_url")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BuildStatusConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.CloudWatchLogsConfigProperty",
        jsii_struct_bases=[],
        name_mapping={
            "status": "status",
            "group_name": "groupName",
            "stream_name": "streamName",
        },
    )
    class CloudWatchLogsConfigProperty:
        def __init__(
            self,
            *,
            status: builtins.str,
            group_name: typing.Optional[builtins.str] = None,
            stream_name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''``CloudWatchLogs`` is a property of the `AWS CodeBuild Project LogsConfig <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-logsconfig.html>`_ property type that specifies settings for CloudWatch logs generated by an AWS CodeBuild build.

            :param status: The current status of the logs in CloudWatch Logs for a build project. Valid values are:. - ``ENABLED`` : CloudWatch Logs are enabled for this build project. - ``DISABLED`` : CloudWatch Logs are not enabled for this build project.
            :param group_name: The group name of the logs in CloudWatch Logs. For more information, see `Working with Log Groups and Log Streams <https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Working-with-log-groups-and-streams.html>`_ .
            :param stream_name: The prefix of the stream name of the CloudWatch Logs. For more information, see `Working with Log Groups and Log Streams <https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Working-with-log-groups-and-streams.html>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-cloudwatchlogsconfig.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                cloud_watch_logs_config_property = codebuild.CfnProject.CloudWatchLogsConfigProperty(
                    status="status",
                
                    # the properties below are optional
                    group_name="groupName",
                    stream_name="streamName"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__9fd7e79cf3768d0f7405de2c01fb064f7342370a61620313a099220750e1df2c)
                check_type(argname="argument status", value=status, expected_type=type_hints["status"])
                check_type(argname="argument group_name", value=group_name, expected_type=type_hints["group_name"])
                check_type(argname="argument stream_name", value=stream_name, expected_type=type_hints["stream_name"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "status": status,
            }
            if group_name is not None:
                self._values["group_name"] = group_name
            if stream_name is not None:
                self._values["stream_name"] = stream_name

        @builtins.property
        def status(self) -> builtins.str:
            '''The current status of the logs in CloudWatch Logs for a build project. Valid values are:.

            - ``ENABLED`` : CloudWatch Logs are enabled for this build project.
            - ``DISABLED`` : CloudWatch Logs are not enabled for this build project.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-cloudwatchlogsconfig.html#cfn-codebuild-project-cloudwatchlogsconfig-status
            '''
            result = self._values.get("status")
            assert result is not None, "Required property 'status' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def group_name(self) -> typing.Optional[builtins.str]:
            '''The group name of the logs in CloudWatch Logs.

            For more information, see `Working with Log Groups and Log Streams <https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Working-with-log-groups-and-streams.html>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-cloudwatchlogsconfig.html#cfn-codebuild-project-cloudwatchlogsconfig-groupname
            '''
            result = self._values.get("group_name")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def stream_name(self) -> typing.Optional[builtins.str]:
            '''The prefix of the stream name of the CloudWatch Logs.

            For more information, see `Working with Log Groups and Log Streams <https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Working-with-log-groups-and-streams.html>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-cloudwatchlogsconfig.html#cfn-codebuild-project-cloudwatchlogsconfig-streamname
            '''
            result = self._values.get("stream_name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CloudWatchLogsConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.EnvironmentProperty",
        jsii_struct_bases=[],
        name_mapping={
            "compute_type": "computeType",
            "image": "image",
            "type": "type",
            "certificate": "certificate",
            "environment_variables": "environmentVariables",
            "image_pull_credentials_type": "imagePullCredentialsType",
            "privileged_mode": "privilegedMode",
            "registry_credential": "registryCredential",
        },
    )
    class EnvironmentProperty:
        def __init__(
            self,
            *,
            compute_type: builtins.str,
            image: builtins.str,
            type: builtins.str,
            certificate: typing.Optional[builtins.str] = None,
            environment_variables: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[typing.Union["CfnProject.EnvironmentVariableProperty", typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]]]] = None,
            image_pull_credentials_type: typing.Optional[builtins.str] = None,
            privileged_mode: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            registry_credential: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnProject.RegistryCredentialProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''``Environment`` is a property of the `AWS::CodeBuild::Project <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html>`_ resource that specifies the environment for an AWS CodeBuild project.

            :param compute_type: The type of compute environment. This determines the number of CPU cores and memory the build environment uses. Available values include: - ``BUILD_GENERAL1_SMALL`` : Use up to 3 GB memory and 2 vCPUs for builds. - ``BUILD_GENERAL1_MEDIUM`` : Use up to 7 GB memory and 4 vCPUs for builds. - ``BUILD_GENERAL1_LARGE`` : Use up to 15 GB memory and 8 vCPUs for builds. For more information, see `Build Environment Compute Types <https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-compute-types.html>`_ in the *AWS CodeBuild User Guide.*
            :param image: The image tag or image digest that identifies the Docker image to use for this build project. Use the following formats: - For an image tag: ``<registry>/<repository>:<tag>`` . For example, in the Docker repository that CodeBuild uses to manage its Docker images, this would be ``aws/codebuild/standard:4.0`` . - For an image digest: ``<registry>/<repository>@<digest>`` . For example, to specify an image with the digest "sha256:cbbf2f9a99b47fc460d422812b6a5adff7dfee951d8fa2e4a98caa0382cfbdbf," use ``<registry>/<repository>@sha256:cbbf2f9a99b47fc460d422812b6a5adff7dfee951d8fa2e4a98caa0382cfbdbf`` . For more information, see `Docker images provided by CodeBuild <https://docs.aws.amazon.com//codebuild/latest/userguide/build-env-ref-available.html>`_ in the *AWS CodeBuild user guide* .
            :param type: The type of build environment to use for related builds. - The environment type ``ARM_CONTAINER`` is available only in regions US East (N. Virginia), US East (Ohio), US West (Oregon), EU (Ireland), Asia Pacific (Mumbai), Asia Pacific (Tokyo), Asia Pacific (Sydney), and EU (Frankfurt). - The environment type ``LINUX_CONTAINER`` with compute type ``build.general1.2xlarge`` is available only in regions US East (N. Virginia), US East (Ohio), US West (Oregon), Canada (Central), EU (Ireland), EU (London), EU (Frankfurt), Asia Pacific (Tokyo), Asia Pacific (Seoul), Asia Pacific (Singapore), Asia Pacific (Sydney), China (Beijing), and China (Ningxia). - The environment type ``LINUX_GPU_CONTAINER`` is available only in regions US East (N. Virginia), US East (Ohio), US West (Oregon), Canada (Central), EU (Ireland), EU (London), EU (Frankfurt), Asia Pacific (Tokyo), Asia Pacific (Seoul), Asia Pacific (Singapore), Asia Pacific (Sydney) , China (Beijing), and China (Ningxia). - The environment types ``WINDOWS_CONTAINER`` and ``WINDOWS_SERVER_2019_CONTAINER`` are available only in regions US East (N. Virginia), US East (Ohio), US West (Oregon), and EU (Ireland). For more information, see `Build environment compute types <https://docs.aws.amazon.com//codebuild/latest/userguide/build-env-ref-compute-types.html>`_ in the *AWS CodeBuild user guide* .
            :param certificate: The ARN of the Amazon S3 bucket, path prefix, and object key that contains the PEM-encoded certificate for the build project. For more information, see `certificate <https://docs.aws.amazon.com/codebuild/latest/userguide/create-project-cli.html#cli.environment.certificate>`_ in the *AWS CodeBuild User Guide* .
            :param environment_variables: A set of environment variables to make available to builds for this build project.
            :param image_pull_credentials_type: The type of credentials AWS CodeBuild uses to pull images in your build. There are two valid values:. - ``CODEBUILD`` specifies that AWS CodeBuild uses its own credentials. This requires that you modify your ECR repository policy to trust AWS CodeBuild service principal. - ``SERVICE_ROLE`` specifies that AWS CodeBuild uses your build project's service role. When you use a cross-account or private registry image, you must use SERVICE_ROLE credentials. When you use an AWS CodeBuild curated image, you must use CODEBUILD credentials.
            :param privileged_mode: Enables running the Docker daemon inside a Docker container. Set to true only if the build project is used to build Docker images. Otherwise, a build that attempts to interact with the Docker daemon fails. The default setting is ``false`` . You can initialize the Docker daemon during the install phase of your build by adding one of the following sets of commands to the install phase of your buildspec file: If the operating system's base image is Ubuntu Linux: ``- nohup /usr/local/bin/dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2375 --storage-driver=overlay&`` ``- timeout 15 sh -c "until docker info; do echo .; sleep 1; done"`` If the operating system's base image is Alpine Linux and the previous command does not work, add the ``-t`` argument to ``timeout`` : ``- nohup /usr/local/bin/dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2375 --storage-driver=overlay&`` ``- timeout -t 15 sh -c "until docker info; do echo .; sleep 1; done"``
            :param registry_credential: ``RegistryCredential`` is a property of the `AWS::CodeBuild::Project Environment <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-environment>`_ property that specifies information about credentials that provide access to a private Docker registry. When this is set:. - ``imagePullCredentialsType`` must be set to ``SERVICE_ROLE`` . - images cannot be curated or an Amazon ECR image.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                environment_property = codebuild.CfnProject.EnvironmentProperty(
                    compute_type="computeType",
                    image="image",
                    type="type",
                
                    # the properties below are optional
                    certificate="certificate",
                    environment_variables=[codebuild.CfnProject.EnvironmentVariableProperty(
                        name="name",
                        value="value",
                
                        # the properties below are optional
                        type="type"
                    )],
                    image_pull_credentials_type="imagePullCredentialsType",
                    privileged_mode=False,
                    registry_credential=codebuild.CfnProject.RegistryCredentialProperty(
                        credential="credential",
                        credential_provider="credentialProvider"
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__74b1cecf931c73947073d02ea5285c46abc4ae7354108c7a52b768ff49bb82b4)
                check_type(argname="argument compute_type", value=compute_type, expected_type=type_hints["compute_type"])
                check_type(argname="argument image", value=image, expected_type=type_hints["image"])
                check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
                check_type(argname="argument environment_variables", value=environment_variables, expected_type=type_hints["environment_variables"])
                check_type(argname="argument image_pull_credentials_type", value=image_pull_credentials_type, expected_type=type_hints["image_pull_credentials_type"])
                check_type(argname="argument privileged_mode", value=privileged_mode, expected_type=type_hints["privileged_mode"])
                check_type(argname="argument registry_credential", value=registry_credential, expected_type=type_hints["registry_credential"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "compute_type": compute_type,
                "image": image,
                "type": type,
            }
            if certificate is not None:
                self._values["certificate"] = certificate
            if environment_variables is not None:
                self._values["environment_variables"] = environment_variables
            if image_pull_credentials_type is not None:
                self._values["image_pull_credentials_type"] = image_pull_credentials_type
            if privileged_mode is not None:
                self._values["privileged_mode"] = privileged_mode
            if registry_credential is not None:
                self._values["registry_credential"] = registry_credential

        @builtins.property
        def compute_type(self) -> builtins.str:
            '''The type of compute environment.

            This determines the number of CPU cores and memory the build environment uses. Available values include:

            - ``BUILD_GENERAL1_SMALL`` : Use up to 3 GB memory and 2 vCPUs for builds.
            - ``BUILD_GENERAL1_MEDIUM`` : Use up to 7 GB memory and 4 vCPUs for builds.
            - ``BUILD_GENERAL1_LARGE`` : Use up to 15 GB memory and 8 vCPUs for builds.

            For more information, see `Build Environment Compute Types <https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-compute-types.html>`_ in the *AWS CodeBuild User Guide.*

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html#cfn-codebuild-project-environment-computetype
            '''
            result = self._values.get("compute_type")
            assert result is not None, "Required property 'compute_type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def image(self) -> builtins.str:
            '''The image tag or image digest that identifies the Docker image to use for this build project.

            Use the following formats:

            - For an image tag: ``<registry>/<repository>:<tag>`` . For example, in the Docker repository that CodeBuild uses to manage its Docker images, this would be ``aws/codebuild/standard:4.0`` .
            - For an image digest: ``<registry>/<repository>@<digest>`` . For example, to specify an image with the digest "sha256:cbbf2f9a99b47fc460d422812b6a5adff7dfee951d8fa2e4a98caa0382cfbdbf," use ``<registry>/<repository>@sha256:cbbf2f9a99b47fc460d422812b6a5adff7dfee951d8fa2e4a98caa0382cfbdbf`` .

            For more information, see `Docker images provided by CodeBuild <https://docs.aws.amazon.com//codebuild/latest/userguide/build-env-ref-available.html>`_ in the *AWS CodeBuild user guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html#cfn-codebuild-project-environment-image
            '''
            result = self._values.get("image")
            assert result is not None, "Required property 'image' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def type(self) -> builtins.str:
            '''The type of build environment to use for related builds.

            - The environment type ``ARM_CONTAINER`` is available only in regions US East (N. Virginia), US East (Ohio), US West (Oregon), EU (Ireland), Asia Pacific (Mumbai), Asia Pacific (Tokyo), Asia Pacific (Sydney), and EU (Frankfurt).
            - The environment type ``LINUX_CONTAINER`` with compute type ``build.general1.2xlarge`` is available only in regions US East (N. Virginia), US East (Ohio), US West (Oregon), Canada (Central), EU (Ireland), EU (London), EU (Frankfurt), Asia Pacific (Tokyo), Asia Pacific (Seoul), Asia Pacific (Singapore), Asia Pacific (Sydney), China (Beijing), and China (Ningxia).
            - The environment type ``LINUX_GPU_CONTAINER`` is available only in regions US East (N. Virginia), US East (Ohio), US West (Oregon), Canada (Central), EU (Ireland), EU (London), EU (Frankfurt), Asia Pacific (Tokyo), Asia Pacific (Seoul), Asia Pacific (Singapore), Asia Pacific (Sydney) , China (Beijing), and China (Ningxia).
            - The environment types ``WINDOWS_CONTAINER`` and ``WINDOWS_SERVER_2019_CONTAINER`` are available only in regions US East (N. Virginia), US East (Ohio), US West (Oregon), and EU (Ireland).

            For more information, see `Build environment compute types <https://docs.aws.amazon.com//codebuild/latest/userguide/build-env-ref-compute-types.html>`_ in the *AWS CodeBuild user guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html#cfn-codebuild-project-environment-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def certificate(self) -> typing.Optional[builtins.str]:
            '''The ARN of the Amazon S3 bucket, path prefix, and object key that contains the PEM-encoded certificate for the build project.

            For more information, see `certificate <https://docs.aws.amazon.com/codebuild/latest/userguide/create-project-cli.html#cli.environment.certificate>`_ in the *AWS CodeBuild User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html#cfn-codebuild-project-environment-certificate
            '''
            result = self._values.get("certificate")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def environment_variables(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union["CfnProject.EnvironmentVariableProperty", _aws_cdk_core_f4b25747.IResolvable]]]]:
            '''A set of environment variables to make available to builds for this build project.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html#cfn-codebuild-project-environment-environmentvariables
            '''
            result = self._values.get("environment_variables")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union["CfnProject.EnvironmentVariableProperty", _aws_cdk_core_f4b25747.IResolvable]]]], result)

        @builtins.property
        def image_pull_credentials_type(self) -> typing.Optional[builtins.str]:
            '''The type of credentials AWS CodeBuild uses to pull images in your build. There are two valid values:.

            - ``CODEBUILD`` specifies that AWS CodeBuild uses its own credentials. This requires that you modify your ECR repository policy to trust AWS CodeBuild service principal.
            - ``SERVICE_ROLE`` specifies that AWS CodeBuild uses your build project's service role.

            When you use a cross-account or private registry image, you must use SERVICE_ROLE credentials. When you use an AWS CodeBuild curated image, you must use CODEBUILD credentials.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html#cfn-codebuild-project-environment-imagepullcredentialstype
            '''
            result = self._values.get("image_pull_credentials_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def privileged_mode(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''Enables running the Docker daemon inside a Docker container.

            Set to true only if the build project is used to build Docker images. Otherwise, a build that attempts to interact with the Docker daemon fails. The default setting is ``false`` .

            You can initialize the Docker daemon during the install phase of your build by adding one of the following sets of commands to the install phase of your buildspec file:

            If the operating system's base image is Ubuntu Linux:

            ``- nohup /usr/local/bin/dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2375 --storage-driver=overlay&``

            ``- timeout 15 sh -c "until docker info; do echo .; sleep 1; done"``

            If the operating system's base image is Alpine Linux and the previous command does not work, add the ``-t`` argument to ``timeout`` :

            ``- nohup /usr/local/bin/dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2375 --storage-driver=overlay&``

            ``- timeout -t 15 sh -c "until docker info; do echo .; sleep 1; done"``

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html#cfn-codebuild-project-environment-privilegedmode
            '''
            result = self._values.get("privileged_mode")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def registry_credential(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.RegistryCredentialProperty"]]:
            '''``RegistryCredential`` is a property of the `AWS::CodeBuild::Project Environment <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-environment>`_ property that specifies information about credentials that provide access to a private Docker registry. When this is set:.

            - ``imagePullCredentialsType`` must be set to ``SERVICE_ROLE`` .
            - images cannot be curated or an Amazon ECR image.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html#cfn-codebuild-project-environment-registrycredential
            '''
            result = self._values.get("registry_credential")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.RegistryCredentialProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EnvironmentProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.EnvironmentVariableProperty",
        jsii_struct_bases=[],
        name_mapping={"name": "name", "value": "value", "type": "type"},
    )
    class EnvironmentVariableProperty:
        def __init__(
            self,
            *,
            name: builtins.str,
            value: builtins.str,
            type: typing.Optional[builtins.str] = None,
        ) -> None:
            '''``EnvironmentVariable`` is a property of the `AWS CodeBuild Project Environment <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html>`_ property type that specifies the name and value of an environment variable for an AWS CodeBuild project environment. When you use the environment to run a build, these variables are available for your builds to use. ``EnvironmentVariable`` contains a list of ``EnvironmentVariable`` property types.

            :param name: The name or key of the environment variable.
            :param value: The value of the environment variable. .. epigraph:: We strongly discourage the use of ``PLAINTEXT`` environment variables to store sensitive values, especially AWS secret key IDs and secret access keys. ``PLAINTEXT`` environment variables can be displayed in plain text using the AWS CodeBuild console and the AWS CLI . For sensitive values, we recommend you use an environment variable of type ``PARAMETER_STORE`` or ``SECRETS_MANAGER`` .
            :param type: The type of environment variable. Valid values include:. - ``PARAMETER_STORE`` : An environment variable stored in Systems Manager Parameter Store. For environment variables of this type, specify the name of the parameter as the ``value`` of the EnvironmentVariable. The parameter value will be substituted for the name at runtime. You can also define Parameter Store environment variables in the buildspec. To learn how to do so, see `env/parameter-store <https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec.env.parameter-store>`_ in the *AWS CodeBuild User Guide* . - ``PLAINTEXT`` : An environment variable in plain text format. This is the default value. - ``SECRETS_MANAGER`` : An environment variable stored in AWS Secrets Manager . For environment variables of this type, specify the name of the secret as the ``value`` of the EnvironmentVariable. The secret value will be substituted for the name at runtime. You can also define AWS Secrets Manager environment variables in the buildspec. To learn how to do so, see `env/secrets-manager <https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec.env.secrets-manager>`_ in the *AWS CodeBuild User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environmentvariable.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                environment_variable_property = codebuild.CfnProject.EnvironmentVariableProperty(
                    name="name",
                    value="value",
                
                    # the properties below are optional
                    type="type"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__78adc2a5842507505507c044dbbbad64350cc33d0b9f8e004113856c465d61bd)
                check_type(argname="argument name", value=name, expected_type=type_hints["name"])
                check_type(argname="argument value", value=value, expected_type=type_hints["value"])
                check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "name": name,
                "value": value,
            }
            if type is not None:
                self._values["type"] = type

        @builtins.property
        def name(self) -> builtins.str:
            '''The name or key of the environment variable.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environmentvariable.html#cfn-codebuild-project-environmentvariable-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def value(self) -> builtins.str:
            '''The value of the environment variable.

            .. epigraph::

               We strongly discourage the use of ``PLAINTEXT`` environment variables to store sensitive values, especially AWS secret key IDs and secret access keys. ``PLAINTEXT`` environment variables can be displayed in plain text using the AWS CodeBuild console and the AWS CLI . For sensitive values, we recommend you use an environment variable of type ``PARAMETER_STORE`` or ``SECRETS_MANAGER`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environmentvariable.html#cfn-codebuild-project-environmentvariable-value
            '''
            result = self._values.get("value")
            assert result is not None, "Required property 'value' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def type(self) -> typing.Optional[builtins.str]:
            '''The type of environment variable. Valid values include:.

            - ``PARAMETER_STORE`` : An environment variable stored in Systems Manager Parameter Store. For environment variables of this type, specify the name of the parameter as the ``value`` of the EnvironmentVariable. The parameter value will be substituted for the name at runtime. You can also define Parameter Store environment variables in the buildspec. To learn how to do so, see `env/parameter-store <https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec.env.parameter-store>`_ in the *AWS CodeBuild User Guide* .
            - ``PLAINTEXT`` : An environment variable in plain text format. This is the default value.
            - ``SECRETS_MANAGER`` : An environment variable stored in AWS Secrets Manager . For environment variables of this type, specify the name of the secret as the ``value`` of the EnvironmentVariable. The secret value will be substituted for the name at runtime. You can also define AWS Secrets Manager environment variables in the buildspec. To learn how to do so, see `env/secrets-manager <https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec.env.secrets-manager>`_ in the *AWS CodeBuild User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environmentvariable.html#cfn-codebuild-project-environmentvariable-type
            '''
            result = self._values.get("type")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EnvironmentVariableProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.GitSubmodulesConfigProperty",
        jsii_struct_bases=[],
        name_mapping={"fetch_submodules": "fetchSubmodules"},
    )
    class GitSubmodulesConfigProperty:
        def __init__(
            self,
            *,
            fetch_submodules: typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable],
        ) -> None:
            '''``GitSubmodulesConfig`` is a property of the `AWS CodeBuild Project Source <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html>`_ property type that specifies information about the Git submodules configuration for the build project.

            :param fetch_submodules: Set to true to fetch Git submodules for your AWS CodeBuild build project.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-gitsubmodulesconfig.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                git_submodules_config_property = codebuild.CfnProject.GitSubmodulesConfigProperty(
                    fetch_submodules=False
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__bd05bd3055ec6faa05880a0d7033d621a0c338ae45a954c15d541c78a4ff24c4)
                check_type(argname="argument fetch_submodules", value=fetch_submodules, expected_type=type_hints["fetch_submodules"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "fetch_submodules": fetch_submodules,
            }

        @builtins.property
        def fetch_submodules(
            self,
        ) -> typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]:
            '''Set to true to fetch Git submodules for your AWS CodeBuild build project.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-gitsubmodulesconfig.html#cfn-codebuild-project-gitsubmodulesconfig-fetchsubmodules
            '''
            result = self._values.get("fetch_submodules")
            assert result is not None, "Required property 'fetch_submodules' is missing"
            return typing.cast(typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "GitSubmodulesConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.LogsConfigProperty",
        jsii_struct_bases=[],
        name_mapping={"cloud_watch_logs": "cloudWatchLogs", "s3_logs": "s3Logs"},
    )
    class LogsConfigProperty:
        def __init__(
            self,
            *,
            cloud_watch_logs: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnProject.CloudWatchLogsConfigProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            s3_logs: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnProject.S3LogsConfigProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''``LogsConfig`` is a property of the `AWS CodeBuild Project <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html>`_ resource that specifies information about logs for a build project. These can be logs in Amazon CloudWatch Logs, built in a specified S3 bucket, or both.

            :param cloud_watch_logs: Information about CloudWatch Logs for a build project. CloudWatch Logs are enabled by default.
            :param s3_logs: Information about logs built to an S3 bucket for a build project. S3 logs are not enabled by default.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-logsconfig.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                logs_config_property = codebuild.CfnProject.LogsConfigProperty(
                    cloud_watch_logs=codebuild.CfnProject.CloudWatchLogsConfigProperty(
                        status="status",
                
                        # the properties below are optional
                        group_name="groupName",
                        stream_name="streamName"
                    ),
                    s3_logs=codebuild.CfnProject.S3LogsConfigProperty(
                        status="status",
                
                        # the properties below are optional
                        encryption_disabled=False,
                        location="location"
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__8326159c8f6edcf21cc27de730ec3f1b5533fcb658ccafa35c028a6500952352)
                check_type(argname="argument cloud_watch_logs", value=cloud_watch_logs, expected_type=type_hints["cloud_watch_logs"])
                check_type(argname="argument s3_logs", value=s3_logs, expected_type=type_hints["s3_logs"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if cloud_watch_logs is not None:
                self._values["cloud_watch_logs"] = cloud_watch_logs
            if s3_logs is not None:
                self._values["s3_logs"] = s3_logs

        @builtins.property
        def cloud_watch_logs(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.CloudWatchLogsConfigProperty"]]:
            '''Information about CloudWatch Logs for a build project.

            CloudWatch Logs are enabled by default.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-logsconfig.html#cfn-codebuild-project-logsconfig-cloudwatchlogs
            '''
            result = self._values.get("cloud_watch_logs")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.CloudWatchLogsConfigProperty"]], result)

        @builtins.property
        def s3_logs(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.S3LogsConfigProperty"]]:
            '''Information about logs built to an S3 bucket for a build project.

            S3 logs are not enabled by default.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-logsconfig.html#cfn-codebuild-project-logsconfig-s3logs
            '''
            result = self._values.get("s3_logs")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.S3LogsConfigProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LogsConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.ProjectBuildBatchConfigProperty",
        jsii_struct_bases=[],
        name_mapping={
            "batch_report_mode": "batchReportMode",
            "combine_artifacts": "combineArtifacts",
            "restrictions": "restrictions",
            "service_role": "serviceRole",
            "timeout_in_mins": "timeoutInMins",
        },
    )
    class ProjectBuildBatchConfigProperty:
        def __init__(
            self,
            *,
            batch_report_mode: typing.Optional[builtins.str] = None,
            combine_artifacts: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            restrictions: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnProject.BatchRestrictionsProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            service_role: typing.Optional[builtins.str] = None,
            timeout_in_mins: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''Contains configuration information about a batch build project.

            :param batch_report_mode: Specifies how build status reports are sent to the source provider for the batch build. This property is only used when the source provider for your project is Bitbucket, GitHub, or GitHub Enterprise, and your project is configured to report build statuses to the source provider. - **REPORT_AGGREGATED_BATCH** - (Default) Aggregate all of the build statuses into a single status report. - **REPORT_INDIVIDUAL_BUILDS** - Send a separate status report for each individual build.
            :param combine_artifacts: Specifies if the build artifacts for the batch build should be combined into a single artifact location.
            :param restrictions: A ``BatchRestrictions`` object that specifies the restrictions for the batch build.
            :param service_role: Specifies the service role ARN for the batch build project.
            :param timeout_in_mins: Specifies the maximum amount of time, in minutes, that the batch build must be completed in.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectbuildbatchconfig.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                project_build_batch_config_property = codebuild.CfnProject.ProjectBuildBatchConfigProperty(
                    batch_report_mode="batchReportMode",
                    combine_artifacts=False,
                    restrictions=codebuild.CfnProject.BatchRestrictionsProperty(
                        compute_types_allowed=["computeTypesAllowed"],
                        maximum_builds_allowed=123
                    ),
                    service_role="serviceRole",
                    timeout_in_mins=123
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__7c619576ee7a19a6070bc5aa172a4f5c592e233f1feaa921d79dca337ff3a3ab)
                check_type(argname="argument batch_report_mode", value=batch_report_mode, expected_type=type_hints["batch_report_mode"])
                check_type(argname="argument combine_artifacts", value=combine_artifacts, expected_type=type_hints["combine_artifacts"])
                check_type(argname="argument restrictions", value=restrictions, expected_type=type_hints["restrictions"])
                check_type(argname="argument service_role", value=service_role, expected_type=type_hints["service_role"])
                check_type(argname="argument timeout_in_mins", value=timeout_in_mins, expected_type=type_hints["timeout_in_mins"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if batch_report_mode is not None:
                self._values["batch_report_mode"] = batch_report_mode
            if combine_artifacts is not None:
                self._values["combine_artifacts"] = combine_artifacts
            if restrictions is not None:
                self._values["restrictions"] = restrictions
            if service_role is not None:
                self._values["service_role"] = service_role
            if timeout_in_mins is not None:
                self._values["timeout_in_mins"] = timeout_in_mins

        @builtins.property
        def batch_report_mode(self) -> typing.Optional[builtins.str]:
            '''Specifies how build status reports are sent to the source provider for the batch build.

            This property is only used when the source provider for your project is Bitbucket, GitHub, or GitHub Enterprise, and your project is configured to report build statuses to the source provider.

            - **REPORT_AGGREGATED_BATCH** - (Default) Aggregate all of the build statuses into a single status report.
            - **REPORT_INDIVIDUAL_BUILDS** - Send a separate status report for each individual build.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectbuildbatchconfig.html#cfn-codebuild-project-projectbuildbatchconfig-batchreportmode
            '''
            result = self._values.get("batch_report_mode")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def combine_artifacts(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''Specifies if the build artifacts for the batch build should be combined into a single artifact location.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectbuildbatchconfig.html#cfn-codebuild-project-projectbuildbatchconfig-combineartifacts
            '''
            result = self._values.get("combine_artifacts")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def restrictions(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.BatchRestrictionsProperty"]]:
            '''A ``BatchRestrictions`` object that specifies the restrictions for the batch build.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectbuildbatchconfig.html#cfn-codebuild-project-projectbuildbatchconfig-restrictions
            '''
            result = self._values.get("restrictions")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.BatchRestrictionsProperty"]], result)

        @builtins.property
        def service_role(self) -> typing.Optional[builtins.str]:
            '''Specifies the service role ARN for the batch build project.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectbuildbatchconfig.html#cfn-codebuild-project-projectbuildbatchconfig-servicerole
            '''
            result = self._values.get("service_role")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def timeout_in_mins(self) -> typing.Optional[jsii.Number]:
            '''Specifies the maximum amount of time, in minutes, that the batch build must be completed in.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectbuildbatchconfig.html#cfn-codebuild-project-projectbuildbatchconfig-timeoutinmins
            '''
            result = self._values.get("timeout_in_mins")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ProjectBuildBatchConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.ProjectCacheProperty",
        jsii_struct_bases=[],
        name_mapping={"type": "type", "location": "location", "modes": "modes"},
    )
    class ProjectCacheProperty:
        def __init__(
            self,
            *,
            type: builtins.str,
            location: typing.Optional[builtins.str] = None,
            modes: typing.Optional[typing.Sequence[builtins.str]] = None,
        ) -> None:
            '''``ProjectCache`` is a property of the `AWS CodeBuild Project <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html>`_ resource that specifies information about the cache for the build project. If ``ProjectCache`` is not specified, then both of its properties default to ``NO_CACHE`` .

            :param type: The type of cache used by the build project. Valid values include:. - ``NO_CACHE`` : The build project does not use any cache. - ``S3`` : The build project reads and writes from and to S3. - ``LOCAL`` : The build project stores a cache locally on a build host that is only available to that build host.
            :param location: Information about the cache location:. - ``NO_CACHE`` or ``LOCAL`` : This value is ignored. - ``S3`` : This is the S3 bucket name/prefix.
            :param modes: An array of strings that specify the local cache modes. You can use one or more local cache modes at the same time. This is only used for ``LOCAL`` cache types. Possible values are: - **LOCAL_SOURCE_CACHE** - Caches Git metadata for primary and secondary sources. After the cache is created, subsequent builds pull only the change between commits. This mode is a good choice for projects with a clean working directory and a source that is a large Git repository. If you choose this option and your project does not use a Git repository (GitHub, GitHub Enterprise, or Bitbucket), the option is ignored. - **LOCAL_DOCKER_LAYER_CACHE** - Caches existing Docker layers. This mode is a good choice for projects that build or pull large Docker images. It can prevent the performance issues caused by pulling large Docker images down from the network. .. epigraph:: - You can use a Docker layer cache in the Linux environment only. - The ``privileged`` flag must be set so that your project has the required Docker permissions. - You should consider the security implications before you use a Docker layer cache. - **LOCAL_CUSTOM_CACHE** - Caches directories you specify in the buildspec file. This mode is a good choice if your build scenario is not suited to one of the other three local cache modes. If you use a custom cache: - Only directories can be specified for caching. You cannot specify individual files. - Symlinks are used to reference cached directories. - Cached directories are linked to your build before it downloads its project sources. Cached items are overridden if a source item has the same name. Directories are specified using cache paths in the buildspec file.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectcache.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                project_cache_property = codebuild.CfnProject.ProjectCacheProperty(
                    type="type",
                
                    # the properties below are optional
                    location="location",
                    modes=["modes"]
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__7c61638f2d20614d1db79464bf9ef41460a29113654eba2391645ea83cab8d90)
                check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                check_type(argname="argument location", value=location, expected_type=type_hints["location"])
                check_type(argname="argument modes", value=modes, expected_type=type_hints["modes"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "type": type,
            }
            if location is not None:
                self._values["location"] = location
            if modes is not None:
                self._values["modes"] = modes

        @builtins.property
        def type(self) -> builtins.str:
            '''The type of cache used by the build project. Valid values include:.

            - ``NO_CACHE`` : The build project does not use any cache.
            - ``S3`` : The build project reads and writes from and to S3.
            - ``LOCAL`` : The build project stores a cache locally on a build host that is only available to that build host.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectcache.html#cfn-codebuild-project-projectcache-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def location(self) -> typing.Optional[builtins.str]:
            '''Information about the cache location:.

            - ``NO_CACHE`` or ``LOCAL`` : This value is ignored.
            - ``S3`` : This is the S3 bucket name/prefix.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectcache.html#cfn-codebuild-project-projectcache-location
            '''
            result = self._values.get("location")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def modes(self) -> typing.Optional[typing.List[builtins.str]]:
            '''An array of strings that specify the local cache modes.

            You can use one or more local cache modes at the same time. This is only used for ``LOCAL`` cache types.

            Possible values are:

            - **LOCAL_SOURCE_CACHE** - Caches Git metadata for primary and secondary sources. After the cache is created, subsequent builds pull only the change between commits. This mode is a good choice for projects with a clean working directory and a source that is a large Git repository. If you choose this option and your project does not use a Git repository (GitHub, GitHub Enterprise, or Bitbucket), the option is ignored.
            - **LOCAL_DOCKER_LAYER_CACHE** - Caches existing Docker layers. This mode is a good choice for projects that build or pull large Docker images. It can prevent the performance issues caused by pulling large Docker images down from the network.

            .. epigraph::

               - You can use a Docker layer cache in the Linux environment only.
               - The ``privileged`` flag must be set so that your project has the required Docker permissions.
               - You should consider the security implications before you use a Docker layer cache.

            - **LOCAL_CUSTOM_CACHE** - Caches directories you specify in the buildspec file. This mode is a good choice if your build scenario is not suited to one of the other three local cache modes. If you use a custom cache:
            - Only directories can be specified for caching. You cannot specify individual files.
            - Symlinks are used to reference cached directories.
            - Cached directories are linked to your build before it downloads its project sources. Cached items are overridden if a source item has the same name. Directories are specified using cache paths in the buildspec file.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectcache.html#cfn-codebuild-project-projectcache-modes
            '''
            result = self._values.get("modes")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ProjectCacheProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.ProjectFileSystemLocationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "identifier": "identifier",
            "location": "location",
            "mount_point": "mountPoint",
            "type": "type",
            "mount_options": "mountOptions",
        },
    )
    class ProjectFileSystemLocationProperty:
        def __init__(
            self,
            *,
            identifier: builtins.str,
            location: builtins.str,
            mount_point: builtins.str,
            type: builtins.str,
            mount_options: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Information about a file system created by Amazon Elastic File System (EFS).

            For more information, see `What Is Amazon Elastic File System? <https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html>`_

            :param identifier: The name used to access a file system created by Amazon EFS. CodeBuild creates an environment variable by appending the ``identifier`` in all capital letters to ``CODEBUILD_`` . For example, if you specify ``my_efs`` for ``identifier`` , a new environment variable is create named ``CODEBUILD_MY_EFS`` . The ``identifier`` is used to mount your file system.
            :param location: A string that specifies the location of the file system created by Amazon EFS. Its format is ``efs-dns-name:/directory-path`` . You can find the DNS name of file system when you view it in the Amazon EFS console. The directory path is a path to a directory in the file system that CodeBuild mounts. For example, if the DNS name of a file system is ``fs-abcd1234.efs.us-west-2.amazonaws.com`` , and its mount directory is ``my-efs-mount-directory`` , then the ``location`` is ``fs-abcd1234.efs.us-west-2.amazonaws.com:/my-efs-mount-directory`` . The directory path in the format ``efs-dns-name:/directory-path`` is optional. If you do not specify a directory path, the location is only the DNS name and CodeBuild mounts the entire file system.
            :param mount_point: The location in the container where you mount the file system.
            :param type: The type of the file system. The one supported type is ``EFS`` .
            :param mount_options: The mount options for a file system created by Amazon EFS. The default mount options used by CodeBuild are ``nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2`` . For more information, see `Recommended NFS Mount Options <https://docs.aws.amazon.com/efs/latest/ug/mounting-fs-nfs-mount-settings.html>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectfilesystemlocation.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                project_file_system_location_property = codebuild.CfnProject.ProjectFileSystemLocationProperty(
                    identifier="identifier",
                    location="location",
                    mount_point="mountPoint",
                    type="type",
                
                    # the properties below are optional
                    mount_options="mountOptions"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__0b0643ca64cba71d2feb9c367b59efd7d5be0d0a3a0176d31da1b5dfb88637c1)
                check_type(argname="argument identifier", value=identifier, expected_type=type_hints["identifier"])
                check_type(argname="argument location", value=location, expected_type=type_hints["location"])
                check_type(argname="argument mount_point", value=mount_point, expected_type=type_hints["mount_point"])
                check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                check_type(argname="argument mount_options", value=mount_options, expected_type=type_hints["mount_options"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "identifier": identifier,
                "location": location,
                "mount_point": mount_point,
                "type": type,
            }
            if mount_options is not None:
                self._values["mount_options"] = mount_options

        @builtins.property
        def identifier(self) -> builtins.str:
            '''The name used to access a file system created by Amazon EFS.

            CodeBuild creates an environment variable by appending the ``identifier`` in all capital letters to ``CODEBUILD_`` . For example, if you specify ``my_efs`` for ``identifier`` , a new environment variable is create named ``CODEBUILD_MY_EFS`` .

            The ``identifier`` is used to mount your file system.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectfilesystemlocation.html#cfn-codebuild-project-projectfilesystemlocation-identifier
            '''
            result = self._values.get("identifier")
            assert result is not None, "Required property 'identifier' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def location(self) -> builtins.str:
            '''A string that specifies the location of the file system created by Amazon EFS.

            Its format is ``efs-dns-name:/directory-path`` . You can find the DNS name of file system when you view it in the Amazon EFS console. The directory path is a path to a directory in the file system that CodeBuild mounts. For example, if the DNS name of a file system is ``fs-abcd1234.efs.us-west-2.amazonaws.com`` , and its mount directory is ``my-efs-mount-directory`` , then the ``location`` is ``fs-abcd1234.efs.us-west-2.amazonaws.com:/my-efs-mount-directory`` .

            The directory path in the format ``efs-dns-name:/directory-path`` is optional. If you do not specify a directory path, the location is only the DNS name and CodeBuild mounts the entire file system.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectfilesystemlocation.html#cfn-codebuild-project-projectfilesystemlocation-location
            '''
            result = self._values.get("location")
            assert result is not None, "Required property 'location' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def mount_point(self) -> builtins.str:
            '''The location in the container where you mount the file system.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectfilesystemlocation.html#cfn-codebuild-project-projectfilesystemlocation-mountpoint
            '''
            result = self._values.get("mount_point")
            assert result is not None, "Required property 'mount_point' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def type(self) -> builtins.str:
            '''The type of the file system.

            The one supported type is ``EFS`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectfilesystemlocation.html#cfn-codebuild-project-projectfilesystemlocation-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def mount_options(self) -> typing.Optional[builtins.str]:
            '''The mount options for a file system created by Amazon EFS.

            The default mount options used by CodeBuild are ``nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2`` . For more information, see `Recommended NFS Mount Options <https://docs.aws.amazon.com/efs/latest/ug/mounting-fs-nfs-mount-settings.html>`_ .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectfilesystemlocation.html#cfn-codebuild-project-projectfilesystemlocation-mountoptions
            '''
            result = self._values.get("mount_options")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ProjectFileSystemLocationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.ProjectSourceVersionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "source_identifier": "sourceIdentifier",
            "source_version": "sourceVersion",
        },
    )
    class ProjectSourceVersionProperty:
        def __init__(
            self,
            *,
            source_identifier: builtins.str,
            source_version: typing.Optional[builtins.str] = None,
        ) -> None:
            '''A source identifier and its corresponding version.

            :param source_identifier: An identifier for a source in the build project. The identifier can only contain alphanumeric characters and underscores, and must be less than 128 characters in length.
            :param source_version: The source version for the corresponding source identifier. If specified, must be one of:. - For CodeCommit: the commit ID, branch, or Git tag to use. - For GitHub: the commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build. If a pull request ID is specified, it must use the format ``pr/pull-request-ID`` (for example, ``pr/25`` ). If a branch name is specified, the branch's HEAD commit ID is used. If not specified, the default branch's HEAD commit ID is used. - For Bitbucket: the commit ID, branch name, or tag name that corresponds to the version of the source code you want to build. If a branch name is specified, the branch's HEAD commit ID is used. If not specified, the default branch's HEAD commit ID is used. - For Amazon S3: the version ID of the object that represents the build input ZIP file to use. For more information, see `Source Version Sample with CodeBuild <https://docs.aws.amazon.com/codebuild/latest/userguide/sample-source-version.html>`_ in the *AWS CodeBuild User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectsourceversion.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                project_source_version_property = codebuild.CfnProject.ProjectSourceVersionProperty(
                    source_identifier="sourceIdentifier",
                
                    # the properties below are optional
                    source_version="sourceVersion"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__1c4b5711714ac53def1f540346df3f3e1c18c70b9b0e49c763d5721d6679079f)
                check_type(argname="argument source_identifier", value=source_identifier, expected_type=type_hints["source_identifier"])
                check_type(argname="argument source_version", value=source_version, expected_type=type_hints["source_version"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "source_identifier": source_identifier,
            }
            if source_version is not None:
                self._values["source_version"] = source_version

        @builtins.property
        def source_identifier(self) -> builtins.str:
            '''An identifier for a source in the build project.

            The identifier can only contain alphanumeric characters and underscores, and must be less than 128 characters in length.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectsourceversion.html#cfn-codebuild-project-projectsourceversion-sourceidentifier
            '''
            result = self._values.get("source_identifier")
            assert result is not None, "Required property 'source_identifier' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def source_version(self) -> typing.Optional[builtins.str]:
            '''The source version for the corresponding source identifier. If specified, must be one of:.

            - For CodeCommit: the commit ID, branch, or Git tag to use.
            - For GitHub: the commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build. If a pull request ID is specified, it must use the format ``pr/pull-request-ID`` (for example, ``pr/25`` ). If a branch name is specified, the branch's HEAD commit ID is used. If not specified, the default branch's HEAD commit ID is used.
            - For Bitbucket: the commit ID, branch name, or tag name that corresponds to the version of the source code you want to build. If a branch name is specified, the branch's HEAD commit ID is used. If not specified, the default branch's HEAD commit ID is used.
            - For Amazon S3: the version ID of the object that represents the build input ZIP file to use.

            For more information, see `Source Version Sample with CodeBuild <https://docs.aws.amazon.com/codebuild/latest/userguide/sample-source-version.html>`_ in the *AWS CodeBuild User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectsourceversion.html#cfn-codebuild-project-projectsourceversion-sourceversion
            '''
            result = self._values.get("source_version")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ProjectSourceVersionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.ProjectTriggersProperty",
        jsii_struct_bases=[],
        name_mapping={
            "build_type": "buildType",
            "filter_groups": "filterGroups",
            "webhook": "webhook",
        },
    )
    class ProjectTriggersProperty:
        def __init__(
            self,
            *,
            build_type: typing.Optional[builtins.str] = None,
            filter_groups: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[typing.Union["CfnProject.WebhookFilterProperty", typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]]]]]] = None,
            webhook: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
        ) -> None:
            '''``ProjectTriggers`` is a property of the `AWS CodeBuild Project <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html>`_ resource that specifies webhooks that trigger an AWS CodeBuild build.

            .. epigraph::

               The Webhook feature isn't available in AWS CloudFormation for GitHub Enterprise projects. Use the AWS CLI or AWS CodeBuild console to create the webhook.

            :param build_type: Specifies the type of build this webhook will trigger. Allowed values are:. - **BUILD** - A single build - **BUILD_BATCH** - A batch build
            :param filter_groups: A list of lists of ``WebhookFilter`` objects used to determine which webhook events are triggered. At least one ``WebhookFilter`` in the array must specify ``EVENT`` as its type.
            :param webhook: Specifies whether or not to begin automatically rebuilding the source code every time a code change is pushed to the repository.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projecttriggers.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                project_triggers_property = codebuild.CfnProject.ProjectTriggersProperty(
                    build_type="buildType",
                    filter_groups=[[codebuild.CfnProject.WebhookFilterProperty(
                        pattern="pattern",
                        type="type",
                
                        # the properties below are optional
                        exclude_matched_pattern=False
                    )]],
                    webhook=False
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__3ad8a90a68b1dc84c36b685076efc5bcdeb9160cec8408f43aa9f5565253b4f5)
                check_type(argname="argument build_type", value=build_type, expected_type=type_hints["build_type"])
                check_type(argname="argument filter_groups", value=filter_groups, expected_type=type_hints["filter_groups"])
                check_type(argname="argument webhook", value=webhook, expected_type=type_hints["webhook"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if build_type is not None:
                self._values["build_type"] = build_type
            if filter_groups is not None:
                self._values["filter_groups"] = filter_groups
            if webhook is not None:
                self._values["webhook"] = webhook

        @builtins.property
        def build_type(self) -> typing.Optional[builtins.str]:
            '''Specifies the type of build this webhook will trigger. Allowed values are:.

            - **BUILD** - A single build
            - **BUILD_BATCH** - A batch build

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projecttriggers.html#cfn-codebuild-project-projecttriggers-buildtype
            '''
            result = self._values.get("build_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def filter_groups(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union["CfnProject.WebhookFilterProperty", _aws_cdk_core_f4b25747.IResolvable]]]]]]:
            '''A list of lists of ``WebhookFilter`` objects used to determine which webhook events are triggered.

            At least one ``WebhookFilter`` in the array must specify ``EVENT`` as its type.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projecttriggers.html#cfn-codebuild-project-projecttriggers-filtergroups
            '''
            result = self._values.get("filter_groups")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union["CfnProject.WebhookFilterProperty", _aws_cdk_core_f4b25747.IResolvable]]]]]], result)

        @builtins.property
        def webhook(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''Specifies whether or not to begin automatically rebuilding the source code every time a code change is pushed to the repository.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projecttriggers.html#cfn-codebuild-project-projecttriggers-webhook
            '''
            result = self._values.get("webhook")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ProjectTriggersProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.RegistryCredentialProperty",
        jsii_struct_bases=[],
        name_mapping={
            "credential": "credential",
            "credential_provider": "credentialProvider",
        },
    )
    class RegistryCredentialProperty:
        def __init__(
            self,
            *,
            credential: builtins.str,
            credential_provider: builtins.str,
        ) -> None:
            '''``RegistryCredential`` is a property of the `AWS CodeBuild Project Environment <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-environment.html>`_ property type that specifies information about credentials that provide access to a private Docker registry. When this is set:.

            - ``imagePullCredentialsType`` must be set to ``SERVICE_ROLE`` .
            - images cannot be curated or an Amazon ECR image.

            For more information, see `Private Registry with AWS Secrets Manager Sample for AWS CodeBuild <https://docs.aws.amazon.com/codebuild/latest/userguide/sample-private-registry.html>`_ .

            :param credential: The Amazon Resource Name (ARN) or name of credentials created using AWS Secrets Manager . .. epigraph:: The ``credential`` can use the name of the credentials only if they exist in your current AWS Region .
            :param credential_provider: The service that created the credentials to access a private Docker registry. The valid value, SECRETS_MANAGER, is for AWS Secrets Manager .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-registrycredential.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                registry_credential_property = codebuild.CfnProject.RegistryCredentialProperty(
                    credential="credential",
                    credential_provider="credentialProvider"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__2e3873672c4ca3ac39380390083959dc0f4e59c73ea4775c80131875df1a2e2b)
                check_type(argname="argument credential", value=credential, expected_type=type_hints["credential"])
                check_type(argname="argument credential_provider", value=credential_provider, expected_type=type_hints["credential_provider"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "credential": credential,
                "credential_provider": credential_provider,
            }

        @builtins.property
        def credential(self) -> builtins.str:
            '''The Amazon Resource Name (ARN) or name of credentials created using AWS Secrets Manager .

            .. epigraph::

               The ``credential`` can use the name of the credentials only if they exist in your current AWS Region .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-registrycredential.html#cfn-codebuild-project-registrycredential-credential
            '''
            result = self._values.get("credential")
            assert result is not None, "Required property 'credential' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def credential_provider(self) -> builtins.str:
            '''The service that created the credentials to access a private Docker registry.

            The valid value, SECRETS_MANAGER, is for AWS Secrets Manager .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-registrycredential.html#cfn-codebuild-project-registrycredential-credentialprovider
            '''
            result = self._values.get("credential_provider")
            assert result is not None, "Required property 'credential_provider' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RegistryCredentialProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.S3LogsConfigProperty",
        jsii_struct_bases=[],
        name_mapping={
            "status": "status",
            "encryption_disabled": "encryptionDisabled",
            "location": "location",
        },
    )
    class S3LogsConfigProperty:
        def __init__(
            self,
            *,
            status: builtins.str,
            encryption_disabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            location: typing.Optional[builtins.str] = None,
        ) -> None:
            '''``S3Logs`` is a property of the `AWS CodeBuild Project LogsConfig <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-logsconfig.html>`_ property type that specifies settings for logs generated by an AWS CodeBuild build in an S3 bucket.

            :param status: The current status of the S3 build logs. Valid values are:. - ``ENABLED`` : S3 build logs are enabled for this build project. - ``DISABLED`` : S3 build logs are not enabled for this build project.
            :param encryption_disabled: Set to true if you do not want your S3 build log output encrypted. By default S3 build logs are encrypted.
            :param location: The ARN of an S3 bucket and the path prefix for S3 logs. If your Amazon S3 bucket name is ``my-bucket`` , and your path prefix is ``build-log`` , then acceptable formats are ``my-bucket/build-log`` or ``arn:aws:s3:::my-bucket/build-log`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-s3logsconfig.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                s3_logs_config_property = codebuild.CfnProject.S3LogsConfigProperty(
                    status="status",
                
                    # the properties below are optional
                    encryption_disabled=False,
                    location="location"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__6e624819cc8ed37b9008cc37e7670a6acca35181a3d3889b35cafcc78aa53974)
                check_type(argname="argument status", value=status, expected_type=type_hints["status"])
                check_type(argname="argument encryption_disabled", value=encryption_disabled, expected_type=type_hints["encryption_disabled"])
                check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "status": status,
            }
            if encryption_disabled is not None:
                self._values["encryption_disabled"] = encryption_disabled
            if location is not None:
                self._values["location"] = location

        @builtins.property
        def status(self) -> builtins.str:
            '''The current status of the S3 build logs. Valid values are:.

            - ``ENABLED`` : S3 build logs are enabled for this build project.
            - ``DISABLED`` : S3 build logs are not enabled for this build project.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-s3logsconfig.html#cfn-codebuild-project-s3logsconfig-status
            '''
            result = self._values.get("status")
            assert result is not None, "Required property 'status' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def encryption_disabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''Set to true if you do not want your S3 build log output encrypted.

            By default S3 build logs are encrypted.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-s3logsconfig.html#cfn-codebuild-project-s3logsconfig-encryptiondisabled
            '''
            result = self._values.get("encryption_disabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def location(self) -> typing.Optional[builtins.str]:
            '''The ARN of an S3 bucket and the path prefix for S3 logs.

            If your Amazon S3 bucket name is ``my-bucket`` , and your path prefix is ``build-log`` , then acceptable formats are ``my-bucket/build-log`` or ``arn:aws:s3:::my-bucket/build-log`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-s3logsconfig.html#cfn-codebuild-project-s3logsconfig-location
            '''
            result = self._values.get("location")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3LogsConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.SourceAuthProperty",
        jsii_struct_bases=[],
        name_mapping={"type": "type", "resource": "resource"},
    )
    class SourceAuthProperty:
        def __init__(
            self,
            *,
            type: builtins.str,
            resource: typing.Optional[builtins.str] = None,
        ) -> None:
            '''``SourceAuth`` is a property of the `AWS CodeBuild Project Source <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html>`_ property type that specifies authorization settings for AWS CodeBuild to access the source code to be built.

            ``SourceAuth`` is for use by the CodeBuild console only. Do not get or set it directly.

            :param type: The authorization type to use. The only valid value is ``OAUTH`` , which represents the OAuth authorization type. .. epigraph:: This data type is used by the AWS CodeBuild console only.
            :param resource: The resource value that applies to the specified authorization type. .. epigraph:: This data type is used by the AWS CodeBuild console only.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-sourceauth.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                source_auth_property = codebuild.CfnProject.SourceAuthProperty(
                    type="type",
                
                    # the properties below are optional
                    resource="resource"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__34251d7daab872fadbffae6ce715d221b491ddf989c00300fc27041f4821e165)
                check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "type": type,
            }
            if resource is not None:
                self._values["resource"] = resource

        @builtins.property
        def type(self) -> builtins.str:
            '''The authorization type to use. The only valid value is ``OAUTH`` , which represents the OAuth authorization type.

            .. epigraph::

               This data type is used by the AWS CodeBuild console only.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-sourceauth.html#cfn-codebuild-project-sourceauth-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def resource(self) -> typing.Optional[builtins.str]:
            '''The resource value that applies to the specified authorization type.

            .. epigraph::

               This data type is used by the AWS CodeBuild console only.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-sourceauth.html#cfn-codebuild-project-sourceauth-resource
            '''
            result = self._values.get("resource")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SourceAuthProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.SourceProperty",
        jsii_struct_bases=[],
        name_mapping={
            "type": "type",
            "auth": "auth",
            "build_spec": "buildSpec",
            "build_status_config": "buildStatusConfig",
            "git_clone_depth": "gitCloneDepth",
            "git_submodules_config": "gitSubmodulesConfig",
            "insecure_ssl": "insecureSsl",
            "location": "location",
            "report_build_status": "reportBuildStatus",
            "source_identifier": "sourceIdentifier",
        },
    )
    class SourceProperty:
        def __init__(
            self,
            *,
            type: builtins.str,
            auth: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnProject.SourceAuthProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            build_spec: typing.Optional[builtins.str] = None,
            build_status_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnProject.BuildStatusConfigProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            git_clone_depth: typing.Optional[jsii.Number] = None,
            git_submodules_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnProject.GitSubmodulesConfigProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
            insecure_ssl: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            location: typing.Optional[builtins.str] = None,
            report_build_status: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            source_identifier: typing.Optional[builtins.str] = None,
        ) -> None:
            '''``Source`` is a property of the `AWS::CodeBuild::Project <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html>`_ resource that specifies the source code settings for the project, such as the source code's repository type and location.

            :param type: The type of repository that contains the source code to be built. Valid values include:. - ``BITBUCKET`` : The source code is in a Bitbucket repository. - ``CODECOMMIT`` : The source code is in an CodeCommit repository. - ``CODEPIPELINE`` : The source code settings are specified in the source action of a pipeline in CodePipeline. - ``GITHUB`` : The source code is in a GitHub or GitHub Enterprise Cloud repository. - ``GITHUB_ENTERPRISE`` : The source code is in a GitHub Enterprise Server repository. - ``NO_SOURCE`` : The project does not have input source code. - ``S3`` : The source code is in an Amazon S3 bucket.
            :param auth: Information about the authorization settings for AWS CodeBuild to access the source code to be built. This information is for the AWS CodeBuild console's use only. Your code should not get or set ``Auth`` directly.
            :param build_spec: The build specification for the project. If this value is not provided, then the source code must contain a buildspec file named ``buildspec.yml`` at the root level. If this value is provided, it can be either a single string containing the entire build specification, or the path to an alternate buildspec file relative to the value of the built-in environment variable ``CODEBUILD_SRC_DIR`` . The alternate buildspec file can have a name other than ``buildspec.yml`` , for example ``myspec.yml`` or ``build_spec_qa.yml`` or similar. For more information, see the `Build Spec Reference <https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec-ref-example>`_ in the *AWS CodeBuild User Guide* .
            :param build_status_config: Contains information that defines how the build project reports the build status to the source provider. This option is only used when the source provider is ``GITHUB`` , ``GITHUB_ENTERPRISE`` , or ``BITBUCKET`` .
            :param git_clone_depth: The depth of history to download. Minimum value is 0. If this value is 0, greater than 25, or not provided, then the full history is downloaded with each build project. If your source type is Amazon S3, this value is not supported.
            :param git_submodules_config: Information about the Git submodules configuration for the build project.
            :param insecure_ssl: This is used with GitHub Enterprise only. Set to true to ignore SSL warnings while connecting to your GitHub Enterprise project repository. The default value is ``false`` . ``InsecureSsl`` should be used for testing purposes only. It should not be used in a production environment.
            :param location: Information about the location of the source code to be built. Valid values include:. - For source code settings that are specified in the source action of a pipeline in CodePipeline, ``location`` should not be specified. If it is specified, CodePipeline ignores it. This is because CodePipeline uses the settings in a pipeline's source action instead of this value. - For source code in an CodeCommit repository, the HTTPS clone URL to the repository that contains the source code and the buildspec file (for example, ``https://git-codecommit.<region-ID>.amazonaws.com/v1/repos/<repo-name>`` ). - For source code in an Amazon S3 input bucket, one of the following. - The path to the ZIP file that contains the source code (for example, ``<bucket-name>/<path>/<object-name>.zip`` ). - The path to the folder that contains the source code (for example, ``<bucket-name>/<path-to-source-code>/<folder>/`` ). - For source code in a GitHub repository, the HTTPS clone URL to the repository that contains the source and the buildspec file. You must connect your AWS account to your GitHub account. Use the AWS CodeBuild console to start creating a build project. When you use the console to connect (or reconnect) with GitHub, on the GitHub *Authorize application* page, for *Organization access* , choose *Request access* next to each repository you want to allow AWS CodeBuild to have access to, and then choose *Authorize application* . (After you have connected to your GitHub account, you do not need to finish creating the build project. You can leave the AWS CodeBuild console.) To instruct AWS CodeBuild to use this connection, in the ``source`` object, set the ``auth`` object's ``type`` value to ``OAUTH`` . - For source code in a Bitbucket repository, the HTTPS clone URL to the repository that contains the source and the buildspec file. You must connect your AWS account to your Bitbucket account. Use the AWS CodeBuild console to start creating a build project. When you use the console to connect (or reconnect) with Bitbucket, on the Bitbucket *Confirm access to your account* page, choose *Grant access* . (After you have connected to your Bitbucket account, you do not need to finish creating the build project. You can leave the AWS CodeBuild console.) To instruct AWS CodeBuild to use this connection, in the ``source`` object, set the ``auth`` object's ``type`` value to ``OAUTH`` . If you specify ``CODEPIPELINE`` for the ``Type`` property, don't specify this property. For all of the other types, you must specify ``Location`` .
            :param report_build_status: Set to true to report the status of a build's start and finish to your source provider. This option is valid only when your source provider is GitHub, GitHub Enterprise, or Bitbucket. If this is set and you use a different source provider, an ``invalidInputException`` is thrown.
            :param source_identifier: An identifier for this project source. The identifier can only contain alphanumeric characters and underscores, and must be less than 128 characters in length.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                source_property = codebuild.CfnProject.SourceProperty(
                    type="type",
                
                    # the properties below are optional
                    auth=codebuild.CfnProject.SourceAuthProperty(
                        type="type",
                
                        # the properties below are optional
                        resource="resource"
                    ),
                    build_spec="buildSpec",
                    build_status_config=codebuild.CfnProject.BuildStatusConfigProperty(
                        context="context",
                        target_url="targetUrl"
                    ),
                    git_clone_depth=123,
                    git_submodules_config=codebuild.CfnProject.GitSubmodulesConfigProperty(
                        fetch_submodules=False
                    ),
                    insecure_ssl=False,
                    location="location",
                    report_build_status=False,
                    source_identifier="sourceIdentifier"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__6eb006c928c177466aa136afb4080043f5bc3e27df60ab5f84c91b7ca2908e70)
                check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                check_type(argname="argument auth", value=auth, expected_type=type_hints["auth"])
                check_type(argname="argument build_spec", value=build_spec, expected_type=type_hints["build_spec"])
                check_type(argname="argument build_status_config", value=build_status_config, expected_type=type_hints["build_status_config"])
                check_type(argname="argument git_clone_depth", value=git_clone_depth, expected_type=type_hints["git_clone_depth"])
                check_type(argname="argument git_submodules_config", value=git_submodules_config, expected_type=type_hints["git_submodules_config"])
                check_type(argname="argument insecure_ssl", value=insecure_ssl, expected_type=type_hints["insecure_ssl"])
                check_type(argname="argument location", value=location, expected_type=type_hints["location"])
                check_type(argname="argument report_build_status", value=report_build_status, expected_type=type_hints["report_build_status"])
                check_type(argname="argument source_identifier", value=source_identifier, expected_type=type_hints["source_identifier"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "type": type,
            }
            if auth is not None:
                self._values["auth"] = auth
            if build_spec is not None:
                self._values["build_spec"] = build_spec
            if build_status_config is not None:
                self._values["build_status_config"] = build_status_config
            if git_clone_depth is not None:
                self._values["git_clone_depth"] = git_clone_depth
            if git_submodules_config is not None:
                self._values["git_submodules_config"] = git_submodules_config
            if insecure_ssl is not None:
                self._values["insecure_ssl"] = insecure_ssl
            if location is not None:
                self._values["location"] = location
            if report_build_status is not None:
                self._values["report_build_status"] = report_build_status
            if source_identifier is not None:
                self._values["source_identifier"] = source_identifier

        @builtins.property
        def type(self) -> builtins.str:
            '''The type of repository that contains the source code to be built. Valid values include:.

            - ``BITBUCKET`` : The source code is in a Bitbucket repository.
            - ``CODECOMMIT`` : The source code is in an CodeCommit repository.
            - ``CODEPIPELINE`` : The source code settings are specified in the source action of a pipeline in CodePipeline.
            - ``GITHUB`` : The source code is in a GitHub or GitHub Enterprise Cloud repository.
            - ``GITHUB_ENTERPRISE`` : The source code is in a GitHub Enterprise Server repository.
            - ``NO_SOURCE`` : The project does not have input source code.
            - ``S3`` : The source code is in an Amazon S3 bucket.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def auth(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.SourceAuthProperty"]]:
            '''Information about the authorization settings for AWS CodeBuild to access the source code to be built.

            This information is for the AWS CodeBuild console's use only. Your code should not get or set ``Auth`` directly.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-auth
            '''
            result = self._values.get("auth")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.SourceAuthProperty"]], result)

        @builtins.property
        def build_spec(self) -> typing.Optional[builtins.str]:
            '''The build specification for the project.

            If this value is not provided, then the source code must contain a buildspec file named ``buildspec.yml`` at the root level. If this value is provided, it can be either a single string containing the entire build specification, or the path to an alternate buildspec file relative to the value of the built-in environment variable ``CODEBUILD_SRC_DIR`` . The alternate buildspec file can have a name other than ``buildspec.yml`` , for example ``myspec.yml`` or ``build_spec_qa.yml`` or similar. For more information, see the `Build Spec Reference <https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec-ref-example>`_ in the *AWS CodeBuild User Guide* .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-buildspec
            '''
            result = self._values.get("build_spec")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def build_status_config(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.BuildStatusConfigProperty"]]:
            '''Contains information that defines how the build project reports the build status to the source provider.

            This option is only used when the source provider is ``GITHUB`` , ``GITHUB_ENTERPRISE`` , or ``BITBUCKET`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-buildstatusconfig
            '''
            result = self._values.get("build_status_config")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.BuildStatusConfigProperty"]], result)

        @builtins.property
        def git_clone_depth(self) -> typing.Optional[jsii.Number]:
            '''The depth of history to download.

            Minimum value is 0. If this value is 0, greater than 25, or not provided, then the full history is downloaded with each build project. If your source type is Amazon S3, this value is not supported.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-gitclonedepth
            '''
            result = self._values.get("git_clone_depth")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def git_submodules_config(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.GitSubmodulesConfigProperty"]]:
            '''Information about the Git submodules configuration for the build project.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-gitsubmodulesconfig
            '''
            result = self._values.get("git_submodules_config")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnProject.GitSubmodulesConfigProperty"]], result)

        @builtins.property
        def insecure_ssl(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''This is used with GitHub Enterprise only.

            Set to true to ignore SSL warnings while connecting to your GitHub Enterprise project repository. The default value is ``false`` . ``InsecureSsl`` should be used for testing purposes only. It should not be used in a production environment.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-insecuressl
            '''
            result = self._values.get("insecure_ssl")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def location(self) -> typing.Optional[builtins.str]:
            '''Information about the location of the source code to be built. Valid values include:.

            - For source code settings that are specified in the source action of a pipeline in CodePipeline, ``location`` should not be specified. If it is specified, CodePipeline ignores it. This is because CodePipeline uses the settings in a pipeline's source action instead of this value.
            - For source code in an CodeCommit repository, the HTTPS clone URL to the repository that contains the source code and the buildspec file (for example, ``https://git-codecommit.<region-ID>.amazonaws.com/v1/repos/<repo-name>`` ).
            - For source code in an Amazon S3 input bucket, one of the following.
            - The path to the ZIP file that contains the source code (for example, ``<bucket-name>/<path>/<object-name>.zip`` ).
            - The path to the folder that contains the source code (for example, ``<bucket-name>/<path-to-source-code>/<folder>/`` ).
            - For source code in a GitHub repository, the HTTPS clone URL to the repository that contains the source and the buildspec file. You must connect your AWS account to your GitHub account. Use the AWS CodeBuild console to start creating a build project. When you use the console to connect (or reconnect) with GitHub, on the GitHub *Authorize application* page, for *Organization access* , choose *Request access* next to each repository you want to allow AWS CodeBuild to have access to, and then choose *Authorize application* . (After you have connected to your GitHub account, you do not need to finish creating the build project. You can leave the AWS CodeBuild console.) To instruct AWS CodeBuild to use this connection, in the ``source`` object, set the ``auth`` object's ``type`` value to ``OAUTH`` .
            - For source code in a Bitbucket repository, the HTTPS clone URL to the repository that contains the source and the buildspec file. You must connect your AWS account to your Bitbucket account. Use the AWS CodeBuild console to start creating a build project. When you use the console to connect (or reconnect) with Bitbucket, on the Bitbucket *Confirm access to your account* page, choose *Grant access* . (After you have connected to your Bitbucket account, you do not need to finish creating the build project. You can leave the AWS CodeBuild console.) To instruct AWS CodeBuild to use this connection, in the ``source`` object, set the ``auth`` object's ``type`` value to ``OAUTH`` .

            If you specify ``CODEPIPELINE`` for the ``Type`` property, don't specify this property. For all of the other types, you must specify ``Location`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-location
            '''
            result = self._values.get("location")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def report_build_status(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''Set to true to report the status of a build's start and finish to your source provider.

            This option is valid only when your source provider is GitHub, GitHub Enterprise, or Bitbucket. If this is set and you use a different source provider, an ``invalidInputException`` is thrown.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-reportbuildstatus
            '''
            result = self._values.get("report_build_status")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def source_identifier(self) -> typing.Optional[builtins.str]:
            '''An identifier for this project source.

            The identifier can only contain alphanumeric characters and underscores, and must be less than 128 characters in length.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-source.html#cfn-codebuild-project-source-sourceidentifier
            '''
            result = self._values.get("source_identifier")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SourceProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.VpcConfigProperty",
        jsii_struct_bases=[],
        name_mapping={
            "security_group_ids": "securityGroupIds",
            "subnets": "subnets",
            "vpc_id": "vpcId",
        },
    )
    class VpcConfigProperty:
        def __init__(
            self,
            *,
            security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
            subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
            vpc_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''``VpcConfig`` is a property of the `AWS::CodeBuild::Project <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html>`_ resource that enable AWS CodeBuild to access resources in an Amazon VPC. For more information, see `Use AWS CodeBuild with Amazon Virtual Private Cloud <https://docs.aws.amazon.com/codebuild/latest/userguide/vpc-support.html>`_ in the *AWS CodeBuild User Guide* .

            :param security_group_ids: A list of one or more security groups IDs in your Amazon VPC. The maximum count is 5.
            :param subnets: A list of one or more subnet IDs in your Amazon VPC. The maximum count is 16.
            :param vpc_id: The ID of the Amazon VPC.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-vpcconfig.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                vpc_config_property = codebuild.CfnProject.VpcConfigProperty(
                    security_group_ids=["securityGroupIds"],
                    subnets=["subnets"],
                    vpc_id="vpcId"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__78efb6e6bc8d525e926d65712ba9887513d80c53534cc5f4c6b66db61d3719a7)
                check_type(argname="argument security_group_ids", value=security_group_ids, expected_type=type_hints["security_group_ids"])
                check_type(argname="argument subnets", value=subnets, expected_type=type_hints["subnets"])
                check_type(argname="argument vpc_id", value=vpc_id, expected_type=type_hints["vpc_id"])
            self._values: typing.Dict[builtins.str, typing.Any] = {}
            if security_group_ids is not None:
                self._values["security_group_ids"] = security_group_ids
            if subnets is not None:
                self._values["subnets"] = subnets
            if vpc_id is not None:
                self._values["vpc_id"] = vpc_id

        @builtins.property
        def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
            '''A list of one or more security groups IDs in your Amazon VPC.

            The maximum count is 5.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-vpcconfig.html#cfn-codebuild-project-vpcconfig-securitygroupids
            '''
            result = self._values.get("security_group_ids")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def subnets(self) -> typing.Optional[typing.List[builtins.str]]:
            '''A list of one or more subnet IDs in your Amazon VPC.

            The maximum count is 16.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-vpcconfig.html#cfn-codebuild-project-vpcconfig-subnets
            '''
            result = self._values.get("subnets")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def vpc_id(self) -> typing.Optional[builtins.str]:
            '''The ID of the Amazon VPC.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-vpcconfig.html#cfn-codebuild-project-vpcconfig-vpcid
            '''
            result = self._values.get("vpc_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "VpcConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnProject.WebhookFilterProperty",
        jsii_struct_bases=[],
        name_mapping={
            "pattern": "pattern",
            "type": "type",
            "exclude_matched_pattern": "excludeMatchedPattern",
        },
    )
    class WebhookFilterProperty:
        def __init__(
            self,
            *,
            pattern: builtins.str,
            type: builtins.str,
            exclude_matched_pattern: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
        ) -> None:
            '''``WebhookFilter`` is a structure of the ``FilterGroups`` property on the `AWS CodeBuild Project ProjectTriggers <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projecttriggers.html>`_ property type that specifies which webhooks trigger an AWS CodeBuild build.

            .. epigraph::

               The Webhook feature isn't available in AWS CloudFormation for GitHub Enterprise projects. Use the AWS CLI or AWS CodeBuild console to create the webhook.

            :param pattern: For a ``WebHookFilter`` that uses ``EVENT`` type, a comma-separated string that specifies one or more events. For example, the webhook filter ``PUSH, PULL_REQUEST_CREATED, PULL_REQUEST_UPDATED`` allows all push, pull request created, and pull request updated events to trigger a build. For a ``WebHookFilter`` that uses any of the other filter types, a regular expression pattern. For example, a ``WebHookFilter`` that uses ``HEAD_REF`` for its ``type`` and the pattern ``^refs/heads/`` triggers a build when the head reference is a branch with a reference name ``refs/heads/branch-name`` .
            :param type: The type of webhook filter. There are six webhook filter types: ``EVENT`` , ``ACTOR_ACCOUNT_ID`` , ``HEAD_REF`` , ``BASE_REF`` , ``FILE_PATH`` , and ``COMMIT_MESSAGE`` . - **EVENT** - A webhook event triggers a build when the provided ``pattern`` matches one of five event types: ``PUSH`` , ``PULL_REQUEST_CREATED`` , ``PULL_REQUEST_UPDATED`` , ``PULL_REQUEST_REOPENED`` , and ``PULL_REQUEST_MERGED`` . The ``EVENT`` patterns are specified as a comma-separated string. For example, ``PUSH, PULL_REQUEST_CREATED, PULL_REQUEST_UPDATED`` filters all push, pull request created, and pull request updated events. .. epigraph:: The ``PULL_REQUEST_REOPENED`` works with GitHub and GitHub Enterprise only. - **ACTOR_ACCOUNT_ID** - A webhook event triggers a build when a GitHub, GitHub Enterprise, or Bitbucket account ID matches the regular expression ``pattern`` . - **HEAD_REF** - A webhook event triggers a build when the head reference matches the regular expression ``pattern`` . For example, ``refs/heads/branch-name`` and ``refs/tags/tag-name`` . Works with GitHub and GitHub Enterprise push, GitHub and GitHub Enterprise pull request, Bitbucket push, and Bitbucket pull request events. - **BASE_REF** - A webhook event triggers a build when the base reference matches the regular expression ``pattern`` . For example, ``refs/heads/branch-name`` . .. epigraph:: Works with pull request events only. - **FILE_PATH** - A webhook triggers a build when the path of a changed file matches the regular expression ``pattern`` . .. epigraph:: Works with GitHub and Bitbucket events push and pull requests events. Also works with GitHub Enterprise push events, but does not work with GitHub Enterprise pull request events. - **COMMIT_MESSAGE** - A webhook triggers a build when the head commit message matches the regular expression ``pattern`` . .. epigraph:: Works with GitHub and Bitbucket events push and pull requests events. Also works with GitHub Enterprise push events, but does not work with GitHub Enterprise pull request events.
            :param exclude_matched_pattern: Used to indicate that the ``pattern`` determines which webhook events do not trigger a build. If true, then a webhook event that does not match the ``pattern`` triggers a build. If false, then a webhook event that matches the ``pattern`` triggers a build.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-webhookfilter.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                webhook_filter_property = codebuild.CfnProject.WebhookFilterProperty(
                    pattern="pattern",
                    type="type",
                
                    # the properties below are optional
                    exclude_matched_pattern=False
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__15d77bcfb2086252b78d19fcc46382a83468906a07b160433db90c4cb7160ca9)
                check_type(argname="argument pattern", value=pattern, expected_type=type_hints["pattern"])
                check_type(argname="argument type", value=type, expected_type=type_hints["type"])
                check_type(argname="argument exclude_matched_pattern", value=exclude_matched_pattern, expected_type=type_hints["exclude_matched_pattern"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "pattern": pattern,
                "type": type,
            }
            if exclude_matched_pattern is not None:
                self._values["exclude_matched_pattern"] = exclude_matched_pattern

        @builtins.property
        def pattern(self) -> builtins.str:
            '''For a ``WebHookFilter`` that uses ``EVENT`` type, a comma-separated string that specifies one or more events.

            For example, the webhook filter ``PUSH, PULL_REQUEST_CREATED, PULL_REQUEST_UPDATED`` allows all push, pull request created, and pull request updated events to trigger a build.

            For a ``WebHookFilter`` that uses any of the other filter types, a regular expression pattern. For example, a ``WebHookFilter`` that uses ``HEAD_REF`` for its ``type`` and the pattern ``^refs/heads/`` triggers a build when the head reference is a branch with a reference name ``refs/heads/branch-name`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-webhookfilter.html#cfn-codebuild-project-webhookfilter-pattern
            '''
            result = self._values.get("pattern")
            assert result is not None, "Required property 'pattern' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def type(self) -> builtins.str:
            '''The type of webhook filter.

            There are six webhook filter types: ``EVENT`` , ``ACTOR_ACCOUNT_ID`` , ``HEAD_REF`` , ``BASE_REF`` , ``FILE_PATH`` , and ``COMMIT_MESSAGE`` .

            - **EVENT** - A webhook event triggers a build when the provided ``pattern`` matches one of five event types: ``PUSH`` , ``PULL_REQUEST_CREATED`` , ``PULL_REQUEST_UPDATED`` , ``PULL_REQUEST_REOPENED`` , and ``PULL_REQUEST_MERGED`` . The ``EVENT`` patterns are specified as a comma-separated string. For example, ``PUSH, PULL_REQUEST_CREATED, PULL_REQUEST_UPDATED`` filters all push, pull request created, and pull request updated events.

            .. epigraph::

               The ``PULL_REQUEST_REOPENED`` works with GitHub and GitHub Enterprise only.

            - **ACTOR_ACCOUNT_ID** - A webhook event triggers a build when a GitHub, GitHub Enterprise, or Bitbucket account ID matches the regular expression ``pattern`` .
            - **HEAD_REF** - A webhook event triggers a build when the head reference matches the regular expression ``pattern`` . For example, ``refs/heads/branch-name`` and ``refs/tags/tag-name`` .

            Works with GitHub and GitHub Enterprise push, GitHub and GitHub Enterprise pull request, Bitbucket push, and Bitbucket pull request events.

            - **BASE_REF** - A webhook event triggers a build when the base reference matches the regular expression ``pattern`` . For example, ``refs/heads/branch-name`` .

            .. epigraph::

               Works with pull request events only.

            - **FILE_PATH** - A webhook triggers a build when the path of a changed file matches the regular expression ``pattern`` .

            .. epigraph::

               Works with GitHub and Bitbucket events push and pull requests events. Also works with GitHub Enterprise push events, but does not work with GitHub Enterprise pull request events.

            - **COMMIT_MESSAGE** - A webhook triggers a build when the head commit message matches the regular expression ``pattern`` .

            .. epigraph::

               Works with GitHub and Bitbucket events push and pull requests events. Also works with GitHub Enterprise push events, but does not work with GitHub Enterprise pull request events.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-webhookfilter.html#cfn-codebuild-project-webhookfilter-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def exclude_matched_pattern(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''Used to indicate that the ``pattern`` determines which webhook events do not trigger a build.

            If true, then a webhook event that does not match the ``pattern`` triggers a build. If false, then a webhook event that matches the ``pattern`` triggers a build.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-webhookfilter.html#cfn-codebuild-project-webhookfilter-excludematchedpattern
            '''
            result = self._values.get("exclude_matched_pattern")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "WebhookFilterProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.CfnProjectProps",
    jsii_struct_bases=[],
    name_mapping={
        "artifacts": "artifacts",
        "environment": "environment",
        "service_role": "serviceRole",
        "source": "source",
        "badge_enabled": "badgeEnabled",
        "build_batch_config": "buildBatchConfig",
        "cache": "cache",
        "concurrent_build_limit": "concurrentBuildLimit",
        "description": "description",
        "encryption_key": "encryptionKey",
        "file_system_locations": "fileSystemLocations",
        "logs_config": "logsConfig",
        "name": "name",
        "queued_timeout_in_minutes": "queuedTimeoutInMinutes",
        "resource_access_role": "resourceAccessRole",
        "secondary_artifacts": "secondaryArtifacts",
        "secondary_sources": "secondarySources",
        "secondary_source_versions": "secondarySourceVersions",
        "source_version": "sourceVersion",
        "tags": "tags",
        "timeout_in_minutes": "timeoutInMinutes",
        "triggers": "triggers",
        "visibility": "visibility",
        "vpc_config": "vpcConfig",
    },
)
class CfnProjectProps:
    def __init__(
        self,
        *,
        artifacts: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ArtifactsProperty, typing.Dict[builtins.str, typing.Any]]],
        environment: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.EnvironmentProperty, typing.Dict[builtins.str, typing.Any]]],
        service_role: builtins.str,
        source: typing.Union[typing.Union[CfnProject.SourceProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable],
        badge_enabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
        build_batch_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ProjectBuildBatchConfigProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        cache: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ProjectCacheProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        concurrent_build_limit: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[builtins.str] = None,
        file_system_locations: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ProjectFileSystemLocationProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        logs_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.LogsConfigProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        name: typing.Optional[builtins.str] = None,
        queued_timeout_in_minutes: typing.Optional[jsii.Number] = None,
        resource_access_role: typing.Optional[builtins.str] = None,
        secondary_artifacts: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ArtifactsProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        secondary_sources: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[typing.Union[CfnProject.SourceProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]]]] = None,
        secondary_source_versions: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ProjectSourceVersionProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        source_version: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
        timeout_in_minutes: typing.Optional[jsii.Number] = None,
        triggers: typing.Optional[typing.Union[typing.Union[CfnProject.ProjectTriggersProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]] = None,
        visibility: typing.Optional[builtins.str] = None,
        vpc_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.VpcConfigProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for defining a ``CfnProject``.

        :param artifacts: ``Artifacts`` is a property of the `AWS::CodeBuild::Project <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html>`_ resource that specifies output settings for artifacts generated by an AWS CodeBuild build.
        :param environment: The build environment settings for the project, such as the environment type or the environment variables to use for the build environment.
        :param service_role: The ARN of the IAM role that enables AWS CodeBuild to interact with dependent AWS services on behalf of the AWS account.
        :param source: The source code settings for the project, such as the source code's repository type and location.
        :param badge_enabled: Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge. For more information, see `Build Badges Sample <https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-badges.html>`_ in the *AWS CodeBuild User Guide* . .. epigraph:: Including build badges with your project is currently not supported if the source type is CodePipeline. If you specify ``CODEPIPELINE`` for the ``Source`` property, do not specify the ``BadgeEnabled`` property.
        :param build_batch_config: A ``ProjectBuildBatchConfig`` object that defines the batch build options for the project.
        :param cache: Settings that AWS CodeBuild uses to store and reuse build dependencies.
        :param concurrent_build_limit: The maximum number of concurrent builds that are allowed for this project. New builds are only started if the current number of builds is less than or equal to this limit. If the current build count meets this limit, new builds are throttled and are not run.
        :param description: A description that makes the build project easy to identify.
        :param encryption_key: The AWS Key Management Service customer master key (CMK) to be used for encrypting the build output artifacts. .. epigraph:: You can use a cross-account KMS key to encrypt the build output artifacts if your service role has permission to that key. You can specify either the Amazon Resource Name (ARN) of the CMK or, if available, the CMK's alias (using the format ``alias/<alias-name>`` ). If you don't specify a value, CodeBuild uses the managed CMK for Amazon Simple Storage Service (Amazon S3).
        :param file_system_locations: An array of ``ProjectFileSystemLocation`` objects for a CodeBuild build project. A ``ProjectFileSystemLocation`` object specifies the ``identifier`` , ``location`` , ``mountOptions`` , ``mountPoint`` , and ``type`` of a file system created using Amazon Elastic File System.
        :param logs_config: Information about logs for the build project. A project can create logs in CloudWatch Logs, an S3 bucket, or both.
        :param name: The name of the build project. The name must be unique across all of the projects in your AWS account .
        :param queued_timeout_in_minutes: The number of minutes a build is allowed to be queued before it times out.
        :param resource_access_role: The ARN of the IAM role that enables CodeBuild to access the CloudWatch Logs and Amazon S3 artifacts for the project's builds.
        :param secondary_artifacts: A list of ``Artifacts`` objects. Each artifacts object specifies output settings that the project generates during a build.
        :param secondary_sources: An array of ``ProjectSource`` objects.
        :param secondary_source_versions: An array of ``ProjectSourceVersion`` objects. If ``secondarySourceVersions`` is specified at the build level, then they take over these ``secondarySourceVersions`` (at the project level).
        :param source_version: A version of the build input to be built for this project. If not specified, the latest version is used. If specified, it must be one of: - For CodeCommit: the commit ID, branch, or Git tag to use. - For GitHub: the commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build. If a pull request ID is specified, it must use the format ``pr/pull-request-ID`` (for example ``pr/25`` ). If a branch name is specified, the branch's HEAD commit ID is used. If not specified, the default branch's HEAD commit ID is used. - For Bitbucket: the commit ID, branch name, or tag name that corresponds to the version of the source code you want to build. If a branch name is specified, the branch's HEAD commit ID is used. If not specified, the default branch's HEAD commit ID is used. - For Amazon S3: the version ID of the object that represents the build input ZIP file to use. If ``sourceVersion`` is specified at the build level, then that version takes precedence over this ``sourceVersion`` (at the project level). For more information, see `Source Version Sample with CodeBuild <https://docs.aws.amazon.com/codebuild/latest/userguide/sample-source-version.html>`_ in the *AWS CodeBuild User Guide* .
        :param tags: An arbitrary set of tags (key-value pairs) for the AWS CodeBuild project. These tags are available for use by AWS services that support AWS CodeBuild build project tags.
        :param timeout_in_minutes: How long, in minutes, from 5 to 480 (8 hours), for AWS CodeBuild to wait before timing out any related build that did not get marked as completed. The default is 60 minutes.
        :param triggers: For an existing AWS CodeBuild build project that has its source code stored in a GitHub repository, enables AWS CodeBuild to begin automatically rebuilding the source code every time a code change is pushed to the repository.
        :param visibility: Specifies the visibility of the project's builds. Possible values are:. - **PUBLIC_READ** - The project builds are visible to the public. - **PRIVATE** - The project builds are not visible to the public.
        :param vpc_config: ``VpcConfig`` specifies settings that enable AWS CodeBuild to access resources in an Amazon VPC. For more information, see `Use AWS CodeBuild with Amazon Virtual Private Cloud <https://docs.aws.amazon.com/codebuild/latest/userguide/vpc-support.html>`_ in the *AWS CodeBuild User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            
            cfn_project_props = codebuild.CfnProjectProps(
                artifacts=codebuild.CfnProject.ArtifactsProperty(
                    type="type",
            
                    # the properties below are optional
                    artifact_identifier="artifactIdentifier",
                    encryption_disabled=False,
                    location="location",
                    name="name",
                    namespace_type="namespaceType",
                    override_artifact_name=False,
                    packaging="packaging",
                    path="path"
                ),
                environment=codebuild.CfnProject.EnvironmentProperty(
                    compute_type="computeType",
                    image="image",
                    type="type",
            
                    # the properties below are optional
                    certificate="certificate",
                    environment_variables=[codebuild.CfnProject.EnvironmentVariableProperty(
                        name="name",
                        value="value",
            
                        # the properties below are optional
                        type="type"
                    )],
                    image_pull_credentials_type="imagePullCredentialsType",
                    privileged_mode=False,
                    registry_credential=codebuild.CfnProject.RegistryCredentialProperty(
                        credential="credential",
                        credential_provider="credentialProvider"
                    )
                ),
                service_role="serviceRole",
                source=codebuild.CfnProject.SourceProperty(
                    type="type",
            
                    # the properties below are optional
                    auth=codebuild.CfnProject.SourceAuthProperty(
                        type="type",
            
                        # the properties below are optional
                        resource="resource"
                    ),
                    build_spec="buildSpec",
                    build_status_config=codebuild.CfnProject.BuildStatusConfigProperty(
                        context="context",
                        target_url="targetUrl"
                    ),
                    git_clone_depth=123,
                    git_submodules_config=codebuild.CfnProject.GitSubmodulesConfigProperty(
                        fetch_submodules=False
                    ),
                    insecure_ssl=False,
                    location="location",
                    report_build_status=False,
                    source_identifier="sourceIdentifier"
                ),
            
                # the properties below are optional
                badge_enabled=False,
                build_batch_config=codebuild.CfnProject.ProjectBuildBatchConfigProperty(
                    batch_report_mode="batchReportMode",
                    combine_artifacts=False,
                    restrictions=codebuild.CfnProject.BatchRestrictionsProperty(
                        compute_types_allowed=["computeTypesAllowed"],
                        maximum_builds_allowed=123
                    ),
                    service_role="serviceRole",
                    timeout_in_mins=123
                ),
                cache=codebuild.CfnProject.ProjectCacheProperty(
                    type="type",
            
                    # the properties below are optional
                    location="location",
                    modes=["modes"]
                ),
                concurrent_build_limit=123,
                description="description",
                encryption_key="encryptionKey",
                file_system_locations=[codebuild.CfnProject.ProjectFileSystemLocationProperty(
                    identifier="identifier",
                    location="location",
                    mount_point="mountPoint",
                    type="type",
            
                    # the properties below are optional
                    mount_options="mountOptions"
                )],
                logs_config=codebuild.CfnProject.LogsConfigProperty(
                    cloud_watch_logs=codebuild.CfnProject.CloudWatchLogsConfigProperty(
                        status="status",
            
                        # the properties below are optional
                        group_name="groupName",
                        stream_name="streamName"
                    ),
                    s3_logs=codebuild.CfnProject.S3LogsConfigProperty(
                        status="status",
            
                        # the properties below are optional
                        encryption_disabled=False,
                        location="location"
                    )
                ),
                name="name",
                queued_timeout_in_minutes=123,
                resource_access_role="resourceAccessRole",
                secondary_artifacts=[codebuild.CfnProject.ArtifactsProperty(
                    type="type",
            
                    # the properties below are optional
                    artifact_identifier="artifactIdentifier",
                    encryption_disabled=False,
                    location="location",
                    name="name",
                    namespace_type="namespaceType",
                    override_artifact_name=False,
                    packaging="packaging",
                    path="path"
                )],
                secondary_sources=[codebuild.CfnProject.SourceProperty(
                    type="type",
            
                    # the properties below are optional
                    auth=codebuild.CfnProject.SourceAuthProperty(
                        type="type",
            
                        # the properties below are optional
                        resource="resource"
                    ),
                    build_spec="buildSpec",
                    build_status_config=codebuild.CfnProject.BuildStatusConfigProperty(
                        context="context",
                        target_url="targetUrl"
                    ),
                    git_clone_depth=123,
                    git_submodules_config=codebuild.CfnProject.GitSubmodulesConfigProperty(
                        fetch_submodules=False
                    ),
                    insecure_ssl=False,
                    location="location",
                    report_build_status=False,
                    source_identifier="sourceIdentifier"
                )],
                secondary_source_versions=[codebuild.CfnProject.ProjectSourceVersionProperty(
                    source_identifier="sourceIdentifier",
            
                    # the properties below are optional
                    source_version="sourceVersion"
                )],
                source_version="sourceVersion",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                timeout_in_minutes=123,
                triggers=codebuild.CfnProject.ProjectTriggersProperty(
                    build_type="buildType",
                    filter_groups=[[codebuild.CfnProject.WebhookFilterProperty(
                        pattern="pattern",
                        type="type",
            
                        # the properties below are optional
                        exclude_matched_pattern=False
                    )]],
                    webhook=False
                ),
                visibility="visibility",
                vpc_config=codebuild.CfnProject.VpcConfigProperty(
                    security_group_ids=["securityGroupIds"],
                    subnets=["subnets"],
                    vpc_id="vpcId"
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d032495b1b8a5f0125f69a4d70521e0e7e99b76caf8db0f15d51589fdc99be4)
            check_type(argname="argument artifacts", value=artifacts, expected_type=type_hints["artifacts"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument service_role", value=service_role, expected_type=type_hints["service_role"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument badge_enabled", value=badge_enabled, expected_type=type_hints["badge_enabled"])
            check_type(argname="argument build_batch_config", value=build_batch_config, expected_type=type_hints["build_batch_config"])
            check_type(argname="argument cache", value=cache, expected_type=type_hints["cache"])
            check_type(argname="argument concurrent_build_limit", value=concurrent_build_limit, expected_type=type_hints["concurrent_build_limit"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument file_system_locations", value=file_system_locations, expected_type=type_hints["file_system_locations"])
            check_type(argname="argument logs_config", value=logs_config, expected_type=type_hints["logs_config"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument queued_timeout_in_minutes", value=queued_timeout_in_minutes, expected_type=type_hints["queued_timeout_in_minutes"])
            check_type(argname="argument resource_access_role", value=resource_access_role, expected_type=type_hints["resource_access_role"])
            check_type(argname="argument secondary_artifacts", value=secondary_artifacts, expected_type=type_hints["secondary_artifacts"])
            check_type(argname="argument secondary_sources", value=secondary_sources, expected_type=type_hints["secondary_sources"])
            check_type(argname="argument secondary_source_versions", value=secondary_source_versions, expected_type=type_hints["secondary_source_versions"])
            check_type(argname="argument source_version", value=source_version, expected_type=type_hints["source_version"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument timeout_in_minutes", value=timeout_in_minutes, expected_type=type_hints["timeout_in_minutes"])
            check_type(argname="argument triggers", value=triggers, expected_type=type_hints["triggers"])
            check_type(argname="argument visibility", value=visibility, expected_type=type_hints["visibility"])
            check_type(argname="argument vpc_config", value=vpc_config, expected_type=type_hints["vpc_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "artifacts": artifacts,
            "environment": environment,
            "service_role": service_role,
            "source": source,
        }
        if badge_enabled is not None:
            self._values["badge_enabled"] = badge_enabled
        if build_batch_config is not None:
            self._values["build_batch_config"] = build_batch_config
        if cache is not None:
            self._values["cache"] = cache
        if concurrent_build_limit is not None:
            self._values["concurrent_build_limit"] = concurrent_build_limit
        if description is not None:
            self._values["description"] = description
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if file_system_locations is not None:
            self._values["file_system_locations"] = file_system_locations
        if logs_config is not None:
            self._values["logs_config"] = logs_config
        if name is not None:
            self._values["name"] = name
        if queued_timeout_in_minutes is not None:
            self._values["queued_timeout_in_minutes"] = queued_timeout_in_minutes
        if resource_access_role is not None:
            self._values["resource_access_role"] = resource_access_role
        if secondary_artifacts is not None:
            self._values["secondary_artifacts"] = secondary_artifacts
        if secondary_sources is not None:
            self._values["secondary_sources"] = secondary_sources
        if secondary_source_versions is not None:
            self._values["secondary_source_versions"] = secondary_source_versions
        if source_version is not None:
            self._values["source_version"] = source_version
        if tags is not None:
            self._values["tags"] = tags
        if timeout_in_minutes is not None:
            self._values["timeout_in_minutes"] = timeout_in_minutes
        if triggers is not None:
            self._values["triggers"] = triggers
        if visibility is not None:
            self._values["visibility"] = visibility
        if vpc_config is not None:
            self._values["vpc_config"] = vpc_config

    @builtins.property
    def artifacts(
        self,
    ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ArtifactsProperty]:
        '''``Artifacts`` is a property of the `AWS::CodeBuild::Project <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html>`_ resource that specifies output settings for artifacts generated by an AWS CodeBuild build.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-artifacts
        '''
        result = self._values.get("artifacts")
        assert result is not None, "Required property 'artifacts' is missing"
        return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ArtifactsProperty], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.EnvironmentProperty]:
        '''The build environment settings for the project, such as the environment type or the environment variables to use for the build environment.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-environment
        '''
        result = self._values.get("environment")
        assert result is not None, "Required property 'environment' is missing"
        return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.EnvironmentProperty], result)

    @builtins.property
    def service_role(self) -> builtins.str:
        '''The ARN of the IAM role that enables AWS CodeBuild to interact with dependent AWS services on behalf of the AWS account.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-servicerole
        '''
        result = self._values.get("service_role")
        assert result is not None, "Required property 'service_role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source(
        self,
    ) -> typing.Union[CfnProject.SourceProperty, _aws_cdk_core_f4b25747.IResolvable]:
        '''The source code settings for the project, such as the source code's repository type and location.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-source
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(typing.Union[CfnProject.SourceProperty, _aws_cdk_core_f4b25747.IResolvable], result)

    @builtins.property
    def badge_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
        '''Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge.

        For more information, see `Build Badges Sample <https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-badges.html>`_ in the *AWS CodeBuild User Guide* .
        .. epigraph::

           Including build badges with your project is currently not supported if the source type is CodePipeline. If you specify ``CODEPIPELINE`` for the ``Source`` property, do not specify the ``BadgeEnabled`` property.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-badgeenabled
        '''
        result = self._values.get("badge_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

    @builtins.property
    def build_batch_config(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ProjectBuildBatchConfigProperty]]:
        '''A ``ProjectBuildBatchConfig`` object that defines the batch build options for the project.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-buildbatchconfig
        '''
        result = self._values.get("build_batch_config")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ProjectBuildBatchConfigProperty]], result)

    @builtins.property
    def cache(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ProjectCacheProperty]]:
        '''Settings that AWS CodeBuild uses to store and reuse build dependencies.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-cache
        '''
        result = self._values.get("cache")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ProjectCacheProperty]], result)

    @builtins.property
    def concurrent_build_limit(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of concurrent builds that are allowed for this project.

        New builds are only started if the current number of builds is less than or equal to this limit. If the current build count meets this limit, new builds are throttled and are not run.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-concurrentbuildlimit
        '''
        result = self._values.get("concurrent_build_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description that makes the build project easy to identify.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[builtins.str]:
        '''The AWS Key Management Service customer master key (CMK) to be used for encrypting the build output artifacts.

        .. epigraph::

           You can use a cross-account KMS key to encrypt the build output artifacts if your service role has permission to that key.

        You can specify either the Amazon Resource Name (ARN) of the CMK or, if available, the CMK's alias (using the format ``alias/<alias-name>`` ). If you don't specify a value, CodeBuild uses the managed CMK for Amazon Simple Storage Service (Amazon S3).

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-encryptionkey
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_system_locations(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ProjectFileSystemLocationProperty]]]]:
        '''An array of ``ProjectFileSystemLocation`` objects for a CodeBuild build project.

        A ``ProjectFileSystemLocation`` object specifies the ``identifier`` , ``location`` , ``mountOptions`` , ``mountPoint`` , and ``type`` of a file system created using Amazon Elastic File System.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-filesystemlocations
        '''
        result = self._values.get("file_system_locations")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ProjectFileSystemLocationProperty]]]], result)

    @builtins.property
    def logs_config(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.LogsConfigProperty]]:
        '''Information about logs for the build project.

        A project can create logs in CloudWatch Logs, an S3 bucket, or both.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-logsconfig
        '''
        result = self._values.get("logs_config")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.LogsConfigProperty]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the build project.

        The name must be unique across all of the projects in your AWS account .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queued_timeout_in_minutes(self) -> typing.Optional[jsii.Number]:
        '''The number of minutes a build is allowed to be queued before it times out.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-queuedtimeoutinminutes
        '''
        result = self._values.get("queued_timeout_in_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def resource_access_role(self) -> typing.Optional[builtins.str]:
        '''The ARN of the IAM role that enables CodeBuild to access the CloudWatch Logs and Amazon S3 artifacts for the project's builds.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-resourceaccessrole
        '''
        result = self._values.get("resource_access_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secondary_artifacts(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ArtifactsProperty]]]]:
        '''A list of ``Artifacts`` objects.

        Each artifacts object specifies output settings that the project generates during a build.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-secondaryartifacts
        '''
        result = self._values.get("secondary_artifacts")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ArtifactsProperty]]]], result)

    @builtins.property
    def secondary_sources(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[CfnProject.SourceProperty, _aws_cdk_core_f4b25747.IResolvable]]]]:
        '''An array of ``ProjectSource`` objects.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-secondarysources
        '''
        result = self._values.get("secondary_sources")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[CfnProject.SourceProperty, _aws_cdk_core_f4b25747.IResolvable]]]], result)

    @builtins.property
    def secondary_source_versions(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ProjectSourceVersionProperty]]]]:
        '''An array of ``ProjectSourceVersion`` objects.

        If ``secondarySourceVersions`` is specified at the build level, then they take over these ``secondarySourceVersions`` (at the project level).

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-secondarysourceversions
        '''
        result = self._values.get("secondary_source_versions")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ProjectSourceVersionProperty]]]], result)

    @builtins.property
    def source_version(self) -> typing.Optional[builtins.str]:
        '''A version of the build input to be built for this project.

        If not specified, the latest version is used. If specified, it must be one of:

        - For CodeCommit: the commit ID, branch, or Git tag to use.
        - For GitHub: the commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build. If a pull request ID is specified, it must use the format ``pr/pull-request-ID`` (for example ``pr/25`` ). If a branch name is specified, the branch's HEAD commit ID is used. If not specified, the default branch's HEAD commit ID is used.
        - For Bitbucket: the commit ID, branch name, or tag name that corresponds to the version of the source code you want to build. If a branch name is specified, the branch's HEAD commit ID is used. If not specified, the default branch's HEAD commit ID is used.
        - For Amazon S3: the version ID of the object that represents the build input ZIP file to use.

        If ``sourceVersion`` is specified at the build level, then that version takes precedence over this ``sourceVersion`` (at the project level).

        For more information, see `Source Version Sample with CodeBuild <https://docs.aws.amazon.com/codebuild/latest/userguide/sample-source-version.html>`_ in the *AWS CodeBuild User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-sourceversion
        '''
        result = self._values.get("source_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_core_f4b25747.CfnTag]]:
        '''An arbitrary set of tags (key-value pairs) for the AWS CodeBuild project.

        These tags are available for use by AWS services that support AWS CodeBuild build project tags.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_core_f4b25747.CfnTag]], result)

    @builtins.property
    def timeout_in_minutes(self) -> typing.Optional[jsii.Number]:
        '''How long, in minutes, from 5 to 480 (8 hours), for AWS CodeBuild to wait before timing out any related build that did not get marked as completed.

        The default is 60 minutes.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-timeoutinminutes
        '''
        result = self._values.get("timeout_in_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def triggers(
        self,
    ) -> typing.Optional[typing.Union[CfnProject.ProjectTriggersProperty, _aws_cdk_core_f4b25747.IResolvable]]:
        '''For an existing AWS CodeBuild build project that has its source code stored in a GitHub repository, enables AWS CodeBuild to begin automatically rebuilding the source code every time a code change is pushed to the repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-triggers
        '''
        result = self._values.get("triggers")
        return typing.cast(typing.Optional[typing.Union[CfnProject.ProjectTriggersProperty, _aws_cdk_core_f4b25747.IResolvable]], result)

    @builtins.property
    def visibility(self) -> typing.Optional[builtins.str]:
        '''Specifies the visibility of the project's builds. Possible values are:.

        - **PUBLIC_READ** - The project builds are visible to the public.
        - **PRIVATE** - The project builds are not visible to the public.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-visibility
        '''
        result = self._values.get("visibility")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_config(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.VpcConfigProperty]]:
        '''``VpcConfig`` specifies settings that enable AWS CodeBuild to access resources in an Amazon VPC.

        For more information, see `Use AWS CodeBuild with Amazon Virtual Private Cloud <https://docs.aws.amazon.com/codebuild/latest/userguide/vpc-support.html>`_ in the *AWS CodeBuild User Guide* .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-vpcconfig
        '''
        result = self._values.get("vpc_config")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.VpcConfigProperty]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnProjectProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_core_f4b25747.IInspectable)
class CfnReportGroup(
    _aws_cdk_core_f4b25747.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.CfnReportGroup",
):
    '''A CloudFormation ``AWS::CodeBuild::ReportGroup``.

    Represents a report group. A report group contains a collection of reports.

    :cloudformationResource: AWS::CodeBuild::ReportGroup
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-reportgroup.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_codebuild as codebuild
        
        cfn_report_group = codebuild.CfnReportGroup(self, "MyCfnReportGroup",
            export_config=codebuild.CfnReportGroup.ReportExportConfigProperty(
                export_config_type="exportConfigType",
        
                # the properties below are optional
                s3_destination=codebuild.CfnReportGroup.S3ReportExportConfigProperty(
                    bucket="bucket",
        
                    # the properties below are optional
                    bucket_owner="bucketOwner",
                    encryption_disabled=False,
                    encryption_key="encryptionKey",
                    packaging="packaging",
                    path="path"
                )
            ),
            type="type",
        
            # the properties below are optional
            delete_reports=False,
            name="name",
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
        export_config: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnReportGroup.ReportExportConfigProperty", typing.Dict[builtins.str, typing.Any]]],
        type: builtins.str,
        delete_reports: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Create a new ``AWS::CodeBuild::ReportGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param export_config: Information about the destination where the raw data of this ``ReportGroup`` is exported.
        :param type: The type of the ``ReportGroup`` . This can be one of the following values:. - **CODE_COVERAGE** - The report group contains code coverage reports. - **TEST** - The report group contains test reports.
        :param delete_reports: When deleting a report group, specifies if reports within the report group should be deleted. - **true** - Deletes any reports that belong to the report group before deleting the report group. - **false** - You must delete any reports in the report group. This is the default value. If you delete a report group that contains one or more reports, an exception is thrown.
        :param name: The name of the ``ReportGroup`` .
        :param tags: A list of tag key and value pairs associated with this report group. These tags are available for use by AWS services that support AWS CodeBuild report group tags.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f92216f1bb6ae54dc1e88dd4aa0da5ee263d04bb7644a86092a09964fdbaad09)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnReportGroupProps(
            export_config=export_config,
            type=type,
            delete_reports=delete_reports,
            name=name,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _aws_cdk_core_f4b25747.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14e3eb7944da4d9dfa360fe917e94b280b8b6002c3765a8dc7f3d66c6b534e51)
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
            type_hints = typing.get_type_hints(_typecheckingstub__731d73dfe91420745e6bd5f99e1ff2fd4c5d84a4bcb01322e1215e0a0e6c033c)
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
        '''The ARN of the AWS CodeBuild report group, such as ``arn:aws:codebuild:region:123456789012:report-group/myReportGroupName`` .

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
        '''A list of tag key and value pairs associated with this report group.

        These tags are available for use by AWS services that support AWS CodeBuild report group tags.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-reportgroup.html#cfn-codebuild-reportgroup-tags
        '''
        return typing.cast(_aws_cdk_core_f4b25747.TagManager, jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="exportConfig")
    def export_config(
        self,
    ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnReportGroup.ReportExportConfigProperty"]:
        '''Information about the destination where the raw data of this ``ReportGroup`` is exported.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-reportgroup.html#cfn-codebuild-reportgroup-exportconfig
        '''
        return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnReportGroup.ReportExportConfigProperty"], jsii.get(self, "exportConfig"))

    @export_config.setter
    def export_config(
        self,
        value: typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnReportGroup.ReportExportConfigProperty"],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2a9045b9271c9bf6517d7be4d11f9b1774e78c8f91fd77a2c0b719e9dac0c67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exportConfig", value)

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''The type of the ``ReportGroup`` . This can be one of the following values:.

        - **CODE_COVERAGE** - The report group contains code coverage reports.
        - **TEST** - The report group contains test reports.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-reportgroup.html#cfn-codebuild-reportgroup-type
        '''
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22e6211e0f2a2cff1764f8540c25aff2bb5326593f0e3778c932021001f44db4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)

    @builtins.property
    @jsii.member(jsii_name="deleteReports")
    def delete_reports(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
        '''When deleting a report group, specifies if reports within the report group should be deleted.

        - **true** - Deletes any reports that belong to the report group before deleting the report group.
        - **false** - You must delete any reports in the report group. This is the default value. If you delete a report group that contains one or more reports, an exception is thrown.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-reportgroup.html#cfn-codebuild-reportgroup-deletereports
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], jsii.get(self, "deleteReports"))

    @delete_reports.setter
    def delete_reports(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cb72ff347730c0506f7c09ba12aed11ef9a53af93a6c972bfcf40f353254eab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteReports", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the ``ReportGroup`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-reportgroup.html#cfn-codebuild-reportgroup-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48d36f8ea8526e127dffb97d94a8417a0e001a2490d52542fd22f9e3ac96bba5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnReportGroup.ReportExportConfigProperty",
        jsii_struct_bases=[],
        name_mapping={
            "export_config_type": "exportConfigType",
            "s3_destination": "s3Destination",
        },
    )
    class ReportExportConfigProperty:
        def __init__(
            self,
            *,
            export_config_type: builtins.str,
            s3_destination: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnReportGroup.S3ReportExportConfigProperty", typing.Dict[builtins.str, typing.Any]]]] = None,
        ) -> None:
            '''Information about the location where the run of a report is exported.

            :param export_config_type: The export configuration type. Valid values are:. - ``S3`` : The report results are exported to an S3 bucket. - ``NO_EXPORT`` : The report results are not exported.
            :param s3_destination: A ``S3ReportExportConfig`` object that contains information about the S3 bucket where the run of a report is exported.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-reportgroup-reportexportconfig.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                report_export_config_property = codebuild.CfnReportGroup.ReportExportConfigProperty(
                    export_config_type="exportConfigType",
                
                    # the properties below are optional
                    s3_destination=codebuild.CfnReportGroup.S3ReportExportConfigProperty(
                        bucket="bucket",
                
                        # the properties below are optional
                        bucket_owner="bucketOwner",
                        encryption_disabled=False,
                        encryption_key="encryptionKey",
                        packaging="packaging",
                        path="path"
                    )
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__2debb973a10dcc817fbae8314b8af44ea8a7e640ad1b0206715ce438044f45b9)
                check_type(argname="argument export_config_type", value=export_config_type, expected_type=type_hints["export_config_type"])
                check_type(argname="argument s3_destination", value=s3_destination, expected_type=type_hints["s3_destination"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "export_config_type": export_config_type,
            }
            if s3_destination is not None:
                self._values["s3_destination"] = s3_destination

        @builtins.property
        def export_config_type(self) -> builtins.str:
            '''The export configuration type. Valid values are:.

            - ``S3`` : The report results are exported to an S3 bucket.
            - ``NO_EXPORT`` : The report results are not exported.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-reportgroup-reportexportconfig.html#cfn-codebuild-reportgroup-reportexportconfig-exportconfigtype
            '''
            result = self._values.get("export_config_type")
            assert result is not None, "Required property 'export_config_type' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def s3_destination(
            self,
        ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnReportGroup.S3ReportExportConfigProperty"]]:
            '''A ``S3ReportExportConfig`` object that contains information about the S3 bucket where the run of a report is exported.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-reportgroup-reportexportconfig.html#cfn-codebuild-reportgroup-reportexportconfig-s3destination
            '''
            result = self._values.get("s3_destination")
            return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnReportGroup.S3ReportExportConfigProperty"]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ReportExportConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codebuild.CfnReportGroup.S3ReportExportConfigProperty",
        jsii_struct_bases=[],
        name_mapping={
            "bucket": "bucket",
            "bucket_owner": "bucketOwner",
            "encryption_disabled": "encryptionDisabled",
            "encryption_key": "encryptionKey",
            "packaging": "packaging",
            "path": "path",
        },
    )
    class S3ReportExportConfigProperty:
        def __init__(
            self,
            *,
            bucket: builtins.str,
            bucket_owner: typing.Optional[builtins.str] = None,
            encryption_disabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
            encryption_key: typing.Optional[builtins.str] = None,
            packaging: typing.Optional[builtins.str] = None,
            path: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Information about the S3 bucket where the raw data of a report are exported.

            :param bucket: The name of the S3 bucket where the raw data of a report are exported.
            :param bucket_owner: The AWS account identifier of the owner of the Amazon S3 bucket. This allows report data to be exported to an Amazon S3 bucket that is owned by an account other than the account running the build.
            :param encryption_disabled: A boolean value that specifies if the results of a report are encrypted.
            :param encryption_key: The encryption key for the report's encrypted raw data.
            :param packaging: The type of build output artifact to create. Valid values include:. - ``NONE`` : CodeBuild creates the raw data in the output bucket. This is the default if packaging is not specified. - ``ZIP`` : CodeBuild creates a ZIP file with the raw data in the output bucket.
            :param path: The path to the exported report's raw data results.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-reportgroup-s3reportexportconfig.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codebuild as codebuild
                
                s3_report_export_config_property = codebuild.CfnReportGroup.S3ReportExportConfigProperty(
                    bucket="bucket",
                
                    # the properties below are optional
                    bucket_owner="bucketOwner",
                    encryption_disabled=False,
                    encryption_key="encryptionKey",
                    packaging="packaging",
                    path="path"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__96033dcf7f4e3529dc1d675c74aa7019970daa92fc6fc430c877d3e0e81498d7)
                check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
                check_type(argname="argument bucket_owner", value=bucket_owner, expected_type=type_hints["bucket_owner"])
                check_type(argname="argument encryption_disabled", value=encryption_disabled, expected_type=type_hints["encryption_disabled"])
                check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
                check_type(argname="argument packaging", value=packaging, expected_type=type_hints["packaging"])
                check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "bucket": bucket,
            }
            if bucket_owner is not None:
                self._values["bucket_owner"] = bucket_owner
            if encryption_disabled is not None:
                self._values["encryption_disabled"] = encryption_disabled
            if encryption_key is not None:
                self._values["encryption_key"] = encryption_key
            if packaging is not None:
                self._values["packaging"] = packaging
            if path is not None:
                self._values["path"] = path

        @builtins.property
        def bucket(self) -> builtins.str:
            '''The name of the S3 bucket where the raw data of a report are exported.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-reportgroup-s3reportexportconfig.html#cfn-codebuild-reportgroup-s3reportexportconfig-bucket
            '''
            result = self._values.get("bucket")
            assert result is not None, "Required property 'bucket' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def bucket_owner(self) -> typing.Optional[builtins.str]:
            '''The AWS account identifier of the owner of the Amazon S3 bucket.

            This allows report data to be exported to an Amazon S3 bucket that is owned by an account other than the account running the build.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-reportgroup-s3reportexportconfig.html#cfn-codebuild-reportgroup-s3reportexportconfig-bucketowner
            '''
            result = self._values.get("bucket_owner")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def encryption_disabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
            '''A boolean value that specifies if the results of a report are encrypted.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-reportgroup-s3reportexportconfig.html#cfn-codebuild-reportgroup-s3reportexportconfig-encryptiondisabled
            '''
            result = self._values.get("encryption_disabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

        @builtins.property
        def encryption_key(self) -> typing.Optional[builtins.str]:
            '''The encryption key for the report's encrypted raw data.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-reportgroup-s3reportexportconfig.html#cfn-codebuild-reportgroup-s3reportexportconfig-encryptionkey
            '''
            result = self._values.get("encryption_key")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def packaging(self) -> typing.Optional[builtins.str]:
            '''The type of build output artifact to create. Valid values include:.

            - ``NONE`` : CodeBuild creates the raw data in the output bucket. This is the default if packaging is not specified.
            - ``ZIP`` : CodeBuild creates a ZIP file with the raw data in the output bucket.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-reportgroup-s3reportexportconfig.html#cfn-codebuild-reportgroup-s3reportexportconfig-packaging
            '''
            result = self._values.get("packaging")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def path(self) -> typing.Optional[builtins.str]:
            '''The path to the exported report's raw data results.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-reportgroup-s3reportexportconfig.html#cfn-codebuild-reportgroup-s3reportexportconfig-path
            '''
            result = self._values.get("path")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3ReportExportConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.CfnReportGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "export_config": "exportConfig",
        "type": "type",
        "delete_reports": "deleteReports",
        "name": "name",
        "tags": "tags",
    },
)
class CfnReportGroupProps:
    def __init__(
        self,
        *,
        export_config: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnReportGroup.ReportExportConfigProperty, typing.Dict[builtins.str, typing.Any]]],
        type: builtins.str,
        delete_reports: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for defining a ``CfnReportGroup``.

        :param export_config: Information about the destination where the raw data of this ``ReportGroup`` is exported.
        :param type: The type of the ``ReportGroup`` . This can be one of the following values:. - **CODE_COVERAGE** - The report group contains code coverage reports. - **TEST** - The report group contains test reports.
        :param delete_reports: When deleting a report group, specifies if reports within the report group should be deleted. - **true** - Deletes any reports that belong to the report group before deleting the report group. - **false** - You must delete any reports in the report group. This is the default value. If you delete a report group that contains one or more reports, an exception is thrown.
        :param name: The name of the ``ReportGroup`` .
        :param tags: A list of tag key and value pairs associated with this report group. These tags are available for use by AWS services that support AWS CodeBuild report group tags.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-reportgroup.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            
            cfn_report_group_props = codebuild.CfnReportGroupProps(
                export_config=codebuild.CfnReportGroup.ReportExportConfigProperty(
                    export_config_type="exportConfigType",
            
                    # the properties below are optional
                    s3_destination=codebuild.CfnReportGroup.S3ReportExportConfigProperty(
                        bucket="bucket",
            
                        # the properties below are optional
                        bucket_owner="bucketOwner",
                        encryption_disabled=False,
                        encryption_key="encryptionKey",
                        packaging="packaging",
                        path="path"
                    )
                ),
                type="type",
            
                # the properties below are optional
                delete_reports=False,
                name="name",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__397a5fa8704df5157d129d09505db14cbf6e27cff6904c9223bbbaeb4cafad3c)
            check_type(argname="argument export_config", value=export_config, expected_type=type_hints["export_config"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument delete_reports", value=delete_reports, expected_type=type_hints["delete_reports"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "export_config": export_config,
            "type": type,
        }
        if delete_reports is not None:
            self._values["delete_reports"] = delete_reports
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def export_config(
        self,
    ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnReportGroup.ReportExportConfigProperty]:
        '''Information about the destination where the raw data of this ``ReportGroup`` is exported.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-reportgroup.html#cfn-codebuild-reportgroup-exportconfig
        '''
        result = self._values.get("export_config")
        assert result is not None, "Required property 'export_config' is missing"
        return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnReportGroup.ReportExportConfigProperty], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of the ``ReportGroup`` . This can be one of the following values:.

        - **CODE_COVERAGE** - The report group contains code coverage reports.
        - **TEST** - The report group contains test reports.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-reportgroup.html#cfn-codebuild-reportgroup-type
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delete_reports(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]]:
        '''When deleting a report group, specifies if reports within the report group should be deleted.

        - **true** - Deletes any reports that belong to the report group before deleting the report group.
        - **false** - You must delete any reports in the report group. This is the default value. If you delete a report group that contains one or more reports, an exception is thrown.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-reportgroup.html#cfn-codebuild-reportgroup-deletereports
        '''
        result = self._values.get("delete_reports")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the ``ReportGroup`` .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-reportgroup.html#cfn-codebuild-reportgroup-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_core_f4b25747.CfnTag]]:
        '''A list of tag key and value pairs associated with this report group.

        These tags are available for use by AWS services that support AWS CodeBuild report group tags.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-reportgroup.html#cfn-codebuild-reportgroup-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_core_f4b25747.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnReportGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_aws_cdk_core_f4b25747.IInspectable)
class CfnSourceCredential(
    _aws_cdk_core_f4b25747.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.CfnSourceCredential",
):
    '''A CloudFormation ``AWS::CodeBuild::SourceCredential``.

    Information about the credentials for a GitHub, GitHub Enterprise, or Bitbucket repository. We strongly recommend that you use AWS Secrets Manager to store your credentials. If you use Secrets Manager , you must have secrets in your secrets manager. For more information, see `Using Dynamic References to Specify Template Values <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html#dynamic-references-secretsmanager>`_ .
    .. epigraph::

       For security purposes, do not use plain text in your AWS CloudFormation template to store your credentials.

    :cloudformationResource: AWS::CodeBuild::SourceCredential
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-sourcecredential.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_codebuild as codebuild
        
        cfn_source_credential = codebuild.CfnSourceCredential(self, "MyCfnSourceCredential",
            auth_type="authType",
            server_type="serverType",
            token="token",
        
            # the properties below are optional
            username="username"
        )
    '''

    def __init__(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        id: builtins.str,
        *,
        auth_type: builtins.str,
        server_type: builtins.str,
        token: builtins.str,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::CodeBuild::SourceCredential``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param auth_type: The type of authentication used by the credentials. Valid options are OAUTH, BASIC_AUTH, or PERSONAL_ACCESS_TOKEN.
        :param server_type: The type of source provider. The valid options are GITHUB, GITHUB_ENTERPRISE, or BITBUCKET.
        :param token: For GitHub or GitHub Enterprise, this is the personal access token. For Bitbucket, this is the app password.
        :param username: The Bitbucket username when the ``authType`` is BASIC_AUTH. This parameter is not valid for other types of source providers or connections.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8af3671099fa95307aa855c32c5271bff0edad2d4763e1f5916666c1de9f3e9d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnSourceCredentialProps(
            auth_type=auth_type,
            server_type=server_type,
            token=token,
            username=username,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _aws_cdk_core_f4b25747.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5891cba835ffb26d002a73be032b0b460a111e259505c25478d1a435c451d724)
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
            type_hints = typing.get_type_hints(_typecheckingstub__eaec9caebf548ea97e4ef10165a6caecf0363069b8b77a6f6dd7b857032df369)
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property
    @jsii.member(jsii_name="authType")
    def auth_type(self) -> builtins.str:
        '''The type of authentication used by the credentials.

        Valid options are OAUTH, BASIC_AUTH, or PERSONAL_ACCESS_TOKEN.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-sourcecredential.html#cfn-codebuild-sourcecredential-authtype
        '''
        return typing.cast(builtins.str, jsii.get(self, "authType"))

    @auth_type.setter
    def auth_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f4f2a2355d7e187a31d16a8c42b013b96be3e75e23a67e449ca3a918c991464)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authType", value)

    @builtins.property
    @jsii.member(jsii_name="serverType")
    def server_type(self) -> builtins.str:
        '''The type of source provider.

        The valid options are GITHUB, GITHUB_ENTERPRISE, or BITBUCKET.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-sourcecredential.html#cfn-codebuild-sourcecredential-servertype
        '''
        return typing.cast(builtins.str, jsii.get(self, "serverType"))

    @server_type.setter
    def server_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cda856471d9b230be0ba326ff411a240dc18b550f41f4fb7432a6cbe7996c574)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverType", value)

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> builtins.str:
        '''For GitHub or GitHub Enterprise, this is the personal access token.

        For Bitbucket, this is the app password.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-sourcecredential.html#cfn-codebuild-sourcecredential-token
        '''
        return typing.cast(builtins.str, jsii.get(self, "token"))

    @token.setter
    def token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15bf729c34a0a146d344ce53f980d81ab16a3219ecc1465c6e1c9bb8ee20cd15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "token", value)

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> typing.Optional[builtins.str]:
        '''The Bitbucket username when the ``authType`` is BASIC_AUTH.

        This parameter is not valid for other types of source providers or connections.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-sourcecredential.html#cfn-codebuild-sourcecredential-username
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "username"))

    @username.setter
    def username(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa810b139be0677dece2577c83c36ccc0ac4284fd3063df0ea04fe624679155c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.CfnSourceCredentialProps",
    jsii_struct_bases=[],
    name_mapping={
        "auth_type": "authType",
        "server_type": "serverType",
        "token": "token",
        "username": "username",
    },
)
class CfnSourceCredentialProps:
    def __init__(
        self,
        *,
        auth_type: builtins.str,
        server_type: builtins.str,
        token: builtins.str,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``CfnSourceCredential``.

        :param auth_type: The type of authentication used by the credentials. Valid options are OAUTH, BASIC_AUTH, or PERSONAL_ACCESS_TOKEN.
        :param server_type: The type of source provider. The valid options are GITHUB, GITHUB_ENTERPRISE, or BITBUCKET.
        :param token: For GitHub or GitHub Enterprise, this is the personal access token. For Bitbucket, this is the app password.
        :param username: The Bitbucket username when the ``authType`` is BASIC_AUTH. This parameter is not valid for other types of source providers or connections.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-sourcecredential.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            
            cfn_source_credential_props = codebuild.CfnSourceCredentialProps(
                auth_type="authType",
                server_type="serverType",
                token="token",
            
                # the properties below are optional
                username="username"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21dcdc0d6ea4af957c572ba6f20450bdbc127bdd7ca2ffbb90d97f5bbac28137)
            check_type(argname="argument auth_type", value=auth_type, expected_type=type_hints["auth_type"])
            check_type(argname="argument server_type", value=server_type, expected_type=type_hints["server_type"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auth_type": auth_type,
            "server_type": server_type,
            "token": token,
        }
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def auth_type(self) -> builtins.str:
        '''The type of authentication used by the credentials.

        Valid options are OAUTH, BASIC_AUTH, or PERSONAL_ACCESS_TOKEN.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-sourcecredential.html#cfn-codebuild-sourcecredential-authtype
        '''
        result = self._values.get("auth_type")
        assert result is not None, "Required property 'auth_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_type(self) -> builtins.str:
        '''The type of source provider.

        The valid options are GITHUB, GITHUB_ENTERPRISE, or BITBUCKET.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-sourcecredential.html#cfn-codebuild-sourcecredential-servertype
        '''
        result = self._values.get("server_type")
        assert result is not None, "Required property 'server_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def token(self) -> builtins.str:
        '''For GitHub or GitHub Enterprise, this is the personal access token.

        For Bitbucket, this is the app password.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-sourcecredential.html#cfn-codebuild-sourcecredential-token
        '''
        result = self._values.get("token")
        assert result is not None, "Required property 'token' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The Bitbucket username when the ``authType`` is BASIC_AUTH.

        This parameter is not valid for other types of source providers or connections.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-sourcecredential.html#cfn-codebuild-sourcecredential-username
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnSourceCredentialProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.CloudWatchLoggingOptions",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "log_group": "logGroup", "prefix": "prefix"},
)
class CloudWatchLoggingOptions:
    def __init__(
        self,
        *,
        enabled: typing.Optional[builtins.bool] = None,
        log_group: typing.Optional[_aws_cdk_aws_logs_6c4320fb.ILogGroup] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Information about logs built to a CloudWatch Log Group for a build project.

        :param enabled: The current status of the logs in Amazon CloudWatch Logs for a build project. Default: true
        :param log_group: The Log Group to send logs to. Default: - no log group specified
        :param prefix: The prefix of the stream name of the Amazon CloudWatch Logs. Default: - no prefix

        :exampleMetadata: infused

        Example::

            codebuild.Project(self, "Project",
                logging=codebuild.LoggingOptions(
                    cloud_watch=codebuild.CloudWatchLoggingOptions(
                        log_group=logs.LogGroup(self, "MyLogGroup")
                    )
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4b7d5dc3371bb02cf8425e20f38b02ab76443ede9587588825f49c0211650cb)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if log_group is not None:
            self._values["log_group"] = log_group
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''The current status of the logs in Amazon CloudWatch Logs for a build project.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def log_group(self) -> typing.Optional[_aws_cdk_aws_logs_6c4320fb.ILogGroup]:
        '''The Log Group to send logs to.

        :default: - no log group specified
        '''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_logs_6c4320fb.ILogGroup], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''The prefix of the stream name of the Amazon CloudWatch Logs.

        :default: - no prefix
        '''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudWatchLoggingOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.CommonProjectProps",
    jsii_struct_bases=[],
    name_mapping={
        "allow_all_outbound": "allowAllOutbound",
        "badge": "badge",
        "build_spec": "buildSpec",
        "cache": "cache",
        "check_secrets_in_plain_text_env_variables": "checkSecretsInPlainTextEnvVariables",
        "concurrent_build_limit": "concurrentBuildLimit",
        "description": "description",
        "encryption_key": "encryptionKey",
        "environment": "environment",
        "environment_variables": "environmentVariables",
        "file_system_locations": "fileSystemLocations",
        "grant_report_group_permissions": "grantReportGroupPermissions",
        "logging": "logging",
        "project_name": "projectName",
        "queued_timeout": "queuedTimeout",
        "role": "role",
        "security_groups": "securityGroups",
        "subnet_selection": "subnetSelection",
        "timeout": "timeout",
        "vpc": "vpc",
    },
)
class CommonProjectProps:
    def __init__(
        self,
        *,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        badge: typing.Optional[builtins.bool] = None,
        build_spec: typing.Optional[BuildSpec] = None,
        cache: typing.Optional[Cache] = None,
        check_secrets_in_plain_text_env_variables: typing.Optional[builtins.bool] = None,
        concurrent_build_limit: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
        environment: typing.Optional[typing.Union[BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
        file_system_locations: typing.Optional[typing.Sequence["IFileSystemLocation"]] = None,
        grant_report_group_permissions: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[typing.Union["LoggingOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        project_name: typing.Optional[builtins.str] = None,
        queued_timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_67de8e8d.IVpc] = None,
    ) -> None:
        '''
        :param allow_all_outbound: Whether to allow the CodeBuild to send all network traffic. If set to false, you must individually add traffic rules to allow the CodeBuild project to connect to network targets. Only used if 'vpc' is supplied. Default: true
        :param badge: Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge. For more information, see Build Badges Sample in the AWS CodeBuild User Guide. Default: false
        :param build_spec: Filename or contents of buildspec in JSON format. Default: - Empty buildspec.
        :param cache: Caching strategy to use. Default: Cache.none
        :param check_secrets_in_plain_text_env_variables: Whether to check for the presence of any secrets in the environment variables of the default type, BuildEnvironmentVariableType.PLAINTEXT. Since using a secret for the value of that kind of variable would result in it being displayed in plain text in the AWS Console, the construct will throw an exception if it detects a secret was passed there. Pass this property as false if you want to skip this validation, and keep using a secret in a plain text environment variable. Default: true
        :param concurrent_build_limit: Maximum number of concurrent builds. Minimum value is 1 and maximum is account build limit. Default: - no explicit limit is set
        :param description: A description of the project. Use the description to identify the purpose of the project. Default: - No description.
        :param encryption_key: Encryption key to use to read and write artifacts. Default: - The AWS-managed CMK for Amazon Simple Storage Service (Amazon S3) is used.
        :param environment: Build environment to use for the build. Default: BuildEnvironment.LinuxBuildImage.STANDARD_1_0
        :param environment_variables: Additional environment variables to add to the build environment. Default: - No additional environment variables are specified.
        :param file_system_locations: An ProjectFileSystemLocation objects for a CodeBuild build project. A ProjectFileSystemLocation object specifies the identifier, location, mountOptions, mountPoint, and type of a file system created using Amazon Elastic File System. Default: - no file system locations
        :param grant_report_group_permissions: Add permissions to this project's role to create and use test report groups with name starting with the name of this project. That is the standard report group that gets created when a simple name (in contrast to an ARN) is used in the 'reports' section of the buildspec of this project. This is usually harmless, but you can turn these off if you don't plan on using test reports in this project. Default: true
        :param logging: Information about logs for the build project. A project can create logs in Amazon CloudWatch Logs, an S3 bucket, or both. Default: - no log configuration is set
        :param project_name: The physical, human-readable name of the CodeBuild Project. Default: - Name is automatically generated.
        :param queued_timeout: The number of minutes after which AWS CodeBuild stops the build if it's still in queue. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: - no queue timeout is set
        :param role: Service Role to assume while running the build. Default: - A role will be created.
        :param security_groups: What security group to associate with the codebuild project's network interfaces. If no security group is identified, one will be created automatically. Only used if 'vpc' is supplied. Default: - Security group will be automatically created.
        :param subnet_selection: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Default: - All private subnets.
        :param timeout: The number of minutes after which AWS CodeBuild stops the build if it's not complete. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: Duration.hours(1)
        :param vpc: VPC network to place codebuild network interfaces. Specify this if the codebuild project needs to access resources in a VPC. Default: - No VPC is specified.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            import aws_cdk.aws_ec2 as ec2
            import aws_cdk.aws_iam as iam
            import aws_cdk.aws_kms as kms
            import aws_cdk.aws_logs as logs
            import aws_cdk.aws_s3 as s3
            import aws_cdk.core as cdk
            
            # bucket: s3.Bucket
            # build_image: codebuild.IBuildImage
            # build_spec: codebuild.BuildSpec
            # cache: codebuild.Cache
            # file_system_location: codebuild.IFileSystemLocation
            # key: kms.Key
            # log_group: logs.LogGroup
            # role: iam.Role
            # security_group: ec2.SecurityGroup
            # subnet: ec2.Subnet
            # subnet_filter: ec2.SubnetFilter
            # value: Any
            # vpc: ec2.Vpc
            
            common_project_props = codebuild.CommonProjectProps(
                allow_all_outbound=False,
                badge=False,
                build_spec=build_spec,
                cache=cache,
                check_secrets_in_plain_text_env_variables=False,
                concurrent_build_limit=123,
                description="description",
                encryption_key=key,
                environment=codebuild.BuildEnvironment(
                    build_image=build_image,
                    certificate=codebuild.BuildEnvironmentCertificate(
                        bucket=bucket,
                        object_key="objectKey"
                    ),
                    compute_type=codebuild.ComputeType.SMALL,
                    environment_variables={
                        "environment_variables_key": codebuild.BuildEnvironmentVariable(
                            value=value,
            
                            # the properties below are optional
                            type=codebuild.BuildEnvironmentVariableType.PLAINTEXT
                        )
                    },
                    privileged=False
                ),
                environment_variables={
                    "environment_variables_key": codebuild.BuildEnvironmentVariable(
                        value=value,
            
                        # the properties below are optional
                        type=codebuild.BuildEnvironmentVariableType.PLAINTEXT
                    )
                },
                file_system_locations=[file_system_location],
                grant_report_group_permissions=False,
                logging=codebuild.LoggingOptions(
                    cloud_watch=codebuild.CloudWatchLoggingOptions(
                        enabled=False,
                        log_group=log_group,
                        prefix="prefix"
                    ),
                    s3=codebuild.S3LoggingOptions(
                        bucket=bucket,
            
                        # the properties below are optional
                        enabled=False,
                        encrypted=False,
                        prefix="prefix"
                    )
                ),
                project_name="projectName",
                queued_timeout=cdk.Duration.minutes(30),
                role=role,
                security_groups=[security_group],
                subnet_selection=ec2.SubnetSelection(
                    availability_zones=["availabilityZones"],
                    one_per_az=False,
                    subnet_filters=[subnet_filter],
                    subnet_group_name="subnetGroupName",
                    subnet_name="subnetName",
                    subnets=[subnet],
                    subnet_type=ec2.SubnetType.ISOLATED
                ),
                timeout=cdk.Duration.minutes(30),
                vpc=vpc
            )
        '''
        if isinstance(environment, dict):
            environment = BuildEnvironment(**environment)
        if isinstance(logging, dict):
            logging = LoggingOptions(**logging)
        if isinstance(subnet_selection, dict):
            subnet_selection = _aws_cdk_aws_ec2_67de8e8d.SubnetSelection(**subnet_selection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed64d36304c2ccdb6eb818ec5e83a5e953ce4ad703b9d20dafcae588e38d942a)
            check_type(argname="argument allow_all_outbound", value=allow_all_outbound, expected_type=type_hints["allow_all_outbound"])
            check_type(argname="argument badge", value=badge, expected_type=type_hints["badge"])
            check_type(argname="argument build_spec", value=build_spec, expected_type=type_hints["build_spec"])
            check_type(argname="argument cache", value=cache, expected_type=type_hints["cache"])
            check_type(argname="argument check_secrets_in_plain_text_env_variables", value=check_secrets_in_plain_text_env_variables, expected_type=type_hints["check_secrets_in_plain_text_env_variables"])
            check_type(argname="argument concurrent_build_limit", value=concurrent_build_limit, expected_type=type_hints["concurrent_build_limit"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument environment_variables", value=environment_variables, expected_type=type_hints["environment_variables"])
            check_type(argname="argument file_system_locations", value=file_system_locations, expected_type=type_hints["file_system_locations"])
            check_type(argname="argument grant_report_group_permissions", value=grant_report_group_permissions, expected_type=type_hints["grant_report_group_permissions"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument project_name", value=project_name, expected_type=type_hints["project_name"])
            check_type(argname="argument queued_timeout", value=queued_timeout, expected_type=type_hints["queued_timeout"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnet_selection", value=subnet_selection, expected_type=type_hints["subnet_selection"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if badge is not None:
            self._values["badge"] = badge
        if build_spec is not None:
            self._values["build_spec"] = build_spec
        if cache is not None:
            self._values["cache"] = cache
        if check_secrets_in_plain_text_env_variables is not None:
            self._values["check_secrets_in_plain_text_env_variables"] = check_secrets_in_plain_text_env_variables
        if concurrent_build_limit is not None:
            self._values["concurrent_build_limit"] = concurrent_build_limit
        if description is not None:
            self._values["description"] = description
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if environment is not None:
            self._values["environment"] = environment
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if file_system_locations is not None:
            self._values["file_system_locations"] = file_system_locations
        if grant_report_group_permissions is not None:
            self._values["grant_report_group_permissions"] = grant_report_group_permissions
        if logging is not None:
            self._values["logging"] = logging
        if project_name is not None:
            self._values["project_name"] = project_name
        if queued_timeout is not None:
            self._values["queued_timeout"] = queued_timeout
        if role is not None:
            self._values["role"] = role
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection
        if timeout is not None:
            self._values["timeout"] = timeout
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether to allow the CodeBuild to send all network traffic.

        If set to false, you must individually add traffic rules to allow the
        CodeBuild project to connect to network targets.

        Only used if 'vpc' is supplied.

        :default: true
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def badge(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge.

        For more information, see Build Badges Sample
        in the AWS CodeBuild User Guide.

        :default: false
        '''
        result = self._values.get("badge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def build_spec(self) -> typing.Optional[BuildSpec]:
        '''Filename or contents of buildspec in JSON format.

        :default: - Empty buildspec.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec-ref-example
        '''
        result = self._values.get("build_spec")
        return typing.cast(typing.Optional[BuildSpec], result)

    @builtins.property
    def cache(self) -> typing.Optional[Cache]:
        '''Caching strategy to use.

        :default: Cache.none
        '''
        result = self._values.get("cache")
        return typing.cast(typing.Optional[Cache], result)

    @builtins.property
    def check_secrets_in_plain_text_env_variables(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''Whether to check for the presence of any secrets in the environment variables of the default type, BuildEnvironmentVariableType.PLAINTEXT. Since using a secret for the value of that kind of variable would result in it being displayed in plain text in the AWS Console, the construct will throw an exception if it detects a secret was passed there. Pass this property as false if you want to skip this validation, and keep using a secret in a plain text environment variable.

        :default: true
        '''
        result = self._values.get("check_secrets_in_plain_text_env_variables")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def concurrent_build_limit(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of concurrent builds.

        Minimum value is 1 and maximum is account build limit.

        :default: - no explicit limit is set
        '''
        result = self._values.get("concurrent_build_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the project.

        Use the description to identify the purpose
        of the project.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey]:
        '''Encryption key to use to read and write artifacts.

        :default: - The AWS-managed CMK for Amazon Simple Storage Service (Amazon S3) is used.
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey], result)

    @builtins.property
    def environment(self) -> typing.Optional[BuildEnvironment]:
        '''Build environment to use for the build.

        :default: BuildEnvironment.LinuxBuildImage.STANDARD_1_0
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[BuildEnvironment], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, BuildEnvironmentVariable]]:
        '''Additional environment variables to add to the build environment.

        :default: - No additional environment variables are specified.
        '''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, BuildEnvironmentVariable]], result)

    @builtins.property
    def file_system_locations(
        self,
    ) -> typing.Optional[typing.List["IFileSystemLocation"]]:
        '''An  ProjectFileSystemLocation objects for a CodeBuild build project.

        A ProjectFileSystemLocation object specifies the identifier, location, mountOptions, mountPoint,
        and type of a file system created using Amazon Elastic File System.

        :default: - no file system locations
        '''
        result = self._values.get("file_system_locations")
        return typing.cast(typing.Optional[typing.List["IFileSystemLocation"]], result)

    @builtins.property
    def grant_report_group_permissions(self) -> typing.Optional[builtins.bool]:
        '''Add permissions to this project's role to create and use test report groups with name starting with the name of this project.

        That is the standard report group that gets created when a simple name
        (in contrast to an ARN)
        is used in the 'reports' section of the buildspec of this project.
        This is usually harmless, but you can turn these off if you don't plan on using test
        reports in this project.

        :default: true

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/test-report-group-naming.html
        '''
        result = self._values.get("grant_report_group_permissions")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def logging(self) -> typing.Optional["LoggingOptions"]:
        '''Information about logs for the build project.

        A project can create logs in Amazon CloudWatch Logs, an S3 bucket, or both.

        :default: - no log configuration is set
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional["LoggingOptions"], result)

    @builtins.property
    def project_name(self) -> typing.Optional[builtins.str]:
        '''The physical, human-readable name of the CodeBuild Project.

        :default: - Name is automatically generated.
        '''
        result = self._values.get("project_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queued_timeout(self) -> typing.Optional[_aws_cdk_core_f4b25747.Duration]:
        '''The number of minutes after which AWS CodeBuild stops the build if it's still in queue.

        For valid values, see the timeoutInMinutes field in the AWS
        CodeBuild User Guide.

        :default: - no queue timeout is set
        '''
        result = self._values.get("queued_timeout")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Duration], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole]:
        '''Service Role to assume while running the build.

        :default: - A role will be created.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]]:
        '''What security group to associate with the codebuild project's network interfaces.

        If no security group is identified, one will be created automatically.

        Only used if 'vpc' is supplied.

        :default: - Security group will be automatically created.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]], result)

    @builtins.property
    def subnet_selection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection]:
        '''Where to place the network interfaces within the VPC.

        Only used if 'vpc' is supplied.

        :default: - All private subnets.
        '''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_core_f4b25747.Duration]:
        '''The number of minutes after which AWS CodeBuild stops the build if it's not complete.

        For valid values, see the timeoutInMinutes field in the AWS
        CodeBuild User Guide.

        :default: Duration.hours(1)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Duration], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_67de8e8d.IVpc]:
        '''VPC network to place codebuild network interfaces.

        Specify this if the codebuild project needs to access resources in a VPC.

        :default: - No VPC is specified.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_67de8e8d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonProjectProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-codebuild.ComputeType")
class ComputeType(enum.Enum):
    '''Build machine compute type.

    :exampleMetadata: infused

    Example::

        # vpc: ec2.Vpc
        # my_security_group: ec2.SecurityGroup
        
        pipelines.CodeBuildStep("Synth",
            # ...standard ShellStep props...
            commands=[],
            env={},
        
            # If you are using a CodeBuildStep explicitly, set the 'cdk.out' directory
            # to be the synth step's output.
            primary_output_directory="cdk.out",
        
            # Control the name of the project
            project_name="MyProject",
        
            # Control parts of the BuildSpec other than the regular 'build' and 'install' commands
            partial_build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2"
            }),
        
            # Control the build environment
            build_environment=codebuild.BuildEnvironment(
                compute_type=codebuild.ComputeType.LARGE
            ),
            timeout=Duration.minutes(90),
        
            # Control Elastic Network Interface creation
            vpc=vpc,
            subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
            security_groups=[my_security_group],
        
            # Additional policy statements for the execution role
            role_policy_statements=[
                iam.PolicyStatement()
            ]
        )
    '''

    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"
    X2_LARGE = "X2_LARGE"


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.DockerImageOptions",
    jsii_struct_bases=[],
    name_mapping={"secrets_manager_credentials": "secretsManagerCredentials"},
)
class DockerImageOptions:
    def __init__(
        self,
        *,
        secrets_manager_credentials: typing.Optional[_aws_cdk_aws_secretsmanager_72af8d6f.ISecret] = None,
    ) -> None:
        '''The options when creating a CodeBuild Docker build image using {@link LinuxBuildImage.fromDockerRegistry} or {@link WindowsBuildImage.fromDockerRegistry}.

        :param secrets_manager_credentials: The credentials, stored in Secrets Manager, used for accessing the repository holding the image, if the repository is private. Default: no credentials will be used (we assume the repository is public)

        :exampleMetadata: lit=test/integ.docker-registry.lit.ts infused

        Example::

            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.from_docker_registry("my-registry/my-repo",
                    secrets_manager_credentials=secrets
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e25f3d1f063a586cd4be7a719e5cdd4d3390bf2cade9979be4f82aa09431a030)
            check_type(argname="argument secrets_manager_credentials", value=secrets_manager_credentials, expected_type=type_hints["secrets_manager_credentials"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if secrets_manager_credentials is not None:
            self._values["secrets_manager_credentials"] = secrets_manager_credentials

    @builtins.property
    def secrets_manager_credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_72af8d6f.ISecret]:
        '''The credentials, stored in Secrets Manager, used for accessing the repository holding the image, if the repository is private.

        :default: no credentials will be used (we assume the repository is public)
        '''
        result = self._values.get("secrets_manager_credentials")
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_72af8d6f.ISecret], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerImageOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.EfsFileSystemLocationProps",
    jsii_struct_bases=[],
    name_mapping={
        "identifier": "identifier",
        "location": "location",
        "mount_point": "mountPoint",
        "mount_options": "mountOptions",
    },
)
class EfsFileSystemLocationProps:
    def __init__(
        self,
        *,
        identifier: builtins.str,
        location: builtins.str,
        mount_point: builtins.str,
        mount_options: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Construction properties for {@link EfsFileSystemLocation}.

        :param identifier: The name used to access a file system created by Amazon EFS.
        :param location: A string that specifies the location of the file system, like Amazon EFS. This value looks like ``fs-abcd1234.efs.us-west-2.amazonaws.com:/my-efs-mount-directory``.
        :param mount_point: The location in the container where you mount the file system.
        :param mount_options: The mount options for a file system such as Amazon EFS. Default: 'nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2'.

        :exampleMetadata: infused

        Example::

            codebuild.Project(self, "MyProject",
                build_spec=codebuild.BuildSpec.from_object({
                    "version": "0.2"
                }),
                file_system_locations=[
                    codebuild.FileSystemLocation.efs(
                        identifier="myidentifier2",
                        location="myclodation.mydnsroot.com:/loc",
                        mount_point="/media",
                        mount_options="opts"
                    )
                ]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbcc57093d54ea5121deaf231a540e66b66673f09f6f6c59270eb229284d3b9e)
            check_type(argname="argument identifier", value=identifier, expected_type=type_hints["identifier"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument mount_point", value=mount_point, expected_type=type_hints["mount_point"])
            check_type(argname="argument mount_options", value=mount_options, expected_type=type_hints["mount_options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "identifier": identifier,
            "location": location,
            "mount_point": mount_point,
        }
        if mount_options is not None:
            self._values["mount_options"] = mount_options

    @builtins.property
    def identifier(self) -> builtins.str:
        '''The name used to access a file system created by Amazon EFS.'''
        result = self._values.get("identifier")
        assert result is not None, "Required property 'identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def location(self) -> builtins.str:
        '''A string that specifies the location of the file system, like Amazon EFS.

        This value looks like ``fs-abcd1234.efs.us-west-2.amazonaws.com:/my-efs-mount-directory``.
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mount_point(self) -> builtins.str:
        '''The location in the container where you mount the file system.'''
        result = self._values.get("mount_point")
        assert result is not None, "Required property 'mount_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mount_options(self) -> typing.Optional[builtins.str]:
        '''The mount options for a file system such as Amazon EFS.

        :default: 'nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2'.
        '''
        result = self._values.get("mount_options")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EfsFileSystemLocationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-codebuild.EventAction")
class EventAction(enum.Enum):
    '''The types of webhook event actions.

    :exampleMetadata: infused

    Example::

        git_hub_source = codebuild.Source.git_hub(
            owner="awslabs",
            repo="aws-cdk",
            webhook=True,  # optional, default: true if `webhookFilters` were provided, false otherwise
            webhook_triggers_batch_build=True,  # optional, default is false
            webhook_filters=[
                codebuild.FilterGroup.in_event_of(codebuild.EventAction.PUSH).and_branch_is("master").and_commit_message_is("the commit message")
            ]
        )
    '''

    PUSH = "PUSH"
    '''A push (of a branch, or a tag) to the repository.'''
    PULL_REQUEST_CREATED = "PULL_REQUEST_CREATED"
    '''Creating a Pull Request.'''
    PULL_REQUEST_UPDATED = "PULL_REQUEST_UPDATED"
    '''Updating a Pull Request.'''
    PULL_REQUEST_MERGED = "PULL_REQUEST_MERGED"
    '''Merging a Pull Request.'''
    PULL_REQUEST_REOPENED = "PULL_REQUEST_REOPENED"
    '''Re-opening a previously closed Pull Request.

    Note that this event is only supported for GitHub and GitHubEnterprise sources.
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.FileSystemConfig",
    jsii_struct_bases=[],
    name_mapping={"location": "location"},
)
class FileSystemConfig:
    def __init__(
        self,
        *,
        location: typing.Union[CfnProject.ProjectFileSystemLocationProperty, typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''The type returned from {@link IFileSystemLocation#bind}.

        :param location: File system location wrapper property.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            
            file_system_config = codebuild.FileSystemConfig(
                location=codebuild.CfnProject.ProjectFileSystemLocationProperty(
                    identifier="identifier",
                    location="location",
                    mount_point="mountPoint",
                    type="type",
            
                    # the properties below are optional
                    mount_options="mountOptions"
                )
            )
        '''
        if isinstance(location, dict):
            location = CfnProject.ProjectFileSystemLocationProperty(**location)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ddde554f590a88f001162f0f7655f9dec75e7c70ea4a41ee380f1fde82305d8)
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "location": location,
        }

    @builtins.property
    def location(self) -> CfnProject.ProjectFileSystemLocationProperty:
        '''File system location wrapper property.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codebuild-project-projectfilesystemlocation.html
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(CfnProject.ProjectFileSystemLocationProperty, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileSystemConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FileSystemLocation(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.FileSystemLocation",
):
    '''FileSystemLocation provider definition for a CodeBuild Project.

    :exampleMetadata: infused

    Example::

        codebuild.Project(self, "MyProject",
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2"
            }),
            file_system_locations=[
                codebuild.FileSystemLocation.efs(
                    identifier="myidentifier2",
                    location="myclodation.mydnsroot.com:/loc",
                    mount_point="/media",
                    mount_options="opts"
                )
            ]
        )
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="efs")
    @builtins.classmethod
    def efs(
        cls,
        *,
        identifier: builtins.str,
        location: builtins.str,
        mount_point: builtins.str,
        mount_options: typing.Optional[builtins.str] = None,
    ) -> "IFileSystemLocation":
        '''EFS file system provider.

        :param identifier: The name used to access a file system created by Amazon EFS.
        :param location: A string that specifies the location of the file system, like Amazon EFS. This value looks like ``fs-abcd1234.efs.us-west-2.amazonaws.com:/my-efs-mount-directory``.
        :param mount_point: The location in the container where you mount the file system.
        :param mount_options: The mount options for a file system such as Amazon EFS. Default: 'nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2'.
        '''
        props = EfsFileSystemLocationProps(
            identifier=identifier,
            location=location,
            mount_point=mount_point,
            mount_options=mount_options,
        )

        return typing.cast("IFileSystemLocation", jsii.sinvoke(cls, "efs", [props]))


class FilterGroup(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.FilterGroup",
):
    '''An object that represents a group of filter conditions for a webhook.

    Every condition in a given FilterGroup must be true in order for the whole group to be true.
    You construct instances of it by calling the {@link #inEventOf} static factory method,
    and then calling various ``andXyz`` instance methods to create modified instances of it
    (this class is immutable).

    You pass instances of this class to the ``webhookFilters`` property when constructing a source.

    :exampleMetadata: infused

    Example::

        git_hub_source = codebuild.Source.git_hub(
            owner="awslabs",
            repo="aws-cdk",
            webhook=True,  # optional, default: true if `webhookFilters` were provided, false otherwise
            webhook_triggers_batch_build=True,  # optional, default is false
            webhook_filters=[
                codebuild.FilterGroup.in_event_of(codebuild.EventAction.PUSH).and_branch_is("master").and_commit_message_is("the commit message")
            ]
        )
    '''

    @jsii.member(jsii_name="inEventOf")
    @builtins.classmethod
    def in_event_of(cls, *actions: EventAction) -> "FilterGroup":
        '''Creates a new event FilterGroup that triggers on any of the provided actions.

        :param actions: the actions to trigger the webhook on.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7ee82b054f2fce2cc647f54bbe392be03a653535de1e769d1bae93d96a67cf3)
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast("FilterGroup", jsii.sinvoke(cls, "inEventOf", [*actions]))

    @jsii.member(jsii_name="andActorAccountIs")
    def and_actor_account_is(self, pattern: builtins.str) -> "FilterGroup":
        '''Create a new FilterGroup with an added condition: the account ID of the actor initiating the event must match the given pattern.

        :param pattern: a regular expression.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44ae6460fccbc30ea0a21d6003515fd50ee84f033f45c8dfad1c388369610523)
            check_type(argname="argument pattern", value=pattern, expected_type=type_hints["pattern"])
        return typing.cast("FilterGroup", jsii.invoke(self, "andActorAccountIs", [pattern]))

    @jsii.member(jsii_name="andActorAccountIsNot")
    def and_actor_account_is_not(self, pattern: builtins.str) -> "FilterGroup":
        '''Create a new FilterGroup with an added condition: the account ID of the actor initiating the event must not match the given pattern.

        :param pattern: a regular expression.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55191b53117efc7c12b5109c057af34f6f4d2419adecc0e9a56cc4f3e7ded2dd)
            check_type(argname="argument pattern", value=pattern, expected_type=type_hints["pattern"])
        return typing.cast("FilterGroup", jsii.invoke(self, "andActorAccountIsNot", [pattern]))

    @jsii.member(jsii_name="andBaseBranchIs")
    def and_base_branch_is(self, branch_name: builtins.str) -> "FilterGroup":
        '''Create a new FilterGroup with an added condition: the Pull Request that is the source of the event must target the given base branch.

        Note that you cannot use this method if this Group contains the ``PUSH`` event action.

        :param branch_name: the name of the branch (can be a regular expression).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__653d6e2311acdaecb81dae0669031dceded5b465feb0dd66568202ef8f2b42f8)
            check_type(argname="argument branch_name", value=branch_name, expected_type=type_hints["branch_name"])
        return typing.cast("FilterGroup", jsii.invoke(self, "andBaseBranchIs", [branch_name]))

    @jsii.member(jsii_name="andBaseBranchIsNot")
    def and_base_branch_is_not(self, branch_name: builtins.str) -> "FilterGroup":
        '''Create a new FilterGroup with an added condition: the Pull Request that is the source of the event must not target the given base branch.

        Note that you cannot use this method if this Group contains the ``PUSH`` event action.

        :param branch_name: the name of the branch (can be a regular expression).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abbf3760f382c85794ee5de9f8ac4af08cd6ab3d95f51181b0db68d05369ec6d)
            check_type(argname="argument branch_name", value=branch_name, expected_type=type_hints["branch_name"])
        return typing.cast("FilterGroup", jsii.invoke(self, "andBaseBranchIsNot", [branch_name]))

    @jsii.member(jsii_name="andBaseRefIs")
    def and_base_ref_is(self, pattern: builtins.str) -> "FilterGroup":
        '''Create a new FilterGroup with an added condition: the Pull Request that is the source of the event must target the given Git reference.

        Note that you cannot use this method if this Group contains the ``PUSH`` event action.

        :param pattern: a regular expression.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2cd7277e86df1c85aac31dafb09d355eea7b9faa3a6eeca46a2b15ef0488626)
            check_type(argname="argument pattern", value=pattern, expected_type=type_hints["pattern"])
        return typing.cast("FilterGroup", jsii.invoke(self, "andBaseRefIs", [pattern]))

    @jsii.member(jsii_name="andBaseRefIsNot")
    def and_base_ref_is_not(self, pattern: builtins.str) -> "FilterGroup":
        '''Create a new FilterGroup with an added condition: the Pull Request that is the source of the event must not target the given Git reference.

        Note that you cannot use this method if this Group contains the ``PUSH`` event action.

        :param pattern: a regular expression.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6ffce69c3bd55d1840fc662b879bf505a627b9e256d84cdb8636575f4d393aa)
            check_type(argname="argument pattern", value=pattern, expected_type=type_hints["pattern"])
        return typing.cast("FilterGroup", jsii.invoke(self, "andBaseRefIsNot", [pattern]))

    @jsii.member(jsii_name="andBranchIs")
    def and_branch_is(self, branch_name: builtins.str) -> "FilterGroup":
        '''Create a new FilterGroup with an added condition: the event must affect the given branch.

        :param branch_name: the name of the branch (can be a regular expression).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5bcdad3cdd8e48c789c2b805b65c483668b17e2b1857ee7904e7ecdb9533cb5)
            check_type(argname="argument branch_name", value=branch_name, expected_type=type_hints["branch_name"])
        return typing.cast("FilterGroup", jsii.invoke(self, "andBranchIs", [branch_name]))

    @jsii.member(jsii_name="andBranchIsNot")
    def and_branch_is_not(self, branch_name: builtins.str) -> "FilterGroup":
        '''Create a new FilterGroup with an added condition: the event must not affect the given branch.

        :param branch_name: the name of the branch (can be a regular expression).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3111ccdb416278d9efe4937ab127207bee3d8e85669a1ee91f49451dd0ba0059)
            check_type(argname="argument branch_name", value=branch_name, expected_type=type_hints["branch_name"])
        return typing.cast("FilterGroup", jsii.invoke(self, "andBranchIsNot", [branch_name]))

    @jsii.member(jsii_name="andCommitMessageIs")
    def and_commit_message_is(self, commit_message: builtins.str) -> "FilterGroup":
        '''Create a new FilterGroup with an added condition: the event must affect a head commit with the given message.

        :param commit_message: the commit message (can be a regular expression).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57f511329729868fc5ebb70e93b8172741973d866feff96f854776da691dc8f5)
            check_type(argname="argument commit_message", value=commit_message, expected_type=type_hints["commit_message"])
        return typing.cast("FilterGroup", jsii.invoke(self, "andCommitMessageIs", [commit_message]))

    @jsii.member(jsii_name="andCommitMessageIsNot")
    def and_commit_message_is_not(self, commit_message: builtins.str) -> "FilterGroup":
        '''Create a new FilterGroup with an added condition: the event must not affect a head commit with the given message.

        :param commit_message: the commit message (can be a regular expression).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f761971cf5f12aa2fbbb02a412081fe823b847f2ead58983a83b3ffa88621fe)
            check_type(argname="argument commit_message", value=commit_message, expected_type=type_hints["commit_message"])
        return typing.cast("FilterGroup", jsii.invoke(self, "andCommitMessageIsNot", [commit_message]))

    @jsii.member(jsii_name="andFilePathIs")
    def and_file_path_is(self, pattern: builtins.str) -> "FilterGroup":
        '''Create a new FilterGroup with an added condition: the push that is the source of the event must affect a file that matches the given pattern.

        Note that you can only use this method if this Group contains only the ``PUSH`` event action,
        and only for GitHub, Bitbucket and GitHubEnterprise sources.

        :param pattern: a regular expression.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9103410499a75b4c59428ff91207730d6654a6754131dcadb6be8d18bd6900e)
            check_type(argname="argument pattern", value=pattern, expected_type=type_hints["pattern"])
        return typing.cast("FilterGroup", jsii.invoke(self, "andFilePathIs", [pattern]))

    @jsii.member(jsii_name="andFilePathIsNot")
    def and_file_path_is_not(self, pattern: builtins.str) -> "FilterGroup":
        '''Create a new FilterGroup with an added condition: the push that is the source of the event must not affect a file that matches the given pattern.

        Note that you can only use this method if this Group contains only the ``PUSH`` event action,
        and only for GitHub, Bitbucket and GitHubEnterprise sources.

        :param pattern: a regular expression.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1e46c4ca1b9a231e314b5f141efb9c7fd7c07aa396b4e47413df279ea49c8af)
            check_type(argname="argument pattern", value=pattern, expected_type=type_hints["pattern"])
        return typing.cast("FilterGroup", jsii.invoke(self, "andFilePathIsNot", [pattern]))

    @jsii.member(jsii_name="andHeadRefIs")
    def and_head_ref_is(self, pattern: builtins.str) -> "FilterGroup":
        '''Create a new FilterGroup with an added condition: the event must affect a Git reference (ie., a branch or a tag) that matches the given pattern.

        :param pattern: a regular expression.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e0f7cafebb819916109455e2daf1943bdf446f5499d0b1d3850fd79ae53fe2a)
            check_type(argname="argument pattern", value=pattern, expected_type=type_hints["pattern"])
        return typing.cast("FilterGroup", jsii.invoke(self, "andHeadRefIs", [pattern]))

    @jsii.member(jsii_name="andHeadRefIsNot")
    def and_head_ref_is_not(self, pattern: builtins.str) -> "FilterGroup":
        '''Create a new FilterGroup with an added condition: the event must not affect a Git reference (ie., a branch or a tag) that matches the given pattern.

        :param pattern: a regular expression.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8360327b95f000e04f1be92da1cbb309e7cbc121d5b99e1c63d2ca370b07e59)
            check_type(argname="argument pattern", value=pattern, expected_type=type_hints["pattern"])
        return typing.cast("FilterGroup", jsii.invoke(self, "andHeadRefIsNot", [pattern]))

    @jsii.member(jsii_name="andTagIs")
    def and_tag_is(self, tag_name: builtins.str) -> "FilterGroup":
        '''Create a new FilterGroup with an added condition: the event must affect the given tag.

        :param tag_name: the name of the tag (can be a regular expression).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23fefd45e9bb8c9a0e96ee10e6e55d42bcc040adef67dc6e8d36835d94b9c1e0)
            check_type(argname="argument tag_name", value=tag_name, expected_type=type_hints["tag_name"])
        return typing.cast("FilterGroup", jsii.invoke(self, "andTagIs", [tag_name]))

    @jsii.member(jsii_name="andTagIsNot")
    def and_tag_is_not(self, tag_name: builtins.str) -> "FilterGroup":
        '''Create a new FilterGroup with an added condition: the event must not affect the given tag.

        :param tag_name: the name of the tag (can be a regular expression).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebe4b0a2b94a8430bdc8d5f74476e00ebee6feee0cc7370440becbc1d4ea8294)
            check_type(argname="argument tag_name", value=tag_name, expected_type=type_hints["tag_name"])
        return typing.cast("FilterGroup", jsii.invoke(self, "andTagIsNot", [tag_name]))


class GitHubEnterpriseSourceCredentials(
    _aws_cdk_core_f4b25747.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.GitHubEnterpriseSourceCredentials",
):
    '''The source credentials used when contacting the GitHub Enterprise API.

    **Note**: CodeBuild only allows a single credential for GitHub Enterprise
    to be saved in a given AWS account in a given region -
    any attempt to add more than one will result in an error.

    :resource: AWS::CodeBuild::SourceCredential
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_codebuild as codebuild
        import aws_cdk.core as cdk
        
        # secret_value: cdk.SecretValue
        
        git_hub_enterprise_source_credentials = codebuild.GitHubEnterpriseSourceCredentials(self, "MyGitHubEnterpriseSourceCredentials",
            access_token=secret_value
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        access_token: _aws_cdk_core_f4b25747.SecretValue,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param access_token: The personal access token to use when contacting the instance of the GitHub Enterprise API.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaba559d5ff242aad31285cd81284e9acac6adafddba92970cda887bb9db9077)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GitHubEnterpriseSourceCredentialsProps(access_token=access_token)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.GitHubEnterpriseSourceCredentialsProps",
    jsii_struct_bases=[],
    name_mapping={"access_token": "accessToken"},
)
class GitHubEnterpriseSourceCredentialsProps:
    def __init__(self, *, access_token: _aws_cdk_core_f4b25747.SecretValue) -> None:
        '''Creation properties for {@link GitHubEnterpriseSourceCredentials}.

        :param access_token: The personal access token to use when contacting the instance of the GitHub Enterprise API.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            import aws_cdk.core as cdk
            
            # secret_value: cdk.SecretValue
            
            git_hub_enterprise_source_credentials_props = codebuild.GitHubEnterpriseSourceCredentialsProps(
                access_token=secret_value
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a89edebfa59b0fd006e159d4293d16316c461501494085514c70e11ad15c368)
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_token": access_token,
        }

    @builtins.property
    def access_token(self) -> _aws_cdk_core_f4b25747.SecretValue:
        '''The personal access token to use when contacting the instance of the GitHub Enterprise API.'''
        result = self._values.get("access_token")
        assert result is not None, "Required property 'access_token' is missing"
        return typing.cast(_aws_cdk_core_f4b25747.SecretValue, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubEnterpriseSourceCredentialsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GitHubSourceCredentials(
    _aws_cdk_core_f4b25747.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.GitHubSourceCredentials",
):
    '''The source credentials used when contacting the GitHub API.

    **Note**: CodeBuild only allows a single credential for GitHub
    to be saved in a given AWS account in a given region -
    any attempt to add more than one will result in an error.

    :resource: AWS::CodeBuild::SourceCredential
    :exampleMetadata: infused

    Example::

        codebuild.GitHubSourceCredentials(self, "CodeBuildGitHubCreds",
            access_token=SecretValue.secrets_manager("my-token")
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        access_token: _aws_cdk_core_f4b25747.SecretValue,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param access_token: The personal access token to use when contacting the GitHub API.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f89c04c069698072dd828c8e1e2aa73b7ad9465f77b05b61d67b2a3b38e934b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GitHubSourceCredentialsProps(access_token=access_token)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.GitHubSourceCredentialsProps",
    jsii_struct_bases=[],
    name_mapping={"access_token": "accessToken"},
)
class GitHubSourceCredentialsProps:
    def __init__(self, *, access_token: _aws_cdk_core_f4b25747.SecretValue) -> None:
        '''Creation properties for {@link GitHubSourceCredentials}.

        :param access_token: The personal access token to use when contacting the GitHub API.

        :exampleMetadata: infused

        Example::

            codebuild.GitHubSourceCredentials(self, "CodeBuildGitHubCreds",
                access_token=SecretValue.secrets_manager("my-token")
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6f904a96c0298f8cae335aab69e03df4d048c91c4948db12e1f8cf9937c150c)
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_token": access_token,
        }

    @builtins.property
    def access_token(self) -> _aws_cdk_core_f4b25747.SecretValue:
        '''The personal access token to use when contacting the GitHub API.'''
        result = self._values.get("access_token")
        assert result is not None, "Required property 'access_token' is missing"
        return typing.cast(_aws_cdk_core_f4b25747.SecretValue, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubSourceCredentialsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-codebuild.IArtifacts")
class IArtifacts(typing_extensions.Protocol):
    '''The abstract interface of a CodeBuild build output.

    Implemented by {@link Artifacts}.
    '''

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''The CodeBuild type of this artifact.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="identifier")
    def identifier(self) -> typing.Optional[builtins.str]:
        '''The artifact identifier.

        This property is required on secondary artifacts.
        '''
        ...

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        project: "IProject",
    ) -> ArtifactsConfig:
        '''Callback when an Artifacts class is used in a CodeBuild Project.

        :param scope: a root Construct that allows creating new Constructs.
        :param project: the Project this Artifacts is used in.
        '''
        ...


class _IArtifactsProxy:
    '''The abstract interface of a CodeBuild build output.

    Implemented by {@link Artifacts}.
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-codebuild.IArtifacts"

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''The CodeBuild type of this artifact.'''
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="identifier")
    def identifier(self) -> typing.Optional[builtins.str]:
        '''The artifact identifier.

        This property is required on secondary artifacts.
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identifier"))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        project: "IProject",
    ) -> ArtifactsConfig:
        '''Callback when an Artifacts class is used in a CodeBuild Project.

        :param scope: a root Construct that allows creating new Constructs.
        :param project: the Project this Artifacts is used in.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__888f30ad13bd42579be3737723c20534ee72000800799d07145ec29b934fac19)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        return typing.cast(ArtifactsConfig, jsii.invoke(self, "bind", [scope, project]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IArtifacts).__jsii_proxy_class__ = lambda : _IArtifactsProxy


@jsii.interface(jsii_type="@aws-cdk/aws-codebuild.IBuildImage")
class IBuildImage(typing_extensions.Protocol):
    '''Represents a Docker image used for the CodeBuild Project builds.

    Use the concrete subclasses, either:
    {@link LinuxBuildImage} or {@link WindowsBuildImage}.
    '''

    @builtins.property
    @jsii.member(jsii_name="defaultComputeType")
    def default_compute_type(self) -> ComputeType:
        '''The default {@link ComputeType} to use with this image, if one was not specified in {@link BuildEnvironment#computeType} explicitly.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> builtins.str:
        '''The Docker image identifier that the build environment uses.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-available.html
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''The type of build environment.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="imagePullPrincipalType")
    def image_pull_principal_type(self) -> typing.Optional["ImagePullPrincipalType"]:
        '''The type of principal that CodeBuild will use to pull this build Docker image.

        :default: ImagePullPrincipalType.SERVICE_ROLE
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="repository")
    def repository(self) -> typing.Optional[_aws_cdk_aws_ecr_093ed842.IRepository]:
        '''An optional ECR repository that the image is hosted in.

        :default: no repository
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="secretsManagerCredentials")
    def secrets_manager_credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_72af8d6f.ISecret]:
        '''The secretsManagerCredentials for access to a private registry.

        :default: no credentials will be used
        '''
        ...

    @jsii.member(jsii_name="runScriptBuildspec")
    def run_script_buildspec(self, entrypoint: builtins.str) -> BuildSpec:
        '''Make a buildspec to run the indicated script.

        :param entrypoint: -
        '''
        ...

    @jsii.member(jsii_name="validate")
    def validate(
        self,
        *,
        build_image: typing.Optional["IBuildImage"] = None,
        certificate: typing.Optional[typing.Union[BuildEnvironmentCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
        compute_type: typing.Optional[ComputeType] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
        privileged: typing.Optional[builtins.bool] = None,
    ) -> typing.List[builtins.str]:
        '''Allows the image a chance to validate whether the passed configuration is correct.

        :param build_image: The image used for the builds. Default: LinuxBuildImage.STANDARD_1_0
        :param certificate: The location of the PEM-encoded certificate for the build project. Default: - No external certificate is added to the project
        :param compute_type: The type of compute to use for this build. See the {@link ComputeType} enum for the possible values. Default: taken from {@link #buildImage#defaultComputeType}
        :param environment_variables: The environment variables that your builds can use.
        :param privileged: Indicates how the project builds Docker images. Specify true to enable running the Docker daemon inside a Docker container. This value must be set to true only if this build project will be used to build Docker images, and the specified build environment image is not one provided by AWS CodeBuild with Docker support. Otherwise, all associated builds that attempt to interact with the Docker daemon will fail. Default: false
        '''
        ...


class _IBuildImageProxy:
    '''Represents a Docker image used for the CodeBuild Project builds.

    Use the concrete subclasses, either:
    {@link LinuxBuildImage} or {@link WindowsBuildImage}.
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-codebuild.IBuildImage"

    @builtins.property
    @jsii.member(jsii_name="defaultComputeType")
    def default_compute_type(self) -> ComputeType:
        '''The default {@link ComputeType} to use with this image, if one was not specified in {@link BuildEnvironment#computeType} explicitly.'''
        return typing.cast(ComputeType, jsii.get(self, "defaultComputeType"))

    @builtins.property
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> builtins.str:
        '''The Docker image identifier that the build environment uses.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-available.html
        '''
        return typing.cast(builtins.str, jsii.get(self, "imageId"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''The type of build environment.'''
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="imagePullPrincipalType")
    def image_pull_principal_type(self) -> typing.Optional["ImagePullPrincipalType"]:
        '''The type of principal that CodeBuild will use to pull this build Docker image.

        :default: ImagePullPrincipalType.SERVICE_ROLE
        '''
        return typing.cast(typing.Optional["ImagePullPrincipalType"], jsii.get(self, "imagePullPrincipalType"))

    @builtins.property
    @jsii.member(jsii_name="repository")
    def repository(self) -> typing.Optional[_aws_cdk_aws_ecr_093ed842.IRepository]:
        '''An optional ECR repository that the image is hosted in.

        :default: no repository
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_ecr_093ed842.IRepository], jsii.get(self, "repository"))

    @builtins.property
    @jsii.member(jsii_name="secretsManagerCredentials")
    def secrets_manager_credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_72af8d6f.ISecret]:
        '''The secretsManagerCredentials for access to a private registry.

        :default: no credentials will be used
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_72af8d6f.ISecret], jsii.get(self, "secretsManagerCredentials"))

    @jsii.member(jsii_name="runScriptBuildspec")
    def run_script_buildspec(self, entrypoint: builtins.str) -> BuildSpec:
        '''Make a buildspec to run the indicated script.

        :param entrypoint: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0846aa90e32428976ac8e211ae813855c25ca5693497ba30491399a7ba2b51c9)
            check_type(argname="argument entrypoint", value=entrypoint, expected_type=type_hints["entrypoint"])
        return typing.cast(BuildSpec, jsii.invoke(self, "runScriptBuildspec", [entrypoint]))

    @jsii.member(jsii_name="validate")
    def validate(
        self,
        *,
        build_image: typing.Optional[IBuildImage] = None,
        certificate: typing.Optional[typing.Union[BuildEnvironmentCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
        compute_type: typing.Optional[ComputeType] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
        privileged: typing.Optional[builtins.bool] = None,
    ) -> typing.List[builtins.str]:
        '''Allows the image a chance to validate whether the passed configuration is correct.

        :param build_image: The image used for the builds. Default: LinuxBuildImage.STANDARD_1_0
        :param certificate: The location of the PEM-encoded certificate for the build project. Default: - No external certificate is added to the project
        :param compute_type: The type of compute to use for this build. See the {@link ComputeType} enum for the possible values. Default: taken from {@link #buildImage#defaultComputeType}
        :param environment_variables: The environment variables that your builds can use.
        :param privileged: Indicates how the project builds Docker images. Specify true to enable running the Docker daemon inside a Docker container. This value must be set to true only if this build project will be used to build Docker images, and the specified build environment image is not one provided by AWS CodeBuild with Docker support. Otherwise, all associated builds that attempt to interact with the Docker daemon will fail. Default: false
        '''
        build_environment = BuildEnvironment(
            build_image=build_image,
            certificate=certificate,
            compute_type=compute_type,
            environment_variables=environment_variables,
            privileged=privileged,
        )

        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "validate", [build_environment]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBuildImage).__jsii_proxy_class__ = lambda : _IBuildImageProxy


@jsii.interface(jsii_type="@aws-cdk/aws-codebuild.IFileSystemLocation")
class IFileSystemLocation(typing_extensions.Protocol):
    '''The interface of a CodeBuild FileSystemLocation.

    Implemented by {@link EfsFileSystemLocation}.
    '''

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        project: "IProject",
    ) -> FileSystemConfig:
        '''Called by the project when a file system is added so it can perform binding operations on this file system location.

        :param scope: -
        :param project: -
        '''
        ...


class _IFileSystemLocationProxy:
    '''The interface of a CodeBuild FileSystemLocation.

    Implemented by {@link EfsFileSystemLocation}.
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-codebuild.IFileSystemLocation"

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        project: "IProject",
    ) -> FileSystemConfig:
        '''Called by the project when a file system is added so it can perform binding operations on this file system location.

        :param scope: -
        :param project: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df7b1cf51ae3dbacd0e0a8d3f6fae2139ecfa80b56998de22f2ef3f219fbce59)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        return typing.cast(FileSystemConfig, jsii.invoke(self, "bind", [scope, project]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IFileSystemLocation).__jsii_proxy_class__ = lambda : _IFileSystemLocationProxy


@jsii.interface(jsii_type="@aws-cdk/aws-codebuild.IProject")
class IProject(
    _aws_cdk_core_f4b25747.IResource,
    _aws_cdk_aws_iam_940a1ce0.IGrantable,
    _aws_cdk_aws_ec2_67de8e8d.IConnectable,
    _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleSource,
    typing_extensions.Protocol,
):
    @builtins.property
    @jsii.member(jsii_name="projectArn")
    def project_arn(self) -> builtins.str:
        '''The ARN of this Project.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="projectName")
    def project_name(self) -> builtins.str:
        '''The human-visible name of this Project.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole]:
        '''The IAM service Role of this Project.

        Undefined for imported Projects.
        '''
        ...

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(
        self,
        policy_statement: _aws_cdk_aws_iam_940a1ce0.PolicyStatement,
    ) -> None:
        '''
        :param policy_statement: -
        '''
        ...

    @jsii.member(jsii_name="enableBatchBuilds")
    def enable_batch_builds(self) -> typing.Optional[BatchBuildConfig]:
        '''Enable batch builds.

        Returns an object contining the batch service role if batch builds
        could be enabled.
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
        '''
        :param metric_name: The name of the metric.
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :return: a CloudWatch metric associated with this build project.
        '''
        ...

    @jsii.member(jsii_name="metricBuilds")
    def metric_builds(
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
        '''Measures the number of builds triggered.

        Units: Count

        Valid CloudWatch statistics: Sum

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

    @jsii.member(jsii_name="metricDuration")
    def metric_duration(
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
        '''Measures the duration of all builds over time.

        Units: Seconds

        Valid CloudWatch statistics: Average (recommended), Maximum, Minimum

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
        ...

    @jsii.member(jsii_name="metricFailedBuilds")
    def metric_failed_builds(
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
        '''Measures the number of builds that failed because of client error or because of a timeout.

        Units: Count

        Valid CloudWatch statistics: Sum

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

    @jsii.member(jsii_name="metricSucceededBuilds")
    def metric_succeeded_builds(
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
        '''Measures the number of successful builds.

        Units: Count

        Valid CloudWatch statistics: Sum

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

    @jsii.member(jsii_name="notifyOn")
    def notify_on(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        events: typing.Sequence["ProjectNotificationEvents"],
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule triggered when the project events emitted by you specified, it very similar to ``onEvent`` API.

        You can also use the methods ``notifyOnBuildSucceeded`` and
        ``notifyOnBuildFailed`` to define rules for these specific event emitted.

        :param id: The logical identifier of the CodeStar Notifications rule that will be created.
        :param target: The target to register for the CodeStar Notifications destination.
        :param events: A list of event types associated with this notification rule for CodeBuild Project. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :return: CodeStar Notifications rule associated with this build project.
        '''
        ...

    @jsii.member(jsii_name="notifyOnBuildFailed")
    def notify_on_build_failed(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar notification rule which triggers when a build fails.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        ...

    @jsii.member(jsii_name="notifyOnBuildSucceeded")
    def notify_on_build_succeeded(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar notification rule which triggers when a build completes successfully.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        ...

    @jsii.member(jsii_name="onBuildFailed")
    def on_build_failed(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines an event rule which triggers when a build fails.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        ...

    @jsii.member(jsii_name="onBuildStarted")
    def on_build_started(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines an event rule which triggers when a build starts.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        ...

    @jsii.member(jsii_name="onBuildSucceeded")
    def on_build_succeeded(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines an event rule which triggers when a build completes successfully.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        ...

    @jsii.member(jsii_name="onEvent")
    def on_event(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule triggered when something happens with this project.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        '''
        ...

    @jsii.member(jsii_name="onPhaseChange")
    def on_phase_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule that triggers upon phase change of this build project.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        '''
        ...

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule triggered when the build project state changes.

        You can filter specific build status events using an event
        pattern filter on the ``build-status`` detail field::

           const rule = project.onStateChange('OnBuildStarted', { target });
           rule.addEventPattern({
             detail: {
               'build-status': [
                 "IN_PROGRESS",
                 "SUCCEEDED",
                 "FAILED",
                 "STOPPED"
               ]
             }
           });

        You can also use the methods ``onBuildFailed`` and ``onBuildSucceeded`` to define rules for
        these specific state changes.

        To access fields from the event in the event target input,
        use the static fields on the ``StateChangeEvent`` class.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        '''
        ...


class _IProjectProxy(
    jsii.proxy_for(_aws_cdk_core_f4b25747.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_iam_940a1ce0.IGrantable), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_ec2_67de8e8d.IConnectable), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleSource), # type: ignore[misc]
):
    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-codebuild.IProject"

    @builtins.property
    @jsii.member(jsii_name="projectArn")
    def project_arn(self) -> builtins.str:
        '''The ARN of this Project.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "projectArn"))

    @builtins.property
    @jsii.member(jsii_name="projectName")
    def project_name(self) -> builtins.str:
        '''The human-visible name of this Project.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "projectName"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole]:
        '''The IAM service Role of this Project.

        Undefined for imported Projects.
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole], jsii.get(self, "role"))

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(
        self,
        policy_statement: _aws_cdk_aws_iam_940a1ce0.PolicyStatement,
    ) -> None:
        '''
        :param policy_statement: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75f64ef9b5ef16e4579d9a51586f4308efa27b6f21db52c991c31e8f73875598)
            check_type(argname="argument policy_statement", value=policy_statement, expected_type=type_hints["policy_statement"])
        return typing.cast(None, jsii.invoke(self, "addToRolePolicy", [policy_statement]))

    @jsii.member(jsii_name="enableBatchBuilds")
    def enable_batch_builds(self) -> typing.Optional[BatchBuildConfig]:
        '''Enable batch builds.

        Returns an object contining the batch service role if batch builds
        could be enabled.
        '''
        return typing.cast(typing.Optional[BatchBuildConfig], jsii.invoke(self, "enableBatchBuilds", []))

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
        '''
        :param metric_name: The name of the metric.
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :return: a CloudWatch metric associated with this build project.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85c8dd9ecb6dc3a9d962873c457341a93f043113cdec431955ea1967f988fc8c)
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

    @jsii.member(jsii_name="metricBuilds")
    def metric_builds(
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
        '''Measures the number of builds triggered.

        Units: Count

        Valid CloudWatch statistics: Sum

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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricBuilds", [props]))

    @jsii.member(jsii_name="metricDuration")
    def metric_duration(
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
        '''Measures the duration of all builds over time.

        Units: Seconds

        Valid CloudWatch statistics: Average (recommended), Maximum, Minimum

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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricDuration", [props]))

    @jsii.member(jsii_name="metricFailedBuilds")
    def metric_failed_builds(
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
        '''Measures the number of builds that failed because of client error or because of a timeout.

        Units: Count

        Valid CloudWatch statistics: Sum

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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricFailedBuilds", [props]))

    @jsii.member(jsii_name="metricSucceededBuilds")
    def metric_succeeded_builds(
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
        '''Measures the number of successful builds.

        Units: Count

        Valid CloudWatch statistics: Sum

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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricSucceededBuilds", [props]))

    @jsii.member(jsii_name="notifyOn")
    def notify_on(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        events: typing.Sequence["ProjectNotificationEvents"],
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule triggered when the project events emitted by you specified, it very similar to ``onEvent`` API.

        You can also use the methods ``notifyOnBuildSucceeded`` and
        ``notifyOnBuildFailed`` to define rules for these specific event emitted.

        :param id: The logical identifier of the CodeStar Notifications rule that will be created.
        :param target: The target to register for the CodeStar Notifications destination.
        :param events: A list of event types associated with this notification rule for CodeBuild Project. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :return: CodeStar Notifications rule associated with this build project.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0056666a08cbecc480a9fd20b36ae0b1ec37ccd2c381ee950cb1b1716fbac89)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = ProjectNotifyOnOptions(
            events=events,
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOn", [id, target, options]))

    @jsii.member(jsii_name="notifyOnBuildFailed")
    def notify_on_build_failed(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar notification rule which triggers when a build fails.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae7a9e862730271ceeac0a6fe693002cc4babb21ae8a8ae932a9b14216c25a47)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnBuildFailed", [id, target, options]))

    @jsii.member(jsii_name="notifyOnBuildSucceeded")
    def notify_on_build_succeeded(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar notification rule which triggers when a build completes successfully.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9eb1ed5290183f0adb4b653e5802170dc8e4cdbbe69df28502502da11591ffa)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnBuildSucceeded", [id, target, options]))

    @jsii.member(jsii_name="onBuildFailed")
    def on_build_failed(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines an event rule which triggers when a build fails.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2aefc247d3c8675ae991646fe2ff7aa138ee5c918989b3a3095edf6a431ddfa7)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onBuildFailed", [id, options]))

    @jsii.member(jsii_name="onBuildStarted")
    def on_build_started(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines an event rule which triggers when a build starts.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d60f36597d4a8e107a6f406127fbeffc6ab0d51cd6883da6a0ea0602d33b923)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onBuildStarted", [id, options]))

    @jsii.member(jsii_name="onBuildSucceeded")
    def on_build_succeeded(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines an event rule which triggers when a build completes successfully.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04f52587407f3580295d095b951259b443e8f2ed305d418a55260dd70a336ba1)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onBuildSucceeded", [id, options]))

    @jsii.member(jsii_name="onEvent")
    def on_event(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule triggered when something happens with this project.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2dd7b02f58e88b3858339f17ce861de9b54f361073efdc2245f0d57d9b1286e2)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onEvent", [id, options]))

    @jsii.member(jsii_name="onPhaseChange")
    def on_phase_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule that triggers upon phase change of this build project.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6983aeb56e3c2be1ff14062d5d3b0c80295e2581d0a4c84f7577ecd9688f4e0c)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onPhaseChange", [id, options]))

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule triggered when the build project state changes.

        You can filter specific build status events using an event
        pattern filter on the ``build-status`` detail field::

           const rule = project.onStateChange('OnBuildStarted', { target });
           rule.addEventPattern({
             detail: {
               'build-status': [
                 "IN_PROGRESS",
                 "SUCCEEDED",
                 "FAILED",
                 "STOPPED"
               ]
             }
           });

        You can also use the methods ``onBuildFailed`` and ``onBuildSucceeded`` to define rules for
        these specific state changes.

        To access fields from the event in the event target input,
        use the static fields on the ``StateChangeEvent`` class.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e5bd333832fcb44f7aadd0b4368185187212849efa6d526c6f8365dcbb8b309)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onStateChange", [id, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IProject).__jsii_proxy_class__ = lambda : _IProjectProxy


@jsii.interface(jsii_type="@aws-cdk/aws-codebuild.IReportGroup")
class IReportGroup(_aws_cdk_core_f4b25747.IResource, typing_extensions.Protocol):
    '''The interface representing the ReportGroup resource - either an existing one, imported using the {@link ReportGroup.fromReportGroupName} method, or a new one, created with the {@link ReportGroup} class.'''

    @builtins.property
    @jsii.member(jsii_name="reportGroupArn")
    def report_group_arn(self) -> builtins.str:
        '''The ARN of the ReportGroup.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="reportGroupName")
    def report_group_name(self) -> builtins.str:
        '''The name of the ReportGroup.

        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="grantWrite")
    def grant_write(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grants the given entity permissions to write (that is, upload reports to) this report group.

        :param identity: -
        '''
        ...


class _IReportGroupProxy(
    jsii.proxy_for(_aws_cdk_core_f4b25747.IResource), # type: ignore[misc]
):
    '''The interface representing the ReportGroup resource - either an existing one, imported using the {@link ReportGroup.fromReportGroupName} method, or a new one, created with the {@link ReportGroup} class.'''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-codebuild.IReportGroup"

    @builtins.property
    @jsii.member(jsii_name="reportGroupArn")
    def report_group_arn(self) -> builtins.str:
        '''The ARN of the ReportGroup.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "reportGroupArn"))

    @builtins.property
    @jsii.member(jsii_name="reportGroupName")
    def report_group_name(self) -> builtins.str:
        '''The name of the ReportGroup.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "reportGroupName"))

    @jsii.member(jsii_name="grantWrite")
    def grant_write(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grants the given entity permissions to write (that is, upload reports to) this report group.

        :param identity: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a31943eaf7fe844ca3848f12ee3bb5c5b85db65e1fd3f413e9bbde0dda720ad9)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantWrite", [identity]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IReportGroup).__jsii_proxy_class__ = lambda : _IReportGroupProxy


@jsii.interface(jsii_type="@aws-cdk/aws-codebuild.ISource")
class ISource(typing_extensions.Protocol):
    '''The abstract interface of a CodeBuild source.

    Implemented by {@link Source}.
    '''

    @builtins.property
    @jsii.member(jsii_name="badgeSupported")
    def badge_supported(self) -> builtins.bool:
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        ...

    @builtins.property
    @jsii.member(jsii_name="identifier")
    def identifier(self) -> typing.Optional[builtins.str]:
        ...

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        project: IProject,
    ) -> "SourceConfig":
        '''
        :param scope: -
        :param project: -
        '''
        ...


class _ISourceProxy:
    '''The abstract interface of a CodeBuild source.

    Implemented by {@link Source}.
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-codebuild.ISource"

    @builtins.property
    @jsii.member(jsii_name="badgeSupported")
    def badge_supported(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "badgeSupported"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="identifier")
    def identifier(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identifier"))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        project: IProject,
    ) -> "SourceConfig":
        '''
        :param scope: -
        :param project: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d1a30f0166cbcb4fbfe707342fd63a4fdbea160461b56ca074fc85c3c63146e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        return typing.cast("SourceConfig", jsii.invoke(self, "bind", [scope, project]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISource).__jsii_proxy_class__ = lambda : _ISourceProxy


@jsii.enum(jsii_type="@aws-cdk/aws-codebuild.ImagePullPrincipalType")
class ImagePullPrincipalType(enum.Enum):
    '''The type of principal CodeBuild will use to pull your build Docker image.'''

    CODEBUILD = "CODEBUILD"
    '''CODEBUILD specifies that CodeBuild uses its own identity when pulling the image.

    This means the resource policy of the ECR repository that hosts the image will be modified to trust
    CodeBuild's service principal.
    This is the required principal type when using CodeBuild's pre-defined images.
    '''
    SERVICE_ROLE = "SERVICE_ROLE"
    '''SERVICE_ROLE specifies that AWS CodeBuild uses the project's role when pulling the image.

    The role will be granted pull permissions on the ECR repository hosting the image.
    '''


@jsii.implements(IBuildImage)
class LinuxArmBuildImage(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.LinuxArmBuildImage",
):
    '''A CodeBuild image running aarch64 Linux.

    This class has a bunch of public constants that represent the CodeBuild ARM images.

    You can also specify a custom image using the static method:

    - LinuxBuildImage.fromEcrRepository(repo[, tag])

    :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-available.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_codebuild as codebuild
        
        linux_arm_build_image = codebuild.LinuxArmBuildImage.from_code_build_image_id("id")
    '''

    @jsii.member(jsii_name="fromCodeBuildImageId")
    @builtins.classmethod
    def from_code_build_image_id(cls, id: builtins.str) -> IBuildImage:
        '''Uses a Docker image provided by CodeBuild.

        :param id: The image identifier.

        :return: A Docker image provided by CodeBuild.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-available.html

        Example::

            "aws/codebuild/amazonlinux2-aarch64-standard:1.0"
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf04d8b43fd1ffcdcedd8d4bb415c3067621c08332ef9fc7f697f4a8f4560687)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(IBuildImage, jsii.sinvoke(cls, "fromCodeBuildImageId", [id]))

    @jsii.member(jsii_name="fromEcrRepository")
    @builtins.classmethod
    def from_ecr_repository(
        cls,
        repository: _aws_cdk_aws_ecr_093ed842.IRepository,
        tag_or_digest: typing.Optional[builtins.str] = None,
    ) -> IBuildImage:
        '''Returns an ARM image running Linux from an ECR repository.

        NOTE: if the repository is external (i.e. imported), then we won't be able to add
        a resource policy statement for it so CodeBuild can pull the image.

        :param repository: The ECR repository.
        :param tag_or_digest: Image tag or digest (default "latest", digests must start with ``sha256:``).

        :return: An aarch64 Linux build image from an ECR repository.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-ecr.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69e742a6a9b5c1454d5aa47beca071723e16d1cd0a1990efa3a3d332f29a9927)
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument tag_or_digest", value=tag_or_digest, expected_type=type_hints["tag_or_digest"])
        return typing.cast(IBuildImage, jsii.sinvoke(cls, "fromEcrRepository", [repository, tag_or_digest]))

    @jsii.member(jsii_name="runScriptBuildspec")
    def run_script_buildspec(self, entrypoint: builtins.str) -> BuildSpec:
        '''Make a buildspec to run the indicated script.

        :param entrypoint: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b8de24993e2603ae59c2d5be2e8cbc515642de724ad670445d3ca5b3e32a292)
            check_type(argname="argument entrypoint", value=entrypoint, expected_type=type_hints["entrypoint"])
        return typing.cast(BuildSpec, jsii.invoke(self, "runScriptBuildspec", [entrypoint]))

    @jsii.member(jsii_name="validate")
    def validate(
        self,
        *,
        build_image: typing.Optional[IBuildImage] = None,
        certificate: typing.Optional[typing.Union[BuildEnvironmentCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
        compute_type: typing.Optional[ComputeType] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
        privileged: typing.Optional[builtins.bool] = None,
    ) -> typing.List[builtins.str]:
        '''Validates by checking the BuildEnvironment computeType as aarch64 images only support ComputeType.SMALL and ComputeType.LARGE.

        :param build_image: The image used for the builds. Default: LinuxBuildImage.STANDARD_1_0
        :param certificate: The location of the PEM-encoded certificate for the build project. Default: - No external certificate is added to the project
        :param compute_type: The type of compute to use for this build. See the {@link ComputeType} enum for the possible values. Default: taken from {@link #buildImage#defaultComputeType}
        :param environment_variables: The environment variables that your builds can use.
        :param privileged: Indicates how the project builds Docker images. Specify true to enable running the Docker daemon inside a Docker container. This value must be set to true only if this build project will be used to build Docker images, and the specified build environment image is not one provided by AWS CodeBuild with Docker support. Otherwise, all associated builds that attempt to interact with the Docker daemon will fail. Default: false
        '''
        build_environment = BuildEnvironment(
            build_image=build_image,
            certificate=certificate,
            compute_type=compute_type,
            environment_variables=environment_variables,
            privileged=privileged,
        )

        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "validate", [build_environment]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LINUX_2_STANDARD_1_0")
    def AMAZON_LINUX_2_STANDARD_1_0(cls) -> IBuildImage:
        '''Image "aws/codebuild/amazonlinux2-aarch64-standard:1.0".'''
        return typing.cast(IBuildImage, jsii.sget(cls, "AMAZON_LINUX_2_STANDARD_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LINUX_2_STANDARD_2_0")
    def AMAZON_LINUX_2_STANDARD_2_0(cls) -> IBuildImage:
        '''Image "aws/codebuild/amazonlinux2-aarch64-standard:2.0".'''
        return typing.cast(IBuildImage, jsii.sget(cls, "AMAZON_LINUX_2_STANDARD_2_0"))

    @builtins.property
    @jsii.member(jsii_name="defaultComputeType")
    def default_compute_type(self) -> ComputeType:
        '''The default {@link ComputeType} to use with this image, if one was not specified in {@link BuildEnvironment#computeType} explicitly.'''
        return typing.cast(ComputeType, jsii.get(self, "defaultComputeType"))

    @builtins.property
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> builtins.str:
        '''The Docker image identifier that the build environment uses.'''
        return typing.cast(builtins.str, jsii.get(self, "imageId"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''The type of build environment.'''
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="imagePullPrincipalType")
    def image_pull_principal_type(self) -> typing.Optional[ImagePullPrincipalType]:
        '''The type of principal that CodeBuild will use to pull this build Docker image.'''
        return typing.cast(typing.Optional[ImagePullPrincipalType], jsii.get(self, "imagePullPrincipalType"))

    @builtins.property
    @jsii.member(jsii_name="repository")
    def repository(self) -> typing.Optional[_aws_cdk_aws_ecr_093ed842.IRepository]:
        '''An optional ECR repository that the image is hosted in.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ecr_093ed842.IRepository], jsii.get(self, "repository"))

    @builtins.property
    @jsii.member(jsii_name="secretsManagerCredentials")
    def secrets_manager_credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_72af8d6f.ISecret]:
        '''The secretsManagerCredentials for access to a private registry.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_72af8d6f.ISecret], jsii.get(self, "secretsManagerCredentials"))


@jsii.implements(IBuildImage)
class LinuxBuildImage(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.LinuxBuildImage",
):
    '''A CodeBuild image running x86-64 Linux.

    This class has a bunch of public constants that represent the most popular images.

    You can also specify a custom image using one of the static methods:

    - LinuxBuildImage.fromDockerRegistry(image[, { secretsManagerCredentials }])
    - LinuxBuildImage.fromEcrRepository(repo[, tag])
    - LinuxBuildImage.fromAsset(parent, id, props)

    :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-available.html
    :exampleMetadata: infused

    Example::

        pipeline = pipelines.CodePipeline(self, "Pipeline",
            synth=pipelines.ShellStep("Synth",
                input=pipelines.CodePipelineSource.connection("my-org/my-app", "main",
                    connection_arn="arn:aws:codestar-connections:us-east-1:222222222222:connection/7d2469ff-514a-4e4f-9003-5ca4a43cdc41"
                ),
                commands=["npm ci", "npm run build", "npx cdk synth"]
            ),
        
            # Turn this on because the pipeline uses Docker image assets
            docker_enabled_for_self_mutation=True
        )
        
        pipeline.add_wave("MyWave",
            post=[
                pipelines.CodeBuildStep("RunApproval",
                    commands=["command-from-image"],
                    build_environment=codebuild.BuildEnvironment(
                        # The user of a Docker image asset in the pipeline requires turning on
                        # 'dockerEnabledForSelfMutation'.
                        build_image=codebuild.LinuxBuildImage.from_asset(self, "Image",
                            directory="./docker-image"
                        )
                    )
                )
            ]
        )
    '''

    @jsii.member(jsii_name="fromAsset")
    @builtins.classmethod
    def from_asset(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        directory: builtins.str,
        build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        file: typing.Optional[builtins.str] = None,
        invalidation: typing.Optional[typing.Union[_aws_cdk_aws_ecr_assets_ef09b699.DockerImageAssetInvalidationOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        network_mode: typing.Optional[_aws_cdk_aws_ecr_assets_ef09b699.NetworkMode] = None,
        platform: typing.Optional[_aws_cdk_aws_ecr_assets_ef09b699.Platform] = None,
        repository_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
        extra_hash: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow: typing.Optional[_aws_cdk_assets_b1c45fb6.FollowMode] = None,
        ignore_mode: typing.Optional[_aws_cdk_core_f4b25747.IgnoreMode] = None,
        follow_symlinks: typing.Optional[_aws_cdk_core_f4b25747.SymlinkFollowMode] = None,
    ) -> IBuildImage:
        '''Uses an Docker image asset as a x86-64 Linux build image.

        :param scope: -
        :param id: -
        :param directory: The directory where the Dockerfile is stored. Any directory inside with a name that matches the CDK output folder (cdk.out by default) will be excluded from the asset
        :param build_args: Build args to pass to the ``docker build`` command. Since Docker build arguments are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Default: - no build args are passed
        :param file: Path to the Dockerfile (relative to the directory). Default: 'Dockerfile'
        :param invalidation: Options to control which parameters are used to invalidate the asset hash. Default: - hash all parameters
        :param network_mode: Networking mode for the RUN commands during build. Support docker API 1.25+. Default: - no networking mode specified (the default networking mode ``NetworkMode.DEFAULT`` will be used)
        :param platform: Platform to build for. *Requires Docker Buildx*. Default: - no platform specified (the current machine architecture will be used)
        :param repository_name: (deprecated) ECR repository name. Specify this property if you need to statically address the image, e.g. from a Kubernetes Pod. Note, this is only the repository name, without the registry and the tag parts. Default: - the default ECR repository for CDK assets
        :param target: Docker target to build to. Default: - no target
        :param extra_hash: (deprecated) Extra information to encode into the fingerprint (e.g. build instructions and other inputs). Default: - hash is only based on source content
        :param exclude: (deprecated) Glob patterns to exclude from the copy. Default: nothing is excluded
        :param follow: (deprecated) A strategy for how to handle symlinks. Default: Never
        :param ignore_mode: (deprecated) The ignore behavior to use for exclude patterns. Default: - GLOB for file assets, DOCKER or GLOB for docker assets depending on whether the '
        :param follow_symlinks: A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f0a41a87e30c3e2ba678aa154b1266ff2de5f42a22960039c6beca45b7603e3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_ecr_assets_ef09b699.DockerImageAssetProps(
            directory=directory,
            build_args=build_args,
            file=file,
            invalidation=invalidation,
            network_mode=network_mode,
            platform=platform,
            repository_name=repository_name,
            target=target,
            extra_hash=extra_hash,
            exclude=exclude,
            follow=follow,
            ignore_mode=ignore_mode,
            follow_symlinks=follow_symlinks,
        )

        return typing.cast(IBuildImage, jsii.sinvoke(cls, "fromAsset", [scope, id, props]))

    @jsii.member(jsii_name="fromCodeBuildImageId")
    @builtins.classmethod
    def from_code_build_image_id(cls, id: builtins.str) -> IBuildImage:
        '''Uses a Docker image provided by CodeBuild.

        :param id: The image identifier.

        :return: A Docker image provided by CodeBuild.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-available.html

        Example::

            "aws/codebuild/standard:4.0"
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e252b3ae32d547c8e4a2173466c9654296d2f355341f40b820ef3714e13c9340)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(IBuildImage, jsii.sinvoke(cls, "fromCodeBuildImageId", [id]))

    @jsii.member(jsii_name="fromDockerRegistry")
    @builtins.classmethod
    def from_docker_registry(
        cls,
        name: builtins.str,
        *,
        secrets_manager_credentials: typing.Optional[_aws_cdk_aws_secretsmanager_72af8d6f.ISecret] = None,
    ) -> IBuildImage:
        '''
        :param name: -
        :param secrets_manager_credentials: The credentials, stored in Secrets Manager, used for accessing the repository holding the image, if the repository is private. Default: no credentials will be used (we assume the repository is public)

        :return: a x86-64 Linux build image from a Docker Hub image.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82e58c2d34be75497e7a0c4d829ed0b97b389293abf8ea317abb1e4e8b725438)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        options = DockerImageOptions(
            secrets_manager_credentials=secrets_manager_credentials
        )

        return typing.cast(IBuildImage, jsii.sinvoke(cls, "fromDockerRegistry", [name, options]))

    @jsii.member(jsii_name="fromEcrRepository")
    @builtins.classmethod
    def from_ecr_repository(
        cls,
        repository: _aws_cdk_aws_ecr_093ed842.IRepository,
        tag_or_digest: typing.Optional[builtins.str] = None,
    ) -> IBuildImage:
        '''
        :param repository: The ECR repository.
        :param tag_or_digest: Image tag or digest (default "latest", digests must start with ``sha256:``).

        :return:

        A x86-64 Linux build image from an ECR repository.

        NOTE: if the repository is external (i.e. imported), then we won't be able to add
        a resource policy statement for it so CodeBuild can pull the image.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-ecr.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10d159ee3efe986396bdd9f43f0bf6a3837f50c70dbe4237965afc937d6e8971)
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument tag_or_digest", value=tag_or_digest, expected_type=type_hints["tag_or_digest"])
        return typing.cast(IBuildImage, jsii.sinvoke(cls, "fromEcrRepository", [repository, tag_or_digest]))

    @jsii.member(jsii_name="runScriptBuildspec")
    def run_script_buildspec(self, entrypoint: builtins.str) -> BuildSpec:
        '''Make a buildspec to run the indicated script.

        :param entrypoint: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a8b21167889275f833562be670400e3fcd7dd0399b7a6a5cec48b79a2da3f1e)
            check_type(argname="argument entrypoint", value=entrypoint, expected_type=type_hints["entrypoint"])
        return typing.cast(BuildSpec, jsii.invoke(self, "runScriptBuildspec", [entrypoint]))

    @jsii.member(jsii_name="validate")
    def validate(
        self,
        *,
        build_image: typing.Optional[IBuildImage] = None,
        certificate: typing.Optional[typing.Union[BuildEnvironmentCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
        compute_type: typing.Optional[ComputeType] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
        privileged: typing.Optional[builtins.bool] = None,
    ) -> typing.List[builtins.str]:
        '''Allows the image a chance to validate whether the passed configuration is correct.

        :param build_image: The image used for the builds. Default: LinuxBuildImage.STANDARD_1_0
        :param certificate: The location of the PEM-encoded certificate for the build project. Default: - No external certificate is added to the project
        :param compute_type: The type of compute to use for this build. See the {@link ComputeType} enum for the possible values. Default: taken from {@link #buildImage#defaultComputeType}
        :param environment_variables: The environment variables that your builds can use.
        :param privileged: Indicates how the project builds Docker images. Specify true to enable running the Docker daemon inside a Docker container. This value must be set to true only if this build project will be used to build Docker images, and the specified build environment image is not one provided by AWS CodeBuild with Docker support. Otherwise, all associated builds that attempt to interact with the Docker daemon will fail. Default: false
        '''
        _ = BuildEnvironment(
            build_image=build_image,
            certificate=certificate,
            compute_type=compute_type,
            environment_variables=environment_variables,
            privileged=privileged,
        )

        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "validate", [_]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LINUX_2")
    def AMAZON_LINUX_2(cls) -> IBuildImage:
        return typing.cast(IBuildImage, jsii.sget(cls, "AMAZON_LINUX_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LINUX_2_2")
    def AMAZON_LINUX_2_2(cls) -> IBuildImage:
        return typing.cast(IBuildImage, jsii.sget(cls, "AMAZON_LINUX_2_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LINUX_2_3")
    def AMAZON_LINUX_2_3(cls) -> IBuildImage:
        '''The Amazon Linux 2 x86_64 standard image, version ``3.0``.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "AMAZON_LINUX_2_3"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LINUX_2_ARM")
    def AMAZON_LINUX_2_ARM(cls) -> IBuildImage:
        '''
        :deprecated: Use LinuxArmBuildImage.AMAZON_LINUX_2_STANDARD_1_0 instead.

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "AMAZON_LINUX_2_ARM"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="AMAZON_LINUX_2_ARM_2")
    def AMAZON_LINUX_2_ARM_2(cls) -> IBuildImage:
        '''(deprecated) Image "aws/codebuild/amazonlinux2-aarch64-standard:2.0".

        :deprecated: Use LinuxArmBuildImage.AMAZON_LINUX_2_STANDARD_2_0 instead.

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "AMAZON_LINUX_2_ARM_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="STANDARD_1_0")
    def STANDARD_1_0(cls) -> IBuildImage:
        return typing.cast(IBuildImage, jsii.sget(cls, "STANDARD_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="STANDARD_2_0")
    def STANDARD_2_0(cls) -> IBuildImage:
        return typing.cast(IBuildImage, jsii.sget(cls, "STANDARD_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="STANDARD_3_0")
    def STANDARD_3_0(cls) -> IBuildImage:
        return typing.cast(IBuildImage, jsii.sget(cls, "STANDARD_3_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="STANDARD_4_0")
    def STANDARD_4_0(cls) -> IBuildImage:
        '''The ``aws/codebuild/standard:4.0`` build image.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "STANDARD_4_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="STANDARD_5_0")
    def STANDARD_5_0(cls) -> IBuildImage:
        '''The ``aws/codebuild/standard:5.0`` build image.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "STANDARD_5_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_ANDROID_JAVA8_24_4_1")
    def UBUNTU_14_04_ANDROID_JAVA8_24_4_1(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_ANDROID_JAVA8_24_4_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_ANDROID_JAVA8_26_1_1")
    def UBUNTU_14_04_ANDROID_JAVA8_26_1_1(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_ANDROID_JAVA8_26_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_BASE")
    def UBUNTU_14_04_BASE(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_BASE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_DOCKER_17_09_0")
    def UBUNTU_14_04_DOCKER_17_09_0(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_DOCKER_17_09_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_DOCKER_18_09_0")
    def UBUNTU_14_04_DOCKER_18_09_0(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_DOCKER_18_09_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_DOTNET_CORE_1_1")
    def UBUNTU_14_04_DOTNET_CORE_1_1(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_DOTNET_CORE_1_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_DOTNET_CORE_2_0")
    def UBUNTU_14_04_DOTNET_CORE_2_0(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_DOTNET_CORE_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_DOTNET_CORE_2_1")
    def UBUNTU_14_04_DOTNET_CORE_2_1(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_DOTNET_CORE_2_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_GOLANG_1_10")
    def UBUNTU_14_04_GOLANG_1_10(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_GOLANG_1_10"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_GOLANG_1_11")
    def UBUNTU_14_04_GOLANG_1_11(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_GOLANG_1_11"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_NODEJS_10_1_0")
    def UBUNTU_14_04_NODEJS_10_1_0(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_NODEJS_10_1_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_NODEJS_10_14_1")
    def UBUNTU_14_04_NODEJS_10_14_1(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_NODEJS_10_14_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_NODEJS_6_3_1")
    def UBUNTU_14_04_NODEJS_6_3_1(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_NODEJS_6_3_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_NODEJS_8_11_0")
    def UBUNTU_14_04_NODEJS_8_11_0(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_NODEJS_8_11_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_OPEN_JDK_11")
    def UBUNTU_14_04_OPEN_JDK_11(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_OPEN_JDK_11"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_OPEN_JDK_8")
    def UBUNTU_14_04_OPEN_JDK_8(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_OPEN_JDK_8"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_OPEN_JDK_9")
    def UBUNTU_14_04_OPEN_JDK_9(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_OPEN_JDK_9"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PHP_5_6")
    def UBUNTU_14_04_PHP_5_6(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_PHP_5_6"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PHP_7_0")
    def UBUNTU_14_04_PHP_7_0(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_PHP_7_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PHP_7_1")
    def UBUNTU_14_04_PHP_7_1(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_PHP_7_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PYTHON_2_7_12")
    def UBUNTU_14_04_PYTHON_2_7_12(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_PYTHON_2_7_12"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PYTHON_3_3_6")
    def UBUNTU_14_04_PYTHON_3_3_6(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_PYTHON_3_3_6"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PYTHON_3_4_5")
    def UBUNTU_14_04_PYTHON_3_4_5(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_PYTHON_3_4_5"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PYTHON_3_5_2")
    def UBUNTU_14_04_PYTHON_3_5_2(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_PYTHON_3_5_2"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PYTHON_3_6_5")
    def UBUNTU_14_04_PYTHON_3_6_5(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_PYTHON_3_6_5"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_PYTHON_3_7_1")
    def UBUNTU_14_04_PYTHON_3_7_1(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_PYTHON_3_7_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_RUBY_2_2_5")
    def UBUNTU_14_04_RUBY_2_2_5(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_RUBY_2_2_5"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_RUBY_2_3_1")
    def UBUNTU_14_04_RUBY_2_3_1(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_RUBY_2_3_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_RUBY_2_5_1")
    def UBUNTU_14_04_RUBY_2_5_1(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_RUBY_2_5_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="UBUNTU_14_04_RUBY_2_5_3")
    def UBUNTU_14_04_RUBY_2_5_3(cls) -> IBuildImage:
        '''
        :deprecated: Use {@link STANDARD_2_0} and specify runtime in buildspec runtime-versions section

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "UBUNTU_14_04_RUBY_2_5_3"))

    @builtins.property
    @jsii.member(jsii_name="defaultComputeType")
    def default_compute_type(self) -> ComputeType:
        '''The default {@link ComputeType} to use with this image, if one was not specified in {@link BuildEnvironment#computeType} explicitly.'''
        return typing.cast(ComputeType, jsii.get(self, "defaultComputeType"))

    @builtins.property
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> builtins.str:
        '''The Docker image identifier that the build environment uses.'''
        return typing.cast(builtins.str, jsii.get(self, "imageId"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''The type of build environment.'''
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="imagePullPrincipalType")
    def image_pull_principal_type(self) -> typing.Optional[ImagePullPrincipalType]:
        '''The type of principal that CodeBuild will use to pull this build Docker image.'''
        return typing.cast(typing.Optional[ImagePullPrincipalType], jsii.get(self, "imagePullPrincipalType"))

    @builtins.property
    @jsii.member(jsii_name="repository")
    def repository(self) -> typing.Optional[_aws_cdk_aws_ecr_093ed842.IRepository]:
        '''An optional ECR repository that the image is hosted in.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ecr_093ed842.IRepository], jsii.get(self, "repository"))

    @builtins.property
    @jsii.member(jsii_name="secretsManagerCredentials")
    def secrets_manager_credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_72af8d6f.ISecret]:
        '''The secretsManagerCredentials for access to a private registry.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_72af8d6f.ISecret], jsii.get(self, "secretsManagerCredentials"))


@jsii.enum(jsii_type="@aws-cdk/aws-codebuild.LocalCacheMode")
class LocalCacheMode(enum.Enum):
    '''Local cache modes to enable for the CodeBuild Project.

    :exampleMetadata: infused

    Example::

        codebuild.Project(self, "Project",
            source=codebuild.Source.git_hub_enterprise(
                https_clone_url="https://my-github-enterprise.com/owner/repo"
            ),
        
            # Enable Docker AND custom caching
            cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER, codebuild.LocalCacheMode.CUSTOM),
        
            # BuildSpec with a 'cache' section necessary for 'CUSTOM' caching. This can
            # also come from 'buildspec.yml' in your source.
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "build": {
                        "commands": ["..."]
                    }
                },
                "cache": {
                    "paths": ["/root/cachedir/**/*"
                    ]
                }
            })
        )
    '''

    SOURCE = "SOURCE"
    '''Caches Git metadata for primary and secondary sources.'''
    DOCKER_LAYER = "DOCKER_LAYER"
    '''Caches existing Docker layers.'''
    CUSTOM = "CUSTOM"
    '''Caches directories you specify in the buildspec file.'''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.LoggingOptions",
    jsii_struct_bases=[],
    name_mapping={"cloud_watch": "cloudWatch", "s3": "s3"},
)
class LoggingOptions:
    def __init__(
        self,
        *,
        cloud_watch: typing.Optional[typing.Union[CloudWatchLoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        s3: typing.Optional[typing.Union["S3LoggingOptions", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Information about logs for the build project.

        A project can create logs in Amazon CloudWatch Logs, an S3 bucket, or both.

        :param cloud_watch: Information about Amazon CloudWatch Logs for a build project. Default: - enabled
        :param s3: Information about logs built to an S3 bucket for a build project. Default: - disabled

        :exampleMetadata: infused

        Example::

            codebuild.Project(self, "Project",
                logging=codebuild.LoggingOptions(
                    cloud_watch=codebuild.CloudWatchLoggingOptions(
                        log_group=logs.LogGroup(self, "MyLogGroup")
                    )
                )
            )
        '''
        if isinstance(cloud_watch, dict):
            cloud_watch = CloudWatchLoggingOptions(**cloud_watch)
        if isinstance(s3, dict):
            s3 = S3LoggingOptions(**s3)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6f8b863f2ac970d653f2691f88e393d07a6c57410419271609262d28a03402f)
            check_type(argname="argument cloud_watch", value=cloud_watch, expected_type=type_hints["cloud_watch"])
            check_type(argname="argument s3", value=s3, expected_type=type_hints["s3"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cloud_watch is not None:
            self._values["cloud_watch"] = cloud_watch
        if s3 is not None:
            self._values["s3"] = s3

    @builtins.property
    def cloud_watch(self) -> typing.Optional[CloudWatchLoggingOptions]:
        '''Information about Amazon CloudWatch Logs for a build project.

        :default: - enabled
        '''
        result = self._values.get("cloud_watch")
        return typing.cast(typing.Optional[CloudWatchLoggingOptions], result)

    @builtins.property
    def s3(self) -> typing.Optional["S3LoggingOptions"]:
        '''Information about logs built to an S3 bucket for a build project.

        :default: - disabled
        '''
        result = self._values.get("s3")
        return typing.cast(typing.Optional["S3LoggingOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoggingOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PhaseChangeEvent(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.PhaseChangeEvent",
):
    '''Event fields for the CodeBuild "phase change" event.

    :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html#sample-build-notifications-ref
    '''

    @jsii.python.classproperty
    @jsii.member(jsii_name="buildComplete")
    def build_complete(cls) -> builtins.str:
        '''Whether the build is complete.'''
        return typing.cast(builtins.str, jsii.sget(cls, "buildComplete"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="buildId")
    def build_id(cls) -> builtins.str:
        '''The triggering build's id.'''
        return typing.cast(builtins.str, jsii.sget(cls, "buildId"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="completedPhase")
    def completed_phase(cls) -> builtins.str:
        '''The phase that was just completed.'''
        return typing.cast(builtins.str, jsii.sget(cls, "completedPhase"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="completedPhaseDurationSeconds")
    def completed_phase_duration_seconds(cls) -> builtins.str:
        '''The duration of the completed phase.'''
        return typing.cast(builtins.str, jsii.sget(cls, "completedPhaseDurationSeconds"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="completedPhaseStatus")
    def completed_phase_status(cls) -> builtins.str:
        '''The status of the completed phase.'''
        return typing.cast(builtins.str, jsii.sget(cls, "completedPhaseStatus"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="projectName")
    def project_name(cls) -> builtins.str:
        '''The triggering build's project name.'''
        return typing.cast(builtins.str, jsii.sget(cls, "projectName"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.PipelineProjectProps",
    jsii_struct_bases=[CommonProjectProps],
    name_mapping={
        "allow_all_outbound": "allowAllOutbound",
        "badge": "badge",
        "build_spec": "buildSpec",
        "cache": "cache",
        "check_secrets_in_plain_text_env_variables": "checkSecretsInPlainTextEnvVariables",
        "concurrent_build_limit": "concurrentBuildLimit",
        "description": "description",
        "encryption_key": "encryptionKey",
        "environment": "environment",
        "environment_variables": "environmentVariables",
        "file_system_locations": "fileSystemLocations",
        "grant_report_group_permissions": "grantReportGroupPermissions",
        "logging": "logging",
        "project_name": "projectName",
        "queued_timeout": "queuedTimeout",
        "role": "role",
        "security_groups": "securityGroups",
        "subnet_selection": "subnetSelection",
        "timeout": "timeout",
        "vpc": "vpc",
    },
)
class PipelineProjectProps(CommonProjectProps):
    def __init__(
        self,
        *,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        badge: typing.Optional[builtins.bool] = None,
        build_spec: typing.Optional[BuildSpec] = None,
        cache: typing.Optional[Cache] = None,
        check_secrets_in_plain_text_env_variables: typing.Optional[builtins.bool] = None,
        concurrent_build_limit: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
        environment: typing.Optional[typing.Union[BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
        file_system_locations: typing.Optional[typing.Sequence[IFileSystemLocation]] = None,
        grant_report_group_permissions: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[typing.Union[LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        project_name: typing.Optional[builtins.str] = None,
        queued_timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_67de8e8d.IVpc] = None,
    ) -> None:
        '''
        :param allow_all_outbound: Whether to allow the CodeBuild to send all network traffic. If set to false, you must individually add traffic rules to allow the CodeBuild project to connect to network targets. Only used if 'vpc' is supplied. Default: true
        :param badge: Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge. For more information, see Build Badges Sample in the AWS CodeBuild User Guide. Default: false
        :param build_spec: Filename or contents of buildspec in JSON format. Default: - Empty buildspec.
        :param cache: Caching strategy to use. Default: Cache.none
        :param check_secrets_in_plain_text_env_variables: Whether to check for the presence of any secrets in the environment variables of the default type, BuildEnvironmentVariableType.PLAINTEXT. Since using a secret for the value of that kind of variable would result in it being displayed in plain text in the AWS Console, the construct will throw an exception if it detects a secret was passed there. Pass this property as false if you want to skip this validation, and keep using a secret in a plain text environment variable. Default: true
        :param concurrent_build_limit: Maximum number of concurrent builds. Minimum value is 1 and maximum is account build limit. Default: - no explicit limit is set
        :param description: A description of the project. Use the description to identify the purpose of the project. Default: - No description.
        :param encryption_key: Encryption key to use to read and write artifacts. Default: - The AWS-managed CMK for Amazon Simple Storage Service (Amazon S3) is used.
        :param environment: Build environment to use for the build. Default: BuildEnvironment.LinuxBuildImage.STANDARD_1_0
        :param environment_variables: Additional environment variables to add to the build environment. Default: - No additional environment variables are specified.
        :param file_system_locations: An ProjectFileSystemLocation objects for a CodeBuild build project. A ProjectFileSystemLocation object specifies the identifier, location, mountOptions, mountPoint, and type of a file system created using Amazon Elastic File System. Default: - no file system locations
        :param grant_report_group_permissions: Add permissions to this project's role to create and use test report groups with name starting with the name of this project. That is the standard report group that gets created when a simple name (in contrast to an ARN) is used in the 'reports' section of the buildspec of this project. This is usually harmless, but you can turn these off if you don't plan on using test reports in this project. Default: true
        :param logging: Information about logs for the build project. A project can create logs in Amazon CloudWatch Logs, an S3 bucket, or both. Default: - no log configuration is set
        :param project_name: The physical, human-readable name of the CodeBuild Project. Default: - Name is automatically generated.
        :param queued_timeout: The number of minutes after which AWS CodeBuild stops the build if it's still in queue. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: - no queue timeout is set
        :param role: Service Role to assume while running the build. Default: - A role will be created.
        :param security_groups: What security group to associate with the codebuild project's network interfaces. If no security group is identified, one will be created automatically. Only used if 'vpc' is supplied. Default: - Security group will be automatically created.
        :param subnet_selection: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Default: - All private subnets.
        :param timeout: The number of minutes after which AWS CodeBuild stops the build if it's not complete. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: Duration.hours(1)
        :param vpc: VPC network to place codebuild network interfaces. Specify this if the codebuild project needs to access resources in a VPC. Default: - No VPC is specified.

        :exampleMetadata: infused

        Example::

            # Create a Cloudfront Web Distribution
            import aws_cdk.aws_cloudfront as cloudfront
            # distribution: cloudfront.Distribution
            
            
            # Create the build project that will invalidate the cache
            invalidate_build_project = codebuild.PipelineProject(self, "InvalidateProject",
                build_spec=codebuild.BuildSpec.from_object({
                    "version": "0.2",
                    "phases": {
                        "build": {
                            "commands": ["aws cloudfront create-invalidation --distribution-id ${CLOUDFRONT_ID} --paths \"/*\""
                            ]
                        }
                    }
                }),
                environment_variables={
                    "CLOUDFRONT_ID": codebuild.BuildEnvironmentVariable(value=distribution.distribution_id)
                }
            )
            
            # Add Cloudfront invalidation permissions to the project
            distribution_arn = f"arn:aws:cloudfront::{this.account}:distribution/{distribution.distributionId}"
            invalidate_build_project.add_to_role_policy(iam.PolicyStatement(
                resources=[distribution_arn],
                actions=["cloudfront:CreateInvalidation"
                ]
            ))
            
            # Create the pipeline (here only the S3 deploy and Invalidate cache build)
            deploy_bucket = s3.Bucket(self, "DeployBucket")
            deploy_input = codepipeline.Artifact()
            codepipeline.Pipeline(self, "Pipeline",
                stages=[codepipeline.StageProps(
                    stage_name="Deploy",
                    actions=[
                        codepipeline_actions.S3DeployAction(
                            action_name="S3Deploy",
                            bucket=deploy_bucket,
                            input=deploy_input,
                            run_order=1
                        ),
                        codepipeline_actions.CodeBuildAction(
                            action_name="InvalidateCache",
                            project=invalidate_build_project,
                            input=deploy_input,
                            run_order=2
                        )
                    ]
                )
                ]
            )
        '''
        if isinstance(environment, dict):
            environment = BuildEnvironment(**environment)
        if isinstance(logging, dict):
            logging = LoggingOptions(**logging)
        if isinstance(subnet_selection, dict):
            subnet_selection = _aws_cdk_aws_ec2_67de8e8d.SubnetSelection(**subnet_selection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be82c34c86ec190d07ba76d4a9645f2e45f0b0d62e6cd433971de287ebad41c7)
            check_type(argname="argument allow_all_outbound", value=allow_all_outbound, expected_type=type_hints["allow_all_outbound"])
            check_type(argname="argument badge", value=badge, expected_type=type_hints["badge"])
            check_type(argname="argument build_spec", value=build_spec, expected_type=type_hints["build_spec"])
            check_type(argname="argument cache", value=cache, expected_type=type_hints["cache"])
            check_type(argname="argument check_secrets_in_plain_text_env_variables", value=check_secrets_in_plain_text_env_variables, expected_type=type_hints["check_secrets_in_plain_text_env_variables"])
            check_type(argname="argument concurrent_build_limit", value=concurrent_build_limit, expected_type=type_hints["concurrent_build_limit"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument environment_variables", value=environment_variables, expected_type=type_hints["environment_variables"])
            check_type(argname="argument file_system_locations", value=file_system_locations, expected_type=type_hints["file_system_locations"])
            check_type(argname="argument grant_report_group_permissions", value=grant_report_group_permissions, expected_type=type_hints["grant_report_group_permissions"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument project_name", value=project_name, expected_type=type_hints["project_name"])
            check_type(argname="argument queued_timeout", value=queued_timeout, expected_type=type_hints["queued_timeout"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnet_selection", value=subnet_selection, expected_type=type_hints["subnet_selection"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if badge is not None:
            self._values["badge"] = badge
        if build_spec is not None:
            self._values["build_spec"] = build_spec
        if cache is not None:
            self._values["cache"] = cache
        if check_secrets_in_plain_text_env_variables is not None:
            self._values["check_secrets_in_plain_text_env_variables"] = check_secrets_in_plain_text_env_variables
        if concurrent_build_limit is not None:
            self._values["concurrent_build_limit"] = concurrent_build_limit
        if description is not None:
            self._values["description"] = description
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if environment is not None:
            self._values["environment"] = environment
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if file_system_locations is not None:
            self._values["file_system_locations"] = file_system_locations
        if grant_report_group_permissions is not None:
            self._values["grant_report_group_permissions"] = grant_report_group_permissions
        if logging is not None:
            self._values["logging"] = logging
        if project_name is not None:
            self._values["project_name"] = project_name
        if queued_timeout is not None:
            self._values["queued_timeout"] = queued_timeout
        if role is not None:
            self._values["role"] = role
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection
        if timeout is not None:
            self._values["timeout"] = timeout
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether to allow the CodeBuild to send all network traffic.

        If set to false, you must individually add traffic rules to allow the
        CodeBuild project to connect to network targets.

        Only used if 'vpc' is supplied.

        :default: true
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def badge(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge.

        For more information, see Build Badges Sample
        in the AWS CodeBuild User Guide.

        :default: false
        '''
        result = self._values.get("badge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def build_spec(self) -> typing.Optional[BuildSpec]:
        '''Filename or contents of buildspec in JSON format.

        :default: - Empty buildspec.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec-ref-example
        '''
        result = self._values.get("build_spec")
        return typing.cast(typing.Optional[BuildSpec], result)

    @builtins.property
    def cache(self) -> typing.Optional[Cache]:
        '''Caching strategy to use.

        :default: Cache.none
        '''
        result = self._values.get("cache")
        return typing.cast(typing.Optional[Cache], result)

    @builtins.property
    def check_secrets_in_plain_text_env_variables(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''Whether to check for the presence of any secrets in the environment variables of the default type, BuildEnvironmentVariableType.PLAINTEXT. Since using a secret for the value of that kind of variable would result in it being displayed in plain text in the AWS Console, the construct will throw an exception if it detects a secret was passed there. Pass this property as false if you want to skip this validation, and keep using a secret in a plain text environment variable.

        :default: true
        '''
        result = self._values.get("check_secrets_in_plain_text_env_variables")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def concurrent_build_limit(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of concurrent builds.

        Minimum value is 1 and maximum is account build limit.

        :default: - no explicit limit is set
        '''
        result = self._values.get("concurrent_build_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the project.

        Use the description to identify the purpose
        of the project.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey]:
        '''Encryption key to use to read and write artifacts.

        :default: - The AWS-managed CMK for Amazon Simple Storage Service (Amazon S3) is used.
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey], result)

    @builtins.property
    def environment(self) -> typing.Optional[BuildEnvironment]:
        '''Build environment to use for the build.

        :default: BuildEnvironment.LinuxBuildImage.STANDARD_1_0
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[BuildEnvironment], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, BuildEnvironmentVariable]]:
        '''Additional environment variables to add to the build environment.

        :default: - No additional environment variables are specified.
        '''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, BuildEnvironmentVariable]], result)

    @builtins.property
    def file_system_locations(
        self,
    ) -> typing.Optional[typing.List[IFileSystemLocation]]:
        '''An  ProjectFileSystemLocation objects for a CodeBuild build project.

        A ProjectFileSystemLocation object specifies the identifier, location, mountOptions, mountPoint,
        and type of a file system created using Amazon Elastic File System.

        :default: - no file system locations
        '''
        result = self._values.get("file_system_locations")
        return typing.cast(typing.Optional[typing.List[IFileSystemLocation]], result)

    @builtins.property
    def grant_report_group_permissions(self) -> typing.Optional[builtins.bool]:
        '''Add permissions to this project's role to create and use test report groups with name starting with the name of this project.

        That is the standard report group that gets created when a simple name
        (in contrast to an ARN)
        is used in the 'reports' section of the buildspec of this project.
        This is usually harmless, but you can turn these off if you don't plan on using test
        reports in this project.

        :default: true

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/test-report-group-naming.html
        '''
        result = self._values.get("grant_report_group_permissions")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def logging(self) -> typing.Optional[LoggingOptions]:
        '''Information about logs for the build project.

        A project can create logs in Amazon CloudWatch Logs, an S3 bucket, or both.

        :default: - no log configuration is set
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[LoggingOptions], result)

    @builtins.property
    def project_name(self) -> typing.Optional[builtins.str]:
        '''The physical, human-readable name of the CodeBuild Project.

        :default: - Name is automatically generated.
        '''
        result = self._values.get("project_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queued_timeout(self) -> typing.Optional[_aws_cdk_core_f4b25747.Duration]:
        '''The number of minutes after which AWS CodeBuild stops the build if it's still in queue.

        For valid values, see the timeoutInMinutes field in the AWS
        CodeBuild User Guide.

        :default: - no queue timeout is set
        '''
        result = self._values.get("queued_timeout")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Duration], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole]:
        '''Service Role to assume while running the build.

        :default: - A role will be created.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]]:
        '''What security group to associate with the codebuild project's network interfaces.

        If no security group is identified, one will be created automatically.

        Only used if 'vpc' is supplied.

        :default: - Security group will be automatically created.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]], result)

    @builtins.property
    def subnet_selection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection]:
        '''Where to place the network interfaces within the VPC.

        Only used if 'vpc' is supplied.

        :default: - All private subnets.
        '''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_core_f4b25747.Duration]:
        '''The number of minutes after which AWS CodeBuild stops the build if it's not complete.

        For valid values, see the timeoutInMinutes field in the AWS
        CodeBuild User Guide.

        :default: Duration.hours(1)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Duration], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_67de8e8d.IVpc]:
        '''VPC network to place codebuild network interfaces.

        Specify this if the codebuild project needs to access resources in a VPC.

        :default: - No VPC is specified.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_67de8e8d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineProjectProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IProject)
class Project(
    _aws_cdk_core_f4b25747.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.Project",
):
    '''A representation of a CodeBuild Project.

    :exampleMetadata: infused

    Example::

        # bucket: s3.Bucket
        
        
        project = codebuild.Project(self, "MyProject",
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2"
            }),
            artifacts=codebuild.Artifacts.s3(
                bucket=bucket,
                include_build_id=False,
                package_zip=True,
                path="another/path",
                identifier="AddArtifact1"
            )
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        artifacts: typing.Optional[IArtifacts] = None,
        secondary_artifacts: typing.Optional[typing.Sequence[IArtifacts]] = None,
        secondary_sources: typing.Optional[typing.Sequence[ISource]] = None,
        source: typing.Optional[ISource] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        badge: typing.Optional[builtins.bool] = None,
        build_spec: typing.Optional[BuildSpec] = None,
        cache: typing.Optional[Cache] = None,
        check_secrets_in_plain_text_env_variables: typing.Optional[builtins.bool] = None,
        concurrent_build_limit: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
        environment: typing.Optional[typing.Union[BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
        file_system_locations: typing.Optional[typing.Sequence[IFileSystemLocation]] = None,
        grant_report_group_permissions: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[typing.Union[LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        project_name: typing.Optional[builtins.str] = None,
        queued_timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_67de8e8d.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param artifacts: Defines where build artifacts will be stored. Could be: PipelineBuildArtifacts, NoArtifacts and S3Artifacts. Default: NoArtifacts
        :param secondary_artifacts: The secondary artifacts for the Project. Can also be added after the Project has been created by using the {@link Project#addSecondaryArtifact} method. Default: - No secondary artifacts.
        :param secondary_sources: The secondary sources for the Project. Can be also added after the Project has been created by using the {@link Project#addSecondarySource} method. Default: - No secondary sources.
        :param source: The source of the build. *Note*: if {@link NoSource} is given as the source, then you need to provide an explicit ``buildSpec``. Default: - NoSource
        :param allow_all_outbound: Whether to allow the CodeBuild to send all network traffic. If set to false, you must individually add traffic rules to allow the CodeBuild project to connect to network targets. Only used if 'vpc' is supplied. Default: true
        :param badge: Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge. For more information, see Build Badges Sample in the AWS CodeBuild User Guide. Default: false
        :param build_spec: Filename or contents of buildspec in JSON format. Default: - Empty buildspec.
        :param cache: Caching strategy to use. Default: Cache.none
        :param check_secrets_in_plain_text_env_variables: Whether to check for the presence of any secrets in the environment variables of the default type, BuildEnvironmentVariableType.PLAINTEXT. Since using a secret for the value of that kind of variable would result in it being displayed in plain text in the AWS Console, the construct will throw an exception if it detects a secret was passed there. Pass this property as false if you want to skip this validation, and keep using a secret in a plain text environment variable. Default: true
        :param concurrent_build_limit: Maximum number of concurrent builds. Minimum value is 1 and maximum is account build limit. Default: - no explicit limit is set
        :param description: A description of the project. Use the description to identify the purpose of the project. Default: - No description.
        :param encryption_key: Encryption key to use to read and write artifacts. Default: - The AWS-managed CMK for Amazon Simple Storage Service (Amazon S3) is used.
        :param environment: Build environment to use for the build. Default: BuildEnvironment.LinuxBuildImage.STANDARD_1_0
        :param environment_variables: Additional environment variables to add to the build environment. Default: - No additional environment variables are specified.
        :param file_system_locations: An ProjectFileSystemLocation objects for a CodeBuild build project. A ProjectFileSystemLocation object specifies the identifier, location, mountOptions, mountPoint, and type of a file system created using Amazon Elastic File System. Default: - no file system locations
        :param grant_report_group_permissions: Add permissions to this project's role to create and use test report groups with name starting with the name of this project. That is the standard report group that gets created when a simple name (in contrast to an ARN) is used in the 'reports' section of the buildspec of this project. This is usually harmless, but you can turn these off if you don't plan on using test reports in this project. Default: true
        :param logging: Information about logs for the build project. A project can create logs in Amazon CloudWatch Logs, an S3 bucket, or both. Default: - no log configuration is set
        :param project_name: The physical, human-readable name of the CodeBuild Project. Default: - Name is automatically generated.
        :param queued_timeout: The number of minutes after which AWS CodeBuild stops the build if it's still in queue. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: - no queue timeout is set
        :param role: Service Role to assume while running the build. Default: - A role will be created.
        :param security_groups: What security group to associate with the codebuild project's network interfaces. If no security group is identified, one will be created automatically. Only used if 'vpc' is supplied. Default: - Security group will be automatically created.
        :param subnet_selection: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Default: - All private subnets.
        :param timeout: The number of minutes after which AWS CodeBuild stops the build if it's not complete. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: Duration.hours(1)
        :param vpc: VPC network to place codebuild network interfaces. Specify this if the codebuild project needs to access resources in a VPC. Default: - No VPC is specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ec8dd4874fb2321351b09050a733240b38f8f630963ed988aa42dee8882f0b9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ProjectProps(
            artifacts=artifacts,
            secondary_artifacts=secondary_artifacts,
            secondary_sources=secondary_sources,
            source=source,
            allow_all_outbound=allow_all_outbound,
            badge=badge,
            build_spec=build_spec,
            cache=cache,
            check_secrets_in_plain_text_env_variables=check_secrets_in_plain_text_env_variables,
            concurrent_build_limit=concurrent_build_limit,
            description=description,
            encryption_key=encryption_key,
            environment=environment,
            environment_variables=environment_variables,
            file_system_locations=file_system_locations,
            grant_report_group_permissions=grant_report_group_permissions,
            logging=logging,
            project_name=project_name,
            queued_timeout=queued_timeout,
            role=role,
            security_groups=security_groups,
            subnet_selection=subnet_selection,
            timeout=timeout,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromProjectArn")
    @builtins.classmethod
    def from_project_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        project_arn: builtins.str,
    ) -> IProject:
        '''
        :param scope: -
        :param id: -
        :param project_arn: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61bd361c9664084139d451cac78033814931bd053310b8f80c1616b9a6d67155)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument project_arn", value=project_arn, expected_type=type_hints["project_arn"])
        return typing.cast(IProject, jsii.sinvoke(cls, "fromProjectArn", [scope, id, project_arn]))

    @jsii.member(jsii_name="fromProjectName")
    @builtins.classmethod
    def from_project_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        project_name: builtins.str,
    ) -> IProject:
        '''Import a Project defined either outside the CDK, or in a different CDK Stack (and exported using the {@link export} method).

        :param scope: the parent Construct for this Construct.
        :param id: the logical name of this Construct.
        :param project_name: the name of the project to import.

        :return: a reference to the existing Project

        :note:

        if you're importing a CodeBuild Project for use
        in a CodePipeline, make sure the existing Project
        has permissions to access the S3 Bucket of that Pipeline -
        otherwise, builds in that Pipeline will always fail.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a62d83fea5682a870c65d59458d7e761a9a4a32a443b4c715344b91835f95263)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument project_name", value=project_name, expected_type=type_hints["project_name"])
        return typing.cast(IProject, jsii.sinvoke(cls, "fromProjectName", [scope, id, project_name]))

    @jsii.member(jsii_name="serializeEnvVariables")
    @builtins.classmethod
    def serialize_env_variables(
        cls,
        environment_variables: typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]],
        validate_no_plain_text_secrets: typing.Optional[builtins.bool] = None,
        principal: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IGrantable] = None,
    ) -> typing.List[CfnProject.EnvironmentVariableProperty]:
        '''Convert the environment variables map of string to {@link BuildEnvironmentVariable}, which is the customer-facing type, to a list of {@link CfnProject.EnvironmentVariableProperty}, which is the representation of environment variables in CloudFormation.

        :param environment_variables: the map of string to environment variables.
        :param validate_no_plain_text_secrets: whether to throw an exception if any of the plain text environment variables contain secrets, defaults to 'false'.
        :param principal: -

        :return: an array of {@link CfnProject.EnvironmentVariableProperty} instances
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__398e76aa361c058058bcf2fab93ce577ac0b05b3da01e8cc5f4bc52a1e891dbd)
            check_type(argname="argument environment_variables", value=environment_variables, expected_type=type_hints["environment_variables"])
            check_type(argname="argument validate_no_plain_text_secrets", value=validate_no_plain_text_secrets, expected_type=type_hints["validate_no_plain_text_secrets"])
            check_type(argname="argument principal", value=principal, expected_type=type_hints["principal"])
        return typing.cast(typing.List[CfnProject.EnvironmentVariableProperty], jsii.sinvoke(cls, "serializeEnvVariables", [environment_variables, validate_no_plain_text_secrets, principal]))

    @jsii.member(jsii_name="addFileSystemLocation")
    def add_file_system_location(
        self,
        file_system_location: IFileSystemLocation,
    ) -> None:
        '''Adds a fileSystemLocation to the Project.

        :param file_system_location: the fileSystemLocation to add.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff1c8eaa80bd3957d81338cb301ceeeb2a475c13a886987958c72ec9a0729fd2)
            check_type(argname="argument file_system_location", value=file_system_location, expected_type=type_hints["file_system_location"])
        return typing.cast(None, jsii.invoke(self, "addFileSystemLocation", [file_system_location]))

    @jsii.member(jsii_name="addSecondaryArtifact")
    def add_secondary_artifact(self, secondary_artifact: IArtifacts) -> None:
        '''Adds a secondary artifact to the Project.

        :param secondary_artifact: the artifact to add as a secondary artifact.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-multi-in-out.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__677f880080fcc0d6f790d1ca12b664b2bfc31822dd7b60b85190dc8de4f63e1a)
            check_type(argname="argument secondary_artifact", value=secondary_artifact, expected_type=type_hints["secondary_artifact"])
        return typing.cast(None, jsii.invoke(self, "addSecondaryArtifact", [secondary_artifact]))

    @jsii.member(jsii_name="addSecondarySource")
    def add_secondary_source(self, secondary_source: ISource) -> None:
        '''Adds a secondary source to the Project.

        :param secondary_source: the source to add as a secondary source.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-multi-in-out.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5ce36ddce9071499ef0ba4682c64cf04251b4d4aa7c2e2b60c3b76130786fd2)
            check_type(argname="argument secondary_source", value=secondary_source, expected_type=type_hints["secondary_source"])
        return typing.cast(None, jsii.invoke(self, "addSecondarySource", [secondary_source]))

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(
        self,
        statement: _aws_cdk_aws_iam_940a1ce0.PolicyStatement,
    ) -> None:
        '''Add a permission only if there's a policy attached.

        :param statement: The permissions statement to add.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7d7ce26017e929c0061701a258c134dcddf25e899508b621fc5c34484a22ab3)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(None, jsii.invoke(self, "addToRolePolicy", [statement]))

    @jsii.member(jsii_name="bindAsNotificationRuleSource")
    def bind_as_notification_rule_source(
        self,
        _scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleSourceConfig:
        '''Returns a source configuration for notification rule.

        :param _scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cfa12d40a16fa0e6832bf8bd0c6a32a7bc8296838efb9c02ffa5ce046cbc0b2)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleSourceConfig, jsii.invoke(self, "bindAsNotificationRuleSource", [_scope]))

    @jsii.member(jsii_name="bindToCodePipeline")
    def bind_to_code_pipeline(
        self,
        _scope: _aws_cdk_core_f4b25747.Construct,
        *,
        artifact_bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
    ) -> None:
        '''A callback invoked when the given project is added to a CodePipeline.

        :param _scope: the construct the binding is taking place in.
        :param artifact_bucket: The artifact bucket that will be used by the action that invokes this project.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8a334c2273783dc7e914b32e7694c15b5e2d3b66c9046c24b0eb3ba887766c1)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        options = BindToCodePipelineOptions(artifact_bucket=artifact_bucket)

        return typing.cast(None, jsii.invoke(self, "bindToCodePipeline", [_scope, options]))

    @jsii.member(jsii_name="enableBatchBuilds")
    def enable_batch_builds(self) -> typing.Optional[BatchBuildConfig]:
        '''Enable batch builds.

        Returns an object contining the batch service role if batch builds
        could be enabled.
        '''
        return typing.cast(typing.Optional[BatchBuildConfig], jsii.invoke(self, "enableBatchBuilds", []))

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
        '''
        :param metric_name: The name of the metric.
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions: (deprecated) Dimensions of the metric. Default: - No dimensions.
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :return: a CloudWatch metric associated with this build project.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b557da2d053f95d43712ef2f385b251305d84b5db47100e79b3bccc58880243f)
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

    @jsii.member(jsii_name="metricBuilds")
    def metric_builds(
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
        '''Measures the number of builds triggered.

        Units: Count

        Valid CloudWatch statistics: Sum

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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricBuilds", [props]))

    @jsii.member(jsii_name="metricDuration")
    def metric_duration(
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
        '''Measures the duration of all builds over time.

        Units: Seconds

        Valid CloudWatch statistics: Average (recommended), Maximum, Minimum

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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricDuration", [props]))

    @jsii.member(jsii_name="metricFailedBuilds")
    def metric_failed_builds(
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
        '''Measures the number of builds that failed because of client error or because of a timeout.

        Units: Count

        Valid CloudWatch statistics: Sum

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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricFailedBuilds", [props]))

    @jsii.member(jsii_name="metricSucceededBuilds")
    def metric_succeeded_builds(
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
        '''Measures the number of successful builds.

        Units: Count

        Valid CloudWatch statistics: Sum

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

        return typing.cast(_aws_cdk_aws_cloudwatch_9b88bb94.Metric, jsii.invoke(self, "metricSucceededBuilds", [props]))

    @jsii.member(jsii_name="notifyOn")
    def notify_on(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        events: typing.Sequence["ProjectNotificationEvents"],
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule triggered when the project events emitted by you specified, it very similar to ``onEvent`` API.

        You can also use the methods ``notifyOnBuildSucceeded`` and
        ``notifyOnBuildFailed`` to define rules for these specific event emitted.

        :param id: -
        :param target: -
        :param events: A list of event types associated with this notification rule for CodeBuild Project. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25c79a24fef003cf9aa9b0edbeada41b08f45b433cac04a556ed064b9164ed26)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = ProjectNotifyOnOptions(
            events=events,
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOn", [id, target, options]))

    @jsii.member(jsii_name="notifyOnBuildFailed")
    def notify_on_build_failed(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar notification rule which triggers when a build fails.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44f9487bc7882f9fae2ff2ad21c248d77ce081e3958144945aeb471764bf4f02)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnBuildFailed", [id, target, options]))

    @jsii.member(jsii_name="notifyOnBuildSucceeded")
    def notify_on_build_succeeded(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar notification rule which triggers when a build completes successfully.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45b519a221bf531799c83a66ac2a9222554bccc08d17c3e5b7d865ef0b7ae01a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnBuildSucceeded", [id, target, options]))

    @jsii.member(jsii_name="onBuildFailed")
    def on_build_failed(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines an event rule which triggers when a build fails.

        To access fields from the event in the event target input,
        use the static fields on the ``StateChangeEvent`` class.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3339bcc0f06be4576f664c0ce85e13853544f3129fb36b369cd37a812d919bc)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onBuildFailed", [id, options]))

    @jsii.member(jsii_name="onBuildStarted")
    def on_build_started(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines an event rule which triggers when a build starts.

        To access fields from the event in the event target input,
        use the static fields on the ``StateChangeEvent`` class.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fa1bcd24015cb5308173ef0b970fbf2ec7999d2af93a6b616b7569eb36f12f6)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onBuildStarted", [id, options]))

    @jsii.member(jsii_name="onBuildSucceeded")
    def on_build_succeeded(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines an event rule which triggers when a build completes successfully.

        To access fields from the event in the event target input,
        use the static fields on the ``StateChangeEvent`` class.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b97479dcab1b70f438c4964f56b1c94779dfe677d4523de11048f2d8dcc10838)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onBuildSucceeded", [id, options]))

    @jsii.member(jsii_name="onEvent")
    def on_event(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule triggered when something happens with this project.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8db4fa22a1e7f4a89388a71c35a59ec89da2ac98cefa54a118f992e365538cd3)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onEvent", [id, options]))

    @jsii.member(jsii_name="onPhaseChange")
    def on_phase_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule that triggers upon phase change of this build project.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__246f55059bc2f1d77c1603caae9d6b4fcfd25cbfefc44cc6e43cc1b5cbc5b751)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onPhaseChange", [id, options]))

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule triggered when the build project state changes.

        You can filter specific build status events using an event
        pattern filter on the ``build-status`` detail field::

           const rule = project.onStateChange('OnBuildStarted', { target });
           rule.addEventPattern({
             detail: {
               'build-status': [
                 "IN_PROGRESS",
                 "SUCCEEDED",
                 "FAILED",
                 "STOPPED"
               ]
             }
           });

        You can also use the methods ``onBuildFailed`` and ``onBuildSucceeded`` to define rules for
        these specific state changes.

        To access fields from the event in the event target input,
        use the static fields on the ``StateChangeEvent`` class.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85e9cef52515f8397e72addd577013713ff86ca6a000ef561afa3cabf0cd7381)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onStateChange", [id, options]))

    @jsii.member(jsii_name="validate")
    def _validate(self) -> typing.List[builtins.str]:
        '''Validate the current construct.

        This method can be implemented by derived constructs in order to perform
        validation logic. It is called on all constructs before synthesis.

        :override: true
        '''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "validate", []))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_67de8e8d.Connections:
        '''Access the Connections object.

        Will fail if this Project does not have a VPC set.
        '''
        return typing.cast(_aws_cdk_aws_ec2_67de8e8d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_940a1ce0.IPrincipal:
        '''The principal to grant permissions to.'''
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="projectArn")
    def project_arn(self) -> builtins.str:
        '''The ARN of the project.'''
        return typing.cast(builtins.str, jsii.get(self, "projectArn"))

    @builtins.property
    @jsii.member(jsii_name="projectName")
    def project_name(self) -> builtins.str:
        '''The name of the project.'''
        return typing.cast(builtins.str, jsii.get(self, "projectName"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole]:
        '''The IAM role for this project.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole], jsii.get(self, "role"))


@jsii.enum(jsii_type="@aws-cdk/aws-codebuild.ProjectNotificationEvents")
class ProjectNotificationEvents(enum.Enum):
    '''The list of event types for AWS Codebuild.

    :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-buildproject
    '''

    BUILD_FAILED = "BUILD_FAILED"
    '''Trigger notification when project build state failed.'''
    BUILD_SUCCEEDED = "BUILD_SUCCEEDED"
    '''Trigger notification when project build state succeeded.'''
    BUILD_IN_PROGRESS = "BUILD_IN_PROGRESS"
    '''Trigger notification when project build state in progress.'''
    BUILD_STOPPED = "BUILD_STOPPED"
    '''Trigger notification when project build state stopped.'''
    BUILD_PHASE_FAILED = "BUILD_PHASE_FAILED"
    '''Trigger notification when project build phase failure.'''
    BUILD_PHASE_SUCCEEDED = "BUILD_PHASE_SUCCEEDED"
    '''Trigger notification when project build phase success.'''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.ProjectNotifyOnOptions",
    jsii_struct_bases=[
        _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions
    ],
    name_mapping={
        "detail_type": "detailType",
        "enabled": "enabled",
        "notification_rule_name": "notificationRuleName",
        "events": "events",
    },
)
class ProjectNotifyOnOptions(
    _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions,
):
    def __init__(
        self,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
        events: typing.Sequence[ProjectNotificationEvents],
    ) -> None:
        '''Additional options to pass to the notification rule.

        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        :param events: A list of event types associated with this notification rule for CodeBuild Project. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            import aws_cdk.aws_codestarnotifications as codestarnotifications
            
            project_notify_on_options = codebuild.ProjectNotifyOnOptions(
                events=[codebuild.ProjectNotificationEvents.BUILD_FAILED],
            
                # the properties below are optional
                detail_type=codestarnotifications.DetailType.BASIC,
                enabled=False,
                notification_rule_name="notificationRuleName"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__261b4c92e6827a39b91fca1acd5bbf43152f2d44eec59299c1f72e806fa6066c)
            check_type(argname="argument detail_type", value=detail_type, expected_type=type_hints["detail_type"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument notification_rule_name", value=notification_rule_name, expected_type=type_hints["notification_rule_name"])
            check_type(argname="argument events", value=events, expected_type=type_hints["events"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "events": events,
        }
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if enabled is not None:
            self._values["enabled"] = enabled
        if notification_rule_name is not None:
            self._values["notification_rule_name"] = notification_rule_name

    @builtins.property
    def detail_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event as it would appear in AWS CloudWatch.
        FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created.

        :default: DetailType.FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''The status of the notification rule.

        If the enabled is set to DISABLED, notifications aren't sent for the notification rule.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def notification_rule_name(self) -> typing.Optional[builtins.str]:
        '''The name for the notification rule.

        Notification rule names must be unique in your AWS account.

        :default: - generated from the ``id``
        '''
        result = self._values.get("notification_rule_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def events(self) -> typing.List[ProjectNotificationEvents]:
        '''A list of event types associated with this notification rule for CodeBuild Project.

        For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#concepts-api
        '''
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[ProjectNotificationEvents], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectNotifyOnOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.ProjectProps",
    jsii_struct_bases=[CommonProjectProps],
    name_mapping={
        "allow_all_outbound": "allowAllOutbound",
        "badge": "badge",
        "build_spec": "buildSpec",
        "cache": "cache",
        "check_secrets_in_plain_text_env_variables": "checkSecretsInPlainTextEnvVariables",
        "concurrent_build_limit": "concurrentBuildLimit",
        "description": "description",
        "encryption_key": "encryptionKey",
        "environment": "environment",
        "environment_variables": "environmentVariables",
        "file_system_locations": "fileSystemLocations",
        "grant_report_group_permissions": "grantReportGroupPermissions",
        "logging": "logging",
        "project_name": "projectName",
        "queued_timeout": "queuedTimeout",
        "role": "role",
        "security_groups": "securityGroups",
        "subnet_selection": "subnetSelection",
        "timeout": "timeout",
        "vpc": "vpc",
        "artifacts": "artifacts",
        "secondary_artifacts": "secondaryArtifacts",
        "secondary_sources": "secondarySources",
        "source": "source",
    },
)
class ProjectProps(CommonProjectProps):
    def __init__(
        self,
        *,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        badge: typing.Optional[builtins.bool] = None,
        build_spec: typing.Optional[BuildSpec] = None,
        cache: typing.Optional[Cache] = None,
        check_secrets_in_plain_text_env_variables: typing.Optional[builtins.bool] = None,
        concurrent_build_limit: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
        environment: typing.Optional[typing.Union[BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
        file_system_locations: typing.Optional[typing.Sequence[IFileSystemLocation]] = None,
        grant_report_group_permissions: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[typing.Union[LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        project_name: typing.Optional[builtins.str] = None,
        queued_timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_67de8e8d.IVpc] = None,
        artifacts: typing.Optional[IArtifacts] = None,
        secondary_artifacts: typing.Optional[typing.Sequence[IArtifacts]] = None,
        secondary_sources: typing.Optional[typing.Sequence[ISource]] = None,
        source: typing.Optional[ISource] = None,
    ) -> None:
        '''
        :param allow_all_outbound: Whether to allow the CodeBuild to send all network traffic. If set to false, you must individually add traffic rules to allow the CodeBuild project to connect to network targets. Only used if 'vpc' is supplied. Default: true
        :param badge: Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge. For more information, see Build Badges Sample in the AWS CodeBuild User Guide. Default: false
        :param build_spec: Filename or contents of buildspec in JSON format. Default: - Empty buildspec.
        :param cache: Caching strategy to use. Default: Cache.none
        :param check_secrets_in_plain_text_env_variables: Whether to check for the presence of any secrets in the environment variables of the default type, BuildEnvironmentVariableType.PLAINTEXT. Since using a secret for the value of that kind of variable would result in it being displayed in plain text in the AWS Console, the construct will throw an exception if it detects a secret was passed there. Pass this property as false if you want to skip this validation, and keep using a secret in a plain text environment variable. Default: true
        :param concurrent_build_limit: Maximum number of concurrent builds. Minimum value is 1 and maximum is account build limit. Default: - no explicit limit is set
        :param description: A description of the project. Use the description to identify the purpose of the project. Default: - No description.
        :param encryption_key: Encryption key to use to read and write artifacts. Default: - The AWS-managed CMK for Amazon Simple Storage Service (Amazon S3) is used.
        :param environment: Build environment to use for the build. Default: BuildEnvironment.LinuxBuildImage.STANDARD_1_0
        :param environment_variables: Additional environment variables to add to the build environment. Default: - No additional environment variables are specified.
        :param file_system_locations: An ProjectFileSystemLocation objects for a CodeBuild build project. A ProjectFileSystemLocation object specifies the identifier, location, mountOptions, mountPoint, and type of a file system created using Amazon Elastic File System. Default: - no file system locations
        :param grant_report_group_permissions: Add permissions to this project's role to create and use test report groups with name starting with the name of this project. That is the standard report group that gets created when a simple name (in contrast to an ARN) is used in the 'reports' section of the buildspec of this project. This is usually harmless, but you can turn these off if you don't plan on using test reports in this project. Default: true
        :param logging: Information about logs for the build project. A project can create logs in Amazon CloudWatch Logs, an S3 bucket, or both. Default: - no log configuration is set
        :param project_name: The physical, human-readable name of the CodeBuild Project. Default: - Name is automatically generated.
        :param queued_timeout: The number of minutes after which AWS CodeBuild stops the build if it's still in queue. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: - no queue timeout is set
        :param role: Service Role to assume while running the build. Default: - A role will be created.
        :param security_groups: What security group to associate with the codebuild project's network interfaces. If no security group is identified, one will be created automatically. Only used if 'vpc' is supplied. Default: - Security group will be automatically created.
        :param subnet_selection: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Default: - All private subnets.
        :param timeout: The number of minutes after which AWS CodeBuild stops the build if it's not complete. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: Duration.hours(1)
        :param vpc: VPC network to place codebuild network interfaces. Specify this if the codebuild project needs to access resources in a VPC. Default: - No VPC is specified.
        :param artifacts: Defines where build artifacts will be stored. Could be: PipelineBuildArtifacts, NoArtifacts and S3Artifacts. Default: NoArtifacts
        :param secondary_artifacts: The secondary artifacts for the Project. Can also be added after the Project has been created by using the {@link Project#addSecondaryArtifact} method. Default: - No secondary artifacts.
        :param secondary_sources: The secondary sources for the Project. Can be also added after the Project has been created by using the {@link Project#addSecondarySource} method. Default: - No secondary sources.
        :param source: The source of the build. *Note*: if {@link NoSource} is given as the source, then you need to provide an explicit ``buildSpec``. Default: - NoSource

        :exampleMetadata: infused

        Example::

            # bucket: s3.Bucket
            
            
            project = codebuild.Project(self, "MyProject",
                build_spec=codebuild.BuildSpec.from_object({
                    "version": "0.2"
                }),
                artifacts=codebuild.Artifacts.s3(
                    bucket=bucket,
                    include_build_id=False,
                    package_zip=True,
                    path="another/path",
                    identifier="AddArtifact1"
                )
            )
        '''
        if isinstance(environment, dict):
            environment = BuildEnvironment(**environment)
        if isinstance(logging, dict):
            logging = LoggingOptions(**logging)
        if isinstance(subnet_selection, dict):
            subnet_selection = _aws_cdk_aws_ec2_67de8e8d.SubnetSelection(**subnet_selection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb596f44f7bf1ee04210a7fd27fb05beeb17f3c31a8afc3a224a7dc982c6d277)
            check_type(argname="argument allow_all_outbound", value=allow_all_outbound, expected_type=type_hints["allow_all_outbound"])
            check_type(argname="argument badge", value=badge, expected_type=type_hints["badge"])
            check_type(argname="argument build_spec", value=build_spec, expected_type=type_hints["build_spec"])
            check_type(argname="argument cache", value=cache, expected_type=type_hints["cache"])
            check_type(argname="argument check_secrets_in_plain_text_env_variables", value=check_secrets_in_plain_text_env_variables, expected_type=type_hints["check_secrets_in_plain_text_env_variables"])
            check_type(argname="argument concurrent_build_limit", value=concurrent_build_limit, expected_type=type_hints["concurrent_build_limit"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument environment_variables", value=environment_variables, expected_type=type_hints["environment_variables"])
            check_type(argname="argument file_system_locations", value=file_system_locations, expected_type=type_hints["file_system_locations"])
            check_type(argname="argument grant_report_group_permissions", value=grant_report_group_permissions, expected_type=type_hints["grant_report_group_permissions"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument project_name", value=project_name, expected_type=type_hints["project_name"])
            check_type(argname="argument queued_timeout", value=queued_timeout, expected_type=type_hints["queued_timeout"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnet_selection", value=subnet_selection, expected_type=type_hints["subnet_selection"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument artifacts", value=artifacts, expected_type=type_hints["artifacts"])
            check_type(argname="argument secondary_artifacts", value=secondary_artifacts, expected_type=type_hints["secondary_artifacts"])
            check_type(argname="argument secondary_sources", value=secondary_sources, expected_type=type_hints["secondary_sources"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if badge is not None:
            self._values["badge"] = badge
        if build_spec is not None:
            self._values["build_spec"] = build_spec
        if cache is not None:
            self._values["cache"] = cache
        if check_secrets_in_plain_text_env_variables is not None:
            self._values["check_secrets_in_plain_text_env_variables"] = check_secrets_in_plain_text_env_variables
        if concurrent_build_limit is not None:
            self._values["concurrent_build_limit"] = concurrent_build_limit
        if description is not None:
            self._values["description"] = description
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if environment is not None:
            self._values["environment"] = environment
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if file_system_locations is not None:
            self._values["file_system_locations"] = file_system_locations
        if grant_report_group_permissions is not None:
            self._values["grant_report_group_permissions"] = grant_report_group_permissions
        if logging is not None:
            self._values["logging"] = logging
        if project_name is not None:
            self._values["project_name"] = project_name
        if queued_timeout is not None:
            self._values["queued_timeout"] = queued_timeout
        if role is not None:
            self._values["role"] = role
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection
        if timeout is not None:
            self._values["timeout"] = timeout
        if vpc is not None:
            self._values["vpc"] = vpc
        if artifacts is not None:
            self._values["artifacts"] = artifacts
        if secondary_artifacts is not None:
            self._values["secondary_artifacts"] = secondary_artifacts
        if secondary_sources is not None:
            self._values["secondary_sources"] = secondary_sources
        if source is not None:
            self._values["source"] = source

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether to allow the CodeBuild to send all network traffic.

        If set to false, you must individually add traffic rules to allow the
        CodeBuild project to connect to network targets.

        Only used if 'vpc' is supplied.

        :default: true
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def badge(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge.

        For more information, see Build Badges Sample
        in the AWS CodeBuild User Guide.

        :default: false
        '''
        result = self._values.get("badge")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def build_spec(self) -> typing.Optional[BuildSpec]:
        '''Filename or contents of buildspec in JSON format.

        :default: - Empty buildspec.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec-ref-example
        '''
        result = self._values.get("build_spec")
        return typing.cast(typing.Optional[BuildSpec], result)

    @builtins.property
    def cache(self) -> typing.Optional[Cache]:
        '''Caching strategy to use.

        :default: Cache.none
        '''
        result = self._values.get("cache")
        return typing.cast(typing.Optional[Cache], result)

    @builtins.property
    def check_secrets_in_plain_text_env_variables(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''Whether to check for the presence of any secrets in the environment variables of the default type, BuildEnvironmentVariableType.PLAINTEXT. Since using a secret for the value of that kind of variable would result in it being displayed in plain text in the AWS Console, the construct will throw an exception if it detects a secret was passed there. Pass this property as false if you want to skip this validation, and keep using a secret in a plain text environment variable.

        :default: true
        '''
        result = self._values.get("check_secrets_in_plain_text_env_variables")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def concurrent_build_limit(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of concurrent builds.

        Minimum value is 1 and maximum is account build limit.

        :default: - no explicit limit is set
        '''
        result = self._values.get("concurrent_build_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the project.

        Use the description to identify the purpose
        of the project.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey]:
        '''Encryption key to use to read and write artifacts.

        :default: - The AWS-managed CMK for Amazon Simple Storage Service (Amazon S3) is used.
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey], result)

    @builtins.property
    def environment(self) -> typing.Optional[BuildEnvironment]:
        '''Build environment to use for the build.

        :default: BuildEnvironment.LinuxBuildImage.STANDARD_1_0
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[BuildEnvironment], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, BuildEnvironmentVariable]]:
        '''Additional environment variables to add to the build environment.

        :default: - No additional environment variables are specified.
        '''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, BuildEnvironmentVariable]], result)

    @builtins.property
    def file_system_locations(
        self,
    ) -> typing.Optional[typing.List[IFileSystemLocation]]:
        '''An  ProjectFileSystemLocation objects for a CodeBuild build project.

        A ProjectFileSystemLocation object specifies the identifier, location, mountOptions, mountPoint,
        and type of a file system created using Amazon Elastic File System.

        :default: - no file system locations
        '''
        result = self._values.get("file_system_locations")
        return typing.cast(typing.Optional[typing.List[IFileSystemLocation]], result)

    @builtins.property
    def grant_report_group_permissions(self) -> typing.Optional[builtins.bool]:
        '''Add permissions to this project's role to create and use test report groups with name starting with the name of this project.

        That is the standard report group that gets created when a simple name
        (in contrast to an ARN)
        is used in the 'reports' section of the buildspec of this project.
        This is usually harmless, but you can turn these off if you don't plan on using test
        reports in this project.

        :default: true

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/test-report-group-naming.html
        '''
        result = self._values.get("grant_report_group_permissions")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def logging(self) -> typing.Optional[LoggingOptions]:
        '''Information about logs for the build project.

        A project can create logs in Amazon CloudWatch Logs, an S3 bucket, or both.

        :default: - no log configuration is set
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[LoggingOptions], result)

    @builtins.property
    def project_name(self) -> typing.Optional[builtins.str]:
        '''The physical, human-readable name of the CodeBuild Project.

        :default: - Name is automatically generated.
        '''
        result = self._values.get("project_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def queued_timeout(self) -> typing.Optional[_aws_cdk_core_f4b25747.Duration]:
        '''The number of minutes after which AWS CodeBuild stops the build if it's still in queue.

        For valid values, see the timeoutInMinutes field in the AWS
        CodeBuild User Guide.

        :default: - no queue timeout is set
        '''
        result = self._values.get("queued_timeout")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Duration], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole]:
        '''Service Role to assume while running the build.

        :default: - A role will be created.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]]:
        '''What security group to associate with the codebuild project's network interfaces.

        If no security group is identified, one will be created automatically.

        Only used if 'vpc' is supplied.

        :default: - Security group will be automatically created.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]], result)

    @builtins.property
    def subnet_selection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection]:
        '''Where to place the network interfaces within the VPC.

        Only used if 'vpc' is supplied.

        :default: - All private subnets.
        '''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection], result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_core_f4b25747.Duration]:
        '''The number of minutes after which AWS CodeBuild stops the build if it's not complete.

        For valid values, see the timeoutInMinutes field in the AWS
        CodeBuild User Guide.

        :default: Duration.hours(1)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.Duration], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_67de8e8d.IVpc]:
        '''VPC network to place codebuild network interfaces.

        Specify this if the codebuild project needs to access resources in a VPC.

        :default: - No VPC is specified.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_67de8e8d.IVpc], result)

    @builtins.property
    def artifacts(self) -> typing.Optional[IArtifacts]:
        '''Defines where build artifacts will be stored.

        Could be: PipelineBuildArtifacts, NoArtifacts and S3Artifacts.

        :default: NoArtifacts
        '''
        result = self._values.get("artifacts")
        return typing.cast(typing.Optional[IArtifacts], result)

    @builtins.property
    def secondary_artifacts(self) -> typing.Optional[typing.List[IArtifacts]]:
        '''The secondary artifacts for the Project.

        Can also be added after the Project has been created by using the {@link Project#addSecondaryArtifact} method.

        :default: - No secondary artifacts.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-multi-in-out.html
        '''
        result = self._values.get("secondary_artifacts")
        return typing.cast(typing.Optional[typing.List[IArtifacts]], result)

    @builtins.property
    def secondary_sources(self) -> typing.Optional[typing.List[ISource]]:
        '''The secondary sources for the Project.

        Can be also added after the Project has been created by using the {@link Project#addSecondarySource} method.

        :default: - No secondary sources.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-multi-in-out.html
        '''
        result = self._values.get("secondary_sources")
        return typing.cast(typing.Optional[typing.List[ISource]], result)

    @builtins.property
    def source(self) -> typing.Optional[ISource]:
        '''The source of the build.

        *Note*: if {@link NoSource} is given as the source,
        then you need to provide an explicit ``buildSpec``.

        :default: - NoSource
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[ISource], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IReportGroup)
class ReportGroup(
    _aws_cdk_core_f4b25747.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.ReportGroup",
):
    '''The ReportGroup resource class.

    :exampleMetadata: infused

    Example::

        # source: codebuild.Source
        
        
        # create a new ReportGroup
        report_group = codebuild.ReportGroup(self, "ReportGroup")
        
        project = codebuild.Project(self, "Project",
            source=source,
            build_spec=codebuild.BuildSpec.from_object({
                # ...
                "reports": {
                    "report_group.report_group_arn": {
                        "files": "**/*",
                        "base-directory": "build/test-results"
                    }
                }
            })
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        export_bucket: typing.Optional[_aws_cdk_aws_s3_55f001a5.IBucket] = None,
        removal_policy: typing.Optional[_aws_cdk_core_f4b25747.RemovalPolicy] = None,
        report_group_name: typing.Optional[builtins.str] = None,
        zip_export: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param export_bucket: An optional S3 bucket to export the reports to. Default: - the reports will not be exported
        :param removal_policy: What to do when this resource is deleted from a stack. As CodeBuild does not allow deleting a ResourceGroup that has reports inside of it, this is set to retain the resource by default. Default: RemovalPolicy.RETAIN
        :param report_group_name: The physical name of the report group. Default: - CloudFormation-generated name
        :param zip_export: Whether to output the report files into the export bucket as-is, or create a ZIP from them before doing the export. Ignored if {@link exportBucket} has not been provided. Default: - false (the files will not be ZIPped)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5084e09c29dea6594ebe2b0196399f821b1c8f3d627c3fd8e226f72f0cfd70e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ReportGroupProps(
            export_bucket=export_bucket,
            removal_policy=removal_policy,
            report_group_name=report_group_name,
            zip_export=zip_export,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromReportGroupName")
    @builtins.classmethod
    def from_report_group_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        report_group_name: builtins.str,
    ) -> IReportGroup:
        '''Reference an existing ReportGroup, defined outside of the CDK code, by name.

        :param scope: -
        :param id: -
        :param report_group_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae1dfb374199c01d2a40ecaff114df8e9b45c1c27939848b34910b1a909a7a73)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument report_group_name", value=report_group_name, expected_type=type_hints["report_group_name"])
        return typing.cast(IReportGroup, jsii.sinvoke(cls, "fromReportGroupName", [scope, id, report_group_name]))

    @jsii.member(jsii_name="grantWrite")
    def grant_write(
        self,
        identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grants the given entity permissions to write (that is, upload reports to) this report group.

        :param identity: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b06acdc8442104d3009601c8f019726e615438c6024c4330707308af559d4617)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantWrite", [identity]))

    @builtins.property
    @jsii.member(jsii_name="reportGroupArn")
    def report_group_arn(self) -> builtins.str:
        '''The ARN of the ReportGroup.'''
        return typing.cast(builtins.str, jsii.get(self, "reportGroupArn"))

    @builtins.property
    @jsii.member(jsii_name="reportGroupName")
    def report_group_name(self) -> builtins.str:
        '''The name of the ReportGroup.'''
        return typing.cast(builtins.str, jsii.get(self, "reportGroupName"))

    @builtins.property
    @jsii.member(jsii_name="exportBucket")
    def _export_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_55f001a5.IBucket]:
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_55f001a5.IBucket], jsii.get(self, "exportBucket"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.ReportGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "export_bucket": "exportBucket",
        "removal_policy": "removalPolicy",
        "report_group_name": "reportGroupName",
        "zip_export": "zipExport",
    },
)
class ReportGroupProps:
    def __init__(
        self,
        *,
        export_bucket: typing.Optional[_aws_cdk_aws_s3_55f001a5.IBucket] = None,
        removal_policy: typing.Optional[_aws_cdk_core_f4b25747.RemovalPolicy] = None,
        report_group_name: typing.Optional[builtins.str] = None,
        zip_export: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Construction properties for {@link ReportGroup}.

        :param export_bucket: An optional S3 bucket to export the reports to. Default: - the reports will not be exported
        :param removal_policy: What to do when this resource is deleted from a stack. As CodeBuild does not allow deleting a ResourceGroup that has reports inside of it, this is set to retain the resource by default. Default: RemovalPolicy.RETAIN
        :param report_group_name: The physical name of the report group. Default: - CloudFormation-generated name
        :param zip_export: Whether to output the report files into the export bucket as-is, or create a ZIP from them before doing the export. Ignored if {@link exportBucket} has not been provided. Default: - false (the files will not be ZIPped)

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            import aws_cdk.aws_s3 as s3
            import aws_cdk.core as cdk
            
            # bucket: s3.Bucket
            
            report_group_props = codebuild.ReportGroupProps(
                export_bucket=bucket,
                removal_policy=cdk.RemovalPolicy.DESTROY,
                report_group_name="reportGroupName",
                zip_export=False
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__618621f2e819a5ad5cfa5615c17b87df5158db7d857e982c642debe0176fe99a)
            check_type(argname="argument export_bucket", value=export_bucket, expected_type=type_hints["export_bucket"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument report_group_name", value=report_group_name, expected_type=type_hints["report_group_name"])
            check_type(argname="argument zip_export", value=zip_export, expected_type=type_hints["zip_export"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if export_bucket is not None:
            self._values["export_bucket"] = export_bucket
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if report_group_name is not None:
            self._values["report_group_name"] = report_group_name
        if zip_export is not None:
            self._values["zip_export"] = zip_export

    @builtins.property
    def export_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_55f001a5.IBucket]:
        '''An optional S3 bucket to export the reports to.

        :default: - the reports will not be exported
        '''
        result = self._values.get("export_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_55f001a5.IBucket], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_core_f4b25747.RemovalPolicy]:
        '''What to do when this resource is deleted from a stack.

        As CodeBuild does not allow deleting a ResourceGroup that has reports inside of it,
        this is set to retain the resource by default.

        :default: RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_core_f4b25747.RemovalPolicy], result)

    @builtins.property
    def report_group_name(self) -> typing.Optional[builtins.str]:
        '''The physical name of the report group.

        :default: - CloudFormation-generated name
        '''
        result = self._values.get("report_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def zip_export(self) -> typing.Optional[builtins.bool]:
        '''Whether to output the report files into the export bucket as-is, or create a ZIP from them before doing the export.

        Ignored if {@link exportBucket} has not been provided.

        :default: - false (the files will not be ZIPped)
        '''
        result = self._values.get("zip_export")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ReportGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.S3ArtifactsProps",
    jsii_struct_bases=[ArtifactsProps],
    name_mapping={
        "identifier": "identifier",
        "bucket": "bucket",
        "encryption": "encryption",
        "include_build_id": "includeBuildId",
        "name": "name",
        "package_zip": "packageZip",
        "path": "path",
    },
)
class S3ArtifactsProps(ArtifactsProps):
    def __init__(
        self,
        *,
        identifier: typing.Optional[builtins.str] = None,
        bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
        encryption: typing.Optional[builtins.bool] = None,
        include_build_id: typing.Optional[builtins.bool] = None,
        name: typing.Optional[builtins.str] = None,
        package_zip: typing.Optional[builtins.bool] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Construction properties for {@link S3Artifacts}.

        :param identifier: The artifact identifier. This property is required on secondary artifacts.
        :param bucket: The name of the output bucket.
        :param encryption: If this is false, build output will not be encrypted. This is useful if the artifact to publish a static website or sharing content with others Default: true - output will be encrypted
        :param include_build_id: Indicates if the build ID should be included in the path. If this is set to true, then the build artifact will be stored in "//". Default: true
        :param name: The name of the build output ZIP file or folder inside the bucket. The full S3 object key will be "//" or "/" depending on whether ``includeBuildId`` is set to true. If not set, ``overrideArtifactName`` will be set and the name from the buildspec will be used instead. Default: undefined, and use the name from the buildspec
        :param package_zip: If this is true, all build output will be packaged into a single .zip file. Otherwise, all files will be uploaded to /. Default: true - files will be archived
        :param path: The path inside of the bucket for the build output .zip file or folder. If a value is not specified, then build output will be stored at the root of the bucket (or under the directory if ``includeBuildId`` is set to true). Default: the root of the bucket

        :exampleMetadata: infused

        Example::

            # bucket: s3.Bucket
            
            
            project = codebuild.Project(self, "MyProject",
                build_spec=codebuild.BuildSpec.from_object({
                    "version": "0.2"
                }),
                artifacts=codebuild.Artifacts.s3(
                    bucket=bucket,
                    include_build_id=False,
                    package_zip=True,
                    path="another/path",
                    identifier="AddArtifact1"
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29d210a9244c7e2ed346916796bcaae2a31a9aa62858134f50d4c24b761548f1)
            check_type(argname="argument identifier", value=identifier, expected_type=type_hints["identifier"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument include_build_id", value=include_build_id, expected_type=type_hints["include_build_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument package_zip", value=package_zip, expected_type=type_hints["package_zip"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
        }
        if identifier is not None:
            self._values["identifier"] = identifier
        if encryption is not None:
            self._values["encryption"] = encryption
        if include_build_id is not None:
            self._values["include_build_id"] = include_build_id
        if name is not None:
            self._values["name"] = name
        if package_zip is not None:
            self._values["package_zip"] = package_zip
        if path is not None:
            self._values["path"] = path

    @builtins.property
    def identifier(self) -> typing.Optional[builtins.str]:
        '''The artifact identifier.

        This property is required on secondary artifacts.
        '''
        result = self._values.get("identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_55f001a5.IBucket:
        '''The name of the output bucket.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_55f001a5.IBucket, result)

    @builtins.property
    def encryption(self) -> typing.Optional[builtins.bool]:
        '''If this is false, build output will not be encrypted.

        This is useful if the artifact to publish a static website or sharing content with others

        :default: true - output will be encrypted
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def include_build_id(self) -> typing.Optional[builtins.bool]:
        '''Indicates if the build ID should be included in the path.

        If this is set to true,
        then the build artifact will be stored in "//".

        :default: true
        '''
        result = self._values.get("include_build_id")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the build output ZIP file or folder inside the bucket.

        The full S3 object key will be "//" or
        "/" depending on whether ``includeBuildId`` is set to true.

        If not set, ``overrideArtifactName`` will be set and the name from the
        buildspec will be used instead.

        :default: undefined, and use the name from the buildspec
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def package_zip(self) -> typing.Optional[builtins.bool]:
        '''If this is true, all build output will be packaged into a single .zip file. Otherwise, all files will be uploaded to /.

        :default: true - files will be archived
        '''
        result = self._values.get("package_zip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''The path inside of the bucket for the build output .zip file or folder. If a value is not specified, then build output will be stored at the root of the bucket (or under the  directory if ``includeBuildId`` is set to true).

        :default: the root of the bucket
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ArtifactsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.S3LoggingOptions",
    jsii_struct_bases=[],
    name_mapping={
        "bucket": "bucket",
        "enabled": "enabled",
        "encrypted": "encrypted",
        "prefix": "prefix",
    },
)
class S3LoggingOptions:
    def __init__(
        self,
        *,
        bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
        enabled: typing.Optional[builtins.bool] = None,
        encrypted: typing.Optional[builtins.bool] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Information about logs built to an S3 bucket for a build project.

        :param bucket: The S3 Bucket to send logs to.
        :param enabled: The current status of the logs in Amazon CloudWatch Logs for a build project. Default: true
        :param encrypted: Encrypt the S3 build log output. Default: true
        :param prefix: The path prefix for S3 logs. Default: - no prefix

        :exampleMetadata: infused

        Example::

            codebuild.Project(self, "Project",
                logging=codebuild.LoggingOptions(
                    s3=codebuild.S3LoggingOptions(
                        bucket=s3.Bucket(self, "LogBucket")
                    )
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5621a023a0287c64dfb2886c1dce04b8b841ff2ae61ac61e57b7d3a98a19b1f6)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument encrypted", value=encrypted, expected_type=type_hints["encrypted"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
        }
        if enabled is not None:
            self._values["enabled"] = enabled
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_55f001a5.IBucket:
        '''The S3 Bucket to send logs to.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_55f001a5.IBucket, result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''The current status of the logs in Amazon CloudWatch Logs for a build project.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encrypted(self) -> typing.Optional[builtins.bool]:
        '''Encrypt the S3 build log output.

        :default: true
        '''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''The path prefix for S3 logs.

        :default: - no prefix
        '''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3LoggingOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(ISource)
class Source(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-codebuild.Source",
):
    '''Source provider definition for a CodeBuild Project.

    :exampleMetadata: infused

    Example::

        git_hub_source = codebuild.Source.git_hub(
            owner="awslabs",
            repo="aws-cdk",
            webhook=True,  # optional, default: true if `webhookFilters` were provided, false otherwise
            webhook_triggers_batch_build=True,  # optional, default is false
            webhook_filters=[
                codebuild.FilterGroup.in_event_of(codebuild.EventAction.PUSH).and_branch_is("master").and_commit_message_is("the commit message")
            ]
        )
    '''

    def __init__(self, *, identifier: typing.Optional[builtins.str] = None) -> None:
        '''
        :param identifier: The source identifier. This property is required on secondary sources.
        '''
        props = SourceProps(identifier=identifier)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bitBucket")
    @builtins.classmethod
    def bit_bucket(
        cls,
        *,
        owner: builtins.str,
        repo: builtins.str,
        branch_or_ref: typing.Optional[builtins.str] = None,
        build_status_name: typing.Optional[builtins.str] = None,
        build_status_url: typing.Optional[builtins.str] = None,
        clone_depth: typing.Optional[jsii.Number] = None,
        fetch_submodules: typing.Optional[builtins.bool] = None,
        report_build_status: typing.Optional[builtins.bool] = None,
        webhook: typing.Optional[builtins.bool] = None,
        webhook_filters: typing.Optional[typing.Sequence[FilterGroup]] = None,
        webhook_triggers_batch_build: typing.Optional[builtins.bool] = None,
        identifier: typing.Optional[builtins.str] = None,
    ) -> ISource:
        '''
        :param owner: The BitBucket account/user that owns the repo.
        :param repo: The name of the repo (without the username).
        :param branch_or_ref: The commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build. Default: the default branch's HEAD commit ID is used
        :param build_status_name: This parameter is used for the ``name`` parameter in the Bitbucket commit status. Can use built-in CodeBuild variables, like $AWS_REGION. Default: "AWS CodeBuild $AWS_REGION ($PROJECT_NAME)"
        :param build_status_url: The URL that the build will report back to the source provider. Can use built-in CodeBuild variables, like $AWS_REGION. Default: - link to the AWS Console for CodeBuild to a particular build execution
        :param clone_depth: The depth of history to download. Minimum value is 0. If this value is 0, greater than 25, or not provided, then the full history is downloaded with each build of the project.
        :param fetch_submodules: Whether to fetch submodules while cloning git repo. Default: false
        :param report_build_status: Whether to send notifications on your build's start and end. Default: true
        :param webhook: Whether to create a webhook that will trigger a build every time an event happens in the repository. Default: true if any ``webhookFilters`` were provided, false otherwise
        :param webhook_filters: A list of webhook filters that can constraint what events in the repository will trigger a build. A build is triggered if any of the provided filter groups match. Only valid if ``webhook`` was not provided as false. Default: every push and every Pull Request (create or update) triggers a build
        :param webhook_triggers_batch_build: Trigger a batch build from a webhook instead of a standard one. Enabling this will enable batch builds on the CodeBuild project. Default: false
        :param identifier: The source identifier. This property is required on secondary sources.
        '''
        props = BitBucketSourceProps(
            owner=owner,
            repo=repo,
            branch_or_ref=branch_or_ref,
            build_status_name=build_status_name,
            build_status_url=build_status_url,
            clone_depth=clone_depth,
            fetch_submodules=fetch_submodules,
            report_build_status=report_build_status,
            webhook=webhook,
            webhook_filters=webhook_filters,
            webhook_triggers_batch_build=webhook_triggers_batch_build,
            identifier=identifier,
        )

        return typing.cast(ISource, jsii.sinvoke(cls, "bitBucket", [props]))

    @jsii.member(jsii_name="codeCommit")
    @builtins.classmethod
    def code_commit(
        cls,
        *,
        repository: _aws_cdk_aws_codecommit_692dd32c.IRepository,
        branch_or_ref: typing.Optional[builtins.str] = None,
        clone_depth: typing.Optional[jsii.Number] = None,
        fetch_submodules: typing.Optional[builtins.bool] = None,
        identifier: typing.Optional[builtins.str] = None,
    ) -> ISource:
        '''
        :param repository: 
        :param branch_or_ref: The commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build. Default: the default branch's HEAD commit ID is used
        :param clone_depth: The depth of history to download. Minimum value is 0. If this value is 0, greater than 25, or not provided, then the full history is downloaded with each build of the project.
        :param fetch_submodules: Whether to fetch submodules while cloning git repo. Default: false
        :param identifier: The source identifier. This property is required on secondary sources.
        '''
        props = CodeCommitSourceProps(
            repository=repository,
            branch_or_ref=branch_or_ref,
            clone_depth=clone_depth,
            fetch_submodules=fetch_submodules,
            identifier=identifier,
        )

        return typing.cast(ISource, jsii.sinvoke(cls, "codeCommit", [props]))

    @jsii.member(jsii_name="gitHub")
    @builtins.classmethod
    def git_hub(
        cls,
        *,
        owner: builtins.str,
        repo: builtins.str,
        branch_or_ref: typing.Optional[builtins.str] = None,
        build_status_context: typing.Optional[builtins.str] = None,
        build_status_url: typing.Optional[builtins.str] = None,
        clone_depth: typing.Optional[jsii.Number] = None,
        fetch_submodules: typing.Optional[builtins.bool] = None,
        report_build_status: typing.Optional[builtins.bool] = None,
        webhook: typing.Optional[builtins.bool] = None,
        webhook_filters: typing.Optional[typing.Sequence[FilterGroup]] = None,
        webhook_triggers_batch_build: typing.Optional[builtins.bool] = None,
        identifier: typing.Optional[builtins.str] = None,
    ) -> ISource:
        '''
        :param owner: The GitHub account/user that owns the repo.
        :param repo: The name of the repo (without the username).
        :param branch_or_ref: The commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build. Default: the default branch's HEAD commit ID is used
        :param build_status_context: This parameter is used for the ``context`` parameter in the GitHub commit status. Can use built-in CodeBuild variables, like $AWS_REGION. Default: "AWS CodeBuild $AWS_REGION ($PROJECT_NAME)"
        :param build_status_url: The URL that the build will report back to the source provider. Can use built-in CodeBuild variables, like $AWS_REGION. Default: - link to the AWS Console for CodeBuild to a particular build execution
        :param clone_depth: The depth of history to download. Minimum value is 0. If this value is 0, greater than 25, or not provided, then the full history is downloaded with each build of the project.
        :param fetch_submodules: Whether to fetch submodules while cloning git repo. Default: false
        :param report_build_status: Whether to send notifications on your build's start and end. Default: true
        :param webhook: Whether to create a webhook that will trigger a build every time an event happens in the repository. Default: true if any ``webhookFilters`` were provided, false otherwise
        :param webhook_filters: A list of webhook filters that can constraint what events in the repository will trigger a build. A build is triggered if any of the provided filter groups match. Only valid if ``webhook`` was not provided as false. Default: every push and every Pull Request (create or update) triggers a build
        :param webhook_triggers_batch_build: Trigger a batch build from a webhook instead of a standard one. Enabling this will enable batch builds on the CodeBuild project. Default: false
        :param identifier: The source identifier. This property is required on secondary sources.
        '''
        props = GitHubSourceProps(
            owner=owner,
            repo=repo,
            branch_or_ref=branch_or_ref,
            build_status_context=build_status_context,
            build_status_url=build_status_url,
            clone_depth=clone_depth,
            fetch_submodules=fetch_submodules,
            report_build_status=report_build_status,
            webhook=webhook,
            webhook_filters=webhook_filters,
            webhook_triggers_batch_build=webhook_triggers_batch_build,
            identifier=identifier,
        )

        return typing.cast(ISource, jsii.sinvoke(cls, "gitHub", [props]))

    @jsii.member(jsii_name="gitHubEnterprise")
    @builtins.classmethod
    def git_hub_enterprise(
        cls,
        *,
        https_clone_url: builtins.str,
        branch_or_ref: typing.Optional[builtins.str] = None,
        build_status_context: typing.Optional[builtins.str] = None,
        build_status_url: typing.Optional[builtins.str] = None,
        clone_depth: typing.Optional[jsii.Number] = None,
        fetch_submodules: typing.Optional[builtins.bool] = None,
        ignore_ssl_errors: typing.Optional[builtins.bool] = None,
        report_build_status: typing.Optional[builtins.bool] = None,
        webhook: typing.Optional[builtins.bool] = None,
        webhook_filters: typing.Optional[typing.Sequence[FilterGroup]] = None,
        webhook_triggers_batch_build: typing.Optional[builtins.bool] = None,
        identifier: typing.Optional[builtins.str] = None,
    ) -> ISource:
        '''
        :param https_clone_url: The HTTPS URL of the repository in your GitHub Enterprise installation.
        :param branch_or_ref: The commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build. Default: the default branch's HEAD commit ID is used
        :param build_status_context: This parameter is used for the ``context`` parameter in the GitHub commit status. Can use built-in CodeBuild variables, like $AWS_REGION. Default: "AWS CodeBuild $AWS_REGION ($PROJECT_NAME)"
        :param build_status_url: The URL that the build will report back to the source provider. Can use built-in CodeBuild variables, like $AWS_REGION. Default: - link to the AWS Console for CodeBuild to a particular build execution
        :param clone_depth: The depth of history to download. Minimum value is 0. If this value is 0, greater than 25, or not provided, then the full history is downloaded with each build of the project.
        :param fetch_submodules: Whether to fetch submodules while cloning git repo. Default: false
        :param ignore_ssl_errors: Whether to ignore SSL errors when connecting to the repository. Default: false
        :param report_build_status: Whether to send notifications on your build's start and end. Default: true
        :param webhook: Whether to create a webhook that will trigger a build every time an event happens in the repository. Default: true if any ``webhookFilters`` were provided, false otherwise
        :param webhook_filters: A list of webhook filters that can constraint what events in the repository will trigger a build. A build is triggered if any of the provided filter groups match. Only valid if ``webhook`` was not provided as false. Default: every push and every Pull Request (create or update) triggers a build
        :param webhook_triggers_batch_build: Trigger a batch build from a webhook instead of a standard one. Enabling this will enable batch builds on the CodeBuild project. Default: false
        :param identifier: The source identifier. This property is required on secondary sources.
        '''
        props = GitHubEnterpriseSourceProps(
            https_clone_url=https_clone_url,
            branch_or_ref=branch_or_ref,
            build_status_context=build_status_context,
            build_status_url=build_status_url,
            clone_depth=clone_depth,
            fetch_submodules=fetch_submodules,
            ignore_ssl_errors=ignore_ssl_errors,
            report_build_status=report_build_status,
            webhook=webhook,
            webhook_filters=webhook_filters,
            webhook_triggers_batch_build=webhook_triggers_batch_build,
            identifier=identifier,
        )

        return typing.cast(ISource, jsii.sinvoke(cls, "gitHubEnterprise", [props]))

    @jsii.member(jsii_name="s3")
    @builtins.classmethod
    def s3(
        cls,
        *,
        bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
        path: builtins.str,
        version: typing.Optional[builtins.str] = None,
        identifier: typing.Optional[builtins.str] = None,
    ) -> ISource:
        '''
        :param bucket: 
        :param path: 
        :param version: The version ID of the object that represents the build input ZIP file to use. Default: latest
        :param identifier: The source identifier. This property is required on secondary sources.
        '''
        props = S3SourceProps(
            bucket=bucket, path=path, version=version, identifier=identifier
        )

        return typing.cast(ISource, jsii.sinvoke(cls, "s3", [props]))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _aws_cdk_core_f4b25747.Construct,
        _project: IProject,
    ) -> "SourceConfig":
        '''Called by the project when the source is added so that the source can perform binding operations on the source.

        For example, it can grant permissions to the
        code build project to read from the S3 bucket.

        :param _scope: -
        :param _project: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__958faeefce502b7ab214d99d2b1b31d489fc6afa94ef7c7df40092541335d648)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
            check_type(argname="argument _project", value=_project, expected_type=type_hints["_project"])
        return typing.cast("SourceConfig", jsii.invoke(self, "bind", [_scope, _project]))

    @builtins.property
    @jsii.member(jsii_name="badgeSupported")
    def badge_supported(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "badgeSupported"))

    @builtins.property
    @jsii.member(jsii_name="type")
    @abc.abstractmethod
    def type(self) -> builtins.str:
        ...

    @builtins.property
    @jsii.member(jsii_name="identifier")
    def identifier(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identifier"))


class _SourceProxy(Source):
    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Source).__jsii_proxy_class__ = lambda : _SourceProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.SourceConfig",
    jsii_struct_bases=[],
    name_mapping={
        "source_property": "sourceProperty",
        "build_triggers": "buildTriggers",
        "source_version": "sourceVersion",
    },
)
class SourceConfig:
    def __init__(
        self,
        *,
        source_property: typing.Union[CfnProject.SourceProperty, typing.Dict[builtins.str, typing.Any]],
        build_triggers: typing.Optional[typing.Union[CfnProject.ProjectTriggersProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        source_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''The type returned from {@link ISource#bind}.

        :param source_property: 
        :param build_triggers: 
        :param source_version: ``AWS::CodeBuild::Project.SourceVersion``. Default: the latest version

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            
            source_config = codebuild.SourceConfig(
                source_property=codebuild.CfnProject.SourceProperty(
                    type="type",
            
                    # the properties below are optional
                    auth=codebuild.CfnProject.SourceAuthProperty(
                        type="type",
            
                        # the properties below are optional
                        resource="resource"
                    ),
                    build_spec="buildSpec",
                    build_status_config=codebuild.CfnProject.BuildStatusConfigProperty(
                        context="context",
                        target_url="targetUrl"
                    ),
                    git_clone_depth=123,
                    git_submodules_config=codebuild.CfnProject.GitSubmodulesConfigProperty(
                        fetch_submodules=False
                    ),
                    insecure_ssl=False,
                    location="location",
                    report_build_status=False,
                    source_identifier="sourceIdentifier"
                ),
            
                # the properties below are optional
                build_triggers=codebuild.CfnProject.ProjectTriggersProperty(
                    build_type="buildType",
                    filter_groups=[[codebuild.CfnProject.WebhookFilterProperty(
                        pattern="pattern",
                        type="type",
            
                        # the properties below are optional
                        exclude_matched_pattern=False
                    )]],
                    webhook=False
                ),
                source_version="sourceVersion"
            )
        '''
        if isinstance(source_property, dict):
            source_property = CfnProject.SourceProperty(**source_property)
        if isinstance(build_triggers, dict):
            build_triggers = CfnProject.ProjectTriggersProperty(**build_triggers)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27104d913f02d5d417aab88b4c03f348283cb39c47953205e4621768c52ee4a3)
            check_type(argname="argument source_property", value=source_property, expected_type=type_hints["source_property"])
            check_type(argname="argument build_triggers", value=build_triggers, expected_type=type_hints["build_triggers"])
            check_type(argname="argument source_version", value=source_version, expected_type=type_hints["source_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "source_property": source_property,
        }
        if build_triggers is not None:
            self._values["build_triggers"] = build_triggers
        if source_version is not None:
            self._values["source_version"] = source_version

    @builtins.property
    def source_property(self) -> CfnProject.SourceProperty:
        result = self._values.get("source_property")
        assert result is not None, "Required property 'source_property' is missing"
        return typing.cast(CfnProject.SourceProperty, result)

    @builtins.property
    def build_triggers(self) -> typing.Optional[CfnProject.ProjectTriggersProperty]:
        result = self._values.get("build_triggers")
        return typing.cast(typing.Optional[CfnProject.ProjectTriggersProperty], result)

    @builtins.property
    def source_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodeBuild::Project.SourceVersion``.

        :default: the latest version

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codebuild-project.html#cfn-codebuild-project-sourceversion
        '''
        result = self._values.get("source_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.SourceProps",
    jsii_struct_bases=[],
    name_mapping={"identifier": "identifier"},
)
class SourceProps:
    def __init__(self, *, identifier: typing.Optional[builtins.str] = None) -> None:
        '''Properties common to all Source classes.

        :param identifier: The source identifier. This property is required on secondary sources.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            
            source_props = codebuild.SourceProps(
                identifier="identifier"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abf86ff362340269c6878410401499accc558bb0b687f458dace50f3d7e6bf96)
            check_type(argname="argument identifier", value=identifier, expected_type=type_hints["identifier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if identifier is not None:
            self._values["identifier"] = identifier

    @builtins.property
    def identifier(self) -> typing.Optional[builtins.str]:
        '''The source identifier.

        This property is required on secondary sources.
        '''
        result = self._values.get("identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StateChangeEvent(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.StateChangeEvent",
):
    '''Event fields for the CodeBuild "state change" event.

    :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-build-notifications.html#sample-build-notifications-ref
    '''

    @jsii.python.classproperty
    @jsii.member(jsii_name="buildId")
    def build_id(cls) -> builtins.str:
        '''Return the build id.'''
        return typing.cast(builtins.str, jsii.sget(cls, "buildId"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="buildStatus")
    def build_status(cls) -> builtins.str:
        '''The triggering build's status.'''
        return typing.cast(builtins.str, jsii.sget(cls, "buildStatus"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="currentPhase")
    def current_phase(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "currentPhase"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="projectName")
    def project_name(cls) -> builtins.str:
        '''The triggering build's project name.'''
        return typing.cast(builtins.str, jsii.sget(cls, "projectName"))


class UntrustedCodeBoundaryPolicy(
    _aws_cdk_aws_iam_940a1ce0.ManagedPolicy,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.UntrustedCodeBoundaryPolicy",
):
    '''Permissions Boundary for a CodeBuild Project running untrusted code.

    This class is a Policy, intended to be used as a Permissions Boundary
    for a CodeBuild project. It allows most of the actions necessary to run
    the CodeBuild project, but disallows reading from Parameter Store
    and Secrets Manager.

    Use this when your CodeBuild project is running untrusted code (for
    example, if you are using one to automatically build Pull Requests
    that anyone can submit), and you want to prevent your future self
    from accidentally exposing Secrets to this build.

    (The reason you might want to do this is because otherwise anyone
    who can submit a Pull Request to your project can write a script
    to email those secrets to themselves).

    Example::

        # project: codebuild.Project
        
        iam.PermissionsBoundary.of(project).apply(codebuild.UntrustedCodeBoundaryPolicy(self, "Boundary"))
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        additional_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_940a1ce0.PolicyStatement]] = None,
        managed_policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param additional_statements: Additional statements to add to the default set of statements. Default: - No additional statements
        :param managed_policy_name: The name of the managed policy. Default: - A name is automatically generated.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec25dd855c00da90e76a93e2f29685952fa5a3d32ab8aeb1d36b2fe96d974433)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = UntrustedCodeBoundaryPolicyProps(
            additional_statements=additional_statements,
            managed_policy_name=managed_policy_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.UntrustedCodeBoundaryPolicyProps",
    jsii_struct_bases=[],
    name_mapping={
        "additional_statements": "additionalStatements",
        "managed_policy_name": "managedPolicyName",
    },
)
class UntrustedCodeBoundaryPolicyProps:
    def __init__(
        self,
        *,
        additional_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_940a1ce0.PolicyStatement]] = None,
        managed_policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Construction properties for UntrustedCodeBoundaryPolicy.

        :param additional_statements: Additional statements to add to the default set of statements. Default: - No additional statements
        :param managed_policy_name: The name of the managed policy. Default: - A name is automatically generated.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codebuild as codebuild
            import aws_cdk.aws_iam as iam
            
            # policy_statement: iam.PolicyStatement
            
            untrusted_code_boundary_policy_props = codebuild.UntrustedCodeBoundaryPolicyProps(
                additional_statements=[policy_statement],
                managed_policy_name="managedPolicyName"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9600200b19e2f4c8ae29f91bd7eaa6740b5e735df5f8937ef3281d6d71ef6073)
            check_type(argname="argument additional_statements", value=additional_statements, expected_type=type_hints["additional_statements"])
            check_type(argname="argument managed_policy_name", value=managed_policy_name, expected_type=type_hints["managed_policy_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if additional_statements is not None:
            self._values["additional_statements"] = additional_statements
        if managed_policy_name is not None:
            self._values["managed_policy_name"] = managed_policy_name

    @builtins.property
    def additional_statements(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_940a1ce0.PolicyStatement]]:
        '''Additional statements to add to the default set of statements.

        :default: - No additional statements
        '''
        result = self._values.get("additional_statements")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_940a1ce0.PolicyStatement]], result)

    @builtins.property
    def managed_policy_name(self) -> typing.Optional[builtins.str]:
        '''The name of the managed policy.

        :default: - A name is automatically generated.
        '''
        result = self._values.get("managed_policy_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UntrustedCodeBoundaryPolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IBuildImage)
class WindowsBuildImage(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.WindowsBuildImage",
):
    '''A CodeBuild image running Windows.

    This class has a bunch of public constants that represent the most popular images.

    You can also specify a custom image using one of the static methods:

    - WindowsBuildImage.fromDockerRegistry(image[, { secretsManagerCredentials }, imageType])
    - WindowsBuildImage.fromEcrRepository(repo[, tag, imageType])
    - WindowsBuildImage.fromAsset(parent, id, props, [, imageType])

    :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-available.html
    :exampleMetadata: infused

    Example::

        # ecr_repository: ecr.Repository
        
        
        codebuild.Project(self, "Project",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.WindowsBuildImage.from_ecr_repository(ecr_repository, "v1.0", codebuild.WindowsImageType.SERVER_2019),
                # optional certificate to include in the build image
                certificate=codebuild.BuildEnvironmentCertificate(
                    bucket=s3.Bucket.from_bucket_name(self, "Bucket", "my-bucket"),
                    object_key="path/to/cert.pem"
                )
            )
        )
    '''

    @jsii.member(jsii_name="fromAsset")
    @builtins.classmethod
    def from_asset(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: typing.Union[_aws_cdk_aws_ecr_assets_ef09b699.DockerImageAssetProps, typing.Dict[builtins.str, typing.Any]],
        image_type: typing.Optional["WindowsImageType"] = None,
    ) -> IBuildImage:
        '''Uses an Docker image asset as a Windows build image.

        :param scope: -
        :param id: -
        :param props: -
        :param image_type: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbb26183c1276596779e68e902e47f41c05c8edb53f62d770edb65862844c26d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
            check_type(argname="argument image_type", value=image_type, expected_type=type_hints["image_type"])
        return typing.cast(IBuildImage, jsii.sinvoke(cls, "fromAsset", [scope, id, props, image_type]))

    @jsii.member(jsii_name="fromDockerRegistry")
    @builtins.classmethod
    def from_docker_registry(
        cls,
        name: builtins.str,
        options: typing.Optional[typing.Union[DockerImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        image_type: typing.Optional["WindowsImageType"] = None,
    ) -> IBuildImage:
        '''
        :param name: -
        :param options: -
        :param image_type: -

        :return: a Windows build image from a Docker Hub image.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64b2dc590fc0bfdff5235bade85135f8d593e76022e4fe45e5c12f871aa6aba3)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
            check_type(argname="argument image_type", value=image_type, expected_type=type_hints["image_type"])
        return typing.cast(IBuildImage, jsii.sinvoke(cls, "fromDockerRegistry", [name, options, image_type]))

    @jsii.member(jsii_name="fromEcrRepository")
    @builtins.classmethod
    def from_ecr_repository(
        cls,
        repository: _aws_cdk_aws_ecr_093ed842.IRepository,
        tag_or_digest: typing.Optional[builtins.str] = None,
        image_type: typing.Optional["WindowsImageType"] = None,
    ) -> IBuildImage:
        '''
        :param repository: The ECR repository.
        :param tag_or_digest: Image tag or digest (default "latest", digests must start with ``sha256:``).
        :param image_type: -

        :return:

        A Windows build image from an ECR repository.

        NOTE: if the repository is external (i.e. imported), then we won't be able to add
        a resource policy statement for it so CodeBuild can pull the image.

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-ecr.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cffd3f58ab48407a015f49afb05420e0ba5e3113cf2b4f0d328b3e3b85b4b92d)
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument tag_or_digest", value=tag_or_digest, expected_type=type_hints["tag_or_digest"])
            check_type(argname="argument image_type", value=image_type, expected_type=type_hints["image_type"])
        return typing.cast(IBuildImage, jsii.sinvoke(cls, "fromEcrRepository", [repository, tag_or_digest, image_type]))

    @jsii.member(jsii_name="runScriptBuildspec")
    def run_script_buildspec(self, entrypoint: builtins.str) -> BuildSpec:
        '''Make a buildspec to run the indicated script.

        :param entrypoint: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d28327d3567761be5c82ad17ec064753844bcca0921b5f1705a425b310fa6bcd)
            check_type(argname="argument entrypoint", value=entrypoint, expected_type=type_hints["entrypoint"])
        return typing.cast(BuildSpec, jsii.invoke(self, "runScriptBuildspec", [entrypoint]))

    @jsii.member(jsii_name="validate")
    def validate(
        self,
        *,
        build_image: typing.Optional[IBuildImage] = None,
        certificate: typing.Optional[typing.Union[BuildEnvironmentCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
        compute_type: typing.Optional[ComputeType] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
        privileged: typing.Optional[builtins.bool] = None,
    ) -> typing.List[builtins.str]:
        '''Allows the image a chance to validate whether the passed configuration is correct.

        :param build_image: The image used for the builds. Default: LinuxBuildImage.STANDARD_1_0
        :param certificate: The location of the PEM-encoded certificate for the build project. Default: - No external certificate is added to the project
        :param compute_type: The type of compute to use for this build. See the {@link ComputeType} enum for the possible values. Default: taken from {@link #buildImage#defaultComputeType}
        :param environment_variables: The environment variables that your builds can use.
        :param privileged: Indicates how the project builds Docker images. Specify true to enable running the Docker daemon inside a Docker container. This value must be set to true only if this build project will be used to build Docker images, and the specified build environment image is not one provided by AWS CodeBuild with Docker support. Otherwise, all associated builds that attempt to interact with the Docker daemon will fail. Default: false
        '''
        build_environment = BuildEnvironment(
            build_image=build_image,
            certificate=certificate,
            compute_type=compute_type,
            environment_variables=environment_variables,
            privileged=privileged,
        )

        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "validate", [build_environment]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="WIN_SERVER_CORE_2016_BASE")
    def WIN_SERVER_CORE_2016_BASE(cls) -> IBuildImage:
        '''(deprecated) Corresponds to the standard CodeBuild image ``aws/codebuild/windows-base:1.0``.

        :deprecated: ``WindowsBuildImage.WINDOWS_BASE_2_0`` should be used instead.

        :stability: deprecated
        '''
        return typing.cast(IBuildImage, jsii.sget(cls, "WIN_SERVER_CORE_2016_BASE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="WIN_SERVER_CORE_2019_BASE")
    def WIN_SERVER_CORE_2019_BASE(cls) -> IBuildImage:
        '''The standard CodeBuild image ``aws/codebuild/windows-base:2019-1.0``, which is based off Windows Server Core 2019.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "WIN_SERVER_CORE_2019_BASE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="WINDOWS_BASE_2_0")
    def WINDOWS_BASE_2_0(cls) -> IBuildImage:
        '''The standard CodeBuild image ``aws/codebuild/windows-base:2.0``, which is based off Windows Server Core 2016.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "WINDOWS_BASE_2_0"))

    @builtins.property
    @jsii.member(jsii_name="defaultComputeType")
    def default_compute_type(self) -> ComputeType:
        '''The default {@link ComputeType} to use with this image, if one was not specified in {@link BuildEnvironment#computeType} explicitly.'''
        return typing.cast(ComputeType, jsii.get(self, "defaultComputeType"))

    @builtins.property
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> builtins.str:
        '''The Docker image identifier that the build environment uses.'''
        return typing.cast(builtins.str, jsii.get(self, "imageId"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''The type of build environment.'''
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="imagePullPrincipalType")
    def image_pull_principal_type(self) -> typing.Optional[ImagePullPrincipalType]:
        '''The type of principal that CodeBuild will use to pull this build Docker image.'''
        return typing.cast(typing.Optional[ImagePullPrincipalType], jsii.get(self, "imagePullPrincipalType"))

    @builtins.property
    @jsii.member(jsii_name="repository")
    def repository(self) -> typing.Optional[_aws_cdk_aws_ecr_093ed842.IRepository]:
        '''An optional ECR repository that the image is hosted in.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_ecr_093ed842.IRepository], jsii.get(self, "repository"))

    @builtins.property
    @jsii.member(jsii_name="secretsManagerCredentials")
    def secrets_manager_credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_72af8d6f.ISecret]:
        '''The secretsManagerCredentials for access to a private registry.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_72af8d6f.ISecret], jsii.get(self, "secretsManagerCredentials"))


@jsii.enum(jsii_type="@aws-cdk/aws-codebuild.WindowsImageType")
class WindowsImageType(enum.Enum):
    '''Environment type for Windows Docker images.

    :exampleMetadata: infused

    Example::

        # ecr_repository: ecr.Repository
        
        
        codebuild.Project(self, "Project",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.WindowsBuildImage.from_ecr_repository(ecr_repository, "v1.0", codebuild.WindowsImageType.SERVER_2019),
                # optional certificate to include in the build image
                certificate=codebuild.BuildEnvironmentCertificate(
                    bucket=s3.Bucket.from_bucket_name(self, "Bucket", "my-bucket"),
                    object_key="path/to/cert.pem"
                )
            )
        )
    '''

    STANDARD = "STANDARD"
    '''The standard environment type, WINDOWS_CONTAINER.'''
    SERVER_2019 = "SERVER_2019"
    '''The WINDOWS_SERVER_2019_CONTAINER environment type.'''


@jsii.implements(IArtifacts)
class Artifacts(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-codebuild.Artifacts",
):
    '''Artifacts definition for a CodeBuild Project.

    :exampleMetadata: infused

    Example::

        # bucket: s3.Bucket
        
        
        project = codebuild.Project(self, "MyProject",
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2"
            }),
            artifacts=codebuild.Artifacts.s3(
                bucket=bucket,
                include_build_id=False,
                package_zip=True,
                path="another/path",
                identifier="AddArtifact1"
            )
        )
    '''

    def __init__(self, *, identifier: typing.Optional[builtins.str] = None) -> None:
        '''
        :param identifier: The artifact identifier. This property is required on secondary artifacts.
        '''
        props = ArtifactsProps(identifier=identifier)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="s3")
    @builtins.classmethod
    def s3(
        cls,
        *,
        bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
        encryption: typing.Optional[builtins.bool] = None,
        include_build_id: typing.Optional[builtins.bool] = None,
        name: typing.Optional[builtins.str] = None,
        package_zip: typing.Optional[builtins.bool] = None,
        path: typing.Optional[builtins.str] = None,
        identifier: typing.Optional[builtins.str] = None,
    ) -> IArtifacts:
        '''
        :param bucket: The name of the output bucket.
        :param encryption: If this is false, build output will not be encrypted. This is useful if the artifact to publish a static website or sharing content with others Default: true - output will be encrypted
        :param include_build_id: Indicates if the build ID should be included in the path. If this is set to true, then the build artifact will be stored in "//". Default: true
        :param name: The name of the build output ZIP file or folder inside the bucket. The full S3 object key will be "//" or "/" depending on whether ``includeBuildId`` is set to true. If not set, ``overrideArtifactName`` will be set and the name from the buildspec will be used instead. Default: undefined, and use the name from the buildspec
        :param package_zip: If this is true, all build output will be packaged into a single .zip file. Otherwise, all files will be uploaded to /. Default: true - files will be archived
        :param path: The path inside of the bucket for the build output .zip file or folder. If a value is not specified, then build output will be stored at the root of the bucket (or under the directory if ``includeBuildId`` is set to true). Default: the root of the bucket
        :param identifier: The artifact identifier. This property is required on secondary artifacts.
        '''
        props = S3ArtifactsProps(
            bucket=bucket,
            encryption=encryption,
            include_build_id=include_build_id,
            name=name,
            package_zip=package_zip,
            path=path,
            identifier=identifier,
        )

        return typing.cast(IArtifacts, jsii.sinvoke(cls, "s3", [props]))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: _aws_cdk_core_f4b25747.Construct,
        _project: IProject,
    ) -> ArtifactsConfig:
        '''Callback when an Artifacts class is used in a CodeBuild Project.

        :param _scope: -
        :param _project: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__568d47ea3ff175a778eb09e742c96e61f270bd341d8b1ea9ca0df3d06d07294c)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
            check_type(argname="argument _project", value=_project, expected_type=type_hints["_project"])
        return typing.cast(ArtifactsConfig, jsii.invoke(self, "bind", [_scope, _project]))

    @builtins.property
    @jsii.member(jsii_name="type")
    @abc.abstractmethod
    def type(self) -> builtins.str:
        '''The CodeBuild type of this artifact.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="identifier")
    def identifier(self) -> typing.Optional[builtins.str]:
        '''The artifact identifier.

        This property is required on secondary artifacts.
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identifier"))


class _ArtifactsProxy(Artifacts):
    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''The CodeBuild type of this artifact.'''
        return typing.cast(builtins.str, jsii.get(self, "type"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Artifacts).__jsii_proxy_class__ = lambda : _ArtifactsProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.BitBucketSourceProps",
    jsii_struct_bases=[SourceProps],
    name_mapping={
        "identifier": "identifier",
        "owner": "owner",
        "repo": "repo",
        "branch_or_ref": "branchOrRef",
        "build_status_name": "buildStatusName",
        "build_status_url": "buildStatusUrl",
        "clone_depth": "cloneDepth",
        "fetch_submodules": "fetchSubmodules",
        "report_build_status": "reportBuildStatus",
        "webhook": "webhook",
        "webhook_filters": "webhookFilters",
        "webhook_triggers_batch_build": "webhookTriggersBatchBuild",
    },
)
class BitBucketSourceProps(SourceProps):
    def __init__(
        self,
        *,
        identifier: typing.Optional[builtins.str] = None,
        owner: builtins.str,
        repo: builtins.str,
        branch_or_ref: typing.Optional[builtins.str] = None,
        build_status_name: typing.Optional[builtins.str] = None,
        build_status_url: typing.Optional[builtins.str] = None,
        clone_depth: typing.Optional[jsii.Number] = None,
        fetch_submodules: typing.Optional[builtins.bool] = None,
        report_build_status: typing.Optional[builtins.bool] = None,
        webhook: typing.Optional[builtins.bool] = None,
        webhook_filters: typing.Optional[typing.Sequence[FilterGroup]] = None,
        webhook_triggers_batch_build: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Construction properties for {@link BitBucketSource}.

        :param identifier: The source identifier. This property is required on secondary sources.
        :param owner: The BitBucket account/user that owns the repo.
        :param repo: The name of the repo (without the username).
        :param branch_or_ref: The commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build. Default: the default branch's HEAD commit ID is used
        :param build_status_name: This parameter is used for the ``name`` parameter in the Bitbucket commit status. Can use built-in CodeBuild variables, like $AWS_REGION. Default: "AWS CodeBuild $AWS_REGION ($PROJECT_NAME)"
        :param build_status_url: The URL that the build will report back to the source provider. Can use built-in CodeBuild variables, like $AWS_REGION. Default: - link to the AWS Console for CodeBuild to a particular build execution
        :param clone_depth: The depth of history to download. Minimum value is 0. If this value is 0, greater than 25, or not provided, then the full history is downloaded with each build of the project.
        :param fetch_submodules: Whether to fetch submodules while cloning git repo. Default: false
        :param report_build_status: Whether to send notifications on your build's start and end. Default: true
        :param webhook: Whether to create a webhook that will trigger a build every time an event happens in the repository. Default: true if any ``webhookFilters`` were provided, false otherwise
        :param webhook_filters: A list of webhook filters that can constraint what events in the repository will trigger a build. A build is triggered if any of the provided filter groups match. Only valid if ``webhook`` was not provided as false. Default: every push and every Pull Request (create or update) triggers a build
        :param webhook_triggers_batch_build: Trigger a batch build from a webhook instead of a standard one. Enabling this will enable batch builds on the CodeBuild project. Default: false

        :exampleMetadata: infused

        Example::

            bb_source = codebuild.Source.bit_bucket(
                owner="owner",
                repo="repo"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d5553106ac16ef245e539725bb5e42b89c5c2697ed07f31495c6351673f2288)
            check_type(argname="argument identifier", value=identifier, expected_type=type_hints["identifier"])
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument repo", value=repo, expected_type=type_hints["repo"])
            check_type(argname="argument branch_or_ref", value=branch_or_ref, expected_type=type_hints["branch_or_ref"])
            check_type(argname="argument build_status_name", value=build_status_name, expected_type=type_hints["build_status_name"])
            check_type(argname="argument build_status_url", value=build_status_url, expected_type=type_hints["build_status_url"])
            check_type(argname="argument clone_depth", value=clone_depth, expected_type=type_hints["clone_depth"])
            check_type(argname="argument fetch_submodules", value=fetch_submodules, expected_type=type_hints["fetch_submodules"])
            check_type(argname="argument report_build_status", value=report_build_status, expected_type=type_hints["report_build_status"])
            check_type(argname="argument webhook", value=webhook, expected_type=type_hints["webhook"])
            check_type(argname="argument webhook_filters", value=webhook_filters, expected_type=type_hints["webhook_filters"])
            check_type(argname="argument webhook_triggers_batch_build", value=webhook_triggers_batch_build, expected_type=type_hints["webhook_triggers_batch_build"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "owner": owner,
            "repo": repo,
        }
        if identifier is not None:
            self._values["identifier"] = identifier
        if branch_or_ref is not None:
            self._values["branch_or_ref"] = branch_or_ref
        if build_status_name is not None:
            self._values["build_status_name"] = build_status_name
        if build_status_url is not None:
            self._values["build_status_url"] = build_status_url
        if clone_depth is not None:
            self._values["clone_depth"] = clone_depth
        if fetch_submodules is not None:
            self._values["fetch_submodules"] = fetch_submodules
        if report_build_status is not None:
            self._values["report_build_status"] = report_build_status
        if webhook is not None:
            self._values["webhook"] = webhook
        if webhook_filters is not None:
            self._values["webhook_filters"] = webhook_filters
        if webhook_triggers_batch_build is not None:
            self._values["webhook_triggers_batch_build"] = webhook_triggers_batch_build

    @builtins.property
    def identifier(self) -> typing.Optional[builtins.str]:
        '''The source identifier.

        This property is required on secondary sources.
        '''
        result = self._values.get("identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> builtins.str:
        '''The BitBucket account/user that owns the repo.

        Example::

            "awslabs"
        '''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repo(self) -> builtins.str:
        '''The name of the repo (without the username).

        Example::

            "aws-cdk"
        '''
        result = self._values.get("repo")
        assert result is not None, "Required property 'repo' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch_or_ref(self) -> typing.Optional[builtins.str]:
        '''The commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build.

        :default: the default branch's HEAD commit ID is used

        Example::

            "mybranch"
        '''
        result = self._values.get("branch_or_ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_status_name(self) -> typing.Optional[builtins.str]:
        '''This parameter is used for the ``name`` parameter in the Bitbucket commit status.

        Can use built-in CodeBuild variables, like $AWS_REGION.

        :default: "AWS CodeBuild $AWS_REGION ($PROJECT_NAME)"

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html

        Example::

            "My build #$CODEBUILD_BUILD_NUMBER"
        '''
        result = self._values.get("build_status_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_status_url(self) -> typing.Optional[builtins.str]:
        '''The URL that the build will report back to the source provider.

        Can use built-in CodeBuild variables, like $AWS_REGION.

        :default: - link to the AWS Console for CodeBuild to a particular build execution

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html

        Example::

            "$CODEBUILD_PUBLIC_BUILD_URL"
        '''
        result = self._values.get("build_status_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def clone_depth(self) -> typing.Optional[jsii.Number]:
        '''The depth of history to download.

        Minimum value is 0.
        If this value is 0, greater than 25, or not provided,
        then the full history is downloaded with each build of the project.
        '''
        result = self._values.get("clone_depth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def fetch_submodules(self) -> typing.Optional[builtins.bool]:
        '''Whether to fetch submodules while cloning git repo.

        :default: false
        '''
        result = self._values.get("fetch_submodules")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def report_build_status(self) -> typing.Optional[builtins.bool]:
        '''Whether to send notifications on your build's start and end.

        :default: true
        '''
        result = self._values.get("report_build_status")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def webhook(self) -> typing.Optional[builtins.bool]:
        '''Whether to create a webhook that will trigger a build every time an event happens in the repository.

        :default: true if any ``webhookFilters`` were provided, false otherwise
        '''
        result = self._values.get("webhook")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def webhook_filters(self) -> typing.Optional[typing.List[FilterGroup]]:
        '''A list of webhook filters that can constraint what events in the repository will trigger a build.

        A build is triggered if any of the provided filter groups match.
        Only valid if ``webhook`` was not provided as false.

        :default: every push and every Pull Request (create or update) triggers a build
        '''
        result = self._values.get("webhook_filters")
        return typing.cast(typing.Optional[typing.List[FilterGroup]], result)

    @builtins.property
    def webhook_triggers_batch_build(self) -> typing.Optional[builtins.bool]:
        '''Trigger a batch build from a webhook instead of a standard one.

        Enabling this will enable batch builds on the CodeBuild project.

        :default: false
        '''
        result = self._values.get("webhook_triggers_batch_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BitBucketSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.CodeCommitSourceProps",
    jsii_struct_bases=[SourceProps],
    name_mapping={
        "identifier": "identifier",
        "repository": "repository",
        "branch_or_ref": "branchOrRef",
        "clone_depth": "cloneDepth",
        "fetch_submodules": "fetchSubmodules",
    },
)
class CodeCommitSourceProps(SourceProps):
    def __init__(
        self,
        *,
        identifier: typing.Optional[builtins.str] = None,
        repository: _aws_cdk_aws_codecommit_692dd32c.IRepository,
        branch_or_ref: typing.Optional[builtins.str] = None,
        clone_depth: typing.Optional[jsii.Number] = None,
        fetch_submodules: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Construction properties for {@link CodeCommitSource}.

        :param identifier: The source identifier. This property is required on secondary sources.
        :param repository: 
        :param branch_or_ref: The commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build. Default: the default branch's HEAD commit ID is used
        :param clone_depth: The depth of history to download. Minimum value is 0. If this value is 0, greater than 25, or not provided, then the full history is downloaded with each build of the project.
        :param fetch_submodules: Whether to fetch submodules while cloning git repo. Default: false

        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_codecommit as codecommit
            # repo: codecommit.Repository
            # bucket: s3.Bucket
            
            
            project = codebuild.Project(self, "MyProject",
                secondary_sources=[
                    codebuild.Source.code_commit(
                        identifier="source2",
                        repository=repo
                    )
                ],
                secondary_artifacts=[
                    codebuild.Artifacts.s3(
                        identifier="artifact2",
                        bucket=bucket,
                        path="some/path",
                        name="file.zip"
                    )
                ]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1950060e6e17c7c5238fb645f443860510e0038e1ec22203314214160708d0c8)
            check_type(argname="argument identifier", value=identifier, expected_type=type_hints["identifier"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument branch_or_ref", value=branch_or_ref, expected_type=type_hints["branch_or_ref"])
            check_type(argname="argument clone_depth", value=clone_depth, expected_type=type_hints["clone_depth"])
            check_type(argname="argument fetch_submodules", value=fetch_submodules, expected_type=type_hints["fetch_submodules"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "repository": repository,
        }
        if identifier is not None:
            self._values["identifier"] = identifier
        if branch_or_ref is not None:
            self._values["branch_or_ref"] = branch_or_ref
        if clone_depth is not None:
            self._values["clone_depth"] = clone_depth
        if fetch_submodules is not None:
            self._values["fetch_submodules"] = fetch_submodules

    @builtins.property
    def identifier(self) -> typing.Optional[builtins.str]:
        '''The source identifier.

        This property is required on secondary sources.
        '''
        result = self._values.get("identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository(self) -> _aws_cdk_aws_codecommit_692dd32c.IRepository:
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(_aws_cdk_aws_codecommit_692dd32c.IRepository, result)

    @builtins.property
    def branch_or_ref(self) -> typing.Optional[builtins.str]:
        '''The commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build.

        :default: the default branch's HEAD commit ID is used

        Example::

            "mybranch"
        '''
        result = self._values.get("branch_or_ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def clone_depth(self) -> typing.Optional[jsii.Number]:
        '''The depth of history to download.

        Minimum value is 0.
        If this value is 0, greater than 25, or not provided,
        then the full history is downloaded with each build of the project.
        '''
        result = self._values.get("clone_depth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def fetch_submodules(self) -> typing.Optional[builtins.bool]:
        '''Whether to fetch submodules while cloning git repo.

        :default: false
        '''
        result = self._values.get("fetch_submodules")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeCommitSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.GitHubEnterpriseSourceProps",
    jsii_struct_bases=[SourceProps],
    name_mapping={
        "identifier": "identifier",
        "https_clone_url": "httpsCloneUrl",
        "branch_or_ref": "branchOrRef",
        "build_status_context": "buildStatusContext",
        "build_status_url": "buildStatusUrl",
        "clone_depth": "cloneDepth",
        "fetch_submodules": "fetchSubmodules",
        "ignore_ssl_errors": "ignoreSslErrors",
        "report_build_status": "reportBuildStatus",
        "webhook": "webhook",
        "webhook_filters": "webhookFilters",
        "webhook_triggers_batch_build": "webhookTriggersBatchBuild",
    },
)
class GitHubEnterpriseSourceProps(SourceProps):
    def __init__(
        self,
        *,
        identifier: typing.Optional[builtins.str] = None,
        https_clone_url: builtins.str,
        branch_or_ref: typing.Optional[builtins.str] = None,
        build_status_context: typing.Optional[builtins.str] = None,
        build_status_url: typing.Optional[builtins.str] = None,
        clone_depth: typing.Optional[jsii.Number] = None,
        fetch_submodules: typing.Optional[builtins.bool] = None,
        ignore_ssl_errors: typing.Optional[builtins.bool] = None,
        report_build_status: typing.Optional[builtins.bool] = None,
        webhook: typing.Optional[builtins.bool] = None,
        webhook_filters: typing.Optional[typing.Sequence[FilterGroup]] = None,
        webhook_triggers_batch_build: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Construction properties for {@link GitHubEnterpriseSource}.

        :param identifier: The source identifier. This property is required on secondary sources.
        :param https_clone_url: The HTTPS URL of the repository in your GitHub Enterprise installation.
        :param branch_or_ref: The commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build. Default: the default branch's HEAD commit ID is used
        :param build_status_context: This parameter is used for the ``context`` parameter in the GitHub commit status. Can use built-in CodeBuild variables, like $AWS_REGION. Default: "AWS CodeBuild $AWS_REGION ($PROJECT_NAME)"
        :param build_status_url: The URL that the build will report back to the source provider. Can use built-in CodeBuild variables, like $AWS_REGION. Default: - link to the AWS Console for CodeBuild to a particular build execution
        :param clone_depth: The depth of history to download. Minimum value is 0. If this value is 0, greater than 25, or not provided, then the full history is downloaded with each build of the project.
        :param fetch_submodules: Whether to fetch submodules while cloning git repo. Default: false
        :param ignore_ssl_errors: Whether to ignore SSL errors when connecting to the repository. Default: false
        :param report_build_status: Whether to send notifications on your build's start and end. Default: true
        :param webhook: Whether to create a webhook that will trigger a build every time an event happens in the repository. Default: true if any ``webhookFilters`` were provided, false otherwise
        :param webhook_filters: A list of webhook filters that can constraint what events in the repository will trigger a build. A build is triggered if any of the provided filter groups match. Only valid if ``webhook`` was not provided as false. Default: every push and every Pull Request (create or update) triggers a build
        :param webhook_triggers_batch_build: Trigger a batch build from a webhook instead of a standard one. Enabling this will enable batch builds on the CodeBuild project. Default: false

        :exampleMetadata: infused

        Example::

            codebuild.Project(self, "Project",
                source=codebuild.Source.git_hub_enterprise(
                    https_clone_url="https://my-github-enterprise.com/owner/repo"
                ),
            
                # Enable Docker AND custom caching
                cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER, codebuild.LocalCacheMode.CUSTOM),
            
                # BuildSpec with a 'cache' section necessary for 'CUSTOM' caching. This can
                # also come from 'buildspec.yml' in your source.
                build_spec=codebuild.BuildSpec.from_object({
                    "version": "0.2",
                    "phases": {
                        "build": {
                            "commands": ["..."]
                        }
                    },
                    "cache": {
                        "paths": ["/root/cachedir/**/*"
                        ]
                    }
                })
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a7e925940a6efaa717f182473c55897a0976b2aeebcfe0aa0c97459e9320e6f)
            check_type(argname="argument identifier", value=identifier, expected_type=type_hints["identifier"])
            check_type(argname="argument https_clone_url", value=https_clone_url, expected_type=type_hints["https_clone_url"])
            check_type(argname="argument branch_or_ref", value=branch_or_ref, expected_type=type_hints["branch_or_ref"])
            check_type(argname="argument build_status_context", value=build_status_context, expected_type=type_hints["build_status_context"])
            check_type(argname="argument build_status_url", value=build_status_url, expected_type=type_hints["build_status_url"])
            check_type(argname="argument clone_depth", value=clone_depth, expected_type=type_hints["clone_depth"])
            check_type(argname="argument fetch_submodules", value=fetch_submodules, expected_type=type_hints["fetch_submodules"])
            check_type(argname="argument ignore_ssl_errors", value=ignore_ssl_errors, expected_type=type_hints["ignore_ssl_errors"])
            check_type(argname="argument report_build_status", value=report_build_status, expected_type=type_hints["report_build_status"])
            check_type(argname="argument webhook", value=webhook, expected_type=type_hints["webhook"])
            check_type(argname="argument webhook_filters", value=webhook_filters, expected_type=type_hints["webhook_filters"])
            check_type(argname="argument webhook_triggers_batch_build", value=webhook_triggers_batch_build, expected_type=type_hints["webhook_triggers_batch_build"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "https_clone_url": https_clone_url,
        }
        if identifier is not None:
            self._values["identifier"] = identifier
        if branch_or_ref is not None:
            self._values["branch_or_ref"] = branch_or_ref
        if build_status_context is not None:
            self._values["build_status_context"] = build_status_context
        if build_status_url is not None:
            self._values["build_status_url"] = build_status_url
        if clone_depth is not None:
            self._values["clone_depth"] = clone_depth
        if fetch_submodules is not None:
            self._values["fetch_submodules"] = fetch_submodules
        if ignore_ssl_errors is not None:
            self._values["ignore_ssl_errors"] = ignore_ssl_errors
        if report_build_status is not None:
            self._values["report_build_status"] = report_build_status
        if webhook is not None:
            self._values["webhook"] = webhook
        if webhook_filters is not None:
            self._values["webhook_filters"] = webhook_filters
        if webhook_triggers_batch_build is not None:
            self._values["webhook_triggers_batch_build"] = webhook_triggers_batch_build

    @builtins.property
    def identifier(self) -> typing.Optional[builtins.str]:
        '''The source identifier.

        This property is required on secondary sources.
        '''
        result = self._values.get("identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def https_clone_url(self) -> builtins.str:
        '''The HTTPS URL of the repository in your GitHub Enterprise installation.'''
        result = self._values.get("https_clone_url")
        assert result is not None, "Required property 'https_clone_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch_or_ref(self) -> typing.Optional[builtins.str]:
        '''The commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build.

        :default: the default branch's HEAD commit ID is used

        Example::

            "mybranch"
        '''
        result = self._values.get("branch_or_ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_status_context(self) -> typing.Optional[builtins.str]:
        '''This parameter is used for the ``context`` parameter in the GitHub commit status.

        Can use built-in CodeBuild variables, like $AWS_REGION.

        :default: "AWS CodeBuild $AWS_REGION ($PROJECT_NAME)"

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html

        Example::

            "My build #$CODEBUILD_BUILD_NUMBER"
        '''
        result = self._values.get("build_status_context")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_status_url(self) -> typing.Optional[builtins.str]:
        '''The URL that the build will report back to the source provider.

        Can use built-in CodeBuild variables, like $AWS_REGION.

        :default: - link to the AWS Console for CodeBuild to a particular build execution

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html

        Example::

            "$CODEBUILD_PUBLIC_BUILD_URL"
        '''
        result = self._values.get("build_status_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def clone_depth(self) -> typing.Optional[jsii.Number]:
        '''The depth of history to download.

        Minimum value is 0.
        If this value is 0, greater than 25, or not provided,
        then the full history is downloaded with each build of the project.
        '''
        result = self._values.get("clone_depth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def fetch_submodules(self) -> typing.Optional[builtins.bool]:
        '''Whether to fetch submodules while cloning git repo.

        :default: false
        '''
        result = self._values.get("fetch_submodules")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ignore_ssl_errors(self) -> typing.Optional[builtins.bool]:
        '''Whether to ignore SSL errors when connecting to the repository.

        :default: false
        '''
        result = self._values.get("ignore_ssl_errors")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def report_build_status(self) -> typing.Optional[builtins.bool]:
        '''Whether to send notifications on your build's start and end.

        :default: true
        '''
        result = self._values.get("report_build_status")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def webhook(self) -> typing.Optional[builtins.bool]:
        '''Whether to create a webhook that will trigger a build every time an event happens in the repository.

        :default: true if any ``webhookFilters`` were provided, false otherwise
        '''
        result = self._values.get("webhook")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def webhook_filters(self) -> typing.Optional[typing.List[FilterGroup]]:
        '''A list of webhook filters that can constraint what events in the repository will trigger a build.

        A build is triggered if any of the provided filter groups match.
        Only valid if ``webhook`` was not provided as false.

        :default: every push and every Pull Request (create or update) triggers a build
        '''
        result = self._values.get("webhook_filters")
        return typing.cast(typing.Optional[typing.List[FilterGroup]], result)

    @builtins.property
    def webhook_triggers_batch_build(self) -> typing.Optional[builtins.bool]:
        '''Trigger a batch build from a webhook instead of a standard one.

        Enabling this will enable batch builds on the CodeBuild project.

        :default: false
        '''
        result = self._values.get("webhook_triggers_batch_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubEnterpriseSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.GitHubSourceProps",
    jsii_struct_bases=[SourceProps],
    name_mapping={
        "identifier": "identifier",
        "owner": "owner",
        "repo": "repo",
        "branch_or_ref": "branchOrRef",
        "build_status_context": "buildStatusContext",
        "build_status_url": "buildStatusUrl",
        "clone_depth": "cloneDepth",
        "fetch_submodules": "fetchSubmodules",
        "report_build_status": "reportBuildStatus",
        "webhook": "webhook",
        "webhook_filters": "webhookFilters",
        "webhook_triggers_batch_build": "webhookTriggersBatchBuild",
    },
)
class GitHubSourceProps(SourceProps):
    def __init__(
        self,
        *,
        identifier: typing.Optional[builtins.str] = None,
        owner: builtins.str,
        repo: builtins.str,
        branch_or_ref: typing.Optional[builtins.str] = None,
        build_status_context: typing.Optional[builtins.str] = None,
        build_status_url: typing.Optional[builtins.str] = None,
        clone_depth: typing.Optional[jsii.Number] = None,
        fetch_submodules: typing.Optional[builtins.bool] = None,
        report_build_status: typing.Optional[builtins.bool] = None,
        webhook: typing.Optional[builtins.bool] = None,
        webhook_filters: typing.Optional[typing.Sequence[FilterGroup]] = None,
        webhook_triggers_batch_build: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Construction properties for {@link GitHubSource} and {@link GitHubEnterpriseSource}.

        :param identifier: The source identifier. This property is required on secondary sources.
        :param owner: The GitHub account/user that owns the repo.
        :param repo: The name of the repo (without the username).
        :param branch_or_ref: The commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build. Default: the default branch's HEAD commit ID is used
        :param build_status_context: This parameter is used for the ``context`` parameter in the GitHub commit status. Can use built-in CodeBuild variables, like $AWS_REGION. Default: "AWS CodeBuild $AWS_REGION ($PROJECT_NAME)"
        :param build_status_url: The URL that the build will report back to the source provider. Can use built-in CodeBuild variables, like $AWS_REGION. Default: - link to the AWS Console for CodeBuild to a particular build execution
        :param clone_depth: The depth of history to download. Minimum value is 0. If this value is 0, greater than 25, or not provided, then the full history is downloaded with each build of the project.
        :param fetch_submodules: Whether to fetch submodules while cloning git repo. Default: false
        :param report_build_status: Whether to send notifications on your build's start and end. Default: true
        :param webhook: Whether to create a webhook that will trigger a build every time an event happens in the repository. Default: true if any ``webhookFilters`` were provided, false otherwise
        :param webhook_filters: A list of webhook filters that can constraint what events in the repository will trigger a build. A build is triggered if any of the provided filter groups match. Only valid if ``webhook`` was not provided as false. Default: every push and every Pull Request (create or update) triggers a build
        :param webhook_triggers_batch_build: Trigger a batch build from a webhook instead of a standard one. Enabling this will enable batch builds on the CodeBuild project. Default: false

        :exampleMetadata: infused

        Example::

            git_hub_source = codebuild.Source.git_hub(
                owner="awslabs",
                repo="aws-cdk",
                webhook=True,  # optional, default: true if `webhookFilters` were provided, false otherwise
                webhook_triggers_batch_build=True,  # optional, default is false
                webhook_filters=[
                    codebuild.FilterGroup.in_event_of(codebuild.EventAction.PUSH).and_branch_is("master").and_commit_message_is("the commit message")
                ]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67bad2f5429c5c9e5c464684dae17243e99fc79b0c34bbb20e0d15027a18df46)
            check_type(argname="argument identifier", value=identifier, expected_type=type_hints["identifier"])
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument repo", value=repo, expected_type=type_hints["repo"])
            check_type(argname="argument branch_or_ref", value=branch_or_ref, expected_type=type_hints["branch_or_ref"])
            check_type(argname="argument build_status_context", value=build_status_context, expected_type=type_hints["build_status_context"])
            check_type(argname="argument build_status_url", value=build_status_url, expected_type=type_hints["build_status_url"])
            check_type(argname="argument clone_depth", value=clone_depth, expected_type=type_hints["clone_depth"])
            check_type(argname="argument fetch_submodules", value=fetch_submodules, expected_type=type_hints["fetch_submodules"])
            check_type(argname="argument report_build_status", value=report_build_status, expected_type=type_hints["report_build_status"])
            check_type(argname="argument webhook", value=webhook, expected_type=type_hints["webhook"])
            check_type(argname="argument webhook_filters", value=webhook_filters, expected_type=type_hints["webhook_filters"])
            check_type(argname="argument webhook_triggers_batch_build", value=webhook_triggers_batch_build, expected_type=type_hints["webhook_triggers_batch_build"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "owner": owner,
            "repo": repo,
        }
        if identifier is not None:
            self._values["identifier"] = identifier
        if branch_or_ref is not None:
            self._values["branch_or_ref"] = branch_or_ref
        if build_status_context is not None:
            self._values["build_status_context"] = build_status_context
        if build_status_url is not None:
            self._values["build_status_url"] = build_status_url
        if clone_depth is not None:
            self._values["clone_depth"] = clone_depth
        if fetch_submodules is not None:
            self._values["fetch_submodules"] = fetch_submodules
        if report_build_status is not None:
            self._values["report_build_status"] = report_build_status
        if webhook is not None:
            self._values["webhook"] = webhook
        if webhook_filters is not None:
            self._values["webhook_filters"] = webhook_filters
        if webhook_triggers_batch_build is not None:
            self._values["webhook_triggers_batch_build"] = webhook_triggers_batch_build

    @builtins.property
    def identifier(self) -> typing.Optional[builtins.str]:
        '''The source identifier.

        This property is required on secondary sources.
        '''
        result = self._values.get("identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> builtins.str:
        '''The GitHub account/user that owns the repo.

        Example::

            "awslabs"
        '''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repo(self) -> builtins.str:
        '''The name of the repo (without the username).

        Example::

            "aws-cdk"
        '''
        result = self._values.get("repo")
        assert result is not None, "Required property 'repo' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch_or_ref(self) -> typing.Optional[builtins.str]:
        '''The commit ID, pull request ID, branch name, or tag name that corresponds to the version of the source code you want to build.

        :default: the default branch's HEAD commit ID is used

        Example::

            "mybranch"
        '''
        result = self._values.get("branch_or_ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_status_context(self) -> typing.Optional[builtins.str]:
        '''This parameter is used for the ``context`` parameter in the GitHub commit status.

        Can use built-in CodeBuild variables, like $AWS_REGION.

        :default: "AWS CodeBuild $AWS_REGION ($PROJECT_NAME)"

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html

        Example::

            "My build #$CODEBUILD_BUILD_NUMBER"
        '''
        result = self._values.get("build_status_context")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_status_url(self) -> typing.Optional[builtins.str]:
        '''The URL that the build will report back to the source provider.

        Can use built-in CodeBuild variables, like $AWS_REGION.

        :default: - link to the AWS Console for CodeBuild to a particular build execution

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html

        Example::

            "$CODEBUILD_PUBLIC_BUILD_URL"
        '''
        result = self._values.get("build_status_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def clone_depth(self) -> typing.Optional[jsii.Number]:
        '''The depth of history to download.

        Minimum value is 0.
        If this value is 0, greater than 25, or not provided,
        then the full history is downloaded with each build of the project.
        '''
        result = self._values.get("clone_depth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def fetch_submodules(self) -> typing.Optional[builtins.bool]:
        '''Whether to fetch submodules while cloning git repo.

        :default: false
        '''
        result = self._values.get("fetch_submodules")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def report_build_status(self) -> typing.Optional[builtins.bool]:
        '''Whether to send notifications on your build's start and end.

        :default: true
        '''
        result = self._values.get("report_build_status")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def webhook(self) -> typing.Optional[builtins.bool]:
        '''Whether to create a webhook that will trigger a build every time an event happens in the repository.

        :default: true if any ``webhookFilters`` were provided, false otherwise
        '''
        result = self._values.get("webhook")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def webhook_filters(self) -> typing.Optional[typing.List[FilterGroup]]:
        '''A list of webhook filters that can constraint what events in the repository will trigger a build.

        A build is triggered if any of the provided filter groups match.
        Only valid if ``webhook`` was not provided as false.

        :default: every push and every Pull Request (create or update) triggers a build
        '''
        result = self._values.get("webhook_filters")
        return typing.cast(typing.Optional[typing.List[FilterGroup]], result)

    @builtins.property
    def webhook_triggers_batch_build(self) -> typing.Optional[builtins.bool]:
        '''Trigger a batch build from a webhook instead of a standard one.

        Enabling this will enable batch builds on the CodeBuild project.

        :default: false
        '''
        result = self._values.get("webhook_triggers_batch_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-codebuild.IBindableBuildImage")
class IBindableBuildImage(IBuildImage, typing_extensions.Protocol):
    '''A variant of {@link IBuildImage} that allows binding to the project.'''

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        project: IProject,
    ) -> BuildImageConfig:
        '''Function that allows the build image access to the construct tree.

        :param scope: -
        :param project: -
        '''
        ...


class _IBindableBuildImageProxy(
    jsii.proxy_for(IBuildImage), # type: ignore[misc]
):
    '''A variant of {@link IBuildImage} that allows binding to the project.'''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-codebuild.IBindableBuildImage"

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        project: IProject,
    ) -> BuildImageConfig:
        '''Function that allows the build image access to the construct tree.

        :param scope: -
        :param project: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc380c2850732baef5b1637caeb465206da05cfc76b457a33e61b2e43fe87d08)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        options = BuildImageBindOptions()

        return typing.cast(BuildImageConfig, jsii.invoke(self, "bind", [scope, project, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBindableBuildImage).__jsii_proxy_class__ = lambda : _IBindableBuildImageProxy


@jsii.implements(IBindableBuildImage)
class LinuxGpuBuildImage(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.LinuxGpuBuildImage",
):
    '''A CodeBuild GPU image running Linux.

    This class has public constants that represent the most popular GPU images from AWS Deep Learning Containers.

    :see: https://aws.amazon.com/releasenotes/available-deep-learning-containers-images
    :exampleMetadata: infused

    Example::

        codebuild.Project(self, "Project",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxGpuBuildImage.DLC_TENSORFLOW_2_1_0_INFERENCE
            )
        )
    '''

    @jsii.member(jsii_name="awsDeepLearningContainersImage")
    @builtins.classmethod
    def aws_deep_learning_containers_image(
        cls,
        repository_name: builtins.str,
        tag: builtins.str,
        account: typing.Optional[builtins.str] = None,
    ) -> IBuildImage:
        '''Returns a Linux GPU build image from AWS Deep Learning Containers.

        :param repository_name: the name of the repository, for example "pytorch-inference".
        :param tag: the tag of the image, for example "1.5.0-gpu-py36-cu101-ubuntu16.04".
        :param account: the AWS account ID where the DLC repository for this region is hosted in. In many cases, the CDK can infer that for you, but for some newer region our information might be out of date; in that case, you can specify the region explicitly using this optional parameter

        :see: https://aws.amazon.com/releasenotes/available-deep-learning-containers-images
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7beb03bea70706aa10530686e7c14ab701ead26eac7e7fbf4c01da51c47b8e5)
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
        return typing.cast(IBuildImage, jsii.sinvoke(cls, "awsDeepLearningContainersImage", [repository_name, tag, account]))

    @jsii.member(jsii_name="fromEcrRepository")
    @builtins.classmethod
    def from_ecr_repository(
        cls,
        repository: _aws_cdk_aws_ecr_093ed842.IRepository,
        tag: typing.Optional[builtins.str] = None,
    ) -> IBuildImage:
        '''Returns a GPU image running Linux from an ECR repository.

        NOTE: if the repository is external (i.e. imported), then we won't be able to add
        a resource policy statement for it so CodeBuild can pull the image.

        :param repository: The ECR repository.
        :param tag: Image tag (default "latest").

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/sample-ecr.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cc910b2e860e48bdf6a539b564146c2d0bcffb9ab5bff521646a42e883fc7b1)
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
        return typing.cast(IBuildImage, jsii.sinvoke(cls, "fromEcrRepository", [repository, tag]))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        project: IProject,
    ) -> BuildImageConfig:
        '''Function that allows the build image access to the construct tree.

        :param scope: -
        :param project: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8e37137c2d3f54a066ac4aa5435048abb5b75478ba569dc33382eb88523b06e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
        _options = BuildImageBindOptions()

        return typing.cast(BuildImageConfig, jsii.invoke(self, "bind", [scope, project, _options]))

    @jsii.member(jsii_name="runScriptBuildspec")
    def run_script_buildspec(self, entrypoint: builtins.str) -> BuildSpec:
        '''Make a buildspec to run the indicated script.

        :param entrypoint: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63d6cd93decbc7b81567d556fc604e1a5adb4ac0261ab1d727c73086274c043b)
            check_type(argname="argument entrypoint", value=entrypoint, expected_type=type_hints["entrypoint"])
        return typing.cast(BuildSpec, jsii.invoke(self, "runScriptBuildspec", [entrypoint]))

    @jsii.member(jsii_name="validate")
    def validate(
        self,
        *,
        build_image: typing.Optional[IBuildImage] = None,
        certificate: typing.Optional[typing.Union[BuildEnvironmentCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
        compute_type: typing.Optional[ComputeType] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
        privileged: typing.Optional[builtins.bool] = None,
    ) -> typing.List[builtins.str]:
        '''Allows the image a chance to validate whether the passed configuration is correct.

        :param build_image: The image used for the builds. Default: LinuxBuildImage.STANDARD_1_0
        :param certificate: The location of the PEM-encoded certificate for the build project. Default: - No external certificate is added to the project
        :param compute_type: The type of compute to use for this build. See the {@link ComputeType} enum for the possible values. Default: taken from {@link #buildImage#defaultComputeType}
        :param environment_variables: The environment variables that your builds can use.
        :param privileged: Indicates how the project builds Docker images. Specify true to enable running the Docker daemon inside a Docker container. This value must be set to true only if this build project will be used to build Docker images, and the specified build environment image is not one provided by AWS CodeBuild with Docker support. Otherwise, all associated builds that attempt to interact with the Docker daemon will fail. Default: false
        '''
        build_environment = BuildEnvironment(
            build_image=build_image,
            certificate=certificate,
            compute_type=compute_type,
            environment_variables=environment_variables,
            privileged=privileged,
        )

        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "validate", [build_environment]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_MXNET_1_4_1")
    def DLC_MXNET_1_4_1(cls) -> IBuildImage:
        '''MXNet 1.4.1 GPU image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_MXNET_1_4_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_MXNET_1_6_0")
    def DLC_MXNET_1_6_0(cls) -> IBuildImage:
        '''MXNet 1.6.0 GPU image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_MXNET_1_6_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_PYTORCH_1_2_0")
    def DLC_PYTORCH_1_2_0(cls) -> IBuildImage:
        '''PyTorch 1.2.0 GPU image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_PYTORCH_1_2_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_PYTORCH_1_3_1")
    def DLC_PYTORCH_1_3_1(cls) -> IBuildImage:
        '''PyTorch 1.3.1 GPU image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_PYTORCH_1_3_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_PYTORCH_1_4_0_INFERENCE")
    def DLC_PYTORCH_1_4_0_INFERENCE(cls) -> IBuildImage:
        '''PyTorch 1.4.0 GPU inference image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_PYTORCH_1_4_0_INFERENCE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_PYTORCH_1_4_0_TRAINING")
    def DLC_PYTORCH_1_4_0_TRAINING(cls) -> IBuildImage:
        '''PyTorch 1.4.0 GPU training image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_PYTORCH_1_4_0_TRAINING"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_PYTORCH_1_5_0_INFERENCE")
    def DLC_PYTORCH_1_5_0_INFERENCE(cls) -> IBuildImage:
        '''PyTorch 1.5.0 GPU inference image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_PYTORCH_1_5_0_INFERENCE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_PYTORCH_1_5_0_TRAINING")
    def DLC_PYTORCH_1_5_0_TRAINING(cls) -> IBuildImage:
        '''PyTorch 1.5.0 GPU training image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_PYTORCH_1_5_0_TRAINING"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_TENSORFLOW_1_14_0")
    def DLC_TENSORFLOW_1_14_0(cls) -> IBuildImage:
        '''Tensorflow 1.14.0 GPU image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_TENSORFLOW_1_14_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_TENSORFLOW_1_15_0")
    def DLC_TENSORFLOW_1_15_0(cls) -> IBuildImage:
        '''Tensorflow 1.15.0 GPU image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_TENSORFLOW_1_15_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_TENSORFLOW_1_15_2_INFERENCE")
    def DLC_TENSORFLOW_1_15_2_INFERENCE(cls) -> IBuildImage:
        '''Tensorflow 1.15.2 GPU inference image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_TENSORFLOW_1_15_2_INFERENCE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_TENSORFLOW_1_15_2_TRAINING")
    def DLC_TENSORFLOW_1_15_2_TRAINING(cls) -> IBuildImage:
        '''Tensorflow 1.15.2 GPU training image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_TENSORFLOW_1_15_2_TRAINING"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_TENSORFLOW_2_0_0")
    def DLC_TENSORFLOW_2_0_0(cls) -> IBuildImage:
        '''Tensorflow 2.0.0 GPU image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_TENSORFLOW_2_0_0"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_TENSORFLOW_2_0_1")
    def DLC_TENSORFLOW_2_0_1(cls) -> IBuildImage:
        '''Tensorflow 2.0.1 GPU image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_TENSORFLOW_2_0_1"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_TENSORFLOW_2_1_0_INFERENCE")
    def DLC_TENSORFLOW_2_1_0_INFERENCE(cls) -> IBuildImage:
        '''Tensorflow 2.1.0 GPU inference image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_TENSORFLOW_2_1_0_INFERENCE"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_TENSORFLOW_2_1_0_TRAINING")
    def DLC_TENSORFLOW_2_1_0_TRAINING(cls) -> IBuildImage:
        '''Tensorflow 2.1.0 GPU training image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_TENSORFLOW_2_1_0_TRAINING"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DLC_TENSORFLOW_2_2_0_TRAINING")
    def DLC_TENSORFLOW_2_2_0_TRAINING(cls) -> IBuildImage:
        '''Tensorflow 2.2.0 GPU training image from AWS Deep Learning Containers.'''
        return typing.cast(IBuildImage, jsii.sget(cls, "DLC_TENSORFLOW_2_2_0_TRAINING"))

    @builtins.property
    @jsii.member(jsii_name="defaultComputeType")
    def default_compute_type(self) -> ComputeType:
        '''The default {@link ComputeType} to use with this image, if one was not specified in {@link BuildEnvironment#computeType} explicitly.'''
        return typing.cast(ComputeType, jsii.get(self, "defaultComputeType"))

    @builtins.property
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> builtins.str:
        '''The Docker image identifier that the build environment uses.'''
        return typing.cast(builtins.str, jsii.get(self, "imageId"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''The type of build environment.'''
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="imagePullPrincipalType")
    def image_pull_principal_type(self) -> typing.Optional[ImagePullPrincipalType]:
        '''The type of principal that CodeBuild will use to pull this build Docker image.'''
        return typing.cast(typing.Optional[ImagePullPrincipalType], jsii.get(self, "imagePullPrincipalType"))


class PipelineProject(
    Project,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codebuild.PipelineProject",
):
    '''A convenience class for CodeBuild Projects that are used in CodePipeline.

    :exampleMetadata: infused

    Example::

        # Create a Cloudfront Web Distribution
        import aws_cdk.aws_cloudfront as cloudfront
        # distribution: cloudfront.Distribution
        
        
        # Create the build project that will invalidate the cache
        invalidate_build_project = codebuild.PipelineProject(self, "InvalidateProject",
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "build": {
                        "commands": ["aws cloudfront create-invalidation --distribution-id ${CLOUDFRONT_ID} --paths \"/*\""
                        ]
                    }
                }
            }),
            environment_variables={
                "CLOUDFRONT_ID": codebuild.BuildEnvironmentVariable(value=distribution.distribution_id)
            }
        )
        
        # Add Cloudfront invalidation permissions to the project
        distribution_arn = f"arn:aws:cloudfront::{this.account}:distribution/{distribution.distributionId}"
        invalidate_build_project.add_to_role_policy(iam.PolicyStatement(
            resources=[distribution_arn],
            actions=["cloudfront:CreateInvalidation"
            ]
        ))
        
        # Create the pipeline (here only the S3 deploy and Invalidate cache build)
        deploy_bucket = s3.Bucket(self, "DeployBucket")
        deploy_input = codepipeline.Artifact()
        codepipeline.Pipeline(self, "Pipeline",
            stages=[codepipeline.StageProps(
                stage_name="Deploy",
                actions=[
                    codepipeline_actions.S3DeployAction(
                        action_name="S3Deploy",
                        bucket=deploy_bucket,
                        input=deploy_input,
                        run_order=1
                    ),
                    codepipeline_actions.CodeBuildAction(
                        action_name="InvalidateCache",
                        project=invalidate_build_project,
                        input=deploy_input,
                        run_order=2
                    )
                ]
            )
            ]
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        badge: typing.Optional[builtins.bool] = None,
        build_spec: typing.Optional[BuildSpec] = None,
        cache: typing.Optional[Cache] = None,
        check_secrets_in_plain_text_env_variables: typing.Optional[builtins.bool] = None,
        concurrent_build_limit: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
        environment: typing.Optional[typing.Union[BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
        file_system_locations: typing.Optional[typing.Sequence[IFileSystemLocation]] = None,
        grant_report_group_permissions: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[typing.Union[LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        project_name: typing.Optional[builtins.str] = None,
        queued_timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_67de8e8d.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param allow_all_outbound: Whether to allow the CodeBuild to send all network traffic. If set to false, you must individually add traffic rules to allow the CodeBuild project to connect to network targets. Only used if 'vpc' is supplied. Default: true
        :param badge: Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge. For more information, see Build Badges Sample in the AWS CodeBuild User Guide. Default: false
        :param build_spec: Filename or contents of buildspec in JSON format. Default: - Empty buildspec.
        :param cache: Caching strategy to use. Default: Cache.none
        :param check_secrets_in_plain_text_env_variables: Whether to check for the presence of any secrets in the environment variables of the default type, BuildEnvironmentVariableType.PLAINTEXT. Since using a secret for the value of that kind of variable would result in it being displayed in plain text in the AWS Console, the construct will throw an exception if it detects a secret was passed there. Pass this property as false if you want to skip this validation, and keep using a secret in a plain text environment variable. Default: true
        :param concurrent_build_limit: Maximum number of concurrent builds. Minimum value is 1 and maximum is account build limit. Default: - no explicit limit is set
        :param description: A description of the project. Use the description to identify the purpose of the project. Default: - No description.
        :param encryption_key: Encryption key to use to read and write artifacts. Default: - The AWS-managed CMK for Amazon Simple Storage Service (Amazon S3) is used.
        :param environment: Build environment to use for the build. Default: BuildEnvironment.LinuxBuildImage.STANDARD_1_0
        :param environment_variables: Additional environment variables to add to the build environment. Default: - No additional environment variables are specified.
        :param file_system_locations: An ProjectFileSystemLocation objects for a CodeBuild build project. A ProjectFileSystemLocation object specifies the identifier, location, mountOptions, mountPoint, and type of a file system created using Amazon Elastic File System. Default: - no file system locations
        :param grant_report_group_permissions: Add permissions to this project's role to create and use test report groups with name starting with the name of this project. That is the standard report group that gets created when a simple name (in contrast to an ARN) is used in the 'reports' section of the buildspec of this project. This is usually harmless, but you can turn these off if you don't plan on using test reports in this project. Default: true
        :param logging: Information about logs for the build project. A project can create logs in Amazon CloudWatch Logs, an S3 bucket, or both. Default: - no log configuration is set
        :param project_name: The physical, human-readable name of the CodeBuild Project. Default: - Name is automatically generated.
        :param queued_timeout: The number of minutes after which AWS CodeBuild stops the build if it's still in queue. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: - no queue timeout is set
        :param role: Service Role to assume while running the build. Default: - A role will be created.
        :param security_groups: What security group to associate with the codebuild project's network interfaces. If no security group is identified, one will be created automatically. Only used if 'vpc' is supplied. Default: - Security group will be automatically created.
        :param subnet_selection: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Default: - All private subnets.
        :param timeout: The number of minutes after which AWS CodeBuild stops the build if it's not complete. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: Duration.hours(1)
        :param vpc: VPC network to place codebuild network interfaces. Specify this if the codebuild project needs to access resources in a VPC. Default: - No VPC is specified.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7517bbe7f9dc2ea06d13b001388a9b5f317cf39c3f32d40d4ee1b6d0c5316783)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PipelineProjectProps(
            allow_all_outbound=allow_all_outbound,
            badge=badge,
            build_spec=build_spec,
            cache=cache,
            check_secrets_in_plain_text_env_variables=check_secrets_in_plain_text_env_variables,
            concurrent_build_limit=concurrent_build_limit,
            description=description,
            encryption_key=encryption_key,
            environment=environment,
            environment_variables=environment_variables,
            file_system_locations=file_system_locations,
            grant_report_group_permissions=grant_report_group_permissions,
            logging=logging,
            project_name=project_name,
            queued_timeout=queued_timeout,
            role=role,
            security_groups=security_groups,
            subnet_selection=subnet_selection,
            timeout=timeout,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codebuild.S3SourceProps",
    jsii_struct_bases=[SourceProps],
    name_mapping={
        "identifier": "identifier",
        "bucket": "bucket",
        "path": "path",
        "version": "version",
    },
)
class S3SourceProps(SourceProps):
    def __init__(
        self,
        *,
        identifier: typing.Optional[builtins.str] = None,
        bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
        path: builtins.str,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Construction properties for {@link S3Source}.

        :param identifier: The source identifier. This property is required on secondary sources.
        :param bucket: 
        :param path: 
        :param version: The version ID of the object that represents the build input ZIP file to use. Default: latest

        :exampleMetadata: infused

        Example::

            bucket = s3.Bucket(self, "MyBucket")
            
            codebuild.Project(self, "MyProject",
                source=codebuild.Source.s3(
                    bucket=bucket,
                    path="path/to/file.zip"
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__777d87dfee1c68258b519f1b2a0b6795faea1dbb619357f46e19fde8ab6ddfab)
            check_type(argname="argument identifier", value=identifier, expected_type=type_hints["identifier"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
            "path": path,
        }
        if identifier is not None:
            self._values["identifier"] = identifier
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def identifier(self) -> typing.Optional[builtins.str]:
        '''The source identifier.

        This property is required on secondary sources.
        '''
        result = self._values.get("identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_55f001a5.IBucket:
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_55f001a5.IBucket, result)

    @builtins.property
    def path(self) -> builtins.str:
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''The version ID of the object that represents the build input ZIP file to use.

        :default: latest
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3SourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Artifacts",
    "ArtifactsConfig",
    "ArtifactsProps",
    "BatchBuildConfig",
    "BindToCodePipelineOptions",
    "BitBucketSourceCredentials",
    "BitBucketSourceCredentialsProps",
    "BitBucketSourceProps",
    "BucketCacheOptions",
    "BuildEnvironment",
    "BuildEnvironmentCertificate",
    "BuildEnvironmentVariable",
    "BuildEnvironmentVariableType",
    "BuildImageBindOptions",
    "BuildImageConfig",
    "BuildSpec",
    "Cache",
    "CfnProject",
    "CfnProjectProps",
    "CfnReportGroup",
    "CfnReportGroupProps",
    "CfnSourceCredential",
    "CfnSourceCredentialProps",
    "CloudWatchLoggingOptions",
    "CodeCommitSourceProps",
    "CommonProjectProps",
    "ComputeType",
    "DockerImageOptions",
    "EfsFileSystemLocationProps",
    "EventAction",
    "FileSystemConfig",
    "FileSystemLocation",
    "FilterGroup",
    "GitHubEnterpriseSourceCredentials",
    "GitHubEnterpriseSourceCredentialsProps",
    "GitHubEnterpriseSourceProps",
    "GitHubSourceCredentials",
    "GitHubSourceCredentialsProps",
    "GitHubSourceProps",
    "IArtifacts",
    "IBindableBuildImage",
    "IBuildImage",
    "IFileSystemLocation",
    "IProject",
    "IReportGroup",
    "ISource",
    "ImagePullPrincipalType",
    "LinuxArmBuildImage",
    "LinuxBuildImage",
    "LinuxGpuBuildImage",
    "LocalCacheMode",
    "LoggingOptions",
    "PhaseChangeEvent",
    "PipelineProject",
    "PipelineProjectProps",
    "Project",
    "ProjectNotificationEvents",
    "ProjectNotifyOnOptions",
    "ProjectProps",
    "ReportGroup",
    "ReportGroupProps",
    "S3ArtifactsProps",
    "S3LoggingOptions",
    "S3SourceProps",
    "Source",
    "SourceConfig",
    "SourceProps",
    "StateChangeEvent",
    "UntrustedCodeBoundaryPolicy",
    "UntrustedCodeBoundaryPolicyProps",
    "WindowsBuildImage",
    "WindowsImageType",
]

publication.publish()

def _typecheckingstub__783137bdef1219c8299fa73812cbf2775c0bf2cc1b0cc2626a3e150604cba15b(
    *,
    artifacts_property: typing.Union[CfnProject.ArtifactsProperty, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__543fb0dbe6d57644358928fa5ebe91fdc920f03017a7f6270527f5abcdfc47b4(
    *,
    identifier: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d7a2f7d03343489b38924ea0ca66ba76a8839905b1ba2cb3a9592d8021f0fde(
    *,
    role: _aws_cdk_aws_iam_940a1ce0.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af4009f097ceffdb1f2e6e5f212ee08efef9ba1a835db5316773e5ea5f9902bd(
    *,
    artifact_bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f370aa69c6c21518dd8fe5baa560143728d59934aa6c1ae749e5f3a4b9da55e3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    password: _aws_cdk_core_f4b25747.SecretValue,
    username: _aws_cdk_core_f4b25747.SecretValue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc76d3d1ab66ce79293ed2ec33f38421ed1cdaa7bd3ab6e681bcd2629b5b69f6(
    *,
    password: _aws_cdk_core_f4b25747.SecretValue,
    username: _aws_cdk_core_f4b25747.SecretValue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ef86c7b56412e30a9ec34e29c484de4e82b900da98a1cc36d17b5baf51839e3(
    *,
    prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed1939e3af93484f8a479f8ad5736852f71e3adc35322c91a62e83ee6b429dc8(
    *,
    build_image: typing.Optional[IBuildImage] = None,
    certificate: typing.Optional[typing.Union[BuildEnvironmentCertificate, typing.Dict[builtins.str, typing.Any]]] = None,
    compute_type: typing.Optional[ComputeType] = None,
    environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
    privileged: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c8df7f26ec8e9badf3c1e1bc83532e47fb7441fa8152a0415550c4b33f4405e(
    *,
    bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
    object_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9b1d8664991b60ade51b64d6c6f11f5d40b655c9ab44a07207821ecc2571742(
    *,
    value: typing.Any,
    type: typing.Optional[BuildEnvironmentVariableType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__118f00606d61b3311a987f2e6085927a009ccbc074c4bf2c29338e814f03f27d(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a81b7cbd7c4ee1bf82cd3918f7aaf6188813a759ce5cfd92f43055c2869b601b(
    value: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__896c395e9727365976920c9afac46f4ac53dc1b7839589cc3c2c9bd45a15202d(
    filename: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a690d23d363dd3a701ea1a18a91365177cc6d0f01d2e8874ee417d74d465eaf(
    bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
    *,
    prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acbfc2e273c01ece9511679ce81d636c3a5d6a50de39f37c49c734c4eab76ad8(
    *modes: LocalCacheMode,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4640761b9219e0ae5cbbf0bdc474c00b8dd392f786e95a3d8a8cef4f7716a7f(
    scope: _aws_cdk_core_f4b25747.Construct,
    id: builtins.str,
    *,
    artifacts: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ArtifactsProperty, typing.Dict[builtins.str, typing.Any]]],
    environment: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.EnvironmentProperty, typing.Dict[builtins.str, typing.Any]]],
    service_role: builtins.str,
    source: typing.Union[typing.Union[CfnProject.SourceProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable],
    badge_enabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    build_batch_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ProjectBuildBatchConfigProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    cache: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ProjectCacheProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    concurrent_build_limit: typing.Optional[jsii.Number] = None,
    description: typing.Optional[builtins.str] = None,
    encryption_key: typing.Optional[builtins.str] = None,
    file_system_locations: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ProjectFileSystemLocationProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    logs_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.LogsConfigProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    name: typing.Optional[builtins.str] = None,
    queued_timeout_in_minutes: typing.Optional[jsii.Number] = None,
    resource_access_role: typing.Optional[builtins.str] = None,
    secondary_artifacts: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ArtifactsProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    secondary_sources: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[typing.Union[CfnProject.SourceProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]]]] = None,
    secondary_source_versions: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ProjectSourceVersionProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    source_version: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    timeout_in_minutes: typing.Optional[jsii.Number] = None,
    triggers: typing.Optional[typing.Union[typing.Union[CfnProject.ProjectTriggersProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]] = None,
    visibility: typing.Optional[builtins.str] = None,
    vpc_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.VpcConfigProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a06132306bff654e679074014a28ac1f606760095358445b8e9bcc53efe271c(
    inspector: _aws_cdk_core_f4b25747.TreeInspector,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8c7914ea84c5e3ad0150d14fc636b09bf92184ec677393e2fb4ce69023e2ae4(
    props: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c55c256ad359fcb0982b272da4db3560f3746767047d09c16073cb119581754d(
    value: typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ArtifactsProperty],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f029191340d240e7cc5678773f76b63f06de56238b92cc309d84f99948ecc4ae(
    value: typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.EnvironmentProperty],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a9134f80fbb1f6c7c3e6be01e699060665a696ae31b28c948bcc938c1e77494(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d416158b8bd0647974cdfc8f7de578714e9e9e3f639676ddaa4a9e0838025d21(
    value: typing.Union[CfnProject.SourceProperty, _aws_cdk_core_f4b25747.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bae52acb00f614cf7323bb3a2c04c0838f471f99af99920226cc46a1edeb9807(
    value: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9c6b0cbd674e4abeadbe277365d8f69f02729897853285e04c984b4429fa79a(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ProjectBuildBatchConfigProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11b11ad399f0c44e1ae18a14725c1cd70d493fab019f28f2bc168121648fd1ed(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ProjectCacheProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5203be9ce9df0e12c8e36eb7f4d6ee39860c05c6e4ce4f44d016444246e0a81b(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70de0d42e0806f2db82cae8edba3eb8e65265388aafc19056626962094c09dc8(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4e64d554e0f7c4ff3839123012965e5631538c0a9ebafc015e62eabb5a3d07b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58d8654761501bdea77af688fe80754a3c5cb919af8a06732ec2946f29ae21ed(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ProjectFileSystemLocationProperty]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b95ef485b0fbbc4d8b02c58f147da30c011ac1d75dc27c26c573353cee4a3cb(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.LogsConfigProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02366a2811452aa694d57d58d427375b7aa3202f77674464fb5f4c851aefca82(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8916c820c6a5cb1afb76e917cbab84c56d729b94a49d61efcea653704305ab68(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ffc3243ca8f0c717d9205a79466595bdd9bbf7af722a819fe45e18ff45c52bc(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__803d0393b0f998fc86dd49c05ba56c5d052380dbae7818c8e50efc712b45d763(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ArtifactsProperty]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de34a8da11b179e3121bff13c58007ab7980257eb31c0c7b79dbc2fc6aed5e3e(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[CfnProject.SourceProperty, _aws_cdk_core_f4b25747.IResolvable]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d20a5dbd795c6414478f5a6f55922f13c9fb45bc4e1b0b8fb211354aa202e1d(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.ProjectSourceVersionProperty]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93da05b250d2d46cbc24ece2a515e46f14f555aaedddb625bb67dd405acaaacd(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3944d824c436ffe2d088a7b50a91faa328ea65e8dfa376a4b372490fe00a966(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__362053508828bf50e0e52654852a731a8f9a33909a21054042d9d0f6a1594c92(
    value: typing.Optional[typing.Union[CfnProject.ProjectTriggersProperty, _aws_cdk_core_f4b25747.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d2de9c0a3d90f90e52edfc4de31dbddfa80e7359c9108ac37497d0718678434(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c65229ca137d90a18456c8c453c33bf6a268312d0699b4fa94e5de9623787a3e(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnProject.VpcConfigProperty]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10e69701b846bc22f6f84739811e2bcf19aca7d43025a4d3790ed5078db67ba6(
    *,
    type: builtins.str,
    artifact_identifier: typing.Optional[builtins.str] = None,
    encryption_disabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    location: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    namespace_type: typing.Optional[builtins.str] = None,
    override_artifact_name: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    packaging: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb6bc6e2fab27920e1a924cd2cf8893f0c2978c2cf77f98d7fcde7351ebb7342(
    *,
    compute_types_allowed: typing.Optional[typing.Sequence[builtins.str]] = None,
    maximum_builds_allowed: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aba374d9d8bf98b487019c75e76750090f342d19b7c9ca16aca58d2d3d7d0fe7(
    *,
    context: typing.Optional[builtins.str] = None,
    target_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fd7e79cf3768d0f7405de2c01fb064f7342370a61620313a099220750e1df2c(
    *,
    status: builtins.str,
    group_name: typing.Optional[builtins.str] = None,
    stream_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74b1cecf931c73947073d02ea5285c46abc4ae7354108c7a52b768ff49bb82b4(
    *,
    compute_type: builtins.str,
    image: builtins.str,
    type: builtins.str,
    certificate: typing.Optional[builtins.str] = None,
    environment_variables: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[typing.Union[CfnProject.EnvironmentVariableProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]]]] = None,
    image_pull_credentials_type: typing.Optional[builtins.str] = None,
    privileged_mode: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    registry_credential: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.RegistryCredentialProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78adc2a5842507505507c044dbbbad64350cc33d0b9f8e004113856c465d61bd(
    *,
    name: builtins.str,
    value: builtins.str,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd05bd3055ec6faa05880a0d7033d621a0c338ae45a954c15d541c78a4ff24c4(
    *,
    fetch_submodules: typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8326159c8f6edcf21cc27de730ec3f1b5533fcb658ccafa35c028a6500952352(
    *,
    cloud_watch_logs: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.CloudWatchLogsConfigProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    s3_logs: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.S3LogsConfigProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c619576ee7a19a6070bc5aa172a4f5c592e233f1feaa921d79dca337ff3a3ab(
    *,
    batch_report_mode: typing.Optional[builtins.str] = None,
    combine_artifacts: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    restrictions: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.BatchRestrictionsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    service_role: typing.Optional[builtins.str] = None,
    timeout_in_mins: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c61638f2d20614d1db79464bf9ef41460a29113654eba2391645ea83cab8d90(
    *,
    type: builtins.str,
    location: typing.Optional[builtins.str] = None,
    modes: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b0643ca64cba71d2feb9c367b59efd7d5be0d0a3a0176d31da1b5dfb88637c1(
    *,
    identifier: builtins.str,
    location: builtins.str,
    mount_point: builtins.str,
    type: builtins.str,
    mount_options: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c4b5711714ac53def1f540346df3f3e1c18c70b9b0e49c763d5721d6679079f(
    *,
    source_identifier: builtins.str,
    source_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ad8a90a68b1dc84c36b685076efc5bcdeb9160cec8408f43aa9f5565253b4f5(
    *,
    build_type: typing.Optional[builtins.str] = None,
    filter_groups: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[typing.Union[CfnProject.WebhookFilterProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]]]]]] = None,
    webhook: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e3873672c4ca3ac39380390083959dc0f4e59c73ea4775c80131875df1a2e2b(
    *,
    credential: builtins.str,
    credential_provider: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e624819cc8ed37b9008cc37e7670a6acca35181a3d3889b35cafcc78aa53974(
    *,
    status: builtins.str,
    encryption_disabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    location: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34251d7daab872fadbffae6ce715d221b491ddf989c00300fc27041f4821e165(
    *,
    type: builtins.str,
    resource: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6eb006c928c177466aa136afb4080043f5bc3e27df60ab5f84c91b7ca2908e70(
    *,
    type: builtins.str,
    auth: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.SourceAuthProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    build_spec: typing.Optional[builtins.str] = None,
    build_status_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.BuildStatusConfigProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    git_clone_depth: typing.Optional[jsii.Number] = None,
    git_submodules_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.GitSubmodulesConfigProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    insecure_ssl: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    location: typing.Optional[builtins.str] = None,
    report_build_status: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    source_identifier: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78efb6e6bc8d525e926d65712ba9887513d80c53534cc5f4c6b66db61d3719a7(
    *,
    security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    subnets: typing.Optional[typing.Sequence[builtins.str]] = None,
    vpc_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15d77bcfb2086252b78d19fcc46382a83468906a07b160433db90c4cb7160ca9(
    *,
    pattern: builtins.str,
    type: builtins.str,
    exclude_matched_pattern: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d032495b1b8a5f0125f69a4d70521e0e7e99b76caf8db0f15d51589fdc99be4(
    *,
    artifacts: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ArtifactsProperty, typing.Dict[builtins.str, typing.Any]]],
    environment: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.EnvironmentProperty, typing.Dict[builtins.str, typing.Any]]],
    service_role: builtins.str,
    source: typing.Union[typing.Union[CfnProject.SourceProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable],
    badge_enabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    build_batch_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ProjectBuildBatchConfigProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    cache: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ProjectCacheProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    concurrent_build_limit: typing.Optional[jsii.Number] = None,
    description: typing.Optional[builtins.str] = None,
    encryption_key: typing.Optional[builtins.str] = None,
    file_system_locations: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ProjectFileSystemLocationProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    logs_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.LogsConfigProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    name: typing.Optional[builtins.str] = None,
    queued_timeout_in_minutes: typing.Optional[jsii.Number] = None,
    resource_access_role: typing.Optional[builtins.str] = None,
    secondary_artifacts: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ArtifactsProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    secondary_sources: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[typing.Union[CfnProject.SourceProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]]]] = None,
    secondary_source_versions: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.ProjectSourceVersionProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    source_version: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    timeout_in_minutes: typing.Optional[jsii.Number] = None,
    triggers: typing.Optional[typing.Union[typing.Union[CfnProject.ProjectTriggersProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]] = None,
    visibility: typing.Optional[builtins.str] = None,
    vpc_config: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnProject.VpcConfigProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f92216f1bb6ae54dc1e88dd4aa0da5ee263d04bb7644a86092a09964fdbaad09(
    scope: _aws_cdk_core_f4b25747.Construct,
    id: builtins.str,
    *,
    export_config: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnReportGroup.ReportExportConfigProperty, typing.Dict[builtins.str, typing.Any]]],
    type: builtins.str,
    delete_reports: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    name: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14e3eb7944da4d9dfa360fe917e94b280b8b6002c3765a8dc7f3d66c6b534e51(
    inspector: _aws_cdk_core_f4b25747.TreeInspector,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__731d73dfe91420745e6bd5f99e1ff2fd4c5d84a4bcb01322e1215e0a0e6c033c(
    props: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2a9045b9271c9bf6517d7be4d11f9b1774e78c8f91fd77a2c0b719e9dac0c67(
    value: typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnReportGroup.ReportExportConfigProperty],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22e6211e0f2a2cff1764f8540c25aff2bb5326593f0e3778c932021001f44db4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cb72ff347730c0506f7c09ba12aed11ef9a53af93a6c972bfcf40f353254eab(
    value: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48d36f8ea8526e127dffb97d94a8417a0e001a2490d52542fd22f9e3ac96bba5(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2debb973a10dcc817fbae8314b8af44ea8a7e640ad1b0206715ce438044f45b9(
    *,
    export_config_type: builtins.str,
    s3_destination: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnReportGroup.S3ReportExportConfigProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96033dcf7f4e3529dc1d675c74aa7019970daa92fc6fc430c877d3e0e81498d7(
    *,
    bucket: builtins.str,
    bucket_owner: typing.Optional[builtins.str] = None,
    encryption_disabled: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    encryption_key: typing.Optional[builtins.str] = None,
    packaging: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__397a5fa8704df5157d129d09505db14cbf6e27cff6904c9223bbbaeb4cafad3c(
    *,
    export_config: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnReportGroup.ReportExportConfigProperty, typing.Dict[builtins.str, typing.Any]]],
    type: builtins.str,
    delete_reports: typing.Optional[typing.Union[builtins.bool, _aws_cdk_core_f4b25747.IResolvable]] = None,
    name: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8af3671099fa95307aa855c32c5271bff0edad2d4763e1f5916666c1de9f3e9d(
    scope: _aws_cdk_core_f4b25747.Construct,
    id: builtins.str,
    *,
    auth_type: builtins.str,
    server_type: builtins.str,
    token: builtins.str,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5891cba835ffb26d002a73be032b0b460a111e259505c25478d1a435c451d724(
    inspector: _aws_cdk_core_f4b25747.TreeInspector,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eaec9caebf548ea97e4ef10165a6caecf0363069b8b77a6f6dd7b857032df369(
    props: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f4f2a2355d7e187a31d16a8c42b013b96be3e75e23a67e449ca3a918c991464(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cda856471d9b230be0ba326ff411a240dc18b550f41f4fb7432a6cbe7996c574(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15bf729c34a0a146d344ce53f980d81ab16a3219ecc1465c6e1c9bb8ee20cd15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa810b139be0677dece2577c83c36ccc0ac4284fd3063df0ea04fe624679155c(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21dcdc0d6ea4af957c572ba6f20450bdbc127bdd7ca2ffbb90d97f5bbac28137(
    *,
    auth_type: builtins.str,
    server_type: builtins.str,
    token: builtins.str,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4b7d5dc3371bb02cf8425e20f38b02ab76443ede9587588825f49c0211650cb(
    *,
    enabled: typing.Optional[builtins.bool] = None,
    log_group: typing.Optional[_aws_cdk_aws_logs_6c4320fb.ILogGroup] = None,
    prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed64d36304c2ccdb6eb818ec5e83a5e953ce4ad703b9d20dafcae588e38d942a(
    *,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    badge: typing.Optional[builtins.bool] = None,
    build_spec: typing.Optional[BuildSpec] = None,
    cache: typing.Optional[Cache] = None,
    check_secrets_in_plain_text_env_variables: typing.Optional[builtins.bool] = None,
    concurrent_build_limit: typing.Optional[jsii.Number] = None,
    description: typing.Optional[builtins.str] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
    environment: typing.Optional[typing.Union[BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
    environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
    file_system_locations: typing.Optional[typing.Sequence[IFileSystemLocation]] = None,
    grant_report_group_permissions: typing.Optional[builtins.bool] = None,
    logging: typing.Optional[typing.Union[LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    project_name: typing.Optional[builtins.str] = None,
    queued_timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_67de8e8d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e25f3d1f063a586cd4be7a719e5cdd4d3390bf2cade9979be4f82aa09431a030(
    *,
    secrets_manager_credentials: typing.Optional[_aws_cdk_aws_secretsmanager_72af8d6f.ISecret] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbcc57093d54ea5121deaf231a540e66b66673f09f6f6c59270eb229284d3b9e(
    *,
    identifier: builtins.str,
    location: builtins.str,
    mount_point: builtins.str,
    mount_options: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ddde554f590a88f001162f0f7655f9dec75e7c70ea4a41ee380f1fde82305d8(
    *,
    location: typing.Union[CfnProject.ProjectFileSystemLocationProperty, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7ee82b054f2fce2cc647f54bbe392be03a653535de1e769d1bae93d96a67cf3(
    *actions: EventAction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44ae6460fccbc30ea0a21d6003515fd50ee84f033f45c8dfad1c388369610523(
    pattern: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55191b53117efc7c12b5109c057af34f6f4d2419adecc0e9a56cc4f3e7ded2dd(
    pattern: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__653d6e2311acdaecb81dae0669031dceded5b465feb0dd66568202ef8f2b42f8(
    branch_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abbf3760f382c85794ee5de9f8ac4af08cd6ab3d95f51181b0db68d05369ec6d(
    branch_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2cd7277e86df1c85aac31dafb09d355eea7b9faa3a6eeca46a2b15ef0488626(
    pattern: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6ffce69c3bd55d1840fc662b879bf505a627b9e256d84cdb8636575f4d393aa(
    pattern: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5bcdad3cdd8e48c789c2b805b65c483668b17e2b1857ee7904e7ecdb9533cb5(
    branch_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3111ccdb416278d9efe4937ab127207bee3d8e85669a1ee91f49451dd0ba0059(
    branch_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57f511329729868fc5ebb70e93b8172741973d866feff96f854776da691dc8f5(
    commit_message: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f761971cf5f12aa2fbbb02a412081fe823b847f2ead58983a83b3ffa88621fe(
    commit_message: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9103410499a75b4c59428ff91207730d6654a6754131dcadb6be8d18bd6900e(
    pattern: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1e46c4ca1b9a231e314b5f141efb9c7fd7c07aa396b4e47413df279ea49c8af(
    pattern: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e0f7cafebb819916109455e2daf1943bdf446f5499d0b1d3850fd79ae53fe2a(
    pattern: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8360327b95f000e04f1be92da1cbb309e7cbc121d5b99e1c63d2ca370b07e59(
    pattern: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23fefd45e9bb8c9a0e96ee10e6e55d42bcc040adef67dc6e8d36835d94b9c1e0(
    tag_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebe4b0a2b94a8430bdc8d5f74476e00ebee6feee0cc7370440becbc1d4ea8294(
    tag_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaba559d5ff242aad31285cd81284e9acac6adafddba92970cda887bb9db9077(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    access_token: _aws_cdk_core_f4b25747.SecretValue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a89edebfa59b0fd006e159d4293d16316c461501494085514c70e11ad15c368(
    *,
    access_token: _aws_cdk_core_f4b25747.SecretValue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f89c04c069698072dd828c8e1e2aa73b7ad9465f77b05b61d67b2a3b38e934b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    access_token: _aws_cdk_core_f4b25747.SecretValue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6f904a96c0298f8cae335aab69e03df4d048c91c4948db12e1f8cf9937c150c(
    *,
    access_token: _aws_cdk_core_f4b25747.SecretValue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__888f30ad13bd42579be3737723c20534ee72000800799d07145ec29b934fac19(
    scope: _aws_cdk_core_f4b25747.Construct,
    project: IProject,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0846aa90e32428976ac8e211ae813855c25ca5693497ba30491399a7ba2b51c9(
    entrypoint: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df7b1cf51ae3dbacd0e0a8d3f6fae2139ecfa80b56998de22f2ef3f219fbce59(
    scope: _aws_cdk_core_f4b25747.Construct,
    project: IProject,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75f64ef9b5ef16e4579d9a51586f4308efa27b6f21db52c991c31e8f73875598(
    policy_statement: _aws_cdk_aws_iam_940a1ce0.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85c8dd9ecb6dc3a9d962873c457341a93f043113cdec431955ea1967f988fc8c(
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

def _typecheckingstub__f0056666a08cbecc480a9fd20b36ae0b1ec37ccd2c381ee950cb1b1716fbac89(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    events: typing.Sequence[ProjectNotificationEvents],
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae7a9e862730271ceeac0a6fe693002cc4babb21ae8a8ae932a9b14216c25a47(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9eb1ed5290183f0adb4b653e5802170dc8e4cdbbe69df28502502da11591ffa(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2aefc247d3c8675ae991646fe2ff7aa138ee5c918989b3a3095edf6a431ddfa7(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d60f36597d4a8e107a6f406127fbeffc6ab0d51cd6883da6a0ea0602d33b923(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04f52587407f3580295d095b951259b443e8f2ed305d418a55260dd70a336ba1(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dd7b02f58e88b3858339f17ce861de9b54f361073efdc2245f0d57d9b1286e2(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6983aeb56e3c2be1ff14062d5d3b0c80295e2581d0a4c84f7577ecd9688f4e0c(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e5bd333832fcb44f7aadd0b4368185187212849efa6d526c6f8365dcbb8b309(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a31943eaf7fe844ca3848f12ee3bb5c5b85db65e1fd3f413e9bbde0dda720ad9(
    identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d1a30f0166cbcb4fbfe707342fd63a4fdbea160461b56ca074fc85c3c63146e(
    scope: _aws_cdk_core_f4b25747.Construct,
    project: IProject,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf04d8b43fd1ffcdcedd8d4bb415c3067621c08332ef9fc7f697f4a8f4560687(
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69e742a6a9b5c1454d5aa47beca071723e16d1cd0a1990efa3a3d332f29a9927(
    repository: _aws_cdk_aws_ecr_093ed842.IRepository,
    tag_or_digest: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b8de24993e2603ae59c2d5be2e8cbc515642de724ad670445d3ca5b3e32a292(
    entrypoint: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f0a41a87e30c3e2ba678aa154b1266ff2de5f42a22960039c6beca45b7603e3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    directory: builtins.str,
    build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    file: typing.Optional[builtins.str] = None,
    invalidation: typing.Optional[typing.Union[_aws_cdk_aws_ecr_assets_ef09b699.DockerImageAssetInvalidationOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    network_mode: typing.Optional[_aws_cdk_aws_ecr_assets_ef09b699.NetworkMode] = None,
    platform: typing.Optional[_aws_cdk_aws_ecr_assets_ef09b699.Platform] = None,
    repository_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[builtins.str] = None,
    extra_hash: typing.Optional[builtins.str] = None,
    exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
    follow: typing.Optional[_aws_cdk_assets_b1c45fb6.FollowMode] = None,
    ignore_mode: typing.Optional[_aws_cdk_core_f4b25747.IgnoreMode] = None,
    follow_symlinks: typing.Optional[_aws_cdk_core_f4b25747.SymlinkFollowMode] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e252b3ae32d547c8e4a2173466c9654296d2f355341f40b820ef3714e13c9340(
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82e58c2d34be75497e7a0c4d829ed0b97b389293abf8ea317abb1e4e8b725438(
    name: builtins.str,
    *,
    secrets_manager_credentials: typing.Optional[_aws_cdk_aws_secretsmanager_72af8d6f.ISecret] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10d159ee3efe986396bdd9f43f0bf6a3837f50c70dbe4237965afc937d6e8971(
    repository: _aws_cdk_aws_ecr_093ed842.IRepository,
    tag_or_digest: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a8b21167889275f833562be670400e3fcd7dd0399b7a6a5cec48b79a2da3f1e(
    entrypoint: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6f8b863f2ac970d653f2691f88e393d07a6c57410419271609262d28a03402f(
    *,
    cloud_watch: typing.Optional[typing.Union[CloudWatchLoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    s3: typing.Optional[typing.Union[S3LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be82c34c86ec190d07ba76d4a9645f2e45f0b0d62e6cd433971de287ebad41c7(
    *,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    badge: typing.Optional[builtins.bool] = None,
    build_spec: typing.Optional[BuildSpec] = None,
    cache: typing.Optional[Cache] = None,
    check_secrets_in_plain_text_env_variables: typing.Optional[builtins.bool] = None,
    concurrent_build_limit: typing.Optional[jsii.Number] = None,
    description: typing.Optional[builtins.str] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
    environment: typing.Optional[typing.Union[BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
    environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
    file_system_locations: typing.Optional[typing.Sequence[IFileSystemLocation]] = None,
    grant_report_group_permissions: typing.Optional[builtins.bool] = None,
    logging: typing.Optional[typing.Union[LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    project_name: typing.Optional[builtins.str] = None,
    queued_timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_67de8e8d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ec8dd4874fb2321351b09050a733240b38f8f630963ed988aa42dee8882f0b9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    artifacts: typing.Optional[IArtifacts] = None,
    secondary_artifacts: typing.Optional[typing.Sequence[IArtifacts]] = None,
    secondary_sources: typing.Optional[typing.Sequence[ISource]] = None,
    source: typing.Optional[ISource] = None,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    badge: typing.Optional[builtins.bool] = None,
    build_spec: typing.Optional[BuildSpec] = None,
    cache: typing.Optional[Cache] = None,
    check_secrets_in_plain_text_env_variables: typing.Optional[builtins.bool] = None,
    concurrent_build_limit: typing.Optional[jsii.Number] = None,
    description: typing.Optional[builtins.str] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
    environment: typing.Optional[typing.Union[BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
    environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
    file_system_locations: typing.Optional[typing.Sequence[IFileSystemLocation]] = None,
    grant_report_group_permissions: typing.Optional[builtins.bool] = None,
    logging: typing.Optional[typing.Union[LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    project_name: typing.Optional[builtins.str] = None,
    queued_timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_67de8e8d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61bd361c9664084139d451cac78033814931bd053310b8f80c1616b9a6d67155(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    project_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a62d83fea5682a870c65d59458d7e761a9a4a32a443b4c715344b91835f95263(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    project_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__398e76aa361c058058bcf2fab93ce577ac0b05b3da01e8cc5f4bc52a1e891dbd(
    environment_variables: typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]],
    validate_no_plain_text_secrets: typing.Optional[builtins.bool] = None,
    principal: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IGrantable] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff1c8eaa80bd3957d81338cb301ceeeb2a475c13a886987958c72ec9a0729fd2(
    file_system_location: IFileSystemLocation,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__677f880080fcc0d6f790d1ca12b664b2bfc31822dd7b60b85190dc8de4f63e1a(
    secondary_artifact: IArtifacts,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5ce36ddce9071499ef0ba4682c64cf04251b4d4aa7c2e2b60c3b76130786fd2(
    secondary_source: ISource,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7d7ce26017e929c0061701a258c134dcddf25e899508b621fc5c34484a22ab3(
    statement: _aws_cdk_aws_iam_940a1ce0.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cfa12d40a16fa0e6832bf8bd0c6a32a7bc8296838efb9c02ffa5ce046cbc0b2(
    _scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8a334c2273783dc7e914b32e7694c15b5e2d3b66c9046c24b0eb3ba887766c1(
    _scope: _aws_cdk_core_f4b25747.Construct,
    *,
    artifact_bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b557da2d053f95d43712ef2f385b251305d84b5db47100e79b3bccc58880243f(
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

def _typecheckingstub__25c79a24fef003cf9aa9b0edbeada41b08f45b433cac04a556ed064b9164ed26(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    events: typing.Sequence[ProjectNotificationEvents],
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44f9487bc7882f9fae2ff2ad21c248d77ce081e3958144945aeb471764bf4f02(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45b519a221bf531799c83a66ac2a9222554bccc08d17c3e5b7d865ef0b7ae01a(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3339bcc0f06be4576f664c0ce85e13853544f3129fb36b369cd37a812d919bc(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fa1bcd24015cb5308173ef0b970fbf2ec7999d2af93a6b616b7569eb36f12f6(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b97479dcab1b70f438c4964f56b1c94779dfe677d4523de11048f2d8dcc10838(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8db4fa22a1e7f4a89388a71c35a59ec89da2ac98cefa54a118f992e365538cd3(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__246f55059bc2f1d77c1603caae9d6b4fcfd25cbfefc44cc6e43cc1b5cbc5b751(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85e9cef52515f8397e72addd577013713ff86ca6a000ef561afa3cabf0cd7381(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__261b4c92e6827a39b91fca1acd5bbf43152f2d44eec59299c1f72e806fa6066c(
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
    events: typing.Sequence[ProjectNotificationEvents],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb596f44f7bf1ee04210a7fd27fb05beeb17f3c31a8afc3a224a7dc982c6d277(
    *,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    badge: typing.Optional[builtins.bool] = None,
    build_spec: typing.Optional[BuildSpec] = None,
    cache: typing.Optional[Cache] = None,
    check_secrets_in_plain_text_env_variables: typing.Optional[builtins.bool] = None,
    concurrent_build_limit: typing.Optional[jsii.Number] = None,
    description: typing.Optional[builtins.str] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
    environment: typing.Optional[typing.Union[BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
    environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
    file_system_locations: typing.Optional[typing.Sequence[IFileSystemLocation]] = None,
    grant_report_group_permissions: typing.Optional[builtins.bool] = None,
    logging: typing.Optional[typing.Union[LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    project_name: typing.Optional[builtins.str] = None,
    queued_timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_67de8e8d.IVpc] = None,
    artifacts: typing.Optional[IArtifacts] = None,
    secondary_artifacts: typing.Optional[typing.Sequence[IArtifacts]] = None,
    secondary_sources: typing.Optional[typing.Sequence[ISource]] = None,
    source: typing.Optional[ISource] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5084e09c29dea6594ebe2b0196399f821b1c8f3d627c3fd8e226f72f0cfd70e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    export_bucket: typing.Optional[_aws_cdk_aws_s3_55f001a5.IBucket] = None,
    removal_policy: typing.Optional[_aws_cdk_core_f4b25747.RemovalPolicy] = None,
    report_group_name: typing.Optional[builtins.str] = None,
    zip_export: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae1dfb374199c01d2a40ecaff114df8e9b45c1c27939848b34910b1a909a7a73(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    report_group_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b06acdc8442104d3009601c8f019726e615438c6024c4330707308af559d4617(
    identity: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__618621f2e819a5ad5cfa5615c17b87df5158db7d857e982c642debe0176fe99a(
    *,
    export_bucket: typing.Optional[_aws_cdk_aws_s3_55f001a5.IBucket] = None,
    removal_policy: typing.Optional[_aws_cdk_core_f4b25747.RemovalPolicy] = None,
    report_group_name: typing.Optional[builtins.str] = None,
    zip_export: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29d210a9244c7e2ed346916796bcaae2a31a9aa62858134f50d4c24b761548f1(
    *,
    identifier: typing.Optional[builtins.str] = None,
    bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
    encryption: typing.Optional[builtins.bool] = None,
    include_build_id: typing.Optional[builtins.bool] = None,
    name: typing.Optional[builtins.str] = None,
    package_zip: typing.Optional[builtins.bool] = None,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5621a023a0287c64dfb2886c1dce04b8b841ff2ae61ac61e57b7d3a98a19b1f6(
    *,
    bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
    enabled: typing.Optional[builtins.bool] = None,
    encrypted: typing.Optional[builtins.bool] = None,
    prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__958faeefce502b7ab214d99d2b1b31d489fc6afa94ef7c7df40092541335d648(
    _scope: _aws_cdk_core_f4b25747.Construct,
    _project: IProject,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27104d913f02d5d417aab88b4c03f348283cb39c47953205e4621768c52ee4a3(
    *,
    source_property: typing.Union[CfnProject.SourceProperty, typing.Dict[builtins.str, typing.Any]],
    build_triggers: typing.Optional[typing.Union[CfnProject.ProjectTriggersProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    source_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abf86ff362340269c6878410401499accc558bb0b687f458dace50f3d7e6bf96(
    *,
    identifier: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec25dd855c00da90e76a93e2f29685952fa5a3d32ab8aeb1d36b2fe96d974433(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    additional_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_940a1ce0.PolicyStatement]] = None,
    managed_policy_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9600200b19e2f4c8ae29f91bd7eaa6740b5e735df5f8937ef3281d6d71ef6073(
    *,
    additional_statements: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_940a1ce0.PolicyStatement]] = None,
    managed_policy_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbb26183c1276596779e68e902e47f41c05c8edb53f62d770edb65862844c26d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: typing.Union[_aws_cdk_aws_ecr_assets_ef09b699.DockerImageAssetProps, typing.Dict[builtins.str, typing.Any]],
    image_type: typing.Optional[WindowsImageType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64b2dc590fc0bfdff5235bade85135f8d593e76022e4fe45e5c12f871aa6aba3(
    name: builtins.str,
    options: typing.Optional[typing.Union[DockerImageOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    image_type: typing.Optional[WindowsImageType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cffd3f58ab48407a015f49afb05420e0ba5e3113cf2b4f0d328b3e3b85b4b92d(
    repository: _aws_cdk_aws_ecr_093ed842.IRepository,
    tag_or_digest: typing.Optional[builtins.str] = None,
    image_type: typing.Optional[WindowsImageType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d28327d3567761be5c82ad17ec064753844bcca0921b5f1705a425b310fa6bcd(
    entrypoint: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__568d47ea3ff175a778eb09e742c96e61f270bd341d8b1ea9ca0df3d06d07294c(
    _scope: _aws_cdk_core_f4b25747.Construct,
    _project: IProject,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d5553106ac16ef245e539725bb5e42b89c5c2697ed07f31495c6351673f2288(
    *,
    identifier: typing.Optional[builtins.str] = None,
    owner: builtins.str,
    repo: builtins.str,
    branch_or_ref: typing.Optional[builtins.str] = None,
    build_status_name: typing.Optional[builtins.str] = None,
    build_status_url: typing.Optional[builtins.str] = None,
    clone_depth: typing.Optional[jsii.Number] = None,
    fetch_submodules: typing.Optional[builtins.bool] = None,
    report_build_status: typing.Optional[builtins.bool] = None,
    webhook: typing.Optional[builtins.bool] = None,
    webhook_filters: typing.Optional[typing.Sequence[FilterGroup]] = None,
    webhook_triggers_batch_build: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1950060e6e17c7c5238fb645f443860510e0038e1ec22203314214160708d0c8(
    *,
    identifier: typing.Optional[builtins.str] = None,
    repository: _aws_cdk_aws_codecommit_692dd32c.IRepository,
    branch_or_ref: typing.Optional[builtins.str] = None,
    clone_depth: typing.Optional[jsii.Number] = None,
    fetch_submodules: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a7e925940a6efaa717f182473c55897a0976b2aeebcfe0aa0c97459e9320e6f(
    *,
    identifier: typing.Optional[builtins.str] = None,
    https_clone_url: builtins.str,
    branch_or_ref: typing.Optional[builtins.str] = None,
    build_status_context: typing.Optional[builtins.str] = None,
    build_status_url: typing.Optional[builtins.str] = None,
    clone_depth: typing.Optional[jsii.Number] = None,
    fetch_submodules: typing.Optional[builtins.bool] = None,
    ignore_ssl_errors: typing.Optional[builtins.bool] = None,
    report_build_status: typing.Optional[builtins.bool] = None,
    webhook: typing.Optional[builtins.bool] = None,
    webhook_filters: typing.Optional[typing.Sequence[FilterGroup]] = None,
    webhook_triggers_batch_build: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67bad2f5429c5c9e5c464684dae17243e99fc79b0c34bbb20e0d15027a18df46(
    *,
    identifier: typing.Optional[builtins.str] = None,
    owner: builtins.str,
    repo: builtins.str,
    branch_or_ref: typing.Optional[builtins.str] = None,
    build_status_context: typing.Optional[builtins.str] = None,
    build_status_url: typing.Optional[builtins.str] = None,
    clone_depth: typing.Optional[jsii.Number] = None,
    fetch_submodules: typing.Optional[builtins.bool] = None,
    report_build_status: typing.Optional[builtins.bool] = None,
    webhook: typing.Optional[builtins.bool] = None,
    webhook_filters: typing.Optional[typing.Sequence[FilterGroup]] = None,
    webhook_triggers_batch_build: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc380c2850732baef5b1637caeb465206da05cfc76b457a33e61b2e43fe87d08(
    scope: _aws_cdk_core_f4b25747.Construct,
    project: IProject,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7beb03bea70706aa10530686e7c14ab701ead26eac7e7fbf4c01da51c47b8e5(
    repository_name: builtins.str,
    tag: builtins.str,
    account: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cc910b2e860e48bdf6a539b564146c2d0bcffb9ab5bff521646a42e883fc7b1(
    repository: _aws_cdk_aws_ecr_093ed842.IRepository,
    tag: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8e37137c2d3f54a066ac4aa5435048abb5b75478ba569dc33382eb88523b06e(
    scope: _aws_cdk_core_f4b25747.Construct,
    project: IProject,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63d6cd93decbc7b81567d556fc604e1a5adb4ac0261ab1d727c73086274c043b(
    entrypoint: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7517bbe7f9dc2ea06d13b001388a9b5f317cf39c3f32d40d4ee1b6d0c5316783(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    badge: typing.Optional[builtins.bool] = None,
    build_spec: typing.Optional[BuildSpec] = None,
    cache: typing.Optional[Cache] = None,
    check_secrets_in_plain_text_env_variables: typing.Optional[builtins.bool] = None,
    concurrent_build_limit: typing.Optional[jsii.Number] = None,
    description: typing.Optional[builtins.str] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_e491a92b.IKey] = None,
    environment: typing.Optional[typing.Union[BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
    environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
    file_system_locations: typing.Optional[typing.Sequence[IFileSystemLocation]] = None,
    grant_report_group_permissions: typing.Optional[builtins.bool] = None,
    logging: typing.Optional[typing.Union[LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    project_name: typing.Optional[builtins.str] = None,
    queued_timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    role: typing.Optional[_aws_cdk_aws_iam_940a1ce0.IRole] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_67de8e8d.ISecurityGroup]] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_67de8e8d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    timeout: typing.Optional[_aws_cdk_core_f4b25747.Duration] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_67de8e8d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__777d87dfee1c68258b519f1b2a0b6795faea1dbb619357f46e19fde8ab6ddfab(
    *,
    identifier: typing.Optional[builtins.str] = None,
    bucket: _aws_cdk_aws_s3_55f001a5.IBucket,
    path: builtins.str,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
