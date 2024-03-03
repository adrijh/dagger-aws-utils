import base64
from dataclasses import dataclass

import boto3
import dagger
from dagger import dag

from dagger_module.common import config as cfg

@dataclass
class ECRCreds:
    uri: str
    username: str
    secret: dagger.Secret


class ECRClient:
    def __init__(self) -> None:
        self.session = self.__get_boto_session()
        self.ecr = self.__get_ecr_client()

    def __get_boto_session(self) -> boto3.Session:
        if cfg.AWS_PROFILE:
            return boto3.Session(
                profile_name=cfg.AWS_PROFILE,
                region_name=cfg.AWS_DEFAULT_REGION,
            )
        else:
            return boto3.Session(
                region_name=cfg.AWS_DEFAULT_REGION,
            )
        
    def __get_ecr_client(self):
        return self.session.client("ecr")

    def __get_auth_creds(self):
        resp = self.ecr.get_authorization_token()
        encoded_secret = resp["authorizationData"][0]["authorizationToken"]
        decoded = base64.b64decode(encoded_secret).decode("utf-8")
        return decoded.split(":")

    def get_creds(self):
        user, token = self.__get_auth_creds()
        return ECRCreds(
            uri=cfg.ECR_REGISTRY_URI,
            username=user,
            secret=dag.set_secret(
                "ECRToken",
                token,
            )
        )
