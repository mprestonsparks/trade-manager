import yaml from 'js-yaml';
import fs from 'fs';
import path from 'path';
import Logger from './logger.js';

const logger = new Logger('YAML');

class YamlManager {
    constructor(repoPath) {
        this.repoPath = repoPath;
        this.statusPath = path.join(repoPath, '.project', 'status', 'DEVELOPMENT_STATUS.yaml');
    }

    /**
     * Read and parse DEVELOPMENT_STATUS.yaml
     * @returns {Object} Parsed YAML data
     */
    readStatus() {
        try {
            logger.debug(`Reading ${this.statusPath}`);
            const content = fs.readFileSync(this.statusPath, 'utf8');
            return yaml.load(content);
        } catch (error) {
            logger.error(`Failed to read status file: ${this.statusPath}`, error);
            throw error;
        }
    }

    /**
     * Write data to DEVELOPMENT_STATUS.yaml
     * @param {Object} data - Data to write
     */
    writeStatus(data) {
        try {
            logger.debug(`Writing to ${this.statusPath}`);
            const content = yaml.dump(data, {
                indent: 2,
                lineWidth: -1
            });
            fs.writeFileSync(this.statusPath, content, 'utf8');
        } catch (error) {
            logger.error(`Failed to write status file: ${this.statusPath}`, error);
            throw error;
        }
    }

    /**
     * Update specific task in DEVELOPMENT_STATUS.yaml
     * @param {number} taskId - Task ID to update
     * @param {Object} updates - Updates to apply
     */
    updateTask(taskId, updates) {
        try {
            const data = this.readStatus();
            const task = data.next_available_tasks.find(t => t.id === taskId);
            
            if (!task) {
                throw new Error(`Task ${taskId} not found`);
            }

            Object.assign(task, updates);
            this.writeStatus(data);
            
            logger.info(`Updated task ${taskId}`);
            return task;
        } catch (error) {
            logger.error(`Failed to update task ${taskId}`, error);
            throw error;
        }
    }

    /**
     * Create a backup of DEVELOPMENT_STATUS.yaml
     * @returns {string} Backup file path
     */
    createBackup() {
        try {
            const backupPath = `${this.statusPath}.bak`;
            fs.copyFileSync(this.statusPath, backupPath);
            logger.debug(`Created backup at ${backupPath}`);
            return backupPath;
        } catch (error) {
            logger.error('Failed to create backup', error);
            throw error;
        }
    }

    /**
     * Restore from backup
     * @param {string} backupPath - Path to backup file
     */
    restoreFromBackup(backupPath) {
        try {
            fs.copyFileSync(backupPath, this.statusPath);
            logger.info(`Restored from backup ${backupPath}`);
        } catch (error) {
            logger.error(`Failed to restore from backup ${backupPath}`, error);
            throw error;
        }
    }

    /**
     * Validate YAML structure
     * @param {Object} data - YAML data to validate
     * @returns {boolean} True if valid
     */
    validateStructure(data) {
        const requiredFields = [
            'next_available_tasks',
            'completed_tasks'
        ];

        const taskFields = [
            'id',
            'name',
            'status',
            'prerequisites_met'
        ];

        try {
            // Check required top-level fields
            for (const field of requiredFields) {
                if (!(field in data)) {
                    throw new Error(`Missing required field: ${field}`);
                }
            }

            // Validate tasks
            for (const task of data.next_available_tasks) {
                for (const field of taskFields) {
                    if (!(field in task)) {
                        throw new Error(`Task ${task.id} missing required field: ${field}`);
                    }
                }
            }

            logger.debug('YAML structure validation passed');
            return true;
        } catch (error) {
            logger.error('YAML structure validation failed', error);
            return false;
        }
    }

    /**
     * Get all tasks with their dependencies
     * @returns {Array} List of tasks with dependencies
     */
    getAllTasks() {
        try {
            const data = this.readStatus();
            return data.next_available_tasks.map(task => ({
                id: task.id,
                title: task.title,
                status: task.status,
                dependencies: task.dependencies || [],
                blocking: task.blocking || [],
                repository: task.repository || this.repoPath
            }));
        } catch (error) {
            logger.error('Failed to get tasks with dependencies', error);
            throw error;
        }
    }

    /**
     * Update task dependencies
     * @param {number} taskId - Task ID to update
     * @param {Array} dependencies - List of task IDs this task depends on
     * @param {Array} blocking - List of task IDs this task is blocking
     */
    updateTaskDependencies(taskId, dependencies, blocking) {
        try {
            const data = this.readStatus();
            const task = data.next_available_tasks.find(t => t.id === taskId);
            
            if (!task) {
                throw new Error(`Task ${taskId} not found`);
            }

            task.dependencies = dependencies;
            task.blocking = blocking;
            
            this.writeStatus(data);
            logger.info(`Updated dependencies for task ${taskId}`);
            return task;
        } catch (error) {
            logger.error(`Failed to update dependencies for task ${taskId}`, error);
            throw error;
        }
    }

    /**
     * Get cross-repository task references
     * @returns {Object} Map of external task references
     */
    getCrossRepoReferences() {
        try {
            const data = this.readStatus();
            const references = {};
            
            data.next_available_tasks.forEach(task => {
                const externalDeps = (task.dependencies || [])
                    .filter(dep => dep.repository && dep.repository !== this.repoPath);
                
                if (externalDeps.length > 0) {
                    references[task.id] = externalDeps;
                }
            });
            
            return references;
        } catch (error) {
            logger.error('Failed to get cross-repo references', error);
            throw error;
        }
    }
}

export default YamlManager;
