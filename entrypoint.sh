#!/bin/bash

#/usr/sbin/nginx

#export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/

PY=/root/anaconda3/envs/ragflow/bin/python
export PYTHONPATH=/home/ah/desktop/ragflow
if [[ -z "$WS" || $WS -lt 1 ]]; then
  WS=1
fi

function task_exe(){
    while [ 1 -eq 1 ];do
      $PY rag/svr/task_executor.py $1;
    done
}

for ((i=0;i<WS;i++))
do
  task_exe  $i &
done

while [ 1 -eq 1 ];do
    $PY api/ragflow_server.py
done

wait;
