export interface TrackedUser {
  lastPostId: string;
  lastStoryId: string;
  lastPostTimestamp: string;
  lastStoryTimestamp: string;
}

export interface ChannelData {
  trackedUsers: {
    [username: string]: TrackedUser;
  };
}

export interface TrackingData {
  channels: {
    [channelId: string]: ChannelData;
  };
}
