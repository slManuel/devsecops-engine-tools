import { IacScanner } from "../infrastructure/scanners/IacScanner";
import { IacScanUseCase } from "../domain/usecase/IacScanUseCase";
import { RestClient } from "../infrastructure/clients/RestClient";
import { ImageScanner } from "../infrastructure/scanners/ImageScanner";
import { ImageScanUseCase } from "../domain/usecase/ImageScanUseCase";
import { DependenciesScanUseCase } from "../domain/usecase/DependenciesScanUseCase";
import { DependenciesScanner } from "../infrastructure/scanners/DependenciesScanner";
import ContainerEngineManager from "../infrastructure/helper/ContainerEngineManager";
import { ScanConfiguration } from "../domain/model/ScanConfiguration";

interface IResult {
    name: string;
    last_updated: string;
}
interface IContainerApiResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: IResult[];
}

export async function iacScanRequest(): Promise<IacScanUseCase> {
    const containerEnginePath = ContainerEngineManager.getContainerEnginePath();
    const containerImageVersion = await getLatestContainerImageVersion();
    const iacScanUseCase = new IacScanUseCase(new IacScanner(), new RestClient(), containerImageVersion, containerEnginePath);
    return iacScanUseCase;
}

export async function imageScanRequest(): Promise<ImageScanUseCase>{
    const containerEnginePath = ContainerEngineManager.getContainerEnginePath();
    const containerImageVersion = await getLatestContainerImageVersion();
    const imageScanUseCase = new ImageScanUseCase(new ImageScanner(), containerImageVersion, containerEnginePath);
    return imageScanUseCase;
}

export async function dependenciesScanRequest(): Promise<DependenciesScanUseCase> {
    const containerEnginePath = ContainerEngineManager.getContainerEnginePath();
    const containerImageVersion = await getLatestContainerImageVersion();
    const dependenciesScanUseCase = new DependenciesScanUseCase(new DependenciesScanner(), containerImageVersion, containerEnginePath);
    return dependenciesScanUseCase;
}

async function getLatestContainerImageVersion(repository: string = 'bancolombia/devsecops-engine-tools'): Promise<string> {
    const config = new ScanConfiguration();
    const configuredVersion = config.getContainerImageVersion();
    
    if (configuredVersion && configuredVersion.trim() !== '') {
        return configuredVersion;
    }

    const restClient = new RestClient();
    const apiUrl = `https://hub.docker.com/v2/repositories/${repository}/tags?page_size=100`;
    
    try {
        const data = await restClient.get(apiUrl) as IContainerApiResponse;
        
        if (data && data.results && data.results.length > 0) {
            const sortedTags = data.results.sort((a: IResult, b: IResult) => {
                return new Date(b.last_updated).getTime() - new Date(a.last_updated).getTime();
            });
            const latestVersion = sortedTags[0].name;
            
            config.refresh();
            const reloadedVersion = config.getContainerImageVersion();
            
            if (reloadedVersion && reloadedVersion.trim() !== '') {
                return reloadedVersion;
            }

            try {
                await config.setContainerImageVersion(latestVersion);
            } catch (saveError) {
                console.warn(`Could not save version to settings: ${saveError instanceof Error ? saveError.message : String(saveError)}. Version will be used for this session only.`);
            }
            
            return latestVersion;
        }
        
        throw new Error(`No tags found for repository '${repository}'. Please verify the repository exists and is accessible, or configure a specific version in VS Code settings (imageVersion).`);
    } catch (error) {
        console.error('Error fetching container image version from Docker Hub:', error);
        throw new Error(
            `Failed to determine container image version. Please configure a specific version in VS Code settings (imageVersion) or ensure Docker Hub API is accessible. Original error: ${error instanceof Error ? error.message : String(error)}`
        );
    }
}