import { useQuery } from '@tanstack/vue-query';
import { apiClient } from '~/utils/apiClient';
import { SnapshotCountResponseSchema, type SnapshotCount } from '~/schemas/stats.schema';

export const useSnapshotStatsQuery = () => {
  return useQuery({
    queryKey: ['snapshot-stats'],
    queryFn: async (): Promise<SnapshotCount[]> => {
      const data = await apiClient('/snapshots/count_by_date');
      return SnapshotCountResponseSchema.parse(data);
    },
  });
};
