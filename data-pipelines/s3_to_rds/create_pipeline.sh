#!/bin/bash

pipeline_name=${1}
file_path=${2}
echo ""
echo "Creating data pipeline $pipeline_name"
id=$(aws datapipeline create-pipeline --name $pipeline_name --unique-id ${pipeline_name}-token --query 'pipelineId'| tr -d '"')
echo ""
echo "Adding config settings from json definition for pipeline id $id"
aws datapipeline put-pipeline-definition --pipeline-id $id --pipeline-definition file://${2}
echo ""
echo "Activating pipeline $id"
aws datapipeline activate-pipeline --pipeline-id $id
