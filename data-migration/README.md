## Scheduling starting and stopping RDS instances

<img src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/stop-start-db-instance-workflow.png">

This implements an automated solution for stopping/starting a RDS Postgres DB instance in a single AZ, on schedule using the 
combination of Amazon EventBridge and AWS Lambda. This could also be extended to multiple instances but beyond the 
scope of this example. We will assume the db instance needs to be made available from 1-5pm 
from 25-31 May 2022.
Furthermore, this example could also be modified to tackle this issue of rds restarting automatically 7 days
after it was last stopped (for maintenance jobs)
https://aws.amazon.com/premiumsupport/knowledge-center/rds-stop-seven-days/#:~:text=If%20you%20don't%20manually,system%2C%20or%20database%20engine%20version.

### Creating lambda function

* Create the Lambda function that will start or stop the RDS instances. If using the console,
  select Python3.9 as the runtime. Under Execution role, select Create a new role. This 
  will create a basic role with logging permissions to cloudwatch. This will be need to be adapted in the next step
  to also allow access to rds. Finally, click Create function.

* Navigate to the role created in the previous step and edit the permissions policy
  attached to the role so it looks like `rds_on_off-role-permissions.json`
  
* Replace the hello world sample code in the lambda function, with lambda_packages/rds_on_off/lambda_function.py. This uses the 
  describe_db_instance API to find the current state of the instance in the region. It’s also important to note that the stop_db_instance API is incapable of turning o

### Creating Eventbridge scheduled rules

* On the Amazon EventBridge console, click Create rule. Under Rule detail, enter ScheduleResourceOn as the rule name, 
  leave Event bus as default and select the Schedule rule type. Click Next.

* Write the desired CRON expression. For example, below we want to trigger the Lambda function every 1 PM BST (UTC+1) from 
   25-31 May 2022, we set it to  "00 17 25-31 5 ? 2022". In eventbridge the cron job is in UTC, so needs to be set at 
  12 PM. Click Next.

<img src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/eventbridge_schedule_cron.png">

* Specify the 'rds_on_off' Lambda function as a target. We will also configure target input - in additional 
  settings > configure target input, select Constant (JSON text) from drop-down and insert 
  the json below in the box. In the Click Next > Next > Create Rule
  
```
{
  "rds_required_state": "stopped",
  "rds_instance_id": "database-1"
}
```

* Optionally, we may want to send unprocessed events for failed target invocatiosn to SQS. 
  We need to create a Dead-letter queue in SQS first  as explained in the video 
  https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-rule-dlq.html 
  Once thats done, select existing SQS to be used as dead letter queue - and select the one created from dropdown. 
  Then Click Next > Next > Create Rule 


* Create the second event rule ScheduleResourceOff that will trigger the rds_on_off function. Repeat steps above as a guide. 
  However, this time,replace the CRON expression with "00 17 25-31 5 ? 2022" to stop the RDS instance at 5 PM UTC (6 PM BST) every day from  
  25-31 May 2022.
  
#### Monitoring

In case the scheduled event, has failed to start or stop the instance, we can investigate 
the cloudwatch logs. 

* Navigate to the logstreams for the lambda function. 

<img src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/rds_on_off_logstream.png">

* investigate the logstream corresponding to the event time 

<img src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/rds_lambda_logs_off_event.png">

* we can also check the SQS dead queue (if event bridge was configured to send any unprocessed events) in cases
  where the lamdba function was not invoked. EventBridge publishes an event to Amazon CloudWatch metrics 
  indicating that a target invocation failed.  Additional metrics are sent to CloudWatch including InvocationsSentToDLQ
  if DLQ is set. https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-rule-dlq.html

### References
https://tutorialsdojo.com/automatically-stop-non-production-rds-databases-with-aws-lambda-and-amazon-eventbridge/
https://aws.amazon.com/blogs/database/schedule-amazon-rds-stop-and-start-using-aws-lambda/
