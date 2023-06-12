'''
# AWS CodeCommit Construct Library

<!--BEGIN STABILITY BANNER-->---


![cfn-resources: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

![cdk-constructs: Stable](https://img.shields.io/badge/cdk--constructs-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

AWS CodeCommit is a version control service that enables you to privately store and manage Git repositories in the AWS cloud.

For further information on CodeCommit,
see the [AWS CodeCommit documentation](https://docs.aws.amazon.com/codecommit).

To add a CodeCommit Repository to your stack:

```python
repo = codecommit.Repository(self, "Repository",
    repository_name="MyRepositoryName",
    description="Some description."
)
```

Use the `repositoryCloneUrlHttp`, `repositoryCloneUrlSsh` or `repositoryCloneUrlGrc`
property to clone your repository.

To add an Amazon SNS trigger to your repository:

```python
# repo: codecommit.Repository


# trigger is established for all repository actions on all branches by default.
repo.notify("arn:aws:sns:*:123456789012:my_topic")
```

## Add initial commit

It is possible to initialize the Repository via the `Code` class.
It provides methods for loading code from a directory, `.zip` file and from a pre-created CDK Asset.

Example:

```python
repo = codecommit.Repository(self, "Repository",
    repository_name="MyRepositoryName",
    code=codecommit.Code.from_directory(path.join(__dirname, "directory/"), "develop")
)
```

## Events

CodeCommit repositories emit Amazon CloudWatch events for certain activities.
Use the `repo.onXxx` methods to define rules that trigger on these events
and invoke targets as a result:

```python
import aws_cdk.aws_sns as sns
import aws_cdk.aws_events_targets as targets

# repo: codecommit.Repository
# project: codebuild.PipelineProject
# my_topic: sns.Topic


# starts a CodeBuild project when a commit is pushed to the "master" branch of the repo
repo.on_commit("CommitToMaster",
    target=targets.CodeBuildProject(project),
    branches=["master"]
)

# publishes a message to an Amazon SNS topic when a comment is made on a pull request
rule = repo.on_comment_on_pull_request("CommentOnPullRequest",
    target=targets.SnsTopic(my_topic)
)
```

## CodeStar Notifications

To define CodeStar Notification rules for Repositories, use one of the `notifyOnXxx()` methods.
They are very similar to `onXxx()` methods for CloudWatch events:

```python
import aws_cdk.aws_chatbot as chatbot

# repository: codecommit.Repository

target = chatbot.SlackChannelConfiguration(self, "MySlackChannel",
    slack_channel_configuration_name="YOUR_CHANNEL_NAME",
    slack_workspace_id="YOUR_SLACK_WORKSPACE_ID",
    slack_channel_id="YOUR_SLACK_CHANNEL_ID"
)
rule = repository.notify_on_pull_request_created("NotifyOnPullRequestCreated", target)
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

import aws_cdk.aws_codestarnotifications as _aws_cdk_aws_codestarnotifications_391e8ded
import aws_cdk.aws_events as _aws_cdk_aws_events_efcdfa54
import aws_cdk.aws_iam as _aws_cdk_aws_iam_940a1ce0
import aws_cdk.aws_s3_assets as _aws_cdk_aws_s3_assets_525817d7
import aws_cdk.core as _aws_cdk_core_f4b25747
import constructs as _constructs_77d1e7e8


@jsii.implements(_aws_cdk_core_f4b25747.IInspectable)
class CfnRepository(
    _aws_cdk_core_f4b25747.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codecommit.CfnRepository",
):
    '''A CloudFormation ``AWS::CodeCommit::Repository``.

    Creates a new, empty repository.

    :cloudformationResource: AWS::CodeCommit::Repository
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_codecommit as codecommit
        
        cfn_repository = codecommit.CfnRepository(self, "MyCfnRepository",
            repository_name="repositoryName",
        
            # the properties below are optional
            code=codecommit.CfnRepository.CodeProperty(
                s3=codecommit.CfnRepository.S3Property(
                    bucket="bucket",
                    key="key",
        
                    # the properties below are optional
                    object_version="objectVersion"
                ),
        
                # the properties below are optional
                branch_name="branchName"
            ),
            repository_description="repositoryDescription",
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            triggers=[codecommit.CfnRepository.RepositoryTriggerProperty(
                destination_arn="destinationArn",
                events=["events"],
                name="name",
        
                # the properties below are optional
                branches=["branches"],
                custom_data="customData"
            )]
        )
    '''

    def __init__(
        self,
        scope: _aws_cdk_core_f4b25747.Construct,
        id: builtins.str,
        *,
        repository_name: builtins.str,
        code: typing.Optional[typing.Union[typing.Union["CfnRepository.CodeProperty", typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]] = None,
        repository_description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
        triggers: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnRepository.RepositoryTriggerProperty", typing.Dict[builtins.str, typing.Any]]]]]] = None,
    ) -> None:
        '''Create a new ``AWS::CodeCommit::Repository``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param repository_name: The name of the new repository to be created. .. epigraph:: The repository name must be unique across the calling AWS account . Repository names are limited to 100 alphanumeric, dash, and underscore characters, and cannot include certain characters. For more information about the limits on repository names, see `Quotas <https://docs.aws.amazon.com/codecommit/latest/userguide/limits.html>`_ in the *AWS CodeCommit User Guide* . The suffix .git is prohibited.
        :param code: Information about code to be committed to a repository after it is created in an AWS CloudFormation stack. Information about code is only used in resource creation. Updates to a stack will not reflect changes made to code properties after initial resource creation. .. epigraph:: You can only use this property to add code when creating a repository with a AWS CloudFormation template at creation time. This property cannot be used for updating code to an existing repository.
        :param repository_description: A comment or description about the new repository. .. epigraph:: The description field for a repository accepts all HTML characters and all valid Unicode characters. Applications that do not HTML-encode the description and display it in a webpage can expose users to potentially malicious code. Make sure that you HTML-encode the description field in any application that uses this API to display the repository description on a webpage.
        :param tags: One or more tag key-value pairs to use when tagging this repository.
        :param triggers: The JSON block of configuration information for each trigger.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ecf2869d7dc24b44482727fb08e2389fbeb198987cc194637a66d0e47801574)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CfnRepositoryProps(
            repository_name=repository_name,
            code=code,
            repository_description=repository_description,
            tags=tags,
            triggers=triggers,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _aws_cdk_core_f4b25747.TreeInspector) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__692604e9933675b0b3135d8ae8e9dfc0a0003eaf16ed3fbc6415f12f865abd74)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b4b41946f6d1087c719909ec37e42b061a719a54dd9bade6f824bf055b7f32d1)
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
        '''When you pass the logical ID of this resource, the function returns the Amazon Resource Name (ARN) of the repository.

        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property
    @jsii.member(jsii_name="attrCloneUrlHttp")
    def attr_clone_url_http(self) -> builtins.str:
        '''When you pass the logical ID of this resource, the function returns the URL to use for cloning the repository over HTTPS.

        :cloudformationAttribute: CloneUrlHttp
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrCloneUrlHttp"))

    @builtins.property
    @jsii.member(jsii_name="attrCloneUrlSsh")
    def attr_clone_url_ssh(self) -> builtins.str:
        '''When you pass the logical ID of this resource, the function returns the URL to use for cloning the repository over SSH.

        :cloudformationAttribute: CloneUrlSsh
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrCloneUrlSsh"))

    @builtins.property
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> builtins.str:
        '''When you pass the logical ID of this resource, the function returns the repository's name.

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
        '''One or more tag key-value pairs to use when tagging this repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-tags
        '''
        return typing.cast(_aws_cdk_core_f4b25747.TagManager, jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        '''The name of the new repository to be created.

        .. epigraph::

           The repository name must be unique across the calling AWS account . Repository names are limited to 100 alphanumeric, dash, and underscore characters, and cannot include certain characters. For more information about the limits on repository names, see `Quotas <https://docs.aws.amazon.com/codecommit/latest/userguide/limits.html>`_ in the *AWS CodeCommit User Guide* . The suffix .git is prohibited.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-repositoryname
        '''
        return typing.cast(builtins.str, jsii.get(self, "repositoryName"))

    @repository_name.setter
    def repository_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c28e8276a640b2a22c4842ba6dd08a926f1dbf807c633c88a41b4637f5fbd4a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repositoryName", value)

    @builtins.property
    @jsii.member(jsii_name="code")
    def code(
        self,
    ) -> typing.Optional[typing.Union["CfnRepository.CodeProperty", _aws_cdk_core_f4b25747.IResolvable]]:
        '''Information about code to be committed to a repository after it is created in an AWS CloudFormation stack.

        Information about code is only used in resource creation. Updates to a stack will not reflect changes made to code properties after initial resource creation.
        .. epigraph::

           You can only use this property to add code when creating a repository with a AWS CloudFormation template at creation time. This property cannot be used for updating code to an existing repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-code
        '''
        return typing.cast(typing.Optional[typing.Union["CfnRepository.CodeProperty", _aws_cdk_core_f4b25747.IResolvable]], jsii.get(self, "code"))

    @code.setter
    def code(
        self,
        value: typing.Optional[typing.Union["CfnRepository.CodeProperty", _aws_cdk_core_f4b25747.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c6629a41223605318bdd941bf139b2c2ce132f9bdb18bb14deb25147ced5ad2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "code", value)

    @builtins.property
    @jsii.member(jsii_name="repositoryDescription")
    def repository_description(self) -> typing.Optional[builtins.str]:
        '''A comment or description about the new repository.

        .. epigraph::

           The description field for a repository accepts all HTML characters and all valid Unicode characters. Applications that do not HTML-encode the description and display it in a webpage can expose users to potentially malicious code. Make sure that you HTML-encode the description field in any application that uses this API to display the repository description on a webpage.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-repositorydescription
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryDescription"))

    @repository_description.setter
    def repository_description(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd0f09793e38f607fb65e562aea547bbb709c1700f891ddfa6e306129a04affc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repositoryDescription", value)

    @builtins.property
    @jsii.member(jsii_name="triggers")
    def triggers(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnRepository.RepositoryTriggerProperty"]]]]:
        '''The JSON block of configuration information for each trigger.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-triggers
        '''
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnRepository.RepositoryTriggerProperty"]]]], jsii.get(self, "triggers"))

    @triggers.setter
    def triggers(
        self,
        value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnRepository.RepositoryTriggerProperty"]]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b224c103195dd538cae80f84fa688044c5245961043f1afc17750f9774590c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "triggers", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codecommit.CfnRepository.CodeProperty",
        jsii_struct_bases=[],
        name_mapping={"s3": "s3", "branch_name": "branchName"},
    )
    class CodeProperty:
        def __init__(
            self,
            *,
            s3: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union["CfnRepository.S3Property", typing.Dict[builtins.str, typing.Any]]],
            branch_name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Information about code to be committed.

            :param s3: Information about the Amazon S3 bucket that contains a ZIP file of code to be committed to the repository. Changes to this property are ignored after initial resource creation.
            :param branch_name: Optional. Specifies a branch name to be used as the default branch when importing code into a repository on initial creation. If this property is not set, the name *main* will be used for the default branch for the repository. Changes to this property are ignored after initial resource creation. We recommend using this parameter to set the name to *main* to align with the default behavior of CodeCommit unless another name is needed.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-code.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codecommit as codecommit
                
                code_property = codecommit.CfnRepository.CodeProperty(
                    s3=codecommit.CfnRepository.S3Property(
                        bucket="bucket",
                        key="key",
                
                        # the properties below are optional
                        object_version="objectVersion"
                    ),
                
                    # the properties below are optional
                    branch_name="branchName"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__aa4d326bfd86ee9953273907985521a90b2c66cc6b1ba4d0d19888af5a0340f9)
                check_type(argname="argument s3", value=s3, expected_type=type_hints["s3"])
                check_type(argname="argument branch_name", value=branch_name, expected_type=type_hints["branch_name"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "s3": s3,
            }
            if branch_name is not None:
                self._values["branch_name"] = branch_name

        @builtins.property
        def s3(
            self,
        ) -> typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnRepository.S3Property"]:
            '''Information about the Amazon S3 bucket that contains a ZIP file of code to be committed to the repository.

            Changes to this property are ignored after initial resource creation.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-code.html#cfn-codecommit-repository-code-s3
            '''
            result = self._values.get("s3")
            assert result is not None, "Required property 's3' is missing"
            return typing.cast(typing.Union[_aws_cdk_core_f4b25747.IResolvable, "CfnRepository.S3Property"], result)

        @builtins.property
        def branch_name(self) -> typing.Optional[builtins.str]:
            '''Optional.

            Specifies a branch name to be used as the default branch when importing code into a repository on initial creation. If this property is not set, the name *main* will be used for the default branch for the repository. Changes to this property are ignored after initial resource creation. We recommend using this parameter to set the name to *main* to align with the default behavior of CodeCommit unless another name is needed.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-code.html#cfn-codecommit-repository-code-branchname
            '''
            result = self._values.get("branch_name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CodeProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codecommit.CfnRepository.RepositoryTriggerProperty",
        jsii_struct_bases=[],
        name_mapping={
            "destination_arn": "destinationArn",
            "events": "events",
            "name": "name",
            "branches": "branches",
            "custom_data": "customData",
        },
    )
    class RepositoryTriggerProperty:
        def __init__(
            self,
            *,
            destination_arn: builtins.str,
            events: typing.Sequence[builtins.str],
            name: builtins.str,
            branches: typing.Optional[typing.Sequence[builtins.str]] = None,
            custom_data: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Information about a trigger for a repository.

            .. epigraph::

               If you want to receive notifications about repository events, consider using notifications instead of triggers. For more information, see `Configuring notifications for repository events <https://docs.aws.amazon.com/codecommit/latest/userguide/how-to-repository-email.html>`_ .

            :param destination_arn: The ARN of the resource that is the target for a trigger (for example, the ARN of a topic in Amazon SNS).
            :param events: The repository events that cause the trigger to run actions in another service, such as sending a notification through Amazon SNS. .. epigraph:: The valid value "all" cannot be used with any other values.
            :param name: The name of the trigger.
            :param branches: The branches to be included in the trigger configuration. If you specify an empty array, the trigger applies to all branches. .. epigraph:: Although no content is required in the array, you must include the array itself.
            :param custom_data: Any custom data associated with the trigger to be included in the information sent to the target of the trigger.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-repositorytrigger.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codecommit as codecommit
                
                repository_trigger_property = codecommit.CfnRepository.RepositoryTriggerProperty(
                    destination_arn="destinationArn",
                    events=["events"],
                    name="name",
                
                    # the properties below are optional
                    branches=["branches"],
                    custom_data="customData"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__80ef2cc4fbdc22d3a6305a881576904ae02fe29ecb5a62cb310f89524b3dfa00)
                check_type(argname="argument destination_arn", value=destination_arn, expected_type=type_hints["destination_arn"])
                check_type(argname="argument events", value=events, expected_type=type_hints["events"])
                check_type(argname="argument name", value=name, expected_type=type_hints["name"])
                check_type(argname="argument branches", value=branches, expected_type=type_hints["branches"])
                check_type(argname="argument custom_data", value=custom_data, expected_type=type_hints["custom_data"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "destination_arn": destination_arn,
                "events": events,
                "name": name,
            }
            if branches is not None:
                self._values["branches"] = branches
            if custom_data is not None:
                self._values["custom_data"] = custom_data

        @builtins.property
        def destination_arn(self) -> builtins.str:
            '''The ARN of the resource that is the target for a trigger (for example, the ARN of a topic in Amazon SNS).

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-repositorytrigger.html#cfn-codecommit-repository-repositorytrigger-destinationarn
            '''
            result = self._values.get("destination_arn")
            assert result is not None, "Required property 'destination_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def events(self) -> typing.List[builtins.str]:
            '''The repository events that cause the trigger to run actions in another service, such as sending a notification through Amazon SNS.

            .. epigraph::

               The valid value "all" cannot be used with any other values.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-repositorytrigger.html#cfn-codecommit-repository-repositorytrigger-events
            '''
            result = self._values.get("events")
            assert result is not None, "Required property 'events' is missing"
            return typing.cast(typing.List[builtins.str], result)

        @builtins.property
        def name(self) -> builtins.str:
            '''The name of the trigger.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-repositorytrigger.html#cfn-codecommit-repository-repositorytrigger-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def branches(self) -> typing.Optional[typing.List[builtins.str]]:
            '''The branches to be included in the trigger configuration.

            If you specify an empty array, the trigger applies to all branches.
            .. epigraph::

               Although no content is required in the array, you must include the array itself.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-repositorytrigger.html#cfn-codecommit-repository-repositorytrigger-branches
            '''
            result = self._values.get("branches")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def custom_data(self) -> typing.Optional[builtins.str]:
            '''Any custom data associated with the trigger to be included in the information sent to the target of the trigger.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-repositorytrigger.html#cfn-codecommit-repository-repositorytrigger-customdata
            '''
            result = self._values.get("custom_data")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RepositoryTriggerProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-codecommit.CfnRepository.S3Property",
        jsii_struct_bases=[],
        name_mapping={
            "bucket": "bucket",
            "key": "key",
            "object_version": "objectVersion",
        },
    )
    class S3Property:
        def __init__(
            self,
            *,
            bucket: builtins.str,
            key: builtins.str,
            object_version: typing.Optional[builtins.str] = None,
        ) -> None:
            '''Information about the Amazon S3 bucket that contains the code that will be committed to the new repository.

            Changes to this property are ignored after initial resource creation.

            :param bucket: The name of the Amazon S3 bucket that contains the ZIP file with the content that will be committed to the new repository. This can be specified using the name of the bucket in the AWS account . Changes to this property are ignored after initial resource creation.
            :param key: The key to use for accessing the Amazon S3 bucket. Changes to this property are ignored after initial resource creation. For more information, see `Creating object key names <https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html>`_ and `Uploading objects <https://docs.aws.amazon.com/AmazonS3/latest/userguide/upload-objects.html>`_ in the Amazon S3 User Guide.
            :param object_version: The object version of the ZIP file, if versioning is enabled for the Amazon S3 bucket. Changes to this property are ignored after initial resource creation.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-s3.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_codecommit as codecommit
                
                s3_property = codecommit.CfnRepository.S3Property(
                    bucket="bucket",
                    key="key",
                
                    # the properties below are optional
                    object_version="objectVersion"
                )
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__e01f9a462ed8c791e05a31d54053198cf2ec948d8dbc9bf396d5555be4229f9c)
                check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
                check_type(argname="argument key", value=key, expected_type=type_hints["key"])
                check_type(argname="argument object_version", value=object_version, expected_type=type_hints["object_version"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "bucket": bucket,
                "key": key,
            }
            if object_version is not None:
                self._values["object_version"] = object_version

        @builtins.property
        def bucket(self) -> builtins.str:
            '''The name of the Amazon S3 bucket that contains the ZIP file with the content that will be committed to the new repository.

            This can be specified using the name of the bucket in the AWS account . Changes to this property are ignored after initial resource creation.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-s3.html#cfn-codecommit-repository-s3-bucket
            '''
            result = self._values.get("bucket")
            assert result is not None, "Required property 'bucket' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def key(self) -> builtins.str:
            '''The key to use for accessing the Amazon S3 bucket.

            Changes to this property are ignored after initial resource creation. For more information, see `Creating object key names <https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html>`_ and `Uploading objects <https://docs.aws.amazon.com/AmazonS3/latest/userguide/upload-objects.html>`_ in the Amazon S3 User Guide.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-s3.html#cfn-codecommit-repository-s3-key
            '''
            result = self._values.get("key")
            assert result is not None, "Required property 'key' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def object_version(self) -> typing.Optional[builtins.str]:
            '''The object version of the ZIP file, if versioning is enabled for the Amazon S3 bucket.

            Changes to this property are ignored after initial resource creation.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codecommit-repository-s3.html#cfn-codecommit-repository-s3-objectversion
            '''
            result = self._values.get("object_version")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3Property(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codecommit.CfnRepositoryProps",
    jsii_struct_bases=[],
    name_mapping={
        "repository_name": "repositoryName",
        "code": "code",
        "repository_description": "repositoryDescription",
        "tags": "tags",
        "triggers": "triggers",
    },
)
class CfnRepositoryProps:
    def __init__(
        self,
        *,
        repository_name: builtins.str,
        code: typing.Optional[typing.Union[typing.Union[CfnRepository.CodeProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]] = None,
        repository_description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
        triggers: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnRepository.RepositoryTriggerProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    ) -> None:
        '''Properties for defining a ``CfnRepository``.

        :param repository_name: The name of the new repository to be created. .. epigraph:: The repository name must be unique across the calling AWS account . Repository names are limited to 100 alphanumeric, dash, and underscore characters, and cannot include certain characters. For more information about the limits on repository names, see `Quotas <https://docs.aws.amazon.com/codecommit/latest/userguide/limits.html>`_ in the *AWS CodeCommit User Guide* . The suffix .git is prohibited.
        :param code: Information about code to be committed to a repository after it is created in an AWS CloudFormation stack. Information about code is only used in resource creation. Updates to a stack will not reflect changes made to code properties after initial resource creation. .. epigraph:: You can only use this property to add code when creating a repository with a AWS CloudFormation template at creation time. This property cannot be used for updating code to an existing repository.
        :param repository_description: A comment or description about the new repository. .. epigraph:: The description field for a repository accepts all HTML characters and all valid Unicode characters. Applications that do not HTML-encode the description and display it in a webpage can expose users to potentially malicious code. Make sure that you HTML-encode the description field in any application that uses this API to display the repository description on a webpage.
        :param tags: One or more tag key-value pairs to use when tagging this repository.
        :param triggers: The JSON block of configuration information for each trigger.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codecommit as codecommit
            
            cfn_repository_props = codecommit.CfnRepositoryProps(
                repository_name="repositoryName",
            
                # the properties below are optional
                code=codecommit.CfnRepository.CodeProperty(
                    s3=codecommit.CfnRepository.S3Property(
                        bucket="bucket",
                        key="key",
            
                        # the properties below are optional
                        object_version="objectVersion"
                    ),
            
                    # the properties below are optional
                    branch_name="branchName"
                ),
                repository_description="repositoryDescription",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                triggers=[codecommit.CfnRepository.RepositoryTriggerProperty(
                    destination_arn="destinationArn",
                    events=["events"],
                    name="name",
            
                    # the properties below are optional
                    branches=["branches"],
                    custom_data="customData"
                )]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2103615b896119597efd165576c74356255b7592e15d875437b9ff3e47be3e18)
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
            check_type(argname="argument code", value=code, expected_type=type_hints["code"])
            check_type(argname="argument repository_description", value=repository_description, expected_type=type_hints["repository_description"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument triggers", value=triggers, expected_type=type_hints["triggers"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "repository_name": repository_name,
        }
        if code is not None:
            self._values["code"] = code
        if repository_description is not None:
            self._values["repository_description"] = repository_description
        if tags is not None:
            self._values["tags"] = tags
        if triggers is not None:
            self._values["triggers"] = triggers

    @builtins.property
    def repository_name(self) -> builtins.str:
        '''The name of the new repository to be created.

        .. epigraph::

           The repository name must be unique across the calling AWS account . Repository names are limited to 100 alphanumeric, dash, and underscore characters, and cannot include certain characters. For more information about the limits on repository names, see `Quotas <https://docs.aws.amazon.com/codecommit/latest/userguide/limits.html>`_ in the *AWS CodeCommit User Guide* . The suffix .git is prohibited.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-repositoryname
        '''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code(
        self,
    ) -> typing.Optional[typing.Union[CfnRepository.CodeProperty, _aws_cdk_core_f4b25747.IResolvable]]:
        '''Information about code to be committed to a repository after it is created in an AWS CloudFormation stack.

        Information about code is only used in resource creation. Updates to a stack will not reflect changes made to code properties after initial resource creation.
        .. epigraph::

           You can only use this property to add code when creating a repository with a AWS CloudFormation template at creation time. This property cannot be used for updating code to an existing repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-code
        '''
        result = self._values.get("code")
        return typing.cast(typing.Optional[typing.Union[CfnRepository.CodeProperty, _aws_cdk_core_f4b25747.IResolvable]], result)

    @builtins.property
    def repository_description(self) -> typing.Optional[builtins.str]:
        '''A comment or description about the new repository.

        .. epigraph::

           The description field for a repository accepts all HTML characters and all valid Unicode characters. Applications that do not HTML-encode the description and display it in a webpage can expose users to potentially malicious code. Make sure that you HTML-encode the description field in any application that uses this API to display the repository description on a webpage.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-repositorydescription
        '''
        result = self._values.get("repository_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_core_f4b25747.CfnTag]]:
        '''One or more tag key-value pairs to use when tagging this repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_core_f4b25747.CfnTag]], result)

    @builtins.property
    def triggers(
        self,
    ) -> typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnRepository.RepositoryTriggerProperty]]]]:
        '''The JSON block of configuration information for each trigger.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codecommit-repository.html#cfn-codecommit-repository-triggers
        '''
        result = self._values.get("triggers")
        return typing.cast(typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnRepository.RepositoryTriggerProperty]]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnRepositoryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Code(metaclass=jsii.JSIIAbstractClass, jsii_type="@aws-cdk/aws-codecommit.Code"):
    '''Represents the contents to initialize the repository with.

    :exampleMetadata: infused

    Example::

        repo = codecommit.Repository(self, "Repository",
            repository_name="MyRepositoryName",
            code=codecommit.Code.from_directory(path.join(__dirname, "directory/"), "develop")
        )
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromAsset")
    @builtins.classmethod
    def from_asset(
        cls,
        asset: _aws_cdk_aws_s3_assets_525817d7.Asset,
        branch: typing.Optional[builtins.str] = None,
    ) -> "Code":
        '''Code from user-supplied asset.

        :param asset: pre-existing asset.
        :param branch: the name of the branch to create in the repository. Default is "main"
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b732f0efeb4f5689123e92f8bfbeba7fbaf4d0d128e8ec1af70ef66e5af0abd4)
            check_type(argname="argument asset", value=asset, expected_type=type_hints["asset"])
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
        return typing.cast("Code", jsii.sinvoke(cls, "fromAsset", [asset, branch]))

    @jsii.member(jsii_name="fromDirectory")
    @builtins.classmethod
    def from_directory(
        cls,
        directory_path: builtins.str,
        branch: typing.Optional[builtins.str] = None,
    ) -> "Code":
        '''Code from directory.

        :param directory_path: the path to the local directory containing the contents to initialize the repository with.
        :param branch: the name of the branch to create in the repository. Default is "main"
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd6dd1afd691420a555123a47372d6fe7b35102be21aa52f359a417f5e73f744)
            check_type(argname="argument directory_path", value=directory_path, expected_type=type_hints["directory_path"])
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
        return typing.cast("Code", jsii.sinvoke(cls, "fromDirectory", [directory_path, branch]))

    @jsii.member(jsii_name="fromZipFile")
    @builtins.classmethod
    def from_zip_file(
        cls,
        file_path: builtins.str,
        branch: typing.Optional[builtins.str] = None,
    ) -> "Code":
        '''Code from preexisting ZIP file.

        :param file_path: the path to the local ZIP file containing the contents to initialize the repository with.
        :param branch: the name of the branch to create in the repository. Default is "main"
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05abfc1f720e5660bf856381274eaa81451d36ec3b4555f3d0ea83bff6e1aa3d)
            check_type(argname="argument file_path", value=file_path, expected_type=type_hints["file_path"])
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
        return typing.cast("Code", jsii.sinvoke(cls, "fromZipFile", [file_path, branch]))

    @jsii.member(jsii_name="bind")
    @abc.abstractmethod
    def bind(self, scope: _constructs_77d1e7e8.Construct) -> "CodeConfig":
        '''This method is called after a repository is passed this instance of Code in its 'code' property.

        :param scope: the binding scope.
        '''
        ...


class _CodeProxy(Code):
    @jsii.member(jsii_name="bind")
    def bind(self, scope: _constructs_77d1e7e8.Construct) -> "CodeConfig":
        '''This method is called after a repository is passed this instance of Code in its 'code' property.

        :param scope: the binding scope.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65e2733119140823206084c1be88dac06a28126c0613e060bad6cede974c8d3b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast("CodeConfig", jsii.invoke(self, "bind", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Code).__jsii_proxy_class__ = lambda : _CodeProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codecommit.CodeConfig",
    jsii_struct_bases=[],
    name_mapping={"code": "code"},
)
class CodeConfig:
    def __init__(
        self,
        *,
        code: typing.Union[CfnRepository.CodeProperty, typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''Represents the structure to pass into the underlying CfnRepository class.

        :param code: represents the underlying code structure.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codecommit as codecommit
            
            code_config = codecommit.CodeConfig(
                code=codecommit.CfnRepository.CodeProperty(
                    s3=codecommit.CfnRepository.S3Property(
                        bucket="bucket",
                        key="key",
            
                        # the properties below are optional
                        object_version="objectVersion"
                    ),
            
                    # the properties below are optional
                    branch_name="branchName"
                )
            )
        '''
        if isinstance(code, dict):
            code = CfnRepository.CodeProperty(**code)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aed044a5f9443a0b0b804ed268d8e7ec3ce5fe19949f044f32a130cb79992aac)
            check_type(argname="argument code", value=code, expected_type=type_hints["code"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "code": code,
        }

    @builtins.property
    def code(self) -> CfnRepository.CodeProperty:
        '''represents the underlying code structure.'''
        result = self._values.get("code")
        assert result is not None, "Required property 'code' is missing"
        return typing.cast(CfnRepository.CodeProperty, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-codecommit.IRepository")
class IRepository(
    _aws_cdk_core_f4b25747.IResource,
    _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleSource,
    typing_extensions.Protocol,
):
    @builtins.property
    @jsii.member(jsii_name="repositoryArn")
    def repository_arn(self) -> builtins.str:
        '''The ARN of this Repository.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="repositoryCloneUrlGrc")
    def repository_clone_url_grc(self) -> builtins.str:
        '''The HTTPS (GRC) clone URL.

        HTTPS (GRC) is the protocol to use with git-remote-codecommit (GRC).

        It is the recommended method for supporting connections made with federated
        access, identity providers, and temporary credentials.

        :see: https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-git-remote-codecommit.html
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="repositoryCloneUrlHttp")
    def repository_clone_url_http(self) -> builtins.str:
        '''The HTTP clone URL.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="repositoryCloneUrlSsh")
    def repository_clone_url_ssh(self) -> builtins.str:
        '''The SSH clone URL.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        '''The human-visible name of this Repository.

        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given principal identity permissions to perform the actions on this repository.

        :param grantee: -
        :param actions: -
        '''
        ...

    @jsii.member(jsii_name="grantPull")
    def grant_pull(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions to pull this repository.

        :param grantee: -
        '''
        ...

    @jsii.member(jsii_name="grantPullPush")
    def grant_pull_push(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions to pull and push this repository.

        :param grantee: -
        '''
        ...

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions to read this repository.

        :param grantee: -
        '''
        ...

    @jsii.member(jsii_name="notifiyOnPullRequestMerged")
    def notifiy_on_pull_request_merged(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''(deprecated) Defines a CodeStar Notification rule which triggers when a pull request is merged.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :deprecated: this method has a typo in its name, use notifyOnPullRequestMerged instead

        :stability: deprecated
        '''
        ...

    @jsii.member(jsii_name="notifyOn")
    def notify_on(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        events: typing.Sequence["RepositoryNotificationEvents"],
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule triggered when the project events specified by you are emitted. Similar to ``onEvent`` API.

        You can also use the methods to define rules for the specific event emitted.
        eg: ``notifyOnPullRequstCreated``.

        :param id: -
        :param target: -
        :param events: A list of event types associated with this notification rule for CodeCommit repositories. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :return: CodeStar Notifications rule associated with this repository.
        '''
        ...

    @jsii.member(jsii_name="notifyOnApprovalRuleOverridden")
    def notify_on_approval_rule_overridden(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when an approval rule is overridden.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        ...

    @jsii.member(jsii_name="notifyOnApprovalStatusChanged")
    def notify_on_approval_status_changed(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when an approval status is changed.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        ...

    @jsii.member(jsii_name="notifyOnBranchOrTagCreated")
    def notify_on_branch_or_tag_created(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when a new branch or tag is created.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        ...

    @jsii.member(jsii_name="notifyOnBranchOrTagDeleted")
    def notify_on_branch_or_tag_deleted(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when a branch or tag is deleted.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        ...

    @jsii.member(jsii_name="notifyOnPullRequestComment")
    def notify_on_pull_request_comment(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when a comment is made on a pull request.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        ...

    @jsii.member(jsii_name="notifyOnPullRequestCreated")
    def notify_on_pull_request_created(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when a pull request is created.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        ...

    @jsii.member(jsii_name="notifyOnPullRequestMerged")
    def notify_on_pull_request_merged(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when a pull request is merged.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        ...

    @jsii.member(jsii_name="onCommentOnCommit")
    def on_comment_on_commit(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a comment is made on a commit.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        ...

    @jsii.member(jsii_name="onCommentOnPullRequest")
    def on_comment_on_pull_request(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a comment is made on a pull request.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        ...

    @jsii.member(jsii_name="onCommit")
    def on_commit(
        self,
        id: builtins.str,
        *,
        branches: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a commit is pushed to a branch.

        :param id: -
        :param branches: The branch to monitor. Default: - All branches
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
        '''Defines a CloudWatch event rule which triggers for repository events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        ...

    @jsii.member(jsii_name="onPullRequestStateChange")
    def on_pull_request_state_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a pull request state is changed.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        ...

    @jsii.member(jsii_name="onReferenceCreated")
    def on_reference_created(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a reference is created (i.e. a new branch/tag is created) to the repository.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        ...

    @jsii.member(jsii_name="onReferenceDeleted")
    def on_reference_deleted(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a reference is delete (i.e. a branch/tag is deleted) from the repository.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        ...

    @jsii.member(jsii_name="onReferenceUpdated")
    def on_reference_updated(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a reference is updated (i.e. a commit is pushed to an existing or new branch) from the repository.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
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
        '''Defines a CloudWatch event rule which triggers when a "CodeCommit Repository State Change" event occurs.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        ...


class _IRepositoryProxy(
    jsii.proxy_for(_aws_cdk_core_f4b25747.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleSource), # type: ignore[misc]
):
    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-codecommit.IRepository"

    @builtins.property
    @jsii.member(jsii_name="repositoryArn")
    def repository_arn(self) -> builtins.str:
        '''The ARN of this Repository.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "repositoryArn"))

    @builtins.property
    @jsii.member(jsii_name="repositoryCloneUrlGrc")
    def repository_clone_url_grc(self) -> builtins.str:
        '''The HTTPS (GRC) clone URL.

        HTTPS (GRC) is the protocol to use with git-remote-codecommit (GRC).

        It is the recommended method for supporting connections made with federated
        access, identity providers, and temporary credentials.

        :see: https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-git-remote-codecommit.html
        '''
        return typing.cast(builtins.str, jsii.get(self, "repositoryCloneUrlGrc"))

    @builtins.property
    @jsii.member(jsii_name="repositoryCloneUrlHttp")
    def repository_clone_url_http(self) -> builtins.str:
        '''The HTTP clone URL.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "repositoryCloneUrlHttp"))

    @builtins.property
    @jsii.member(jsii_name="repositoryCloneUrlSsh")
    def repository_clone_url_ssh(self) -> builtins.str:
        '''The SSH clone URL.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "repositoryCloneUrlSsh"))

    @builtins.property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        '''The human-visible name of this Repository.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "repositoryName"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given principal identity permissions to perform the actions on this repository.

        :param grantee: -
        :param actions: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5a8177a6cf590d8c82e6de87bef54b98fabee49248726312feea0622bd22fc0)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantPull")
    def grant_pull(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions to pull this repository.

        :param grantee: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcc89abe80ba4136feb0c15be610b76e95387c1719a8d187578a09d39e84b1f6)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantPull", [grantee]))

    @jsii.member(jsii_name="grantPullPush")
    def grant_pull_push(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions to pull and push this repository.

        :param grantee: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d0b1c9ace218834acc264be9e184de825d9ae50bb6782aaa8a44c1d61acbf55)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantPullPush", [grantee]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions to read this repository.

        :param grantee: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea04213de3d198b597d590cdb6f5db673cdbad511c5bd29c1b85cf15c387a93e)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantRead", [grantee]))

    @jsii.member(jsii_name="notifiyOnPullRequestMerged")
    def notifiy_on_pull_request_merged(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''(deprecated) Defines a CodeStar Notification rule which triggers when a pull request is merged.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :deprecated: this method has a typo in its name, use notifyOnPullRequestMerged instead

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acf48e8f11b10c3cd2e6d55e036c20c9d70479b30370fd3a7f781212c01cd8ea)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifiyOnPullRequestMerged", [id, target, options]))

    @jsii.member(jsii_name="notifyOn")
    def notify_on(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        events: typing.Sequence["RepositoryNotificationEvents"],
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule triggered when the project events specified by you are emitted. Similar to ``onEvent`` API.

        You can also use the methods to define rules for the specific event emitted.
        eg: ``notifyOnPullRequstCreated``.

        :param id: -
        :param target: -
        :param events: A list of event types associated with this notification rule for CodeCommit repositories. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :return: CodeStar Notifications rule associated with this repository.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f40058eeaf452ced71dc49730a10700cd3b14519f0d62ec0c50c8eb115bd014e)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = RepositoryNotifyOnOptions(
            events=events,
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOn", [id, target, options]))

    @jsii.member(jsii_name="notifyOnApprovalRuleOverridden")
    def notify_on_approval_rule_overridden(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when an approval rule is overridden.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c5fde7b76f0d86bc3668a2526cbb27507757d190c48ae5b76c6d508f609c2b2)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnApprovalRuleOverridden", [id, target, options]))

    @jsii.member(jsii_name="notifyOnApprovalStatusChanged")
    def notify_on_approval_status_changed(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when an approval status is changed.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2af79a53a8fc91ecb31308c5a15f53e8e47c066946fa4e950334cc725e67e99)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnApprovalStatusChanged", [id, target, options]))

    @jsii.member(jsii_name="notifyOnBranchOrTagCreated")
    def notify_on_branch_or_tag_created(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when a new branch or tag is created.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92ce7090a744c648d7a01bc1bde51c6cda8de5f0ad98abd88793a410da35b78f)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnBranchOrTagCreated", [id, target, options]))

    @jsii.member(jsii_name="notifyOnBranchOrTagDeleted")
    def notify_on_branch_or_tag_deleted(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when a branch or tag is deleted.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6aac79e4c5fc7c8040d99c4203ae387b1bd56b18d05248debaa00c69c4037092)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnBranchOrTagDeleted", [id, target, options]))

    @jsii.member(jsii_name="notifyOnPullRequestComment")
    def notify_on_pull_request_comment(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when a comment is made on a pull request.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93e4a8542d74fcd8006a353431e8c9215776da2daae31c655536a88911d052d2)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnPullRequestComment", [id, target, options]))

    @jsii.member(jsii_name="notifyOnPullRequestCreated")
    def notify_on_pull_request_created(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when a pull request is created.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__754850bc93417cb26233c50a30df16d1e753899fd850e1a5bda7dfa1a8929452)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnPullRequestCreated", [id, target, options]))

    @jsii.member(jsii_name="notifyOnPullRequestMerged")
    def notify_on_pull_request_merged(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when a pull request is merged.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8d7aabe857108774ef1c61e3af4a5e0f351fb59d8773c40af6ca12b818a1f33)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnPullRequestMerged", [id, target, options]))

    @jsii.member(jsii_name="onCommentOnCommit")
    def on_comment_on_commit(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a comment is made on a commit.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b09f5603377b407596651d366dadce4aa8b12322b94722c6205bd1d46c5f8d7)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onCommentOnCommit", [id, options]))

    @jsii.member(jsii_name="onCommentOnPullRequest")
    def on_comment_on_pull_request(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a comment is made on a pull request.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__200a6edfb8b39904613976128fc26c4a3f2bae7181be4c51c67f854d1b295975)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onCommentOnPullRequest", [id, options]))

    @jsii.member(jsii_name="onCommit")
    def on_commit(
        self,
        id: builtins.str,
        *,
        branches: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a commit is pushed to a branch.

        :param id: -
        :param branches: The branch to monitor. Default: - All branches
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4227d86c89e250bf22adc3122e3c8d1275198348172651201fce94f6d0f10305)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = OnCommitOptions(
            branches=branches,
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onCommit", [id, options]))

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
        '''Defines a CloudWatch event rule which triggers for repository events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98ab8e85d61ef8ba6dd3db1696ec81241aabf66ae5168633300261902d7ad02a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onEvent", [id, options]))

    @jsii.member(jsii_name="onPullRequestStateChange")
    def on_pull_request_state_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a pull request state is changed.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d772bb61311c7385bf987d5b17fec163a33b122c0e7710217121c46c5942f948)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onPullRequestStateChange", [id, options]))

    @jsii.member(jsii_name="onReferenceCreated")
    def on_reference_created(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a reference is created (i.e. a new branch/tag is created) to the repository.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__288ffa914f33812846070049d40597ebd57ad83ec51d448992b441c9d632150a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onReferenceCreated", [id, options]))

    @jsii.member(jsii_name="onReferenceDeleted")
    def on_reference_deleted(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a reference is delete (i.e. a branch/tag is deleted) from the repository.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a34d8bdcfb5c89bbf1a14e7407e236843cde84e557b135b58009495ca290123)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onReferenceDeleted", [id, options]))

    @jsii.member(jsii_name="onReferenceUpdated")
    def on_reference_updated(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a reference is updated (i.e. a commit is pushed to an existing or new branch) from the repository.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbdc1ed423a16e1e83b94093d3e8e4890f15197a8598030fde54c3439821977d)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onReferenceUpdated", [id, options]))

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
        '''Defines a CloudWatch event rule which triggers when a "CodeCommit Repository State Change" event occurs.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87365ddb257bae5d0ea3f7480554f742082c1a97b699252a0518cc9a3e2be379)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onStateChange", [id, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRepository).__jsii_proxy_class__ = lambda : _IRepositoryProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codecommit.OnCommitOptions",
    jsii_struct_bases=[_aws_cdk_aws_events_efcdfa54.OnEventOptions],
    name_mapping={
        "description": "description",
        "event_pattern": "eventPattern",
        "rule_name": "ruleName",
        "target": "target",
        "branches": "branches",
    },
)
class OnCommitOptions(_aws_cdk_aws_events_efcdfa54.OnEventOptions):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
        branches: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Options for the onCommit() method.

        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        :param branches: The branch to monitor. Default: - All branches

        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_codecommit as codecommit
            import aws_cdk.aws_events_targets as targets
            
            # repo: codecommit.Repository
            
            my_topic = sns.Topic(self, "Topic")
            
            repo.on_commit("OnCommit",
                target=targets.SnsTopic(my_topic)
            )
        '''
        if isinstance(event_pattern, dict):
            event_pattern = _aws_cdk_aws_events_efcdfa54.EventPattern(**event_pattern)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__578249a4366c91f7021ab10cdd180ee33346c1a932b6222e8556213b1b4d4588)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument event_pattern", value=event_pattern, expected_type=type_hints["event_pattern"])
            check_type(argname="argument rule_name", value=rule_name, expected_type=type_hints["rule_name"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument branches", value=branches, expected_type=type_hints["branches"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if event_pattern is not None:
            self._values["event_pattern"] = event_pattern
        if rule_name is not None:
            self._values["rule_name"] = rule_name
        if target is not None:
            self._values["target"] = target
        if branches is not None:
            self._values["branches"] = branches

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the rule's purpose.

        :default: - No description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def event_pattern(
        self,
    ) -> typing.Optional[_aws_cdk_aws_events_efcdfa54.EventPattern]:
        '''Additional restrictions for the event to route to the specified target.

        The method that generates the rule probably imposes some type of event
        filtering. The filtering implied by what you pass here is added
        on top of that filtering.

        :default: - No additional filtering based on an event pattern.

        :see: https://docs.aws.amazon.com/eventbridge/latest/userguide/eventbridge-and-event-patterns.html
        '''
        result = self._values.get("event_pattern")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_efcdfa54.EventPattern], result)

    @builtins.property
    def rule_name(self) -> typing.Optional[builtins.str]:
        '''A name for the rule.

        :default: AWS CloudFormation generates a unique physical ID.
        '''
        result = self._values.get("rule_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget]:
        '''The target to register for the event.

        :default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        result = self._values.get("target")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget], result)

    @builtins.property
    def branches(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The branch to monitor.

        :default: - All branches
        '''
        result = self._values.get("branches")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnCommitOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ReferenceEvent(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codecommit.ReferenceEvent",
):
    '''Fields of CloudWatch Events that change references.

    :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/EventTypes.html#codebuild_event_type
    '''

    @jsii.python.classproperty
    @jsii.member(jsii_name="commitId")
    def commit_id(cls) -> builtins.str:
        '''Commit id this reference now points to.'''
        return typing.cast(builtins.str, jsii.sget(cls, "commitId"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="eventType")
    def event_type(cls) -> builtins.str:
        '''The type of reference event.

        'referenceCreated', 'referenceUpdated' or 'referenceDeleted'
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "eventType"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="referenceFullName")
    def reference_full_name(cls) -> builtins.str:
        '''Full reference name.

        For example, 'refs/tags/myTag'
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "referenceFullName"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="referenceName")
    def reference_name(cls) -> builtins.str:
        '''Name of reference changed (branch or tag name).'''
        return typing.cast(builtins.str, jsii.sget(cls, "referenceName"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="referenceType")
    def reference_type(cls) -> builtins.str:
        '''Type of reference changed.

        'branch' or 'tag'
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "referenceType"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="repositoryId")
    def repository_id(cls) -> builtins.str:
        '''Id of the CodeCommit repository.'''
        return typing.cast(builtins.str, jsii.sget(cls, "repositoryId"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="repositoryName")
    def repository_name(cls) -> builtins.str:
        '''Name of the CodeCommit repository.'''
        return typing.cast(builtins.str, jsii.sget(cls, "repositoryName"))


@jsii.implements(IRepository)
class Repository(
    _aws_cdk_core_f4b25747.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-codecommit.Repository",
):
    '''Provides a CodeCommit Repository.

    :exampleMetadata: infused

    Example::

        # project: codebuild.PipelineProject
        
        repository = codecommit.Repository(self, "MyRepository",
            repository_name="MyRepository"
        )
        project = codebuild.PipelineProject(self, "MyProject")
        
        source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.CodeCommitSourceAction(
            action_name="CodeCommit",
            repository=repository,
            output=source_output
        )
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="CodeBuild",
            project=project,
            input=source_output,
            outputs=[codepipeline.Artifact()],  # optional
            execute_batch_build=True,  # optional, defaults to false
            combine_batch_build_artifacts=True
        )
        
        codepipeline.Pipeline(self, "MyPipeline",
            stages=[codepipeline.StageProps(
                stage_name="Source",
                actions=[source_action]
            ), codepipeline.StageProps(
                stage_name="Build",
                actions=[build_action]
            )
            ]
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        repository_name: builtins.str,
        code: typing.Optional[Code] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param repository_name: Name of the repository. This property is required for all CodeCommit repositories.
        :param code: The contents with which to initialize the repository after it has been created. Default: - No initialization (create empty repo)
        :param description: A description of the repository. Use the description to identify the purpose of the repository. Default: - No description.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c825ecda8071bdb9f5be001248a08eb1b55c9f65defdd68fbd9e176f007c5028)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RepositoryProps(
            repository_name=repository_name, code=code, description=description
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromRepositoryArn")
    @builtins.classmethod
    def from_repository_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        repository_arn: builtins.str,
    ) -> IRepository:
        '''Imports a codecommit repository.

        :param scope: -
        :param id: -
        :param repository_arn: (e.g. ``arn:aws:codecommit:us-east-1:123456789012:MyDemoRepo``).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__038fb3c413f4d36dca9b726fc6125b0350e96f89b020735d6da0a5845417dcad)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument repository_arn", value=repository_arn, expected_type=type_hints["repository_arn"])
        return typing.cast(IRepository, jsii.sinvoke(cls, "fromRepositoryArn", [scope, id, repository_arn]))

    @jsii.member(jsii_name="fromRepositoryName")
    @builtins.classmethod
    def from_repository_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        repository_name: builtins.str,
    ) -> IRepository:
        '''
        :param scope: -
        :param id: -
        :param repository_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__760c9cf58ca69a031e3f7454a4f9fb48fa2adf94b0dd300f78655add22a6c555)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
        return typing.cast(IRepository, jsii.sinvoke(cls, "fromRepositoryName", [scope, id, repository_name]))

    @jsii.member(jsii_name="bindAsNotificationRuleSource")
    def bind_as_notification_rule_source(
        self,
        _scope: _constructs_77d1e7e8.Construct,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleSourceConfig:
        '''Returns a source configuration for notification rule.

        :param _scope: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__583970bec05b0cbbdbba95cabb84b83692e09c84cd2bd39b9a235467508199c8)
            check_type(argname="argument _scope", value=_scope, expected_type=type_hints["_scope"])
        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleSourceConfig, jsii.invoke(self, "bindAsNotificationRuleSource", [_scope]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given principal identity permissions to perform the actions on this repository.

        :param grantee: -
        :param actions: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__effe40993194ef38e2fb70862a4a3bb6652b710e7a68f79e318b61baa8f2a971)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantPull")
    def grant_pull(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions to pull this repository.

        :param grantee: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e83abdbd5c279526d969719288e0e2b74f9db25e590535e6030ec9992ae000f)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantPull", [grantee]))

    @jsii.member(jsii_name="grantPullPush")
    def grant_pull_push(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions to pull and push this repository.

        :param grantee: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e55934828ae98f3fd991ee83a0c25c168821eb3d17cd304b3e36c5a3a9f18470)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantPullPush", [grantee]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    ) -> _aws_cdk_aws_iam_940a1ce0.Grant:
        '''Grant the given identity permissions to read this repository.

        :param grantee: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8fe4160d09032db0f3c7b187e2d2f2bf5a6b4e7f41f9a00efadc9972dd2ea65)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_940a1ce0.Grant, jsii.invoke(self, "grantRead", [grantee]))

    @jsii.member(jsii_name="notifiyOnPullRequestMerged")
    def notifiy_on_pull_request_merged(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when a pull request is merged.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71aa93fa1397dc2d66c25136821119307bca474852854f9f3f6ef50c87757ac0)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifiyOnPullRequestMerged", [id, target, options]))

    @jsii.member(jsii_name="notify")
    def notify(
        self,
        arn: builtins.str,
        *,
        branches: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_data: typing.Optional[builtins.str] = None,
        events: typing.Optional[typing.Sequence["RepositoryEventTrigger"]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "Repository":
        '''Create a trigger to notify another service to run actions on repository events.

        :param arn: Arn of the resource that repository events will notify.
        :param branches: The names of the branches in the AWS CodeCommit repository that contain events that you want to include in the trigger. If you don't specify at least one branch, the trigger applies to all branches.
        :param custom_data: When an event is triggered, additional information that AWS CodeCommit includes when it sends information to the target.
        :param events: The repository events for which AWS CodeCommit sends information to the target, which you specified in the DestinationArn property.If you don't specify events, the trigger runs for all repository events.
        :param name: A name for the trigger.Triggers on a repository must have unique names.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cf0de001cedadb520bbc42c122dbac038a4c3cac2677cf4d9975911eed9c2a1)
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        options = RepositoryTriggerOptions(
            branches=branches, custom_data=custom_data, events=events, name=name
        )

        return typing.cast("Repository", jsii.invoke(self, "notify", [arn, options]))

    @jsii.member(jsii_name="notifyOn")
    def notify_on(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        events: typing.Sequence["RepositoryNotificationEvents"],
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule triggered when the project events specified by you are emitted. Similar to ``onEvent`` API.

        You can also use the methods to define rules for the specific event emitted.
        eg: ``notifyOnPullRequstCreated``.

        :param id: -
        :param target: -
        :param events: A list of event types associated with this notification rule for CodeCommit repositories. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__811a60e79315cda4053534e9f4dfd51f3c641504248cf6c0c76b790675af02a6)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = RepositoryNotifyOnOptions(
            events=events,
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOn", [id, target, options]))

    @jsii.member(jsii_name="notifyOnApprovalRuleOverridden")
    def notify_on_approval_rule_overridden(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when an approval rule is overridden.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d922db2048d4233a31b7dc30de182f2308afbe091d8ced5c07a8cad829a05667)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnApprovalRuleOverridden", [id, target, options]))

    @jsii.member(jsii_name="notifyOnApprovalStatusChanged")
    def notify_on_approval_status_changed(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when an approval status is changed.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__532a18cc4ba3ce06c8e2bdbc7eed23a31ba0c3444dc62e8a9af121a08f3a7550)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnApprovalStatusChanged", [id, target, options]))

    @jsii.member(jsii_name="notifyOnBranchOrTagCreated")
    def notify_on_branch_or_tag_created(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when a new branch or tag is created.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1015eccb5d9010a4313c1c1d34d8d8e88a287fa764c84ce752c317047b24c32)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnBranchOrTagCreated", [id, target, options]))

    @jsii.member(jsii_name="notifyOnBranchOrTagDeleted")
    def notify_on_branch_or_tag_deleted(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when a branch or tag is deleted.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13b41e0a8e6b06be91398239e17ff4109ad60999e690abaebb8d205cd2dd52b7)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnBranchOrTagDeleted", [id, target, options]))

    @jsii.member(jsii_name="notifyOnPullRequestComment")
    def notify_on_pull_request_comment(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when a comment is made on a pull request.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc18e4e522f97015392e88d038528d9eed92fb033c74f21424c20a8889b07a53)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnPullRequestComment", [id, target, options]))

    @jsii.member(jsii_name="notifyOnPullRequestCreated")
    def notify_on_pull_request_created(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when a pull request is created.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29dccf2152a94ffca7cd28dbc2dc8e2ae79122428f13b2c51ee3157f9037d2df)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnPullRequestCreated", [id, target, options]))

    @jsii.member(jsii_name="notifyOnPullRequestMerged")
    def notify_on_pull_request_merged(
        self,
        id: builtins.str,
        target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule:
        '''Defines a CodeStar Notification rule which triggers when a pull request is merged.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e3a65a5e48fa9048e035340c0a8d19d56fbd67aff6c08fbf713b82b169b41b5)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
        options = _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_aws_cdk_aws_codestarnotifications_391e8ded.INotificationRule, jsii.invoke(self, "notifyOnPullRequestMerged", [id, target, options]))

    @jsii.member(jsii_name="onCommentOnCommit")
    def on_comment_on_commit(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a comment is made on a commit.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdee3c05a642c648da43d10d6eab55a4274c06c3df21d48a0d739b8970f0e38d)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onCommentOnCommit", [id, options]))

    @jsii.member(jsii_name="onCommentOnPullRequest")
    def on_comment_on_pull_request(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a comment is made on a pull request.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42ccdd99d31c1f1fdb0923f5ce0d2f3ed7191c80ce6f936000695554b3593595)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onCommentOnPullRequest", [id, options]))

    @jsii.member(jsii_name="onCommit")
    def on_commit(
        self,
        id: builtins.str,
        *,
        branches: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a commit is pushed to a branch.

        :param id: -
        :param branches: The branch to monitor. Default: - All branches
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ac65899d76bfd68cdc05a50672b9eb9a98c711cbb2af6489e86e78d0576738b)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = OnCommitOptions(
            branches=branches,
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onCommit", [id, options]))

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
        '''Defines a CloudWatch event rule which triggers for repository events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02b144e596b8f844439b097589a144898fbed08ba582933c054105268faafd2e)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onEvent", [id, options]))

    @jsii.member(jsii_name="onPullRequestStateChange")
    def on_pull_request_state_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a pull request state is changed.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d303539716f0cad6298567cccd06b87fa503f590cad8f36ad61a7e4907d3f49)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onPullRequestStateChange", [id, options]))

    @jsii.member(jsii_name="onReferenceCreated")
    def on_reference_created(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a reference is created (i.e. a new branch/tag is created) to the repository.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fe8495792affa1be87f234cdfe1db5b867e6cf10682bb85d0cfabc220ff1361)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onReferenceCreated", [id, options]))

    @jsii.member(jsii_name="onReferenceDeleted")
    def on_reference_deleted(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a reference is delete (i.e. a branch/tag is deleted) from the repository.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__457ee694b8e3f5fcd6674c1da03c244a432012454b710b06214547ed5dca9c6a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onReferenceDeleted", [id, options]))

    @jsii.member(jsii_name="onReferenceUpdated")
    def on_reference_updated(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    ) -> _aws_cdk_aws_events_efcdfa54.Rule:
        '''Defines a CloudWatch event rule which triggers when a reference is updated (i.e. a commit is pushed to an existing or new branch) from the repository.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8c7cb939c4c06c8165f723e898d29aa5c0eb00b7dc081fdd7346f8566e93e88)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onReferenceUpdated", [id, options]))

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
        '''Defines a CloudWatch event rule which triggers when a "CodeCommit Repository State Change" event occurs.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49698d1046f92255958399add52af71b8f04164573541b2e02fc14f2ac06ed36)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_efcdfa54.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_aws_cdk_aws_events_efcdfa54.Rule, jsii.invoke(self, "onStateChange", [id, options]))

    @builtins.property
    @jsii.member(jsii_name="repositoryArn")
    def repository_arn(self) -> builtins.str:
        '''The ARN of this Repository.'''
        return typing.cast(builtins.str, jsii.get(self, "repositoryArn"))

    @builtins.property
    @jsii.member(jsii_name="repositoryCloneUrlGrc")
    def repository_clone_url_grc(self) -> builtins.str:
        '''The HTTPS (GRC) clone URL.

        HTTPS (GRC) is the protocol to use with git-remote-codecommit (GRC).

        It is the recommended method for supporting connections made with federated
        access, identity providers, and temporary credentials.
        '''
        return typing.cast(builtins.str, jsii.get(self, "repositoryCloneUrlGrc"))

    @builtins.property
    @jsii.member(jsii_name="repositoryCloneUrlHttp")
    def repository_clone_url_http(self) -> builtins.str:
        '''The HTTP clone URL.'''
        return typing.cast(builtins.str, jsii.get(self, "repositoryCloneUrlHttp"))

    @builtins.property
    @jsii.member(jsii_name="repositoryCloneUrlSsh")
    def repository_clone_url_ssh(self) -> builtins.str:
        '''The SSH clone URL.'''
        return typing.cast(builtins.str, jsii.get(self, "repositoryCloneUrlSsh"))

    @builtins.property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        '''The human-visible name of this Repository.'''
        return typing.cast(builtins.str, jsii.get(self, "repositoryName"))


@jsii.enum(jsii_type="@aws-cdk/aws-codecommit.RepositoryEventTrigger")
class RepositoryEventTrigger(enum.Enum):
    '''Repository events that will cause the trigger to run actions in another service.'''

    ALL = "ALL"
    UPDATE_REF = "UPDATE_REF"
    CREATE_REF = "CREATE_REF"
    DELETE_REF = "DELETE_REF"


@jsii.enum(jsii_type="@aws-cdk/aws-codecommit.RepositoryNotificationEvents")
class RepositoryNotificationEvents(enum.Enum):
    '''List of event types for AWS CodeCommit.

    :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-repositories
    '''

    COMMIT_COMMENT = "COMMIT_COMMENT"
    '''Trigger notication when comment made on commit.'''
    PULL_REQUEST_COMMENT = "PULL_REQUEST_COMMENT"
    '''Trigger notification when comment made on pull request.'''
    APPROVAL_STATUS_CHANGED = "APPROVAL_STATUS_CHANGED"
    '''Trigger notification when approval status changed.'''
    APPROVAL_RULE_OVERRIDDEN = "APPROVAL_RULE_OVERRIDDEN"
    '''Trigger notifications when approval rule is overridden.'''
    PULL_REQUEST_CREATED = "PULL_REQUEST_CREATED"
    '''Trigger notification when pull request created.'''
    PULL_REQUEST_SOURCE_UPDATED = "PULL_REQUEST_SOURCE_UPDATED"
    '''Trigger notification when pull request source updated.'''
    PULL_REQUEST_STATUS_CHANGED = "PULL_REQUEST_STATUS_CHANGED"
    '''Trigger notification when pull request status is changed.'''
    PULL_REQUEST_MERGED = "PULL_REQUEST_MERGED"
    '''Trigger notification when pull requset is merged.'''
    BRANCH_OR_TAG_CREATED = "BRANCH_OR_TAG_CREATED"
    '''Trigger notification when a branch or tag is created.'''
    BRANCH_OR_TAG_DELETED = "BRANCH_OR_TAG_DELETED"
    '''Trigger notification when a branch or tag is deleted.'''
    BRANCH_OR_TAG_UPDATED = "BRANCH_OR_TAG_UPDATED"
    '''Trigger notification when a branch or tag is updated.'''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codecommit.RepositoryNotifyOnOptions",
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
class RepositoryNotifyOnOptions(
    _aws_cdk_aws_codestarnotifications_391e8ded.NotificationRuleOptions,
):
    def __init__(
        self,
        *,
        detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
        events: typing.Sequence[RepositoryNotificationEvents],
    ) -> None:
        '''Additional options to pass to the notification rule.

        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        :param events: A list of event types associated with this notification rule for CodeCommit repositories. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codecommit as codecommit
            import aws_cdk.aws_codestarnotifications as codestarnotifications
            
            repository_notify_on_options = codecommit.RepositoryNotifyOnOptions(
                events=[codecommit.RepositoryNotificationEvents.COMMIT_COMMENT],
            
                # the properties below are optional
                detail_type=codestarnotifications.DetailType.BASIC,
                enabled=False,
                notification_rule_name="notificationRuleName"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b60c1dd760ade8c49c803d5520910a976847a7e323b0a654238ca5c6e3bfe3de)
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
    def events(self) -> typing.List[RepositoryNotificationEvents]:
        '''A list of event types associated with this notification rule for CodeCommit repositories.

        For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#concepts-api
        '''
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[RepositoryNotificationEvents], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryNotifyOnOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codecommit.RepositoryProps",
    jsii_struct_bases=[],
    name_mapping={
        "repository_name": "repositoryName",
        "code": "code",
        "description": "description",
    },
)
class RepositoryProps:
    def __init__(
        self,
        *,
        repository_name: builtins.str,
        code: typing.Optional[Code] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param repository_name: Name of the repository. This property is required for all CodeCommit repositories.
        :param code: The contents with which to initialize the repository after it has been created. Default: - No initialization (create empty repo)
        :param description: A description of the repository. Use the description to identify the purpose of the repository. Default: - No description.

        :exampleMetadata: lit=test/integ.cfn-template-from-repo.lit.ts infused

        Example::

            # Source stage: read from repository
            repo = codecommit.Repository(stack, "TemplateRepo",
                repository_name="template-repo"
            )
            source_output = codepipeline.Artifact("SourceArtifact")
            source = cpactions.CodeCommitSourceAction(
                action_name="Source",
                repository=repo,
                output=source_output,
                trigger=cpactions.CodeCommitTrigger.POLL
            )
            source_stage = {
                "stage_name": "Source",
                "actions": [source]
            }
            
            # Deployment stage: create and deploy changeset with manual approval
            stack_name = "OurStack"
            change_set_name = "StagedChangeSet"
            
            prod_stage = {
                "stage_name": "Deploy",
                "actions": [
                    cpactions.CloudFormationCreateReplaceChangeSetAction(
                        action_name="PrepareChanges",
                        stack_name=stack_name,
                        change_set_name=change_set_name,
                        admin_permissions=True,
                        template_path=source_output.at_path("template.yaml"),
                        run_order=1
                    ),
                    cpactions.ManualApprovalAction(
                        action_name="ApproveChanges",
                        run_order=2
                    ),
                    cpactions.CloudFormationExecuteChangeSetAction(
                        action_name="ExecuteChanges",
                        stack_name=stack_name,
                        change_set_name=change_set_name,
                        run_order=3
                    )
                ]
            }
            
            codepipeline.Pipeline(stack, "Pipeline",
                stages=[source_stage, prod_stage
                ]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5100a0c65f0257c3fa93902ed45493a0eeb499d7c4ef50b102796364b6c10c5b)
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
            check_type(argname="argument code", value=code, expected_type=type_hints["code"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "repository_name": repository_name,
        }
        if code is not None:
            self._values["code"] = code
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def repository_name(self) -> builtins.str:
        '''Name of the repository.

        This property is required for all CodeCommit repositories.
        '''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code(self) -> typing.Optional[Code]:
        '''The contents with which to initialize the repository after it has been created.

        :default: - No initialization (create empty repo)
        '''
        result = self._values.get("code")
        return typing.cast(typing.Optional[Code], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the repository.

        Use the description to identify the
        purpose of the repository.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-codecommit.RepositoryTriggerOptions",
    jsii_struct_bases=[],
    name_mapping={
        "branches": "branches",
        "custom_data": "customData",
        "events": "events",
        "name": "name",
    },
)
class RepositoryTriggerOptions:
    def __init__(
        self,
        *,
        branches: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_data: typing.Optional[builtins.str] = None,
        events: typing.Optional[typing.Sequence[RepositoryEventTrigger]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Creates for a repository trigger to an SNS topic or Lambda function.

        :param branches: The names of the branches in the AWS CodeCommit repository that contain events that you want to include in the trigger. If you don't specify at least one branch, the trigger applies to all branches.
        :param custom_data: When an event is triggered, additional information that AWS CodeCommit includes when it sends information to the target.
        :param events: The repository events for which AWS CodeCommit sends information to the target, which you specified in the DestinationArn property.If you don't specify events, the trigger runs for all repository events.
        :param name: A name for the trigger.Triggers on a repository must have unique names.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_codecommit as codecommit
            
            repository_trigger_options = codecommit.RepositoryTriggerOptions(
                branches=["branches"],
                custom_data="customData",
                events=[codecommit.RepositoryEventTrigger.ALL],
                name="name"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dffc3d46f334ec78217ae3048b37804a3e95c07997687027c74dbd5813d907bf)
            check_type(argname="argument branches", value=branches, expected_type=type_hints["branches"])
            check_type(argname="argument custom_data", value=custom_data, expected_type=type_hints["custom_data"])
            check_type(argname="argument events", value=events, expected_type=type_hints["events"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if branches is not None:
            self._values["branches"] = branches
        if custom_data is not None:
            self._values["custom_data"] = custom_data
        if events is not None:
            self._values["events"] = events
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def branches(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The names of the branches in the AWS CodeCommit repository that contain events that you want to include in the trigger.

        If you don't specify at
        least one branch, the trigger applies to all branches.
        '''
        result = self._values.get("branches")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_data(self) -> typing.Optional[builtins.str]:
        '''When an event is triggered, additional information that AWS CodeCommit includes when it sends information to the target.'''
        result = self._values.get("custom_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def events(self) -> typing.Optional[typing.List[RepositoryEventTrigger]]:
        '''The repository events for which AWS CodeCommit sends information to the target, which you specified in the DestinationArn property.If you don't specify events, the trigger runs for all repository events.'''
        result = self._values.get("events")
        return typing.cast(typing.Optional[typing.List[RepositoryEventTrigger]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''A name for the trigger.Triggers on a repository must have unique names.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryTriggerOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnRepository",
    "CfnRepositoryProps",
    "Code",
    "CodeConfig",
    "IRepository",
    "OnCommitOptions",
    "ReferenceEvent",
    "Repository",
    "RepositoryEventTrigger",
    "RepositoryNotificationEvents",
    "RepositoryNotifyOnOptions",
    "RepositoryProps",
    "RepositoryTriggerOptions",
]

publication.publish()

def _typecheckingstub__5ecf2869d7dc24b44482727fb08e2389fbeb198987cc194637a66d0e47801574(
    scope: _aws_cdk_core_f4b25747.Construct,
    id: builtins.str,
    *,
    repository_name: builtins.str,
    code: typing.Optional[typing.Union[typing.Union[CfnRepository.CodeProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]] = None,
    repository_description: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    triggers: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnRepository.RepositoryTriggerProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__692604e9933675b0b3135d8ae8e9dfc0a0003eaf16ed3fbc6415f12f865abd74(
    inspector: _aws_cdk_core_f4b25747.TreeInspector,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4b41946f6d1087c719909ec37e42b061a719a54dd9bade6f824bf055b7f32d1(
    props: typing.Mapping[builtins.str, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c28e8276a640b2a22c4842ba6dd08a926f1dbf807c633c88a41b4637f5fbd4a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c6629a41223605318bdd941bf139b2c2ce132f9bdb18bb14deb25147ced5ad2(
    value: typing.Optional[typing.Union[CfnRepository.CodeProperty, _aws_cdk_core_f4b25747.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd0f09793e38f607fb65e562aea547bbb709c1700f891ddfa6e306129a04affc(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b224c103195dd538cae80f84fa688044c5245961043f1afc17750f9774590c1(
    value: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.List[typing.Union[_aws_cdk_core_f4b25747.IResolvable, CfnRepository.RepositoryTriggerProperty]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa4d326bfd86ee9953273907985521a90b2c66cc6b1ba4d0d19888af5a0340f9(
    *,
    s3: typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnRepository.S3Property, typing.Dict[builtins.str, typing.Any]]],
    branch_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80ef2cc4fbdc22d3a6305a881576904ae02fe29ecb5a62cb310f89524b3dfa00(
    *,
    destination_arn: builtins.str,
    events: typing.Sequence[builtins.str],
    name: builtins.str,
    branches: typing.Optional[typing.Sequence[builtins.str]] = None,
    custom_data: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e01f9a462ed8c791e05a31d54053198cf2ec948d8dbc9bf396d5555be4229f9c(
    *,
    bucket: builtins.str,
    key: builtins.str,
    object_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2103615b896119597efd165576c74356255b7592e15d875437b9ff3e47be3e18(
    *,
    repository_name: builtins.str,
    code: typing.Optional[typing.Union[typing.Union[CfnRepository.CodeProperty, typing.Dict[builtins.str, typing.Any]], _aws_cdk_core_f4b25747.IResolvable]] = None,
    repository_description: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    triggers: typing.Optional[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Sequence[typing.Union[_aws_cdk_core_f4b25747.IResolvable, typing.Union[CfnRepository.RepositoryTriggerProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b732f0efeb4f5689123e92f8bfbeba7fbaf4d0d128e8ec1af70ef66e5af0abd4(
    asset: _aws_cdk_aws_s3_assets_525817d7.Asset,
    branch: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd6dd1afd691420a555123a47372d6fe7b35102be21aa52f359a417f5e73f744(
    directory_path: builtins.str,
    branch: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05abfc1f720e5660bf856381274eaa81451d36ec3b4555f3d0ea83bff6e1aa3d(
    file_path: builtins.str,
    branch: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65e2733119140823206084c1be88dac06a28126c0613e060bad6cede974c8d3b(
    scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aed044a5f9443a0b0b804ed268d8e7ec3ce5fe19949f044f32a130cb79992aac(
    *,
    code: typing.Union[CfnRepository.CodeProperty, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5a8177a6cf590d8c82e6de87bef54b98fabee49248726312feea0622bd22fc0(
    grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcc89abe80ba4136feb0c15be610b76e95387c1719a8d187578a09d39e84b1f6(
    grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d0b1c9ace218834acc264be9e184de825d9ae50bb6782aaa8a44c1d61acbf55(
    grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea04213de3d198b597d590cdb6f5db673cdbad511c5bd29c1b85cf15c387a93e(
    grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acf48e8f11b10c3cd2e6d55e036c20c9d70479b30370fd3a7f781212c01cd8ea(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f40058eeaf452ced71dc49730a10700cd3b14519f0d62ec0c50c8eb115bd014e(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    events: typing.Sequence[RepositoryNotificationEvents],
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c5fde7b76f0d86bc3668a2526cbb27507757d190c48ae5b76c6d508f609c2b2(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2af79a53a8fc91ecb31308c5a15f53e8e47c066946fa4e950334cc725e67e99(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92ce7090a744c648d7a01bc1bde51c6cda8de5f0ad98abd88793a410da35b78f(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6aac79e4c5fc7c8040d99c4203ae387b1bd56b18d05248debaa00c69c4037092(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93e4a8542d74fcd8006a353431e8c9215776da2daae31c655536a88911d052d2(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__754850bc93417cb26233c50a30df16d1e753899fd850e1a5bda7dfa1a8929452(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8d7aabe857108774ef1c61e3af4a5e0f351fb59d8773c40af6ca12b818a1f33(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b09f5603377b407596651d366dadce4aa8b12322b94722c6205bd1d46c5f8d7(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__200a6edfb8b39904613976128fc26c4a3f2bae7181be4c51c67f854d1b295975(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4227d86c89e250bf22adc3122e3c8d1275198348172651201fce94f6d0f10305(
    id: builtins.str,
    *,
    branches: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98ab8e85d61ef8ba6dd3db1696ec81241aabf66ae5168633300261902d7ad02a(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d772bb61311c7385bf987d5b17fec163a33b122c0e7710217121c46c5942f948(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__288ffa914f33812846070049d40597ebd57ad83ec51d448992b441c9d632150a(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a34d8bdcfb5c89bbf1a14e7407e236843cde84e557b135b58009495ca290123(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbdc1ed423a16e1e83b94093d3e8e4890f15197a8598030fde54c3439821977d(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87365ddb257bae5d0ea3f7480554f742082c1a97b699252a0518cc9a3e2be379(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__578249a4366c91f7021ab10cdd180ee33346c1a932b6222e8556213b1b4d4588(
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
    branches: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c825ecda8071bdb9f5be001248a08eb1b55c9f65defdd68fbd9e176f007c5028(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    repository_name: builtins.str,
    code: typing.Optional[Code] = None,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__038fb3c413f4d36dca9b726fc6125b0350e96f89b020735d6da0a5845417dcad(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    repository_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__760c9cf58ca69a031e3f7454a4f9fb48fa2adf94b0dd300f78655add22a6c555(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    repository_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__583970bec05b0cbbdbba95cabb84b83692e09c84cd2bd39b9a235467508199c8(
    _scope: _constructs_77d1e7e8.Construct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__effe40993194ef38e2fb70862a4a3bb6652b710e7a68f79e318b61baa8f2a971(
    grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e83abdbd5c279526d969719288e0e2b74f9db25e590535e6030ec9992ae000f(
    grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e55934828ae98f3fd991ee83a0c25c168821eb3d17cd304b3e36c5a3a9f18470(
    grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8fe4160d09032db0f3c7b187e2d2f2bf5a6b4e7f41f9a00efadc9972dd2ea65(
    grantee: _aws_cdk_aws_iam_940a1ce0.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71aa93fa1397dc2d66c25136821119307bca474852854f9f3f6ef50c87757ac0(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cf0de001cedadb520bbc42c122dbac038a4c3cac2677cf4d9975911eed9c2a1(
    arn: builtins.str,
    *,
    branches: typing.Optional[typing.Sequence[builtins.str]] = None,
    custom_data: typing.Optional[builtins.str] = None,
    events: typing.Optional[typing.Sequence[RepositoryEventTrigger]] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__811a60e79315cda4053534e9f4dfd51f3c641504248cf6c0c76b790675af02a6(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    events: typing.Sequence[RepositoryNotificationEvents],
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d922db2048d4233a31b7dc30de182f2308afbe091d8ced5c07a8cad829a05667(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__532a18cc4ba3ce06c8e2bdbc7eed23a31ba0c3444dc62e8a9af121a08f3a7550(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1015eccb5d9010a4313c1c1d34d8d8e88a287fa764c84ce752c317047b24c32(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13b41e0a8e6b06be91398239e17ff4109ad60999e690abaebb8d205cd2dd52b7(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc18e4e522f97015392e88d038528d9eed92fb033c74f21424c20a8889b07a53(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29dccf2152a94ffca7cd28dbc2dc8e2ae79122428f13b2c51ee3157f9037d2df(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e3a65a5e48fa9048e035340c0a8d19d56fbd67aff6c08fbf713b82b169b41b5(
    id: builtins.str,
    target: _aws_cdk_aws_codestarnotifications_391e8ded.INotificationRuleTarget,
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdee3c05a642c648da43d10d6eab55a4274c06c3df21d48a0d739b8970f0e38d(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42ccdd99d31c1f1fdb0923f5ce0d2f3ed7191c80ce6f936000695554b3593595(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ac65899d76bfd68cdc05a50672b9eb9a98c711cbb2af6489e86e78d0576738b(
    id: builtins.str,
    *,
    branches: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02b144e596b8f844439b097589a144898fbed08ba582933c054105268faafd2e(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d303539716f0cad6298567cccd06b87fa503f590cad8f36ad61a7e4907d3f49(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fe8495792affa1be87f234cdfe1db5b867e6cf10682bb85d0cfabc220ff1361(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__457ee694b8e3f5fcd6674c1da03c244a432012454b710b06214547ed5dca9c6a(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8c7cb939c4c06c8165f723e898d29aa5c0eb00b7dc081fdd7346f8566e93e88(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49698d1046f92255958399add52af71b8f04164573541b2e02fc14f2ac06ed36(
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_efcdfa54.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
    target: typing.Optional[_aws_cdk_aws_events_efcdfa54.IRuleTarget] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b60c1dd760ade8c49c803d5520910a976847a7e323b0a654238ca5c6e3bfe3de(
    *,
    detail_type: typing.Optional[_aws_cdk_aws_codestarnotifications_391e8ded.DetailType] = None,
    enabled: typing.Optional[builtins.bool] = None,
    notification_rule_name: typing.Optional[builtins.str] = None,
    events: typing.Sequence[RepositoryNotificationEvents],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5100a0c65f0257c3fa93902ed45493a0eeb499d7c4ef50b102796364b6c10c5b(
    *,
    repository_name: builtins.str,
    code: typing.Optional[Code] = None,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dffc3d46f334ec78217ae3048b37804a3e95c07997687027c74dbd5813d907bf(
    *,
    branches: typing.Optional[typing.Sequence[builtins.str]] = None,
    custom_data: typing.Optional[builtins.str] = None,
    events: typing.Optional[typing.Sequence[RepositoryEventTrigger]] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
