import type { NextFunction, Request, RequestHandler, Response } from "express";
import { StatusCodes } from "http-status-codes";
import type { ZodSchema, ZodError } from "zod";

import { ServiceResponse } from "@/common/models/serviceResponse";

export const handleServiceResponse = (serviceResponse: ServiceResponse<unknown>, response: Response) => {
	return response.status(serviceResponse.statusCode).send(serviceResponse);
};

export function validateRequest(schema: ZodSchema): RequestHandler {
	return (req: Request, res: Response, next: NextFunction) => {
		// Let TypeScript infer parameter types
		try {
			schema.parse({
				body: req.body,
				query: req.query,
				params: req.params,
			});
			next();
		} catch (err) {
			const zodError = err as ZodError;
			const errorMessage = `Invalid input: ${zodError.errors.map((e) => e.message).join(", ")}`;
			const serviceResponse = ServiceResponse.failure(errorMessage, null, StatusCodes.BAD_REQUEST);

			// Handle response without returning it
			handleServiceResponse(serviceResponse, res);
		}
	};
}
