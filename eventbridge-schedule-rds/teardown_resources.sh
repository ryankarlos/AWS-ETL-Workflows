
stack_names=( EventRuleCronSchedule EventBusSchedule RDS )
for name in "${stack_names[@]}"
do
  # send stderr to stdout to output error message to variable. Ignore non-error mesaages by redirecting to /dev/null
  ERROR=$(aws cloudformation describe-stacks --stack-name name 2>&1>/dev/null)
  if [[ $ERROR == *"An error occurred (ValidationError)"* ]]; then
    echo ""
    printf "Stack %s does not exist as validation error detected. Skipping delete operation" $name
  else
    echo ""
    printf "Deleting stack %s if exists \n" $name
    aws cloudformation delete-stack --stack-name name
  fi;
done
