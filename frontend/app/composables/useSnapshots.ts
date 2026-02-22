import { useQuery } from '@tanstack/vue-query';
import { apiClient } from '~/utils/apiClient';
import { LatestSnapshotResponseSchema, type LatestSnapshot } from '~/schemas/snapshots.schema';

export const useLatestSnapshotsQuery = (limit: number = 10) => {
  return useQuery({
    queryKey: ['latest-snapshots', limit],
    queryFn: async (): Promise<LatestSnapshot[]> => {
      const data = await apiClient(`/snapshots/latest?limit=${limit}`);
      return LatestSnapshotResponseSchema.parse(data);
    }
  });
};

export const useSnapshotTimelineQuery = (projectId: number) => {
  return useQuery({
    queryKey: ['snapshots', projectId],
    queryFn: async () => await apiClient(`/snapshots/${projectId}`),
  });
}

export const useSnapshotDetailsQuery = (projectId: number, selectedRevision: Ref<number | null>) => {
  return useQuery({
    queryKey: ['snapshot-details', projectId, selectedRevision],
    queryFn: async () => await apiClient(`/snapshots/${projectId}/${selectedRevision.value}`),
    enabled: computed(() => !!selectedRevision.value),
  });
}