#!/bin/bash

# exit script at first cmd error
set -e

STATE=${1}
CRON_ON=${2}
CRON_OFF=${3}

REPO_ROOT=$( cd "$(dirname "$(dirname "${BASH_SOURCE[0]}")" )" || exit ; pwd -P )
EVENTBRIDGE_RULES_CF=$REPO_ROOT/cloudformation/multi_resource_templates/eventbridge-rules-schedule.yaml || exit
EVENTBRIDGE_BUS_CF=$REPO_ROOT/cloudformation/event-bus.yaml || exit
RESOURCE_IMPORT_CF=$REPO_ROOT/cloudformation/resources_to_import/event-bus.txt || exit
RDS_CF=$REPO_ROOT/cloudformation/rds.yaml || exit


if [[ $? -eq 0 ]];then
  echo ""
  echo "Creating change set for EventRuleSchedule Stack"
  aws cloudformation create-change-set --stack-name EventRuleCronSchedule --change-set-type IMPORT \
  --change-set-name ImportChangeSet \
  --capabilities CAPABILITY_IAM \
  --resources-to-import file://"${RESOURCE_IMPORT_CF}" \
  --template-body file://"${EVENTBRIDGE_RULES_CF}" \
  --parameters ParameterKey=State,ParameterValue="$STATE" \
  ParameterKey=CronScheduleOn,ParameterValue="$CRON_ON" \
  ParameterKey=CronScheduleOff,ParameterValue="$CRON_OFF" \
  ParameterKey=DBUsername,ParameterValue="${DB_USERNAME}" \
  ParameterKey=DBPassword,ParameterValue="${DB_PASSWORD}"

fi;

if [[ $? -eq 0 ]];then
  echo ""
  echo "Showing resources to be created in change set"
  aws cloudformation describe-change-set --change-set-name ImportChangeSet --stack-name EventRuleCronSchedule
fi;


while true; do
    read -p "Do you wish to execute change set? " yn
    case $yn in
        [Yy]* ) export EXECUTE="yes"; break;;
        [Nn]* ) export EXECUTE="no"; break;;
        * ) echo "Please answer 'y' or 'n'";;
    esac
done

if [[ $EXECUTE -eq "yes" ]]; then
  echo ""
  echo "Executing change set as requested"
  aws cloudformation execute-change-set --change-set-name ImportChangeSet --stack-name EventRuleCronSchedule
else
  echo ""
  echo "Change set execution not required so exiting"
  exit
fi;
