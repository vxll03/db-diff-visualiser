import { z } from 'zod';

export const AuthSchema = z.object({
  email: z.email('Некорректный email'),
  username: z.string().min(4, 'Минимум 4 символа').nullable(),
  password: z.string().min(8, 'Минимум 8 символов'),
});
