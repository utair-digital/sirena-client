from abc import ABC
from typing import Optional, Dict
from pydantic import BaseModel, PrivateAttr
from xmltodict import parse, expat
from ..messaging.response import ResponseABC
from ..exception import BaseError
from ... import exceptions
from ..types import AsymEncryptionHandShake, PublicMethods

EXCEPTION_MAP = {
    '-42': exceptions.SirenaEncryptionKeyError,  # Кастомный код и ошибка
    '-1': exceptions.SirenaMessageTimedOutError,
    '7505': exceptions.SirenaTicketNotExistError,
    '4006': exceptions.SirenaDateNotControl,
    '28067': exceptions.SirenaPnrAlreadyUnArchived,
    '25235': exceptions.SirenaDuplicateSsr,
    '28151': exceptions.SirenaWrongDocumentIssuedCountry,
    '31054': exceptions.SirenaSystemError,
    '31112': exceptions.SirenaTicketOrDocumentNumberNotFound,
    '31196': exceptions.SirenaUnableToCancelServices,
    '31198': exceptions.SirenaInvalidNumberOfSSR,
    '33000': exceptions.SirenaInternalError,
    '33002': exceptions.SirenaPultBusyError,
    '33003': exceptions.SirenaParseRequestError,
    '33009': exceptions.SirenaParseRequestError,
    '33010': exceptions.SirenaParseRequestError,
    '33011': exceptions.SirenaOrderNotFound,
    '33029': exceptions.WrongDocumentPaymentDocumentType,
    '33033': exceptions.SirenaPnrNotBookedOnline,
    '33034': exceptions.SirenaPnrAndSurnameDontMatch,
    '33036': exceptions.SirenaMoreThanOneSublassProvided,
    '33041': exceptions.SirenaPnrBusyError,
    '33044': exceptions.SirenaPnrWaitingForPaymentConfirmationError,
    '33057': exceptions.SirenaOperationCostOrCurrencyError,
    '33080': exceptions.SirenaUnableToFindReceiptForPnr,
    '33092': exceptions.SirenaAccessToPnrDenied,
    '33099': exceptions.SirenaPassengerNotFoundError,
    '33158': exceptions.SirenaInvalidNumberOfSSR,
    '33177': exceptions.SirenaSegmentNotFoundError,
    '33381': exceptions.SirenaPNRWasChanded,
    '33484': exceptions.SirenaCantAddSSRToNotActiveSegment,
    '33494': exceptions.SirenaFobiddenIpAddress,
    '33521': exceptions.SirenaPnrHasSvcError,
    '33529': exceptions.SirenaInvalidFlightNumber,
    '33553': exceptions.SirenaUnableToDeleteSegment,
    '31211': exceptions.SirenaDuplicateSvc,
    '37021': exceptions.SirenaSeatMapIsTurnedOff,
    '65108': exceptions.SirenaUnableToDerminateAirlineCode,
    '65167': exceptions.SirenaChangeIsNotPermitted,
    '65538': exceptions.SirenaInsuranceExists,
    '65572': exceptions.SirenaInsuranceExists,
    '65148': exceptions.SirenaUnusedSegmentsMustReturned,
    '101171': exceptions.SirenaEmdCancelDenied
}


