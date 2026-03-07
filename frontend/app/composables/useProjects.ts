import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query';
import { apiClient } from '~/utils/apiClient';
import { ApiProjectsSchema, type Project } from '~/schemas/projects.schema';

export const useProjectsQuery = () => {
  return useQuery({
    queryKey: ['projects'],
    queryFn: async (): Promise<Project[]> => {
      const data = await apiClient('/projects');
      return ApiProjectsSchema.parse(data);
    },
  });
};

export const useCreateProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (newProject: { name: string; icon: string }) => {
      return await apiClient('/projects', {
        method: 'POST',
        body: newProject,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
    onError: (err) => {
      console.error('Failed to create project:', err);
    },
  });
};

export const useUpdateProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (updatedProject: { id: number; name: string }) => {
      return await apiClient(`/projects/${updatedProject.id}`, {
        method: 'PATCH',
        body: { name: updatedProject.name },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
    onError: (err) => {
      console.error('Failed to update project:', err);
    },
  });
};

export const useDeleteProject = () => {
  return useMutation({
    mutationFn: async (projectId: number) => {
      return await apiClient(`/projects/${projectId}`, {
        method: 'DELETE',
      });
    },
    onError: (err) => {
      console.error('Failed to delete project:', err);
    },
  });
};
