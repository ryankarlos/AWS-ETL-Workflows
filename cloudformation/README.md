## AWS CLoud Formation

CloudFormation allows you to create and manage Amazon Web Services infrastructure deployments predictably and repeatedly. 
With CloudFormation, you declare all your resources and dependencies in a template file. The template defines a collection of resources as a single unit called a stack. CloudFormation creates and deletes all member resources of the stack together and manages all dependencies between the resources for you.
https://awscli.amazonaws.com/v2/documentation/api/latest/reference/cloudformation/index.html
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html

To create a stack follow the aws documentaiton below:
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-create-stack.html#cfn-using-console-initiating-stack-creation

Once stack is created from template - one can view the resources created
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-view-stack-data-resources.html
In the screenshot below, a stack has been created from `s3_lambda_dynamodb.yaml` template 


<img width="1000" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/example_cloudformation_stack_resources.png">


If stack is deleted, all the resources are deleted unless the resource in template
has  DeletionPolicy set to  'Retain' (for example, see `S3fordynamo` resource in `s3_lambda_dynamodb.yaml`)
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-delete-stack.html


### Change Sets

From AWS documentation:
Change sets allow you to preview how proposed changes to a stack might impact your running resources, for example, whether your changes will delete or replace any critical resources, 
Create a change set by submitting changes for the stack that you want to update. You can submit a modified stack template or modified input parameter values. 
CloudFormation compares your stack with the changes that you submitted to generate the change set; it doesn't make changes to your stack at this point.
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets-create.html

In the screenshot below, the lambda handler entrypoint was updated in lambda resource `batchwrites3dynamo` property in `S3fordynamo` 
and we can see this resource will be modified if change set is executed

<img width="1000" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/example_changeset.png">

AWS CloudFormation makes the changes to your stack only when you decide to execute the change set, allowing you to decide whether to proceed with your proposed changes or explore other changes by creating another change set.
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets-execute.html
Once change set is executed, CloudFormation updates the stack with those changes. So for the update to lambda 
`batchwrites3dynamo` resource, the stack events tab (screenshot below) shows the update has been complete 

<img width="1000" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/cloudformation_stack_events.png">
