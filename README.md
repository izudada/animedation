## Overview

As an anime enthusiast, I enjoy discovering anime with compelling storylines, engaging protagonists, and intriguing plots. Whenever I finish an anime I love, I often find myself looking for something that offers a similar experience.

This leads to questions such as:

- What anime has a storyline similar to the one I just watched?
- Which anime features a protagonist with similar characteristics, abilities, or personality?
- What anime explores similar themes, conflicts, or plot developments?

These questions inspired this project: an **AI-powered anime recommendation system** that takes an anime title or user input and recommends other anime based on the aspects the user wants to explore.

The system focuses on three primary recommendation categories:

- **Plot Similarity:** Recommends anime with similar storylines, conflicts, or plot developments.
- **Main Character Similarity:** Recommends anime featuring protagonists with similar personalities, abilities, backgrounds, or character arcs.
- **Synopsis and Description Similarity:** Recommends anime with similar premises, themes, settings, or overall concepts.

The goal is to help anime fans discover their next favourite series based on what they enjoyed most about the anime they have already watched, rather than relying solely on popularity or genre classifications.

Ultimately, this project will explore how embeddings, Retrieval-Augmented Generation (RAG), context engineering, and fine-tuning a large language model (LLM) can make anime recommendations more relevant, contextual, and aligned with a user's specific interests.

## Project Status

The project is being developed incrementally, starting with a conventional recommendation approach before introducing more advanced AI techniques.

| Component | Status |
|---|---|
| Kitsu API integration | Completed |
| Anime data import | Completed |
| PostgreSQL database integration | Completed |
| Data quality assessment | Completed |
| TF-IDF recommendation baseline | Implemented |
| Cosine similarity ranking | Implemented |
| Recommendation engine testing | Implemented |
| Swagger/OpenAPI documentation | In progress / To be updated |
| Telegram error notifications | In progress |
| Celery background processing | In progress |
| Semantic embeddings | Planned |
| Vector search with pgvector | Planned |
| LLM integration | Planned |
| Retrieval-Augmented Generation (RAG) | Planned |
| LoRA fine-tuning | Planned |
| Recommendation evaluation | Planned |

## Technology Stack

The project uses the following technologies and tools:

- **Python:** Primary programming language.
- **Django:** Backend web framework.
- **Django REST Framework:** REST API development.
- **PostgreSQL:** Relational database for storing anime records.
- **Kitsu REST API:** External anime data source.
- **Scikit-learn:** TF-IDF and similarity calculations.
- **Docker and Docker Compose:** Application containerization and local development.
- **Redis:** Message broker for background processing.
- **Celery:** Asynchronous task execution.
- **Swagger/OpenAPI:** API documentation.
- **Telegram Bot API:** Application error notifications.

## System Architecture

The application uses Django as its backend, PostgreSQL as its primary database, and the Kitsu REST API as its anime data source.

The recommendation engine retrieves anime information from the local database, processes available descriptions, and calculates similarity scores to identify relevant recommendations.

The architecture also incorporates Redis and Celery for background task processing, particularly for asynchronous notification delivery.

See [System Architecture](docs/architecture.md) for the architecture diagram and explanation of how the different components interact.

## Data Quality

The initial Kitsu API import contains 22,534 anime records.

A data quality assessment was performed to identify missing or incomplete fields, including synopses, genres, ratings, posters, and categories.

The assessment informed how incomplete records are handled by the recommendation engine.

See [Data Quality Assessment](docs/data-quality.md) for the validation results and implementation decisions.

## Recommendation Algorithm

The initial recommendation engine uses a **content-based filtering approach** to identify anime with similar descriptions.

The current implementation uses:

- **TF-IDF (Term Frequency-Inverse Document Frequency):** Converts anime synopsis text into numerical representations based on the importance of words within the dataset.
- **Cosine Similarity:** Measures the similarity between anime synopsis vectors.
- **Ranking:** Orders candidate anime based on their calculated similarity scores.

