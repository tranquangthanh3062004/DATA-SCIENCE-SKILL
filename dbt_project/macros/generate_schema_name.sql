{#
  Use the configured schema verbatim (silver / gold) instead of dbt's default
  "<target_schema>_<custom_schema>" so models land in the medallion schemas
  created by infrastructure/docker/init-db.sql.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
