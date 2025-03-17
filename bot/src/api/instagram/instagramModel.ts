import { extendZodWithOpenApi } from "@asteasolutions/zod-to-openapi";
import { z, ZodType } from "zod";

extendZodWithOpenApi(z);

function numericEnum<TValues extends readonly number[]>(
  values: TValues,
) {
  return z.number().superRefine((val, ctx) => {
    if (!values.includes(val)) {
      ctx.addIssue({
        code: z.ZodIssueCode.invalid_enum_value,
        options: [...values],
        received: val,
      });
    }
  }) as ZodType<TValues[number]>;
};

const MEDIA = [1, 2] as const;
export type Post = z.infer<typeof PostSchema>;
export const PostSchema = z.object({
  id: z.number(),
  url: z.string().url(),
  caption: z.string(),
  media_type: numericEnum(MEDIA),
  taken_at: z.string().date(),
  like_count: z.number(),
  comment_count: z.number(),
  video_url: z.optional(z.string())
});

export type Story = z.infer<typeof StorySchema>;
export const StorySchema = z.object({
  id: z.number(),
  url: z.string(),
  media_type: numericEnum(MEDIA),
  taken_at: z.string().date(),
  expiring_at: z.optional(z.string().date())
})

export const InstagramUserSchema = z.object({
  params: z.object({ username: z.string() }),
});
