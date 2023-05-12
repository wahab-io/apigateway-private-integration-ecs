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
from aws_cdk.pipelines import FileSet

from constructs import Construct

from deployment import Deployment


class Pipeline(cdk.Stack):
    def __init__(
        self,
        scope: Construct | None = None,
        id: str | None = None,
        *,
        analytics_reporting: bool | None = None,
        cross_region_references: bool | None = None,
        description: str | None = None,
        env: Environment | Dict[str, Any] | None = None,
        permissions_boundary: PermissionsBoundary | None = None,
        stack_name: str | None = None,
        synthesizer: IStackSynthesizer | None = None,
        tags: Mapping[str, str] | None = None,
        termination_protection: bool | None = None
    ) -> None:
        super().__init__(
            scope,
            id,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        repository = codecommit.Repository(
            self,
            "Repository",
            repository_name="aws-ecs-fargate-nlb-apigateway",
        )

        sample_app_repository = ecr.Repository(
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
            environment=codebuild.BuildEnvironment(privileged=True),
            environment_variables={
                "AWS_ACCOUNT_ID": codebuild.BuildEnvironmentVariable(
                    value=self.account
                ),
                "IMAGE_REPO_NAME": codebuild.BuildEnvironmentVariable(
                    value="sample-app"
                ),
            },
        )
        sample_app_repository.grant_pull_push(sample_app_build_project)

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

        non_prod = Deployment(self, "NonProd")
        code_pipeline.add_stage(non_prod)
