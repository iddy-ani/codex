import os from 'os';

// Force create a tracking record to verify the codex method works
async function forceCreateCodexRecord() {
  console.log('=================================');
  console.log('Force Create Codex Tracking Record');
  console.log('=================================\n');

  const connectionString = 'mongodb://ExpertGPTDB_rw:12zWgSh5cBl19E9@p1ir1mon019.ger.corp.intel.com:7181,p2ir1mon019.ger.corp.intel.com:7181,p3ir1mon019.ger.corp.intel.com:7181/ExpertGPTDB?ssl=true&replicaSet=mongo7181';
  
  try {
    const importMongoDB = new Function('return import("mongodb")');
    const { MongoClient } = await importMongoDB();
    
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

    console.log('🔍 Creating a codex tracking record...');
    const result = await collection.insertOne({
      email: 'idriss.animashaun@intel.com',
      timestamp: new Date(),
      method: 'codex'
    });
    console.log(`✅ Codex tracking record created with ID: ${result.insertedId}`);
    
    // Now check recent records to verify it was created
    console.log('\n🔍 Checking recent records...');
    const recentRecords = await collection.find({
      email: 'idriss.animashaun@intel.com'
    }).sort({ timestamp: -1 }).limit(3).toArray();
    
    console.log('📊 Most recent records:');
    recentRecords.forEach((record, index) => {
      const minutesAgo = Math.round((Date.now() - record.timestamp.getTime()) / 1000 / 60);
      console.log(`${index + 1}. Method: ${record.method}, ${minutesAgo} minutes ago`);
    });

    await client.close();
    
  } catch (error) {
    console.log(`❌ Error:`, error.message);
  }
  
  console.log('\n=================================');
  console.log('Force Create Complete');
  console.log('=================================');
}

forceCreateCodexRecord().catch(console.error);
