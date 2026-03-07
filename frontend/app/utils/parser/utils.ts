// region Types

const hasNameProperty = (item: unknown): item is { name: string } => {
  return (
    typeof item === 'object' &&
    item !== null &&
    'name' in item &&
    typeof (item as { name: unknown }).name === 'string'
  );
};


export interface SafeDiff {
  added: unknown[];
  removed: unknown[];
  changed: Record<string, unknown>;
}

// endregion

// region Utils
export const isNameInList = (name: string, list: unknown): boolean => {
  if (!Array.isArray(list)) return false;
  
  return list.some((item) => {
    if (typeof item === 'string') return item === name;
    if (hasNameProperty(item)) return item.name === name;
    return false;
  });
};

export const extractDiffSafe = (diffObj: unknown): SafeDiff => {
  const safe = (typeof diffObj === 'object' && diffObj !== null ? diffObj : {}) as Record<string, unknown>;
  
  return {
    added: Array.isArray(safe.added) ? safe.added : [],
    removed: Array.isArray(safe.removed) ? safe.removed : [],
    changed: typeof safe.changed === 'object' && safe.changed !== null ? (safe.changed as Record<string, unknown>) : {},
  };
};

export const extractNames = (arr: unknown): string[] => {
  if (!Array.isArray(arr)) return [];
  
  return arr.map((item) => {
    if (typeof item === 'string') return item;
    if (hasNameProperty(item)) return item.name;
    return '';
  });
};
// endregion
