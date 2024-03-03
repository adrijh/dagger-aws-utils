terraform {
  backend "s3" {
    bucket  = "adrianjh-terraform-backend"
    key     = "dagger-demo.tfstate"
    region  = "eu-west-1"
    profile = "terraform"
  }
}
