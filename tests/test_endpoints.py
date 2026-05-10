import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAuth:
    def test_register(self):
        response = client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "pass1234"
            }
        )
        assert response.status_code == 201

    def test_register_duplicate(self):
        # 先注册一个用户
        client.post("/auth/register",json = {
            "username":"dupuser","email":"dup@test.com","password":"pass1234"
        })
        # 再注册相同用户名
        response = client.post("/auth/register",json = {
            "username":"dupuser","email":"another@test.com","password":"pass1234"
        })
        assert response.status_code == 409  # 修改为 409

    def test_login(self):
        client.post("/auth/register", json={
            "username": "loginuser", "email": "login@test.com", "password": "pass1234"
        })
        response = client.post("/auth/login", data={
            "username": "loginuser", "password": "pass1234"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()