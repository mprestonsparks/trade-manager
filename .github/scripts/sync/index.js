const { program } = require('commander');
const GitHubManager = require('./github');
const Logger = require('./logger');

const logger = new Logger('Sync');

program
    .name('sync')
    .description('Sync between GitHub Project V2 and local YAML files');

program
    .command('sync-to-local')
    .description('Sync from GitHub Project V2 to local YAML')
    .requiredOption('--token <token>', 'GitHub token')
    .requiredOption('--owner <owner>', 'Repository owner')
    .requiredOption('--repo <repo>', 'Repository name')
    .requiredOption('--event <event>', 'GitHub event payload')
    .action(async (options) => {
        try {
            const github = new GitHubManager(options.token, options.owner, options.repo);
            const event = JSON.parse(options.event);
            await github.syncProjectToLocal(options.repo, event);
        } catch (error) {
            logger.error('Error in sync-to-local:', error);
            process.exit(1);
        }
    });

program
    .command('sync-to-project')
    .description('Sync from local YAML to GitHub Project V2')
    .requiredOption('--token <token>', 'GitHub token')
    .requiredOption('--owner <owner>', 'Repository owner')
    .requiredOption('--repo <repo>', 'Repository name')
    .requiredOption('--commit <commit>', 'Commit payload')
    .action(async (options) => {
        try {
            const github = new GitHubManager(options.token, options.owner, options.repo);
            const commit = JSON.parse(options.commit);
            await github.syncLocalToProject(options.repo, commit);
        } catch (error) {
            logger.error('Error in sync-to-project:', error);
            process.exit(1);
        }
    });

program.parse();
