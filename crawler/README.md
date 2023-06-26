# Tübingen Search Engine

## Description

The project is a web crawler designed to fetch and analyze english web pages about Tübingen. It employs a
breadth-first search (BFS) approach to crawl web pages, fetching a single URL from each domain at a time to balance load
and maximize parallelization.

## Installation

1. Clone the repository:

```bash
git clone git@github.com:longpollehn/mse-project.git
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Install MySQL and configure MySQL.

4. Configure `.env` file to match your local development.

6. Install pre-commit hooks:

```bash
pre-commit install
```

## Usage

Note: Before running the script, make sure to configure the database settings in the .env file.
Refer to the `.env.example` file for the required configuration variables.

To use the web crawler, follow the workflow below:

1. (Optional) If you want new SERP, delete the `data/serp.json` file, fetch a new search engine results page (SERP) using
   the `fetch_serp.py` script.

```bash
python3 -m mse.fetch_serp
```

2. Run the `initialize_database.py` script. This script sets up the database
   and creates the necessary tables for storing crawled documents and job management.

```bash
python3 -m mse.initialize_database
```

3. Once you have the initialized database, you can start the crawling process using the `craw.py` script.

```bash
python3 -m mse.crawl
```

4. After crawling, you can build the inverted index using the `build_inverted_index.py` script. This script analyzes
   the crawled documents and constructs an inverted index to enable efficient searching.

```bash
python3 -m mse.build_inverted_index
```

5. Build the ranker using the `build_ranker.py` script.
   This script builds the models needed to rank websites. After training, the model
   will be stored in paths defined in the `.env` file.

```bash
python3 -m mse.build_ranker
```

6. Finally, you can run the Flask application to search for documents using the `app.py` script.

```bash
python3 app.py
```

Open the browser and navigate to `http://localhost:5000` to access the search engine.

The crawler will fetch web pages based on the URLs present in the database, classify their relevance,
and store the documents in the database. The `build_inverted_index.py` script will process the crawled documents
and create an inverted index for faster searching.

Remember to review and configure the `.env` file with the appropriate database settings before running the scripts.

## Project Structure

The project has the following structure:
- `.github`: This directory contains the GitHub workflow files for the project.
- `data`: This directory contains the data files for the project.
    - `serp.json`: This file contains the search engine results page (SERP) for the query "Tübingen".
- `mse`: This directory contains the main source code of the web crawler.
    - `build_inverted_index.py`: The script for building the inverted index from the crawled documents.
    - `build_ranker.py`: The script for building the ranker from the inverted index and query.
    - `fetch_serp.py`: The script for fetching the search engine results page (SERP) and saving it as a JSON file.
    - `initialize_database.py`: The script for initializing the database and creating the necessary tables.
    - `crawl.py`: The script for the web crawling process, which fetches web pages, classifies their relevance, and
      stores them in the database.
    - `models.py`: This module defines the database models used for storing crawled documents and job management.
    - `rank.py`: This module contains the ranker class, which uses the built ranker to rank the documents based on the
      query.
    - `utils.py`: This module contains utility functions used in the crawling process.
    - Other modules and utility files related to crawling and database management.
- `static`: This directory contains the static files for the Flask application.
- `tests`: This directory contains the test files for the project. (Note: The test directory could be improved further
  to include more comprehensive testing scenarios and coverage.)
- `.pre-commit-config.yaml`: This file contains the configuration for the pre-commit hooks.
- `.pylintrc`: This file contains the configuration for the pylint linter.
- `app.py`: This file contains the Flask application for the search engine.
- `example.env`: This file contains the example environment variables for the project.
- `requirements.txt`: This file contains the required dependencies for the project.

## Database Schema

The database schema for the web crawler includes the following table:

### Table `job`

The `job` table stores the jobs in the crawling queue and their relevant information.

| Column       | Data Type | Description                                                                       |
|--------------|-----------|-----------------------------------------------------------------------------------|
| id           | Integer   | Unique identifier for the job                                                     |
| bfs_layer    | Integer   | The layer in which the job was fetched into                                       |
| url          | String    | The URL associated with the job                                                   |
| server       | String    | The domain name without any subdomain or suffix                                   |
| domain       | String    | The domain name with the top-level domain (TLD)                                   |
| done         | Boolean   | Indicates whether the job has been crawled or not                                 |
| success      | Boolean   | Indicates whether the job's crawling was success. If none, then job was not done. |
| created_date | DateTime  | The timestamp indicating when the job was created                                 |

### Table `document`

The `document` table stores information about the crawled web documents.

| Column              | Data Type  | Description                                                      |
|---------------------|------------|------------------------------------------------------------------|
| id                  | Integer    | Unique identifier for the document                               |
| bfs_layer           | Integer    | The BFS layer in which the document was fetched into             |
| url                 | Text       | The URL of the crawled web document                              |
| server              | Text       | The domain name without subdomains or suffixes from the URL      |
| domain              | Text       | The domain name with the top-level domain (TLD) from the URL     |
| title               | Text       | The extracted title from the HTML                                |
| text                | Text       | The extracted text content from the HTML                         |
| tokens              | Text       | JSON representation of the preprocessed and tokenized text       |
| all_harvested_links | Text       | JSON representation of all the harvested links from the document |
| non_relevant_links  | Text       | JSON representation of the non-relevant links from the document  |
| relevant_links      | Text       | JSON representation of the relevant links from the document      |
| relevant            | Boolean    | Indicates whether the document is relevant or not                |
| job                 | ForeignKey | The associated job that the document belongs to                  |
| created_date        | DateTime   | The timestamp indicating when the document was created           |
