## AWS CLoud Formation

<img width="1000" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/all-cf-stacks-console.png"></img>


CloudFormation allows you to create and manage Amazon Web Services infrastructure deployments predictably and repeatedly. 
With CloudFormation, you declare all your resources and dependencies in a template file. The template defines a collection of resources as a single unit called a stack. CloudFormation creates and deletes all member resources of the stack together and manages all dependencies between the resources for you.
https://awscli.amazonaws.com/v2/documentation/api/latest/reference/cloudformation/index.html
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html

To create a stack follow the aws documentation below:
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-create-stack.html#cfn-using-console-initiating-stack-creation

Once stack is created from template - one can view the resources created
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-view-stack-data-resources.html
In the screenshot below, a stack has been created from `s3_lambda_dynamodb.yaml` template 

<img width="1000" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/example_cloudformation_stack_resources.png">

If stack is deleted, all the resources are deleted unless the resource in template
has  DeletionPolicy set to  'Retain' (for example, see `S3fordynamo` resource in `s3_lambda_dynamodb.yaml`)
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-delete-stack.html

Everytime that you create a "new" stack and it fails it will rollback and you must delete the empty stack and attempt to redeploy again. 
The only time where you can update the stack in case it rollbacks due to fail in resource creation is if the stack had already 
been created successfully and any subsequent updates to the stack resulted in rollbacks.
It is recommended to make use of change sets (next section) before creating a new stack to help confirm the resources 
that need to create. 

One can use `aws cloudformation validate-template --template-url <s3_url>` (remote) or `aws cloudformation validate-template --template-body <file>` (local) 
command to check your template file for syntax errors. During validation, AWS CloudFormation first checks if the template 
is valid JSON. If it isn't, CloudFormation checks if the template is valid YAML. If both checks fail, CloudFormation 
returns a template validation error [3]. Note: The aws cloudformation validate-template command is designed to check 
only the syntax of your template. It does not ensure that the property values that you have specified for a resource are 
valid for that resource. Nor does it determine the number of resources that will exist when the stack is created.

* example output for correct template

```
$ aws cloudformation validate-template --template-body file://cloudformation/multi_resource_templates/eventbridge-rules-schedule.yaml
{
    "Parameters": [
        {
            "ParameterKey": "State",
            "DefaultValue": "ENABLED",
            "NoEcho": false,
            "Description": "Default State when EventBridge Rule is created"
        },
        {
            "ParameterKey": "CronScheduleOff",
            "DefaultValue": "cron(00 19 * 5 ? 2022)",
            "NoEcho": false,
            "Description": "s3 path to glue script"
        },
        {
            "ParameterKey": "CronScheduleOn",
            "DefaultValue": "cron(00 17 * 5 ? 2022)",
            "NoEcho": false,
            "Description": "s3 path to glue script"
        }
    ],
    "Capabilities": [
        "CAPABILITY_IAM"
    ],
    "CapabilitiesReason": "The following resource(s) require capabilities: [AWS::IAM::Role]"
}
```

* Template validation error with Type missing in Resource field

```
$ aws cloudformation validate-template --template-body file://cloudformation/multi_resource_templates/eventbridge-rules-schedule.yaml

An error occurred (ValidationError) when calling the ValidateTemplate operation: Template format error: [/Resources/ScheduleResourceOn] Every Resources o
```

* Template validation error with indentation issue

```
$ aws cloudformation validate-template --template-body file://cloudformation/multi_resource_templates/eventbridge-rules-schedule.yaml

An error occurred (ValidationError) when calling the ValidateTemplate operation: Template format error: YAML not well-formed. (line 6, column 3)
```

* Template missing value for ARN field in Target property of ScheduleResourceOff logical ID.

```
$ aws cloudformation validate-template --template-body file://cloudformation/multi_resource_templates/eventbridge-rules-schedule.yaml

An error occurred (ValidationError) when calling the ValidateTemplate operation: [/Resources/ScheduleResourceOff/Type/Targets/0/Arn] 'null' values are not allowed in templates
```

