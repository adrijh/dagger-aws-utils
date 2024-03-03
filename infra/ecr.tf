resource "aws_ecr_repository" "without_dockerfile" {
  name                 = "without-dockerfile"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_ecr_repository" "with_dockerfile" {
  name                 = "with-dockerfile"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}
