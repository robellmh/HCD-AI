from app.auth.config import API_SECRET_KEY
from app.users.routers import router
from fastapi.testclient import TestClient

client = TestClient(router)


def test_create_user(client: TestClient) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    user_data = {
        "email": "testuser@example.com",
        "password": "securepassword",
        "role": "user",
    }

    response = client.post("/users/create", json=user_data, headers=headers)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["email"] == user_data["email"]
    assert json_response["action_taken"] == "created"


def test_get_user(client: TestClient) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    user_data = {
        "email": "testuser2@example.com",
        "password": "securepassword",
        "role": "user",
    }
    create_response = client.post("/users/create", json=user_data, headers=headers)
    assert create_response.status_code == 200
    user_id = create_response.json()["user_id"]

    response = client.get(f"/users/get/{user_id}", headers=headers)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["user_id"] == user_id
    assert json_response["email"] == user_data["email"]


def test_delete_user(client: TestClient) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    user_data = {
        "email": "testuser3@example.com",
        "password": "securepassword",
        "role": "user",
    }
    create_response = client.post("/users/create", json=user_data, headers=headers)
    assert create_response.status_code == 200
    user_id = create_response.json()["user_id"]

    response = client.post(f"/users/delete/{user_id}", headers=headers)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["user_id"] == user_id
    assert json_response["action_taken"] == "deleted"


def test_get_nonexistent_user(client: TestClient) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    non_existent_user_id = 999999
    response = client.get(f"/users/get/{non_existent_user_id}", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_delete_nonexistent_user(client: TestClient) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    non_existent_user_id = 999999
    response = client.post(f"/users/delete/{non_existent_user_id}", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_create_user_invalid_role(client: TestClient) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    user_data = {
        "email": "testuser4@example.com",
        "password": "securepassword",
        "role": "invalidrole",
    }

    response = client.post("/users/create", json=user_data, headers=headers)
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Role must be either 'admin' or 'user' or left blank"
    )


def test_create_user_existing_email(client: TestClient) -> None:
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_SECRET_KEY}",
    }

    user_data = {
        "email": "testuser5@example.com",
        "password": "securepassword",
        "role": "user",
    }

    response1 = client.post("/users/create", json=user_data, headers=headers)
    assert response1.status_code == 200

    response2 = client.post("/users/create", json=user_data, headers=headers)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Email already registered"
