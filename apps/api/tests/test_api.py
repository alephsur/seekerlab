from uuid import uuid4

import pytest
from pydantic import ValidationError

from seekerlab.config import Settings
from seekerlab.modules.identity.dependencies import Principal, require_tester


def test_feedback_round_trip_and_duplicate_protection(client, builder_headers, tester_headers, campaign_payload):
    created = client.post("/api/v1/campaigns", json=campaign_payload, headers=builder_headers)
    assert created.status_code == 201
    campaign = created.json()
    assert campaign["reward_amount"] == "3.000000"
    path = f"/api/v1/campaigns/{campaign['id']}/submissions"
    feedback = {"feedback": "The onboarding button is difficult to find on a small screen."}
    assert client.post(path, json=feedback, headers=tester_headers).status_code == 201
    assert client.post(path, json=feedback, headers=tester_headers).status_code == 409
    history = client.get("/api/v1/submissions/me", headers=tester_headers).json()
    assert len(history) == 1
    assert history[0]["status"] == "pending_review"
    assert client.get(f"/api/v1/campaigns/{campaign['id']}").json()["submitted_count"] == 1
    assert client.get(path, headers=tester_headers).status_code == 403
    assert len(client.get(path, headers=builder_headers).json()) == 1


def test_builder_permissions(client, tester_headers, campaign_payload):
    assert client.post("/api/v1/campaigns", json=campaign_payload).status_code == 401
    assert client.post("/api/v1/campaigns", json=campaign_payload, headers=tester_headers).status_code == 403


def test_closed_campaign_and_missing_campaign(client, builder_headers, tester_headers, campaign_payload):
    campaign = client.post("/api/v1/campaigns", json=campaign_payload, headers=builder_headers).json()
    path = f"/api/v1/campaigns/{campaign['id']}"
    assert client.post(path + "/close", headers=builder_headers).status_code == 200
    assert client.post(path + "/submissions", json={"feedback": "A useful observation about the app."}, headers=tester_headers).status_code == 409
    assert client.get("/api/v1/campaigns").json() == []
    assert client.get(f"/api/v1/campaigns/{uuid4()}").status_code == 404


def test_capacity_applies_to_different_testers(client, builder_headers, tester_headers, campaign_payload):
    campaign = client.post("/api/v1/campaigns", json=campaign_payload, headers=builder_headers).json()
    path = f"/api/v1/campaigns/{campaign['id']}/submissions"
    payload = {"feedback": "A useful observation about the interface."}
    assert client.post(path, json=payload, headers=tester_headers).status_code == 201
    client.app.dependency_overrides[require_tester] = lambda: Principal("another-tester", "tester")
    assert client.post(path, json=payload, headers=tester_headers).status_code == 409


def test_validation_and_identity_cannot_be_spoofed(client, builder_headers, tester_headers, campaign_payload):
    bad = {**campaign_payload, "reward_amount": "-1"}
    assert client.post("/api/v1/campaigns", json=bad, headers=builder_headers).status_code == 422
    campaign = client.post("/api/v1/campaigns", json=campaign_payload, headers=builder_headers).json()
    response = client.post(f"/api/v1/campaigns/{campaign['id']}/submissions", headers=tester_headers,
                           json={"feedback": "A useful observation about the interface.", "tester_id": "victim"})
    assert response.status_code == 422


def test_development_authentication_refuses_production():
    with pytest.raises(ValidationError):
        Settings(app_env="production", dev_auth_enabled=True,
                 dev_builder_token="b" * 48, dev_tester_token="t" * 48)


def test_disabled_authentication_does_not_accept_dev_tokens(client, tester_headers):
    from seekerlab.config import get_settings
    client.app.dependency_overrides[get_settings] = lambda: Settings(dev_auth_enabled=False)
    assert client.get("/api/v1/submissions/me", headers=tester_headers).status_code == 503
