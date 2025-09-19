import * as fs from 'fs';
import * as path from 'path';
import { IMetricsData } from "../../domain/model/metrics/IMetricsData";

/**
 * Service responsible for storing metrics data to JSON files
 */
export class MetricsStorageService {

    /**
     * Store metrics data to a JSON file in the workspace root
     * @param metricsData The structured metrics data to store
     * @returns The path to the created JSON file
     */
    public static async storeMetrics(metricsData: IMetricsData): Promise<string> {
        try {
            // Generate filename with timestamp and tool name (using same format as scan results)
            const timestamp = new Date().toLocaleString().replace(/[\/,:\s]/g, '-');
            const fileName = `devsecops-metrics-${metricsData.tool}-${timestamp}.json`;

            // Store in workspace root
            const filePath = path.join(process.cwd(), fileName);

            // Write metrics data to JSON file
            const jsonContent = JSON.stringify(metricsData, null, 2);
            await fs.promises.writeFile(filePath, jsonContent, 'utf8');

            return filePath;
        } catch (error) {
            throw new Error(`Failed to store metrics: ${error instanceof Error ? error.message : String(error)}`);
        }
    }
}