### Recommendation Workflow

1. Retrieve the selected anime from the database.
2. Extract and preprocess its synopsis.
3. Transform the synopsis into numerical vectors using TF-IDF.
4. Calculate similarity scores using cosine similarity.
5. Rank candidate anime based on their similarity scores.
6. Return the highest-ranked recommendations.

### Planned Improvements

The recommendation engine will progressively explore:

- Sentence Transformers and semantic embeddings.
- Vector similarity search using pgvector.
- Category-specific retrieval for plot, synopsis, and character similarity.
- LLM-assisted recommendation explanations.
- Retrieval-Augmented Generation (RAG).

See [Recommendation Engine](docs/recommendation-engine.md) for implementation details.

## API Documentation

The application exposes backend functionality through REST API endpoints using Django REST Framework.

API documentation is provided through OpenAPI/Swagger to make endpoints, request parameters, and response structures easier to explore.

See [API Documentation](docs/api-documentation.md) for available endpoints, request examples, and instructions for accessing the Swagger interface.

## Logging and Monitoring

The application incorporates logging and API request monitoring to help identify errors, investigate failed requests, and monitor API performance.

The logging and notification implementation includes:

- API request and response logging.
- Server-side error monitoring.
- Detection of slow API requests.
- Telegram notifications for critical errors and slow requests.
- Asynchronous notification delivery using Celery.
- Redis as the message broker for background tasks.

See [Logging and Monitoring](docs/logging-and-monitoring.md) for implementation details.

## Testing

Testing is an important part of the development process to ensure that the recommendation engine and supporting application components behave as expected.

Testing covers:

- Recommendation algorithm functionality.
- Similarity calculations and ranking.
- Anime data import operations.
- API endpoint behaviour.
- Background task execution.
- Error handling and invalid inputs.

See [Testing Guide](docs/testing.md) for test coverage and instructions on running the test suite.

## Installation and Setup

### Prerequisites

- Python 3.10+
- Docker
- Docker Compose
- Git

### Clone the Repository

```bash
git clone https://github.com/izudada/animedation.git
cd  animedation
```

### Environment Configuration

Create a `.env` file using the provided example:

```bash
cp .env.example .env
```

Configure the required environment variables before starting the application.

### Start the Application

```bash
make up
```

### Run Database Migrations

```bash
make migrate
```

### Run Tests

```bash
docker compose exec web python manage.py test
```

## Development Roadmap

The project follows an incremental development approach, with each stage introducing and evaluating a new technique.

| Stage | Focus | Objective |
|---|---|---|
| 1 | Anime Data Foundation | Build a reliable anime catalogue |
| 2 | Recommendation Baseline | Implement TF-IDF and cosine similarity |
| 3 | Semantic Embeddings | Introduce semantic retrieval |
| 4 | Context Engineering | Control and structure LLM inputs |
| 5 | Retrieval-Augmented Generation | Ground recommendations in catalogue data |
| 6 | LoRA Fine-tuning | Experiment with model adaptation |
| 7 | Evaluation | Compare recommendation quality |
| 8 | Integration and Deployment | Optimise and deploy the application |

See [Development Roadmap](docs/development-roadmap.md) for the detailed implementation plan.

## Important Resources

**Kitsu JSON:API Documentation (edge)**

[Kitsu API](https://hummingbird-me.github.io/api-docs/)

**Scikit-learn Documentation**

[Scikit-learn](https://scikit-learn.org/)

**Sentence Transformers**

[Sentence Transformers](https://www.sbert.net/)

**Hugging Face Learn**

[Hugging Face](https://huggingface.co/learn/)

**Hugging Face PEFT**

[PEFT Documentation](https://huggingface.co/docs/peft/index)

**TRL Documentation**

[TRL](https://huggingface.co/docs/trl/index)

**pgvector**

[pgvector](https://github.com/pgvector/pgvector)
