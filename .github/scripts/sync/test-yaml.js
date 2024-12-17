import YamlManager from './yaml.js';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testYamlManager() {
    console.log('Testing YamlManager...\n');
    
    // Create YamlManager instance
    const yamlManager = new YamlManager(path.resolve(__dirname, '../../..'));
    
    try {
        // Test reading YAML
        console.log('1. Testing YAML reading:');
        const data = yamlManager.readStatus();
        console.log('Successfully read YAML file');
        console.log(`Found ${data.next_available_tasks.length} tasks\n`);
        
        // Test backup creation
        console.log('2. Testing backup creation:');
        const backupPath = yamlManager.createBackup();
        console.log(`Created backup at: ${backupPath}\n`);
        
        // Test task update
        console.log('3. Testing task update:');
        const taskId = data.next_available_tasks[0].id;
        const originalStatus = data.next_available_tasks[0].status;
        const updatedTask = yamlManager.updateTask(taskId, {
            status: 'test_status'
        });
        console.log('Task updated successfully');
        
        // Test getting all tasks with dependencies
        console.log('\n4. Testing getAllTasks:');
        const tasks = yamlManager.getAllTasks();
        console.log(`Retrieved ${tasks.length} tasks with dependencies`);
        
        // Test updating task dependencies
        console.log('\n5. Testing dependency updates:');
        const updatedDeps = yamlManager.updateTaskDependencies(taskId, [2, 3], [4, 5]);
        console.log('Dependencies updated successfully');
        
        // Test cross-repo references
        console.log('\n6. Testing cross-repo references:');
        const refs = yamlManager.getCrossRepoReferences();
        console.log('Cross-repo references retrieved:', Object.keys(refs).length);
        
        // Validate structure
        console.log('\n7. Testing YAML structure validation:');
        const isValid = yamlManager.validateStructure(data);
        console.log(`YAML structure is ${isValid ? 'valid' : 'invalid'}\n`);
        
        // Restore original status
        yamlManager.updateTask(taskId, {
            status: originalStatus
        });
        console.log('Restored original task status\n');
        
        // Test restore from backup
        console.log('8. Testing restore from backup:');
        yamlManager.restoreFromBackup(backupPath);
        console.log('Successfully restored from backup');
        
    } catch (error) {
        console.error('Test failed:', error);
    }
}

testYamlManager();
