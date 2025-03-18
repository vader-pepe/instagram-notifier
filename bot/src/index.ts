import { env } from "@/common/utils/envConfig";
import { app, logger } from "@/server";
import axios from "axios";
import { ApplicationCommandOptionType, Channel, Client, GatewayIntentBits, REST, Routes, TextChannel } from "discord.js";
import { Post, Story } from "@/api/instagram/instagramModel";
import { Storage } from "./storage";
import { InstagramEmbeds } from "./instagramEmbeds";
import { TrackedUser } from "./types/interfaces";

const server = app.listen(env.PORT, () => {
  const { NODE_ENV, HOST, PORT } = env;
  logger.info(`Server (${NODE_ENV}) running on port http://${HOST}:${PORT}`);
});

const client = new Client({ intents: [GatewayIntentBits.Guilds] });
const storage = new Storage();

// Slash Command Registration
const commands = [
  {
    name: 'track',
    description: 'Start tracking an Instagram user',
    options: [{
      name: 'username',
      description: 'Instagram username to track',
      type: ApplicationCommandOptionType.String,
      required: true
    }]
  },
  {
    name: 'untrack',
    description: 'Stop tracking an Instagram user',
    options: [{
      name: 'username',
      description: 'Instagram username to stop tracking',
      type: ApplicationCommandOptionType.String,
      required: true
    }]
  },
  {
    name: 'list',
    description: 'List tracked Instagram users for this channel'
  }
];

// Bot Ready Event
client.once('ready', async () => {
  logger.info(`Logged in as ${client.user?.tag}!`);

  // Register commands
  const rest = new REST({ version: '10' }).setToken(env.DISCORD_TOKEN);
  try {
    await rest.put(
      Routes.applicationCommands(process.env.CLIENT_ID!),
      { body: commands }
    );
    logger.info(`Successfully registered application commands.`);
  } catch (error) {
    logger.error(`Error registering commands: ${error}`);
  }

  setInterval(() => {
    checkInstagramUpdates()
  }, 60 * 1000 * 5);
});

// Interaction Handling
client.on('interactionCreate', async interaction => {
  if (!interaction.isCommand()) return;

  const { commandName, options, channelId } = interaction;

  try {
    await interaction.deferReply({ ephemeral: true });

    switch (commandName) {
      case 'track':
        const usernameOption = options.get('username', true).value;
        const username = String(usernameOption).toLowerCase();
        const [post, story] = await Promise.all([
          axios.get<Post[]>(`${env.API_URL}/posts?username=${username}`),
          axios.get<Story[]>(`${env.API_URL}/stories?username=${username}`)
        ]);

        if (!post || !story) {
          await interaction.editReply('❌ Failed to track user. Account may not exist or be private.');
          return;
        }

        storage.addTrackedUser(channelId!, username, post.data[0]?.id.toString() || "", story.data[0]?.id.toString() || "", post.data[0]?.taken_at || "", story.data[0]?.taken_at || "");
        await interaction.editReply(`✅ Now tracking @${username} (posts and stories)!`);
        break;
      case 'untrack':
        const untrackUsernameOption = options.get('username', true).value;
        const untrackUsername = String(untrackUsernameOption).toLowerCase();

        storage.removeTrackedUser(channelId!, untrackUsername);
        await interaction.editReply(`✅ Stopped tracking @${untrackUsername}!`);
        break;

      case 'list':
        const trackedUsers = Object.keys(storage.getChannelData(channelId!).trackedUsers);
        await interaction.editReply(
          trackedUsers.length > 0
            ? `📋 Tracked users: ${trackedUsers.join(', ')}`
            : 'No users being tracked in this channel.'
        );
        break;
    }
  } catch (error) {
    logger.error(`Error handling command: ${error}`);
    await interaction.editReply('❌ An error occurred while processing your request.');
  }
});

