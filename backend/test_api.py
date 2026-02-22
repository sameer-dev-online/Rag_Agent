"""
Quick test script for RAG API endpoints.
Run this after starting the server to verify functionality.
"""
import httpx
import asyncio
import sys


async def test_rag_api():
    """Test RAG API endpoints."""
    base_url = "http://localhost:8000/api/v1"
    api_key = "your-api-key"  # Replace with your actual API key
    headers = {"X-API-Key": api_key}

    print("=" * 60)
    print("RAG API Test Suite")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test 1: Health Check
            print("\n[Test 1] Health Check...")
            resp = await client.get(f"{base_url}/health")
            if resp.status_code == 200:
                print("✓ Health check passed")
                print(f"  Response: {resp.json()}")
            else:
                print(f"✗ Health check failed: {resp.status_code}")
                return

            # Test 2: Upload Document
            print("\n[Test 2] Upload Document...")
            print("  Note: Create a test.txt file in the current directory")

            try:
                with open("test.txt", "r") as f:
                    content = f.read()
                    if not content:
                        print("  Creating test file with sample content...")
                        with open("test.txt", "w") as wf:
                            wf.write("This is a test document.\n\nIt contains information about testing the RAG system.\n\nThe system should be able to retrieve this information when queried.")
            except FileNotFoundError:
                print("  Creating test.txt file...")
                with open("test.txt", "w") as f:
                    f.write("This is a test document.\n\nIt contains information about testing the RAG system.\n\nThe system should be able to retrieve this information when queried.")

            with open("test.txt", "rb") as f:
                files = {"file": ("test.txt", f, "text/plain")}
                data = {"user_id": "test_user", "title": "Test Document"}
                resp = await client.post(
                    f"{base_url}/documents",
                    headers=headers,
                    files=files,
                    data=data
                )

            if resp.status_code == 201:
                print("✓ Document upload passed")
                result = resp.json()
                print(f"  Document ID: {result['data']['document_id']}")
                print(f"  Chunks created: {result['data']['num_chunks']}")
            else:
                print(f"✗ Document upload failed: {resp.status_code}")
                print(f"  Response: {resp.json()}")
                return

            # Wait a moment for embeddings to be processed
            print("\n  Waiting for embeddings to be indexed...")
            await asyncio.sleep(2)

            # Test 3: Chat without conversation_id (creates new conversation)
            print("\n[Test 3] Chat - New Conversation...")
            chat_data = {
                "message": "What is in the test document?",
                "user_id": "test_user"
            }
            resp = await client.post(
                f"{base_url}/chat",
                headers=headers,
                json=chat_data
            )

            if resp.status_code == 200:
                print("✓ Chat (new conversation) passed")
                result = resp.json()
                conversation_id = result['data']['conversation_id']
                print(f"  Conversation ID: {conversation_id}")
                print(f"  Assistant response: {result['data']['assistant_message']['content'][:100]}...")
                print(f"  Contexts retrieved: {len(result['data']['retrieved_contexts'])}")
            else:
                print(f"✗ Chat failed: {resp.status_code}")
                print(f"  Response: {resp.json()}")
                return

            # Test 4: Chat with existing conversation_id
            print("\n[Test 4] Chat - Continue Conversation...")
            chat_data = {
                "message": "Can you tell me more?",
                "user_id": "test_user",
                "conversation_id": conversation_id
            }
            resp = await client.post(
                f"{base_url}/chat",
                headers=headers,
                json=chat_data
            )

            if resp.status_code == 200:
                print("✓ Chat (continue conversation) passed")
                result = resp.json()
                print(f"  Assistant response: {result['data']['assistant_message']['content'][:100]}...")
            else:
                print(f"✗ Chat continuation failed: {resp.status_code}")
                print(f"  Response: {resp.json()}")

            # Test 5: Get Conversation
            print("\n[Test 5] Get Conversation...")
            resp = await client.get(
                f"{base_url}/conversations/{conversation_id}",
                headers=headers,
                params={"user_id": "test_user"}
            )

            if resp.status_code == 200:
                print("✓ Get conversation passed")
                result = resp.json()
                print(f"  Messages count: {len(result['data']['messages'])}")
                print(f"  Conversation title: {result['data']['conversation']['title']}")
            else:
                print(f"✗ Get conversation failed: {resp.status_code}")
                print(f"  Response: {resp.json()}")

            print("\n" + "=" * 60)
            print("All tests completed successfully!")
            print("=" * 60)

        except httpx.ConnectError:
            print("\n✗ Error: Could not connect to server")
            print("  Make sure the server is running on http://localhost:8000")
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    print("\nMake sure to:")
    print("1. Start the server: uvicorn app.main:app --reload")
    print("2. Set your API_KEY in .env file")
    print("3. Update the api_key variable in this script\n")

    asyncio.run(test_rag_api())
