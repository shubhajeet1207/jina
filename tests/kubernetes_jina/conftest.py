# Contains reusable fixtures for the kubernetes testing module
import operator
import os
from typing import List

import pykube
import pytest
import docker
from pytest_kind import KindCluster

from jina.logging.logger import JinaLogger

client = docker.from_env()
cur_dir = os.path.dirname(__file__)


@pytest.fixture()
def logger():
    logger = JinaLogger('kubernetes-testing')
    return logger


@pytest.fixture()
def test_executor_image(logger: JinaLogger):
    image, build_logs = client.images.build(path=os.path.join(cur_dir, 'test-executor'), tag='test-executor:0.11.0')
    for chunk in build_logs:
        if 'stream' in chunk:
            for line in chunk['stream'].splitlines():
                logger.debug(line)
    return image.tags[-1]


@pytest.fixture()
def executor_merger_image(logger: JinaLogger):
    image, build_logs = client.images.build(path=os.path.join(cur_dir, 'executor-merger'), tag='merger-executor:0.1.0')
    for chunk in build_logs:
        if 'stream' in chunk:
            for line in chunk['stream'].splitlines():
                logger.debug(line)
    return image.tags[-1]


@pytest.fixture()
def dummy_dumper_image(logger: JinaLogger):
    image, build_logs = client.images.build(path=os.path.join(cur_dir, 'dummy-dumper'), tag='dummy-dumper:0.1.0')
    for chunk in build_logs:
        if 'stream' in chunk:
            for line in chunk['stream'].splitlines():
                logger.debug(line)
    return image.tags[-1]


class KindClusterWrapper:

    def __init__(self, kind_cluster: KindCluster):
        self._cluster = kind_cluster
        self._kube_config_path = os.path.join(
            os.getcwd(), '.pytest-kind/pytest-kind/kubeconfig')
        self._kind_exec_path = os.path.join(
            os.getcwd(), '.pytest-kind/pytest-kind/kind'
        )
        self._set_kube_config()
        self._pykube_api = self._cluster.api

    def _set_kube_config(self):
        os.environ['KUBECONFIG'] = self._kube_config_path

    @property
    def kube_config_path(self) -> str:
        return self._kube_config_path

    @property
    def kind_exec_path(self) -> str:
        return self._kind_exec_path

    def port_forward(
            self,
            service_name: str,
            local_port: int,
            service_port: int,
            namespace: str = None
    ):
        if namespace:
            return self._cluster.port_forward(
                service_name,
                service_port,
                '-n',
                namespace,
                local_port=local_port,
                retries=20
            )
        else:
            return self._cluster.port_forward(
                service_name,
                service_port,
                local_port=local_port,
                retries=20
            )

    def list_pods(self, namespace: str = None) -> List:
        if namespace:
            return list(pykube.Pod.objects(self._pykube_api, namespace=namespace))
        return list(pykube.Pod.objects(self._pykube_api))

    def list_ready_pods(self, namespace: str = None) -> List:
        return list(filter(operator.attrgetter("ready"), self.list_pods(namespace)))

    def needs_docker_image(self, image_name: str):
        self._cluster.load_docker_image(image_name)


@pytest.fixture()
def k8s_cluster(kind_cluster: KindCluster) -> KindClusterWrapper:
    yield KindClusterWrapper(kind_cluster)