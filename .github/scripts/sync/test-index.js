const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);
const path = require('path');

jest.mock('./github');
const GitHubManager = require('./github');

describe('Sync CLI', () => {
    const scriptPath = path.join(__dirname, 'index.js');

    beforeEach(() => {
        GitHubManager.mockClear();
    });

    describe('sync-to-local', () => {
        it('should handle sync-to-local command correctly', async () => {
            const mockEvent = { type: 'issues', action: 'opened' };
            const cmd = `node ${scriptPath} sync-to-local --token test-token --owner test-owner --repo test-repo --event '${JSON.stringify(mockEvent)}'`;

            const mockSyncProjectToLocal = jest.fn();
            GitHubManager.mockImplementation(() => ({
                syncProjectToLocal: mockSyncProjectToLocal
            }));

            await execAsync(cmd);

            expect(GitHubManager).toHaveBeenCalledWith('test-token', 'test-owner', 'test-repo');
            expect(mockSyncProjectToLocal).toHaveBeenCalledWith('test-repo', mockEvent);
        });

        it('should handle errors gracefully', async () => {
            const mockEvent = { type: 'invalid' };
            const cmd = `node ${scriptPath} sync-to-local --token test-token --owner test-owner --repo test-repo --event '${JSON.stringify(mockEvent)}'`;

            GitHubManager.mockImplementation(() => ({
                syncProjectToLocal: jest.fn().mockRejectedValue(new Error('Test error'))
            }));

            await expect(execAsync(cmd)).rejects.toThrow();
        });
    });

    describe('sync-to-project', () => {
        it('should handle sync-to-project command correctly', async () => {
            const mockCommit = { id: 'test-commit' };
            const cmd = `node ${scriptPath} sync-to-project --token test-token --owner test-owner --repo test-repo --commit '${JSON.stringify(mockCommit)}'`;

            const mockSyncLocalToProject = jest.fn();
            GitHubManager.mockImplementation(() => ({
                syncLocalToProject: mockSyncLocalToProject
            }));

            await execAsync(cmd);

            expect(GitHubManager).toHaveBeenCalledWith('test-token', 'test-owner', 'test-repo');
            expect(mockSyncLocalToProject).toHaveBeenCalledWith('test-repo', mockCommit);
        });

        it('should handle errors gracefully', async () => {
            const mockCommit = { id: 'invalid' };
            const cmd = `node ${scriptPath} sync-to-project --token test-token --owner test-owner --repo test-repo --commit '${JSON.stringify(mockCommit)}'`;

            GitHubManager.mockImplementation(() => ({
                syncLocalToProject: jest.fn().mockRejectedValue(new Error('Test error'))
            }));

            await expect(execAsync(cmd)).rejects.toThrow();
        });
    });
});
