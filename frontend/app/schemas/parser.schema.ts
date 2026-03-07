import { z } from 'zod';
import type { Node } from '@vue-flow/core';

export const NodeStatusSchema = z.enum(['normal', 'added', 'removed', 'changed']);

export const ColumnNodeDataSchema = z.object({
  name: z.string(),
  type: z.string(),
  status: NodeStatusSchema,
  changeDetails: z.array(z.string()),
});

export const TriggerNodeDataSchema = z.object({
  name: z.string(),
  status: NodeStatusSchema,
  definition: z.string().optional(),
  oldDefinition: z.string().optional(),
});

export const TableNodeDataSchema = z.object({
  label: z.string(),
  status: NodeStatusSchema,
  columns: z.array(ColumnNodeDataSchema),
  triggers: z.array(TriggerNodeDataSchema),
});

export const ViewNodeDataSchema = z.object({
  label: z.string(),
  type: z.enum(['view', 'materialized_view']),
  status: NodeStatusSchema,
  definition: z.string().optional(),
  oldDefinition: z.string().optional(),
});

export type NodeStatus = z.infer<typeof NodeStatusSchema>;
export type ColumnNodeData = z.infer<typeof ColumnNodeDataSchema>;
export type TriggerNodeData = z.infer<typeof TriggerNodeDataSchema>;
export type TableNodeData = z.infer<typeof TableNodeDataSchema>;
export type ViewNodeData = z.infer<typeof ViewNodeDataSchema>;

export type TableNode = Node<TableNodeData>;
export type ViewNode = Node<ViewNodeData>;