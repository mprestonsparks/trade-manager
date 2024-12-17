import { Graph } from 'graphlib';
import Logger from './logger.js';
import YamlManager from './yaml.js';

const logger = new Logger('DAG');

class DAGManager {
    constructor(repoPath) {
        this.repoPath = repoPath;
        this.yamlManager = new YamlManager(repoPath);
        this.graph = new Graph({ directed: true });
    }

    /**
     * Build DAG from tasks
     * @returns {Graph} Built graph
     */
    buildGraph() {
        try {
            // Clear existing graph
            this.graph = new Graph({ directed: true });
            
            // Get all tasks
            const tasks = this.yamlManager.getAllTasks();
            
            // Add all tasks as nodes
            tasks.forEach(task => {
                this.graph.setNode(task.id.toString(), task);
            });
            
            // Add dependency edges
            tasks.forEach(task => {
                (task.dependencies || []).forEach(depId => {
                    this.graph.setEdge(depId.toString(), task.id.toString());
                });
            });
            
            logger.debug(`Built graph with ${tasks.length} nodes`);
            return this.graph;
        } catch (error) {
            logger.error('Failed to build graph', error);
            throw error;
        }
    }

    /**
     * Check if graph has cycles
     * @returns {boolean} True if cycles found
     */
    hasCycles() {
        try {
            const cycles = this.findCycles();
            return cycles.length > 0;
        } catch (error) {
            logger.error('Failed to check for cycles', error);
            throw error;
        }
    }

    /**
     * Find all cycles in the graph
     * @returns {Array} List of cycles found
     */
    findCycles() {
        const cycles = [];
        const visited = new Set();
        const recursionStack = new Set();

        const dfs = (nodeId, path = []) => {
            visited.add(nodeId);
            recursionStack.add(nodeId);
            path.push(nodeId);

            const successors = this.graph.successors(nodeId) || [];
            for (const successor of successors) {
                if (!visited.has(successor)) {
                    const cycleFound = dfs(successor, [...path]);
                    if (cycleFound) return true;
                } else if (recursionStack.has(successor)) {
                    const cycle = path.slice(path.indexOf(successor));
                    cycles.push(cycle);
                    return true;
                }
            }

            recursionStack.delete(nodeId);
            path.pop();
            return false;
        };

        const nodes = this.graph.nodes();
        for (const node of nodes) {
            if (!visited.has(node)) {
                dfs(node);
            }
        }

        return cycles;
    }

    /**
     * Get all tasks that are ready to be worked on
     * @returns {Array} List of available tasks
     */
    getAvailableTasks() {
        try {
            const available = [];
            const nodes = this.graph.nodes();
            
            for (const nodeId of nodes) {
                const task = this.graph.node(nodeId);
                const predecessors = this.graph.predecessors(nodeId) || [];
                
                // Check if all dependencies are completed
                const allDepsCompleted = predecessors.every(depId => {
                    const depTask = this.graph.node(depId);
                    return depTask.status === 'completed';
                });
                
                if (allDepsCompleted && task.status !== 'completed') {
                    available.push(task);
                }
            }
            
            return available;
        } catch (error) {
            logger.error('Failed to get available tasks', error);
            throw error;
        }
    }

    /**
     * Update task status and recalculate dependencies
     * @param {number} taskId - Task to update
     * @param {string} status - New status
     */
    async updateTaskStatus(taskId, status) {
        try {
            // Update in YAML
            await this.yamlManager.updateTask(taskId, { status });
            
            // Rebuild graph
            this.buildGraph();
            
            // Get affected tasks
            const affected = this.getAffectedTasks(taskId);
            logger.info(`Updated task ${taskId}, affected tasks: ${affected.length}`);
            
            return affected;
        } catch (error) {
            logger.error(`Failed to update task ${taskId}`, error);
            throw error;
        }
    }

