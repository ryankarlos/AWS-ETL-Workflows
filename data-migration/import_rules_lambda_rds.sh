#!/bin/bash

# exit script at first cmd error
set -e

STATE=${1}
CRON_ON=${2:-"cron(00 18 * 5 ? 2022)"}
CRON_OFF=${3:-"cron(00 19 * 5 ? 2022)"}

REPO_ROOT=$( cd "$(dirname "$(dirname "${BASH_SOURCE[0]}")" )" || exit ; pwd -P )
EVENTBRIDGE_RULES_CF=$REPO_ROOT/cloudformation/multi_resource_templates/eventbridge_schedule.yaml || exit
RESOURCE_IMPORT_CF=$REPO_ROOT/cloudformation/resources_to_import/eventbridge.txt || exit


if [[ $? -eq 0 ]];then
  echo ""
  echo "Creating change set for EventRuleSchedule Stack ...."
  aws cloudformation create-change-set --stack-name EventBridge-RDS-Schedule  --change-set-type IMPORT \
  --change-set-name ImportChange \
  --resources-to-import file://"${RESOURCE_IMPORT_CF}" \
  --template-body file://"${EVENTBRIDGE_RULES_CF}" \
  --parameters ParameterKey=State,ParameterValue="$STATE" \
  ParameterKey=CronScheduleOn,ParameterValue="$CRON_ON" \
  ParameterKey=CronScheduleOff,ParameterValue="$CRON_OFF"
fi;


echo ""
echo "Wait 15 secs before showing changes in change set description ......."
sleep 15


if [[ $? -eq 0 ]];then
  echo ""
  echo "Showing resources to be created in change set"
  aws cloudformation describe-change-set --change-set-name ImportChange --stack-name EventBridge-RDS-Schedule
fi;


while true; do
    read -p "Do you wish to execute change set? " yn
    case $yn in
        [Yy]* ) export EXECUTE="yes"; break;;
        [Nn]* ) export EXECUTE="no"; break;;
        * ) echo "Please answer 'y' or 'n'";;
    esac
done

if [[ $EXECUTE == "yes" ]]; then
  echo ""
  echo "Executing change set as requested"
  aws cloudformation execute-change-set --change-set-name ImportChange --stack-name EventBridge-RDS-Schedule
else
  echo ""
  echo "Change set execution not required so deleting stack and exiting"
   aws cloudformation delete-change-set --change-set-name ImportChange --stack-name EventBridge-RDS-Schedule
  exit
fi;
