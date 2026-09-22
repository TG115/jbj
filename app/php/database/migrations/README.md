# Laravel Migrations

JBJ does not use Laravel migrations.

The shared database schema is managed from:

`/database/migrations`

Run migrations from the project root:

```bash
make migrate
```

Do not use `php artisan migrate` for JBJ schema changes.