    /**
     * Get all tasks affected by a change to the specified task
     * @param {number} taskId - Task that changed
     * @returns {Array} List of affected tasks
     */
    getAffectedTasks(taskId) {
        try {
            const affected = new Set();
            const stack = [taskId.toString()];
            
            while (stack.length > 0) {
                const current = stack.pop();
                affected.add(current);
                
                // Add successors (tasks that depend on this one)
                const successors = this.graph.successors(current) || [];
                for (const successor of successors) {
                    if (!affected.has(successor)) {
                        stack.push(successor);
                    }
                }
            }
            
            affected.delete(taskId.toString()); // Remove the original task
            return Array.from(affected).map(id => this.graph.node(id));
        } catch (error) {
            logger.error(`Failed to get affected tasks for ${taskId}`, error);
            throw error;
        }
    }

    /**
     * Validate the entire dependency structure
     * @returns {Object} Validation results
     */
    validateDependencies() {
        try {
            const results = {
                hasCycles: false,
                unreachableTasks: [],
                missingDependencies: [],
                valid: true
            };
            
            // Check for cycles
            results.hasCycles = this.hasCycles();
            if (results.hasCycles) {
                results.valid = false;
            }
            
            // Check for unreachable tasks
            const components = this.findUnreachableTasks();
            results.unreachableTasks = components;
            if (components.length > 0) {
                results.valid = false;
            }
            
            // Check for missing dependencies
            const missing = this.findMissingDependencies();
            results.missingDependencies = missing;
            if (missing.length > 0) {
                results.valid = false;
            }
            
            return results;
        } catch (error) {
            logger.error('Failed to validate dependencies', error);
            throw error;
        }
    }

    /**
     * Find tasks that are unreachable in the graph
     * @returns {Array} List of unreachable tasks
     */
    findUnreachableTasks() {
        const visited = new Set();
        const unreachable = [];
        
        // Start from root nodes (nodes with no dependencies)
        const roots = this.graph.nodes().filter(node => 
            (this.graph.predecessors(node) || []).length === 0
        );
        
        // DFS from each root
        const dfs = (nodeId) => {
            visited.add(nodeId);
            const successors = this.graph.successors(nodeId) || [];
            for (const successor of successors) {
                if (!visited.has(successor)) {
                    dfs(successor);
                }
            }
        };
        
        // Visit all reachable nodes
        roots.forEach(root => dfs(root));
        
        // Find unreachable nodes
        this.graph.nodes().forEach(node => {
            if (!visited.has(node)) {
                unreachable.push(this.graph.node(node));
            }
        });
        
        return unreachable;
    }

    /**
     * Find dependencies that are referenced but don't exist
     * @returns {Array} List of missing dependencies
     */
    findMissingDependencies() {
        const missing = [];
        const nodes = this.graph.nodes();
        
        nodes.forEach(nodeId => {
            const task = this.graph.node(nodeId);
            (task.dependencies || []).forEach(depId => {
                if (!this.graph.hasNode(depId.toString())) {
                    missing.push({
                        taskId: parseInt(nodeId),
                        missingDependency: depId
                    });
                }
            });
        });
        
        return missing;
    }

    /**
     * Get tasks from other repositories that this task depends on
     * @param {number} taskId - Task to check
     * @returns {Array} List of cross-repo dependencies
     */
    getCrossRepoDependencies(taskId) {
        try {
            const task = this.graph.node(taskId.toString());
            if (!task) {
                throw new Error(`Task ${taskId} not found`);
            }

            const crossRepoDeps = [];
            const allDeps = task.dependencies || [];

            allDeps.forEach(depId => {
                const depTask = this.graph.node(depId.toString());
                if (depTask && depTask.repository !== task.repository) {
                    crossRepoDeps.push(depTask);
                }
            });

            return crossRepoDeps;
        } catch (error) {
            logger.error(`Failed to get cross-repo dependencies for task ${taskId}`, error);
            throw error;
        }
    }

