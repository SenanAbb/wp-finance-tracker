-- Seed: Categorías y datos mock para usuario +34643326603
-- Fechas: Oct 2025 - Mar 2026
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

-- Insertar usuario de prueba
insert into public.users (phone_number, display_name)
values ('+34643326603', 'Sanan Abbasov')
on conflict (phone_number) do nothing;

-- Obtener el ID del usuario para usar en las siguientes inserciones
with user_data as (
  select id from public.users where phone_number = '+34643326603'
)

-- Insertar múltiples cuentas bancarias
insert into public.accounts (user_id, name, type, balance, currency)
select 
  user_data.id,
  account.name,
  account.type,
  account.balance,
  'EUR'
from user_data,
lateral (
  values
    ('Efectivo', 'cash', 3.80),
    ('Revolut', 'banco', 859.03)
) as account(name, type, balance)
on conflict do nothing;