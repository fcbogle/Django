import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from images.models import Image  # Replace with your actual Image model
from images.forms import ImageCreateForm  # Replace with your actual ImageCreateForm

@pytest.mark.django_db
def test_image_create_view_get(client):
    """
    Test that the image_create view renders the form on a GET request.
    """
    # Create and log in a test user
    User.objects.create_user(username="testuser", password="password")
    client.login(username="testuser", password="password")

    # Simulate a GET request
    response = client.get(reverse('images:create'))

    # Assert that the response contains the form and the correct template
    assert response.status_code == 200
    assert 'form' in response.context
    assert isinstance(response.context['form'], ImageCreateForm)
    assert 'images/image/create.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_image_create_view_post_valid(client):
    """
    Test that the image_create view processes valid POST data and creates an image.
    """
    # Create and log in a test user
    user = User.objects.create_user(username="testuser", password="password")
    client.login(username="testuser", password="password")

    # Simulate a POST request with valid data
    valid_data = {
        'title': 'Test Image',
        'url': 'https://example.com/test.jpg',
        'description': 'A test image',
    }
    response = client.post(reverse('images:create'), data=valid_data)

    # Assert redirection and that the image is created
    assert response.status_code == 302  # Redirection
    assert Image.objects.count() == 1
    new_image = Image.objects.first()
    assert new_image.title == 'Test Image'
    assert new_image.user == user
