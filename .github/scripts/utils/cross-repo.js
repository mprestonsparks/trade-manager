/**
 * Cross-Repository Reference Handler
 * Manages dependencies and references between different repositories in the trading system
 */

const { Octokit } = require('@octokit/rest');
const yaml = require('js-yaml');
const path = require('path');
const fs = require('fs').promises;

class CrossRepoHandler {
    constructor(token, owner) {
        this.octokit = new Octokit({ auth: token });
        this.owner = owner;
        this.repos = [
            'trade-manager',
            'trade-dashboard',
            'trade-discovery',
            'market-analysis'
        ];
    }

    /**
     * Parse cross-repo references from a YAML file
     * @param {string} content - YAML content
     * @returns {Array} Array of cross-repo references
     */
    parseReferences(content) {
        if (!content) return [];

        let data;
        try {
            data = yaml.load(content);
            if (!data) return [];
        } catch (error) {
            return [];
        }

        const references = [];

        const findRefs = (obj) => {
            if (typeof obj === 'object' && obj !== null) {
                if (obj.reference && typeof obj.reference === 'string') {
                    // Format: repo:issue#
                    const match = obj.reference.match(/^([^:]+):(\d+)$/);
                    if (match && this.repos.includes(match[1])) {
                        references.push({
                            repo: match[1],
                            issue: parseInt(match[2])
                        });
                    }
                }
                Object.values(obj).forEach(findRefs);
            }
        };

        findRefs(data);
        return references;
    }

    /**
     * Update cross-repo references
     * @param {string} sourceRepo - Source repository name
     * @param {number} sourceIssue - Source issue number
     * @param {Array} references - Array of cross-repo references
     */
    async updateReferences(sourceRepo, sourceIssue, references) {
        for (const ref of references) {
            try {
                // Get the target issue
                const issue = await this.octokit.issues.get({
                    owner: this.owner,
                    repo: ref.repo,
                    issue_number: ref.issue
                });

                // Update the target issue body with a reference back
                const body = this.addReference(
                    issue.data.body || '',
                    sourceRepo,
                    sourceIssue
                );

                await this.octokit.issues.update({
                    owner: this.owner,
                    repo: ref.repo,
                    issue_number: ref.issue,
                    body
                });
            } catch (error) {
                console.error(`Error updating reference in ${ref.repo}#${ref.issue}:`, error);
            }
        }
    }

    /**
     * Add a reference to an issue body
     * @param {string} body - Current issue body
     * @param {string} repo - Repository name
     * @param {number} issue - Issue number
     * @returns {string} Updated issue body
     */
    addReference(body, repo, issue) {
        const referenceSection = '## Related Issues\n';
        const reference = `- ${repo}#${issue}`;

        if (body.includes(referenceSection)) {
            if (!body.includes(reference)) {
                // Find the last line in the Related Issues section
                const lines = body.split('\n');
                const sectionIndex = lines.findIndex(line => line === '## Related Issues');
                let lastReferenceIndex = sectionIndex;
                
                for (let i = sectionIndex + 1; i < lines.length; i++) {
                    if (lines[i].startsWith('- ')) {
                        lastReferenceIndex = i;
                    } else if (lines[i].startsWith('##')) {
                        break;
                    }
                }
                
                lines.splice(lastReferenceIndex + 1, 0, reference);
                return lines.join('\n');
            }
        } else {
            return body + '\n\n' + referenceSection + reference + '\n';
        }

        return body;
    }

    /**
     * Validate cross-repo references
     * @param {Array} references - Array of cross-repo references
     * @returns {Promise<boolean>} True if all references are valid
     */
    async validateReferences(references) {
        for (const ref of references) {
            try {
                await this.octokit.issues.get({
                    owner: this.owner,
                    repo: ref.repo,
                    issue_number: ref.issue
                });
            } catch (error) {
                console.error(`Invalid reference ${ref.repo}#${ref.issue}:`, error);
                return false;
            }
        }
        return true;
    }

    /**
     * Get all repositories that reference a specific issue
     * @param {string} targetRepo - Target repository name
     * @param {number} targetIssue - Target issue number
     * @returns {Promise<Array>} Array of repositories with references
     */
    async getReferencingRepos(targetRepo, targetIssue) {
        const referencingRepos = [];

        for (const repo of this.repos) {
            if (repo === targetRepo) continue;

            try {
                const statusFile = await this.octokit.repos.getContent({
                    owner: this.owner,
                    repo: repo,
                    path: '.project/status/DEVELOPMENT_STATUS.yaml'
                });

                const content = Buffer.from(statusFile.data.content, 'base64').toString();
                const references = this.parseReferences(content);

                if (references.some(ref => 
                    ref.repo === targetRepo && ref.issue === targetIssue)) {
                    referencingRepos.push(repo);
                }
            } catch (error) {
                console.error(`Error checking references in ${repo}:`, error);
            }
        }

        return referencingRepos;
    }
}

module.exports = CrossRepoHandler;
