import re


class FootnoteReferenceProcessor:
    """Used to keep state of encountered notes references in multiple rule texts."""

    NOTE_REFERENCE_REGEX = re.compile(r"\[[A-Za-z0-9.]+\]")
    INTRODUCTORY_NOTE_REFERENCE_REGEX = re.compile(r"@{doc:COMM}\[([A-Za-z0-9\s]+)\]")

    def __init__(self):
        self.found_note_ids = []
        self.unique_note_ids = set()
        self.note_number_by_id = {}

    def _replace_note_reference(self, ref_match):
        ref = ref_match.group()
        ref_id = ref.strip("[]")

        self.found_note_ids.append(ref_id)
        self.unique_note_ids.add(ref_id)

        # each newly encountered note reference gets an n+1 number, but if we've seen it before
        # we fetch the note reference number like it was when it was seen for the first time
        # e.g. [A] [B] [C] [B] would result in numbering of: A=1, B=2, C=3, so after replacing:
        # [1] [2] [3] [2]
        if ref_id not in self.note_number_by_id:
            self.note_number_by_id[ref_id] = len(self.unique_note_ids)

        note_number = self.note_number_by_id[ref_id]

        return f'<sup><a href="#roo_note_{note_number}" class="govuk-link">{note_number})</a></sup>'

    def replace_all_notes_references(self, text):
        if not text:
            return text

        text_replaced = self.NOTE_REFERENCE_REGEX.sub(
            self._replace_note_reference, text
        )
        return text_replaced

    def _replace_introductory_note_reference(self, ref_match):
        ref, *_ = ref_match.groups()

        ref_replaced = f"{ref} (below)"
        return ref_replaced

    def replace_all_introductory_notes_references(self, text):
        if not text:
            return text

        text_replaced = self.INTRODUCTORY_NOTE_REFERENCE_REGEX.sub(
            self._replace_introductory_note_reference, text
        )
        return text_replaced
