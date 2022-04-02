#  ETL jobs using glue

### Transforming data in S3 csv and storing as parquet 

<img width="1000" alt="flights_glue_job" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/example_etl_workflow.png">




First need to create a database in the glue catalog to store the raw and transformed table schemas. Ive called this flights_summary
The raw CSV files in S3 bucket are crawled using populate the schema and data in the glue data catalog which can be queried with athena. (reference https://docs.aws.amazon.com/glue/latest/ug/tutorial-add-crawler.html)
The properties of crawler created can be accessed via console cli as below. The path to the raw csv data "s3://flight-delays-2008/delays", has been provided,  "DatabaseName": "flights_summary" (created in glue data catalog)


``aws glue get-crawler --name flights``


<img width="493" alt="Screenshot 2022-04-03 at 00 16 03" src="https://user-images.githubusercontent.com/16509490/161404600-2fefffb7-72d4-4cb7-9697-06791c8005b9.png">

For this case, Ive created a customm classifer  "header-detect-csv" with the col names and types for the table in catalog as the crawler can sometimes have issues with detecting the column names correctly on its own.

<img width="581" alt="Screenshot 2022-04-03 at 00 28 57" src="https://user-images.githubusercontent.com/16509490/161404762-afc2ba63-ddee-437c-8388-0b7e74d132bb.png">

When the crawler is run successfully, we should see a table in the catalog called delays, which can be queried through athena.If you are running athena for the first time, its best to create a workgroup with the necessary IAM permissions and  bucket to store the query logs and results before you can run a query.

<img width="1171" alt="image" src="https://user-images.githubusercontent.com/16509490/161404956-a707505a-cdce-4bbe-a446-a5ac7cd0dd03.png">


In the query editor, we can then see the top 10 rows of the table 'delays' in the 'flights_summary' db in the AWS data catalog

<img width="1306" alt="image" src="https://user-images.githubusercontent.com/16509490/161405022-398ae72e-9814-4bc0-9647-7674c0e57102.png">


We can now create a glue job for the ETL which uses the catalog table 'delays' as source, performs a few transformation steps (.e.g drop fields, cast types and drop duplicate fields) and finally loads to S3 in parquet format (which can be partitioned by specified key). 


<img width="450" alt="flights_glue_job" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/flights_glue_job.png">


We can also ask glue to create/update another table in catalog with transformed schema and data or do this later via another crawler from parquet results in the bucket.  The transformed data can be accessed by athena for querying and visualised via Quicksight.

The job run can be monitored in the job runs in the console or for the logs and error outputs from cloudwatch log group streams.

<img width="1373" alt="image" src="https://user-images.githubusercontent.com/16509490/161405206-13f67ae3-d7e5-4a17-846d-601b03fa132c.png">

Once the job is finished we should see the final table in the catalog

<img width="1299" alt="image" src="https://user-images.githubusercontent.com/16509490/161405155-860b55a3-b5ce-4e1b-9259-4b4e69dbb138.png">


We can also use Redshift spectrum to copy external table in redshift from catalog and query in there if required.




