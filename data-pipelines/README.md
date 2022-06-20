## Creating the different DataPipelines


#### s3 to RDS
The bash script  `data-pipelines/s3_to_rds/create-pipeline.sh`  will create the pipeline with the configuration and activate it
After `cd` into datapipeline directory, run the command below. The first arg is the name of the pipeline to be created and 
the second arg is the relative path to the defintion json.
```
$ sh aws_vpc/data-pipeline/create_pipeline.sh S3-RDS-datapipeline s3_to_rds/postgres-definition.json

Creating data pipeline S3-RDS-datapipeline and activating ...

Adding config settings from json definition for pipeline id df-0092274JVOD89B1BTDB
{
    "validationErrors": [],
    "validationWarnings": [],
    "errored": false
}

Activating pipeline df-0092274JVOD89B1BTDB
```

#### s3 to s3

Run the cloudformation template stored in `cloudformation/datapipeline/s3-to-s3.yaml` 
to create stack using the cli command 

```
$ aws cloudformation create-stack --stack-name DataPipelineS3toS3 \
--template-body file://cloudformation/datapipeline/s3-to-s3.yaml \
--parameters ParameterKey=InputPath,ParameterValue=s3://s3-eventbridge-batch/sample-data.txt \
ParameterKey=OutputPath,ParameterValue=s3://elasticbeanstalk-us-east-1-376337229415

{
    "StackId": "arn:aws:cloudformation:us-east-1:376337229415:stack/myteststack/fba95660-f033-11ec-84b3-0a195593347d"
}


```

#### s3 to Redshift

Refer to the `data-pipelines/s3_to_redshift/README.md`