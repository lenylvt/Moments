import requests

# Function to send HTTP request with emoji in the title

def send_verse(title):
    # Encode the title properly to handle emoji characters
    encoded_title = title.encode('utf-8')
    headers = {'Title': encoded_title}
    response = requests.get('http://example.com', headers=headers)
    return response.text

# Example usage
send_verse('Hello World 🌍')