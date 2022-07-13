# AWS ETL pipelines

Examples of architecture using AWS ETL and DB services:

* [Data Pipelines (S3 to Redshift/RDS/S3)](data-pipelines)
* [S3 to DynamoDB](s3_to_dynamodb)
* [Glue and Athena/Redshift](glue_etl)
* [Kinesis (Streams and Firehose)](kinesis)
* [Step-functions](step_functions)
* [EventBridge](eventbridge-schedule-rds)

All source code can be found in this [repository](https://github.com/ryankarlos/AWS-ETL-Workflows)
and the scripts for the various examples are stored in the respective named folders.

## Dependencies

For running some of the scripts locally, first install [poetry](https://python-poetry.org/docs/)

```
pip install poetry
```
and then install the dependencies from the poetry.lock file [Ref](https://python-poetry.org/docs/basic-usage/#installing-with-poetrylock)

```
poetry install

Installing dependencies from lock file

```


The command below  will spawn a new shell with a virtual env containing the newly installed dependencies


```
$ poetry shell

Spawning shell within /Users/rk1103/Library/Caches/pypoetry/virtualenvs/aws-etl-fV9WWBi4-py3.9
(base) rk1103@Ryans-MacBook-Air aws_etl % . /Users/rk1103/Library/Caches/pypoetry/virtualenvs/aws-etl-fV9WWBi4-py3.9/bin/activate
(aws-etl-fV9WWBi4-py3.9) (base) rk1103@Ryans-MacBook-Air aws_etl %
```

Most of the resources are created via cloudformation templates. The process for doing this is 
described [here](cloudformation) 