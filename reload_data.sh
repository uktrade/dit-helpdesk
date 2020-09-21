python manage.py collectstatic --noinput
python manage.py migrate
python manage.py loaddata countries_data
python manage.py pull_api_update
python manage.py prepare_import_data
python manage.py prepare_search_data
python manage.py scrape_section_hierarchy
python manage.py import_rules_of_origin --data_path "import"
python manage.py import_regulations
python manage.py import_search_keywords -f output/commodity_category_all_with_synonyms_greenpage.csv
python manage.py swap_rebuild_index