from .base import (
    BaseCommodityObjectDetailView,
    BaseSectionedCommodityObjectDetailView,
)
from .helpers import _commodity_code_html
from .sections import (
    BaseTariffAndChargesNorthernIrelandSection,
    OtherMeasuresNorthernIrelandSection,
    ProductRegulationsNorthernIrelandSection,
    QuotasNorthernIrelandSection,
    RulesOfOriginNorthernIrelandSection,
)
from .views import (
    chapter_detail,
    HeadingDetailNorthernIrelandView,
    HeadingDetailView,
    measure_condition_detail,
    measure_quota_detail,
    section_detail,
    SubHeadingDetailNorthernIrelandView,
    SubHeadingDetailView,
)
