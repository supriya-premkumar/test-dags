# -*- coding: utf-8 -*-
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from airflow.utils.dates import days_ago
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.models import DAG
from airflow.exceptions import AirflowException
import datetime

log = LoggingMixin().log

configmaps = ["airflow-configmap"]

try:
    # Kubernetes is optional, so not available in vanilla Airflow
    # pip install 'apache-airflow[kubernetes]'
    from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator

    args = {
        'owner': 'airflow',
        'start_date': days_ago(2)
    }

    dag = DAG(
        dag_id='git-sync-k8s-operator',
        default_args=args,
        schedule_interval='@hourly',
        start_date=days_ago(2))

    k1 = KubernetesPodOperator(
        namespace='airflow',
        image="ubuntu:16.04",
        cmds=["bash", "-cx"],
        arguments=["ls", "/root/airflow"],
        labels={"foo": "bar"},
        name="first-task",
        in_cluster=True,
        task_id="task-1",
        get_logs=True,
        dag=dag,
        is_delete_operator_pod=False,
        configmaps=configmaps,
    )

    k2 = KubernetesPodOperator(
        namespace='airflow',
        image="Python:3.6",
        cmds=["Python","-c"],
        arguments=["print('hello world!')"],
        labels={"foo": "bar"},
        name="second-task",
        task_id="task-2",
        get_logs=True,
        in_cluster=True,
        dag=dag,
        is_delete_operator_pod=False,
        configmaps=configmaps,
    )

except ImportError as e:
    log.warn("Could not import KubernetesPodOperator: " + str(e))
    log.warn("Install kubernetes dependencies with: "
             "    pip install 'apache-airflow[kubernetes]'")

# k1.set_upstream(start)
# k2.set_upstream(start)

k1 >> k2
