import sys
import requests
import os

def download_crt(url):
    response = requests.get(url)
    if response.status_code == 200:
        filename = url.split('/')[-1]
        if not filename.endswith('.crt'):
            filename += '.crt'
        os.makedirs("./certificates", exist_ok=True)
        with open(f"./certificates/{filename}", 'wb') as f:
            f.write(response.content)
        print(f"File {filename} downloaded successfully")
    else:
        print(f"Error downloading file. Status code: {response.status_code}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Use: python get_certificates.py <url>")
        sys.exit(1)
    url = sys.argv[1]
    download_crt(url)