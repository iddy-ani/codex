import fetch from 'node-fetch';
import os from 'os';

class UserTracker {
  private readonly connectionString = 'mongodb://ExpertGPTDB_rw:12zWgSh5cBl19E9@p1ir1mon019.ger.corp.intel.com:7181,p2ir1mon019.ger.corp.intel.com:7181,p3ir1mon019.ger.corp.intel.com:7181/ExpertGPTDB?ssl=true&replicaSet=mongo7181';
  private readonly databaseName = 'ExpertGPTDB';

  private async getUserEmail(userIdsid: string): Promise<string | null> {
    try {
      const url = `https://ldapagator.apps1-ir-int.icloud.intel.com/user?username=${userIdsid}`;
      
      // Use node-fetch with SSL verification disabled (similar to Python's verify=False)
      const response = await fetch(url, {
        method: 'GET',
        // @ts-ignore - ignore SSL verification for internal Intel services
        rejectUnauthorized: false
      });

      if (response.status !== 200) {
        return null;
      }

      const data = await response.json() as { email?: string };
      return data.email || null;
    } catch (error) {
      // Silently fail - don't let user lookup errors break the CLI
      return null;
    }
  }

  public async trackUser(method: string = 'codex'): Promise<void> {
    try {
      // Use a function to dynamically import mongodb
      const importMongoDB = new Function('return import("mongodb")');
      const { MongoClient } = await importMongoDB();
      
      // Get current user
      const user = os.userInfo().username;
      
      // Get user email from Intel LDAP service
      const userEmail = await this.getUserEmail(user);
      
      if (!userEmail) {
        // Can't track without email, silently return
        return;
      }

      // Connect to MongoDB
      const client = new MongoClient(this.connectionString);
      await client.connect();
      
      const db = client.db(this.databaseName);
      const collection = db.collection('tracking');

      // Check if user has been tracked recently (within 1 hour)
      const oneHourAgo = new Date(Date.now() - (60 * 60 * 1000));
      const recentRecord = await collection.findOne({
        email: userEmail,
        timestamp: { $gte: oneHourAgo }
      });

      if (!recentRecord) {
        // Track the user
        await collection.insertOne({
          email: userEmail,
          timestamp: new Date(),
          method: method
        });
      }

      // Close connection
      await client.close();
    } catch (error) {
      // Silently fail - don't let tracking errors break the CLI
      // This will happen if mongodb is not installed or there are network issues
    }
  }
}

// Export a singleton instance
export const userTracker = new UserTracker();

// Track user when CLI starts (call this early in the CLI lifecycle)
export async function trackCLIUsage(): Promise<void> {
  await userTracker.trackUser('codex');
}
