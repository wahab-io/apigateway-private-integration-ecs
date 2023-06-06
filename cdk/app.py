#!/usr/bin/env python3
import aws_cdk as cdk
from pipeline import Pipeline
from backend import Backend
from repository import Repository


app = cdk.App()

# create a repository stack
repository = Repository(app, "Repository", env=cdk.Environment(region="us-east-1"))

# create a backend stack outside the scope of the pipeline
backend = Backend(app, "Backend", env=cdk.Environment(region="us-east-1"))
backend.add_dependency(repository)

# create a pipeline stack that can deploy backend as part of CI/CD
pipeline = Pipeline(app, "Pipeline", env=cdk.Environment(region="us-west-2"))

app.synth()