    /**
     * Get tasks in other repositories that depend on this task
     * @param {number} taskId - Task to check
     * @returns {Array} List of cross-repo dependents
     */
    getCrossRepoDependents(taskId) {
        try {
            const task = this.graph.node(taskId.toString());
            if (!task) {
                throw new Error(`Task ${taskId} not found`);
            }

            const crossRepoDeps = [];
            const successors = this.graph.successors(taskId.toString()) || [];

            successors.forEach(sucId => {
                const sucTask = this.graph.node(sucId);
                if (sucTask && sucTask.repository !== task.repository) {
                    crossRepoDeps.push(sucTask);
                }
            });

            return crossRepoDeps;
        } catch (error) {
            logger.error(`Failed to get cross-repo dependents for task ${taskId}`, error);
            throw error;
        }
    }

    /**
     * Get all tasks for a specific milestone
     * @param {string} milestone - Milestone name
     * @returns {Array} List of tasks in the milestone
     */
    getTasksByMilestone(milestone) {
        try {
            const milestoneTasks = [];
            this.graph.nodes().forEach(nodeId => {
                const task = this.graph.node(nodeId);
                if (task.milestone === milestone) {
                    milestoneTasks.push(task);
                }
            });
            return milestoneTasks;
        } catch (error) {
            logger.error(`Failed to get tasks for milestone ${milestone}`, error);
            throw error;
        }
    }

    /**
     * Calculate milestone completion status
     * @param {string} milestone - Milestone name
     * @returns {Object} Milestone status information
     */
    getMilestoneStatus(milestone) {
        try {
            const tasks = this.getTasksByMilestone(milestone);
            const total = tasks.length;
            const completed = tasks.filter(t => t.status === 'completed').length;
            const inProgress = tasks.filter(t => t.status === 'in_progress').length;
            const blocked = tasks.filter(t => t.status === 'blocked').length;

            return {
                milestone,
                total,
                completed,
                inProgress,
                blocked,
                percentComplete: total > 0 ? (completed / total) * 100 : 0,
                repositories: [...new Set(tasks.map(t => t.repository))]
            };
        } catch (error) {
            logger.error(`Failed to get status for milestone ${milestone}`, error);
            throw error;
        }
    }

    /**
     * Get overall project status
     * @returns {Object} Project-wide status information
     */
    getProjectStatus() {
        try {
            const nodes = this.graph.nodes();
            const tasks = nodes.map(id => this.graph.node(id));
            
            // Get all unique milestones
            const milestones = [...new Set(tasks.map(t => t.milestone).filter(Boolean))];
            
            // Calculate overall stats
            const stats = {
                totalTasks: tasks.length,
                completedTasks: tasks.filter(t => t.status === 'completed').length,
                inProgressTasks: tasks.filter(t => t.status === 'in_progress').length,
                blockedTasks: tasks.filter(t => t.status === 'blocked').length,
                repositories: [...new Set(tasks.map(t => t.repository))],
                milestones: milestones.map(m => this.getMilestoneStatus(m)),
                crossRepoDependencies: this.getAllCrossRepoDependencies()
            };
            
            // Calculate completion percentage
            stats.percentComplete = (stats.completedTasks / stats.totalTasks) * 100;
            
            return stats;
        } catch (error) {
            logger.error('Failed to get project status', error);
            throw error;
        }
    }

    /**
     * Get all cross-repository dependencies
     * @returns {Array} List of all cross-repo dependencies
     */
    getAllCrossRepoDependencies() {
        try {
            const crossRepoDeps = [];
            
            this.graph.nodes().forEach(nodeId => {
                const task = this.graph.node(nodeId);
                const deps = this.getCrossRepoDependencies(parseInt(nodeId));
                
                if (deps.length > 0) {
                    crossRepoDeps.push({
                        taskId: parseInt(nodeId),
                        repository: task.repository,
                        dependencies: deps
                    });
                }
            });
            
            return crossRepoDeps;
        } catch (error) {
            logger.error('Failed to get all cross-repo dependencies', error);
            throw error;
        }
    }

