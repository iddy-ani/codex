import os from 'os';

// Test the exact same logic as the user tracking
async function debugUserTracking() {
  console.log('=================================');
  console.log('Debug User Tracking Step by Step');
  console.log('=================================\n');

  const connectionString = 'mongodb://ExpertGPTDB_rw:12zWgSh5cBl19E9@p1ir1mon019.ger.corp.intel.com:7181,p2ir1mon019.ger.corp.intel.com:7181,p3ir1mon019.ger.corp.intel.com:7181/ExpertGPTDB?ssl=true&replicaSet=mongo7181';
  
  try {
    console.log('🔍 Step 1: Dynamic MongoDB import...');
    const importMongoDB = new Function('return import("mongodb")');
    const { MongoClient } = await importMongoDB();
    console.log('✅ MongoDB import successful');
    
    console.log('\n🔍 Step 2: Get current user...');
    const user = os.userInfo().username;
    console.log(`✅ Current user: ${user}`);
    
    console.log('\n🔍 Step 3: Get user email from LDAP...');
    const url = `https://ldapagator.apps1-ir-int.icloud.intel.com/user?username=${user}`;
    
    // Create an HTTPS agent that ignores SSL certificate errors
    const https = await import('https');
    const agent = new https.Agent({
      rejectUnauthorized: false
    });
    
    const fetch = (await import('node-fetch')).default;
    const response = await fetch(url, {
      method: 'GET',
      agent: agent
    });

    if (response.status !== 200) {
      console.log(`❌ LDAP lookup failed with status: ${response.status}`);
      return;
    }

    const data = await response.json();
    const userEmail = data.email;
    console.log(`✅ User email found: ${userEmail}`);
    
    if (!userEmail) {
      console.log('❌ No email found, tracking would stop here');
      return;
    }

    console.log('\n🔍 Step 4: Connect to MongoDB...');
    const client = new MongoClient(connectionString, {
      tls: true,
      tlsAllowInvalidCertificates: true,
      tlsAllowInvalidHostnames: true,
      serverSelectionTimeoutMS: 10000,
      connectTimeoutMS: 10000,
      socketTimeoutMS: 10000
    });
    await client.connect();
    console.log('✅ MongoDB connection successful');
    
    const db = client.db('ExpertGPTDB');
    const collection = db.collection('tracking');

    console.log('\n🔍 Step 5: Check for recent records...');
    const oneHourAgo = new Date(Date.now() - (60 * 60 * 1000));
    const recentRecord = await collection.findOne({
      email: userEmail,
      timestamp: { $gte: oneHourAgo }
    });

    if (recentRecord) {
      console.log('⚠️ Recent record found, tracking would be skipped:');
      console.log(`   Method: ${recentRecord.method}`);
      console.log(`   Timestamp: ${recentRecord.timestamp}`);
      console.log(`   Minutes ago: ${Math.round((Date.now() - recentRecord.timestamp.getTime()) / 1000 / 60)}`);
    } else {
      console.log('✅ No recent record found, proceeding with tracking...');
      
      console.log('\n🔍 Step 6: Insert tracking record...');
      const result = await collection.insertOne({
        email: userEmail,
        timestamp: new Date(),
        method: 'debug-test-codex'
      });
      console.log(`✅ Tracking record inserted with ID: ${result.insertedId}`);
    }

    await client.close();
    console.log('✅ MongoDB connection closed');
    
    console.log('\n🎉 All steps completed successfully!');
    console.log('The CLI user tracking should be working properly.');
    
  } catch (error) {
    console.log(`❌ Error during tracking:`, error.message);
    console.log('Stack trace:', error.stack);
  }
  
  console.log('\n=================================');
  console.log('Debug User Tracking Complete');
  console.log('=================================');
}

debugUserTracking().catch(console.error);
