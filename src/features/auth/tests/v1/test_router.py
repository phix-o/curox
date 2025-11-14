from fastapi.testclient import TestClient

from src.common.utils.other import reverse
from src.main import app

client = TestClient(app)

def test_login():
    url = reverse('login')
    response = client.post(url)
    
    assert response.status_code == 400