class ResponseModelABC(BaseModel, ABC):
    response: ResponseABC
    error: Optional[BaseError]

    _parsed_response: Optional[Dict] = PrivateAttr(default=None)
    _root_level_key: str = 'answer'

    class Config:
        arbitrary_types_allowed = True

    def __nonzero__(self) -> bool:
        return bool(self.error is None)

    __bool__ = __nonzero__

    @property
    def method_name(self) -> str:
        if not self.response.method_name:
            raise Exception("Method name must be provided")
        return self.response.method_name

    @classmethod
    def parse(cls, response: ResponseABC) -> "ResponseModelABC":
        response = cls(response=response)
        response._check_for_error()
        return response

    @property
    def payload(self) -> Optional[Dict]:
        if self._parsed_response is None:
            self._parsed_response = self._parse_response()
        return self._parsed_response

    def raise_for_error(self):
        if self.error is not None:
            raise self.error

    @property
    def should_retry(self) -> bool:
        return not bool(self.response)

    @property
    def symmetric_key(self) -> bytes:
        """
        Получение симметричного ключа шифрования,
        если этот 'Response' ассимитричного шифрования для хэндшейка
        """
        if self.method_name != AsymEncryptionHandShake.ASYM_HAND_SHAKE.value:
            raise RuntimeError("Trying to get symmetric key from from invalid response method")
        return self.data   # noqa

    @property
    def data(self) -> Optional[Dict]:
        if not self.payload or self.error is not None:
            return self.payload
        return self.payload[self._root_level_key][self.method_name]

    @staticmethod
    def _remove_symbol(_base_xml: str, _line_no: int, _offset: int) -> str:
        """
        Метод вырезания некорректного символа в xml, который не позволяет корректно распарсить xml
        :param _base_xml: базовый текст xml
        :param _line_no: номер строки, на которой произошла ошибка
        :param _offset: отступ с начала строки, на котором произошла ошибка
        :return: скорректированный xml
        """
        splitted = _base_xml.split("\n")
        splitted[_line_no - 1] = splitted[_line_no - 1][:_offset] + splitted[_line_no - 1][_offset + 1:]
        return "\n".join(splitted)

    def _parse_response(self) -> Optional[Dict]:
        """
        В некоторых случаях агенты добавляют нечитаемые символы
        в элементы, пробуем распарсить несколько раз
        """
        result = None
        result_attempt = 0
        payload = self.response.payload
        while not result and result_attempt < 5:
            try:
                result = dict(
                    parse(
                        payload,
                        attr_prefix='@',
                        cdata_key='text',
                        force_list=self._get_force_list(self.method_name),
                        dict_constructor=dict
                    )
                )['sirena']
            except expat.ExpatError as e:
                payload = self._remove_symbol(payload, e.lineno, e.offset)
                result_attempt += 1
        return result

    @staticmethod
    def _get_force_list(method_name: str):
        """
        Возвращает force list для парсинга xml
        :param method_name: Метод в сирене
        :return:
        """
        # TODO: need more tests
        #  функция вычисления проставления флага для полей, которые могут быть как списком, так и не списком, пример:
        #  поле flight - может быть ключом списка перелетов и в то же время может быть номером рейса у сегмента,
        #  поэтому нельзя просто проставить этот ключ в force_list
        force_list_for_method = {
            'order': (
                'passenger', 'segment', 'svc',
                'leg', 'price', 'ssr', 'contact',
                'email', 'payment', 'insurance'
            ),
            "svc_add": (  # такие же как order, чтобы проще разбирать ответ
                'passenger', 'segment', 'svc',
                'leg', 'price', 'ssr', 'contact',
                'email', 'payment', 'insurance'
            ),
            'pricing_route': (
                'flight', 'variant'
            ),
            "pricing_variant": (
                "direction", "svc", "price"
            ),
            # "pricing_variant": pricing_variant,
            'view_flown_status': (
                'passenger', 'segment', 'svc'
            )
        }
        if method_name in force_list_for_method.keys():
            return force_list_for_method.get(method_name)
        return tuple()

    def _check_for_error(self):
        self._check_expired_keys_error(self.payload)

        error_level = self.payload.get(self._root_level_key, dict()).get(self.method_name)
        if not error_level:
            return
        if 'error' not in error_level:
            return
        error_code = error_level.get("error", {}).get("@code")
        error_text = error_level.get("error", {}).get("text")
        if error_code in EXCEPTION_MAP.keys():
            self.error = EXCEPTION_MAP.get(error_code)
            return
        self.error = exceptions.BaseSirenaError(
            message=f'Unhandled error by sirena response with code {error_code}: {error_text}'
        )

    def _check_expired_keys_error(self, error: Dict):
        root_level = error.get(self._root_level_key)
        error = root_level.get('error')
        if not error and self.method_name != 'describe':
            error = root_level.get('describe')
        if not error:
            return
        if error and all([
            self.method_name not in PublicMethods._value2member_map_,   # noqa
            error.get('@code') and error.get('@code') == '-1',
            error.get('@crypt_error') and error.get('@crypt_error') in ('4', '5')
        ]):
            raise exceptions.SirenaEncryptionKeyError(error.get('@text', 'Unknown symmetric key'))
        if e := error.get('error') or error:
            raise exceptions.SirenaFobiddenIpAddress(e.get('text'), e.get('@code'))
