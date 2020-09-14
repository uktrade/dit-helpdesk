"""
Prepare data subsets for testing from actual JSON data

"""
from collections import defaultdict, Counter
import os
import json
import logging

data_dir = "import_data/prepared"

entities = ['sections', 'chapters', 'headings', 'sub_headings', 'commodities']

data_paths = {
    key: os.path.join(data_dir, f"{key}.json")
    for key in entities
}

# means how many of these children *each* immediate parent object can have
# if no entry means every instance of the object is included
limits = {
    "headings": 4,
    "sub_headings": 4,
    "commodities": 4,
}


logger = logging.getLogger(__name__)


def load_data():
    data = {}

    for entity, path in data_paths.items():
        with open(path) as f:
            data[entity] = json.load(f)

    return data


def _extend(a, b):
    return a.extend(b)


def _prepare_subsets(data, subsets, entities_left, parents):
    if not entities_left:
        return

    entity = entities_left.pop(0)
    limit = limits.get(entity)
    logger.info("Preparing subsets for %s", entity)

    children_by_parent = defaultdict(list)
    children = []
    children_counts = Counter()

    for item in data[entity]:
        parent_sid = item['parent_goods_nomenclature_sid']
        if parent_sid not in parents or children_counts[parent_sid] >= limit:
            continue

        children_by_parent[parent_sid].append(item["goods_nomenclature_sid"])
        children.append(item["goods_nomenclature_sid"])
        children_counts[parent_sid] += 1
        subsets[entity].append(item)

    _prepare_subsets(data, subsets, entities_left, children)


def prepare_subsets(data):
    """
    Sections and Chapters are linked in a different way than the other entities, so there needs
    to be a separate entry point with extra logic.
    Section (parent) has a list of chapter IDs (children), whereas in the other entities it's the
    children which contain an ID to the parent.

    :param data:
    :return:
    """
    subsets = defaultdict(list)

    sections = data["sections"]

    children = set()
    #import ipdb; ipdb.set_trace()
    for section in sections[:limits.get("sections")]:
        subsets["sections"].append(section)
        children = children | (
            set(
                section["child_goods_nomenclature_sids"][:limits.get("chapters")]
            )
        )
    #import ipdb; ipdb.set_trace()
    for chapter in data["chapters"]:
        chapter_sid = chapter["goods_nomenclature_sid"]
        if chapter_sid not in children:
            continue
        subsets["chapters"].append(chapter)
    #import ipdb; ipdb.set_trace()
    _prepare_subsets(data, subsets, entities[2:], children)

    return subsets


def main():
    data = load_data()
    subsets = prepare_subsets(data)

    for key, val in subsets.items():
        print(f"{key} - {len(val)}")

    out_dir = "import_data/test_subsets"

    for key, val in subsets.items():
        with open(os.path.join(out_dir, f"{key}.json"), 'w') as f:
            json.dump(val, f, indent=4)
    import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    main()
