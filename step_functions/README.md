# Step Functions for ETL tasks

This directory contains state machine definitions used to execute tasks for the following
use cases:

### AWS Glue ETL

This example uses the definition `definitions/glue_etl.json` to start the glue job (created from glue_etl/script.py), 
wait for job to complete, then query athena table and finally publish number of rows to SNS

<img width="1000" alt="glue_step_function" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/stepfunction_glue_etl.png">
