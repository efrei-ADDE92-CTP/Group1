from locust import HttpUser, TaskSet, task, between
import json

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


#locust -f 02-Load_Testing.py --host=http://localhost:8080