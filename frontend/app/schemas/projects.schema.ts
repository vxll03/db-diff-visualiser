import { z } from 'zod';

export const ProjectSchema = z.object({
  id: z.number(),
  name: z.string(),
  icon: z.string().nullable(),
  created_at: z.iso.datetime(),

  tables_count: z.number(),
  snapshots_count: z.number(),
  triggers_count: z.number(),
  views_count: z.number(),
  mat_views_count: z.number(),
  functions_count: z.number(),
});

export const ApiProjectsSchema = z.array(ProjectSchema);
export type Project = z.infer<typeof ProjectSchema>;
