import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import DAGManager from './dag.js';
import YamlManager from './yaml.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testBasicFunctionality() {
    console.log('\n=== Testing Basic Functionality ===\n');
    const dagManager = new DAGManager(path.resolve(__dirname, '../../..'));
    
    try {
        // 1. Test graph building
        console.log('1. Testing graph building:');
        const graph = dagManager.buildGraph();
        console.log(`Graph built with ${graph.nodes().length} nodes\n`);
        
        // 2. Test cycle detection
        console.log('2. Testing cycle detection:');
        const hasCycles = dagManager.hasCycles();
        console.log(`Graph ${hasCycles ? 'has' : 'does not have'} cycles\n`);
        
        if (hasCycles) {
            const cycles = dagManager.findCycles();
            console.log('Found cycles:', cycles, '\n');
        }
        
        // 3. Test available tasks
        console.log('3. Testing available tasks:');
        const available = dagManager.getAvailableTasks();
        console.log(`Found ${available.length} available tasks\n`);
        
        // 4. Test task status update
        console.log('4. Testing task status update:');
        if (available.length > 0) {
            const taskId = available[0].id;
            const affected = await dagManager.updateTaskStatus(taskId, 'in_progress');
            console.log(`Updated task ${taskId}, affected ${affected.length} other tasks\n`);
            
            // Reset status
            await dagManager.updateTaskStatus(taskId, 'ready');
        }
        
        // 5. Test dependency validation
        console.log('5. Testing dependency validation:');
        const validation = dagManager.validateDependencies();
        console.log('Validation results:', validation, '\n');
        
        return true;
    } catch (error) {
        console.error('Basic functionality test failed:', error);
        return false;
    }
}

async function testEdgeCases() {
    console.log('\n=== Testing Edge Cases ===\n');
    const dagManager = new DAGManager(path.resolve(__dirname, '../../..'));
    const yamlManager = new YamlManager(path.resolve(__dirname, '../../..'));
    
    try {
        // 1. Test empty task list
        console.log('1. Testing empty task list:');
        const originalData = yamlManager.readStatus();
        const backupPath = yamlManager.createBackup();
        
        // Temporarily remove all tasks
        await yamlManager.updateTask(1, { dependencies: [] });
        dagManager.buildGraph();
        const emptyAvailable = dagManager.getAvailableTasks();
        console.log(`Empty graph available tasks: ${emptyAvailable.length}\n`);
        
        // Restore backup
        yamlManager.restoreFromBackup(backupPath);
        
        // 2. Test invalid task status
        console.log('2. Testing invalid task status:');
        try {
            await dagManager.updateTaskStatus(999, 'invalid_status');
            console.log('❌ Should have thrown error for invalid task\n');
        } catch (error) {
            console.log('✅ Correctly handled invalid task ID\n');
        }
        
        // 3. Test self-referential task
        console.log('3. Testing self-referential task:');
        const task = originalData.next_available_tasks[0];
        const originalDeps = [...(task.dependencies || [])];
        
        // Add self as dependency
        await yamlManager.updateTask(task.id, {
            dependencies: [...(task.dependencies || []), task.id]
        });
        
        dagManager.buildGraph();
        const validation = dagManager.validateDependencies();
        console.log('Validation with self-reference:', validation);
        
        // Restore original dependencies
        await yamlManager.updateTask(task.id, {
            dependencies: originalDeps
        });
        console.log('Restored original dependencies\n');
        
        return true;
    } catch (error) {
        console.error('Edge case test failed:', error);
        return false;
    }
}

