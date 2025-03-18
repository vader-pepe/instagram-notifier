import { ColorResolvable, EmbedBuilder } from "discord.js";
import { Post, Story } from "@/api/instagram/instagramModel";

export class InstagramEmbeds {
  static BASE_COLOR: ColorResolvable = '#E1306C'; // Instagram brand color

  static createPostEmbed(username: string, post: Post) {
    const embed = new EmbedBuilder()
      .setColor(this.BASE_COLOR)
      .setTitle(`📸 New Instagram Post from @${username}`)
      .setURL(post.permalink)
      .setDescription(post.caption || '')
      .setFooter({ text: 'Instagram Post Notification' })
      .setTimestamp(new Date(post.taken_at) || new Date());
    if (post.media_type === 2) {
      embed.setImage(post.url);
      // TODO: add video
    } else {
      embed.setImage(post.url);
    }
    return embed;
  }

  static createStoryEmbed(username: string, story: Story) {
    const embed = new EmbedBuilder()
      .setColor(this.BASE_COLOR)
      .setTitle(`🎥 New Instagram Story from @${username}`)
      .setURL(story.permalink)
      .setFooter({ text: 'Instagram Story Notification' })
      .setTimestamp(new Date(story.taken_at) || new Date())
      .setImage(story.url);

    if (story.media_type === 2) {
      embed.setDescription('**Video Story**\n')
    }

    return embed;
  }
};
