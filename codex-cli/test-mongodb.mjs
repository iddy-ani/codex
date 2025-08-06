import os from 'os';

async function testMongoDBConnection() {
  console.log('=================================');
  console.log('Testing MongoDB Connection Details');
  console.log('=================================\n');

  try {
    // Dynamic import of MongoDB
    const importMongoDB = new Function('return import("mongodb")');
    const { MongoClient } = await importMongoDB();
    
    const connectionString = 'mongodb://ExpertGPTDB_rw:12zWgSh5cBl19E9@p1ir1mon019.ger.corp.intel.com:7181,p2ir1mon019.ger.corp.intel.com:7181,p3ir1mon019.ger.corp.intel.com:7181/ExpertGPTDB?ssl=true&replicaSet=mongo7181';
    
    console.log('🔍 Connection string (sanitized):');
    console.log('mongodb://[username]:[password]@p1ir1mon019.ger.corp.intel.com:7181,p2ir1mon019.ger.corp.intel.com:7181,p3ir1mon019.ger.corp.intel.com:7181/ExpertGPTDB?ssl=true&replicaSet=mongo7181');
    console.log('\n🔍 Testing connection with detailed error handling...');
    
    const client = new MongoClient(connectionString, {
      tls: true,
      tlsAllowInvalidCertificates: true,
      tlsAllowInvalidHostnames: true,
      serverSelectionTimeoutMS: 10000, // 10 second timeout
      connectTimeoutMS: 10000,
      socketTimeoutMS: 10000,
    });
    
    console.log('⏳ Attempting to connect...');
    await client.connect();
    
    console.log('✅ MongoDB connection successful!');
    
    const db = client.db('ExpertGPTDB');
    console.log('✅ Database selected: ExpertGPTDB');
    
    const collection = db.collection('tracking');
    console.log('✅ Collection selected: tracking');
    
    // Try to perform a simple operation
    const count = await collection.countDocuments({});
    console.log(`📊 Found ${count} tracking records in database`);
    
    // Test inserting a sample record
    const testRecord = {
      email: 'test@intel.com',
      timestamp: new Date(),
      method: 'connection-test'
    };
    
    const result = await collection.insertOne(testRecord);
    console.log(`✅ Test record inserted with ID: ${result.insertedId}`);
    
    // Clean up the test record
    await collection.deleteOne({ _id: result.insertedId });
    console.log('✅ Test record cleaned up');
    
    await client.close();
    console.log('✅ Connection closed successfully');
    
  } catch (error) {
    console.log('❌ MongoDB connection failed with detailed error:');
    console.error('Error name:', error.name);
    console.error('Error message:', error.message);
    
    if (error.code) {
      console.error('Error code:', error.code);
    }
    
    if (error.codeName) {
      console.error('Error code name:', error.codeName);
    }
    
    console.log('\n🔧 Possible reasons for failure:');
    console.log('1. Not connected to Intel corporate network');
    console.log('2. VPN not connected to Intel network');
    console.log('3. Firewall blocking MongoDB ports (7181)');
    console.log('4. MongoDB servers are down or unreachable');
    console.log('5. Authentication credentials are incorrect');
    console.log('6. SSL/TLS certificate issues');
    console.log('7. Network proxy blocking the connection');
    
    console.log('\n💡 To resolve:');
    console.log('- Ensure you are on Intel corporate network or VPN');
    console.log('- Check if ports 7181 are accessible');
    console.log('- Verify MongoDB service is running on Intel infrastructure');
  }
  
  console.log('\n=================================');
  console.log('MongoDB Connection Test Complete');
  console.log('=================================');
}

testMongoDBConnection().catch(console.error);
