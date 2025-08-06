import os from 'os';
import fetch from 'node-fetch';

// Test individual components of user tracking
async function testComponents() {
  console.log('=================================');
  console.log('Testing User Tracking Components');
  console.log('=================================\n');

  // Test 1: Get current user
  console.log('🔍 Test 1: Getting current user...');
  try {
    const user = os.userInfo().username;
    console.log(`✅ Current user: ${user}`);
  } catch (error) {
    console.log(`❌ Failed to get current user: ${error.message}`);
  }

  // Test 2: Test LDAP lookup (this will likely fail outside Intel network)
  console.log('\n🔍 Test 2: Testing LDAP lookup...');
  try {
    const user = os.userInfo().username;
    const url = `https://ldapagator.apps1-ir-int.icloud.intel.com/user?username=${user}`;
    
    // Create an HTTPS agent that ignores SSL certificate errors
    const https = await import('https');
    const agent = new https.default.Agent({
      rejectUnauthorized: false
    });
    
    const response = await fetch(url, {
      method: 'GET',
      agent: agent,
      timeout: 5000 // 5 second timeout
    });

    if (response.status === 200) {
      const data = await response.json();
      console.log(`✅ LDAP lookup successful for user: ${user}`);
      console.log(`📧 Email found: ${data.email || 'No email in response'}`);
    } else {
      console.log(`⚠️ LDAP lookup returned status: ${response.status}`);
    }
  } catch (error) {
    console.log(`⚠️ LDAP lookup failed (expected outside Intel network): ${error.message}`);
  }

  // Test 3: Test MongoDB availability (this will likely fail)
  console.log('\n🔍 Test 3: Testing MongoDB connection...');
  try {
    // Dynamic import of MongoDB
    const importMongoDB = new Function('return import("mongodb")');
    const { MongoClient } = await importMongoDB();
    
    const connectionString = 'mongodb://ExpertGPTDB_rw:12zWgSh5cBl19E9@p1ir1mon019.ger.corp.intel.com:7181,p2ir1mon019.ger.corp.intel.com:7181,p3ir1mon019.ger.corp.intel.com:7181/ExpertGPTDB?ssl=true&replicaSet=mongo7181';
    
    const client = new MongoClient(connectionString);
    
    // Set a short timeout
    await Promise.race([
      client.connect(),
      new Promise((_, reject) => setTimeout(() => reject(new Error('Connection timeout')), 5000))
    ]);
    
    console.log('✅ MongoDB connection successful!');
    
    const db = client.db('ExpertGPTDB');
    const collection = db.collection('tracking');
    
    // Try to perform a simple operation
    const count = await collection.countDocuments({});
    console.log(`📊 Found ${count} tracking records in database`);
    
    await client.close();
  } catch (error) {
    console.log(`⚠️ MongoDB connection failed (expected outside Intel network): ${error.message}`);
  }

  console.log('\n=================================');
  console.log('Component Test Summary:');
  console.log('- User tracking is designed to fail silently');
  console.log('- CLI will work normally even if tracking fails');
  console.log('- Tracking only works on Intel network with proper access');
  console.log('=================================');
}

testComponents().catch(console.error);
