# Anime Dataset — Data Ingestion and Quality Assessment

## 1. Overview

This document describes how anime data was collected from the Kitsu API, imported into the Django application, and assessed for data quality before implementing the recommendation engine.

The assessment focuses on:

- Documenting the data source and ingestion process.
- Measuring the completeness of selected anime attributes.
- Investigating selected missing values by comparing database records with the stored source data.
- Determining how incomplete records should be handled by the Version 1 recommendation engine.

This is an initial data quality assessment, not a comprehensive audit of the dataset.

## 2. Data Source and Ingestion

### 2.1 Data Source

The anime dataset was collected from the [Kitsu API](https://hummingbird-me.github.io/api-docs/).

Kitsu provides anime information through a JSON:API interface.

The anime endpoint used was:

```text
https://kitsu.io/api/edge/anime
```

The API provides information such as:

- Anime titles and alternative titles.
- Synopsis descriptions.
- Average ratings.
- Genres and categories.
- Poster and cover image URLs.
- Release dates.
- Episode counts and release status.
- Relationships to associated characters and other resources.

Kitsu serves as the data source for the initial anime catalogue. Recommendation logic is implemented separately within the Django application.

### 2.2 Data Import Process

A custom Django management command was implemented to retrieve anime records from the Kitsu API and persist them in the application's database.

The importer:

1. Sends requests to the Kitsu anime endpoint.
2. Retrieves paginated responses using the pagination links provided by the API.
3. Processes anime attributes and relevant relationships.
4. Extracts the required information for the Django `Anime` model.
5. Uses Django's ORM to create or update records.

The Kitsu anime ID is stored as `external_id` and used as the external identifier for each record.

The import uses `update_or_create` to update existing records or create new ones, allowing the importer to be run again without creating duplicate records for the same external ID.

The original anime resource is retained in the `raw_data` JSON field for reference and comparison during debugging and data validation.

**Implementation location:** The custom import command is located under the `training` application's `management/commands/import_kimetsu_anime` directory.

**Import command:** python manage.py import_kimetsu_anime

### 2.3 Data Persistence

The imported information is stored in the Django `Anime` model.

| Model field | Description |
|---|---|
| `external_id` | Kitsu anime ID |
| `title` | Primary anime title |
| `canonical_title` | Canonical anime title |
| `title_en` | English title |
| `title_en_jp` | English-Japanese title |
| `title_ja_jp` | Japanese title |
| `abbreviated_titles` | Alternative abbreviated titles |
| `localized_titles` | Localized title information |
| `synopsis` | Anime description |
| `average_rating` | Average rating |
| `genres` | Associated genres |
| `categories` | Associated categories |
| `poster_image_url` | Poster image URL |
| `cover_image_url` | Cover image URL |
| `start_date` | Release start date |
| `end_date` | Release end date |
| `episode_count` | Number of episodes |
| `status` | Anime release status |
| `raw_data` | Original anime resource data |

Character records were intentionally not imported during this stage to keep the initial ingestion process simpler and faster. Character enrichment is deferred to Version 2.

## 3. Dataset Summary

Following the initial import, the database contained:

| Metric | Count |
|---|---:|
| Total anime records | 22,534 |
| Total character records | 0 |

The zero character count is intentional and reflects the decision to defer character enrichment. It does not indicate an unexpected failure in the anime import.

The figures in this document represent the dataset at the time the assessment was performed.

## 4. Data Quality Assessment

### 4.1 Assessment Method

A basic data quality assessment was performed using the following activities:

1. **Data profiling:** Measuring the completeness of selected fields across the imported anime records.
2. **Source comparison:** Comparing selected database values with corresponding values in the original anime resource stored in `raw_data`.
3. **Impact assessment:** Determining how missing attributes affect the recommendation features planned for Version 1.
4. **Decision-making:** Defining how incomplete records should be handled by the recommendation engine.

The assessment primarily focused on completeness. Selected missing values were also investigated to determine whether they were absent from the stored source response or appeared to be missing during import.

### 4.2 Completeness Calculation

Completeness measures the proportion of records that contain an available value for a particular field.

The calculation used was:

```text
Completeness (%) =
(Records with available values / Total records) × 100
```

Missing data percentage was calculated as:

```text
Missing (%) =
(Missing records / Total records) × 100
```

For this assessment, null or empty values were treated as missing according to the field type.

A Django management command named `data_import_health_check` was implemented to automate these checks.

Run the command using:

```bash
python manage.py data_import_health_check
```

The command checks for missing:

- Titles.
- Synopses.
- Average ratings.
- Poster image URLs.
- Genres.
- Categories.

These checks measure field completeness. They do not establish whether populated values are accurate, valid, current, or useful for recommendations.

### 4.3 Validation Results

The initial validation produced the following results:

| Field | Missing Records | Missing Percentage | Available Records | Completeness |
|---|---:|---:|---:|---:|
| Title | 0 | 0.00% | 22,534 | 100.00% |
| Synopsis | 1,314 | 5.83% | 21,220 | 94.17% |
| Average rating | 10,583 | 46.96% | 11,951 | 53.04% |
| Poster image URL | 49 | 0.22% | 22,485 | 99.78% |
| Genres | 8,776 | 38.95% | 13,758 | 61.05% |
| Categories | 812 | 3.60% | 21,722 | 96.40% |

All percentages are calculated against the total of 22,534 anime records.

### 4.4 Observations and Recommendation Impact

The validation results highlight the following:

**Titles**

All imported records have titles. This provides a complete foundation for title-based search.

**Synopses**

Approximately 94.17% of records have synopsis descriptions. This provides sufficient initial coverage for implementing synopsis-based recommendations.

Records without synopses will not be eligible for synopsis-based similarity matching.

**Average ratings**

Almost 47% of records have no average rating. Ratings will therefore remain optional and will not be required for content-based recommendations.

**Genres**

Approximately 38.95% of records have no genre information. Genre-based matching will only use records with available genres.

**Categories**

Categories are available for most records. They can be evaluated as supplementary metadata during recommendation experiments.

**Poster images**

Only 49 records have missing poster image URLs. Images will be displayed when available, with missing images handled by the application.

## 5. Investigation of Missing Data

After identifying missing values, selected records were inspected to investigate whether the missing information was already absent from the stored Kitsu resource or appeared to have been lost during the import process.

The investigation compared values in the Django `Anime` model with their corresponding values in the original resource stored in `raw_data`.

| Field | Database value inspected | Source value inspected | Observation |
|---|---|---|---|
| Genres | `Anime.genres` | `raw_data["relationships"]["genres"]["data"]` | Inspected records had empty genre relationships in both locations. |
| Average rating | `Anime.average_rating` | `raw_data["attributes"]["averageRating"]` | Inspected records had `None` in both locations. |
| Synopsis | `Anime.synopsis` | `raw_data["attributes"]["synopsis"]` | Ten inspected records had empty synopsis values in the model and `None` in the stored source resource. |

### 5.1 Investigation Findings

The inspected samples did not reveal evidence of an importer extraction problem for the fields examined.

The missing values in these samples were also absent from their corresponding stored source resources. This suggests that the source response did not provide those values for the inspected records.

However, this investigation covered selected records rather than every record with missing data. It therefore does not establish that all missing values across the dataset originated from Kitsu.

No bulk re-import or data deletion was performed as a result of this investigation.

## 6. Version 1 Data Handling Decisions and Limitations

### 6.1 Data Handling Decisions

Based on the validation results, the following decisions were made for Version 1:

| Field | Handling strategy |
|---|---|
| Title | Use all records for title-based search. |
| Synopsis | Exclude records without a synopsis from synopsis-based similarity matching. |
| Genres | Use records with available genres for genre-based matching. |
| Average rating | Treat as optional; do not require ratings for recommendations. |
| Categories | Use when available as supplementary metadata. |
| Poster image URL | Display when available. |
| Characters | Defer character-based recommendations to Version 2. |

### 6.2 Why Incomplete Records Are Retained

Records with missing attributes will not be deleted simply because some fields are unavailable.

An anime without a synopsis may still be useful for title search or genre-based recommendations. Similarly, an anime without genres may still be useful for synopsis-based recommendations.

The recommendation process should only require the information relevant to the selected recommendation method.

This approach preserves the available catalogue data while allowing each recommendation feature to operate on records that meet its specific data requirements.

### 6.3 Current Limitations

The assessment identified the following limitations:

1. Some anime records do not have synopsis descriptions.
2. Genre information is unavailable for a significant portion of the dataset.
3. Average ratings are missing for almost half of the records.
4. Character information has not yet been imported or validated.
5. Duplicate records have not yet been independently assessed.
6. Field validity, URL accessibility, data freshness and broader source accuracy have not been comprehensively assessed.

These limitations will be considered during implementation and evaluation of the recommendation engine.

## 7. Next Step

The dataset is sufficiently populated to begin implementing the Version 1 conventional content-based recommendation baseline.

The initial implementation will focus on:

- TF-IDF for converting anime synopsis text into numerical representations.
- Cosine similarity for comparing anime descriptions.
- Ranking anime based on synopsis similarity.
- Genre and metadata matching where the required information is available.

The recommendation baseline will provide a benchmark for evaluating more advanced approaches, including semantic embeddings, Retrieval-Augmented Generation (RAG), context engineering and fine-tuning in later development stages.

---

**Document status:** Initial data ingestion and quality assessment completed.

**Dataset source:** Kitsu API.

**Dataset size at assessment:** 22,534 anime records.

**Project scope:** Version 1 — Conventional content-based recommendation system.