    /**
     * Get critical path tasks - tasks that are blocking the most other tasks
     * @returns {Array} List of tasks on the critical path
     */
    getCriticalPathTasks() {
        try {
            const criticalTasks = [];
            const nodes = this.graph.nodes();
            
            nodes.forEach(nodeId => {
                const task = this.graph.node(nodeId);
                const successors = this.graph.successors(nodeId) || [];
                const allDownstream = this.getAllDownstreamTasks(parseInt(nodeId));
                
                criticalTasks.push({
                    task,
                    directDependents: successors.length,
                    totalDownstream: allDownstream.length,
                    blocksCompletedTasks: allDownstream.filter(t => t.status === 'completed').length,
                    blocksInProgressTasks: allDownstream.filter(t => t.status === 'in_progress').length
                });
            });
            
            // Sort by impact (total downstream tasks affected)
            return criticalTasks.sort((a, b) => b.totalDownstream - a.totalDownstream);
        } catch (error) {
            logger.error('Failed to get critical path tasks', error);
            throw error;
        }
    }

    /**
     * Get all tasks that depend on this task (directly or indirectly)
     * @param {number} taskId - Task to analyze
     * @returns {Array} List of downstream tasks
     */
    getAllDownstreamTasks(taskId) {
        try {
            const downstream = new Set();
            const stack = [taskId.toString()];
            
            while (stack.length > 0) {
                const current = stack.pop();
                const successors = this.graph.successors(current) || [];
                
                successors.forEach(sucId => {
                    if (!downstream.has(sucId)) {
                        downstream.add(sucId);
                        stack.push(sucId);
                    }
                });
            }
            
            return Array.from(downstream).map(id => this.graph.node(id));
        } catch (error) {
            logger.error(`Failed to get downstream tasks for ${taskId}`, error);
            throw error;
        }
    }

    /**
     * Get recommended next tasks based on impact and readiness
     * @param {Object} options - Filter options
     * @param {string} options.milestone - Optional milestone to focus on
     * @param {string} options.repository - Optional repository to focus on
     * @param {number} options.limit - Max number of tasks to return
     * @returns {Array} List of recommended tasks with priority scores
     */
    getRecommendedTasks(options = {}) {
        try {
            const available = this.getAvailableTasks();
            const recommendations = [];
            
            for (const task of available) {
                // Skip if doesn't match filters
                if (options.milestone && task.milestone !== options.milestone) continue;
                if (options.repository && task.repository !== options.repository) continue;
                
                // Calculate priority score
                const downstream = this.getAllDownstreamTasks(task.id);
                const crossRepoDeps = this.getCrossRepoDependencies(task.id);
                const crossRepoDependent = this.getCrossRepoDependents(task.id);
                
                const score = {
                    task,
                    priorityScore: 0,
                    reasons: []
                };
                
                // Factor 1: Number of downstream tasks
                const downstreamImpact = downstream.length * 10;
                score.priorityScore += downstreamImpact;
                if (downstreamImpact > 0) {
                    score.reasons.push(`Blocks ${downstream.length} other tasks`);
                }
                
                // Factor 2: Cross-repo impact
                const crossRepoImpact = (crossRepoDeps.length + crossRepoDependent.length) * 15;
                score.priorityScore += crossRepoImpact;
                if (crossRepoImpact > 0) {
                    score.reasons.push(`Involved in ${crossRepoDeps.length + crossRepoDependent.length} cross-repo relationships`);
                }
                
                // Factor 3: Milestone progress impact
                if (task.milestone) {
                    const milestoneStatus = this.getMilestoneStatus(task.milestone);
                    const milestoneImpact = (1 - milestoneStatus.percentComplete / 100) * 20;
                    score.priorityScore += milestoneImpact;
                    if (milestoneImpact > 0) {
                        score.reasons.push(`Helps complete milestone ${task.milestone} (${milestoneStatus.percentComplete.toFixed(1)}% done)`);
                    }
                }
                
                // Factor 4: Complexity and estimated time
                if (task.complexity) {
                    const complexityScore = (5 - task.complexity) * 5; // Lower complexity = higher priority
                    score.priorityScore += complexityScore;
                    if (complexityScore > 0) {
                        score.reasons.push(`Relatively ${task.complexity <= 2 ? 'simple' : 'complex'} task`);
                    }
                }
                
                recommendations.push(score);
            }
            
            // Sort by priority score
            recommendations.sort((a, b) => b.priorityScore - a.priorityScore);
            
            // Apply limit if specified
            return options.limit ? recommendations.slice(0, options.limit) : recommendations;
            
        } catch (error) {
            logger.error('Failed to get recommended tasks', error);
            throw error;
        }
    }

