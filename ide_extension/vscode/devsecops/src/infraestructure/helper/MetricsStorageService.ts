import * as https from 'https';
import { IMetricsData } from "../../domain/model/metrics/IMetricsData";
import { METRICS_DATA_UPLOAD_URL } from '../../application/appService/Constants';

/**
 * Service responsible for uploading metrics data to remote server
 */
export class MetricsStorageService {

    private static readonly REQUEST_TIMEOUT = 30000;

    /**
     * Upload metrics data to server
     * @param metricsData
     * @returns 
     */
    public static async storeMetricsData(metricsData: IMetricsData): Promise<void> {
        try {
            await this.uploadMetricsDataToServer(metricsData);
        } catch (error) {
            throw new Error(`Failed to upload metrics: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    /**
     * Upload metrics data to remote service via the backend API
     * @param metricsData 
     */
    private static async uploadMetricsDataToServer(metricsData: IMetricsData): Promise<void> {
        return new Promise((resolve, reject) => {
            const url = new URL(METRICS_DATA_UPLOAD_URL);
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
                        resolve();
                    } else {
                        const error = new Error(`Remote upload failed with status ${response.statusCode}: ${responseData}`);
                        reject(error);
                    }
                });
            });

            request.on('error', (error) => {
                reject(new Error(`Network error during remote upload: ${error.message}`));
            });

            request.on('timeout', () => {
                request.destroy();
                reject(new Error(`Remote upload timed out after ${this.REQUEST_TIMEOUT}ms`));
            });

            request.write(jsonPayload);
            request.end();
        });
    }

}