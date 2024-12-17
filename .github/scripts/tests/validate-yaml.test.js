const fs = require('fs').promises;
const path = require('path');
const yaml = require('js-yaml');

// Mock the process.exit
jest.spyOn(process, 'exit').mockImplementation(() => {});
jest.spyOn(console, 'error').mockImplementation(() => {});

// Create test YAML files
const validYaml = {
  project_phase: "development",
  tasks: [
    {
      id: 1,
      title: "Test Task",
      status: "pending",
      dependencies: [2],
      cross_repo_refs: [
        {
          repo: "trade-dashboard",
          issue: 123
        }
      ]
    },
    {
      id: 2,
      title: "Dependency Task",
      status: "completed"
    }
  ],
  dependencies: {
    "1": [2]
  },
  metadata: {
    last_updated: "2024-12-17T14:44:17-06:00",
    version: "1.0.0"
  }
};

const invalidYaml = {
  project_phase: "invalid_phase",
  tasks: [
    {
      id: 1,
      title: "",  // Invalid: empty title
      status: "unknown_status"  // Invalid: unknown status
    }
  ],
  dependencies: {
    "1": [999]  // Invalid: non-existent dependency
  }
};

const duplicateIdsYaml = {
  project_phase: "development",
  tasks: [
    {
      id: 1,
      title: "Task 1",
      status: "pending"
    },
    {
      id: 1,  // Duplicate ID
      title: "Task 2",
      status: "pending"
    }
  ],
  dependencies: {}
};

describe('YAML Validation Tests', () => {
  beforeAll(async () => {
    // Create test YAML files
    await fs.writeFile(
      path.join(__dirname, 'fixtures', 'valid.yaml'),
      yaml.dump(validYaml)
    );
    await fs.writeFile(
      path.join(__dirname, 'fixtures', 'invalid.yaml'),
      yaml.dump(invalidYaml)
    );
    await fs.writeFile(
      path.join(__dirname, 'fixtures', 'duplicate-ids.yaml'),
      yaml.dump(duplicateIdsYaml)
    );
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('validates a correct YAML file', async () => {
    const { validateYamlFile } = require('../utils/validate-yaml.js');
    const result = await validateYamlFile(path.join(__dirname, 'fixtures', 'valid.yaml'));
    expect(result).toBe(true);
    expect(process.exit).not.toHaveBeenCalled();
  });

  test('fails on invalid project phase', async () => {
    const { validateYamlFile } = require('../utils/validate-yaml.js');
    await validateYamlFile(path.join(__dirname, 'fixtures', 'invalid.yaml'));
    expect(process.exit).toHaveBeenCalledWith(1);
    expect(console.error).toHaveBeenCalled();
  });

  test('fails on duplicate task IDs', async () => {
    const { validateYamlFile } = require('../utils/validate-yaml.js');
    await validateYamlFile(path.join(__dirname, 'fixtures', 'duplicate-ids.yaml'));
    expect(process.exit).toHaveBeenCalledWith(1);
    expect(console.error).toHaveBeenCalledWith(
      'Error validating C:\\Users\\Butle\\Desktop\\Preston\\gitRepos\\trade-manager\\.github\\scripts\\tests\\fixtures\\duplicate-ids.yaml:',
      'Duplicate task ID 1'
    );
  });

  test('validates cross-repo references', () => {
    const { validateCrossRepoRefs } = require('../utils/validate-yaml.js');
    expect(() => validateCrossRepoRefs(validYaml)).not.toThrow();
    
    const invalidRepo = {
      ...validYaml,
      tasks: [{
        ...validYaml.tasks[0],
        cross_repo_refs: [{ repo: 'invalid-repo', issue: 1 }]
      }]
    };
    expect(() => validateCrossRepoRefs(invalidRepo)).toThrow();
  });

  test('validates dependency consistency', () => {
    const { validateDependencyConsistency } = require('../utils/validate-yaml.js');
    expect(() => validateDependencyConsistency(validYaml)).not.toThrow();
    expect(() => validateDependencyConsistency(invalidYaml)).toThrow();
  });
});
