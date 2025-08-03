import http.client
import sys
import json

if len(sys.argv) < 4:
    print("Usage: python script.py <bearer_token_file> <start_date> <end_date>")
    sys.exit(1)

bearer_token_file = sys.argv[1]
start_date = sys.argv[2]
end_date = sys.argv[3]

with open(bearer_token_file, "r") as f:
    bearer_token = f.read().strip()

conn = http.client.HTTPSConnection("api.abnormalplatform.com")

# payload = "{\r\n  \"pageSize\"=100\r\n  \"pageNumber\": 1,\r\n  \"nextPageNumber\": 2\r\n  \"attackVector\"=Attachment\r\n}"
payload = ''

headers = {
    'Authorization': f'Bearer {bearer_token}',
    'Content-Type': 'text/plain'
}

# Format the dates properly in the request
query = f"/v1/threats?filter=receivedTime%20gte%20{start_date}T00%3A00%3A00Z%20lte%20{end_date}T23%3A59%3A59Z&pageSize=2000&pageNumber=1&source=All&attackVector=Attachment"

conn.request("GET", query, payload, headers)

res = conn.getresponse()
data = res.read()

# Try to parse the JSON response for threats but if the key doesn't exist then display the alternative output
try:
    threats = json.loads(data.decode("utf-8"))["threats"]
except KeyError:
    print(data.decode("utf-8"))
    sys.exit(1)

# Loop over each threat ID and request the attachments
for i, threat in enumerate(threats, start=1):
    threat_id = threat["threatId"]
    conn.request("GET", f"/v1/threats/{threat_id}/attachments", headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    print(f"Fetching attachment name for threats in specified date range {i}/{len(threats)}", end='\r', file=sys.stderr, flush=True)
