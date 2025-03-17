import { OpenAPIRegistry } from "@asteasolutions/zod-to-openapi";
import express, { type Router } from "express";
import { InstagramUserSchema, PostSchema, StorySchema } from "./instagramModel";
import { createApiResponse } from "@/api-docs/openAPIResponseBuilders";
import { instagramController } from "./instagramController";
import { validateRequest } from "@/common/utils/httpHandlers";

export const instagramRegistry = new OpenAPIRegistry();
export const instagramRouter: Router = express.Router();

instagramRegistry.register("Post", PostSchema);
instagramRegistry.register("Story", StorySchema);

instagramRegistry.registerPath({
  method: "get",
  path: "/instagram/post/{user}",
  tags: ["Post"],
  request: { params: InstagramUserSchema.shape.params },
  responses: createApiResponse(PostSchema, "Success")
});

instagramRouter.get("/post/:username", validateRequest(InstagramUserSchema), instagramController.getLastPost);

instagramRegistry.registerPath({
  method: "get",
  path: "/instagram/story/{username}",
  tags: ["Story"],
  request: { params: InstagramUserSchema.shape.params },
  responses: createApiResponse(StorySchema, "Success")
});

instagramRouter.get("/story/:username", validateRequest(InstagramUserSchema), instagramController.getLastStory);
