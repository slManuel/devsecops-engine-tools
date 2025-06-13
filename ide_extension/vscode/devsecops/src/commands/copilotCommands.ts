import * as vscode from 'vscode';

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
      
      // Extract validation rule from diagnostic data if available
      const validationRule = diagnostic.source === 'devsecops' && diagnostic.relatedInformation?.length 
        ? diagnostic.relatedInformation[0]?.message 
        : '';

      if(validationRule) {
        issueDescription += validationRule;
      }
      
      const copilotExtension = vscode.extensions.getExtension('GitHub.copilot');
      const copilotChatExtension = vscode.extensions.getExtension('GitHub.copilot-chat');
      
      if (copilotExtension && copilotExtension.isActive) {
        try {
          await vscode.commands
            .executeCommand("github.copilot.chat.fix +when:!editorReadonly && !github.copilot.interactiveSession.disabled");
          setTimeout(() => {
            // Enhanced prompt with validation rule information
            const prompt = validationRule 
              ? `Fix this security issue: ${issueId} - ${issueDescription}. Validation Rule: ${validationRule}. Please provide a secure solution that addresses the specific validation rule violation.`
              : `Fix this security issue: ${issueId} - ${issueDescription}`;
            
            void vscode.env.clipboard.writeText(prompt);
            void vscode.commands.executeCommand('editor.action.clipboardPasteAction');
          }, 500);
        } catch (error) {
          if (copilotChatExtension && copilotChatExtension.isActive) {
            setTimeout(() => {
              const chatInput = validationRule
              ? `/fix This code has a security issue: ${issueId} - ${issueDescription}. Validation Rule: ${validationRule}`
              : `/fix This code has a security issue: ${issueId} - ${issueDescription}`;
              
              void vscode.env.clipboard.writeText(chatInput);
              void vscode.commands.executeCommand('editor.action.clipboardPasteAction');
            }, 500);
            await vscode.commands.executeCommand('github.copilot.chat.explain.palette');
          } else {
            void vscode.window.showInformationMessage('Please install GitHub Copilot and GitHub Copilot Chat extensions to use this feature');
          }
        }
      } else {
        void vscode.window.showInformationMessage('GitHub Copilot extension is required for this feature');
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
          await vscode.commands.executeCommand('github.copilot.chat.focus');
          
          setTimeout(() => {
            const chatInput = validationRule
              ? '/explain This code has a security issue: ' + 
                `${issueId} - ${issueDescription}. Validation Rule: ${validationRule}. Can you explain why this is a problem ` +
                'and how to fix it securely according to this validation rule?'
              : '/explain This code has a security issue: ' + 
                `${issueId} - ${issueDescription}. Can you explain why this is a problem ` +
                'and how to fix it securely?';
            
            void vscode.env.clipboard.writeText(chatInput);
            void vscode.commands.executeCommand('editor.action.clipboardPasteAction');
          }, 500);
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