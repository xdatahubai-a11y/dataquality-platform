.PHONY: setup test-data seed run-checks test deploy-aws deploy-azure local clean

setup: ## Local setup with Docker
	@bash scripts/setup_local.sh

test-data: ## Generate test datasets
	@python3 scripts/generate_test_data.py

seed: ## Seed database with rules
	@python3 scripts/seed_database.py

run-checks: ## Run DQ checks on test data
	@python3 scripts/run_test_suite.py

test: ## Run pytest
	@python3 -m pytest tests/ -v

deploy-aws: ## Deploy to AWS with Terraform
	cd infra/terraform/aws && terraform init && terraform apply

deploy-azure: ## Deploy to Azure with Terraform
	cd infra/terraform/azure && terraform init && terraform apply

local: test-data seed run-checks ## Full local run (data + seed + checks)

clean: ## Remove generated test data
	rm -rf test_data/

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
