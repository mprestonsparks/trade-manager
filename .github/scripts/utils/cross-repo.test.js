const CrossRepoHandler = require('./cross-repo');

describe('CrossRepoHandler', () => {
    let handler;
    const mockToken = 'test-token';
    const mockOwner = 'test-owner';

    beforeEach(() => {
        handler = new CrossRepoHandler(mockToken, mockOwner);
    });

    describe('parseReferences', () => {
        it('should parse valid cross-repo references', () => {
            const yamlContent = `
                dependencies:
                    - name: Feature A
                      reference: trade-dashboard:123
                    - name: Feature B
                      reference: market-analysis:456
            `;

            const refs = handler.parseReferences(yamlContent);
            expect(refs).toHaveLength(2);
            expect(refs[0]).toEqual({ repo: 'trade-dashboard', issue: 123 });
            expect(refs[1]).toEqual({ repo: 'market-analysis', issue: 456 });
        });

        it('should ignore invalid references', () => {
            const yamlContent = `
                dependencies:
                    - name: Feature A
                      reference: invalid-repo:123
                    - name: Feature B
                      reference: market-analysis:abc
                    - name: Feature C
                      reference: not-a-reference
            `;

            const refs = handler.parseReferences(yamlContent);
            expect(refs).toHaveLength(0);
        });

        it('should handle empty or invalid YAML', () => {
            expect(handler.parseReferences('')).toEqual([]);
            expect(handler.parseReferences('invalid: { yaml: [')).toEqual([]);
        });

        it('should handle nested references', () => {
            const yamlContent = `
                dependencies:
                    - name: Feature A
                      subtasks:
                        - name: Subtask 1
                          reference: trade-dashboard:123
                        - name: Subtask 2
                          reference: market-analysis:456
            `;

            const refs = handler.parseReferences(yamlContent);
            expect(refs).toHaveLength(2);
        });
    });

    describe('addReference', () => {
        it('should add reference to empty body', () => {
            const body = '';
            const result = handler.addReference(body, 'trade-manager', 123);
            expect(result).toContain('## Related Issues\n- trade-manager#123\n');
        });

        it('should add reference to existing section', () => {
            const body = '## Related Issues\n- market-analysis#456\n';
            const result = handler.addReference(body, 'trade-manager', 123);
            expect(result).toContain('- market-analysis#456\n- trade-manager#123\n');
        });

        it('should not duplicate existing reference', () => {
            const body = '## Related Issues\n- trade-manager#123\n';
            const result = handler.addReference(body, 'trade-manager', 123);
            expect(result).toBe(body);
        });

        it('should handle multiple sections', () => {
            const body = '## Description\nSome text\n\n## Related Issues\n- market-analysis#456\n\n## Notes\nMore text';
            const result = handler.addReference(body, 'trade-manager', 123);
            expect(result).toContain('- market-analysis#456\n- trade-manager#123\n');
            expect(result).toContain('## Description\n');
            expect(result).toContain('## Notes\n');
        });
    });

    describe('validateReferences', () => {
        it('should validate references using GitHub API', async () => {
            const mockGet = jest.fn().mockResolvedValue({});
            handler.octokit.issues = { get: mockGet };

            const refs = [
                { repo: 'trade-dashboard', issue: 123 },
                { repo: 'market-analysis', issue: 456 }
            ];

            const isValid = await handler.validateReferences(refs);
            expect(isValid).toBe(true);
            expect(mockGet).toHaveBeenCalledTimes(2);
        });

        it('should return false for invalid references', async () => {
            const mockGet = jest.fn().mockRejectedValue(new Error('Not found'));
            handler.octokit.issues = { get: mockGet };

            const refs = [
                { repo: 'trade-dashboard', issue: 999 }
            ];

            const isValid = await handler.validateReferences(refs);
            expect(isValid).toBe(false);
        });

        it('should handle empty references array', async () => {
            const isValid = await handler.validateReferences([]);
            expect(isValid).toBe(true);
        });
    });

    describe('getReferencingRepos', () => {
        it('should find repos that reference a specific issue', async () => {
            const mockGetContent = jest.fn().mockResolvedValue({
                data: {
                    content: Buffer.from(`
                        dependencies:
                            - reference: trade-manager:123
                    `).toString('base64')
                }
            });

            handler.octokit.repos = { getContent: mockGetContent };

            const refs = await handler.getReferencingRepos('trade-manager', 123);
            expect(refs).toContain('trade-dashboard');
        });

        it('should handle errors gracefully', async () => {
            const mockGetContent = jest.fn().mockRejectedValue(new Error('Not found'));
            handler.octokit.repos = { getContent: mockGetContent };

            const refs = await handler.getReferencingRepos('trade-manager', 123);
            expect(refs).toEqual([]);
        });
    });
});
