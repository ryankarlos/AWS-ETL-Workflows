## Example 3

In this example, we will run a glue job to transform a fraud dataset into a format which is 
required for successfully importing into AWS Fraud Deetctor for training a model. 

All source code can be found in this [repository](https://github.com/ryankarlos/AWS-ETL-Workflows)
and the scripts for the various examples are stored in the respective named folders.

The simulated datasets `datasets/fraud/dataset1/fraudTest.csv` and `datasets/fraud/dataset1/fraudTrain.csv` have been 
downloaded from Kaggle https://www.kaggle.com/datasets/kartik2112/fraud-detection and contain  
variables for each online account registration event as required for creating an event 
in [AWS Fraud Detector](https://docs.aws.amazon.com/frauddetector/latest/ug/create-event-dataset.html): 

This contains the following variables:

* **index** - Unique Identifier for each row
* **transdatetrans_time** - Transaction DateTime
* **cc_num** - Credit Card Number of Customer
* **merchant** - Merchant Name
* **category** - Category of Merchant
* **amt** - Amount of Transaction
* **first** - First Name of Credit Card Holder
* **last** - Last Name of Credit Card Holder
* **gender** - Gender of Credit Card Holder
* **street** - Street Address of Credit Card Holder
* **city** - City of Credit Card Holder
* **state** - State of Credit Card Holder
* **zip** - Zip of Credit Card Holder
* **lat** - Latitude Location of Credit Card Holder
* **long** - Longitude Location of Credit Card Holder
* **city_pop** - Credit Card Holder's City Population
* **job** - Job of Credit Card Holder
* **dob** - Date of Birth of Credit Card Holder
* **trans_num** - Transaction Number
* **unix_time** - UNIX Time of transaction
* **merch_lat** - Latitude Location of Merchant
* **merch_long** - Longitude Location of Merchant
* **is_fraud** - Fraud Flag <--- Target Class

We need to transform the data so it meets the requirement of AWS Fraud detector, as we would like to 
train a model to identify fraudulent data entries and identify levels of risk associated with the predictions 
and what the appropriate actions to take should be. The model training requires some mandatory variables in the dataset:

`EVENT_LABEL` A label that classifies the event as 'fraud' or 'legit'.
`EVENT_TIMESTAMP` : The timestamp when the event occurred. The timestamp must be in ISO 8601 standard in UTC.

Using AWS glue we can transform the train and test datasets to conform to the AWS Fraud Detector 
requirements. 

### Upload raw data to S3 

Run the following command specifying the local path to fraud test and train raw data to upload 
and bucket name.  This creates a bucket (if it does not already exists) and then 
proceeds to the upload step. 

```
$ python s3/transfer_data_s3.py --bucket_name fraud-sample-data --local_dir datasets/fraud-sample-data/dataset1
2022-05-15 01:21:55,390 botocore.credentials INFO:Found credentials in shared credentials file: ~/.aws/credentials
2022-05-15 01:21:55,982 __main__ INFO:Creating new bucket with name:fraud-sample-data
0it [00:00, ?it/s]2022-05-15 01:21:56,733 __main__ INFO:Starting upload ....
0it [00:00, ?it/s]
2022-05-15 01:21:57,163 __main__ INFO:Successfully uploaded all files in datasets/fraud-sample-data/dataset1 to S3  bucket fraud-sample-data
```

### Upload glue script to S3 

If glue jobs have been run previously, there should be a bucket in S3 of the format - `aws-glue-assets-${AWS::AccountId}-${AWS::Region}`
Inside this bucket there will be a scripts folder where glue references all the scripts generated if glue job etl workflow is 
created from the console.
Upload the glue script fraud-etl-glue.py into the bucket in the scripts folder via console or cli.

If this bucket does not exist, then create your own. However, the ScriptLocation property of the GlueJOb resource in the 
cloudformation template used to create the scripts will need to be modified accordingly so it creates the glue job created can reference
the script in the correct location.

### Setting up resources and running etl pipeline

We can create the necessary resources for the glue etl pipeline via cloudformation template in `cloudformation/glue/glue-example3.yaml`
either via the cloudformation console or [cli](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/create-stack.html)
Note: that when creating from the cli, the `--capabilities CAPABILITY_NAMED_IAM` arg would need to be set. If done via the console, 
this box would require to be ticked before creating the stack or else it will throw an error.
This will create a glue job, classifer, custom crawler, eventbridge rule, lambda function and associated role.
We intend to build the architecture depicted below with the resources created.
A user triggers the crawler which crawls data from the S3 bucket and updates tbe glue catalog. Eventbridge rule is configured to 
detect when the glue crawler stops and triggers the target (lambda function), which starts the glue job to fetch the data 
from the data catalog, apply the pyspark and glue transforms and write the transformed dynamic dataframe back to S3. 

![](../screenshots/glue-etl-architecture-example-3.png") 

The outputs of the different steps in the glue spark script can be seen in the `example3.ipynb` notebook  in the [notebooks](https://github.com/ryankarlos/AWS-ETL-Workflows/tree/master/glue_etl/notebooks) folder.

Note: the classifier is configured to read both csvs files  (train and test data) into a single table in the glue data catalog, by specifying the input 
to the parent folder of both test and train csvs. If we needed to crawl these csvs separately, then we would need two separate classifiers
and have an exclusion rule for each one .e.g ignore the `fraudTrain.csv` if only requiring to crawl test csv and ignore the `fraudTest.csv` if
only crawling the train csv.
The pyspark script applies the necessary transformation logic and then splits the data into train and test dataframes based on the
timestamp limit settings chosen by the user. This can be overriden in the default arguments properties in the cloudformation template for the 
glue job resource. The arguments are  "--train_max_cut_off" which sets the timestamp for the last data point in the training set and "--test_min_cut_off" 
which sets the timestamp for the first data point in the test set. 

#### Deleting resources


To delete the resources, delete the cloudformation stack.
