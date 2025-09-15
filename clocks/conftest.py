import pytest
from rest_framework.test import APIClient


# ------------------------
# DRF APIClient
# ------------------------
@pytest.fixture
def api_client():
    return APIClient()
