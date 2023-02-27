# Application of Big Data - Part 2

<div style="text-align: right"> Mathys Goncalves -  Wilfried Ponnou - Adrien Tarcy - Adrien Leblanc - BDIA </div>
</br>

## Objectifs 

Deploy, through an API, a trained prediction model using the DevOps philosophy on a cloud provider.

</br>

Technologies : 
- Language : Python 
- API framework : Flask
- Cloud Providers : Microsoft Azure 
- Load Testing Framework : Locust
- Metrics : Prometheus
  
</br>

## Fast Launching 

To run the project run this commands :

```ps
sudo systemctl restart docker.socket docker.service  
sudo docker build . -t knn:0.0.1
sudo docker run --network host -it knn:0.0.1   
```

Example of request :
```ps
curl localhost:5050/predict -H "Content-Type: application/json" -d '{"sepal length (cm)": 5,"sepal width (cm)": 3,"petal length (cm)": 1,"petal width (cm)": 0.2}'

curl localhost:5050/metrics
```
</br>

## **Model Training**

You can find this part [Here](01-Modeling.ipynb).

### **Dataset informations**

We are using the Iris flowers dataset.
This is perhaps the best known database to be found in the pattern recognition literature. Fisher's paper is a classic in the field and is referenced frequently to this day. (See Duda & Hart, for example.) The data set contains 3 classes of 50 instances each, where each class refers to a type of iris plant. One class is linearly separable from the other 2; the latter are NOT linearly separable from each other.

Predicted attribute: class of iris plant.

This is an exceedingly simple domain.

</br>

### **Attribute Information:**

1. sepal length in cm
2. sepal width in cm
3. petal length in cm
4. petal width in cm
5. class: Iris Setosa - Iris Versicolour - Iris Virginica

</br>

### **Modelisation**

Normalization is an important process in machine learning, as it allows the data to be treated in a consistent manner and normalized to the same scale. This can help improve the performance of the machine learning algorithm by preventing the dominance of a single feature or variable over others.

There are several types of normalization, such as Min-Max normalization, Z-Score normalization and L2 normalization. Sklearn Normalizer supports all three types of normalization. Here we choose L2 normalization.  This means that the sum of the squares of each dimension of the data is equal to 1.

L2 normalization is often used in classification algorithms for multi-dimensional data, as it can help to avoid the domination of one dimension over the others.

Using Normalizer can help improve the performance of your machine learning model by normalizing the data, which can reduce variance and avoid domination by a single feature or variable.

</br>

Since performance is not our priority we use a K-nearest neighbors (KNN). These advantages are : 

- Simplicity: The KNN model is very simple and easy to understand and implement. It does not require any training upfront, which makes it very fast.
- Little data required: The KNN model needs little data to work properly. It can work with a small amount of data and provide satisfactory results.
- Nonparametric: The KNN model is considered a nonparametric model, which means that it does not make any assumptions about the distribution of the data. This makes it useful for data that do not have a normal distribution.
- Easy adjustment: The KNN model can be easily adjusted as needed by changing the number of nearest neighbors used for classification.
- Performance: The KNN model can give good performance for classification tasks using a simple and fast approach.

The model is then exported with joblib to serialize it and use it in the next steps.

</br>

## **API integration**

You can find this part [Here](01-API.py).

</br>

### **Dockerization**

We have chosen a lightweight version of the Python image which is python:3.7.16-slim-bullseye. In our Dockerfile, we import this image and define our python script which is 01-API.py. Note that here it is necessary to indicate a file requirements.txt. The python library pipreqs was used to simply generate it beforehand.

```dockerfile
FROM python:3.7.16-slim-bullseye

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

COPY 01-API.py /var/server/app.py

CMD ["python3", "/var/server/app.py"]
```

</br>

> **NOTE** : use *'sudo chmod 666 /var/run/docker.sock'* to allow next commands. 

</br>

To create the container, it is first necessary to start Docker, then to build. weather being the name followed by the version (0.0.1).

```ps
sudo systemctl restart docker.socket docker.service  
docker build . -t knn:0.0.1
```

We can now verify that the container works:

```ps
docker run --network host -it knn:0.0.1   

[Output]
    {"prediction":[0.0]}
```

</br>

## **Github Actions**

The next goal is to use Github Actions to automate certain processes in the main.yaml.

1. Repo checkout

First we need to checkout the repo before executing the other steps.
```yaml
      - run: echo "🔎! The name of your branch is ${{ github.ref }} and your repository is ${{ github.repository }}."

      - name: Check out repository code
        uses: actions/checkout@v3
```

2. Docker deployment

We login, build and deploy the Docker container as we used before.

```yaml
      - name: Logging in Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_TOKEN }}
          
      - name: Extract metadata (tags, labels) for Docker
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: adrienleblanc/efrei-iris-classification-api

      - name: Build and push Docker image
        uses: docker/build-push-action@v3
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

3. Hadolint 
  
Then we can use Hadolint to check the validity of our image and good practices.

```yaml
      - name: hadolint
        uses: hadolint/hadolint-action@v2.0.0
        with:
          dockerfile: Dockerfile