async function testErrorConditions() {
    console.log('\n=== Testing Error Conditions ===\n');
    const dagManager = new DAGManager(path.resolve(__dirname, '../../..'));
    
    try {
        // 1. Test null/undefined handling
        console.log('1. Testing null/undefined handling:');
        try {
            await dagManager.updateTaskStatus(null, 'ready');
            console.log('❌ Should have thrown error for null task ID\n');
        } catch (error) {
            console.log('✅ Correctly handled null task ID\n');
        }
        
        // 2. Test concurrent updates
        console.log('2. Testing concurrent updates:');
        const taskId = 1;
        const updates = [
            dagManager.updateTaskStatus(taskId, 'in_progress'),
            dagManager.updateTaskStatus(taskId, 'completed'),
            dagManager.updateTaskStatus(taskId, 'ready')
        ];
        
        await Promise.all(updates);
        const finalStatus = dagManager.graph.node(taskId.toString()).status;
        console.log(`Final task status after concurrent updates: ${finalStatus}\n`);
        
        // Reset status
        await dagManager.updateTaskStatus(taskId, 'ready');
        
        // 3. Test circular dependency detection
        console.log('3. Testing circular dependency detection:');
        const yamlManager = new YamlManager(path.resolve(__dirname, '../../..'));
        const backupPath = yamlManager.createBackup();
        
        // Create a circular dependency
        const task1 = 1;
        const task2 = 2;
        await yamlManager.updateTask(task1, {
            dependencies: [task2]
        });
        await yamlManager.updateTask(task2, {
            dependencies: [task1]
        });
        
        dagManager.buildGraph();
        const hasCycles = dagManager.hasCycles();
        console.log(`Circular dependency detected: ${hasCycles}`);
        
        // Restore backup
        yamlManager.restoreFromBackup(backupPath);
        console.log('Restored original dependencies\n');
        
        return true;
    } catch (error) {
        console.error('Error condition test failed:', error);
        return false;
    }
}

async function testCrossRepoFeatures() {
    console.log('\n=== Testing Cross-Repository Features ===\n');
    const dagManager = new DAGManager(path.resolve(__dirname, '../../..'));
    const yamlManager = new YamlManager(path.resolve(__dirname, '../../..'));
    
    try {
        // Setup: Create cross-repo dependencies
        console.log('1. Setting up cross-repo dependencies:');
        const backupPath = yamlManager.createBackup();
        
        // Add cross-repo dependencies
        await yamlManager.updateTask(1, {
            dependencies: [2],
            repository: 'trade-manager'
        });
        await yamlManager.updateTask(2, {
            dependencies: [],
            repository: 'trade-dashboard'
        });
        
        dagManager.buildGraph();
        
        // 1. Test cross-repo dependency detection
        console.log('2. Testing cross-repo dependency detection:');
        const crossRepoDeps = dagManager.getCrossRepoDependencies(1);
        console.log(`Found ${crossRepoDeps.length} cross-repo dependencies`);
        
        // 2. Test cross-repo dependents
        console.log('\n3. Testing cross-repo dependents:');
        const crossRepoDependents = dagManager.getCrossRepoDependents(2);
        console.log(`Found ${crossRepoDependents.length} cross-repo dependents`);
        
        // 3. Test all cross-repo dependencies
        console.log('\n4. Testing all cross-repo dependencies:');
        const allCrossRepoDeps = dagManager.getAllCrossRepoDependencies();
        console.log(`Found ${allCrossRepoDeps.length} total cross-repo relationships`);
        
        // Restore original data
        yamlManager.restoreFromBackup(backupPath);
        console.log('\nRestored original dependencies');
        
        return true;
    } catch (error) {
        console.error('Cross-repo feature test failed:', error);
        return false;
    }
}

