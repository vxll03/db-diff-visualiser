import dayjs from 'dayjs';

/**
 * Returns 'Feb 22, 2026'
 */
export const formatDate = (date: string | Date | null, formatStr: string = 'MMM D, YYYY') => {
  if (!date) return '';
  return dayjs(date).format(formatStr);
};

/**
 * Returns 'Feb 22, 14:30'
 */
export const formatDateTime = (date: string | Date | null) => {
  if (!date) return '';
  return dayjs(date).format('MMM D, HH:mm');
};
