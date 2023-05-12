"""Deployment Stage
"""

from typing import Dict, Any, Sequence
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import Environment, IPolicyValidationPluginBeta1, PermissionsBoundary
from backend import Backend


class Deployment(cdk.Stage):
    """Deployment(cdk.Stage)

    Args:
        cdk (Stage): Base class for Stage
    """

    def __init__(
        self,
        scope: Construct,
        unique_id: str,
        *,
        env: Environment | Dict[str, Any] | None = None,
        outdir: str | None = None,
        permissions_boundary: PermissionsBoundary | None = None,
        policy_validation_beta1: Sequence[IPolicyValidationPluginBeta1] | None = None,
        stage_name: str | None = None
    ) -> None:
        super().__init__(
            scope,
            unique_id,
            env=env,
            outdir=outdir,
            permissions_boundary=permissions_boundary,
            policy_validation_beta1=policy_validation_beta1,
            stage_name=stage_name,
        )

        Backend(self, "Backend")
