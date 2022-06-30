from diagrams import Diagram, Cluster, Edge
from diagrams.aws.storage import SimpleStorageServiceS3
from diagrams.aws.analytics import GlueCrawlers, GlueDataCatalog, Glue
from diagrams.aws.general import User

with Diagram("Diagram", show=True, direction="LR"):
    S31 = SimpleStorageServiceS3("Raw Data")
    S32 = SimpleStorageServiceS3("Transformed Data")
    User = User("User")
    Glue_Job = Glue("Glue Job")
    Crawler = GlueCrawlers("GlueCrawler")
    Data_Catalog = GlueDataCatalog("GlueDataCatalog")

    User >>  Edge(label="Trigger glue job after crawler completes")  >> Glue_Job >> S32
    Data_Catalog << Crawler << Edge(label="run crawler") << User
    S31 >> Crawler
    Data_Catalog - Glue_Job
