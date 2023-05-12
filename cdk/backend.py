"""Backend stack that creates all resources
"""
from typing import Mapping, Dict, Any
import aws_cdk as cdk
from aws_cdk import Environment, IStackSynthesizer, PermissionsBoundary
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_logs as logs
from constructs import Construct


class Backend(cdk.Stack):
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
        termination_protection: bool | None = None,
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

        vpc = ec2.Vpc(self, "VPC", max_azs=3)
        nlb = elbv2.NetworkLoadBalancer(self, "NLB", vpc=vpc)
        vpc_link = apigw.VpcLink(self, "VpcLink", targets=[nlb])

        proxy = "{proxy}"
        integration = apigw.Integration(
            type=apigw.IntegrationType.HTTP_PROXY,
            integration_http_method="ANY",
            options=apigw.IntegrationOptions(
                connection_type=apigw.ConnectionType.VPC_LINK,
                vpc_link=vpc_link,
                request_parameters={
                    "integration.request.path.proxy": "method.request.path.proxy"
                },
            ),
            uri=f"http://{nlb.load_balancer_dns_name}/{proxy}",
        )

        log_group = logs.LogGroup(self, "APIGatewayAccessLogs")

        api = apigw.RestApi(
            self,
            "RestApi",
            deploy_options=apigw.StageOptions(
                tracing_enabled=True,
                access_log_destination=apigw.LogGroupLogDestination(log_group),
            ),
        )
        api.root.add_proxy(
            any_method=True,
            default_integration=integration,
            default_method_options=apigw.MethodOptions(
                request_parameters={"method.request.path.proxy": True}
            ),
        )

        cluster = ecs.Cluster(self, "Cluster", vpc=vpc, container_insights=True)
        sample_app_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self,
            "FlaskService",
            cluster=cluster,
            load_balancer=nlb,
            memory_limit_mib=1024,
            cpu=512,
            runtime_platform=ecs.RuntimePlatform(
                cpu_architecture=ecs.CpuArchitecture.ARM64,
                operating_system_family=ecs.OperatingSystemFamily.LINUX,
            ),
            task_image_options=ecs_patterns.NetworkLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_ecr_repository(
                    ecr.Repository.from_repository_name(
                        self, "SampleApp", repository_name="sample-app"
                    )
                ),
                container_port=5000,
            ),
        )

        sample_app_service.service.connections.allow_from(
            ec2.Peer.ipv4("10.0.0.0/16"),
            ec2.Port.tcp(5000),
            "Allow connection from NLB",
        )
