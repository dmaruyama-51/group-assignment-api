# Room Assignment API

## Description

This project provides an API to optimize grouping in seminars and study sessions. The groupings will allow participants to interact with as many different participants as possible through multiple rounds.

## Features
- Assign members to groups for multiple rounds of group work.
- Provide group assignments that maximize opportunities for interaction across rounds.
- Offer two assignment algorithms:
  - Random assignment
  - Greedy assignment
  - Combinatorial optimization assignment

## Technical Stack
- Language: Python 3.11
- Framework: FastAPI
- Dependency Management: Poetry
- Containerization: Docker
- CI/CD: GitHub Actions
- Deployment: Google Cloud Run

## Development Environment
- Code Quality Management
    - Ruff: Linter/Formatter
    - Mypy: Type Checker
- Development Commands (Makefile)
    - make lint: Run linter
    - make format: Run formatter
    - make dev: Start development server

## API Usage

The API's Swagger documentation can be accessed at:

[API Documentation](https://room-assignment-api-1037219502389.asia-northeast1.run.app/docs)


## CI/CD
GitHub Actions are used for continuous integration and deployment:
- **PR Checks**: Runs tests, linting, and coverage checks on pull requests.
- **Deploy**: Deploys the latest changes to Artifact Regustrt and Cloud Run upon merging.

### Pre-requisites for Deployment

Before deploying via GitHub Actions, ensure the following environment variables and secrets are registered:

#### Environment Variables (GitHub Actions)
- `PROJECT_ID`: GCP Project ID.
- `REGION`: GCP Region.
- `REPOSITORY_NAME`: Artifact Registry repository name.
- `API_NAME`: Cloud Run service name.

#### Secrets (GitHub Actions)
- `WORKLOAD_IDENTITY_PROVIDER`: Value for the Workload Identity Provider.
- `SERVICE_ACCOUNT`: Email address of the service account.
