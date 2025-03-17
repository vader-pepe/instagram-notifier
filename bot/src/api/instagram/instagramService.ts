import { env } from "@/common/utils/envConfig";
import axios from "axios";
import { Post, Story } from "./instagramModel";
import { ServiceResponse } from "@/common/models/serviceResponse";
import { StatusCodes } from "http-status-codes";

export class InstagramService {
  async getLastPost(username: string): Promise<ServiceResponse<Post | null>> {
    const raw = await axios.get<Post[]>(`${env.API_URL}/posts?username=${username}`);
    const data = raw.data;
    if (data.length === 0) {
      return ServiceResponse.failure("No post found!", null, StatusCodes.NOT_FOUND);
    }
    return ServiceResponse.success<Post>("Post found!", data[0]);
  }

  async getLastStory(username: string): Promise<ServiceResponse<Story | null>> {
    const raw = await axios.get<Story[]>(`${env.API_URL}/stories?username=${username}`);
    const data = raw.data;
    if (data.length === 0) {
      return ServiceResponse.failure("No story found!", null, StatusCodes.NOT_FOUND);
    }
    return ServiceResponse.success<Story>("Story found!", data[0])
  }
}

export const instagramService = new InstagramService();
