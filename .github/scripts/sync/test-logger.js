const Logger = require('./logger');

async function testLogger() {
    console.log('Testing Logger...\n');
    
    // Create logger instance
    const logger = new Logger('TEST');
    
    // Test basic logging
    console.log('1. Testing basic logging:');
    logger.info('This is an info message');
    logger.warn('This is a warning message');
    logger.error('This is an error message');
    
    // Test error with Error object
    console.log('\n2. Testing error with Error object:');
    logger.error('Failed operation', new Error('Something went wrong'));
    
    // Test debug logging
    console.log('\n3. Testing debug logging (should only show if DEBUG=true):');
    process.env.DEBUG = 'true';
    logger.debug('This is a debug message');
    delete process.env.DEBUG;
    logger.debug('This debug message should not show');
    
    // Test activity logging
    console.log('\n4. Testing activity logging in DEVELOPMENT_STATUS.yaml:');
    try {
        await logger.logActivity(
            'test_action',
            'Testing logger functionality',
            1
        );
        console.log('Activity logged successfully');
    } catch (error) {
        console.error('Failed to log activity:', error);
    }
}

testLogger();
