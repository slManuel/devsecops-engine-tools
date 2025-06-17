import { execSync } from "child_process";

export default class DockerPathDetector { 

    static getDockerPath(): string {
        if (process.env.DOCKER_PATH) {
            return process.env.DOCKER_PATH;
        }

        try {
            const whichResult = execSync("which docker", { encoding: "utf-8" }).trim();
            if (whichResult) {
                return whichResult;
            }
        } catch (e) {
            // Ignore error if docker command is not found
        }
        try {
            const whichResult = execSync("which podman", { encoding: "utf-8" }).trim();
            if (whichResult) {
                return whichResult;
            }
        } catch (e) {
            // Ignore error if podman command is not found
        }

        return "/usr/local/bin/docker";
    }
    
}