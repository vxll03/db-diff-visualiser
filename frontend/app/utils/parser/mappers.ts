import type { Edge } from '@vue-flow/core';
import type { SnapshotDetails } from '~/schemas/snapshots.schema';
import {
  TableNodeDataSchema,
  ViewNodeDataSchema,
  type TableNode,
  type ViewNode,
  type TriggerNodeData,
  type ColumnNodeData,
} from '@/schemas/parser.schema';
import { isNameInList, extractDiffSafe, extractNames, type SafeDiff } from './utils';

// region Types
interface ColumnDiffDetails {
  type?: { old: string; new: string };
  nullable?: { old: boolean; new: boolean };
}

interface TableDiffDetails {
  added_columns?: unknown[];
  removed_columns?: unknown[];
  changed_columns?: Record<string, ColumnDiffDetails>;
}

interface TriggerItem {
  name: string;
  table?: string;
  definition?: string;
}

interface ColumnItem {
  name: string;
  type?: string;
}

interface ForeignKeyItem {
  constrained_columns: string[];
  referred_table: string;
  referred_columns: string[];
}

interface TableItem {
  name: string;
  columns?: ColumnItem[];
  foreign_keys?: ForeignKeyItem[];
}

interface ViewItem {
  name: string;
  definition?: string;
}

interface DiffDataNested {
  views?: unknown;
  materialized_views?: unknown;
}

// endregion

// region Mappers
export const mapTablesToNodesAndEdges = (snapshot: SnapshotDetails) => {
  const nodes: TableNode[] = [];
  const edges: Edge[] = [];

  const tables: TableItem[] = (snapshot.schema_data?.tables as TableItem[]) || [];
  const diff = snapshot.diff_data || { added_tables: [], removed_tables: [], changed_tables: {} };
  const triggersList: TriggerItem[] = (snapshot.triggers_data?.triggers as TriggerItem[]) || [];
  const trgDiff = extractDiffSafe(snapshot.triggers_diff_data);

  const triggersByTable: Record<string, TriggerNodeData[]> = {};

  triggersList.forEach((t: TriggerItem) => {
    if (!t.table) return;
    if (!triggersByTable[t.table]) triggersByTable[t.table] = [];

    const status = isNameInList(t.name, trgDiff.added)
      ? 'added'
      : trgDiff.changed[t.name]
        ? 'changed'
        : 'normal';
    const changedTrigger = trgDiff.changed[t.name] as { old?: string } | undefined;
    const oldDef = changedTrigger?.old || (status === 'added' ? undefined : t.definition);

    triggersByTable[t.table]!.push({
      name: t.name,
      status,
      definition: t.definition,
      oldDefinition: oldDef,
    });
  });

  tables.forEach((table: TableItem) => {
    const isAdded = isNameInList(table.name, diff.added_tables || []);
    const isChanged = !!diff.changed_tables?.[table.name];
    const tableStatus = isAdded ? 'added' : isChanged ? 'changed' : 'normal';

    const changes = (diff.changed_tables?.[table.name] || {}) as TableDiffDetails;
    const addedColNames = extractNames(changes.added_columns);
    const removedColNames = extractNames(changes.removed_columns);

    const processedColumns: ColumnNodeData[] = (table.columns || []).map((col: ColumnItem) => {
      let colStatus: ColumnNodeData['status'] = 'normal';
      const changeDetails: string[] = [];

      if (addedColNames.includes(col.name)) {
        colStatus = 'added';
      } else if (changes.changed_columns?.[col.name]) {
        colStatus = 'changed';
        const colDiff = changes.changed_columns[col.name];

        if (colDiff!.type) changeDetails.push(`Type: ${colDiff!.type.old} → ${colDiff!.type.new}`);
        if (colDiff!.nullable !== undefined) {
          changeDetails.push(
            `Nullable: ${colDiff!.nullable.old ? 'NULL' : 'NOT NULL'} → ${colDiff!.nullable.new ? 'NULL' : 'NOT NULL'}`,
          );
        }
      }
      return { name: col.name, type: col.type || 'UNKNOWN', status: colStatus, changeDetails };
    });

    removedColNames.forEach((colName: string) => {
      processedColumns.push({
        name: colName,
        type: 'REMOVED',
        status: 'removed',
        changeDetails: [],
      });
    });

    const validTableData = TableNodeDataSchema.parse({
      label: table.name,
      status: tableStatus,
      columns: processedColumns,
      triggers: triggersByTable[table.name] || [],
    });

    nodes.push({
      id: `table-${table.name}`,
      type: 'customTable',
      position: { x: 0, y: 0 },
      data: validTableData,
    });

    table.foreign_keys?.forEach((fk: ForeignKeyItem) => {
      const isSelfRef = table.name === fk.referred_table;

      fk.constrained_columns.forEach((sourceCol: string, index: number) => {
        edges.push({
          id: `fk-${table.name}-${sourceCol}-${fk.referred_table}-${fk.referred_columns[index]}`,
          source: `table-${table.name}`,
          target: `table-${fk.referred_table}`,
          type: 'smoothstep',
          sourceHandle: `${sourceCol}-source-right`,
          targetHandle: isSelfRef 
            ? `${fk.referred_columns[index]}-target-right` 
            : `${fk.referred_columns[index]}-target-left`,
          animated: true,
          data: { sourceCol, targetCol: fk.referred_columns[index] },
          style: { stroke: ACCENT, strokeWidth: 2 },
        });
      });
    });
  });

  extractNames(diff.removed_tables).forEach((tableName: string) => {
    const validData = TableNodeDataSchema.parse({
      label: tableName,
      status: 'removed',
      columns: [],
      triggers: [],
    });
    nodes.push({
      id: `table-${tableName}`,
      type: 'customTable',
      position: { x: 0, y: 0 },
      data: validData,
    });
  });

  return { nodes, edges };
};

