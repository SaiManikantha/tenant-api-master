FROM python:3.7

WORKDIR /usr/src/tenant-api

COPY requirements.txt ./
RUN mkdir charts /.config /.cache && chmod -R 777 charts /.config /.cache
RUN pip install --no-cache-dir -r requirements.txt

# Install Helm
RUN curl https://baltocdn.com/helm/signing.asc | apt-key add -
RUN apt-get install apt-transport-https --yes
RUN echo "deb https://baltocdn.com/helm/stable/debian/ all main" | tee /etc/apt/sources.list.d/helm-stable-debian.list
RUN curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list
RUN apt-get update
RUN apt-get install kubectl helm

COPY app ./app

EXPOSE 8080

CMD ["uvicorn", "api:app", "--app-dir", "app", "--host", "0.0.0.0", "--port", "8080"]