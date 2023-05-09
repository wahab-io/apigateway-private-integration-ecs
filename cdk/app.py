#!/usr/bin/env python3
import os

import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns


app = cdk.App()
stack = cdk.Stack(app, "ApiGatewayNlbEcsStack")

# create a VPC
vpc = ec2.Vpc(stack, "VPC", max_azs=3)

# create ecs cluster and network load balancer service
cluster = ecs.Cluster(stack, "EcsCluster")
ecs_patterns.NetworkLoadBalancedFargateService(
    stack,
    "Service",
    cluster=cluster,
    vpc=vpc,
    memory_limit_mib=4096,
    cpu=1024,
    task_image_options=ecs_patterns.NetworkLoadBalancedTaskImageOptions(image="")
)

app.synth()
