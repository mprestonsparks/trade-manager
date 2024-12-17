import { default as DAGManager } from './dag.js';
import { default as YamlManager } from './yaml.js';

export class TaskDecomposer {
    constructor(dagManager, yamlManager) {
        this.dagManager = dagManager;
        this.yamlManager = yamlManager;
    }

    /**
     * Analyzes a task to determine if it needs decomposition
     * @param {Object} task - The task to analyze
     * @returns {Object} Analysis results
     */
    analyzeTaskGranularity(task) {
        const indicators = {
            needsDecomposition: false,
            reasons: [],
            suggestedSubtasks: []
        };

        // Check for vague or broad titles
        const broadTerms = ['create', 'implement', 'develop', 'setup', 'build'];
        if (broadTerms.some(term => task.title?.toLowerCase().startsWith(term))) {
            indicators.needsDecomposition = true;
            indicators.reasons.push('Task title suggests a broad scope');
        }

        // Check for missing technical details
        if (!task.technicalDetails || Object.keys(task.technicalDetails || {}).length === 0) {
            indicators.needsDecomposition = true;
            indicators.reasons.push('Missing technical implementation details');
        }

        // Check for missing acceptance criteria
        if (!task.acceptanceCriteria || task.acceptanceCriteria.length === 0) {
            indicators.needsDecomposition = true;
            indicators.reasons.push('Missing acceptance criteria');
        }

        // Generate suggested subtasks based on the analysis
        if (indicators.needsDecomposition) {
            indicators.suggestedSubtasks = this.generateSubtasks(task);
        }

        return indicators;
    }

    /**
     * Generates suggested subtasks based on task type and domain
     * @param {Object} task - The parent task
     * @returns {Array} List of suggested subtasks
     */
    generateSubtasks(task) {
        const subtasks = [];
        const title = task.title?.toLowerCase() || '';

        // Frontend UI task template
        if (title.includes('frontend') || title.includes('ui')) {
            subtasks.push(
                { title: 'Define component architecture and data flow', type: 'planning' },
                { title: 'Create UI component hierarchy', type: 'implementation' },
                { title: 'Implement core UI components', type: 'implementation' },
                { title: 'Add state management', type: 'implementation' },
                { title: 'Implement API integration layer', type: 'implementation' },
                { title: 'Add error handling and loading states', type: 'implementation' },
                { title: 'Create unit tests for components', type: 'testing' },
                { title: 'Add E2E tests for critical flows', type: 'testing' }
            );
        }

        // API task template
        if (title.includes('api') || title.includes('backend')) {
            subtasks.push(
                { title: 'Define API endpoints and schemas', type: 'planning' },
                { title: 'Create database models', type: 'implementation' },
                { title: 'Implement CRUD operations', type: 'implementation' },
                { title: 'Add authentication/authorization', type: 'security' },
                { title: 'Implement error handling', type: 'implementation' },
                { title: 'Add request validation', type: 'security' },
                { title: 'Create API documentation', type: 'documentation' },
                { title: 'Add unit tests for endpoints', type: 'testing' },
                { title: 'Implement integration tests', type: 'testing' }
            );
        }

        return subtasks;
    }

    /**
     * Creates new subtasks in the YAML and updates the DAG
     * @param {number} parentTaskId - The ID of the parent task
     * @param {Array} subtasks - List of subtasks to create
     */
    async createSubtasks(parentTaskId, subtasks) {
        const parent = await this.yamlManager.getTask(parentTaskId);
        if (!parent) throw new Error(`Parent task ${parentTaskId} not found`);

        const createdTasks = [];
        for (const subtask of subtasks) {
            const newTask = {
                ...subtask,
                status: 'ready',
                dependencies: [parentTaskId],
                repository: parent.repository,
                parentTask: parentTaskId
            };

            const taskId = await this.yamlManager.createTask(newTask);
            createdTasks.push(taskId);
        }

        // Update parent task to track subtasks
        await this.yamlManager.updateTask(parentTaskId, {
            ...parent,
            subtasks: createdTasks,
            status: 'in_progress'
        });

        // Rebuild DAG with new tasks
        await this.dagManager.rebuildGraph();
    }

    /**
     * Suggests a technical implementation plan for a task
     * @param {Object} task - The task to analyze
     * @returns {Object} Technical implementation details
     */
    suggestTechnicalImplementation(task) {
        const title = task.title?.toLowerCase() || '';
        const implementation = {
            technicalStack: [],
            architecturalConsiderations: [],
            securityConsiderations: [],
            testingRequirements: [],
            performanceConsiderations: []
        };

        if (title.includes('frontend') || title.includes('ui')) {
            implementation.technicalStack = [
                'React/Vue/Angular for component architecture',
                'TypeScript for type safety',
                'State management (Redux/Vuex)',
                'CSS-in-JS or SCSS for styling'
            ];
            implementation.architecturalConsiderations = [
                'Component reusability',
                'State management patterns',
                'API integration strategy'
            ];
        }

        if (title.includes('api') || title.includes('backend')) {
            implementation.technicalStack = [
                'FastAPI for API development',
                'SQLAlchemy for ORM',
                'Pydantic for data validation',
                'JWT for authentication'
            ];
            implementation.architecturalConsiderations = [
                'RESTful design principles',
                'Database schema design',
                'Error handling strategy'
            ];
        }

        // Add common considerations
        implementation.securityConsiderations = [
            'Input validation',
            'Authentication/Authorization',
            'Data sanitization'
        ];

        implementation.testingRequirements = [
            'Unit tests',
            'Integration tests',
            'E2E tests for critical paths'
        ];

        implementation.performanceConsiderations = [
            'Caching strategy',
            'Query optimization',
            'Load testing requirements'
        ];

        return implementation;
    }
}