async function checkPosts(channelId: string, username: string, userData: TrackedUser, channel: Channel) {
  const rawPost = await axios.get<Post[]>(`${env.API_URL}/posts?username=${username}`);
  const posts = rawPost.data;
  if (posts.length === 0) return;

  const storedPostId = userData.lastPostId;
  const latestPost = posts[0];

  // Case 1: New post detected (normal flow)
  if (latestPost.id.toString() !== storedPostId && latestPost.taken_at > userData.lastPostTimestamp) {
    const embed = InstagramEmbeds.createPostEmbed(username, {
      ...latestPost,
      url: latestPost.url || 'https://example.com/fallback-image.png' // Add actual media URL
    });

    await (channel as TextChannel).send({
      content: `📸 New post from @${username}`,
      embeds: [embed]
    });
    storage.updateLastPost(channelId, username, latestPost.id.toString(), latestPost.taken_at);
    return;
  }

  // Case 2: Post deletion handling
  const storedPostExists = posts.some(post => post.id.toString() === storedPostId);
  if (!storedPostExists) {
    // Find the newest existing post that's older than our stored timestamp
    const validPost = posts.find(post => post.taken_at <= userData.lastPostTimestamp);

    if (validPost) {
      storage.updateLastPost(channelId, username, validPost.id.toString(), validPost.taken_at);
      logger.info(`Updated deleted post reference for ${username}`);
    } else {
      // No recent posts - reset tracking
      storage.removeTrackedUser(channelId, username);
      logger.info(`Reset tracking for ${username} due to deleted posts`);
    }
  }
};

async function checkStories(channelId: string, username: string, userData: TrackedUser, channel: Channel) {
  const rawStories = await axios.get<Story[]>(`${env.API_URL}/stories?username=${username}`);
  const stories = rawStories.data;
  if (stories.length === 0) return;

  const { lastStoryId, lastStoryTimestamp } = userData;
  const latestStory = stories[0];

  // New story detection
  if (latestStory.id.toString() !== lastStoryId && latestStory.taken_at > lastStoryTimestamp) {
    const embed = InstagramEmbeds.createStoryEmbed(username, {
      ...latestStory,
      url: latestStory.url || 'https://example.com/story-fallback.png'
    });

    await (channel as TextChannel).send({
      content: `🎥 New story from @${username}`,
      embeds: [embed]
    });
    storage.updateLastStory(channelId, username, latestStory.id.toString(), latestStory.taken_at);
    return;
  }

  // Handle deleted/expired stories
  const storyExists = stories.some(story => story.id.toString() === lastStoryId);
  if (!storyExists) {
    const validStory = stories.find(story => story.taken_at <= lastStoryTimestamp);

    if (validStory) {
      storage.updateLastStory(channelId, username, validStory.id.toString(), validStory.taken_at);
      logger.info(`Updated story reference for ${username}`);
    } else {
      // Story expired and no recent stories available
      storage.updateLastStory(channelId, username, '', "0");
      logger.info(`Reset story tracking for ${username}`);
    }
  }
};

// Instagram Post Checking
async function checkInstagramUpdates() {
  logger.info('Checking for new Instagram updates...');

  // Get all channels with proper typing
  const allChannels = storage.getAllChannels();
  for (const [channelId, channelData] of Object.entries(allChannels)) {
    for (const [username, userData] of Object.entries(channelData.trackedUsers)) {
      try {
        const channel = await client.channels.fetch(channelId);
        if (channel?.isTextBased() && !channel.isDMBased()) {
          // Check posts with validation
          await checkPosts(channelId, username, userData, channel);

          // Check stories with validation
          await checkStories(channelId, username, userData, channel);
        }
      } catch (error) {
        logger.error(`Error checking ${username}: ${error}`);
      }
    }
  }

};

client.login(env.DISCORD_TOKEN);

const onCloseSignal = () => {
  logger.info("sigint received, shutting down");
  server.close(() => {
    logger.info("server closed");
    process.exit();
  });
  setTimeout(() => process.exit(1), 10000).unref(); // Force shutdown after 10s
};

process.on("SIGINT", onCloseSignal);
process.on("SIGTERM", onCloseSignal);
