import * as vscode from "vscode";

/**
 * Classification model types
 */
export type ClassificationModel = "severity" | "priority";

/**
 * Gets the current classification model from VS Code configuration
 */
export function getClassificationModel(): ClassificationModel {
  const config = vscode.workspace.getConfiguration("devsecops.general");
  const model = config.get<string>("classificationModel", "severity");
  return (model === "priority" ? "priority" : "severity") as ClassificationModel;
}

/**
 * Gets the effective severity based on the current classification model
 * @param severity - The original severity value from the finding
 * @param priority - The priority value from the finding
 * @returns The effective severity to use for display, filtering, and sorting
 */
export function getEffectiveSeverity(severity: string, priority: string): string {
  const model = getClassificationModel();
  
  if (model === "priority" && priority) {
    return priority.toLowerCase().trim();
  }
  
  return severity.toLowerCase().trim();
}

