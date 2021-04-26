from django.conf import settings


class EUCommodityObjectMixin:
    def get_commodity_object(self, **kwargs):
        commodity_code = kwargs["commodity_code"]
        nomenclature_sid = kwargs["nomenclature_sid"]

        eu_commodity_object = self.model.objects.for_region(
            settings.SECONDARY_REGION
        ).get_by_commodity_code(
            commodity_code=commodity_code, goods_nomenclature_sid=nomenclature_sid
        )

        if eu_commodity_object.should_update_tts_content():
            eu_commodity_object.update_tts_content()

        return eu_commodity_object
