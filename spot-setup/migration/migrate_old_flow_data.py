#!/bin/env python

#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import sys
import subprocess
import fnmatch
import re
import pandas as pd
import datetime
from utilities import util

old_oa_path=sys.argv[1]
staging_db=sys.argv[2]
hdfs_staging_path=sys.argv[3]
dest_db = sys.argv[4]
impala_daemon = sys.argv[5]


# Execution example:
#./migrate_old_flow_data.py '/home/spotuser/incubator-spot_old/spot-oa' 'spot_migration' '/user/spotuser/spot_migration/' 'migrated' 'node01'

def main():
  log = util.get_logger('SPOT.MIGRATE.FLOW')

  cur_path = os.path.dirname(os.path.realpath(__file__))
  new_spot_path = os.path.split(os.path.split(cur_path)[0])[0]
  new_oa_path = '{0}/spot-oa'.format(new_spot_path)
  log.info('New Spot OA path: {0}'.format(new_oa_path))
  old_spot_path = os.path.split(old_oa_path)[0]


  log.info("Creating HDFS paths for Impala tables")
  util.create_hdfs_folder('{0}/flow/scores'.format(hdfs_staging_path),log)
  util.create_hdfs_folder('{0}/flow/chords'.format(hdfs_staging_path),log)
  util.create_hdfs_folder('{0}/flow/edge'.format(hdfs_staging_path),log)
  util.create_hdfs_folder('{0}/flow/summary'.format(hdfs_staging_path),log)
  util.create_hdfs_folder('{0}/flow/storyboard'.format(hdfs_staging_path),log)
  util.create_hdfs_folder('{0}/flow/threat_investigation'.format(hdfs_staging_path),log)
  util.create_hdfs_folder('{0}/flow/timeline'.format(hdfs_staging_path),log)
  util.execute_cmd('hdfs dfs -setfacl -R -m user:impala:rwx {0}'.format(hdfs_staging_path),log)


  log.info("Creating Staging tables in Impala")
  util.execute_cmd('impala-shell -i {0} --var=hpath={1} --var=dbname={2} -c -f create_flow_migration_tables.hql'.format(impala_daemon, hdfs_staging_path, staging_db),log)


  ## Flow Ingest Summary
  log.info('Processing Flow Ingest Summary')
  ing_sum_path='{0}/data/flow/ingest_summary/'.format(old_oa_path)
  pattern='is_??????.csv'
  staging_table_name = 'flow_ingest_summary_tmp'
  dest_table_name = 'flow_ingest_summary'

  if os.path.exists(ing_sum_path):
    for file in fnmatch.filter(os.listdir(ing_sum_path), pattern):
      log.info('Processing file: {0}'.format(file))

      filepath='{0}{1}'.format(ing_sum_path, file)
      df = pd.read_csv(filepath)

      s = df.iloc[:,0]
      l_dates = list(s.unique())
      l_dates = map(lambda x: x[0:10].strip(), l_dates)
      l_dates = filter(lambda x: re.match('\d{4}[-/]\d{2}[-/]\d{1}', x), l_dates)
      s_dates = set(l_dates)

      for date_str in s_dates:
        dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        log.info('Processing day: {0} {1} {2} {3}'.format(date_str, dt.year, dt.month, dt.day))

        records = df[df['date'].str.contains(date_str)]
        filename = "ingest_summary_{0}{1}{2}.csv".format(dt.year, dt.month, dt.day)
        records.to_csv(filename, index=False)

        load_cmd = "LOAD DATA LOCAL INPATH '{0}' OVERWRITE INTO TABLE {1}.{2};".format(filename, staging_db, staging_table_name)
        util.execute_hive_cmd(load_cmd, log)

        insert_cmd = "INSERT INTO {0}.{1} PARTITION (y={2}, m={3}, d={4}) SELECT tdate, total FROM {5}.{6}".format(dest_db, dest_table_name, dt.year, dt.month, dt.day, staging_db, staging_table_name)
        util.execute_hive_cmd(insert_cmd, log)

        os.remove(filename)


  ## Iterating days 
  days_path='{0}/data/flow/'.format(old_oa_path)

  if os.path.exists(days_path):
    for day_folder in fnmatch.filter(os.listdir(days_path), '2*'):
        
      print day_folder
      dt = datetime.datetime.strptime(day_folder, '%Y%m%d')
      log.info('Processing day: {0} {1} {2} {3}'.format(day_folder, dt.year, dt.month, dt.day))
      full_day_path = '{0}{1}'.format(days_path,day_folder)


      ## Flow Scores and Flow Threat Investigation
      filename = '{0}/flow_scores.csv'.format(full_day_path) 
      if os.path.isfile(filename):

        log.info("Processing Flow Scores")
        staging_table_name = 'flow_scores_tmp'
        dest_table_name = 'flow_scores'

        load_cmd = "LOAD DATA LOCAL INPATH '{0}' OVERWRITE INTO TABLE {1}.{2};".format(filename, staging_db, staging_table_name)
        util.execute_hive_cmd(load_cmd, log)

        insert_cmd = "INSERT INTO {0}.{1} PARTITION (y={2}, m={3}, d={4}) SELECT tstart,srcip,dstip,sport,dport,proto,ipkt,ibyt,opkt,obyt,score,rank,srcIpInternal,destIpInternal,srcGeo,dstGeo,srcDomain,dstDomain,srcIP_rep,dstIP_rep FROM {5}.{6}".format(dest_db, dest_table_name, dt.year, dt.month, dt.day, staging_db, staging_table_name)
        util.execute_hive_cmd(insert_cmd, log)

        log.info("Processing Flow Threat Investigation")
        staging_table_name = 'flow_scores_tmp'
        dest_table_name = 'flow_threat_investigation'

        insert_cmd = "INSERT INTO {0}.{1} PARTITION (y={2}, m={3}, d={4}) SELECT tstart,srcip,dstip,sport,dport,sev FROM {5}.{6} WHERE sev > 0;".format(dest_db, dest_table_name, dt.year, dt.month, dt.day, staging_db, staging_table_name)
        util.execute_hive_cmd(insert_cmd, log)

        
      # Flow Chords
      log.info("Processing Flow Chords")
      staging_table_name = 'flow_chords_tmp'
      dest_table_name = 'flow_chords'

      for file in fnmatch.filter(os.listdir(full_day_path), 'chord*.tsv'):
        
        ip = re.findall("chord-(\S+).tsv", file)[0]
        ip = ip.replace('_', '.')
        log.info("Processing File: {0} with IP:{1}".format(file, ip))
        filename = '{0}/{1}'.format(full_day_path, file)

        load_cmd = "LOAD DATA LOCAL INPATH '{0}' OVERWRITE INTO TABLE {1}.{2};".format(filename, staging_db, staging_table_name)
        util.execute_hive_cmd(load_cmd, log)

        insert_cmd = "INSERT INTO {0}.{1} PARTITION (y={2}, m={3}, d={4}) SELECT '{5}', srcip, dstip, ibyt, ipkt FROM {6}.{7};".format(dest_db, dest_table_name, dt.year, dt.month, dt.day, ip, staging_db, staging_table_name)
        util.execute_hive_cmd(insert_cmd, log)


      ## Flow Edge
      log.info("Processing Flow Edge")
      staging_table_name = 'flow_edge_tmp'
      dest_table_name = 'flow_edge'
      pattern = 'edge*.tsv'
      edge_files = fnmatch.filter(os.listdir(full_day_path), pattern)

      for file in edge_files:

        parts = (re.findall("edge-(\S+).tsv", file)[0]).split('-')
        hh = int(parts[2])
        mn = int(parts[3])

        log.info("Processing File: {0} with HH: {1} and MN: {2}".format(file, hh, mn))
        filename = '{0}/{1}'.format(full_day_path, file)

        load_cmd = "LOAD DATA LOCAL INPATH '{0}' OVERWRITE INTO TABLE {1}.{2};".format(filename, staging_db, staging_table_name)
        util.execute_hive_cmd(load_cmd, log)

        insert_cmd = "INSERT INTO {0}.{1} PARTITION (y={2}, m={3}, d={4}) SELECT tstart, srcip, dstip, sport, dport, proto, flags, tos, ibyt, ipkt, input, output, rip, obyt, opkt, {5}, {6} FROM {7}.{8} WHERE srcip is not NULL;".format(dest_db, dest_table_name, dt.year, dt.month, dt.day, hh, mn, staging_db, staging_table_name)
        util.execute_hive_cmd(insert_cmd, log)


      ##flow_storyboard
      log.info("Processing Flow Storyboard")
      staging_table_name = 'flow_storyboard_tmp'
      dest_table_name = 'flow_storyboard'
      filename = '{0}/threats.csv'.format(full_day_path)

      if os.path.isfile(filename):

        load_cmd = "LOAD DATA LOCAL INPATH '{0}' OVERWRITE INTO TABLE {1}.{2};".format(filename, staging_db, staging_table_name)
        util.execute_hive_cmd(load_cmd, log)

        insert_cmd = "INSERT INTO {0}.{1} PARTITION (y={2}, m={3}, d={4}) SELECT ip_threat, title, text FROM {5}.{6};".format(dest_db, dest_table_name, dt.year, dt.month, dt.day, staging_db, staging_table_name)
        util.execute_hive_cmd(insert_cmd, log)


      ##flow_timeline
      log.info("Processing Flow Timeline")
      staging_table_name = 'flow_timeline_tmp'
      dest_table_name = 'flow_timeline'

      for file in fnmatch.filter(os.listdir(full_day_path), 'sbdet*.tsv'):
        
        ip = re.findall("sbdet-(\S+).tsv", file)[0]
        log.info("Processing File: {0} with IP:{1}".format(file, ip))
        filename = '{0}/{1}'.format(full_day_path, file)

        load_cmd = "LOAD DATA LOCAL INPATH '{0}' OVERWRITE INTO TABLE {1}.{2};".format(filename, staging_db, staging_table_name)
        util.execute_hive_cmd(load_cmd, log)

        insert_cmd = "INSERT INTO {0}.{1} PARTITION (y={2}, m={3}, d={4}) SELECT '{5}', tstart, tend, srcip, dstip, proto, sport, dport, ipkt, ibyt FROM {6}.{7};".format(dest_db, dest_table_name, dt.year, dt.month, dt.day, ip, staging_db, staging_table_name)
        util.execute_hive_cmd(insert_cmd, log)



  log.info("Dropping staging tables")
  util.execute_cmd('impala-shell -i {0} --var=dbname={1} -c -f drop_flow_migration_tables.hql'.format(impala_daemon, staging_db),log)

  log.info("Removing staging tables' path in HDFS")
  util.execute_cmd('hadoop fs -rm -r {0}/flow/'.format(hdfs_staging_path),log)

  log.info("Moving CSV data to backup folder")
  util.execute_cmd('mkdir {0}/data/backup/'.format(old_oa_path),log)
  util.execute_cmd('cp -r {0}/data/flow/ {0}/data/backup/'.format(old_oa_path),log)
  util.execute_cmd('rm -r {0}/data/flow/'.format(old_oa_path),log)

  log.info("Invalidating metadata in Impala to refresh tables content")
  util.execute_cmd('impala-shell -i {0} -q "INVALIDATE METADATA;"'.format(impala_daemon),log)


  log.info("Creating ipynb template structure and copying advanced mode and threat investigation ipynb templates for each pre-existing day in the new Spot location")
  ipynb_pipeline_path = '{0}/ipynb/flow/'.format(old_oa_path)
  if os.path.exists(ipynb_pipeline_path):
    for folder in os.listdir(ipynb_pipeline_path):
      log.info("Creating ipynb flow folders in new Spot locaiton: {0}".format(folder))
      util.execute_cmd('mkdir -p {0}/ipynb/flow/{1}/'.format(new_oa_path, folder),log)
      log.info("Copying advanced mode ipynb template")
      util.execute_cmd('cp {0}/oa/flow/ipynb_templates/Advanced_Mode_master.ipynb {0}/ipynb/flow/{1}/Advanced_Mode.ipynb'.format(new_oa_path, folder),log)
      log.info("Copying threat investigation ipynb template")
      util.execute_cmd('cp {0}/oa/flow/ipynb_templates/Threat_Investigation_master.ipynb {0}/ipynb/flow/{1}/Threat_Investigation.ipynb'.format(new_oa_path, folder),log)



if __name__=='__main__':
  main()
