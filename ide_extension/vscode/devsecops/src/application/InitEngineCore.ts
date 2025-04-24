import { IacScanner } from "../infraestructure/drivenAdapter/IacScanner";
import { IacScanRequest } from "../infraestructure/entryPoint/IacScanRequest";
import { IacScanUseCase } from "../domain/usecase/IacScanUseCase";
import { RestClient } from "../infraestructure/drivenAdapter/RestClient";
import { ImageScanRequest } from "../infraestructure/entryPoint/ImageScanRequest";
import { ImageScanner } from "../infraestructure/drivenAdapter/ImageScanner";
import { ImageScanUseCase } from "../domain/usecase/ImageScanUseCase";

export function iacScanRequest(): IacScanRequest {
    const iacScanUseCase = new IacScanUseCase(new IacScanner(), new RestClient());
    return new IacScanRequest(iacScanUseCase);
}

export async function imageScanRequest(): Promise<ImageScanRequest>{
    const dockerImageVersion = await getLatestDockerImageVersion();
    const imageScanUseCase = new ImageScanUseCase(new ImageScanner(), dockerImageVersion);
    return new ImageScanRequest(imageScanUseCase);
}


async function getLatestDockerImageVersion(repository: string = 'bancolombia/devsecops-engine-tools'): Promise<string> {
    const restClient = new RestClient();
    const apiUrl = `https://hub.docker.com/v2/repositories/${repository}/tags?page_size=100`;
    
    try {
        const data = await restClient.get(apiUrl);
        
        if (data && data.results && data.results.length > 0) {
            const sortedTags = data.results.sort((a: any, b: any) => {
                return new Date(b.last_updated).getTime() - new Date(a.last_updated).getTime();
            });
            return sortedTags[0].name;
        }
        
        throw new Error('No tags found for the repository');
    } catch (error) {
        console.error('Error fetching Docker image version:', error);
        throw error;
    }
}