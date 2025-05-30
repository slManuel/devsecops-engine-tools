export default class DockerPathDetector { 

    static getDockerPath(): string {
        const dockerPath = process.env.DOCKER_PATH || "/usr/bin/docker";
        return dockerPath;
    }
    
}