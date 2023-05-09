from typing import Mapping, Dict, Any
import aws_cdk as cdk
from aws_cdk import Environment, IStackSynthesizer, PermissionsBoundary, pipelines

from constructs import Construct


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

        pipelines.CodePipeline(self, "Pipeline", synth=pipelines.ShellStep())
