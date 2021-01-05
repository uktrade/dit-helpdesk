from .base import (
    BaseCommodityObjectDetailView,
    BaseSectionedCommodityObjectDetailView,
)
from .helpers import _commodity_code_html
from .sections import (
    BaseOtherMeasuresNorthernIrelandSection,
    BaseTariffsAndTaxesNorthernIrelandSection,
    ProductRegulationsNorthernIrelandSection,
    QuotasNorthernIrelandSection,
    RulesOfOriginNorthernIrelandSection,
)
from .views import (
    ChapterDetailView,
    HeadingDetailNorthernIrelandView,
    HeadingDetailView,
    measure_quota_detail,
    MeasureConditionDetailView,
    section_detail,
    SubHeadingDetailNorthernIrelandView,
    SubHeadingDetailView,
)
