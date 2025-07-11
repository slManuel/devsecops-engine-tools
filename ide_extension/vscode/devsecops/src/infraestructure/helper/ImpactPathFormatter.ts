type ImpactPathComponent = {
  component_id: string;
};

export type ImpactPath = ImpactPathComponent[];

type TreeNode = {
  name: string;
  children: Map<string, TreeNode>;
};

function isExternalComponent(componentId: string): boolean {
  return !componentId.includes(':unspecified') && !componentId.includes('base-repository:');
}

function buildImpactPathTree(paths: ImpactPath[]): TreeNode {
  const root: TreeNode = { name: 'ROOT', children: new Map() };

  for (const path of paths) {
    let current = root;
    for (let i = 0; i < path.length; i++) {
      const { component_id } = path[i];

      if (isExternalComponent(component_id)) {
        if (!current.children.has(component_id)) {
          current.children.set(component_id, { 
            name: component_id, 
            children: new Map()
          });
        }
        current = current.children.get(component_id)!;
      }
    }
  }

  return root;
}

function getDirectDependencies(paths: ImpactPath[]): Set<string> {
  const directDeps = new Set<string>();
  
  for (const path of paths) {
    const firstExternalDep = path.find(component => isExternalComponent(component.component_id));
    if (firstExternalDep) {
      directDeps.add(firstExternalDep.component_id);
    }
  }
  
  return directDeps;
}

function formatComponentName(componentId: string): string {
  const match = componentId.match(/gav:\/\/([^:]+):([^:]+):(.+)/);
  if (match) {
    const [, group, artifact, version] = match;
    return `${artifact} (${version})`;
  }
  return componentId;
}

function getVulnerableComponent(paths: ImpactPath[]): string {
  if (paths.length === 0) return 'Unknown';
  
  for (const path of paths) {
    for (let i = path.length - 1; i >= 0; i--) {
      if (isExternalComponent(path[i].component_id)) {
        return path[i].component_id;
      }
    }
  }
  
  return 'Unknown';
}

