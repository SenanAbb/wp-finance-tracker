-- Se puede ejecutar con psql o desde el SQL editor de Supabase

-- Insertar categorías globales (sin user_id)
insert into public.categories (name, type)
values
  -- Categorías de gastos
  ('comida', 'expense'),
  ('transporte', 'expense'),
  ('hogar', 'expense'),
  ('ocio', 'expense'),
  ('salud', 'expense'),
  ('educación', 'expense'),
  ('trabajo', 'expense'),
  ('ropa', 'expense'),
  ('tecnología', 'expense'),
  ('otros', 'expense'),
  -- Categorías de ingresos
  ('salario', 'income'),
  ('freelance', 'income'),
  ('inversiones', 'income'),
  ('otros ingresos', 'income'),
  -- Categorías de inversión
  ('criptomonedas', 'investment'),
  ('acciones', 'investment'),
  ('fondos', 'investment')
on conflict do nothing;