"""
Unit tests for router_page.py HTTP endpoints functionality.

This module contains comprehensive unit tests for the page router endpoints,
covering all HTTP functionality including form processing, validation,
template rendering, and error handling. Tests are organized by endpoint
and functionality for easy maintenance and understanding.

All tests use proper type annotations, follow the AAA (Arrange, Act, Assert)
testing pattern, and include detailed documentation for clarity.
"""

import pytest
from fastapi.testclient import TestClient

from app.api.schemas import JoinChatForm


class TestHomePageEndpoint:
    """Test cases for the home page GET endpoint."""
    
    def test_home_page_returns_200(self, test_client: TestClient) -> None:
        """
        Test that home page returns HTTP 200 status code.
        
        This test verifies that the home page endpoint is accessible
        and returns a successful response without errors.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
        """
        # Arrange: No setup needed for simple GET request
        
        # Act: Make GET request to home page
        response = test_client.get("/")
        
        # Assert: Verify successful response
        assert response.status_code == 200, "Home page should return 200 status code"
    
    def test_home_page_returns_html(self, test_client: TestClient) -> None:
        """
        Test that home page returns HTML content type.
        
        This test verifies that the response contains proper HTML content
        and the content-type header is set correctly for browser rendering.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
        """
        # Arrange: No setup needed for simple GET request
        
        # Act: Make GET request to home page
        response = test_client.get("/")
        
        # Assert: Verify HTML content type
        assert response.status_code == 200, "Response should be successful"
        assert "text/html" in response.headers["content-type"], "Response should be HTML"
    
    def test_home_page_contains_form(self, test_client: TestClient) -> None:
        """
        Test that home page contains the chat entry form.
        
        This test verifies that the rendered HTML contains the necessary
        form elements for username and room_id input, ensuring the user
        interface is properly rendered.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
        """
        # Arrange: No setup needed for simple GET request
        
        # Act: Make GET request to home page
        response = test_client.get("/")
        
        # Assert: Verify form elements are present in HTML
        assert response.status_code == 200, "Response should be successful"
        html_content = response.text
        
        # Check for form structure and input fields
        assert 'action="/join_chat"' in html_content, "Form should have correct action"
        assert 'name="username"' in html_content, "Username input should be present"
        assert 'name="room_id"' in html_content, "Room ID input should be present"
        assert 'type="submit"' in html_content, "Submit button should be present"


