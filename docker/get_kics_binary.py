import requests
import sys
import os


def download_artifact(organization, project, artifact_name, token, pipeline_id):
    try:
        headers = {
            "Authorization": f"Basic {token}"
        }

        url_build_id = f"https://dev.azure.com/{organization}/{project}/_apis/pipelines/{pipeline_id}/runs?api-version=7.1"
        print("url_build_id", url_build_id)
        builds_response = requests.get(url_build_id, headers=headers)
        print("builds_response", builds_response)
        builds = builds_response.json()
        build_id = next((build['id'] for build in builds['value'] if build['result'] == 'succeeded'), None)
        print("build_id", build_id)

        if not build_id:
            print("No se encontró un build exitoso.")
            return None

        url_artifact = f"https://dev.azure.com/{organization}/{project}/_apis/build/builds/{build_id}/artifacts?artifactName={artifact_name}&api-version=7.1"
        print("url_artifact", url_artifact)
        artifact_response = requests.get(url_artifact, headers=headers)
        print("artifact_response", artifact_response)
        artifact = artifact_response.json()
        artifact_download_url = artifact['resource']['downloadUrl']

        response = requests.get(artifact_download_url, headers=headers, stream=True)
        os.makedirs("./kics_binary", exist_ok=True)
        file_path = os.path.join("./kics_binary", f"{artifact_name}.zip")
        with open(file_path, "wb") as file_stream:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file_stream.write(chunk)

        print(f"Artifact descargado en: {file_path}")
        return file_path
    except Exception as error:
        print(f"Error downloading artifact: {error}")
        return None

def extrac_artifact(artifact_path):
    import zipfile
    try:
        with zipfile.ZipFile(artifact_path, 'r') as zip_ref:
            zip_ref.extractall("./kics_binary")
        print(f"Artifact extracted to: ./kics_binary")
    except zipfile.BadZipFile as e:
        print(f"Error extracting artifact: {e}")
        
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