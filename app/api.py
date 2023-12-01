from fastapi import FastAPI
import tenant

app = FastAPI(
    title="Pappaya Lite API",
    description="This API allows for creating and managing builds for pappaya lite tenants",
    version="0.1.0"
)


@app.get("/")
def pappaya_lite():
    return {"PappayaLiteTenant": "0.1.0"}


@app.post("/build/create")
def create_build(build: tenant.BuildParam):
    tenant.kubeconfig()

    odoo_values = tenant.odoo_value_overrides(build)
    chart_builder = tenant.define_chart_builder(build.namespace, build.build_name, odoo_values, build.app_version)

    if not chart_builder.is_installed:
        tenant.build_initial(chart_builder)
        return {
            'status': 'success',
            'message': 'Build started'
        }
    else:
        return {
            'status': 'error',
            'message': 'Build already exists'
        }


@app.post("/build/update")
def update_build(build: tenant.BuildParam):
    tenant.kubeconfig()

    odoo_values = tenant.odoo_value_overrides(build, True)
    chart_builder = tenant.define_chart_builder(build.namespace, build.build_name, odoo_values, build.app_version)

    if chart_builder.is_installed:
        tenant.build_upgrade(chart_builder, build.build_name, odoo_values, build.app_version)
        return {
            'status': 'success',
            'message': 'Build update started'
        }
    else:
        return {
            'status': 'error',
            'message': 'Cannot find build'
        }


@app.get("/build/status", response_model=tenant.BuildStatus)
def get_build_status(build_name: str, namespace: str):
    build_status = tenant.get_build_status(build_name, namespace)
    odoo_pod_status = tenant.get_pod_status(namespace, 'odoo')
    if odoo_pod_status == 'running':
        odoo_app_status = tenant.get_odoo_status(namespace)
    else:
        odoo_app_status = 'n/a'

    postgresql_pod_status = tenant.get_pod_status(namespace, 'postgresql')
    if postgresql_pod_status == 'running':
        postgresql_app_status = tenant.get_postgresql_status(namespace)
    else:
        postgresql_app_status = 'n/a'

    if build_status:
        return {
            'build_status': build_status,
            'odoo_pod_status': odoo_pod_status,
            'odoo_app_status': odoo_app_status,
            'postgresql_pod_status': postgresql_pod_status,
            'postgresql_app_status': postgresql_app_status,
        }
    else:
        return {
            'build_status': 'not avaiable'
        }
