import dagre from 'dagre';
import type { Edge } from '@vue-flow/core';
import type { TableNode, ViewNode } from '@/schemas/parser.schema';

export const TABLE_NODE_WIDTH = 250;
export const VIEW_NODE_WIDTH = 300;
export const NODE_GAP_X = 50;
export const NODE_GAP_Y = 60;

export const TABLE_HEADER_HEIGHT = 42;
export const TABLE_REMOVED_PLACEHOLDER_HEIGHT = 40;
export const COLUMN_ROW_HEIGHT = 36;
export const TRIGGERS_HEADER_HEIGHT = 30;
export const TRIGGER_ROW_HEIGHT = 36;
export const NODE_PADDING_Y = 4;
export const VIEW_NODE_HEIGHT = 100;

export const calculateNodeHeight = (node: TableNode): number => {
  let height = TABLE_HEADER_HEIGHT;

  if (node.data!.status === 'removed' && !node.data!.columns?.length) {
    height += TABLE_REMOVED_PLACEHOLDER_HEIGHT;
  } else {
    height += (node.data!.columns?.length || 0) * COLUMN_ROW_HEIGHT;
  }

  if (node.data!.triggers?.length) {
    height += TRIGGERS_HEADER_HEIGHT + node.data!.triggers.length * TRIGGER_ROW_HEIGHT;
  }

  return height + NODE_PADDING_Y;
};

export const applyTableLayout = (nodes: TableNode[], edges: Edge[]) => {
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
    g.setGraph({ rankdir: 'LR', ranksep: 250, nodesep: NODE_GAP_Y });

    connectedNodes.forEach((node) => {
      g.setNode(node.id, { width: TABLE_NODE_WIDTH, height: calculateNodeHeight(node) });
    });

    edges.forEach((edge) => g.setEdge(edge.source, edge.target));
    dagre.layout(g);

    connectedNodes.forEach((node) => {
      const dagreNode = g.node(node.id);
      const h = calculateNodeHeight(node);
      node.position = { x: dagreNode.x - TABLE_NODE_WIDTH / 2, y: dagreNode.y - h / 2 };
      maxDagreX = Math.max(maxDagreX, node.position.x);
    });
  }

  const GRID_START_X = connectedNodes.length > 0 ? maxDagreX + 400 : 0;
  let currentX = GRID_START_X;
  let currentY = 0;
  let rowMaxHeight = 0;

  disconnectedNodes.forEach((node, index) => {
    const h = calculateNodeHeight(node);
    node.position = { x: currentX, y: currentY };
    rowMaxHeight = Math.max(rowMaxHeight, h);

    if ((index + 1) % 4 === 0) {
      currentX = GRID_START_X;
      currentY += rowMaxHeight + NODE_GAP_Y;
      rowMaxHeight = 0;
    } else {
      currentX += TABLE_NODE_WIDTH + NODE_GAP_X;
    }
  });

  return { nodes, edges };
};

export const applyViewLayout = (nodes: ViewNode[], edges: Edge[]) => {
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: 'LR', ranksep: 100, nodesep: NODE_GAP_Y });

  nodes.forEach((node) => {
    g.setNode(node.id, { width: VIEW_NODE_WIDTH, height: VIEW_NODE_HEIGHT });
  });

  dagre.layout(g);

  nodes.forEach((node) => {
    const dagreNode = g.node(node.id);
    node.position = { x: dagreNode.x - VIEW_NODE_WIDTH / 2, y: dagreNode.y - VIEW_NODE_HEIGHT / 2 };
  });

  return { nodes, edges };
};
