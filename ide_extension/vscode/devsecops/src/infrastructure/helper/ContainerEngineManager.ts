import { exec, execSync } from "child_process";
import { promisify } from "util";
import * as path from "path";
import * as os from "os";
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

  /**
   * Check if running on Windows
   */
  private static isWindows(): boolean {
    return process.platform === 'win32';
  }

  /**
   * Get the appropriate command to find executables based on platform
   */
  private static getWhichCommand(): string {
    return this.isWindows() ? 'where' : 'which';
  }

  /**
   * Normalize a Windows path to Docker-compatible format
   * Converts C:\Users\... to /c/Users/... for Docker on Windows
   */
  static normalizePathForDocker(filePath: string): string {
    if (!this.isWindows()) {
      return filePath;
    }

    // Convert Windows path to Unix-style for Docker
    // C:\Users\... -> /c/Users/...
    let normalized = filePath.replace(/\\/g, '/');
    
    // Handle drive letter (C: -> /c)
    if (normalized.match(/^[a-zA-Z]:/)) {
      const driveLetter = normalized.charAt(0).toLowerCase();
      normalized = `/${driveLetter}${normalized.substring(2)}`;
    }

    return normalized;
  }

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

    const whichCommand = this.getWhichCommand();

    try {
      const dockerPath = execSync(`${whichCommand} docker`, { encoding: "utf-8" }).trim();
      if (dockerPath) {
        // On Windows, 'where' returns multiple paths, take the first one
        const firstPath = dockerPath.split('\n')[0].trim();
        this.detectedEngine = {
          path: this.isWindows() ? 'docker' : firstPath,
          type: 'docker'
        };
        return this.detectedEngine;
      }
    } catch (e) {
      // Ignore error if docker command is not found
    }

    try {
      const podmanPath = execSync(`${whichCommand} podman`, { encoding: "utf-8" }).trim();
      if (podmanPath) {
        // On Windows, 'where' returns multiple paths, take the first one
        const firstPath = podmanPath.split('\n')[0].trim();
        this.detectedEngine = {
          path: this.isWindows() ? 'podman' : firstPath,
          type: 'podman'
        };
        return this.detectedEngine;
      }
    } catch (e) {
      // Ignore error if podman command is not found
    }

    // Default fallback
    this.detectedEngine = {
      path: this.isWindows() ? 'docker' : '/usr/local/bin/docker',
      type: 'docker'
    };
    return this.detectedEngine;
  }

  static async getContainerImages(): Promise<Array<{name: string, tag: string, fullName: string}>> {
    const engine = this.detectContainerEngine();
    
    try {
      const pathSeparator = this.isWindows() ? ';' : ':';
      const engineDir = this.isWindows() ? path.dirname(engine.path) : engine.path.replace(/\/(docker|podman)$/, "");
      const { stdout } = await execAsync(`${engine.path} images --format "table {{.Repository}}\\t{{.Tag}}\\t{{.ID}}"`, {
        env: {
          ...process.env,
          PATH: process.env.PATH + pathSeparator + engineDir,
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
      const pathSeparator = this.isWindows() ? ';' : ':';
      const engineDir = this.isWindows() ? path.dirname(engine.path) : engine.path.replace(/\/(docker|podman)$/, "");
      const { stdout } = await execAsync(`${engine.path} version --format "{{.Client.Version}}"`, {
        env: {
          ...process.env,
          PATH: process.env.PATH + pathSeparator + engineDir,
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
      const pathSeparator = this.isWindows() ? ';' : ':';
      const engineDir = this.isWindows() ? path.dirname(engine.path) : engine.path.replace(/\/(docker|podman)$/, "");
      const { stdout, stderr } = await execAsync(fullCommand, {
        env: {
          ...process.env,
          PATH: process.env.PATH + pathSeparator + engineDir,
        }
      });
      
      return { stdout, stderr };
    } catch (error: any) {
      throw new Error(`Container engine command failed: ${error.message}`);
    }
  }

  static async exportImageToTar(imageName: string, outputPath: string): Promise<boolean> {
    try {
      const normalizedPath = this.normalizePathForDocker(outputPath);
      await this.executeCommand(`save -o "${normalizedPath}" "${imageName}"`);
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
        // Remove entire temp directory
        if (fs.existsSync(dirPath)) {
          fs.rmSync(dirPath, { recursive: true, force: true });
        }
        this.tempDirectoryPath = null;
      } else {
        // Remove single file
        if (fs.existsSync(filePath)) {
          fs.unlinkSync(filePath);
        }
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
    const tempDir = this.ensureDevsecopsDirectory();
    const safeImageName = imageName.replace(/[^a-zA-Z0-9.-]/g, '_');
    const timestamp = Date.now();
    return path.join(tempDir, `devsecops_image_${safeImageName}_${timestamp}.tar`);
  }
}
