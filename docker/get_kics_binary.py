import requests
import sys
import os
import base64


def download_artifact(organization, project, artifact_name, token, pipeline_id):
    try:
        token_b64 = base64.b64encode(f":{token}".encode()).decode()
        headers = {
            "Authorization": f"Basic {token_b64}"
        }

        url_build_id = f"https://dev.azure.com/{organization}/{project}/_apis/pipelines/{pipeline_id}/runs?api-version=7.1"
        print("[INFO] Fetching builds from:", url_build_id)
        builds_response = requests.get(url_build_id, headers=headers)
        print(f"[INFO] Builds response status: {builds_response.status_code}")

        if builds_response.status_code != 200:
            print(f"[ERROR] Unexpected status {builds_response.status_code} fetching builds.")
            print(f"[ERROR] Response body: {builds_response.text[:2000]}")
            return None

        try:
            builds = builds_response.json()
        except Exception as json_err:
            print(f"[ERROR] Failed to parse builds response as JSON: {json_err}")
            print(f"[ERROR] Raw response body: {builds_response.text[:2000]}")
            return None

        build_id = next((build['id'] for build in builds['value'] if build['result'] == 'succeeded'), None)
        print(f"[INFO] Latest successful build_id: {build_id}")

        if not build_id:
            print("[ERROR] No successful build found in pipeline runs.")
            available = [(b.get('id'), b.get('result')) for b in builds.get('value', [])]
            print(f"[INFO] Available runs (id, result): {available}")
            return None

        url_artifact = f"https://dev.azure.com/{organization}/{project}/_apis/build/builds/{build_id}/artifacts?artifactName={artifact_name}&api-version=7.1"
        print("[INFO] Fetching artifact from:", url_artifact)
        artifact_response = requests.get(url_artifact, headers=headers)
        print(f"[INFO] Artifact response status: {artifact_response.status_code}")

        if artifact_response.status_code != 200:
            print(f"[ERROR] Unexpected status {artifact_response.status_code} fetching artifact.")
            print(f"[ERROR] Response body: {artifact_response.text[:2000]}")
            return None

        try:
            artifact = artifact_response.json()
        except Exception as json_err:
            print(f"[ERROR] Failed to parse artifact response as JSON: {json_err}")
            print(f"[ERROR] Raw response body: {artifact_response.text[:2000]}")
            return None

        artifact_download_url = artifact['resource']['downloadUrl']
        print(f"[INFO] Downloading artifact from: {artifact_download_url}")

        response = requests.get(artifact_download_url, headers=headers, stream=True)
        print(f"[INFO] Download response status: {response.status_code}")
        if response.status_code != 200:
            print(f"[ERROR] Failed to download artifact. Status: {response.status_code}")
            print(f"[ERROR] Response body: {response.text[:2000]}")
            return None

        os.makedirs("./kics_binary", exist_ok=True)
        file_path = os.path.join("./kics_binary", f"{artifact_name}.zip")
        with open(file_path, "wb") as file_stream:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file_stream.write(chunk)

        print(f"[INFO] Artifact downloaded to: {file_path}")
        return file_path
    except Exception as error:
        print(f"[ERROR] Unexpected error downloading artifact: {error}")
        return None

def extrac_artifact(artifact_path):
    import zipfile
    try:
        print(f"[INFO] Extracting artifact: {artifact_path}")
        with zipfile.ZipFile(artifact_path, 'r') as zip_ref:
            zip_ref.extractall("./kics_binary")
        print(f"[INFO] Artifact extracted to: ./kics_binary")
    except zipfile.BadZipFile as e:
        print(f"[ERROR] Bad zip file — the downloaded artifact may be corrupted or not a zip: {e}")
        with open(artifact_path, 'rb') as f:
            print(f"[ERROR] First 200 bytes of file: {f.read(200)}")
        
# Example usage
# organization = "your-organization"
# project = "your-project"
# artifact_name = "artifact_name"
# pipeline_id = "pipeline_id"
# token = "your-personal-access-token"

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python get_kics_binary.py <organization> <project> <artifact_name> <pipeline_id> <token>")
        sys.exit(1)

    organization = sys.argv[1]
    project = sys.argv[2]
    artifact_name = sys.argv[3]
    token = sys.argv[4]
    pipeline_id = sys.argv[5]
    
    
    file_path = download_artifact(organization, project, artifact_name, token, pipeline_id)
    if file_path and os.path.exists(file_path):
        extrac_artifact(file_path)
    else:
        print("No se pudo descargar el artefacto, no se puede extraer.")