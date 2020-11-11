from elasticsearch_dsl import analyzer

html_strip = analyzer(
    "html_strip",
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball", "asciifolding"],
    char_filter=["html_strip"],
)
