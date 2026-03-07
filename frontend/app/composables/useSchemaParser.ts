import type { SnapshotDetails } from '~/schemas/snapshots.schema';
import { mapTablesToNodesAndEdges, mapViewsToNodesAndEdges } from '@/utils/parser/mappers';
import { applyTableLayout, applyViewLayout } from '@/utils/parser/layout';

export const useSchemaParser = () => {
  const parseSchemaToFlow = (snapshot: SnapshotDetails | null | undefined) => {
    if (!snapshot || !snapshot.schema_data) return { nodes: [], edges: [] };
    const { nodes, edges } = mapTablesToNodesAndEdges(snapshot);
    return applyTableLayout(nodes, edges);
  };

  const parseViewsToFlow = (snapshot: SnapshotDetails | null | undefined) => {
    if (!snapshot || !snapshot.views_data) return { nodes: [], edges: [] };
    const { nodes, edges } = mapViewsToNodesAndEdges(snapshot);
    return applyViewLayout(nodes, edges);
  };

  return { parseSchemaToFlow, parseViewsToFlow };
};