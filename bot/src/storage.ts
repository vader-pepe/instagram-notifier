import { ChannelData, TrackingData } from "./types/interfaces";
import fs from "node:fs";

export class Storage {
  private data: TrackingData;

  constructor() {
    this.data = { channels: {} };
    this.loadData();
  }

  private loadData() {
    try {
      const rawData = fs.readFileSync("tracking.json", "utf8");
      this.data = JSON.parse(rawData);
    } catch (error) {
      this.data = { channels: {} };
    }
  }

  getAllChannels(): { [channelId: string]: ChannelData } {
    return this.data.channels;
  }

  private saveData() {
    fs.writeFileSync("tracking.json", JSON.stringify(this.data, null, 2));
  }

  getChannelData(channelId: string): ChannelData {
    return this.data.channels[channelId] || { trackedUsers: {} };
  }

  addTrackedUser(channelId: string, username: string, postId: string, storyId: string, lastPostTimestamp: string, lastStoryTimestamp: string) {
    if (!this.data.channels[channelId]) {
      this.data.channels[channelId] = { trackedUsers: {} };
    }
    this.data.channels[channelId].trackedUsers[username] = {
      lastPostId: postId,
      lastStoryId: storyId,
      lastPostTimestamp: lastPostTimestamp,
      lastStoryTimestamp: lastStoryTimestamp,
    };
    this.saveData();
  }

  updateLastStory(channelId: string, username: string, storyId: string, timestamp: string) {
    if (this.data.channels[channelId]?.trackedUsers[username]) {
      this.data.channels[channelId].trackedUsers[username] = {
        ...this.data.channels[channelId].trackedUsers[username],
        lastStoryId: storyId,
        lastStoryTimestamp: timestamp
      };
      this.saveData();
    }
  }

  updateLastPost(channelId: string, username: string, postId: string, timestamp: string) {
    if (this.data.channels[channelId]?.trackedUsers[username]) {
      this.data.channels[channelId].trackedUsers[username] = {
        ...this.data.channels[channelId].trackedUsers[username],
        lastPostId: postId,
        lastPostTimestamp: timestamp
      };
      this.saveData();
    }
  }

  updateLastStoryId(channelId: string, username: string, storyId: string) {
    if (this.data.channels[channelId]?.trackedUsers[username]) {
      this.data.channels[channelId].trackedUsers[username].lastStoryId = storyId;
      this.saveData();
    }
  }

  removeTrackedUser(channelId: string, username: string) {
    if (this.data.channels[channelId]?.trackedUsers[username]) {
      delete this.data.channels[channelId].trackedUsers[username];
      this.saveData();
    }
  }

  updateLastPostId(channelId: string, username: string, postId: string) {
    if (this.data.channels[channelId]?.trackedUsers[username]) {
      this.data.channels[channelId].trackedUsers[username].lastPostId = postId;
      this.saveData();
    }
  }
}
