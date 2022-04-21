# Step Functions for ETL tasks

This directory contains state machine definitions used to execute tasks for the following
use cases:

### AWS Glue ETL

This example uses the definition `definitions/glue_etl.json` to start the glue job (created from glue_etl/script.py), 
wait for job to complete, then query athena table and finally publish number of rows to SNS

<img width="1000" alt="glue_step_function" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/stepfunction_glue_etl.png">


An example definition json is in step_functions/definitions/glue_etl.json. Create state machine
based on this definition by running commmand in 
https://docs.aws.amazon.com/cli/latest/reference/stepfunctions/create-state-machine.html
and supplying definition value as json


To execute statemachine, execute following command and pass arn for state machine created.
To get arn - you can use the `aws stepfunctions list-state-machines` command

```
$ aws stepfunctions start-execution --state-machine-arn <arn>
{
    "executionArn": "arn:aws:states:us-east-1:376337229415:execution:ETLDemo:905b2d8e-e659-4e18-ba1f-714882100324",
    "startDate": "2022-04-21T02:37:21.064000+01:00"
}
```

We can check status of the execution


```
$ aws stepfunctions describe-execution --execution-arn "arn:aws:states:us-east-1:376337229415:execution:ETLDemo:905b2d8e-e659-4e18-ba1f-714882100324"


{
    "executionArn": "<arn>",
    "stateMachineArn": "<arn>",
    "name": "905b2d8e-e659-4e18-ba1f-714882100324",
    "status": "FAILED",
    "startDate": "2022-04-21T02:37:21.064000+01:00",
    "stopDate": "2022-04-21T02:38:18.965000+01:00",
    "input": "{}",
    "inputDetails": {
        "included": true
    },
    "traceHeader": "Root=1-6260b551-db5653e799449c7169fc982b;Sampled=1"
}
```

If failed, we can retrieve execution history. Command below does this in reverse order and only
prints out two items (so we get the latest event that failed) and the cause for failure.

```

$ aws stepfunctions get-execution-history  --execution-arn <enter-arn> --no-include-execution-data --reverse-order --max-items 2
{
    "events": [
        {
            "timestamp": "2022-04-21T02:38:18.965000+01:00",
            "type": "ExecutionFailed",
            "id": 9,
            "previousEventId": 0,
            "executionFailedEventDetails": {
                "error": "States.Runtime",
                "cause": "An error occurred while executing the state 'Glue StartJobRun' (entered at the event id #8). The JSONPath '$.JobName' specified for the field 'JobName.$' could not be found in the input '{}'"
            }
        },
        {
            "timestamp": "2022-04-21T02:38:18.965000+01:00",
            "type": "TaskStateEntered",
            "id": 8,
            "previousEventId": 7,
            "stateEnteredEventDetails": {
                "name": "Glue StartJobRun"
            }
        }
    ],
    "NextToken": "eyJuZXh0VG9rZW4iOiBudWxsLCAiYm90b190cnVuY2F0ZV9hbW91bnQiOiAyfQ=="
}

```