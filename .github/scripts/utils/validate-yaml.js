const fs = require('fs').promises;
const path = require('path');
const yaml = require('js-yaml');
const Ajv = require('ajv');
const addFormats = require('ajv-formats');

async function validateYamlFile(filePath) {
    try {
        // Read the schema
        const schemaPath = path.join(__dirname, 'schemas', 'status.schema.json');
        const schemaContent = await fs.readFile(schemaPath, 'utf8');
        const schema = JSON.parse(schemaContent);

        // Read the YAML file
        const yamlContent = await fs.readFile(filePath, 'utf8');
        const data = yaml.load(yamlContent);

        // Initialize validator
        const ajv = new Ajv({ allErrors: true });
        addFormats(ajv);
        const validate = ajv.compile(schema);

        // Validate the data
        const valid = validate(data);

        if (!valid) {
            console.error(`Validation failed for ${filePath}:`);
            validate.errors.forEach(error => {
                console.error(`- ${error.instancePath}: ${error.message}`);
            });
            process.exit(1);
        }

        // Additional custom validations
        validateDependencyConsistency(data);
        validateCrossRepoRefs(data);
        validateTaskIds(data);

        console.log(`✓ ${filePath} is valid`);
        return true;
    } catch (error) {
        console.error(`Error validating ${filePath}:`, error.message);
        process.exit(1);
    }
}

function validateDependencyConsistency(data) {
    if (!data || !data.tasks) {
        throw new Error('Invalid data structure: missing tasks array');
    }
    
    // Check if all dependency references exist as tasks
    const taskIds = new Set(data.tasks.map(task => task.id));
    
    // Check task dependencies
    data.tasks.forEach(task => {
        (task.dependencies || []).forEach(depId => {
            if (!taskIds.has(depId)) {
                throw new Error(`Task ${task.id} references non-existent dependency ${depId}`);
            }
        });
    });

    // Check global dependencies
    Object.entries(data.dependencies || {}).forEach(([taskId, deps]) => {
        if (!taskIds.has(parseInt(taskId))) {
            throw new Error(`Dependencies list references non-existent task ${taskId}`);
        }
        deps.forEach(depId => {
            if (!taskIds.has(depId)) {
                throw new Error(`Task ${taskId} has non-existent dependency ${depId}`);
            }
        });
    });
}

function validateCrossRepoRefs(data) {
    if (!data || !data.tasks) {
        throw new Error('Invalid data structure: missing tasks array');
    }

    const validRepos = ['trade-manager', 'trade-dashboard', 'trade-discovery', 'market-analysis'];
    
    data.tasks.forEach(task => {
        (task.cross_repo_refs || []).forEach(ref => {
            if (!validRepos.includes(ref.repo)) {
                throw new Error(`Task ${task.id} references invalid repository ${ref.repo}`);
            }
            if (!Number.isInteger(ref.issue) || ref.issue <= 0) {
                throw new Error(`Task ${task.id} has invalid issue number ${ref.issue}`);
            }
        });
    });
}

function validateTaskIds(data) {
    if (!data || !data.tasks) {
        throw new Error('Invalid data structure: missing tasks array');
    }

    // Check for duplicate task IDs
    const seenIds = new Set();
    data.tasks.forEach(task => {
        if (seenIds.has(task.id)) {
            throw new Error(`Duplicate task ID ${task.id}`);
        }
        seenIds.add(task.id);
    });
}

// Main execution
if (require.main === module) {
    const files = process.argv.slice(2);
    if (files.length === 0) {
        console.error('No files provided for validation');
        process.exit(1);
    }

    Promise.all(files.map(validateYamlFile))
        .catch(error => {
            console.error('Validation failed:', error);
            process.exit(1);
        });
}

module.exports = {
    validateYamlFile,
    validateDependencyConsistency,
    validateCrossRepoRefs,
    validateTaskIds
};
