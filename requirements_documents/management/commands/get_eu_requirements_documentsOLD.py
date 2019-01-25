def get_and_store_commodity_documents(commodity_obj, country, language='EN'):

    url = REQUIREMENTS_URL % {
        'origin_country': country, 'commodity': commodity_obj.commodity_code,
        'language': language, 'destination_country': 'GB'
    }

    response = requests.get(url)
    data = json.loads(response.content)

    for item in data:
        code = mclean(item["code"])
        label = mclean(item["label"])
        requirement_type = mclean(item["type"])

        document = get_commodity_document(code, requirement_type)
        if document is None:
            continue

        HasRequirementDocument.objects.get_or_create(
            commodity=commodity_obj, document=document,
            eu_trade_helpdesk_website_destination_country='GB',
            eu_trade_helpdesk_website_origin_country=country,
            eu_trade_helpdesk_website_label=label,
        )
        print('finished: ' + commodity_obj.commodity_code)




def get_commodity_document(
        code, requirement_type, destination_country='eu', language='en'
):
    url = REQUIREMENT_URL % {
        'destination_country': destination_country, 'language': language,
        'code': code, 'requirement_type': requirement_type
    }
    response = requests.get(url)
    if response.status_code != 200:
        print('warning: %s gave status: %s' % (url, response.status_code))
        return None

    document, created = RequirementDocument.objects.get_or_create(
        code=code, requirement_type=requirement_type,
        destination_country=destination_country, language=language
    )

    html = response.text
    document.html = html
    document.html_normalised = fhtml(html)
    document.query_url = url
    document.save()

    return document


def create_db_objects_OLD(document_dicts, hasreq_dicts):

    doc_objects = [
        RequirementDocument(**copy_dict(di, without=['temp_uid']))
        for di in document_dicts
    ]
    import pdb; pdb.set_trace()
    doc_objects = bulk_upsert2(
        RequirementDocument.objects.all(),
        doc_objects,
        RequirementDocument.UNIQUENESS_FIELDS,
        RequirementDocument.ALL_FIELDS
    )

    for i, di in hasreq_dicts:
        import pdb; pdb.set_trace()
        di['document'] = doc_objects[i]

    has_req_document_objects = [
        HasRequirementDocument(**copy_dict(di, without=['document_temp_uid']))
        for di in hasreq_dicts
    ]
    from manager_utils.manager_utils import bulk_upsert, bulk_upsert2
    has_req_document_objects = bulk_upsert2(
        HasRequirementDocument.objects.all(),
        has_req_document_objects,
        HasRequirementDocument.UNIQUENESS_FIELDS,
        HasRequirementDocument.ALL_FIELDS
    )
    import pdb; pdb.set_trace()