import { NextFunction, RequestHandler, Response, Request } from "express";
import { instagramService } from "@/api/instagram/instagramService";
import { handleServiceResponse } from "@/common/utils/httpHandlers";

class InstagramController {
  public getLastPost: RequestHandler<{ username: string }> = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const serviceResponse = await instagramService.getLastPost(req.params.username);
      handleServiceResponse(serviceResponse, res);
    } catch (err) {
      next(err);
    }
  }

  public getLastStory: RequestHandler<{ username: string }> = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const serviceResponse = await instagramService.getLastStory(req.params.username);
      handleServiceResponse(serviceResponse, res);
    } catch (err) {
      next(err);
    }
  }
}

export const instagramController = new InstagramController();