### Change Sets

From AWS documentation:
Change sets allow you to preview how proposed changes to a stack might impact your running resources, for example, 
whether your changes will delete or replace any critical resources, 
Create a change set by submitting changes for the stack that you want to update. You can submit a modified stack template
or modified input parameter values. 
CloudFormation compares your stack with the changes that you submitted to generate the change set; it doesn't make 
changes to your stack at this point.
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets-create.html

In the screenshot below, the lambda handler entrypoint was updated in lambda resource `batchwrites3dynamo` property in `S3fordynamo` 
and we can see this resource will be modified if change set is executed

<img width="1000" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/example_changeset.png">

AWS CloudFormation makes the changes to your stack only when you decide to execute the change set, allowing you to decide whether to proceed with your proposed changes or explore other changes by creating another change set.
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets-execute.html
Once change set is executed, CloudFormation updates the stack with those changes. So for the update to lambda 
`batchwrites3dynamo` resource, the stack events tab (screenshot below) shows the update has been complete 

<img width="1000" src="https://github.com/ryankarlos/aws_etl/blob/master/screenshots/cloudformation_stack_events.png">

In summary, change sets allow you to preview how proposed changes to a stack might impact your running resources, for 
example, whether your changes will delete or replace any critical resources, AWS CloudFormation makes the changes to your stack 
only when you decide to execute the change set, allowing you to decide whether to proceed with your proposed changes or 
explore other changes by creating another change set [1]. See creating a change set [2] for more information. 

The difference between Change Set and Direct Update is that with Direct update you submit changes and AWS CloudFormation 
immediately deploys them whereas with Change Set you are able to review and preview the changes AWS CloudFormation will 
make to your stack before creation, and then decide whether to apply those changes.
It is always best practice to always use Change Set to ensure that AWS CloudFormation doesn't make unintentional changes
or when you want to consider several options. For example, you can use a change set to verify that AWS CloudFormation 
won't replace your stack's database instances during an update [4]. It depends on the resource you are updating 
whether you do a Direct Update or a Change Set but there are instances where the resource you are trying to update 
can delete or modify another resource that depends on it. Hence, it is always advisable to use a Change Set on all occasions.

### Version Control of Resource Changes

Regarding version control, it is always best to keep an exact history of your resources. These methods can help you 
track changes between different versions of your templates, which can help you track changes to your stack resources. 
By maintaining a history, you can always revert your stack to a certain version of your template [5]. One way of doing 
this is by storing your cloudformation templates and storing them in version control repositories such as GitHub and 
naming them by version and date of deployment where they can be reviewed prior deployment.

### Nested Stacks and Existing Resource Imports

