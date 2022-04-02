import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import functions as SqlFuncs

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node Amazon S3
AmazonS3_node1648261615433 = glueContext.create_dynamic_frame.from_catalog(
    database="flights_summary",
    table_name="delays",
    transformation_ctx="AmazonS3_node1648261615433",
)

# Script generated for node Drop Fields
DropFields_node1648261622521 = DropFields.apply(
    frame=AmazonS3_node1648261615433,
    paths=[
        "'year'",
        "'deptime'",
        "'dayofweek'",
        "'crsdeptime'",
        "'arrtime'",
        "'crsarrtime'",
        "'flightnum'",
        "'tailnum'",
        "'crselapsedtime'",
        "'airtime'",
        "'arrdelay'",
        "'depdelay'",
        "'taxiin'",
        "'taxiout'",
        "'cancelled'",
        "'cancellationcode'",
    ],
    transformation_ctx="DropFields_node1648261622521",
)

# Script generated for node Apply Mapping
ApplyMapping_node1648261643881 = ApplyMapping.apply(
    frame=DropFields_node1648261622521,
    mappings=[
        ("'month'", "long", "'month'", "long"),
        ("'dayofmonth'", "long", "'dayofmonth'", "long"),
        ("'uniquecarrier'", "string", "'uniquecarrier'", "string"),
        ("'actualelapsedtime'", "long", "'actualelapsedtime'", "long"),
        ("'origin'", "string", "'origin'", "string"),
        ("'dest'", "string", "'dest'", "string"),
        ("'distance'", "long", "'distance'", "long"),
        ("'diverted'", "long", "'diverted'", "long"),
        ("'carrierdelay'", "long", "'carrierdelay'", "long"),
        ("'weatherdelay'", "long", "'weatherdelay'", "long"),
        ("'nasdelay'", "long", "'nasdelay'", "long"),
        ("'securitydelay'", "long", "'securitydelay'", "long"),
        ("'lateaircraftdelay'", "long", "'lateaircraftdelay'", "long"),
    ],
    transformation_ctx="ApplyMapping_node1648261643881",
)

# Script generated for node Drop Duplicates
DropDuplicates_node1648261649257 = DynamicFrame.fromDF(
    ApplyMapping_node1648261643881.toDF().dropDuplicates(),
    glueContext,
    "DropDuplicates_node1648261649257",
)

# Script generated for node Amazon S3
AmazonS3_node1648261656864 = glueContext.getSink(
    path="s3://flight-delays-2008/output_glue_etl/",
    connection_type="s3",
    updateBehavior="UPDATE_IN_DATABASE",
    partitionKeys=["'month'"],
    compression="gzip",
    enableUpdateCatalog=True,
    transformation_ctx="AmazonS3_node1648261656864",
)
AmazonS3_node1648261656864.setCatalogInfo(
    catalogDatabase="flights_summary", catalogTableName="fl_delays_with_codes"
)
AmazonS3_node1648261656864.setFormat("glueparquet")
AmazonS3_node1648261656864.writeFrame(DropDuplicates_node1648261649257)
job.commit()
