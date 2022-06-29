## Creating the different DataPipelines

We will create different data pipelines for automating the movement and transformation of data between 
different AWS services.  In each pipeline, you define pipeline objects, such as activities, schedules, 
data nodes, and resources.

https://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/what-is-datapipeline.html

DataPipeline contains three main components 

* Pipeline json definition file for specifying the objects https://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/dp-writing-pipeline-definition.html
* Pipeline for scheduling the tasks and creating EC2 instances/EMR for running the tasks
* Task Runner automatically installed on resources created which polls and performs the tasks

In all these examples, the data pipeline scheduling has been set to `ondemand`and requires manual triggering.
However, we could also schedule a cron job to run from specific start to end at desired frequency as shown in 
the examples here https://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/dp-object-schedule.html

### s3 to RDS

Before running this data pipeline, we need to create an S3 bucket and copy the following objects into it 

* datasets/sample-data.csv 
* bash script - data-pipelines/s3_to_rds/psql-copy-s3-rds.sh

The bash script runs the copy command for copying the csv data into rds postgres database via psql. It runs this 
in an EC2 resource (which is configured via data pipeline configuration) and installs the neccessary packages/libraires 
such as postgresql13 for using the psql. The bash script takes in keyword args 
for the jdbc string, username, password and table name as shown in the command below. These are configured via the 
script arguments setting in the shell command activity in datapipeline task configuration.
A special thanks to this https://github.com/awslabs/aws-support-tools/blob/master/DataPipeline/MySqlRdsToPostgreSqlRds/dbconv-mysqlRDS-to-postgresqlRDS.sh
for helping me generate a working version of this script for my use case !

```
$ cd data-pipelines/s3_to_rds
$ sh psql-copy-s3-rds.sh --red_jdbc=<jdbcstring> --red_usr=<Username> --red_pwd=<Password> --red_tbl=<TableName>
```

The bash script  `data-pipelines/s3_to_rds/create-pipeline.sh`  will create the pipeline with the configuration and activate it
After `cd` into root of the repo, run the command below. The first arg is the name of the pipeline to be created and 
the second arg is the relative path to the defintion json. The placeholder values for the jdbcconnstring, username and password in the 
json definition would need to be replaced before running the script. Alternatively, these could be modifed in the console 
once the pipeline is created and then activated.

```
$ sh data-pipeline/create_pipeline.sh S3-RDS-datapipeline s3_to_rds/postgres-definition.json

Creating data pipeline S3-RDS-datapipeline and activating ...

Adding config settings from json definition for pipeline id df-04865961XZQ7LL0G3TRX
{
    "validationErrors": [],
    "validationWarnings": [],
    "errored": false
}

Activating pipeline df-04865961XZQ7LL0G3TRX
```

Alternatively we can use the cloudformation template `cloudformation/datapipeline/s3-to-rds-postgres.yaml`  to create a 
`The AWS::DataPipeline::Pipeline resource`with all the parameter and pipeline objects, such as activities, schedules, 
data nodes, and resources.https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-datapipeline-pipeline.html
The jdbcstring should be in the format `jdbc:postgresql://<endpoint>.rds.amazonaws.com:<port>/<dbname>`
Replace the `<username>` and `<password>` with the username and password for the RDS db created.

```
aws cloudformation create-stack --stack-name DataPipelineS3toRDS \
--template-body file://cloudformation/datapipeline/s3-to-rds-postgres.yaml \
--parameters ParameterKey=myRDSjdbcstring,ParameterValue=<myRDSjdbcstrin> \
ParameterKey=myRDSUsername,ParameterValue=<username> \ 
ParameterKey=myRDSPassword,ParameterValue=<password>

```
Once the stack is created successfully, the pipeline is automatically activated.

<img src=https://github.com/ryankarlos/aws_etl/blob/master/screenshots/DataPipeline_s3tords_Cftemplate.png></img>

We can check the design of the pipeline and the task dependencies if we click on the pipeline id in the console and select
edit pipeline. We can see that in this configuration, we have a `RDSPOstgresTableCreateActivity` (Sql Activity https://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/dp-object-sqlactivity.html) and 
`CopyS3DatatoEC2` (ShellCommand Activity https://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/dp-object-shellcommandactivity.html) which run on an EC2 resource (t1.micro. Amazon Linux AMI) 
https://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/dp-object-ec2resource.html. The TableCreateActivity
requires a database reference (RDSPostgres JDBC Database type https://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/dp-object-jdbcdatabase.html) 
which contains the parameters such as connection string, DB username, password, table name etc required to connect to the database and run the sql query for creating the `persons`
table with the required schema. Note that this only creates a table if it does not already exist. So in subsequent commands
it will not do so unless the table is manually deleted. The bash script which runs in the subsequent task to truncate 
data in any existing table from previous data pipeline runs so the table will only have the latest copy of 
data from the csv file in S3.
The `CopyS3DatatoEC2` script installs aws-cli and runs the aws s3 cp command via the cli 
to copy the csv file from the S3 bucket into path in EC2 resource so it can be later copied into RDS postgres in a subsequent 
task. This is done - as I am not sure RDS postgres supports copying data directly from S3 to db so needs to be staged into
EC2 location first and then copy command run afterwards.
The final activity is the `CopyDatatoRDS` (ShellCommandActivity) which has parameters for `ScriptURi` and `ScriptArguments` 
configured to run the script `psql-copy-s3-rds.sh` copied to S3 previously with the required arguments. 
This installs the necessary dependencies and first truncates the table (in case there is existing data in it) and then 
runs the copy command to copy data from csv file which was copied to the folder in EC2 resource into RDS Postgres.

<img src=https://github.com/ryankarlos/aws_etl/blob/master/screenshots/datapipeline-s3-rds.png></img>

Navigating to the console, we should be able to monitor the status of the data pipeline task executions 

<img src=https://github.com/ryankarlos/aws_etl/blob/master/screenshots/s3-rds-component-status.png></img>

We can also diagnose  failed executions from the logs in S3 in the location configured in pipeline definition `s3://data-pipeline-logs1/logs/<pipeline-id>/`
A sample of these logs is stored in data-pipelines/s3-to-rds/results_logs. These include the taskrunner in the ec2 resource and 
activity/stdout logs for the other activities (shell command and sql table create task activity)

One the pipeline has run successfully, we can  check the data in Postgres RDS we can use PgAdmin and connect to the RDS server

* Create new server 
* In the General tab, choose a  server name e.g. RDSPostgres
* In the connection tab fill out the following details (which can be found in the configuration in the AWS RDS console)
- Endpoint/Host 
- Port 
- Username
- Password
* Click save and you should see the new server created in the browser window on the left
* Go to Tools -> Query tool. This should open up the query tool window. 
* Run the command as in the screenshot below and you should see the data in the table if the data pipeline has run successfully

<img src=https://github.com/ryankarlos/aws_etl/blob/master/screenshots/RDSPostgresDataQuery.png></img>

Once complete, delete all the resources to avoid unnecessary billing charges. Deleting the cloudformation stack for RDS 
will terminate the RDS instance. 

### s3 to s3

<img src=https://github.com/ryankarlos/aws_etl/blob/master/screenshots/dp-s3-to-s3-tasks.png></img>

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
Compared to the previous example, this is a lot more simplistic and just runs a shellcommand activity on the EC2 resource

### s3 to Redshift

Refer to the `data-pipelines/s3_to_redshift/README.md`
