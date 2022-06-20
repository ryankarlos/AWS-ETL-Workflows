## Creating the different DataPipelines

We will create different data pipelines for automating the movement and transformation of data between 
different AWS services.  In each pipeline, you define pipeline objects, such as activities, schedules, 
data nodes, and resources.

https://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/what-is-datapipeline.html

DataPipeline contains three main components 

* Pipeline json definition file for specifying the objects https://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/dp-writing-pipeline-definition.html
* Pipeline for scheduling the tasks and creating EC2 instances/EMR for running the tasks
* Task Runner automatically installed on resources created which polls and performs the tasks

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

Or using cloudformation template `cloudformation/datapipeline/s3-to-rds-postgres.yaml`  to create a `The AWS::DataPipeline::Pipeline resource` 
with all the parameter and pipeline objects, such as activities, schedules, data nodes, and resources.
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html

```
aws cloudformation create-stack --stack-name DataPipelineS3toRDS \
--template-body file://cloudformation/datapipeline/s3-to-rds-postgres.yaml \
--parameters ParameterKey=Endpoint,ParameterValue=<endpoint> \
ParameterKey=myRDSUsername,ParameterValue=<username> \
ParameterKey=myRDSPassword,ParameterValue=<password>

```

Once the stack is created successfully, the pipeline is automatically activated.

<img src=https://github.com/ryankarlos/aws_etl/blob/master/screenshots/cf-stack-data-pipeline-s3-rds.png></img>

Navigating to the console, we should be able to monitor the status of the data pipeline task executions and diagnose 
failed executions from the logs in S3 in the location configured in pipeline definition `s3://data-pipeline-logs1/logs/<pipeline-id>/`

<img src=https://github.com/ryankarlos/aws_etl/blob/master/screenshots/data-pipeline-s3-rds-pg.png></img>


#### s3 to s3

Run the cloudformation template stored in `cloudformation/datapipeline/s3-to-s3.yaml` 
to create stack using the cli command 

```
$ aws cloudformation create-stack --stack-name DataPipelineS3toS3 \
--template-body file://cloudformation/datapipeline/s3-to-s3.yaml \
--parameters ParameterKey=InputPath,ParameterValue=s3://s3-eventbridge-batch/sample-data.txt \
ParameterKey=OutputPath,ParameterValue=s3://<bucket-name>

```

Navigate to the datapipeline console and click ion datapipeline id associated with the name used .e.g DataPipelineS3toS3

The pipeline should be activated and you can track the progress of the cli task 

<img src=https://github.com/ryankarlos/aws_etl/blob/master/screenshots/data-pipeline-s3-s3.png></img>

#### s3 to Redshift

Refer to the `data-pipelines/s3_to_redshift/README.md`