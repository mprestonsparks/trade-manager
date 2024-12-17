import { TaskDecomposer } from './task-decomposition.js';

async function runDecompositionTests() {
    console.log('\n=== Testing Task Decomposition Features ===\n');
    
    // For testing purposes, we'll create mock manager objects
    const mockYamlManager = {
        getTask: async (id) => ({ id, status: 'ready' }),
        createTask: async (task) => Math.floor(Math.random() * 1000),
        updateTask: async (id, task) => true
    };

    const mockDagManager = {
        rebuildGraph: async () => true
    };

    const decomposer = new TaskDecomposer(mockDagManager, mockYamlManager);

    // Test 1: Analyzing vague tasks
    console.log('1. Testing vague task analysis:');
    const vagueTask = {
        id: 1,
        title: 'Create frontend UI',
        status: 'ready',
        repository: 'trade-dashboard'
    };

    const analysis = decomposer.analyzeTaskGranularity(vagueTask);
    console.log('Analysis results:', JSON.stringify(analysis, null, 2));

    // Test 2: Generating technical implementation plan
    console.log('\n2. Testing technical implementation suggestions:');
    const techPlan = decomposer.suggestTechnicalImplementation(vagueTask);
    console.log('Technical plan:', JSON.stringify(techPlan, null, 2));

    // Test 3: Subtask generation
    console.log('\n3. Testing subtask generation:');
    const subtasks = decomposer.generateSubtasks(vagueTask);
    console.log('Generated subtasks:', JSON.stringify(subtasks, null, 2));

    // Test 4: Testing API task decomposition
    console.log('\n4. Testing API task decomposition:');
    const apiTask = {
        id: 2,
        title: 'Create FastAPI backend',
        status: 'ready',
        repository: 'trade-manager'
    };

    const apiAnalysis = decomposer.analyzeTaskGranularity(apiTask);
    console.log('API task analysis:', JSON.stringify(apiAnalysis, null, 2));

    // Test 5: Creating subtasks in system
    console.log('\n5. Testing subtask creation:');
    try {
        await decomposer.createSubtasks(1, subtasks.slice(0, 2));
        console.log('Successfully created subtasks');
    } catch (error) {
        console.error('Failed to create subtasks:', error);
    }

    console.log('\n=== Task Decomposition Tests Complete ===');
}

runDecompositionTests();
