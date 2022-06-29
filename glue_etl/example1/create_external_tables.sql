

-- create external schema

create external schema if not exists spectrum_flights
from data catalog
database 'myspectrum_db'
iam_role 'arn:aws:iam::376337229415:role/myspectrum_role'
create external database if not exists;

-- create external table to query from redshift -  specify s3 output path containingparquet data
-- from glue job (not sure if this works for partitione dir structure - may need to load each partition
-- separately

create external table spectrum_flights.fl_delays_with_codes(
  dayofmonth integer,
  uniquecarrier varchar,
  actualelapsedtime integer,
  origin varchar,
  dest varchar,
  distance integer,
  diverted smallint,
  carrierdelay integer,
  weatherdelay integer,
  nasdelay integer,
  securitydelay integer,
  lateaircraftdelay integer)
STORED AS PARQUET
LOCATION
  's3://flight-delays-2008/output_glue_etl/'







