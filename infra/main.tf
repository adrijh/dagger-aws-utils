locals {
  prefix                     = "dagger-test"
  without_dockerfile_version = "0.0.1"
  with_dockerfile_version    = "0.0.1"
}

data "aws_region" "current" {}

data "aws_caller_identity" "current" {}

data "aws_vpc" "this" {
  tags = {
    Name = "*MainVPC*"
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.this.id]
  }

  tags = {
    Name = "*Private*"
  }
}

module "without_dockerfile" {
  source = "terraform-aws-modules/lambda/aws"

  function_name                           = "${local.prefix}-without-dockerfile"
  timeout                                 = 10
  reserved_concurrent_executions          = 1
  create_current_version_allowed_triggers = false

  create_package = false
  package_type   = "Image"
  image_uri      = "${aws_ecr_repository.without_dockerfile.repository_url}:${local.without_dockerfile_version}"

  vpc_subnet_ids        = data.aws_subnets.private.ids
  attach_network_policy = true
}


module "with_dockerfile" {
  source = "terraform-aws-modules/lambda/aws"

  function_name                           = "${local.prefix}-with-dockerfile"
  timeout                                 = 10
  reserved_concurrent_executions          = 1
  create_current_version_allowed_triggers = false

  create_package = false
  package_type   = "Image"
  image_uri      = "${aws_ecr_repository.with_dockerfile.repository_url}:${local.with_dockerfile_version}"

  vpc_subnet_ids        = data.aws_subnets.private.ids
  attach_network_policy = true
}
