from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import LambdaFunction
from diagrams.aws.storage import SimpleStorageServiceS3
from diagrams.aws.integration import Eventbridge
from diagrams.aws.analytics import GlueCrawlers, GlueDataCatalog, Glue
from diagrams.aws.management import Cloudwatch
from diagrams.aws.general import User

with Diagram("Diagram", show=True, direction="LR"):
    Lambda_Glue = LambdaFunction("Lambda Glue")
    S31 = SimpleStorageServiceS3("Raw Data")
    S32 = SimpleStorageServiceS3("Transformed Data")
    Eventbridge = Eventbridge("EventBridge")
    User = User("User")
    Glue_Job = Glue("Glue Job")
    Crawler = GlueCrawlers("GlueCrawler")
    Data_Catalog = GlueDataCatalog("GlueDataCatalog")
    CloudWatch = Cloudwatch("CloudWatch Logs")

    Data_Catalog << Crawler << Edge(label="run crawler") << User
    Crawler >> Eventbridge >> Lambda_Glue >> Glue_Job >> S32
    S31 >> Crawler
    Data_Catalog - Glue_Job >> CloudWatch
