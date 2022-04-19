# AWS ETL pipelines

Examples of architecture using AWS ETL and DB services:

* Data Pipeline (S3 to Redshift): data-pipelines/s3_to_redshift/README.md
* Lambda (S3 to DynamoDB) : data-pipelines/s3_dynamodb/README.md
* Glue and Athena: glue_etl/README.md
* Kinesis (Streams and Firehose) and ElasticSearch: kinesis/README.md
* Step-functions: step_functions/README.md

## Dependencies

For running some of the scripts locally, first install poetry https://python-poetry.org/docs/

```
pip install poetry
```
and then install the dependencies from the poetry.lock file in the repo  
https://python-poetry.org/docs/basic-usage/#installing-with-poetrylock

```
poetry install

Installing dependencies from lock file

```


The command below  will spawn a new shell with a virtual env containing the newly installed dependencies
https://python-poetry.org/docs/basic-usage/#activating-the-virtual-environment

```
$ poetry shell

Spawning shell within /Users/rk1103/Library/Caches/pypoetry/virtualenvs/aws-etl-fV9WWBi4-py3.9
(base) rk1103@Ryans-MacBook-Air aws_etl % . /Users/rk1103/Library/Caches/pypoetry/virtualenvs/aws-etl-fV9WWBi4-py3.9/bin/activate
(aws-etl-fV9WWBi4-py3.9) (base) rk1103@Ryans-MacBook-Air aws_etl %
```