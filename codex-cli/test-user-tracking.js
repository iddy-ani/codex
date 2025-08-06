#!/usr/bin/env node

// Test script for user tracking functionality
import { userTracker } from './dist/user-tracking-simple.js';

async function testUserTracking() {
  console.log('=================================');
  console.log('Testing ExpertGPT Codex User Tracking');
  console.log('=================================\n');

  try {
    console.log('🔍 Testing user tracking functionality...');
    
    // Test the tracking method
    await userTracker.trackUser('test-run');
    
    console.log('✅ User tracking test completed successfully!');
    console.log('📝 If this was successful, a record should be added to the ExpertGPTDB tracking collection');
    console.log('💡 Note: Tracking fails silently if MongoDB is unavailable or LDAP lookup fails');
    
  } catch (error) {
    console.log('❌ User tracking test failed:');
    console.error(error.message);
    console.log('\n🔧 This is expected if:');
    console.log('   - MongoDB is not installed');
    console.log('   - Network connection to Intel MongoDB is unavailable');
    console.log('   - LDAP service is unreachable');
    console.log('   - User is not on Intel network');
  }
  
  console.log('\n=================================');
  console.log('Test completed');
  console.log('=================================');
}

// Run the test
testUserTracking().catch(console.error);
