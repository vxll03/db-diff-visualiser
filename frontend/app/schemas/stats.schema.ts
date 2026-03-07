import { z } from 'zod';

export const SnapshotCountSchema = z.object({
  date: z.string(),
  count: z.number(),
});

export const SnapshotCountResponseSchema = z.array(SnapshotCountSchema);
export type SnapshotCount = z.infer<typeof SnapshotCountSchema>;