function formatTree(node: TreeNode, depth = 0, isLast = false, parentPrefix = '', vulnerableComponentId = ''): string {
  let output = '';

  if (node.name !== 'ROOT') {
    const isRoot = depth === 1;
    const isVulnerable = node.name === vulnerableComponentId;
    
    const prefix = isRoot ? '📦 ' : (isLast ? '└── ' : '├── ');
    const vulnerableEmoji = isVulnerable ? '🚨 ' : '';
    const connector = isRoot ? '' : parentPrefix;
    const connectorFix = isVulnerable ? connector.slice(1) : connector;
    
    const componentName = formatComponentName(node.name);
    let cssClass = isRoot ? 'root-dependency' : 'dependency-item';
    if (isVulnerable) {
      cssClass += ' vulnerable-item';
    }
    
    output += `<div class="tree-line ${cssClass}">${connectorFix}${prefix}${vulnerableEmoji}<span class="component-name">${escapeHtml(componentName)}</span></div>`;
  }

  const children = Array.from(node.children.values());
  children.forEach((child, index) => {
    const isLastChild = index === children.length - 1;
    const newPrefix = node.name === 'ROOT' ? '' : parentPrefix + (isLast ? '    ' : '│   ');
    output += formatTree(child, depth + 1, isLastChild, newPrefix, vulnerableComponentId);
  });

  return output;
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function formatImpactPathsCollapsed(impactPaths: ImpactPath[]): string {
  if (!impactPaths || impactPaths.length === 0) {
    return `
      <div class="impact-paths-container">
        <div class="no-paths-message">
          <span class="icon">⚠️</span>
          <span>No impact paths found.</span>
        </div>
      </div>
    `;
  }

  const tree = buildImpactPathTree(impactPaths);
  const vulnerableComponent = getVulnerableComponent(impactPaths);
  const directDependencies = getDirectDependencies(impactPaths);

  const styles = `
    <style>
      .impact-paths-container {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: var(--vscode-editor-background);
        color: var(--vscode-editor-foreground);
        border: 2px solid var(--vscode-panel-border);
        border-radius: 12px;
        padding: 1.5em;
        margin: 1em 0;
        max-width: 100%;
        overflow-x: auto;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        line-height: 1.6;
      }
      .vulnerability-header {
        background: linear-gradient(135deg, var(--vscode-inputValidation-warningBackground), var(--vscode-button-secondaryBackground));
        border: 2px solid var(--vscode-inputValidation-warningBorder);
        border-radius: 8px;
        padding: 1em;
        margin-bottom: 1.2em;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
      .vulnerability-title {
        color: #ffffff;
        font-weight: 600;
        font-size: 1.1em;
        margin-bottom: 0.8em;
      }
      .vulnerable-component {
        color: var(--vscode-errorForeground);
        font-weight: bold;
        font-family: var(--vscode-editor-font-family);
        background: var(--vscode-inputValidation-errorBackground);
        padding: 6px 10px;
        border-radius: 4px;
        display: inline-block;
        word-break: break-all;
        border: 1px solid var(--vscode-inputValidation-errorBorder);
      }
      .recommendations {
        background: linear-gradient(135deg, var(--vscode-inputValidation-infoBackground), var(--vscode-button-secondaryBackground));
        border: 2px solid var(--vscode-inputValidation-infoBorder);
        border-radius: 8px;
        padding: 1em;
        margin-bottom: 1.2em;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
      .recommendations-title {
        color: #ffffff;
        font-weight: 600;
        font-size: 1.1em;
        margin-bottom: 0.8em;
      }
      .direct-dependency {
        color: #ffffff;
        font-family: var(--vscode-editor-font-family);
        background: linear-gradient(135deg, #007acc, #005a9e);
        padding: 0.4em 0.8em;
        border-radius: 6px;
        margin: 0.3em 0.5em 0.3em 0;
        display: inline-block;
        border: 2px solid #005a9e;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }
      .direct-dependency:hover {
        background: #ffffff;
        color: #333333;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
      }
      .paths-section {
        margin-top: 16px;
      }
      .paths-title {
        color: #ffffff;
        font-weight: 600;
        font-size: 1.1em;
        margin-bottom: 1em;
        border-bottom: 2px solid #007acc;
        padding-bottom: 0.5em;
      }
      .tree-container {
        background: var(--vscode-input-background);
        border: 2px solid var(--vscode-panel-border);
        border-radius: 8px;
        padding: 1.2em;
        font-family: var(--vscode-editor-font-family);
        font-size: var(--vscode-editor-font-size, 13px);
        line-height: 1.5;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
      }
      .tree-line {
        margin: 2px 0;
        white-space: pre;
        color: var(--vscode-foreground);
      }
      .root-dependency .component-name {
        color: var(--vscode-textLink-foreground);
        font-weight: bold;
      }
      .dependency-item .component-name {
        color: var(--vscode-textLink-foreground);
        font-weight: 500;
      }
      .vulnerable-item {
        background: var(--vscode-inputValidation-errorBackground);
        padding: 0.5em 0.8em;
        border-radius: 6px;
        margin: 0.3em 0;
        border-left: 4px solid var(--vscode-errorForeground);
        box-shadow: 0 2px 4px rgba(229, 20, 0, 0.15);
      }
      .vulnerable-item .component-name {
        color: var(--vscode-errorForeground);
        font-weight: bold;
      }
      .component-name:hover {
        background: var(--vscode-list-hoverBackground);
        padding: 0.3em 0.5em;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s ease;
      }
      .no-paths-message {
        text-align: center;
        color: var(--vscode-descriptionForeground);
        padding: 20px;
      }
      .icon {
        font-size: 18px;
        margin-right: 8px;
      }
      
      /* Fallbacks for when CSS variables are not available */
      @media (prefers-color-scheme: dark) {
        .impact-paths-container {
          background: #1e1e1e;
          color: #cccccc;
          border-color: #3c3c3c;
        }
        .tree-container {
          background: #252526;
          border-color: #3c3c3c;
        }
        .vulnerability-header {
          background: #332b00;
          border-color: #4d4000;
        }
        .recommendations {
          background: #003366;
          border-color: #004080;
        }
        .vulnerable-item {
          background: #3d1a1a;
          border-left-color: #f14c4c;
        }
      }
      
      @media (prefers-color-scheme: light) {
        .impact-paths-container {
          background: #ffffff;
          color: #333333;
          border-color: #e0e0e0;
        }
        .tree-container {
          background: #f8f9fa;
          border-color: #e0e0e0;
        }
        .vulnerability-header {
          background: #fff3cd;
          border-color: #ffeaa7;
        }
        .recommendations {
          background: #d1ecf1;
          border-color: #bee5eb;
        }
        .vulnerable-item {
          background: #f8d7da;
          border-left-color: #dc3545;
        }
      }
    </style>
  `;

  const directDepsHtml = Array.from(directDependencies)
    .map(dep => `<span class="direct-dependency">${escapeHtml(formatComponentName(dep))}</span>`)
    .join('');

  return `
    ${styles}
    <div class="impact-paths-container">
      <div class="vulnerability-header">
        <div class="vulnerability-title">🔍 Vulnerable dependency found</div>
        <div class="vulnerable-component">${escapeHtml(formatComponentName(vulnerableComponent))}</div>
      </div>
      
      <div class="recommendations">
        <div class="recommendations-title">💡 Parent dependencies to update</div>
        <div>${directDepsHtml}</div>
      </div>
      
      <div class="paths-section">
        <div class="paths-title">🌳 Dependency tree</div>
        <div class="tree-container">${formatTree(tree, 0, false, '', vulnerableComponent)}</div>
      </div>
    </div>
  `;
}

export function formatImpactPathsForPrompt(impactPaths: ImpactPath[]): string {
  if (!impactPaths || impactPaths.length === 0) {
    return "No impact paths found.";
  }

  const vulnerableComponent = getVulnerableComponent(impactPaths);
  const directDependencies = getDirectDependencies(impactPaths);

  let result = "";
  
  if (vulnerableComponent) {
    result += `Vulnerable Component: ${vulnerableComponent}\n`;
  }
  
  if (directDependencies.size > 0) {
    result += `Direct Dependencies Affected: ${Array.from(directDependencies).join(", ")}\n`;
  }
  
  result += "\nDependency Chains:\n";
  
  // Group paths by direct dependency
  const pathsByDirectDep = new Map<string, string[]>();
  
  for (const path of impactPaths) {
    const firstExternalDep = path.find(component => isExternalComponent(component.component_id));
    if (firstExternalDep) {
      const directDep = firstExternalDep.component_id;
      const chain = path
        .filter(component => isExternalComponent(component.component_id))
        .map(component => component.component_id)
        .join(" → ");
      
      if (!pathsByDirectDep.has(directDep)) {
        pathsByDirectDep.set(directDep, []);
      }
      
      if (!pathsByDirectDep.get(directDep)!.includes(chain)) {
        pathsByDirectDep.get(directDep)!.push(chain);
      }
    }
  }
  
  for (const [directDep, chains] of pathsByDirectDep) {
    result += `\n• From ${directDep}:\n`;
    for (const chain of chains) {
      result += `  └── ${chain}\n`;
    }
  }
  
  return result.trim();
}
