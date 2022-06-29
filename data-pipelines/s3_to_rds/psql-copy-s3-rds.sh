#echo "Arguments: $@"

for i in "$@"
do
case "$i" in
    --red_jdbc=*|-a=*)
    REDJdbc="${i#*=}"
    shift
    ;;
    -b=*|--red_usr=*)
    REDUsr="${i#*=}"
    shift
    ;;
    -c=*|--red_pwd=*)
    REDPwd="${i#*=}"
    shift
    ;;
    -d=*|--red_tbl=*)
    REDTbl="${i#*=}"
    shift
    ;;
    *)
    echo "unknown option"
    ;;
esac
done

echo "Postgresql Jdbc: $REDJdbc"
echo "Postgresql Usr: $REDUsr"
#echo "RDS Pwd: $RDSPwd"
echo "Postgresql Tbl: $REDTbl"


export PGPASSWORD=$REDPwd

# exit script on error
set -e

#Install postgresql client
sudo amazon-linux-extras install postgresql13 -y

# Parse Postgresql Jdbc Connect String
#"jdbc:postgresql://eudb3.cvprvckckqrm.eu-west-1.redshift.amazonaws.com:5439/dbtest?tcpKeepAlive=true"
REDHost=`echo $REDJdbc | awk -F: '{print $3}' | sed 's/\///g'`
echo "Postgresql Host: $REDHost"
REDPort=`echo $REDJdbc | awk -F: '{print $4}' | awk -F/ '{print $1}'`
echo "Postgresql Port: $REDPort"
REDDb=`echo $REDJdbc | awk -F: '{print $4}' | awk -F/ '{print $2}' | awk -F? '{print $1}'`
echo "Postgresqlt DB: $REDDb"

echo "Running table truncate command before copy"
psql -h $REDHost -p $REDPort -U $REDUsr -d $REDDb -c 'TRUNCATE TABLE '$REDTbl';'

echo "Running the copy command"
psql -h $REDHost -p $REDPort -U $REDUsr -d $REDDb -c '\COPY '$REDTbl' FROM '/home/ec2-user/sample-data.csv' CSV'
echo "Data copied to Target table"
