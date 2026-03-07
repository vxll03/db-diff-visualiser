import { z } from 'zod';

export const ColumnSchema = z.object({
  name: z.string(),
  type: z.string(),
  nullable: z.boolean().optional(),
  default: z.string().nullable().optional(),
});

export const ForeignKeySchema = z.object({
  constrained_columns: z.array(z.string()),
  referred_table: z.string(),
  referred_columns: z.array(z.string()),
});

export const TableSchema = z.object({
  name: z.string(),
  columns: z.array(ColumnSchema),
  primary_key: z.array(z.string()).optional(),
  foreign_keys: z.array(ForeignKeySchema).optional(),
});

export const SchemaDataSchema = z.object({
  tables: z.array(TableSchema).default([]),
});

export const SchemaDiffSchema = z.object({
  added_tables: z.array(z.string()).default([]),
  removed_tables: z.array(z.string()).default([]),
  changed_tables: z.record(z.string(), z.any()).default({}),
});

export const MetaItemSchema = z.object({
  name: z.string(),
  definition: z.string().optional(),
  table: z.string().optional(),
});

export const MetaDiffSchema = z.object({
  added: z.array(MetaItemSchema).default([]),
  removed: z.array(z.string()).default([]),
  changed: z
    .record(z.string(), z.object({ old: z.string().nullable(), new: z.string().nullable() }))
    .default({}),
});

export const ViewsDataSchema = z.object({
  views: z.array(MetaItemSchema).default([]),
  materialized_views: z.array(MetaItemSchema).default([]),
});

export const ViewsDiffSchema = z.object({
  views: MetaDiffSchema.default({ added: [], removed: [], changed: {} }),
  materialized_views: MetaDiffSchema.default({ added: [], removed: [], changed: {} }),
});

export const FunctionsDataSchema = z.object({
  functions: z.array(MetaItemSchema).default([]),
});

export const TriggersDataSchema = z.object({
  triggers: z.array(MetaItemSchema).default([]),
});

export const SnapshotDetailsSchema = z.object({
  id: z.number(),
  project_id: z.number(),
  revision_id: z.string(),
  prev_revision_id: z.string().nullable(),
  created_at: z.iso.datetime(),

  schema_data: SchemaDataSchema.nullable().catch(null),
  diff_data: SchemaDiffSchema.nullable().catch(null),

  views_data: ViewsDataSchema.nullable().catch(null),
  views_diff_data: ViewsDiffSchema.nullable().catch(null),

  functions_data: FunctionsDataSchema.nullable().catch(null),
  functions_diff_data: MetaDiffSchema.nullable().catch(null),

  triggers_data: TriggersDataSchema.nullable().catch(null),
  triggers_diff_data: MetaDiffSchema.nullable().catch(null),
});

export const LatestSnapshotSchema = z.object({
  id: z.number(),
  revision_id: z.string(),
  project_id: z.number().nullable().optional(),
  project_name: z.string(),
  created_at: z.iso.datetime(),
});

export const LatestSnapshotResponseSchema = z.array(LatestSnapshotSchema);
export const TimelineSnapshotSchema = LatestSnapshotSchema.omit({ project_name: true });
export const TimelineSnapshotResponseSchema = z.array(TimelineSnapshotSchema);

export type TimeLineSnapshot = z.infer<typeof TimelineSnapshotSchema>;
export type LatestSnapshot = z.infer<typeof LatestSnapshotSchema>;
export type SnapshotDetails = z.infer<typeof SnapshotDetailsSchema>;
