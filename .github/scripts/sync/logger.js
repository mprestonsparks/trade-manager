/**
 * Standardized logging for sync operations
 */
class Logger {
    constructor(context) {
        this.context = context;
    }

    /**
     * Format a message with timestamp and context
     * @param {string} level - Log level
     * @param {string} message - Message to log
     * @returns {string} Formatted message
     */
    formatMessage(level, message) {
        const timestamp = new Date().toISOString();
        return `[${timestamp}] [${level}] [${this.context}] ${message}`;
    }

    /**
     * Log an info message
     * @param {string} message - Message to log
     */
    info(message) {
        console.log(this.formatMessage('INFO', message));
    }

    /**
     * Log a warning message
     * @param {string} message - Message to log
     */
    warn(message) {
        console.warn(this.formatMessage('WARN', message));
    }

    /**
     * Log an error message
     * @param {string} message - Message to log
     * @param {Error} [error] - Optional error object
     */
    error(message, error) {
        console.error(this.formatMessage('ERROR', message));
        if (error) {
            console.error(error);
        }
    }

    /**
     * Log a debug message
     * @param {string} message - Message to log
     */
    debug(message) {
        if (process.env.DEBUG) {
            console.debug(this.formatMessage('DEBUG', message));
        }
    }

    /**
     * Create an activity log entry in DEVELOPMENT_STATUS.yaml
     * @param {string} action - Action performed
     * @param {string} details - Action details
     * @param {number} [taskId] - Optional task ID
     */
    async logActivity(action, details, taskId = null) {
        const yaml = require('js-yaml');
        const fs = require('fs');
        const path = require('path');

        try {
            const statusPath = path.resolve(process.cwd(), '.project/status/DEVELOPMENT_STATUS.yaml');
            const data = yaml.load(fs.readFileSync(statusPath, 'utf8'));

            if (!data.ai_activity_log) {
                data.ai_activity_log = [];
            }

            data.ai_activity_log.push({
                timestamp: new Date().toISOString(),
                action,
                details,
                task_id: taskId
            });

            fs.writeFileSync(statusPath, yaml.dump(data, { indent: 2, lineWidth: -1 }));
            this.debug(`Activity logged: ${action}`);
        } catch (error) {
            this.error('Failed to log activity', error);
        }
    }
}

export default Logger;
