import type { NextFunction, Request, RequestHandler, Response } from "express";

import { userService } from "@/api/user/userService";
import { handleServiceResponse } from "@/common/utils/httpHandlers";

class UserController {
  // Typed as RequestHandler for GET /users
  public getUsers: RequestHandler = async (_req: Request, res: Response, next) => {
    try {
      const serviceResponse = await userService.findAll();
      handleServiceResponse(serviceResponse, res);
    } catch (err) {
      next(err); // Forward errors to Express error middleware
    }
  };

  // Typed as RequestHandler with route param for GET /users/:id
  public getUser: RequestHandler<{ id: string }> = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const id = Number.parseInt(req.params.id, 10);
      const serviceResponse = await userService.findById(id);
      handleServiceResponse(serviceResponse, res);
    } catch (err) {
      next(err);
    }
  };
}

export const userController = new UserController();
