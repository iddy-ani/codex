import os from 'os';

async function checkMostRecentTracking() {
  console.log('=================================');
  console.log('Checking Most Recent Tracking');
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
    
    const db = client.db('ExpertGPTDB');
    const collection = db.collection('tracking');
    
    // Get the most recent records for this specific email
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
    
    // Check the very latest record
    if (recentRecords.length > 0) {
      const latestRecord = recentRecords[0];
      const minutesAgo = Math.round((Date.now() - latestRecord.timestamp.getTime()) / 1000 / 60);
      
      if (minutesAgo < 5) {
        console.log('✅ Recent tracking record found! User tracking is working.');
      } else {
        console.log('⚠️ Latest record is older than 5 minutes. CLI might not be tracking.');
      }
    }
    
    await client.close();
    
  } catch (error) {
    console.log('❌ Failed to check tracking records:');
    console.error('Error:', error.message);
  }
  
  console.log('\n=================================');
  console.log('Most Recent Tracking Check Complete');
  console.log('=================================');
}

checkMostRecentTracking().catch(console.error);