export const mapViewsToNodesAndEdges = (snapshot: SnapshotDetails) => {
  const nodes: ViewNode[] = [];
  const edges: Edge[] = [];

  const views: ViewItem[] = Array.isArray(snapshot.views_data?.views)
    ? snapshot.views_data!.views
    : [];
  const matViews: ViewItem[] = Array.isArray(snapshot.views_data?.materialized_views)
    ? snapshot.views_data!.materialized_views
    : [];

  const diffData = snapshot.views_diff_data || {};
  const isNested = 'views' in diffData || 'materialized_views' in diffData;

  const processList = (list: ViewItem[], diff: SafeDiff, type: 'view' | 'materialized_view') => {
    list.forEach((v: ViewItem) => {
      const status = isNameInList(v.name, diff.added)
        ? 'added'
        : diff.changed[v.name]
          ? 'changed'
          : 'normal';
      const changedView = diff.changed[v.name] as { old?: string } | undefined;
      const oldDefinition = changedView?.old || (status === 'added' ? undefined : v.definition);

      const validViewData = ViewNodeDataSchema.parse({
        label: v.name,
        status,
        type,
        definition: v.definition,
        oldDefinition,
      });

      nodes.push({
        id: `view-${v.name}`,
        type: 'customView',
        position: { x: 0, y: 0 },
        data: validViewData,
      });
    });

    diff.removed.forEach((r: unknown) => {
      const name = typeof r === 'string' ? r : (r as ViewItem)?.name;
      if (name && !nodes.some((n) => n.id === `view-${name}`)) {
        const validRemovedData = ViewNodeDataSchema.parse({
          label: name,
          status: 'removed',
          type,
        });
        nodes.push({
          id: `view-${name}`,
          type: 'customView',
          position: { x: 0, y: 0 },
          data: validRemovedData,
        });
      }
    });
  };

  const nestedDiff = diffData as DiffDataNested;
  processList(views, extractDiffSafe(isNested ? nestedDiff.views : diffData), 'view');
  processList(
    matViews,
    extractDiffSafe(isNested ? nestedDiff.materialized_views : diffData),
    'materialized_view',
  );

  return { nodes, edges };
};
// endregion
