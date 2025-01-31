import requests
import os
from pprint import pprint
import time
from typing import List, Optional

# API base URL
BASE_URL = "http://localhost:8000"

DOCUMENT_CATEGORIES = [
    "Technical Documentation",
    "Business Strategy",
    "Research Paper",
    "Educational Material",
    "Project Planning",
]


class APITester:
    def __init__(self):
        self.token = None
        self.headers = {}

    def update_auth_header(self, token):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}

    def test_register_user(self, email, password):
        print("\n=== Testing User Registration ===")
        response = requests.post(
            f"{BASE_URL}/users/register", json={"email": email, "password": password}
        )
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        return response.json()

    def test_login_user(self, email, password):
        print("\n=== Testing User Login ===")
        response = requests.post(
            f"{BASE_URL}/users/login", json={"email": email, "password": password}
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        pprint(data)
        if "access_token" in data:
            self.update_auth_header(data["access_token"])
        return data

    def test_get_current_user(self):
        print("\n=== Testing Get Current User ===")
        response = requests.get(f"{BASE_URL}/users/me", headers=self.headers)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        return response.json()

    def test_create_categories(self, names):
        print("\n=== Testing Create Category ===")
        for name in names:
            try:
                response = requests.post(
                    f"{BASE_URL}/categories/", headers=self.headers, json={"name": name}
                )
                print(f"Status Code: {response.status_code}")
                pprint(response.json())
            except Exception as e:
                print(f"Error creating category {name}: {str(e)}")

    def test_get_categories(self):
        print("\n=== Testing Get Categories ===")
        response = requests.get(f"{BASE_URL}/categories/", headers=self.headers)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        return response.json()

    def test_upload_file(self, file_path):
        print("\n=== Testing Upload File ===")
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{BASE_URL}/files/",
                headers=self.headers,
                files=files,
            )
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        return response.json()

    def test_get_files(self):
        print("\n=== Testing Get Files ===")
        response = requests.get(f"{BASE_URL}/files/", headers=self.headers)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        return response.json()

    # def test_get_file(self, file_id):
    #     print("\n=== Testing Get File ===")
    #     response = requests.get(f"{BASE_URL}/files/{file_id}", headers=self.headers)
    #     print(f"Status Code: {response.status_code}")
    #     # Save response content to file

    #     if response.status_code == 200:
    #         with open(f"test_download_{file_id}.pdf", "wb") as f:
    #             f.write(response.content)
    #     return response.content

    def test_get_highlighted_file(self, file_id):
        print("\n=== Testing Get Highlighted File ===")
        response = requests.get(
            f"{BASE_URL}/files/{file_id}/highlighted", headers=self.headers
        )
        print(f"Status Code: {response.status_code}")
        return response.content

    def test_delete_file(self, file_id):
        print("\n=== Testing Delete File ===")
        response = requests.delete(f"{BASE_URL}/files/{file_id}", headers=self.headers)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        return response.json()

    def test_delete_category(self, category_id):
        print("\n=== Testing Delete Category ===")
        response = requests.delete(
            f"{BASE_URL}/categories/{category_id}", headers=self.headers
        )
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        return response.json()

    def test_delete_user(self):
        print("\n=== Testing Delete User ===")
        response = requests.delete(f"{BASE_URL}/users/me", headers=self.headers)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        return response.json()

    def test_get_news(self, page: int = 1, categories: Optional[List[str]] = None):
        print("\n=== Testing Get News ===")
        url = f"{BASE_URL}/news/?page={page}"
        if categories:
            for category in categories:
                url += f"&categories={category}"

        response = requests.get(url, headers=self.headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Page: {data['page']}")
            print(f"Total Pages: {data['total_pages']}")
            print(f"Has More: {data['has_more']}")
            print(f"Number of articles: {len(data['articles'])}")
            # Print first article title as sample
            if data["articles"]:
                print(f"Sample article title: {data['articles'][0]['title']}")
        else:
            print("Error response:", response.text)
        return response.json()

    def test_reset_news_history(self):
        print("\n=== Testing Reset News History ===")
        response = requests.post(f"{BASE_URL}/news/reset-history", headers=self.headers)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        return response.json()


def main():
    # Create test instance
    tester = APITester()

    # Test user registration and login
    email = f"tester_{time.time()}@example.com"
    password = "testpassword123"

    try:
        # Register new user
        tester.test_register_user(email, password)

        # Login
        tester.test_login_user(email, password)

        # Test news endpoints
        print("\n=== Testing News Endpoints ===")

        # Test getting news without categories
        print("\nGetting news without categories:")
        tester.test_get_news(page=1)

        # Test getting news with categories
        print("\nGetting news with categories:")
        test_categories = ["Politics", "Technology", "Health"]
        tester.test_get_news(page=1, categories=test_categories)

        # Test pagination
        print("\nTesting pagination:")
        page_1 = tester.test_get_news(page=1)
        if page_1["has_more"]:
            print("\nGetting page 2:")
            tester.test_get_news(page=2)

        # Test reset history
        print("\nTesting reset history:")
        tester.test_reset_news_history()

        # Verify we get fresh articles after reset
        print("\nGetting news after reset:")
        tester.test_get_news(page=1)

        # Get user info
        tester.test_get_current_user()

        # # Create categories
        # tester.test_create_categories(DOCUMENT_CATEGORIES)

        # # Get categories
        # tester.test_get_categories()

        # # Upload test file
        # # Create a test file
        # test_file_path = "test.docx"
        # # with open(test_file_path, "w") as f:
        # #     f.write("This is a test file content.")

        # try:
        #     # Upload file
        #     file = tester.test_upload_file(test_file_path)

        #     # Get files
        #     tester.test_get_files()

        #     # Get file content
        #     # tester.test_get_file(file["id"])

        #     # Wait for 10 seconds
        #     time.sleep(20)

        #     # Get file content
        #     # tester.test_get_file(file["id"])
        #     tester.test_get_files()

        #     # Try to get highlighted file (might fail if processing isn't complete)
        #     try:
        #         tester.test_get_highlighted_file(file["id"])
        #     except Exception as e:
        #         print(f"Note: Highlighted file not ready yet: {str(e)}")

        #     # # Delete file
        #     # tester.test_delete_file(file["id"])

        # finally:
        #     pass

        #     # Cleanup test file
        #     if os.path.exists(test_file_path):
        #         os.remove(test_file_path)

        # Delete category
        # tester.test_delete_category(category["id"])

        # Delete user
        # tester.test_delete_user()

    except Exception as e:
        print(f"Error during testing: {str(e)}")


if __name__ == "__main__":
    main()