class TestJoinChatSuccess:
    """Test cases for successful join_chat POST requests."""
    
    def test_join_chat_valid_data(
        self,
        test_client: TestClient,
        sample_form_data_valid: dict[str, str | int]
    ) -> None:
        """
        Test join_chat with valid form data returns success.
        
        This test verifies that when valid form data is submitted,
        the endpoint processes it successfully and returns a response
        without validation errors.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
            sample_form_data_valid: Valid form data from fixture
        """
        # Arrange: Valid form data is provided by fixture
        
        # Act: Submit valid form data
        response = test_client.post("/join_chat", data=sample_form_data_valid)
        
        # Assert: Verify successful processing
        assert response.status_code == 200, "Valid form should return 200 status code"
        assert "text/html" in response.headers["content-type"], "Response should be HTML"
    
    def test_join_chat_returns_chat_page(
        self,
        test_client: TestClient,
        sample_form_data_valid: dict[str, str | int]
    ) -> None:
        """
        Test that successful join_chat returns the chat interface page.
        
        This test verifies that upon successful form submission, the user
        is redirected to the chat interface (index.html template) with
        the correct template context.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
            sample_form_data_valid: Valid form data from fixture
        """
        # Arrange: Valid form data is provided by fixture
        
        # Act: Submit valid form data
        response = test_client.post("/join_chat", data=sample_form_data_valid)
        
        # Assert: Verify chat page is rendered
        assert response.status_code == 200, "Response should be successful"
        html_content = response.text
        
        # Check for chat interface elements
        assert "Chat with WebSocket" in html_content, "Chat page title should be present"
        assert 'id="messages"' in html_content, "Messages container should be present"
        assert 'id="messageInput"' in html_content, "Message input should be present"
    
    def test_join_chat_generates_user_id(
        self,
        test_client: TestClient,
        sample_form_data_valid: dict[str, str | int]
    ) -> None:
        """
        Test that join_chat generates a user_id for the session.
        
        This test verifies that a user_id is generated and included
        in the template context, ensuring each user gets a unique
        identifier for the chat session.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
            sample_form_data_valid: Valid form data from fixture
        """
        # Arrange: Valid form data is provided by fixture
        
        # Act: Submit valid form data
        response = test_client.post("/join_chat", data=sample_form_data_valid)
        
        # Assert: Verify user_id is present in response
        assert response.status_code == 200, "Response should be successful"
        html_content = response.text
        
        # Check for user_id in data attributes
        assert 'data-user-id=' in html_content, "User ID should be present in HTML"
    
    def test_join_chat_user_id_in_range(
        self,
        test_client: TestClient,
        sample_form_data_valid: dict[str, str | int]
    ) -> None:
        """
        Test that generated user_id is within expected range (100-100000).
        
        This test verifies that the random user_id generation produces
        values within the specified range, ensuring proper uniqueness
        and avoiding conflicts with system IDs.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
            sample_form_data_valid: Valid form data from fixture
        """
        # Arrange: Valid form data is provided by fixture
        
        # Act: Submit valid form data multiple times to test range
        user_ids = []
        for _ in range(5):  # Test multiple generations
            response = test_client.post("/join_chat", data=sample_form_data_valid)
            assert response.status_code == 200, "Response should be successful"
            
            # Extract user_id from HTML (simplified extraction)
            html_content = response.text
            if 'data-user-id="' in html_content:
                start = html_content.find('data-user-id="') + len('data-user-id="')
                end = html_content.find('"', start)
                user_id = int(html_content[start:end])
                user_ids.append(user_id)
        
        # Assert: Verify all user_ids are in range
        for user_id in user_ids:
            assert 100 <= user_id <= 100000, f"User ID {user_id} should be in range 100-100000"
    
    def test_join_chat_sanitizes_username(
        self,
        test_client: TestClient
    ) -> None:
        """
        Test that join_chat trims whitespace from username.
        
        This test verifies that the Pydantic validator properly sanitizes
        username input by removing leading and trailing whitespace,
        ensuring clean data storage and display.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
        """
        # Arrange: Form data with whitespace in username
        form_data_with_whitespace = {
            "username": "  testuser  ",
            "room_id": 1
        }
        
        # Act: Submit form with whitespace
        response = test_client.post("/join_chat", data=form_data_with_whitespace)
        
        # Assert: Verify successful processing (whitespace should be trimmed)
        assert response.status_code == 200, "Form with whitespace should be processed successfully"
        html_content = response.text
        
        # Check that the username appears without extra whitespace
        assert "testuser" in html_content, "Sanitized username should be present"


