# DevSecOps Loading Animator

A comprehensive loading animation utility for VS Code extensions that provides various animated loading indicators for output channels.

## Features

- 🌀 **Multiple Animation Types**: Spinner, dots, progress bars, ASCII art, and pulse animations
- 🎨 **Branded Design**: Custom DevSecOps branding with security-themed icons
- ⏱️ **Elapsed Time**: Optional elapsed time display
- 📊 **Progress Tracking**: Built-in progress bar functionality
- 🔄 **Phase Management**: Show different phases of operations
- ❌ **Error Handling**: Styled error display
- 🎪 **Easy Integration**: Simple API for quick implementation

## Usage

### Basic Loading Animation

```typescript
import { LoadingAnimator } from "../infraestructure/helper/LoadingAnimator";

const outputChannel = vscode.window.createOutputChannel("My Output");
const animator = new LoadingAnimator(outputChannel);

// Start a spinner animation
animator.start({
  message: "Processing scan results",
  animationType: 'spinner',
  showElapsedTime: true
});

// Update the message
animator.updateMessage("Analyzing security findings...");

// Show progress
animator.showProgress(50, "Half way done!");

// Stop the animation
animator.stop();
```

### Quick Start Functions

```typescript
import { createLoadingSpinner, createLoadingDots, createASCIILoader } from "../infraestructure/helper/LoadingAnimator";

// Create different types of loaders quickly
const spinner = createLoadingSpinner(outputChannel, "Scanning...");
const dots = createLoadingDots(outputChannel, "Processing...");
const ascii = createASCIILoader(outputChannel);

// Don't forget to stop them
spinner.stop();
```

### Async Operations with Loading

```typescript
import { LoadingAnimator } from "../infraestructure/helper/LoadingAnimator";

const result = await LoadingAnimator.withLoading(
  outputChannel,
  async (animator) => {
    animator.showPhase('initialization', 'Setting up scanner');
    await setupScanner();
    
    animator.showPhase('scanning', 'Running security scan');
    const findings = await runScan();
    
    animator.showPhase('completed', `Found ${findings.length} issues`);
    return findings;
  },
  {
    message: "Running security analysis",
    animationType: 'spinner'
  }
);
```

## Animation Types

1. **Spinner** (`'spinner'`): Rotating characters ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏
2. **Dots** (`'dots'`): Moving dots ⠁⠂⠄⡀⢀⠠⠐⠈
3. **Progress** (`'progress'`): Animated progress bar ▁▂▃▄▅▆▇█
4. **Pulse** (`'pulse'`): Colored hearts 💙💚💛🧡❤️💜
5. **ASCII** (`'ascii'`): Branded DevSecOps messages with security icons

## Configuration Options

```typescript
interface LoadingOptions {
  message?: string;                    // Custom loading message
  animationType?: 'spinner' | 'dots' | 'progress' | 'ascii' | 'pulse';
  interval?: number;                   // Animation frame interval (ms)
  showElapsedTime?: boolean;          // Show elapsed time
  customFrames?: string[];            // Custom animation frames
}
```

## Phase Management

```typescript
// Show different phases of your operation
animator.showPhase('initialization', 'Setting up security scanners');
animator.showPhase('scanning', 'Analyzing code for vulnerabilities');
animator.showPhase('processing', 'Processing scan results');
animator.showPhase('completed', 'Security scan finished');
```

## Error Handling

```typescript
try {
  // Your scanning operation
  const result = await performScan();
} catch (error) {
  animator.showError(`Scan failed: ${error.message}`);
}
```

## Examples in the Codebase

- **IaC Scan**: Uses spinner animation with phase tracking
- **Dependencies Scan**: Uses dots animation for package analysis
- **Image Scan**: Uses ASCII art animation for container scanning

## Demo Commands

The extension includes demo commands to showcase all animation types:

- `DevSecOps: Demo Loading Animations` - Interactive demo of all animation types
- `DevSecOps: Demo Async Loading` - Example of loading with async operations

## Best Practices

1. **Choose appropriate animations**: Use ASCII art for longer operations, spinners for quick tasks
2. **Update phases**: Keep users informed about progress with phase updates
3. **Handle errors gracefully**: Always use `showError()` for error states
4. **Show completion**: Use the completion banner to indicate success
5. **Elapsed time**: Enable elapsed time for operations that might take a while

## Security Theming

The LoadingAnimator includes security-themed icons and messages:
- 🛡️ Security shield for protection
- 🔍 Magnifying glass for scanning
- 🔒 Lock icons for security
- 🐳 Docker whale for container scanning
- 📊 Charts for analysis

This creates a cohesive visual experience that aligns with the DevSecOps mission.
