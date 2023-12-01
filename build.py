from avionix import ChartBuilder, ChartInfo, ObjectMeta
from avionix.kube.apps import Deployment, DeploymentSpec, PodTemplateSpec
from avionix.kube.core import Container, ContainerPort, EnvVar, EnvVarSource, SecretKeySelector, LabelSelector, Volume, VolumeMount, PodSpec, Secret, SecretVolumeSource, Service, ServiceSpec, ServicePort
from kubernetes import config
import base64, os, sys, getopt, json


# GLOBALS
deployment_mode = 'development'
print('Deployment mode:', deployment_mode)

container = Container(
    name='tenant-api',
    # image='registry.pappayacloud.com:5000/tenant-api:0.0.1',
    image='muthukswamy/tenant-api:0.0.1',
    env=[
        EnvVar(name='KUBECONFIG', value='/usr/src/tenant-api/config/' + deployment_mode + '/kube.yaml'),
        EnvVar(name='TLS_KEY', value_from=EnvVarSource(secret_key_ref=SecretKeySelector(name='tls-secret', key='tls_key'))),
        EnvVar(name='TLS_CERTIFICATE', value_from=EnvVarSource(secret_key_ref=SecretKeySelector(name='tls-secret', key='tls_cert')))
    ],
    ports=[ContainerPort(8080)],
    volume_mounts=[VolumeMount(name='kubeconfig', mount_path='/usr/src/tenant-api/config/' + deployment_mode, read_only=True)],
    image_pull_policy='Always'
)

volume = Volume(
    name='kubeconfig',
    secret=SecretVolumeSource(secret_name='kube-config-secret', optional=False, default_mode=0o0400)
)

deployment = Deployment(
    metadata=ObjectMeta(name='tenant-api', labels={'pappayalite.com/app': 'tenant-api'}),
    spec=DeploymentSpec(
        replicas=1,
        template=PodTemplateSpec(
            ObjectMeta(labels={'pappayalite.com/app': 'tenant-api'}),
            spec=PodSpec(
                containers=[container],
                volumes=[volume]
            ),
        ),
        selector=LabelSelector(match_labels={'pappayalite.com/app': 'tenant-api'}),
    ),
)

try:
    kubeconfig = open('config/' + deployment_mode + '/kube.yaml', 'r')
    kubeconfig_data = kubeconfig.read()
    kubeconfig.close()
except FileNotFoundError:
    print('ERROR: Setup kube config file -- See README.md')
    exit(0)

kube_config_secret = Secret(
    metadata=ObjectMeta(name='kube-config-secret', labels={'pappayalite.com/app': 'tenant-api'}),
    data={'kube.yaml': base64.b64encode(kubeconfig_data.encode('ascii'))}
)

try:
    tls_key = open('config/' + deployment_mode + '/ssl-key', 'r')
    tls_key_data = tls_key.read()
    tls_key.close()
    tls_cert = open('config/' + deployment_mode + '/ssl-cert', 'r')
    tls_cert_data = tls_cert.read()
    tls_cert.close()
except FileNotFoundError:
    print('ERROR: Setup tls key and certificate files -- See README.md')
    exit(0)

tls_key_secret = Secret(
    metadata=ObjectMeta(name='tls-secret', labels={'pappayalite.com/app': 'tenant-api'}),
    data={
        'tls_key': base64.b64encode(tls_key_data.encode('ascii')),
        'tls_cert': base64.b64encode(tls_cert_data.encode('ascii')),
    }
)

service = Service(
    metadata=ObjectMeta(name='tenant-api-service', labels={'pappayalite.com/app': 'tenant-api'}),
    spec=ServiceSpec(selector={'pappayalite.com/app': 'tenant-api'}, ports=[ServicePort(port=80, target_port=8080)])
)

builder = ChartBuilder(
    ChartInfo(api_version='3.2.4', name='tenant-api', version='0.1.0', app_version='0.0.1'),
    [deployment, kube_config_secret, tls_key_secret, service],
    'charts',
    False,
    'pappayalite-tenant-api'
)

kube_config_path = os.path.dirname(os.path.realpath(__file__)) + '/config/' + deployment_mode + '/kube.yaml'
os.environ['KUBECONFIG'] = kube_config_path
config.load_kube_config(config_file=kube_config_path)

if builder.is_installed:
    print('Already installed. Upgrading...')
    builder.upgrade_chart(options={'atomic': None})
else:
    print('Installing...')
    builder.install_chart(options={'create-namespace': None, 'dependency-update': None})