"""Repository stack that creates ECR repositories for the application.
"""
from typing import Any
import aws_cdk as cdk
from aws_cdk import aws_ecr as ecr

from constructs import Construct


class Repository(cdk.Stack):
    """Repository stack that creates ECR repositories for the application.

    Args:
        Stack: Construct class.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.image_repository = ecr.Repository(
            self, "ContainerRepository", repository_name="sample-app"
        )
