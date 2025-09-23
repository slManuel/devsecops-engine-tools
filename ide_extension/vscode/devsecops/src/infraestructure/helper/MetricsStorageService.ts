import * as fs from 'fs';
import * as path from 'path';
import * as https from 'https';
import { IMetricsData } from "../../domain/model/metrics/IMetricsData";
import { OutputChannel } from 'vscode';

/**
 * Service responsible for storing metrics data to JSON files and uploading to AWS S3
 */
export class MetricsStorageService {
    
    private static readonly S3_UPLOAD_URL = 'https://devsecops-dev.apps.ambientesbc.com/engine-backend/metrics/api/uploadMetrics?folder=devsecops_ide_extension';
    private static readonly REQUEST_TIMEOUT = 30000; // 30 seconds

    /**
     * Store metrics data locally and upload to S3
     * @param metricsData
     * @param outputChannel 
     * @returns 
     */
    public static async storeMetrics(metricsData: IMetricsData, outputChannel?: OutputChannel): Promise<string> {
        try {
            const timestamp = new Date().toLocaleString().replace(/[\/,:\s]/g, '-');
            const fileName = `devsecops-metrics-${metricsData.tool}-${timestamp}.json`;

            const filePath = path.join(process.cwd(), fileName);

            const jsonContent = JSON.stringify(metricsData, null, 2);
            await fs.promises.writeFile(filePath, jsonContent, 'utf8');

            this.uploadToS3(metricsData, outputChannel).catch((error: Error) => {
                if (outputChannel) {
                    outputChannel.appendLine(`⚠️  Failed to upload metrics to S3: ${error.message}`);
                }
            });

            return filePath;
        } catch (error) {
            throw new Error(`Failed to store metrics: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Upload metrics data to AWS S3 via the backend API
     * @param metricsData 
     * @param outputChannel 
     */
    private static async uploadToS3(metricsData: IMetricsData, outputChannel?: OutputChannel): Promise<void> {
        return new Promise((resolve, reject) => {
            const url = new URL(this.S3_UPLOAD_URL);
            const jsonPayload = JSON.stringify(metricsData);

            const options = {
                hostname: url.hostname,
                port: url.port || 443,
                path: url.pathname + url.search,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Content-Length': Buffer.byteLength(jsonPayload),
                    'User-Agent': 'DevSecOps-VSCode-Extension'
                },
                timeout: this.REQUEST_TIMEOUT
            };

            const request = https.request(options, (response) => {
                let responseData = '';

                response.on('data', (chunk) => {
                    responseData += chunk;
                });

                response.on('end', () => {
                    if (response.statusCode && response.statusCode >= 200 && response.statusCode < 300) {
                        if (outputChannel) {
                            outputChannel.appendLine('✅ Metrics successfully uploaded to S3');
                        }
                        resolve();
                    } else {
                        const error = new Error(`S3 upload failed with status ${response.statusCode}: ${responseData}`);
                        reject(error);
                    }
                });
            });

            request.on('error', (error) => {
                reject(new Error(`Network error during S3 upload: ${error.message}`));
            });

            request.on('timeout', () => {
                request.destroy();
                reject(new Error(`S3 upload timed out after ${this.REQUEST_TIMEOUT}ms`));
            });

            request.write(jsonPayload);
            request.end();
        });
    }

}