```

4. Azure

We can also automate task from Azure. Here we want to deploy our Docker image on a Container App. To do so :
- Login Azure CLI
- Build and push image on Azure
- Deploy a Container App by specifying the targetPort used by our API if not specified, the default port of .py files is 8080. It's also recommanded to create a containerAppEnvironment. We used *azure/container-apps-deploy-action@47e03a783248cc0b5647f7ea03a8fb807fbc8e2f* due to a change in the Azure github action which failed.

```yaml
      - name: 'Login via Azure CLI'
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: 'Build and push image'
        uses: azure/docker-login@v1
        with:
          login-server: ${{ secrets.REGISTRY_LOGIN_SERVER }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}
      - run: |
          docker build . -t ${{ secrets.REGISTRY_LOGIN_SERVER }}/gr1-app:${{ github.sha }}
          docker push ${{ secrets.REGISTRY_LOGIN_SERVER }}/gr1-app:${{ github.sha }}
          
      - name: Deploy Container App
        uses: azure/container-apps-deploy-action@47e03a783248cc0b5647f7ea03a8fb807fbc8e2f
        with:
          acrName: efreiprediction
          containerAppEnvironment: grp1-env
          containerAppName: container-app-gr1
          targetPort: 5050
          resourceGroup: ${{ secrets.RESOURCE_GROUP }}
          imageToDeploy: ${{ secrets.REGISTRY_LOGIN_SERVER }}/gr1-app:${{ github.sha }}
```


</br>

## **Azure config**

In Azure, you first need to check *Ingress* and enable *Insecure connections*.

Then we want to enable auto scaling by configuring a new http scaling rules. We set *Concurrent requests* at 10 but you can choose your own settings.

</br>

## **Prometheus - Metrics**

This code is an example of using Prometheus with Flask, a Python web framework, to monitor and measure the performance of an endpoint.

The code first defines four Prometheus counters and a gauge:

*a* is a counter to count the number of requests served by the endpoint.
*s* is a counter to count the number of successful requests.
*f* is a counter to count the number of failed requests.
*g* is a gauge to measure the rate of success requests (success rate).

The *get_predict* function is the endpoint that serves predictions based on the input data received from a *POST* request. The function increments the counter a to count the number of requests served. Then, it processes the input data, makes a prediction using a machine learning model, and returns the prediction result in JSON format.

The *log_the_status_code* function is a Flask after_request handler that logs the status code of the response and increments either the counter *s* or *f* depending on the response status code. It also updates the gauge *g* with the success rate calculated as the ratio of the number of successful requests over the total number of requests (successful plus failed).

The *metrics* function is an endpoint that returns the latest Prometheus metrics generated by the *generate_latest* function.

In general, this code provides a simple example of how to use Prometheus with Flask to monitor the performance and reliability of an endpoint and to generate metrics for analysis and visualization.

</br>

## **Load Testing**

You can find this part [Here](02-Load_Testing.py).

</br>

There is a lot of ways to do load testing, one of them is Locust.
Locust is an open-source, Python-based load testing framework that is used to test the performance and scalability of web applications and APIs. It allows you to write tests in Python code and simulate the behavior of thousands or even millions of concurrent users, making it a popular choice for testing web applications under high load conditions.

With Locust, you can define user behavior and performance expectations in Python code, and then run a load test by launching a number of worker processes that simulate the behavior of multiple users. You can also monitor performance metrics in real-time and receive detailed reports on how your application performed under the load.

Locust's user-friendly and flexible design makes it an excellent choice for developers and testers who want to quickly and easily perform load testing without having to learn complex testing tools or set up complex testing environments.

</br>

Here is a simple example of how to use locust :

```python
class UserTasks(TaskSet):
    headers = {'Content-Type': 'application/json'}
    payload = {
        "sepal length (cm)": 5,
        "sepal width (cm)": 3,
        "petal length (cm)": 1,
        "petal width (cm)": 0.2
    }
    @task
    def predict(self):
        response = self.client.post("/predict", headers=self.headers, data=json.dumps(self.payload))
        if response.status_code != 200:
            print("Request failed with status code:", response.status_code)

class WebsiteUser(HttpUser):
    tasks = [UserTasks]
    wait_time = between(1, 2)
```

</br>

In the UserTasks class, headers and a sample payload data are defined, which are used in the predict task. The task predict makes a POST request to the "/predict" endpoint of the web application with the headers and payload defined in the UserTasks class. If the response status code is not 200 (OK), a message is printed indicating that the request failed with the returned status code.

The WebsiteUser class is a subclass of HttpUser and defines a list of tasks (UserTasks) that each user will execute and the time that each user will wait between tasks (wait_time). The wait_time is set to be a random value between 1 and 2 seconds using the between function.

In general, this script defines a load testing scenario in which a number of virtual users make predictions using the same endpoint of a web application, and the performance and scalability of the endpoint can be monitored and measured.

In order to run the load testing script :

```ps
locust -f 02-Load_Testing.py --host=http://localhost:5050
```
And open localhost:8089 on your browser to monitor the load test

> **NOTE** : Don't forget to *pip install locust*

</br>
</br>