class TestJoinChatValidationErrors:
    """Test cases for join_chat validation error handling."""
    
    def test_join_chat_empty_username(
        self,
        test_client: TestClient,
        sample_form_data_invalid: dict[str, dict[str, str | int]]
    ) -> None:
        """
        Test join_chat with empty username returns validation error.
        
        This test verifies that submitting a form with an empty username
        triggers validation error and returns the form with error messages.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
            sample_form_data_invalid: Invalid form data scenarios from fixture
        """
        # Arrange: Get empty username scenario
        invalid_data = sample_form_data_invalid["empty_username"]
        
        # Act: Submit form with empty username
        response = test_client.post("/join_chat", data=invalid_data)
        
        # Assert: Verify form is returned with errors
        assert response.status_code == 200, "Should return form with errors, not 400"
        html_content = response.text
        
        # Check for error display
        assert "Validation Errors:" in html_content, "Error messages should be displayed"
        assert 'name="username"' in html_content, "Username field should be present for correction"
    
    def test_join_chat_whitespace_username_sanitized(
        self,
        test_client: TestClient,
        sample_form_data_invalid: dict[str, dict[str, str | int]]
    ) -> None:
        """
        Test join_chat with whitespace-only username gets sanitized and succeeds.
        
        This test verifies that the Pydantic validator properly sanitizes
        whitespace-only usernames by trimming them, and the form submission
        succeeds because the trimmed empty string passes validation.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
            sample_form_data_invalid: Invalid form data scenarios from fixture
        """
        # Arrange: Get whitespace username scenario
        invalid_data = sample_form_data_invalid["whitespace_username"]
        
        # Act: Submit form with whitespace username
        response = test_client.post("/join_chat", data=invalid_data)
        
        # Assert: Verify that whitespace gets trimmed and form succeeds
        assert response.status_code == 200, "Should return successful response"
        html_content = response.text
        
        # Check that chat page is rendered (not error page)
        assert "Chat with WebSocket" in html_content, "Should render chat page after sanitization"
        assert "Validation Errors:" not in html_content, "Should not show validation errors"
        
        # Verify that username is empty in the template (after trimming)
        assert 'data-username=""' in html_content, "Username should be empty after trimming whitespace"
    
    def test_join_chat_long_username(
        self,
        test_client: TestClient,
        sample_form_data_invalid: dict[str, dict[str, str | int]]
    ) -> None:
        """
        Test join_chat with username exceeding 50 characters returns validation error.
        
        This test verifies that the max_length validation constraint
        is properly enforced for username field.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
            sample_form_data_invalid: Invalid form data scenarios from fixture
        """
        # Arrange: Get long username scenario
        invalid_data = sample_form_data_invalid["long_username"]
        
        # Act: Submit form with long username
        response = test_client.post("/join_chat", data=invalid_data)
        
        # Assert: Verify form is returned with errors
        assert response.status_code == 200, "Should return form with errors"
        html_content = response.text
        
        # Check for error display
        assert "Validation Errors:" in html_content, "Error messages should be displayed"
    
    def test_join_chat_zero_room_id(
        self,
        test_client: TestClient,
        sample_form_data_invalid: dict[str, dict[str, str | int]]
    ) -> None:
        """
        Test join_chat with room_id = 0 returns validation error.
        
        This test verifies that the gt=0 validation constraint
        is properly enforced for room_id field.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
            sample_form_data_invalid: Invalid form data scenarios from fixture
        """
        # Arrange: Get zero room_id scenario
        invalid_data = sample_form_data_invalid["zero_room_id"]
        
        # Act: Submit form with zero room_id
        response = test_client.post("/join_chat", data=invalid_data)
        
        # Assert: Verify form is returned with errors
        assert response.status_code == 200, "Should return form with errors"
        html_content = response.text
        
        # Check for error display
        assert "Validation Errors:" in html_content, "Error messages should be displayed"
    
    def test_join_chat_negative_room_id(
        self,
        test_client: TestClient,
        sample_form_data_invalid: dict[str, dict[str, str | int]]
    ) -> None:
        """
        Test join_chat with negative room_id returns validation error.
        
        This test verifies that negative room_id values are properly
        rejected by the validation system.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
            sample_form_data_invalid: Invalid form data scenarios from fixture
        """
        # Arrange: Get negative room_id scenario
        invalid_data = sample_form_data_invalid["negative_room_id"]
        
        # Act: Submit form with negative room_id
        response = test_client.post("/join_chat", data=invalid_data)
        
        # Assert: Verify form is returned with errors
        assert response.status_code == 200, "Should return form with errors"
        html_content = response.text
        
        # Check for error display
        assert "Validation Errors:" in html_content, "Error messages should be displayed"
    
    def test_join_chat_returns_home_with_errors(
        self,
        test_client: TestClient,
        sample_form_data_invalid: dict[str, dict[str, str | int]]
    ) -> None:
        """
        Test that validation errors return home page with error display.
        
        This test verifies that when validation fails, the user is returned
        to the home page (home.html template) with error messages displayed,
        not redirected to the chat interface.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
            sample_form_data_invalid: Invalid form data scenarios from fixture
        """
        # Arrange: Get any invalid data scenario
        invalid_data = sample_form_data_invalid["empty_username"]
        
        # Act: Submit invalid form data
        response = test_client.post("/join_chat", data=invalid_data)
        
        # Assert: Verify home page is returned with errors
        assert response.status_code == 200, "Should return form with errors"
        html_content = response.text
        
        # Check for home page elements (not chat page)
        assert "Welcome to chat" in html_content, "Should return home page"
        assert "Enter your name:" in html_content, "Should show form fields"
        assert "Validation Errors:" in html_content, "Should display error messages"
        assert "Chat with WebSocket" not in html_content, "Should not show chat interface"
    
    def test_join_chat_preserves_form_data(
        self,
        test_client: TestClient,
        sample_form_data_invalid: dict[str, dict[str, str | int]]
    ) -> None:
        """
        Test that form data is preserved when validation errors occur.
        
        This test verifies that when validation fails, the user's input
        is preserved in the form fields, providing a better user experience
        by not forcing them to re-enter all data.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
            sample_form_data_invalid: Invalid form data scenarios from fixture
        """
        # Arrange: Get invalid data with valid username but invalid room_id
        invalid_data = sample_form_data_invalid["zero_room_id"]
        expected_username = invalid_data["username"]
        
        # Act: Submit invalid form data
        response = test_client.post("/join_chat", data=invalid_data)
        
        # Assert: Verify form data is preserved
        assert response.status_code == 200, "Should return form with errors"
        html_content = response.text
        
        # Check that username is preserved in the form
        assert f'value="{expected_username}"' in html_content, "Username should be preserved in form"
    
    def test_join_chat_displays_error_messages(
        self,
        test_client: TestClient,
        sample_form_data_invalid: dict[str, dict[str, str | int]]
    ) -> None:
        """
        Test that validation error messages are properly displayed.
        
        This test verifies that when validation fails, clear and helpful
        error messages are displayed to the user, guiding them to correct
        their input.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
            sample_form_data_invalid: Invalid form data scenarios from fixture
        """
        # Arrange: Get invalid data scenario
        invalid_data = sample_form_data_invalid["empty_username"]
        
        # Act: Submit invalid form data
        response = test_client.post("/join_chat", data=invalid_data)
        
        # Assert: Verify error messages are displayed
        assert response.status_code == 200, "Should return form with errors"
        html_content = response.text
        
        # Check for error message structure
        assert "Validation Errors:" in html_content, "Error header should be present"
        assert "<ul" in html_content, "Error list should be present"
        assert "<li>" in html_content, "Individual error items should be present"


