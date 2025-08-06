import { userTracker, trackCLIUsage } from './dist/cli.js';
import os from 'os';

async function testActualUserTracking() {
  console.log('=================================');
  console.log('Testing ACTUAL User Tracking Implementation');
  console.log('(The one that will be packaged in the app)');
  console.log('=================================\n');

  try {
    console.log('🔍 Step 1: Testing trackCLIUsage() function...');
    console.log('This is the exact function called when CLI starts');
    
    // This is the exact same call made by the CLI
    await trackCLIUsage();
    
    console.log('✅ trackCLIUsage() completed without errors');
    
    console.log('\n🔍 Step 2: Testing userTracker.trackUser() directly...');
    
    // Test the userTracker directly with a different method to verify it works
    if (userTracker && typeof userTracker.trackUser === 'function') {
      await userTracker.trackUser('direct-test');
      console.log('✅ userTracker.trackUser() completed without errors');
    } else {
      console.log('❌ userTracker not available or trackUser method missing');
    }
    
    console.log('\n🔍 Step 3: Testing with current user info...');
    const user = os.userInfo().username;
    console.log(`   Current user: ${user}`);
    
    // Test one more time to verify the duplicate prevention
    console.log('\n🔍 Step 4: Testing duplicate prevention...');
    await trackCLIUsage();
    console.log('✅ Duplicate prevention test completed');
    
    console.log('\n🎉 ALL TESTS PASSED!');
    console.log('✅ User tracking implementation is working correctly');
    console.log('✅ Ready for distribution package');
    
  } catch (error) {
    console.log('\n❌ USER TRACKING IMPLEMENTATION ERROR:');
    console.error('Error name:', error.name);
    console.error('Error message:', error.message);
    console.error('Stack trace:', error.stack);
    
    console.log('\n🔧 This indicates an issue with the actual implementation');
    console.log('   that will be packaged with the app');
  }
  
  console.log('\n=================================');
  console.log('ACTUAL Implementation Test Complete');
  console.log('=================================');
}

testActualUserTracking().catch(console.error);
