import { exec } from "child_process";
import { promisify } from "util";
import * as path from "path";
import * as fs from "fs";
import * as os from "os";

const execAsync = promisify(exec);

export interface ICompressionResult {
  success: boolean;
  filePath?: string;
  error?: string;
}

/**
 * FileCompressionHelper - Cross-platform file compression utility
 * 
 * Provides methods to compress files and directories into zip format
 * compatible with Windows, Linux, and macOS.
 */
export default class FileCompressionHelper {
  // Directories to exclude from compression
  private static readonly EXCLUDE_PATTERNS = [
    'node_modules',
    '.git',
    'dist',
    'build',
    '.vscode',
    'coverage',
    '.next',
    '.nuxt',
    'out',
    '__pycache__',
    '.pytest_cache',
    'venv',
    '.env'
  ];

  private static isWindows(): boolean {
    return process.platform === 'win32';
  }

  /**
   * Compress a file or directory to ZIP format
   * 
   * @param sourcePath - Path to file or directory to compress
   * @param outputPath - Optional output path for the ZIP file
   * @returns ICompressionResult with success status and file path
   */
  static async compressToZip(sourcePath: string, outputPath?: string): Promise<ICompressionResult> {
    try {
      // Validate source exists
      if (!fs.existsSync(sourcePath)) {
        return {
          success: false,
          error: `Source path does not exist: ${sourcePath}`
        };
      }

      // Determine output path
      const finalOutputPath = outputPath || this.generateOutputPath(sourcePath);
      
      // Ensure output directory exists
      const outputDir = path.dirname(finalOutputPath);
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }

      // Delete existing output file if it exists
      if (fs.existsSync(finalOutputPath)) {
        fs.unlinkSync(finalOutputPath);
      }

      // Compress using platform-specific command
      if (this.isWindows()) {
        await this.compressWindows(sourcePath, finalOutputPath);
      } else {
        await this.compressUnix(sourcePath, finalOutputPath);
      }

      // Verify output file was created
      if (!fs.existsSync(finalOutputPath)) {
        return {
          success: false,
          error: 'Compression command completed but output file was not created'
        };
      }

      return {
        success: true,
        filePath: finalOutputPath
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      return {
        success: false,
        error: `Compression failed: ${errorMessage}`
      };
    }
  }

  /**
   * Compress using Windows PowerShell Compress-Archive
   */
  private static async compressWindows(sourcePath: string, outputPath: string): Promise<void> {
    // On Windows, use tar (available on Windows 10+) which supports exclusions
    try {
      await this.compressWithTar(sourcePath, outputPath);
    } catch (error) {
      // Fallback to PowerShell if tar fails
      // Note: PowerShell Compress-Archive doesn't support exclusions easily,
      // so this may include node_modules. Consider this a last resort.
      const psCommand = `Compress-Archive -Path "${sourcePath}" -DestinationPath "${outputPath}" -Force`;
      await execAsync(`powershell -Command "${psCommand}"`, {
        windowsHide: true
      });
    }
  }

  /**
   * Compress using Unix zip command
   */
  private static async compressUnix(sourcePath: string, outputPath: string): Promise<void> {
    const stat = fs.statSync(sourcePath);
    const sourceDir = stat.isDirectory() ? sourcePath : path.dirname(sourcePath);
    const sourceName = stat.isDirectory() ? '.' : path.basename(sourcePath);

    // Build exclusion patterns for zip command
    // Include both root-level and subdirectory patterns
    const exclusions = this.EXCLUDE_PATTERNS.flatMap(pattern => 
      [`-x "${pattern}/*"`, `-x "*/${pattern}/*"`]
    ).join(' ');

    // Use zip command with recursive flag and exclusions
    const zipCommand = `cd "${sourceDir}" && zip -r "${outputPath}" "${sourceName}" ${exclusions} -q`;
    
    try {
      await execAsync(zipCommand);
    } catch (error) {
      // Fallback: try using tar
      await this.compressWithTar(sourcePath, outputPath);
    }
  }

  /**
   * Fallback compression using tar (available on all platforms with recent Node.js/OS versions)
   */
  private static async compressWithTar(sourcePath: string, outputPath: string): Promise<void> {
    const stat = fs.statSync(sourcePath);
    const sourceDir = stat.isDirectory() ? sourcePath : path.dirname(sourcePath);
    const sourceName = stat.isDirectory() ? '.' : path.basename(sourcePath);

    // Build exclusion patterns for tar command
    // Exclude both root-level and subdirectory matches
    const exclusions = this.EXCLUDE_PATTERNS.flatMap(pattern => 
      [`--exclude="${pattern}"`, `--exclude="*/${pattern}"`]
    ).join(' ');

    // Create a .tar.gz instead of .zip as fallback
    const tarOutputPath = outputPath.replace(/\.zip$/, '.tar.gz');
    
    const tarCommand = this.isWindows()
      ? `tar -czf "${tarOutputPath}" ${exclusions} -C "${sourceDir}" "${sourceName}"`
      : `cd "${sourceDir}" && tar -czf "${tarOutputPath}" ${exclusions} "${sourceName}"`;

    await execAsync(tarCommand);
    
    // If we created a .tar.gz but expected .zip, rename it
    if (tarOutputPath !== outputPath) {
      fs.renameSync(tarOutputPath, outputPath);
    }
  }

  /**
   * Generate output path for compressed file
   */
  private static generateOutputPath(sourcePath: string): string {
    const tempDir = os.tmpdir();
    const timestamp = Date.now();
    const sourceName = path.basename(sourcePath);
    const fileName = `devsecops_${sourceName}_${timestamp}.zip`;
    
    return path.join(tempDir, fileName);
  }

  /**
   * Cleanup temporary compressed files
   */
  static cleanup(filePath: string): void {
    try {
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
      }
    } catch (error) {
      console.error(`Failed to cleanup compressed file ${filePath}:`, error);
    }
  }

  /**
   * Get file size in bytes
   */
  static getFileSize(filePath: string): number {
    try {
      const stats = fs.statSync(filePath);
      return stats.size;
    } catch (error) {
      return 0;
    }
  }

  /**
   * Format file size for display
   */
  static formatFileSize(bytes: number): string {
    if (bytes === 0) {
      return '0 Bytes';
    }
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return `${Math.round((bytes / Math.pow(k, i)) * 100) / 100} ${sizes[i]}`;
  }
}