class TestTemplateContext:
    """Test cases for template context and data passing."""
    
    def test_join_chat_context_has_required_fields(
        self,
        test_client: TestClient,
        sample_form_data_valid: dict[str, str | int]
    ) -> None:
        """
        Test that successful join_chat provides all required template context.
        
        This test verifies that when form submission is successful, all
        necessary data is passed to the template context for proper
        chat interface rendering.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
            sample_form_data_valid: Valid form data from fixture
        """
        # Arrange: Valid form data is provided by fixture
        
        # Act: Submit valid form data
        response = test_client.post("/join_chat", data=sample_form_data_valid)
        
        # Assert: Verify all required context fields are present
        assert response.status_code == 200, "Response should be successful"
        html_content = response.text
        
        # Check for all required template variables
        assert 'data-room-id=' in html_content, "Room ID should be in template context"
        assert 'data-username=' in html_content, "Username should be in template context"
        assert 'data-user-id=' in html_content, "User ID should be in template context"
    
    def test_join_chat_error_context_structure(
        self,
        test_client: TestClient,
        sample_form_data_invalid: dict[str, dict[str, str | int]]
    ) -> None:
        """
        Test that error context has proper structure for form re-rendering.
        
        This test verifies that when validation errors occur, the template
        context includes all necessary data for re-rendering the form
        with preserved user input and error messages.
        
        Args:
            test_client: FastAPI TestClient instance for HTTP testing
            sample_form_data_invalid: Invalid form data scenarios from fixture
        """
        # Arrange: Get invalid data scenario
        invalid_data = sample_form_data_invalid["empty_username"]
        
        # Act: Submit invalid form data
        response = test_client.post("/join_chat", data=invalid_data)
        
        # Assert: Verify error context structure
        assert response.status_code == 200, "Should return form with errors"
        html_content = response.text
        
        # Check for error context elements
        assert "Validation Errors:" in html_content, "Error messages should be in context"
        assert 'name="username"' in html_content, "Form fields should be present"
        assert 'name="room_id"' in html_content, "Form fields should be present"
