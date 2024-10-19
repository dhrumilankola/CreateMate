import requests
import time
import json

# Base URL of your API
BASE_URL = "http://localhost:8000"

def submit_user_input():
    url = f"{BASE_URL}/user-input"
    payload = {
        "area_of_interest": "Technology",
        "content_type": "Event Updates",
        "keywords": ["Ethereum"],
        "post_frequency": 3
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("User input submitted successfully.")
        print("Response:", response.json())
    except requests.exceptions.RequestException as e:
        print("Error submitting user input:", e)

def get_state():
    url = f"{BASE_URL}/state"
    try:
        response = requests.get(url)
        response.raise_for_status()
        state = response.json()
        print("Current state:")
        print(json.dumps(state, indent=4))
        return state
    except requests.exceptions.RequestException as e:
        print("Error retrieving state:", e)
        return None

def submit_feedback(liked=True, comments=""):
    url = f"{BASE_URL}/feedback"
    payload = {
        "liked": liked,
        "comments": comments
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Feedback submitted successfully.")
        print("Response:", response.json())
    except requests.exceptions.RequestException as e:
        print("Error submitting feedback:", e)

def main():
    print("Submitting user input...")
    submit_user_input()

    # Wait for the system to process the user input
    print("Waiting for the system to process the user input...")
    time.sleep(5)  # Adjust the sleep time as needed

    print("\nRetrieving current state...")
    state = get_state()

    if state and state.get("generated_content"):
        print("\nInitial generated content received.")
    else:
        print("\nNo generated content found. Waiting for content generation...")
        time.sleep(5)  # Wait for content to be generated
        state = get_state()

    if state and state.get("generated_content"):
        print("\nInitial generated content:")
        for content in state["generated_content"]:
            print(f"Day: {content['day']}")
            print(f"Topic: {content['topic']}")
            print(f"Content:\n{content['content']}\n")
    else:
        print("\nFailed to retrieve generated content.")
        return

    # Simulate user feedback
    print("Submitting feedback...")
    submit_feedback(liked=True, comments="Great initial post!")

    # Wait for the system to process the feedback
    print("Waiting for the system to process the feedback and generate remaining content...")
    time.sleep(10)  # Adjust the sleep time as needed

    print("\nRetrieving updated state...")
    state = get_state()

    if state and state.get("generated_content"):
        print("\nAll generated content:")
        for content in state["generated_content"]:
            print(f"Day: {content['day']}")
            print(f"Topic: {content['topic']}")
            print(f"Content:\n{content['content']}\n")
    else:
        print("\nFailed to retrieve updated generated content.")

if __name__ == "__main__":
    main()