    /**
     * Analyze task complexity and dependencies
     * @param {number} taskId - Task to analyze
     * @returns {Object} Task analysis
     */
    analyzeTask(taskId) {
        try {
            const task = this.graph.node(taskId.toString());
            if (!task) {
                throw new Error(`Task ${taskId} not found`);
            }
            
            const downstream = this.getAllDownstreamTasks(taskId);
            const crossRepoDeps = this.getCrossRepoDependencies(taskId);
            const crossRepoDependent = this.getCrossRepoDependents(taskId);
            
            return {
                task,
                impact: {
                    blockedTasks: downstream.length,
                    crossRepoDependencies: crossRepoDeps.length,
                    crossRepoDependents: crossRepoDependent.length,
                    affectedRepositories: [
                        ...new Set([
                            task.repository,
                            ...crossRepoDeps.map(t => t.repository),
                            ...crossRepoDependent.map(t => t.repository)
                        ])
                    ]
                },
                milestone: task.milestone ? {
                    name: task.milestone,
                    status: this.getMilestoneStatus(task.milestone)
                } : null,
                recommendations: {
                    shouldPrioritize: downstream.length > 0 || crossRepoDeps.length > 0,
                    blocksHighPriority: downstream.some(t => t.priority === 'high'),
                    suggestedNextSteps: this.getSuggestedNextSteps(taskId)
                }
            };
        } catch (error) {
            logger.error(`Failed to analyze task ${taskId}`, error);
            throw error;
        }
    }

    /**
     * Get suggested next steps for a task
     * @param {number} taskId - Task to get suggestions for
     * @returns {Array} List of suggested next steps
     */
    getSuggestedNextSteps(taskId) {
        try {
            const task = this.graph.node(taskId.toString());
            const suggestions = [];
            
            // Check dependencies
            const deps = this.getCrossRepoDependencies(taskId);
            if (deps.length > 0) {
                suggestions.push({
                    type: 'dependency',
                    message: `Coordinate with ${deps.length} cross-repo dependencies`,
                    details: deps.map(d => `${d.repository}#${d.id}`)
                });
            }
            
            // Check milestone
            if (task.milestone) {
                const status = this.getMilestoneStatus(task.milestone);
                if (status.percentComplete < 50) {
                    suggestions.push({
                        type: 'milestone',
                        message: `Prioritize to help complete milestone ${task.milestone}`,
                        details: `Currently at ${status.percentComplete.toFixed(1)}%`
                    });
                }
            }
            
            // Check blocking status
            const downstream = this.getAllDownstreamTasks(taskId);
            if (downstream.length > 0) {
                suggestions.push({
                    type: 'blocking',
                    message: `Unblocks ${downstream.length} other tasks`,
                    details: downstream.map(t => `#${t.id}`)
                });
            }
            
            return suggestions;
        } catch (error) {
            logger.error(`Failed to get suggestions for task ${taskId}`, error);
            throw error;
        }
    }
}

export default DAGManager;
