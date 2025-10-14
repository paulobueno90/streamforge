from streamforge.base.normalize.normalize import GeneralNormalizers, Normalizer
from streamforge.ingestion.okx.normalizers.ohlc import KlineNormalizer
from typing import Union, Dict, Any, List
from streamforge.base.normalize.ohlc.models.candle import Kline
from streamforge.ingestion.okx.normalizers.util import not_data, get_channel_type


normalizer_map = {
    "candle": KlineNormalizer(),
}


class OkxNormalizers(GeneralNormalizers):

    def api(self, data: Union[Dict[str, Any], List]):
        pass

    def ws(self, data: Dict[str, Any]) -> Union[Kline, None]:
        if not_data(data=data):
            return None

        channel_type = get_channel_type(data["arg"]["channel"])
        if normalizer := self._normalizers_map.get(channel_type):
            return normalizer.ws(data)
        else:
            raise NotImplementedError(f'Stream Type: {channel_type}. Normalizer not implemented.')


okx_normalizer = OkxNormalizers(normalizers_map=normalizer_map)