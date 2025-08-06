import os from 'os';

async function verifyTrackingRecord() {
  console.log('=================================');
  console.log('Verifying User Tracking Record Creation');
  console.log('=================================\n');

  try {
    // Dynamic import of MongoDB
    const importMongoDB = new Function('return import("mongodb")');
    const { MongoClient } = await importMongoDB();
    
    const connectionString = 'mongodb://ExpertGPTDB_rw:12zWgSh5cBl19E9@p1ir1mon019.ger.corp.intel.com:7181,p2ir1mon019.ger.corp.intel.com:7181,p3ir1mon019.ger.corp.intel.com:7181/ExpertGPTDB?ssl=true&replicaSet=mongo7181';
    
    const client = new MongoClient(connectionString, {
      tls: true,
      tlsAllowInvalidCertificates: true,
      tlsAllowInvalidHostnames: true,
      serverSelectionTimeoutMS: 10000,
      connectTimeoutMS: 10000,
      socketTimeoutMS: 10000
    });
    
    await client.connect();
    console.log('✅ Connected to MongoDB');
    
    const db = client.db('ExpertGPTDB');
    const collection = db.collection('tracking');
    
    // Get the most recent records for the current user
    const recentRecords = await collection.find({
      email: 'idriss.animashaun@intel.com'
    }).sort({ timestamp: -1 }).limit(5).toArray();
    
    console.log(`📊 Most recent 5 tracking records for idriss.animashaun@intel.com:`);
    
    recentRecords.forEach((record, index) => {
      const minutesAgo = Math.round((Date.now() - record.timestamp.getTime()) / 1000 / 60);
      console.log(`${index + 1}. Method: ${record.method}`);
      console.log(`   Timestamp: ${record.timestamp.toISOString()}`);
      console.log(`   Time ago: ${minutesAgo} minutes ago\n`);
    });
    
    // Check for recent 'codex' method records specifically
    const recentCodexRecords = await collection.find({
      email: 'idriss.animashaun@intel.com',
      method: 'codex',
      timestamp: { $gte: new Date(Date.now() - (2 * 60 * 60 * 1000)) } // Last 2 hours
    }).sort({ timestamp: -1 }).toArray();
    
    console.log(`🔍 Found ${recentCodexRecords.length} 'codex' method records in the last 2 hours:`);
    
    recentCodexRecords.forEach((record, index) => {
      const minutesAgo = Math.round((Date.now() - record.timestamp.getTime()) / 1000 / 60);
      console.log(`${index + 1}. Timestamp: ${record.timestamp.toISOString()} (${minutesAgo} minutes ago)`);
    });
    
    if (recentCodexRecords.length > 0) {
      console.log('\n✅ SUCCESS: User tracking is working correctly!');
      console.log('✅ CLI is creating "codex" method tracking records');
      console.log('✅ Ready for distribution package');
    } else {
      console.log('\n⚠️ No recent "codex" method records found');
      console.log('   This could mean:');
      console.log('   - Tracking is being skipped due to recent activity');
      console.log('   - There was an error in the tracking implementation');
      console.log('   - The CLI tracking is not executing properly');
    }
    
    await client.close();
    
  } catch (error) {
    console.log('❌ Failed to verify tracking records:');
    console.error('Error:', error.message);
  }
  
  console.log('\n=================================');
  console.log('Verification Complete');
  console.log('=================================');
}

verifyTrackingRecord().catch(console.error);
