import dagre from 'dagre';
import type { Node, Edge } from '@vue-flow/core';
import type { SnapshotDetails } from '~/schemas/snapshots.schema';

export interface ColumnNodeData {
  name: string;
  type: string;
  status: 'normal' | 'added' | 'removed' | 'changed';
  changeDetails: string[];
}

export interface TriggerNodeData {
  name: string;
  status: 'normal' | 'added' | 'removed' | 'changed';
  definition?: string;
  oldDefinition?: string;
}

export interface TableNodeData {
  label: string;
  status: 'normal' | 'added' | 'removed' | 'changed';
  columns: ColumnNodeData[];
  triggers: TriggerNodeData[];
}

export interface ViewNodeData {
  label: string;
  type: 'view' | 'materialized_view';
  status: 'normal' | 'added' | 'removed' | 'changed';
  definition?: string;
  oldDefinition?: string;
}

export const useSchemaParser = () => {
  const isNameInList = (name: string, list: any[]): boolean => {
    if (!Array.isArray(list)) return false;
    return list.some((item) => (typeof item === 'string' ? item : item?.name) === name);
  };

  const extractDiffSafe = (diffObj: any) => {
    const safe = diffObj || {};
    return {
      added: Array.isArray(safe.added) ? safe.added : [],
      removed: Array.isArray(safe.removed) ? safe.removed : [],
      changed: typeof safe.changed === 'object' && safe.changed !== null ? safe.changed : {},
    };
  };

  const extractNames = (arr: unknown[] | undefined): string[] => {
    if (!Array.isArray(arr)) return [];
    return arr.map((item) => (typeof item === 'string' ? item : (item as any)?.name || ''));
  };

  const calculateNodeHeight = (node: Node<TableNodeData>) => {
    let height = 42;

    if (node.data!.status === 'removed' && !node.data!.columns?.length) {
      height += 40;
    } else {
      height += (node.data!.columns?.length || 0) * 36;
    }

    if (node.data!.triggers?.length) {
      height += 30;
      height += node.data!.triggers.length * 36;
    }

    return height + 4;
  };

  const parseSchemaToFlow = (snapshot: SnapshotDetails | null | undefined) => {
    const nodes: Node<TableNodeData>[] = [];
    const edges: Edge[] = [];

    if (!snapshot || !snapshot.schema_data) return { nodes, edges };

    const tables = snapshot.schema_data.tables || [];
    const diff = snapshot.diff_data || { added_tables: [], removed_tables: [], changed_tables: {} };

    const triggersList = snapshot.triggers_data?.triggers || [];
    const trgDiff = extractDiffSafe(snapshot.triggers_diff_data);
    const triggersByTable: Record<string, TriggerNodeData[]> = {};

    triggersList.forEach((t: any) => {
      if (!t.table) return;
      if (!triggersByTable[t.table]) triggersByTable[t.table] = [];

      const trgName = t.name;
      let status: TriggerNodeData['status'] = 'normal';
      let oldDef: string | undefined = t.definition;

      if (isNameInList(trgName, trgDiff.added)) {
        status = 'added';
        oldDef = undefined;
      } else if (trgDiff.changed[trgName]) {
        status = 'changed';
        oldDef = trgDiff.changed[trgName].old;
      }

      triggersByTable[t.table]!.push({
        name: trgName,
        status,
        definition: t.definition,
        oldDefinition: oldDef,
      });
    });

    tables.forEach((table: any) => {
      let tableStatus: TableNodeData['status'] = 'normal';
      if (isNameInList(table.name, diff.added_tables || [])) tableStatus = 'added';
      else if (diff.changed_tables?.[table.name]) tableStatus = 'changed';

      const changes = diff.changed_tables?.[table.name] || {};
      const addedColNames = extractNames((changes as any).added_columns);
      const removedColNames = extractNames((changes as any).removed_columns);

      const processedColumns: ColumnNodeData[] = (table.columns || []).map((col: any) => {
        let colStatus: ColumnNodeData['status'] = 'normal';
        const changeDetails: string[] = [];

        if (addedColNames.includes(col.name)) {
          colStatus = 'added';
        } else if (changes.changed_columns?.[col.name]) {
          colStatus = 'changed';
          const colDiff: any = changes.changed_columns[col.name];

          if (colDiff?.type) changeDetails.push(`Type: ${colDiff.type.old} → ${colDiff.type.new}`);
          if (colDiff?.nullable !== undefined) {
            changeDetails.push(
              `Nullable: ${colDiff.nullable.old ? 'NULL' : 'NOT NULL'} → ${colDiff.nullable.new ? 'NULL' : 'NOT NULL'}`,
            );
          }
        }
        return { ...col, status: colStatus, changeDetails };
      });

      removedColNames.forEach((colName) => {
        processedColumns.push({
          name: colName,
          type: 'REMOVED',
          status: 'removed',
          changeDetails: [],
        });
      });

      const tableTriggers = triggersByTable[table.name] || [];

      nodes.push({
        id: `table-${table.name}`,
        type: 'customTable',
        position: { x: 0, y: 0 },
        data: {
          label: table.name,
          status: tableStatus,
          columns: processedColumns,
          triggers: tableTriggers,
        },
      });

      if (table.foreign_keys && table.foreign_keys.length > 0) {
        table.foreign_keys.forEach((fk: any) => {
          fk.constrained_columns.forEach((sourceCol: any, index: number) => {
            const targetCol = fk.referred_columns[index];
            edges.push({
              id: `fk-${table.name}-${sourceCol}-${fk.referred_table}-${targetCol}`,
              source: `table-${table.name}`,
              target: `table-${fk.referred_table}`,
              type: 'smoothstep',
              sourceHandle: `${sourceCol}-source-right`,
              targetHandle: `${targetCol}-target-left`,
              animated: true,
              data: { sourceCol, targetCol },
              style: { stroke: '#11af74', strokeWidth: 2 },
            });
          });
        });
      }
    });

    const removedTables = extractNames(diff.removed_tables);
    removedTables.forEach((tableName: string) => {
      nodes.push({
        id: `table-${tableName}`,
        type: 'customTable',
        position: { x: 0, y: 0 },
        data: { label: tableName, status: 'removed', columns: [], triggers: [] },
      });
    });

    const connectedNodeIds = new Set<string>();
    edges.forEach((e) => {
      connectedNodeIds.add(e.source);
      connectedNodeIds.add(e.target);
    });

    const connectedNodes = nodes.filter((n) => connectedNodeIds.has(n.id));
    const disconnectedNodes = nodes.filter((n) => !connectedNodeIds.has(n.id));

    let maxDagreX = 0;

    if (connectedNodes.length > 0) {
      const g = new dagre.graphlib.Graph();
      g.setDefaultEdgeLabel(() => ({}));
      g.setGraph({ rankdir: 'LR', ranksep: 250, nodesep: 60 });

      connectedNodes.forEach((node) => {
        g.setNode(node.id, { width: 250, height: calculateNodeHeight(node) });
      });

      edges.forEach((edge) => g.setEdge(edge.source, edge.target));
      dagre.layout(g);

      connectedNodes.forEach((node) => {
        const dagreNode = g.node(node.id);
        const h = calculateNodeHeight(node);
        node.position = { x: dagreNode.x - 125, y: dagreNode.y - h / 2 };
        if (node.position.x > maxDagreX) maxDagreX = node.position.x;
      });
    }

    const GRID_START_X = connectedNodes.length > 0 ? maxDagreX + 400 : 0;
    const GRID_START_Y = 0;
    const COLUMNS = 4;
    const NODE_WIDTH = 250;
    const X_GAP = 50;
    const Y_GAP = 60;

    let currentX = GRID_START_X;
    let currentY = GRID_START_Y;
    let rowMaxHeight = 0;

    disconnectedNodes.forEach((node, index) => {
      const h = calculateNodeHeight(node);
      node.position = { x: currentX, y: currentY };
      rowMaxHeight = Math.max(rowMaxHeight, h);

      if ((index + 1) % COLUMNS === 0) {
        currentX = GRID_START_X;
        currentY += rowMaxHeight + Y_GAP;
        rowMaxHeight = 0;
      } else {
        currentX += NODE_WIDTH + X_GAP;
      }
    });

    return { nodes, edges };
  };

  const parseViewsToFlow = (snapshot: SnapshotDetails | null | undefined) => {
    const nodes: Node<ViewNodeData>[] = [];
    const edges: Edge[] = [];

    if (!snapshot || !snapshot.views_data) return { nodes, edges };

    const views = Array.isArray(snapshot.views_data.views) ? snapshot.views_data.views : [];
    const matViews = Array.isArray(snapshot.views_data.materialized_views)
      ? snapshot.views_data.materialized_views
      : [];

    const diffData = snapshot.views_diff_data || {};
    const isNested = 'views' in diffData || 'materialized_views' in diffData;

    const getDiffFor = (key: 'views' | 'materialized_views') => {
      if (isNested) return extractDiffSafe((diffData as any)[key]);
      return extractDiffSafe(diffData);
    };

    const processViewList = (
      list: any[],
      diff: ReturnType<typeof extractDiffSafe>,
      type: 'view' | 'materialized_view',
    ) => {
      list.forEach((v) => {
        const viewName = v.name;
        let status: ViewNodeData['status'] = 'normal';
        let oldDefinition: string | undefined = v.definition;

        if (isNameInList(viewName, diff.added)) {
          status = 'added';
          oldDefinition = undefined;
        } else if (diff.changed[viewName]) {
          status = 'changed';
          oldDefinition = diff.changed[viewName].old;
        }

        nodes.push({
          id: `view-${viewName}`,
          type: 'customView',
          position: { x: 0, y: 0 },
          data: { label: viewName, status, type, definition: v.definition, oldDefinition },
        });
      });

      diff.removed.forEach((r: any) => {
        const name = typeof r === 'string' ? r : r?.name;
        if (name && !nodes.some((n) => n.id === `view-${name}`)) {
          nodes.push({
            id: `view-${name}`,
            type: 'customView',
            position: { x: 0, y: 0 },
            data: { label: name, status: 'removed', type },
          });
        }
      });
    };

    processViewList(views, getDiffFor('views'), 'view');
    processViewList(matViews, getDiffFor('materialized_views'), 'materialized_view');

    const g = new dagre.graphlib.Graph();
    g.setDefaultEdgeLabel(() => ({}));
    g.setGraph({ rankdir: 'LR', ranksep: 100, nodesep: 60 });

    nodes.forEach((node) => {
      g.setNode(node.id, { width: 300, height: 100 });
    });

    dagre.layout(g);

    nodes.forEach((node) => {
      const dagreNode = g.node(node.id);
      node.position = { x: dagreNode.x - 150, y: dagreNode.y - 50 };
    });

    return { nodes, edges };
  };

  return { parseSchemaToFlow, parseViewsToFlow };
};
