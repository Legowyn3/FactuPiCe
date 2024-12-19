const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Rutas base
const PROJECT_ROOT = path.resolve(__dirname, '..');
const FRONTEND_ROOT = path.join(PROJECT_ROOT, 'frontend');
const BACKEND_ROOT = path.join(PROJECT_ROOT, 'backend');

// Función para obtener información de paquetes
function getPackageInfo(packagePath) {
  try {
    const packageJson = require(path.join(packagePath, 'package.json'));
    return {
      name: packageJson.name,
      version: packageJson.version,
      dependencies: Object.keys(packageJson.dependencies || {}),
      devDependencies: Object.keys(packageJson.devDependencies || {})
    };
  } catch (error) {
    return null;
  }
}

// Función para obtener últimos commits
function getRecentCommits(count = 10) {
  try {
    const commits = execSync(`git log -n ${count} --pretty=format:"%h|%s|%ad" --date=short`)
      .toString()
      .split('\n')
      .map(commit => {
        const [hash, subject, date] = commit.split('|');
        return { hash, subject, date };
      });
    return commits;
  } catch (error) {
    console.error('Error obteniendo commits:', error);
    return [];
  }
}

// Función para generar resumen de características
function generateFeatureSummary() {
  return {
    authentication: {
      method: 'NextAuth',
      features: ['Login', 'Registration', 'Session Management']
    },
    invoiceManagement: {
      features: [
        'CRUD Operations',
        'Advanced Filtering',
        'Date Range Selection',
        'Export Functionality',
        'Invoice Statistics'
      ]
    },
    validation: {
      tools: ['Zod'],
      coverage: ['Invoice Creation', 'Invoice Update']
    }
  };
}

// Generar PROJECT_SUMMARY.md
function generateProjectSummary() {
  const frontendPackage = getPackageInfo(FRONTEND_ROOT);
  const backendPackage = getPackageInfo(BACKEND_ROOT);
  const recentCommits = getRecentCommits();
  const featureSummary = generateFeatureSummary();

  const summaryContent = `# Invoice Management System - Project Summary

## Overview
A comprehensive invoice management web application with robust features for tracking, analyzing, and managing invoices.

## Tech Stack
- **Frontend**: 
  - Framework: Next.js
  - Language: TypeScript
  - Styling: Tailwind CSS
  - Version: ${frontendPackage?.version || 'Unknown'}

- **Backend**:
  - ORM: Prisma
  - Database: PostgreSQL
  - Authentication: NextAuth
  - Version: ${backendPackage?.version || 'Unknown'}

## Key Features
${Object.entries(featureSummary).map(([category, details]) => 
  `### ${category.charAt(0).toUpperCase() + category.slice(1)}
${Object.entries(details).map(([key, value]) => 
  `- **${key.charAt(0).toUpperCase() + key.slice(1)}**: ${Array.isArray(value) ? value.join(', ') : JSON.stringify(value)}`
).join('\n')}`
).join('\n\n')}

## Recent Development
${recentCommits.map(commit => 
  `- \`${commit.hash}\` ${commit.subject} (${commit.date})`
).join('\n')}

## Next Steps
1. Enhance export functionality
2. Implement more advanced reporting
3. Improve user experience and accessibility
`;

  fs.writeFileSync(path.join(PROJECT_ROOT, 'PROJECT_SUMMARY.md'), summaryContent);
}

// Generar .dev-context.json
function generateDevContext() {
  const context = {
    project_name: "Invoice Management System",
    version: "0.1.0",
    last_updated: new Date().toISOString(),
    tech_stack: {
      frontend: ["Next.js", "TypeScript", "Tailwind CSS", "Recharts"],
      backend: ["Prisma", "PostgreSQL", "NextAuth"],
      testing: ["Jest", "React Testing Library"]
    },
    current_features: [
      "User Authentication",
      "Invoice CRUD Operations", 
      "Advanced Filtering",
      "Invoice Statistics",
      "CSV Export"
    ],
    recent_changes: getRecentCommits(5).map(commit => commit.subject)
  };

  fs.writeFileSync(
    path.join(PROJECT_ROOT, '.dev-context.json'), 
    JSON.stringify(context, null, 2)
  );
}

// Ejecutar generación de documentos
function main() {
  generateProjectSummary();
  generateDevContext();
  console.log('Documentación de proyecto actualizada.');
}

main();
