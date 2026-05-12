import * as https from 'https';
import { Finding } from '../../domain/model/Finding';
import { AiAction, AiTriggerOrigin, IAiMetricsData } from '../../domain/model/metrics/IAiMetricsData';
import { METRICS_AI_DATA_UPLOAD_URL } from '../../application/appService/Constants';
import { ScanConfigurationService } from '../config/ScanConfigurationService';

export class AiMetricsService {
    private static readonly REQUEST_TIMEOUT = 10000;

    /**
     * Tracks an AI action triggered from a webview or code action.
     * Fire-and-forget: errors are swallowed so they never affect the user flow.
     */
    public static track(
        action: AiAction,
        finding: Finding,
        triggerOrigin: AiTriggerOrigin
    ): void {
        const payload: IAiMetricsData = {
            action,
            source_type: finding.getModule() || 'unknown',
            finding_priority: finding.getEffectiveSeverity() || 'unknown',
            finding_tool: finding.getTool() || 'unknown',
            trigger_origin: triggerOrigin,
            action_date: new Date().toLocaleString()
        };

        AiMetricsService.upload(payload).catch(() => {
            // Metrics upload failure must never surface to the user
        });
    }

    /**
     * Tracks an AI action triggered from a code action (diagnostic context).
     * Use when a Finding object is not available.
     */
    public static trackFromDiagnostic(
        action: AiAction,
        triggerOrigin: AiTriggerOrigin
    ): void {
        const payload: IAiMetricsData = {
            action,
            source_type: 'unknown',
            finding_priority: 'unknown',
            finding_tool: 'unknown',
            trigger_origin: triggerOrigin,
            action_date: new Date().toLocaleString()
        };

        AiMetricsService.upload(payload).catch(() => {
            // Metrics upload failure must never surface to the user
        });
    }

    private static async upload(payload: IAiMetricsData): Promise<void> {
        return new Promise((resolve, reject) => {
            const url = new URL(METRICS_AI_DATA_UPLOAD_URL);
            const jsonPayload = JSON.stringify(payload);
            const debugMode = ScanConfigurationService.getDebugMode();

            if (debugMode) {
                console.log('[DevSecOps AI Metrics] POST', METRICS_AI_DATA_UPLOAD_URL);
                console.log('[DevSecOps AI Metrics] Payload:', JSON.stringify(payload, null, 2));
            }

            const request = https.request(
                {
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
                },
                (response) => {
                    response.resume();
                    if (response.statusCode && response.statusCode >= 200 && response.statusCode < 300) {
                        if (debugMode) {
                            console.log(`[DevSecOps AI Metrics] Response: ${response.statusCode} OK`);
                        }
                        resolve();
                    } else {
                        if (debugMode) {
                            console.log(`[DevSecOps AI Metrics] Response: ${response.statusCode} ERROR`);
                        }
                        reject(new Error(`AI metrics upload failed with status ${response.statusCode}`));
                    }
                }
            );

            request.on('error', reject);
            request.on('timeout', () => {
                request.destroy();
                reject(new Error(`AI metrics upload timed out`));
            });

            request.write(jsonPayload);
            request.end();
        });
    }
}
