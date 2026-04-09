import requests
import json
from dotenv import load_dotenv
import os
import time
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
API_URL = os.getenv("OPEN_ROUTER_API_URL")
MODELS = [m.strip() for m in os.getenv("TEST_MODELS", "").split(",") if m.strip()]

# Create output directory if it doesn't exist
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def open_source_models():
    # Try each model until one works
    for model in MODELS:
        print(f"\nTrying model: {model}")
        try:
            result = run_open_source_model(model)
            if result:
                print(f"\nSuccessfully tested with: {model}")
                return
        except Exception as e:
            print(f"Error with {model}: {e}")
            continue

    print("\nAll models failed. Please try again later.")

def run_open_source_model(MODEL, max_retries=3):
    output_data = {
        "model": MODEL,
        "timestamp": datetime.now().isoformat(),
        "first_call": None,
        "second_call": None
    }
    
    # First API call with reasoning
    print("=" * 60)
    print(f"FIRST API CALL: Asking about 'strawberry' (Model: {MODEL})")
    print("=" * 60)

    # Retry logic for rate limiting
    for attempt in range(max_retries):
        response = requests.post(
            url=API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": "How many r's are in the word 'strawberry'?"
                    }
                ],
                "reasoning": {"enabled": True}
            })
        )

        # Check for rate limiting
        if response.status_code == 429:
            wait_time = 5 * (attempt + 1)  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait_time)
            continue

        # Check for other errors
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False

        break  # Success, exit retry loop
    else:
        print(f"Failed after {max_retries} retries due to rate limiting")
        return False

    # Extract the assistant message with reasoning_details
    result = response.json()
    response = result['choices'][0]['message']

    print("\nResponse:")
    print(response.get('content'))

    if response.get('reasoning_details'):
        print("\n--- Reasoning Details ---")
        print(response.get('reasoning_details'))
        print("--- End Reasoning Details ---")
    
    output_data["first_call"] = {
        "content": response.get('content'),
        "reasoning_details": response.get('reasoning_details')
    }

    # Preserve the assistant message with reasoning_details
    messages = [
        {"role": "user", "content": "How many r's are in the word 'strawberry'?"},
        {
            "role": "assistant",
            "content": response.get('content'),
            "reasoning_details": response.get('reasoning_details')  # Pass back unmodified
        },
        {"role": "user", "content": "Are you sure? Think carefully."}
    ]

    # Second API call - model continues reasoning from where it left off
    print("\n" + "=" * 60)
    print("SECOND API CALL: Asking model to reconsider")
    print("=" * 60)

    # Retry logic for rate limiting
    for attempt in range(max_retries):
        response2 = requests.post(
            url=API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": MODEL,
                "messages": messages,  # Includes preserved reasoning_details
                "reasoning": {"enabled": True}
            })
        )

        # Check for rate limiting
        if response2.status_code == 429:
            wait_time = 5 * (attempt + 1)  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait_time)
            continue

        # Check for other errors
        if response2.status_code != 200:
            print(f"Error: {response2.status_code}")
            print(response2.text)
            return False

        break  # Success, exit retry loop
    else:
        print(f"Failed after {max_retries} retries due to rate limiting")
        return False

    # Extract and display second response
    result2 = response2.json()
    response2_message = result2['choices'][0]['message']

    print("\nResponse:")
    print(response2_message.get('content'))

    if response2_message.get('reasoning_details'):
        print("\n--- Reasoning Details ---")
        print(response2_message.get('reasoning_details'))
        print("--- End Reasoning Details ---")
    
    output_data["second_call"] = {
        "content": response2_message.get('content'),
        "reasoning_details": response2_message.get('reasoning_details')
    }

    # Save output to file with lowercase naming convention
    model_name_safe = MODEL.replace("/", "-").replace(":", "-").lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{model_name_safe}_{timestamp}.json"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print(f"Results saved to: {output_path}")
    print("=" * 60)
    
    # Auto-format the results if format-results.py exists
    format_results_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "format-results.py")
    if os.path.exists(format_results_script):
        print("\nFormatting results...")
        import subprocess
        subprocess.run(["python", format_results_script], check=False)
    
    return True

if __name__ == "__main__":
    open_source_models()
