import os from 'os';

async function checkRecentTracking() {
  console.log('=================================');
  console.log('Checking Recent Tracking Records');
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
    
    // Check for recent records from the current user
    const user = os.userInfo().username;
    console.log(`🔍 Looking for recent records for user: ${user}`);
    
    // Get records from the last hour
    const oneHourAgo = new Date(Date.now() - (60 * 60 * 1000));
    const recentRecords = await collection.find({
      email: { $regex: user, $options: 'i' }, // Case-insensitive search for username in email
      timestamp: { $gte: oneHourAgo }
    }).sort({ timestamp: -1 }).limit(5).toArray();
    
    console.log(`📊 Found ${recentRecords.length} recent records:`);
    
    recentRecords.forEach((record, index) => {
      console.log(`${index + 1}. Email: ${record.email}`);
      console.log(`   Method: ${record.method}`);
      console.log(`   Timestamp: ${record.timestamp}`);
      console.log(`   Time ago: ${Math.round((Date.now() - record.timestamp.getTime()) / 1000 / 60)} minutes ago\n`);
    });
    
    if (recentRecords.length === 0) {
      console.log('⚠️ No recent records found. This could mean:');
      console.log('- User tracking ran but no recent CLI usage');
      console.log('- Email lookup failed');
      console.log('- Different email format than expected');
      
      // Let's check for any records with this user's email
      const allUserRecords = await collection.find({
        email: 'idriss.animashaun@intel.com'
      }).sort({ timestamp: -1 }).limit(3).toArray();
      
      console.log(`\n🔍 Checking for any records with email: idriss.animashaun@intel.com`);
      console.log(`📊 Found ${allUserRecords.length} total records for this email:`);
      
      allUserRecords.forEach((record, index) => {
        console.log(`${index + 1}. Method: ${record.method}`);
        console.log(`   Timestamp: ${record.timestamp}`);
        console.log(`   Time ago: ${Math.round((Date.now() - record.timestamp.getTime()) / 1000 / 60)} minutes ago\n`);
      });
    }
    
    await client.close();
    
  } catch (error) {
    console.log('❌ Failed to check tracking records:');
    console.error('Error:', error.message);
  }
  
  console.log('\n=================================');
  console.log('Recent Tracking Check Complete');
  console.log('=================================');
}

checkRecentTracking().catch(console.error);
