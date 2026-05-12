import * as path from "path";
import * as fs from "fs";
import * as os from "os";
import archiver from "archiver";

export interface ICompressionResult {
  success: boolean;
  filePath?: string;
  error?: string;
}

/**
 * FileCompressionHelper - Cross-platform file compression utility
 * 
 * Provides methods to compress files and directories into zip format
 * using the archiver library (pure Node.js, no shell commands).
 */
export default class FileCompressionHelper {
  // Directories to exclude from compression
  private static readonly EXCLUDE_DIRS = [
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
    '.venv',
    '.env',
    '.gradle'
  ];

  // File extensions to exclude from compression
  private static readonly EXCLUDE_FILE_EXTENSIONS = [
    '.sqlite',
    '.sqlite3',
    '.db'
  ];

  /**
   * Compress a file or directory to ZIP format using archiver (cross-platform, pure Node.js)
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

      await this.compressWithArchiver(sourcePath, finalOutputPath);

      // Verify output file was created
      if (!fs.existsSync(finalOutputPath)) {
        return {
          success: false,
          error: 'Compression completed but output file was not created'
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
   * Compress using archiver library (pure Node.js, works on Windows, Linux and macOS)
   */
  private static compressWithArchiver(sourcePath: string, outputPath: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const output = fs.createWriteStream(outputPath);
      const archive = archiver('zip', { zlib: { level: 6 } });

      output.on('close', resolve);
      archive.on('error', reject);
      archive.pipe(output);

      const stat = fs.statSync(sourcePath);

      if (stat.isDirectory()) {
        // Walk the directory manually to skip excluded dirs BEFORE reading them,
        // avoiding EACCES errors on directories like .gradle that we never need to scan.
        this.addDirectoryToArchive(archive, sourcePath, '');
      } else {
        archive.file(sourcePath, { name: path.basename(sourcePath) });
      }

      archive.finalize();
    });
  }

  /**
   * Recursively walks a directory and adds non-excluded entries to the archive.
   * Excluded directories are never read (avoids EACCES on inaccessible dirs).
   */
  private static addDirectoryToArchive(
    archive: archiver.Archiver,
    dirPath: string,
    archivePath: string
  ): void {
    let entries: string[];
    try {
      entries = fs.readdirSync(dirPath);
    } catch {
      // Skip directories we cannot read (permission denied, etc.)
      return;
    }

    for (const entry of entries) {
      const fullPath = path.join(dirPath, entry);
      const entryArchivePath = archivePath ? `${archivePath}/${entry}` : entry;

      let stat: fs.Stats;
      try {
        stat = fs.statSync(fullPath);
      } catch {
        continue;
      }

      if (stat.isDirectory()) {
        if (!this.EXCLUDE_DIRS.includes(entry)) {
          this.addDirectoryToArchive(archive, fullPath, entryArchivePath);
        }
      } else if (stat.isFile()) {
        if (!this.EXCLUDE_FILE_EXTENSIONS.some(ext => entry.endsWith(ext))) {
          archive.file(fullPath, { name: entryArchivePath });
        }
      }
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
