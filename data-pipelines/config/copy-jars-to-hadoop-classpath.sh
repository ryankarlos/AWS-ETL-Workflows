#!/bin/bash

# --------- Downloaded from aws shared S3 directory:  s3://dynamodb-dpl-us-west-2/copy-jars-to-haddoop-classpath.sh ---------------------------------


# Downloads jars and adds them to Hadoop's classpath on EMR release emr-6.1.0 and above.
# Add a bootstrapAction on EmrCluster resource in Datapipeline: https://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/dp-object-emrcluster.html
# and use this script to download jar files that are needed to be present on Hadoop's classpath for successful execution
# of Hadoop jobs.
#
# Script usage: copy-add_jars_to_hadoop_classpath.sh <region> <s3_path_to_jar1> <s3_path_to_jar2> .. <s3_path_to_jarn>
#
# Usage in bootstrapAction field:
# s3://dynamodb-dpl-us-west-2/copy-jars-to-haddoop-classpath.sh,us-west-2,<s3_path_to_jar1>,<s3_path_to_jar2>
#
# Downloaded jars can be found under /home/hadoop/datapipeline_jars on the EMR cluster.
#
# Note: This would only add downloaded jar files on classpath for emr-6.1.0 release and above.

set -e -x

HADOOP_SHELLPROFILE_DIRECTORY="/etc/hadoop/conf/shellprofile.d"
DATAPIPELINE_JARS_SHELLPROFILE_FILE_PATH="$HADOOP_SHELLPROFILE_DIRECTORY/datapipeline-jars.sh"

DATAPIPELINE_JARS_DOWNLOAD_DIRECTORY="/home/hadoop/datapipeline_jars"
DATAPIPELINE_JARS_DOWNLOAD_DIRECTORY_PATH="$DATAPIPELINE_JARS_DOWNLOAD_DIRECTORY/"

echo "Got arguments: $@"

if [ $# -lt 2 ];
then
  >2& echo "Usage: ./copy-add_jars_to_hadoop_classpath.sh <region> <jar1-s3-path> ... <jarn-s3-path>"
  >2& echo "Region and S3 path to at least 1 jar file is required."
  exit 1
fi

region=$1
shift
echo "Region: $region"

check_or_create_dictory() {
  directory=$1
  use_sudo=$2
  if [ ! -d "$directory" ];
  then
    echo "Creating directory $directory"
    if [ $use_sudo == "true" ];
    then
      sudo mkdir -p "$directory"
    else
      mkdir -p "$directory"
    fi

  else
    echo "$directory already exists"
  fi
}

create_hadoop_shell_profile_script() {
  echo "Creating hadoop shell profile script: $DATAPIPELINE_JARS_SHELLPROFILE_FILE_PATH to add jar files under: $DATAPIPELINE_JARS_DOWNLOAD_DIRECTORY to hadoop classpath."
  # Need to break formatting here, so that the formatting on output file seems correct.
  cat <<< '#!/usr/bin/env bash
hadoop_add_profile datapipelinejars

DATAPIPELINE_JARS_DIRECTORY="/home/hadoop/datapipeline_jars"

function _datapipelinejars_hadoop_classpath
{
  if [ -d "$DATAPIPELINE_JARS_DIRECTORY" ]; then
    hadoop_add_classpath "$DATAPIPELINE_JARS_DIRECTORY/*"
  fi
}
' | sudo tee $DATAPIPELINE_JARS_SHELLPROFILE_FILE_PATH > /dev/null
}

check_or_create_dictory "$HADOOP_SHELLPROFILE_DIRECTORY" "true"
check_or_create_dictory "$DATAPIPELINE_JARS_DOWNLOAD_DIRECTORY" "false"

for s3_path in "$@"
do
  echo "Copying $s3_path to $DATAPIPELINE_JARS_DOWNLOAD_DIRECTORY_PATH"
  aws s3 cp --region $region "$s3_path" "$DATAPIPELINE_JARS_DOWNLOAD_DIRECTORY_PATH"
done

create_hadoop_shell_profile_script