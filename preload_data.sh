set -e

python manage.py collectstatic --noinput
python manage.py migrate
python manage.py pull_api_update
python manage.py prepare_import_data
python manage.py prepare_search_data
python manage.py scrape_section_hierarchy
python manage.py import_old_rules_of_origin --data_path "import"
python manage.py import_rules_of_origin
python manage.py migrate_regulations
python manage.py generate_search_keywords -f search/data
python manage.py import_search_keywords -f output/keywords_and_synonyms_merged.csv