For nested stacks, when you specify 'AWS::CloudFormation::Stack' resource in the parent stack, it doesn't have the 
state of the resource you specified (exists or doesn't exist), you have to manually import the resource into that 
stack so it knows that the resource already exists. Then you can nest that stack into the parent stack and you won't 
see the issue again.  When manually importing resource as in https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/refactor-stacks.html 
the resource is actually not deleted from the source stack but simply moved or imported to the target stack. 
This is why in the documentation it specified to add the `"DeletionPolicy": "Retain"` in the source template so that 
when you remove it from the source template it doesn't get deleted.  


```
$ aws cloudformation update-stack --stack-name "source-stack-name"
```

By this time, the resource still exists but  oesn't belong to any stack so it can now be imported into  the target stack by using the "Import resources into stack" 
function in the console or cli. It is however required that you copy how it exactly was in the source template to the target template. 


```
$ aws cloudformation create-change-set --stack-name S3toDynamo --change-set-name ImportLambdas --change-set-type IMPORT --resources-to-import file://cloudformation/resources_to_import/lambdas.txt --template-body file://cloudformation/multi_resource_templates/s3_lambda_dynamodb.yaml
{
    "Id": "arn:aws:cloudformation:us-east-1:376337229415:changeSet/ImportLambdas/2604754c-95c3-4d19-b259-58d4b4ba317d",
    "StackId": "arn:aws:cloudformation:us-east-1:376337229415:stack/S3toDynamo/77ccdd50-ddd5-11ec-b827-0a97807fcd19"
}

```

Review the change set to make sure the correct resource is being imported into the target stack. 
```
aws cloudformation describe-change-set --stack-name S3toDynamo --change-set-name ImportLambdas


    "Changes": [
        {
            "Type": "Resource",
            "ResourceChange": {
                "Action": "Import",
                "LogicalResourceId": "batchwrites3dynamo",
                "PhysicalResourceId": "batch_write_s3_dynamodb",
                "ResourceType": "AWS::Lambda::Function",
                "Scope": [],
                "Details": []
            }
        },
        {
            "Type": "Resource",
            "ResourceChange": {
                "Action": "Import",
                "LogicalResourceId": "ddbinputtransform",
                "PhysicalResourceId": "ddb_input_transform",
                "ResourceType": "AWS::Lambda::Function",
                "Scope": [],
                "Details": []
            }
        }
    ],

```


Initiate the change set to import the resource into the target stack. Any stack-level tags are applied 
to imported resources at this time. Note: Need to attach policy which allows the lambda:TagResource 
action to IAM user performing the import, otherwise this will throw an error.
On successful completion of the operation (IMPORT_COMPLETE), the resource is successfully imported.

```
$ aws cloudformation execute-change-set --stack-name S3toDynamo --change-set-name ImportLambdas
```

After that, then you can make changes to the resource once fully imported. By then, you can modify this resource as it 
is in the target or new stack.

### Sync resource updates done outside Cloud Formation 

It is possible to update the stack to sync the manual changes you have made outside Cloudformation. By definition the 
resource that have been updated outside and is not in sync with the Cloudformation configuration is called to be "drifted". 
A more proper definition is that a resource is considered to have drifted if any of its actual property values differ 
from the expected property values. As best practice you can use "Drift Detection" to detect whether a stack's actual 
configuration differs, or has drifted, from its expected configuration [6]. For example, when you manually delete an 
S3 bucket created via CloudFormation this resource is considered to have drifted from your Cloudformation configuration. 
Cloudformation doesn't have the ability to update your existing CloudFormation template based on these manual changes. 
In this case, resources that depend on the S3 bucket e.g. where CloudWatch store logs in the specified S3 bucket will 
result in an error "Resource S3 does not exist". You can imagine that CloudFormation only makes API calls against the 
resources specified in the template and it is its only way to know if the resource exists or not.
To resolve drift, you can use the import operation in cases where a resource's configuration has drifted from its 
intended configuration and you want to accept the new configuration as the intended configuration. In most cases, you
would resolve the drift results by updating the resource definition in the stack template with a new configuration and 
then perform a stack update. However, if the new configuration updates a resource property that requires replacement, 
then the resource will be recreated during the stack update. If you want to retain the existing resource, you can use 
the resource import feature to update the resource and resolve the drift results without causing the resource to be 
replaced. See [7] for more information on how to do this operation. In summary, it is always best practice to commit 
changes via CloudFormation since making changes outside of it can complicate stack update or delete operations. 
Especially on occasions where you have resources that depend on other resources. If the root resource changes then this 
can potentially change how the dependent resources function that it provides you with no visibility on the possible 
outcomes of your changes.


### References:
 
[1] Updating stacks using change sets - https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets.html 
[2] Creating a change set - https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets-create.html 
[3] Validating a template - https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-validate-template.html 
[4] AWS CloudFormation stack updates - https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks.html  
[5] AWS CloudFormation best practices - Use code reviews and revision controls to manage your templates - https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#code 
[6] Detecting unmanaged configuration changes to stacks and resources - What is drift? - https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html#what-is-drift 
[7] Resolve drift with an import operation - https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resource-import-resolve-drift.html 
[8] AWS CloudFormation quotas - https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html 
[9] Fn::Sub with a mapping - https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html#w2ab1c31c28c59c11b5 
[10] Parameters - https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html#w2ab1c31c28c59b7 
