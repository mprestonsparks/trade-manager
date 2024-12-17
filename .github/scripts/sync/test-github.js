import GitHubManager from './github.js';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import path from 'path';
import dotenv from 'dotenv';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

async function testGitHubManager() {
    console.log('Testing GitHubManager...\n');
    
    // Get GitHub token from environment
    const token = process.env.GITHUB_TOKEN;
    if (!token) {
        console.error('GITHUB_TOKEN environment variable not set in root .env file');
        return;
    }
    
    // Create GitHubManager instance
    const github = new GitHubManager(token, 'mprestonsparks', 'trade-manager');
    
    try {
        // Test getting issue
        console.log('1. Testing issue retrieval:');
        const issue = await github.getIssue(1);
        console.log(`Successfully retrieved issue: ${issue.title}\n`);
        
        // Test getting project
        console.log('2. Testing project retrieval:');
        const project = await github.getProject(6); // Trading System Development project
        console.log(`Successfully retrieved project: ${project.title}\n`);
        
        // Test label conversion
        console.log('3. Testing status to label conversion:');
        const statuses = ['in-progress', 'blocked', 'ready', 'review', 'completed'];
        for (const status of statuses) {
            const labels = github.getLabelsForStatus(status);
            console.log(`Status '${status}' → Labels: ${labels.join(', ')}`);
        }
        
        // Test task status sync (using first task)
        console.log('\n4. Testing task status sync:');
        const task = {
            id: 1,
            github_issue: 1,
            status: 'in-progress'
        };
        await github.syncTaskStatus(task);
        console.log('Successfully synced task status');
        
        // Test cross-repo functionality
        console.log('\n5. Testing cross-repo functionality:');
        const mockYamlData = {
            status: 'in_progress',
            dependencies: [
                { reference: 'trade-dashboard:123' }
            ]
        };

        const mockParseReferences = jest.fn().mockReturnValue([{ repo: 'trade-dashboard', issue: 123 }]);
        const mockValidateReferences = jest.fn().mockResolvedValue(true);
        const mockUpdateReferences = jest.fn();

        const CrossRepoHandler = {
            parseReferences: mockParseReferences,
            validateReferences: mockValidateReferences,
            updateReferences: mockUpdateReferences
        };

        await github.updateIssueFromYaml('trade-manager', 456, mockYamlData);

        console.log('Successfully tested cross-repo functionality');
        
    } catch (error) {
        console.error('Test failed:', error);
    }
}

testGitHubManager();
