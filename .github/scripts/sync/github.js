import { Octokit } from '@octokit/rest';
import Logger from './logger.js';
const CrossRepoHandler = require('../utils/cross-repo');

const logger = new Logger('GitHub');

class GitHubManager {
    constructor(token, owner, repo) {
        this.octokit = new Octokit({ auth: token });
        this.owner = owner;
        this.repo = repo;
        this.crossRepoHandler = new CrossRepoHandler(token, owner);
    }

    /**
     * Get issue details
     * @param {number} issueNumber - Issue number
     * @returns {Promise<Object>} Issue data
     */
    async getIssue(issueNumber) {
        try {
            const { data } = await this.octokit.issues.get({
                owner: this.owner,
                repo: this.repo,
                issue_number: issueNumber
            });
            logger.debug(`Retrieved issue #${issueNumber}`);
            return data;
        } catch (error) {
            logger.error(`Failed to get issue #${issueNumber}`, error);
            throw error;
        }
    }

    /**
     * Update issue details
     * @param {number} issueNumber - Issue number
     * @param {Object} updates - Updates to apply
     */
    async updateIssue(issueNumber, updates) {
        try {
            await this.octokit.issues.update({
                owner: this.owner,
                repo: this.repo,
                issue_number: issueNumber,
                ...updates
            });
            logger.info(`Updated issue #${issueNumber}`);
        } catch (error) {
            logger.error(`Failed to update issue #${issueNumber}`, error);
            throw error;
        }
    }

    /**
     * Get project details
     * @param {string} projectNumber - Project number
     * @returns {Promise<Object>} Project data
     */
    async getProject(projectNumber) {
        try {
            const query = `
                query($owner: String!, $number: Int!) {
                    user(login: $owner) {
                        projectV2(number: $number) {
                            id
                            title
                            items(first: 100) {
                                nodes {
                                    id
                                    fieldValues(first: 8) {
                                        nodes {
                                            ... on ProjectV2ItemFieldTextValue {
                                                text
                                                field { ... on ProjectV2FieldCommon { name } }
                                            }
                                            ... on ProjectV2ItemFieldSingleSelectValue {
                                                name
                                                field { ... on ProjectV2FieldCommon { name } }
                                            }
                                        }
                                    }
                                    content {
                                        ... on Issue {
                                            number
                                            title
                                            state
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            `;

            const variables = {
                owner: this.owner,
                number: parseInt(projectNumber)
            };

            console.log('GraphQL Query Variables:', variables);
            const response = await this.octokit.graphql(query, variables);
            console.log('GraphQL Response:', JSON.stringify(response, null, 2));

            logger.debug(`Retrieved project #${projectNumber}`);
            return response.user.projectV2;
        } catch (error) {
            logger.error(`Failed to get project #${projectNumber}`, error);
            throw error;
        }
    }

    /**
     * Update project item
     * @param {string} itemId - Project item ID
     * @param {string} fieldId - Field ID
     * @param {string} value - New value
     */
    async updateProjectItem(itemId, fieldId, value) {
        try {
            const mutation = `
                mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: String!) {
                    updateProjectV2ItemFieldValue(
                        input: {
                            projectId: $projectId
                            itemId: $itemId
                            fieldId: $fieldId
                            value: $value
                        }
                    ) {
                        projectV2Item {
                            id
                        }
                    }
                }
            `;

            await this.octokit.graphql(mutation, {
                projectId: itemId,
                itemId: fieldId,
                fieldId,
                value
            });

            logger.info(`Updated project item ${itemId}`);
        } catch (error) {
            logger.error(`Failed to update project item ${itemId}`, error);
            throw error;
        }
    }

    /**
     * Convert task status to issue labels
     * @param {string} status - Task status
     * @returns {string[]} Labels to apply
     */
    getLabelsForStatus(status) {
        const statusLabels = {
            'in-progress': ['in-progress'],
            'blocked': ['blocked'],
            'ready': ['ready'],
            'review': ['review'],
            'completed': ['completed']
        };
        return statusLabels[status] || [];
    }

    /**
     * Sync task status with issue
     * @param {Object} task - Task object
     */
    async syncTaskStatus(task) {
        if (!task.github_issue) {
            logger.warn(`Task ${task.id} has no associated GitHub issue`);
            return;
        }

        try {
            const labels = this.getLabelsForStatus(task.status);
            await this.updateIssue(task.github_issue, {
                state: task.status === 'completed' ? 'closed' : 'open',
                labels
            });

            logger.info(`Synced status for task ${task.id} to issue #${task.github_issue}`);
        } catch (error) {
            logger.error(`Failed to sync task ${task.id} status`, error);
            throw error;
        }
    }

    async updateIssueFromYaml(repo, issueNumber, yamlData) {
        try {
            // Existing issue update logic
            const labels = this.getLabelsForStatus(yamlData.status);
            await this.updateIssue(issueNumber, {
                state: yamlData.status === 'completed' ? 'closed' : 'open',
                labels
            });

            // Handle cross-repo references
            const references = this.crossRepoHandler.parseReferences(yamlData);
            if (references.length > 0) {
                const isValid = await this.crossRepoHandler.validateReferences(references);
                if (isValid) {
                    await this.crossRepoHandler.updateReferences(repo, issueNumber, references);
                } else {
                    logger.warn(`Invalid cross-repo references found in ${repo}#${issueNumber}`);
                }
            }

            logger.info(`Updated issue ${repo}#${issueNumber}`);
        } catch (error) {
            logger.error(`Error updating issue ${repo}#${issueNumber}:`, error);
            throw error;
        }
    }

    async syncProjectToLocal(repo, event) {
        try {
            // Existing sync logic
            const yamlContent = await this.getYamlContent(repo);
            const task = this.parseTaskFromYaml(yamlContent);

            // Update cross-repo references if needed
            if (event.issue) {
                const references = this.crossRepoHandler.parseReferences(yamlContent);
                const referencingRepos = await this.crossRepoHandler.getReferencingRepos(repo, event.issue.number);
                
                for (const refRepo of referencingRepos) {
                    await this.updateRepoStatus(refRepo, {
                        type: 'cross_repo_update',
                        source: { repo, issue: event.issue.number }
                    });
                }
            }

            logger.info(`Synced project to local for ${repo}`);
        } catch (error) {
            logger.error(`Error syncing project to local for ${repo}:`, error);
            throw error;
        }
    }
}

export default GitHubManager;
