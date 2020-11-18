from rules_of_origin.models import (
    RulesDocument, RulesDocumentFootnote, RulesGroup, RulesGroupMember,
    Rule, SubRule,
)

from .parser import parse_file


def import_roo(f):
    roo_data = parse_file(f)

