import builtins
from os import path

from typing import Mapping, Dict, Any
import aws_cdk as cdk
from aws_cdk import Environment, IStackSynthesizer, PermissionsBoundary, pipelines
from aws_cdk import aws_codecommit as codecommit
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as actions
from aws_cdk import aws_ecr as ecr

from constructs import Construct

from deployment import Deployment


class Pipeline(cdk.Stack):
    """Pipeline stack that creates a codepipeline that deploys the sample-app to ECS Fargate and NLB with API Gateway



    Args:
        Stack: cdk.Stack (Construct Class)
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        image_repository: ecr.Repository | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repository = codecommit.Repository(
            self,
            "Repository",
            repository_name="aws-ecs-fargate-nlb-apigateway",
        )

        if image_repository is None:
            image_repository = ecr.Repository(
                self, "ContainerRepository", repository_name="sample-app"
            )

        # create a codepipeline
        pipeline = codepipeline.Pipeline(self, "CodePipeline")

        # source
        source_output = codepipeline.Artifact()
        source_action = actions.CodeCommitSourceAction(
            action_name="CodeCommit",
            repository=repository,
            branch="main",
            output=source_output,
            code_build_clone_output=True,
        )
        pipeline.add_stage(stage_name="Source", actions=[source_action])

        # codebuild project that will create the docker image for sample-app and push it to ECR
        sample_app_build_project = codebuild.PipelineProject(
            self,
            "DockerBuild",
            build_spec=codebuild.BuildSpec.from_source_filename(
                "sample-app/buildspec.yml"
            ),
            environment=codebuild.BuildEnvironment(
                compute_type=codebuild.ComputeType.LARGE,
                build_image=codebuild.LinuxArmBuildImage.AMAZON_LINUX_2_STANDARD_2_0,
                privileged=True,
            ),
            environment_variables={
                "AWS_ACCOUNT_ID": codebuild.BuildEnvironmentVariable(
                    value=self.account
                ),
                "IMAGE_REPO_NAME": codebuild.BuildEnvironmentVariable(
                    value="sample-app"
                ),
            },
        )

        # grant codebuild project access to ECR
        image_repository.grant_pull_push(sample_app_build_project)

        # add codebuild project to code pipeline as stage
        pipeline.add_stage(
            stage_name="BuildImage",
            actions=[
                actions.CodeBuildAction(
                    action_name="CodeBuild",
                    project=sample_app_build_project,
                    input=source_output,
                    outputs=[codepipeline.Artifact("imagedefinitions")],
                )
            ],
        )

        code_pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            code_pipeline=pipeline,
            synth=pipelines.ShellStep(
                "ShellStep",
                input=pipelines.CodePipelineFileSet.from_artifact(source_output),
                commands=[
                    "npm install",
                    "cd cdk",
                    "pip install -r requirements.txt",
                    "npx cdk synth --output ../cdk.out",
                ],
            ),
        )

        non_prod = Deployment(
            self,
            "NonProd",
        )
        code_pipeline.add_stage(non_prod)
