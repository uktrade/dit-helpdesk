# from django.views.decorators.cache import cache_page
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest

from headings.models import Heading


def heading_detail(request, heading_code):
    if len(heading_code) == 4:
        heading = get_object_or_404(Heading, heading_code_4=heading_code)
    else:  # len == 10
        heading = get_object_or_404(Heading, heading_code=heading_code)

    context = {'heading': heading}
    return render(request, 'heading_detail.html', context)


def heading_data(request, heading_code):

    if len(heading_code) == 4:
        heading = get_object_or_404(Heading, heading_code_4=heading_code)
    else:  # len == 10
        heading = get_object_or_404(Heading, heading_code=heading_code)

    heading_data, leafs, _ = get_heading_data(heading, '.')

    return JsonResponse({'treeData': heading_data})


def get_heading_data(heading, root_name):
    root_di = {
        'name': root_name, 'node_id': "root", 'children': []
    }
    all_flattened, leafs = [], []
    heading_leafs = heading.children_concrete.all()
    for commodity in heading_leafs:
        root_di['children'].append({
            'name': commodity.tts_title, 'node_id': str(commodity.pk),
            'children': [], 'href': commodity.get_absolute_url(),
            'commodity_code': commodity.commodity_code
        })
        leafs.append(commodity)
        all_flattened.append(commodity)

    for subheading in heading.child_subheadings.all():
        root_di['children'].append(
            _get_subheading_tree(subheading, leafs, all_flattened)
        )
        all_flattened.append(subheading)
    return root_di, leafs, all_flattened


def _get_subheading_tree(subheading, leafs, all_flattened):
    abs_commodity_di = {
        'name': subheading.tts_heading_obj.title,
        'children': [], 'node_id': str(subheading.pk),
        'commodity_code': subheading.commodity_code
    }
    children = []
    for commodity in subheading.children_concrete.all():
        children.append({
            'name': commodity.tts_title, 'node_id': str(commodity.pk),
            'children': [], 'href': commodity.get_absolute_url(),
            'commodity_code': commodity.commodity_code
        })
        leafs.append(commodity)
        all_flattened.append(commodity)

    for child_abs_commodity in subheading.child_subheadings.all():
        children.append(
            _get_subheading_tree(child_abs_commodity, leafs, all_flattened)
        )
        all_flattened.append(child_abs_commodity)

    # order nodes by commodity codes with nodes labelled 'Other' last
    def child_rank(di):
        return di['name'] == 'Other', di['commodity_code']
    children.sort(key=child_rank)

    abs_commodity_di['children'] = children
    return abs_commodity_di
