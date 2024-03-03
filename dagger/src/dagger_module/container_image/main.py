# Run this pipeline with
# AWS_PROFILE=personal_admin container-image -p 3.12 -s /home/adrian/repos/anime-recommender/src/indexer/ -n dagger-test -t 0.0.1
# container-image -p 3.12 -s /home/adrian/repos/anime-recommender/src/indexer/ -n dagger-test -t 0.0.1

from dataclasses import dataclass
import sys
from pathlib import Path
from argparse import ArgumentParser
from typing import Optional

import anyio
import dagger
from dagger import BuildArg, dag
from dagger_module.common.aws import ECRClient, ECRCreds
from dagger_module.common import config as cfg


@dataclass
class FunctionConfig:
    python_version: str
    src: str
    name: str
    tag: str
    dockerfile_path: Optional[str] = None


def contains_dockerfile(src: str):
    docker_path = Path(src) / "Dockerfile"

    if docker_path.is_file():
        return True

    return False


def arg_parser():
    parser = ArgumentParser()
    parser.add_argument("-p", "--python-version", dest="python_version")
    parser.add_argument("-s", "--src", dest="src", type=str)
    parser.add_argument("-n", "--name", dest="name")
    parser.add_argument("-t", "--tag", dest="tag")
    return parser


async def function_build(
    func_cfg: FunctionConfig,
    ecr_creds: ECRCreds,
) -> None:
    publish_uri = f"{ecr_creds.uri}/{func_cfg.name}:{func_cfg.tag}"
    base_img = cfg.LAMBDA_IMAGE.format(python_version=func_cfg.python_version)
    src_dir = dag.host().directory(func_cfg.src)

    async with dagger.connection(dagger.Config(log_output=sys.stderr)):
        await (
            dag.container()
            .from_(base_img)
            .with_directory(".", src_dir)
            .with_workdir(".")
            .with_exec(["pip", "install", "."], skip_entrypoint=True)
            .with_registry_auth(
                address=ecr_creds.uri,
                username=ecr_creds.username,
                secret=ecr_creds.secret,
            )
            .with_default_args(["app.lambda_handler"])
            .publish(address=publish_uri)
        )


async def function_build_dockerfile(
    func_cfg: FunctionConfig,
    ecr_creds: ECRCreds,
) -> None:
    publish_uri = f"{ecr_creds.uri}/{func_cfg.name}:{func_cfg.tag}"
    src_dir = dag.host().directory(func_cfg.src)
    build_args = [
        BuildArg(name="LANGUAGE_VERSION", value=func_cfg.python_version)
    ]

    async with dagger.connection(dagger.Config(log_output=sys.stderr)):
        await (
            dag.container()
            .build(
                context=src_dir,
                build_args=build_args,
            )
            .with_registry_auth(
                address=ecr_creds.uri,
                username=ecr_creds.username,
                secret=ecr_creds.secret,
            )
            .publish(address=publish_uri)
        )


async def main() -> None:
    parser = arg_parser()
    args = parser.parse_args()
    
    func_cfg = FunctionConfig(
        python_version = args.python_version,
        src = args.src,
        name = args.name,
        tag = args.tag,
    )

    ecr_client = ECRClient()
    ecr_creds = ecr_client.get_creds()

    if contains_dockerfile(func_cfg.src):
        await function_build_dockerfile(func_cfg, ecr_creds)
    else:
        await function_build(func_cfg, ecr_creds)


def handler():
    anyio.run(main)
