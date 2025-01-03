# Group Assignment API

## Description

This project provides an API to optimize grouping in seminars and study sessions. The groupings will allow participants to interact with as many different participants as possible through multiple rounds.

## Features
- Assign members to groups for multiple rounds of group work.
- Provide group assignments that maximize opportunities for interaction across rounds.
- Offer two assignment algorithms:
  - (Random assignment as a baseline)
  - Greedy assignment
  - Combinatorial optimization assignment
 
### Comninatorial Optimization

#### Variables

- $x_{i, j, k}$: Whether participant $i$ is assigned to room $j$ in round $k$ (0 or 1).
- $y_{i_{1}, i_{2}, j, k}$: Whether participants $i_{1}$ and $i_{2}$ are together in room $j$ in round $k$ (0 or 1).

#### Objective Function

Minimize the total number of times a given pair of participants is assigned to the same room across all rounds and rooms.

$$\text{Minimize } \sum_{k=1}^{T} \sum_{j=1}^{R} \sum_{i_1 < i_2} y_{i_{1}, i_{2}, j, k}$$

Let:

- $N$: Total number of participants
- $T$: Number of rounds (total number of groupings to be performed)
- $R$: Number of rooms

#### Constraint

1. Each participant is assigned to only one room in each round.

$$\sum_{j=1}^{R} x_{i, j, k} = 1 \quad \forall i, \forall k$$

2. The number of participants in each room is equal or nearly equal.

$$ \left\lfloor \frac{N}{R} \right\rfloor \leq \sum_{i=1}^{N} x_{i, j, k} \leq \left\lfloor \frac{N}{R} \right\rfloor + 1$$

3. $y_{i_{1}, i_{2}, j, k} = 1$ if and only if $x_{i_{1}, j, k} = 1$ and $x_{i_{2}, j, k} = 1$

$$
\begin{aligned}
    &y_{i_{1}, i_{2}, j, k} \leq x_{i_{1}, j, k} \\
    &y_{i_{1}, i_{2}, j, k} \leq x_{i_{2}, j, k} \\
    &y_{i_{1}, i_{2}, j, k} \geq x_{i_{1}, j, k} + x_{i_{2}, j, k}  - 1
\end{aligned}
$$

#### Note
To reduce the computation time, which becomes very long when optimizing all rounds together, the implementation adopts the following strategy to optimize each round separately:

- The initial round is assigned randomly.
- From the second round onward, optimization is performed for each round individually, using the assignment results from previous rounds.

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
