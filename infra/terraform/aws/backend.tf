# Uncomment and configure for remote state
# terraform {
#   backend "s3" {
#     bucket         = "dataquality-platform-tfstate"
#     key            = "aws/terraform.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "terraform-locks"
#     encrypt        = true
#   }
# }
