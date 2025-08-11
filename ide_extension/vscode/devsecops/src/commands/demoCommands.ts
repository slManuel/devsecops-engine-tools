import * as vscode from "vscode";
import { LoadingAnimator } from "../infraestructure/helper/LoadingAnimator";
import { SimpleProgressLoader } from "../infraestructure/helper/SimpleProgressLoader";

export function registerDemoCommands(context: vscode.ExtensionContext): void {
  // Demo command to showcase different loading animations
  const demoLoadingDisposable = vscode.commands.registerCommand(
    "devsecops.demoLoading",
    async () => {
      const animationType = await vscode.window.showQuickPick([
        { label: "🌀 Spinner Animation", value: "spinner" },
        { label: "💫 Dots Animation", value: "dots" },
        { label: "📊 Progress Bar", value: "progress" },
        { label: "🎨 ASCII Art", value: "ascii" },
        { label: "💙 Pulse Animation", value: "pulse" },
        { label: "🎪 All Animations Demo", value: "all" }
      ], {
        placeHolder: "Select animation type to demo"
      });

      if (!animationType) return;

      const outputChannel = vscode.window.createOutputChannel("DevSecOps Animation Demo");
      
      if (animationType.value === "all") {
        await runAllAnimationsDemo(outputChannel);
      } else {
        await runSingleAnimationDemo(outputChannel, animationType.value as any);
      }
    }
  );

  // Demo command to test loading with async operation
  const demoAsyncLoadingDisposable = vscode.commands.registerCommand(
    "devsecops.demoAsyncLoading",
    async () => {
      const outputChannel = vscode.window.createOutputChannel("DevSecOps Async Demo");
      
      await LoadingAnimator.withLoading(
        outputChannel,
        async (animator) => {
          animator.updateMessage("🚀 Starting mock security scan...");
          await delay(2000);
          
          animator.showPhase('initialization', 'Setting up security scanners');
          await delay(1500);
          
          animator.showProgress(25, 'Scanning dependencies');
          await delay(1000);
          
          animator.showProgress(50, 'Analyzing code structure');
          await delay(1000);
          
          animator.showProgress(75, 'Checking for vulnerabilities');
          await delay(1000);
          
          animator.showProgress(100, 'Finalizing scan results');
          await delay(500);
          
          animator.showPhase('completed', 'Security scan finished successfully');
          
          return "Scan completed successfully!";
        },
        {
          message: "Running comprehensive security analysis",
          animationType: 'spinner',
          showElapsedTime: true
        }
      );
      
      vscode.window.showInformationMessage("Demo async loading completed!");
    }
  );

  // Demo command for simple progress loader
  const demoSimpleProgressDisposable = vscode.commands.registerCommand(
    "devsecops.demoSimpleProgress",
    async () => {
      const outputChannel = vscode.window.createOutputChannel("DevSecOps Simple Progress Demo");
      
      const loader = new SimpleProgressLoader(outputChannel);
      loader.start({
        message: "Infrastructure as Code scan",
        showPercentage: true,
        showElapsedTime: true
      });

      // Simulate scan phases with progress updates
      await delay(1000);
      loader.setProgress(15, "Initializing scanner");
      loader.addStatusUpdate("🚀 Setting up DevSecOps scanner");
      
      await delay(1500);
      loader.setProgress(35, "Scanning IaC files");
      loader.addStatusUpdate("🔍 Analyzing Terraform and CloudFormation files");
      
      await delay(2000);
      loader.setProgress(60, "Checking security policies");
      loader.addStatusUpdate("🛡️ Validating against security best practices");
      
      await delay(1500);
      loader.setProgress(85, "Processing findings");
      loader.addStatusUpdate("📊 Analyzing 23 potential security issues");
      
      await delay(1000);
      loader.setProgress(100, "Scan completed");
      loader.addStatusUpdate("✅ Security scan finished successfully");
      
      await delay(500);
      loader.stop();
      
      vscode.window.showInformationMessage("Simple progress demo completed!");
    }
  );

  context.subscriptions.push(demoLoadingDisposable, demoAsyncLoadingDisposable, demoSimpleProgressDisposable);
}

async function runSingleAnimationDemo(outputChannel: vscode.OutputChannel, type: 'spinner' | 'dots' | 'progress' | 'ascii' | 'pulse') {
  const animator = new LoadingAnimator(outputChannel);
  
  animator.start({
    message: `DevSecOps ${type} animation demo`,
    animationType: type,
    showElapsedTime: true
  });

  // Simulate some work
  await delay(1000);
  animator.updateMessage("🔍 Performing security analysis...");
  await delay(1000);
  animator.showPhase('scanning', 'Deep scanning in progress');
  await delay(2000);
  animator.showPhase('analysis', 'Analyzing findings');
  await delay(1500);
  animator.showPhase('completed', 'Demo completed successfully!');
  await delay(500);
  
  animator.stop();
  vscode.window.showInformationMessage(`${type} animation demo completed!`);
}

async function runAllAnimationsDemo(outputChannel: vscode.OutputChannel) {
  const animations: Array<{ name: string; type: 'spinner' | 'dots' | 'progress' | 'ascii' | 'pulse' }> = [
    { name: "Spinner", type: "spinner" },
    { name: "Dots", type: "dots" },
    { name: "Progress", type: "progress" },
    { name: "ASCII Art", type: "ascii" },
    { name: "Pulse", type: "pulse" }
  ];

  outputChannel.clear();
  outputChannel.appendLine("🎪 DevSecOps Loading Animations Showcase");
  outputChannel.appendLine("=" .repeat(50));
  outputChannel.appendLine("");

  for (const animation of animations) {
    outputChannel.appendLine(`🎬 Now showing: ${animation.name} Animation`);
    outputChannel.appendLine("-".repeat(30));
    
    const animator = new LoadingAnimator(outputChannel);
    animator.start({
      message: `${animation.name} animation showcase`,
      animationType: animation.type,
      interval: animation.type === 'ascii' ? 600 : 150
    });

    await delay(3000);
    animator.stop(false);
    
    outputChannel.appendLine("");
    outputChannel.appendLine(`✅ ${animation.name} demo completed!`);
    outputChannel.appendLine("");
    
    await delay(1000);
  }

  outputChannel.appendLine("🎉 All animations demo completed!");
  outputChannel.appendLine("Thank you for using DevSecOps Engine Tools!");
  
  vscode.window.showInformationMessage("All animations demo completed!");
}

function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
