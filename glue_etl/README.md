#  ETL jobs using glue

### Transforming data in S3 csv and storing as parquet 

<img width="1000" alt="flights_glue_job" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/example_etl_workflow.png">


The raw CSV files in S3 bucket are crawled using populate the schema and data in the glue data catalog which can be queried with athena.
The glue job uses the catalog as source, performs a few transformation steps (.e.g drop fields, cast types and drop duplicate fields)
and then load to S3 in parquet format (which can be partitioned by specified key). We can also ask glue to create/update another 
table in catalog with transformed schema and data.  The transformed data can be accessed by athena for querying and visualised via Quicksight.
We can also use Redshift spectrum to copy external table in redshift from catalog and query in there if required.


<img width="450" alt="flights_glue_job" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/flights_glue_job.png">




