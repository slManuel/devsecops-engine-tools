import { exec, execSync } from "child_process";
import { promisify } from "util";
import * as path from "path";
import * as os from "os";
import * as fs from "fs";
import * as fs from "fs";

const execAsync = promisify(exec);

export interface ContainerEngine {
  path: string;
  type: 'docker' | 'podman';
  version?: string;
}

export default class ContainerEngineManager {
  private static detectedEngine: ContainerEngine | null = null;
  private static tempDirectoryPath: string | null = null;

  static getContainerEnginePath(): string {
    const engine = this.detectContainerEngine();
    return engine.path;
  }

  static detectContainerEngine(): ContainerEngine {
    if (this.detectedEngine) {
      return this.detectedEngine;
    }

    // Check for environment variable override
    if (process.env.DOCKER_PATH) {
      this.detectedEngine = {
        path: process.env.DOCKER_PATH,
        type: process.env.DOCKER_PATH.includes('podman') ? 'podman' : 'docker'
      };
      return this.detectedEngine;
    }

    try {
      const dockerPath = execSync("which docker", { encoding: "utf-8" }).trim();
      if (dockerPath) {
        this.detectedEngine = {
          path: dockerPath,
          type: 'docker'
        };
        return this.detectedEngine;
      }
    } catch (e) {
      // Ignore error if docker command is not found
    }

    try {
      const podmanPath = execSync("which podman", { encoding: "utf-8" }).trim();
      if (podmanPath) {
        this.detectedEngine = {
          path: podmanPath,
          type: 'podman'
        };
        return this.detectedEngine;
      }
    } catch (e) {
      // Ignore error if podman command is not found
    }

    this.detectedEngine = {
      path: "/usr/local/bin/docker",
      type: 'docker'
    };
    return this.detectedEngine;
  }

  static async getContainerImages(): Promise<Array<{name: string, tag: string, fullName: string}>> {
    const engine = this.detectContainerEngine();
    
    try {
      const { stdout } = await execAsync(`${engine.path} images --format "table {{.Repository}}\\t{{.Tag}}\\t{{.ID}}"`, {
        env: {
          ...process.env,
          PATH: process.env.PATH + ':' + engine.path.replace(/\/(docker|podman)$/, ""),
        }
      });

      const lines = stdout.trim().split('\n');
      const images: Array<{name: string, tag: string, fullName: string}> = [];

      // Skip header line
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;

        const columns = line.split(/\s+/);
        if (columns.length >= 2) {
          const repository = columns[0];
          const tag = columns[1];
          
          // Skip <none> entries
          if (repository !== '<none>' && tag !== '<none>') {
            const fullName = `${repository}:${tag}`;
            images.push({
              name: repository,
              tag: tag,
              fullName: fullName
            });
          }
        }
      }

      return images;
    } catch (error) {
      console.error(`Error listing container images: ${error}`);
      return [];
    }
  }

  static async isContainerEngineAvailable(): Promise<{available: boolean, version?: string, engine?: ContainerEngine}> {
    const engine = this.detectContainerEngine();
    
    try {
      const { stdout } = await execAsync(`${engine.path} version --format "{{.Client.Version}}"`, {
        env: {
          ...process.env,
          PATH: process.env.PATH + ':' + engine.path.replace(/\/(docker|podman)$/, ""),
        }
      });

      const version = stdout.trim();
      return {
        available: true,
        version: version,
        engine: { ...engine, version: version }
      };
    } catch (error) {
      console.error(`Container engine not available: ${error}`);
      return {
        available: false,
        engine: engine
      };
    }
  }

  static getEngineType(): 'docker' | 'podman' {
    return this.detectContainerEngine().type;
  }

  static async executeCommand(command: string): Promise<{stdout: string, stderr: string}> {
    const engine = this.detectContainerEngine();
    const fullCommand = `${engine.path} ${command}`;
    
    try {
      const { stdout, stderr } = await execAsync(fullCommand, {
        env: {
          ...process.env,
          PATH: process.env.PATH + ':' + engine.path.replace(/\/(docker|podman)$/, ""),
        }
      });
      
      return { stdout, stderr };
    } catch (error: any) {
      throw new Error(`Container engine command failed: ${error.message}`);
    }
  }

  static async exportImageToTar(imageName: string, outputPath: string): Promise<boolean> {
    try {
      await this.executeCommand(`save -o "${outputPath}" "${imageName}"`);
      return true;
    } catch (error) {
      console.error(`Error exporting image ${imageName}:`, error);
      return false;
    }
  }

  static async removeFile(filePath: string): Promise<void> {
    try {
      const dirPath = path.dirname(filePath);
      const dirName = path.basename(dirPath);
      
      if (dirName.startsWith('devsecops-tmp-')) {
        await execAsync(`rm -rf "${dirPath}"`);
        this.tempDirectoryPath = null;
      } else {
        await execAsync(`rm -f "${filePath}"`);
      }
    } catch (error) {
      console.error(`Error removing file/directory ${filePath}:`, error);
    }
  }

  private static ensureDevsecopsDirectory(): string {
    if (this.tempDirectoryPath && fs.existsSync(this.tempDirectoryPath)) {
      return this.tempDirectoryPath;
    }

    const homeDir = os.homedir();
    const timestamp = Date.now();
    const processId = process.pid;
    const devsecopsDir = path.join(homeDir, `devsecops-tmp-${timestamp}-${processId}`);
    
    if (!fs.existsSync(devsecopsDir)) {
      fs.mkdirSync(devsecopsDir, { recursive: true });
    }
    
    this.tempDirectoryPath = devsecopsDir;
    return devsecopsDir;
  }

  static createTemporaryImagePath(imageName: string): string {
    const tempDir = fs.realpathSync(os.tmpdir());
    const safeImageName = imageName.replace(/[^a-zA-Z0-9.-]/g, '_');
    const timestamp = Date.now();
    // return path.join(tempDir, `devsecops_image_${safeImageName}_${timestamp}.tar`);
    return path.join(process.env.HOME!, `devsecops_image_${safeImageName}_${timestamp}.tar`);
  }
}
