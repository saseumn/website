from flask import url_for
from saseumn.tests.data import users


class TestUsers(object):
    def test_registration(self, client):
        user = users[0]
        r = client.post(url_for("users.register"), data={
            "register-name": user["name"],
            "register-email": user["email"],
            "register-username": user["username"],
            "register-password": user["password"],
            "register-confirm_password": user["password"],
        })
        assert r.status_code == 302
