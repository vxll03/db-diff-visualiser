import { Icon } from '#components';

export const renderIcon = (iconName: string, color?: string) => {
  return () => h(Icon, { name: iconName, size: '18', style: color ? `color: ${color}` : '' });
};
