import json
import subprocess


def get_lambdas():
    functions = {}
    res = subprocess.Popen(
        ["aws", "lambda", "list-functions"],
        stdout=subprocess.PIPE,
    )
    output = res.communicate()[0]
    functions.update(json.loads(output))
    return functions["Functions"]


# for lambda_function in get_lambdas():
#     function_name = lambda_function["FunctionName"]

with open(".env", "r") as f:
    env_vars = [
        line for line in f.read().splitlines() if line.startswith("SOLESEARCH_")
    ]
    env = ",".join(env_vars)
    subprocess.run(
        [
            "aws",
            "lambda",
            "update-function-configuration",
            "--region",
            "us-east-1",
            "--function-name",
            "solesearch-api",
            "--environment",
            f"Variables={{{env}}}",
        ]
    )