async function testProjectStatus() {
    console.log('\n=== Testing Project Status Features ===\n');
    const dagManager = new DAGManager(path.resolve(__dirname, '../../..'));
    const yamlManager = new YamlManager(path.resolve(__dirname, '../../..'));
    
    try {
        // Setup: Add milestone data
        console.log('1. Setting up milestone data:');
        const backupPath = yamlManager.createBackup();
        
        await yamlManager.updateTask(1, {
            milestone: 'alpha',
            status: 'completed'
        });
        await yamlManager.updateTask(2, {
            milestone: 'alpha',
            status: 'in_progress'
        });
        await yamlManager.updateTask(3, {
            milestone: 'beta',
            status: 'ready'
        });
        
        dagManager.buildGraph();
        
        // 1. Test milestone task retrieval
        console.log('2. Testing milestone task retrieval:');
        const alphaTasks = dagManager.getTasksByMilestone('alpha');
        console.log(`Found ${alphaTasks.length} tasks in alpha milestone`);
        
        // 2. Test milestone status
        console.log('\n3. Testing milestone status:');
        const alphaStatus = dagManager.getMilestoneStatus('alpha');
        console.log('Alpha milestone status:', alphaStatus);
        
        // 3. Test project-wide status
        console.log('\n4. Testing project-wide status:');
        const projectStatus = dagManager.getProjectStatus();
        console.log('Project status:', JSON.stringify(projectStatus, null, 2));
        
        // Restore original data
        yamlManager.restoreFromBackup(backupPath);
        console.log('\nRestored original data');
        
        return true;
    } catch (error) {
        console.error('Project status test failed:', error);
        return false;
    }
}

async function testTaskPrioritization() {
    console.log('\n=== Testing Task Prioritization Features ===\n');
    const dagManager = new DAGManager(path.resolve(__dirname, '../../..'));
    const yamlManager = new YamlManager(path.resolve(__dirname, '../../..'));
    
    try {
        // Setup test data
        console.log('1. Setting up test data:');
        const backupPath = yamlManager.createBackup();
        
        // Create a complex dependency structure
        await yamlManager.updateTask(1, {
            milestone: 'alpha',
            complexity: 2,
            status: 'ready',
            repository: 'trade-manager'
        });
        await yamlManager.updateTask(2, {
            milestone: 'alpha',
            complexity: 4,
            status: 'ready',
            repository: 'trade-dashboard',
            dependencies: [1]
        });
        await yamlManager.updateTask(3, {
            milestone: 'beta',
            complexity: 1,
            status: 'ready',
            repository: 'trade-manager',
            dependencies: [2]
        });
        
        dagManager.buildGraph();
        
        // 1. Test critical path detection
        console.log('2. Testing critical path detection:');
        const criticalTasks = dagManager.getCriticalPathTasks();
        console.log(`Found ${criticalTasks.length} tasks on critical path`);
        console.log('Most critical task blocks', criticalTasks[0].totalDownstream, 'tasks\n');
        
        // 2. Test task recommendations
        console.log('3. Testing task recommendations:');
        const recommendations = dagManager.getRecommendedTasks({
            limit: 2
        });
        console.log(`Top recommendation: Task #${recommendations[0].task.id}`);
        console.log('Reasons:', recommendations[0].reasons, '\n');
        
        // 3. Test task analysis
        console.log('4. Testing task analysis:');
        const analysis = dagManager.analyzeTask(1);
        console.log('Task analysis:', JSON.stringify(analysis, null, 2), '\n');
        
        // 4. Test suggested next steps
        console.log('5. Testing suggested next steps:');
        const suggestions = dagManager.getSuggestedNextSteps(1);
        console.log('Suggested steps:', suggestions, '\n');
        
        // Restore original data
        yamlManager.restoreFromBackup(backupPath);
        console.log('Restored original data');
        
        return true;
    } catch (error) {
        console.error('Task prioritization test failed:', error);
        return false;
    }
}

async function runAllTests() {
    console.log('Starting comprehensive DAG Manager tests...');
    
    const results = {
        basicFunctionality: await testBasicFunctionality(),
        edgeCases: await testEdgeCases(),
        errorConditions: await testErrorConditions(),
        crossRepoFeatures: await testCrossRepoFeatures(),
        projectStatus: await testProjectStatus(),
        taskPrioritization: await testTaskPrioritization()
    };
    
    console.log('\n=== Test Results Summary ===');
    Object.entries(results).forEach(([test, passed]) => {
        console.log(`${test}: ${passed ? '✅ PASSED' : '❌ FAILED'}`);
    });
    
    const allPassed = Object.values(results).every(r => r);
    console.log(`\nOverall Result: ${allPassed ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);
}

runAllTests();
