from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('knotapp', '0006_profile_email_verified'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE EXTENSION IF NOT EXISTS pg_trgm;

                CREATE INDEX IF NOT EXISTS knotapp_user_email_lower_idx
                ON auth_user (LOWER(email));

                CREATE INDEX IF NOT EXISTS knotapp_user_username_trgm_idx
                ON auth_user USING GIN (LOWER(username) gin_trgm_ops);

                CREATE INDEX IF NOT EXISTS knotapp_user_first_name_trgm_idx
                ON auth_user USING GIN (LOWER(first_name) gin_trgm_ops);

                CREATE INDEX IF NOT EXISTS knotapp_user_last_name_trgm_idx
                ON auth_user USING GIN (LOWER(last_name) gin_trgm_ops);
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS knotapp_user_last_name_trgm_idx;
                DROP INDEX IF EXISTS knotapp_user_first_name_trgm_idx;
                DROP INDEX IF EXISTS knotapp_user_username_trgm_idx;
                DROP INDEX IF EXISTS knotapp_user_email_lower_idx;
            """,
        ),
    ]
