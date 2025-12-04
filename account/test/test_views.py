import pytest
from django.urls import reverse
from django.contrib.auth.models import User

from account.models import Profile, Contact


@pytest.mark.django_db
def test_dashboard_view(client):
    # Create a test user
    user = User.objects.create_user(username='testuser', password='password')

    # Login the user
    client.login(username='testuser', password='password')

    # Access the dashboard view
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert 'Dashboard' in response.content.decode()  # Check that the dashboard is rendered


@pytest.mark.django_db
def test_follow_post_action(client):
    # Create a couple of users
    # Create test users
    user1 = User.objects.create_user(username='testuser1', password='password1')
    user2 = User.objects.create_user(username='testuser2', password='password2')

    # Log in user1
    client.login(username='testuser1', password='password1')

    # Test follow action
    response = client.post(
        reverse('user_follow'),  # Replace 'user_follow' with the actual URL name of the view
        {'id': user2.id, 'action': 'follow'},
        #content_type='application/json'
        #content_type='application/x-www-form-urlencoded'
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data['status'] == 'success'
    assert Contact.objects.filter(user_from=user1, user_to=user2).exists()

@pytest.mark.django_db
def test_unfollow_post_action(client):
    # Create test users
    user1 = User.objects.create_user(username='testuser1', password='password1')
    user2 = User.objects.create_user(username='testuser2', password='password2')

    # Log in user1
    client.login(username='testuser1', password='password1')

    # Test unfollow action
    response = client.post(
        reverse('user_follow'),
        {'id': user2.id, 'action': 'unfollow'},
        #content_type='application/json'
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data['status'] == 'success'
    assert not Contact.objects.filter(user_from=user1, user_to=user2).exists()



@pytest.mark.django_db
def test_register_view_get(client):
    # Access the register view
    response = client.get(reverse('register'))
    assert response.status_code == 200
    assert 'Create my account' in response.content.decode()  # Check if the registration form is rendered


@pytest.mark.django_db
def test_register_view_post(client):
    # Create data for post
    post_data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123',
        'password2': 'password123',
    }
    # Post to the register endpoint
    response = client.post(reverse('register'), data=post_data)
    # Assert that the response redirects to the "register_done" page
    assert response.status_code == 200
    assert 'Your account has been successfully created.' in response.content.decode()

    # Check if the user was created
    user = User.objects.get(username='testuser')
    assert user is not None
    assert user.email == 'testuser@example.com'
    assert user.check_password('password123')  # Check that the password was properly hashed

    # Check if the profile was created
    profile = Profile.objects.get(user=user)
    assert profile is not None
