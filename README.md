# Kube API to manage Pappaya Lite tenants

# Development
1. Create `kube` file in `config` folder based on `kube-sample`.
1. Create `ssl-cert` and `ssl-key` files in `config` folder based on their sample files. This will be the pappayalite wildcard SSL details.
1. Build docker image ```docker build -t tenant-api . ```
1. Start the container with shared app and config folders ```docker run -d --name tenant-api -p 80:8080 --mount type=bind,bind-propagation=rprivate,source="$(pwd)"/app,target=/usr/src/tenant-api/app --mount type=bind,bind-propagation=rprivate,source="$(pwd)"/config,target=/usr/src/tenant-api/config --env TLS_KEY="$(cat config/ssl-key)" --env TLS_CERTIFICATE="$(cat config/ssl-cert)" tenant-api```
1. Container will start in detached mode and can be accessed in http://localhost
1. Update app files as required.
1. Restart container to see changes ```docker restart tenant-api```
1. When done stop container ```docker stop tenant-api```


# Production deployment to kubernetes

1. Build the image ```docker build -t registry.pappayacloud.com:5000/tenant-api:0.0.1 .```
1. Push the image to repository ```docker push registry.pappayacloud.com:5000/tenant-api:0.0.1```
1. Run the build command ```python3 build.py```
1. This will create the tenant-api build in kubernetes