
This directory contains state machine definitions used to execute tasks for the following
use cases:

### AWS Glue ETL

This example uses the definition `definitions/glue_etl.json` to start the glue job (created from glue_etl/script.py), 
query athena table once the job is complete and finally send a message to SNS

<img width="1000" alt="flights_glue_job" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/kinesis_workflow.png">
