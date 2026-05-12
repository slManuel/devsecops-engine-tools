import * as vscode from 'vscode';
import { AiMetricsService } from '../infrastructure/services/AiMetricsService';
import { DiagnosticService } from '../tree/DiagnosticService';

export function registerCopilotCommands(context: vscode.ExtensionContext): void {
  const fixCommand = vscode.commands.registerCommand(
    'devsecops.fixWithCopilot',
    async (document: vscode.TextDocument, diagnostic: vscode.Diagnostic) => {

      const editor = await vscode.window.showTextDocument(document);
      editor.selection = new vscode.Selection(
        diagnostic.range.start,
        diagnostic.range.end
      );
      editor.revealRange(diagnostic.range);

      const issueId = diagnostic.code?.toString() || '';
      let issueDescription = diagnostic.message;

      const finding = DiagnosticService.getFindingForDiagnostic(document.uri, issueId);
      if (finding) {
        AiMetricsService.track('fix_with_copilot', finding, 'code_action');
      } else {
        AiMetricsService.trackFromDiagnostic('fix_with_copilot', 'code_action');
      }

      // Extract validation rule from diagnostic data if available
      const validationRule = diagnostic.source === 'devsecops' && diagnostic.relatedInformation?.length 
        ? diagnostic.relatedInformation[0]?.message 
        : '';

      if(validationRule) {
        issueDescription += validationRule;
      }
      
      const prompt = validationRule
        ? `Fix this security issue: ${issueId} - ${issueDescription}. Validation Rule: ${validationRule}. Please provide a secure solution that addresses the specific validation rule violation.`
        : `Fix this security issue: ${issueId} - ${issueDescription}`;

      try {
        // Try inline fix chat first (works when editor is focused)
        await vscode.commands.executeCommand('github.copilot.chat.fix');
        setTimeout(() => {
          void vscode.env.clipboard.writeText(prompt);
          void vscode.commands.executeCommand('editor.action.clipboardPasteAction');
        }, 500);
      } catch {
        try {
          // Fallback: open chat panel and paste prompt
          const chatInput = validationRule
            ? `/fix This code has a security issue: ${issueId} - ${issueDescription}. Validation Rule: ${validationRule}`
            : `/fix This code has a security issue: ${issueId} - ${issueDescription}`;
          void vscode.env.clipboard.writeText(chatInput);
          await vscode.commands.executeCommand('github.copilot.chat.explain.palette');
        } catch {
          void vscode.window.showWarningMessage(
            'Could not open Copilot Chat. Make sure GitHub Copilot Chat extension is installed and signed in.',
            'Open Extensions'
          ).then(choice => {
            if (choice === 'Open Extensions') {
              void vscode.commands.executeCommand('workbench.extensions.search', '@id:GitHub.copilot-chat');
            }
          });
        }
      }
    }
  );

  const explainCommand = vscode.commands.registerCommand(
    'devsecops.explainWithCopilot',
    async (document: vscode.TextDocument, diagnostic: vscode.Diagnostic) => {
      const editor = await vscode.window.showTextDocument(document);
      editor.selection = new vscode.Selection(
        diagnostic.range.start,
        diagnostic.range.end
      );
      editor.revealRange(diagnostic.range);
    
      const issueId = diagnostic.code?.toString() || '';
      let issueDescription = diagnostic.message;
      
      const finding = DiagnosticService.getFindingForDiagnostic(document.uri, issueId);
      if (finding) {
        AiMetricsService.track('explain_with_copilot', finding, 'code_action');
      } else {
        AiMetricsService.trackFromDiagnostic('explain_with_copilot', 'code_action');
      }

      // Extract validation rule from diagnostic data if available
      const validationRule = diagnostic.source === 'devsecops' && diagnostic.relatedInformation?.length 
        ? diagnostic.relatedInformation[0]?.message 
        : '';

      if(validationRule) {
        issueDescription += validationRule;
      }
      
      const copilotChatExtension = vscode.extensions.getExtension('GitHub.copilot-chat');
      
      if (copilotChatExtension && copilotChatExtension.isActive) {
        try {
          const chatInput = validationRule
            ? '/explain This code has a security issue: ' + 
              `${issueId} - ${issueDescription}. Validation Rule: ${validationRule}. Can you explain why this is a problem ` +
              'and how to fix it securely according to this validation rule?'
            : '/explain This code has a security issue: ' + 
              `${issueId} - ${issueDescription}. Can you explain why this is a problem ` +
              'and how to fix it securely?';

          void vscode.env.clipboard.writeText(chatInput);
          await vscode.commands.executeCommand('github.copilot.chat.explain.palette');
        } catch (error) {
          void vscode.window.showErrorMessage(`Error using Copilot Chat: ${String(error)}`);
        }
      } else {
        void vscode.window.showInformationMessage('GitHub Copilot Chat extension is required for this feature');
      }
    }
  );

  context.subscriptions.push(fixCommand, explainCommand);
}