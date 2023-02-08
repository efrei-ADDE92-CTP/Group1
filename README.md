# Group 1
Project made for serving a machine learning Model API, on azure container app, using Docker, Prometheuse for monitoring, and locust for load test. All of these using github actions
Steps to run the project, in local mode:
```
!python 01-API.py
```
Post and get prediction:
```
curl https://gr1-container-app.kindsand-29ffcb50.westeurope.azurecontainerapps.io/predict -H "Content-Type: application/json" -d '{"sepal length (cm)": 2,"sepal width (cm)": 1,"petal length (cm)": 3,"petal width (cm)": 0.3}'
```
Monitor metrics of the API with Prometheus
```
curl localhost:8000/metrics
```
Perform load test with locust:
```
!pip install locust
```
Then, from the current working directory:
```
locust -f 02-Load_Testing.py --host=http://localhost:8080
```
Open localhost:8089 on your browser to monitor the load test
