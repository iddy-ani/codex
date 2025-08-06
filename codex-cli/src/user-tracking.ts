import fetch from 'node-fetch';
import os from 'os';

class UserTracker {
  private client: any = null;
  private connected: boolean = false;
  private readonly connectionString = 'mongodb://ExpertGPTDB_rw:12zWgSh5cBl19E9@p1ir1mon019.ger.corp.intel.com:7181,p2ir1mon019.ger.corp.intel.com:7181,p3ir1mon019.ger.corp.intel.com:7181/ExpertGPTDB?ssl=true&replicaSet=mongo7181';
  private readonly databaseName = 'ExpertGPTDB';

  private async loadMongoDB(): Promise<boolean> {
    try {
      // Dynamic import to avoid build issues
      const mongodb = await import('mongodb');
      if (!this.client) {
        this.client = new mongodb.MongoClient(this.connectionString, {
          tls: true,
          tlsAllowInvalidCertificates: true,
          tlsAllowInvalidHostnames: true,
          serverSelectionTimeoutMS: 10000,
          connectTimeoutMS: 10000,
          socketTimeoutMS: 10000
        });
      }
      return true;
    } catch (error) {
      // MongoDB not available - this is fine, tracking will be disabled
      return false;
    }
  }

  private async connect(): Promise<void> {
    if (!this.connected) {
      try {
        const mongoAvailable = await this.loadMongoDB();
        if (!mongoAvailable || !this.client) {
          return;
        }
        
        await this.client.connect();
        this.connected = true;
      } catch (error) {
        // Silently fail - don't let tracking errors break the CLI
        console.debug('Failed to connect to tracking database:', error);
      }
    }
  }

  private async getUserEmail(userIdsid: string): Promise<string | null> {
    try {
      const url = `https://ldapagator.apps1-ir-int.icloud.intel.com/user?username=${userIdsid}`;
      
      // Create an HTTPS agent that ignores SSL certificate errors
      const https = await import('https');
      const agent = new https.Agent({
        rejectUnauthorized: false
      });
      
      // Use node-fetch with SSL verification disabled (similar to Python's verify=False)
      const response = await fetch(url, {
        method: 'GET',
        agent: agent
      });

      if (response.status !== 200) {
        return null;
      }

      const data = await response.json() as { email?: string };
      return data.email || null;
    } catch (error) {
      // Silently fail - don't let user lookup errors break the CLI
      console.debug('Failed to get user email:', error);
      return null;
    }
  }

  private async insertTrackingRecord(userEmail: string, method: string = 'codex'): Promise<void> {
    try {
      await this.connect();
      
      if (!this.connected || !this.client) {
        return;
      }

      const db = this.client.db(this.databaseName);
      const collection = db.collection('tracking');

      await collection.insertOne({
        email: userEmail,
        timestamp: new Date(),
        method: method
      });
    } catch (error) {
      // Silently fail - don't let tracking errors break the CLI
      console.debug('Failed to insert tracking record:', error);
    }
  }

  private async hasRecentUsage(userEmail: string): Promise<boolean> {
    try {
      await this.connect();
      
      if (!this.connected || !this.client) {
        return false;
      }

      const db = this.client.db(this.databaseName);
      const collection = db.collection('tracking');

      // Check if user has used the CLI in the last hour
      const oneHourAgo = new Date(Date.now() - (60 * 60 * 1000));
      
      const recentRecord = await collection.findOne({
        email: userEmail,
        timestamp: { $gte: oneHourAgo }
      });

      return recentRecord !== null;
    } catch (error) {
      // Silently fail - assume no recent usage to err on the side of tracking
      console.debug('Failed to check recent usage:', error);
      return false;
    }
  }

  public async trackUser(method: string = 'codex'): Promise<void> {
    try {
      // Get current user
      const user = os.userInfo().username;
      
      // Get user email from Intel LDAP service
      const userEmail = await this.getUserEmail(user);
      
      if (!userEmail) {
        // Can't track without email, silently return
        return;
      }

      // Check if user has been tracked recently (within 1 hour)
      const hasRecent = await this.hasRecentUsage(userEmail);
      
      if (!hasRecent) {
        // Track the user
        await this.insertTrackingRecord(userEmail, method);
      }
    } catch (error) {
      // Silently fail - don't let tracking errors break the CLI
      console.debug('User tracking failed:', error);
    }
  }

  public async close(): Promise<void> {
    if (this.connected && this.client) {
      try {
        await this.client.close();
        this.connected = false;
      } catch (error) {
        console.debug('Failed to close MongoDB connection:', error);
      }
    }
  }
}

// Export a singleton instance
export const userTracker = new UserTracker();

// Track user when CLI starts (call this early in the CLI lifecycle)
export async function trackCLIUsage(): Promise<void> {
  await userTracker.trackUser('codex');
}

// Ensure connection is closed when process exits
process.on('exit', () => {
  userTracker.close().catch(() => {
    // Ignore errors during cleanup
  });
});

process.on('SIGINT', async () => {
  await userTracker.close();
});

process.on('SIGTERM', async () => {
  await userTracker.close();
});
