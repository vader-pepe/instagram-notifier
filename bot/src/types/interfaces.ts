export interface TrackedUser {
  lastPostId: string;
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
