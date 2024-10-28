import random
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from faker import Faker

faker = Faker()


def create_items():
    for _ in range(500):
        user = faker.profile()
        response = requests.post(
            "http://localhost:8000/item",
            json={
                "name": user["username"],
                "price" : random.randint(1, 10000),
            },
        )

        print(response)


def get_item():
    for _ in range(500):
        
        response = requests.get(
            "http://localhost:8000/item/",
            params={"id": faker.random_number(digits=2)},
        )
        print(response)


with ThreadPoolExecutor() as executor:
    futures = {}

    for i in range(15):
        futures[executor.submit(create_items)] = f"create-item-{i}"

    for _ in range(15):
        futures[executor.submit(get_item)] = f"get-item-{i}"

    for future in as_completed(futures):
        print(f"completed {futures[future]}")
