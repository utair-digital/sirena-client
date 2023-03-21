from sirena_client.base.exception import BaseError


class SirenaResponseError(BaseError):
    """Ошибка в ответе от сирены"""
    http_code = 500
    error_code = 50001
    message = 'sirena response error'


class BaseSirenaError(BaseError):
    """Базовое исключение для ошибок в сирене"""
    http_code = 500
    error_code = 50000
    message = "sirena error"


class SirenaEmptyResponse(SirenaResponseError):
    """Прочитан пустой ответ сирены. Возможно ошибка соединения или прокси"""
    http_code = 500
    error_code = 50002
    message = 'sirena empty response or connection error'


class SirenaSystemError(BaseSirenaError):
    """ Невозможно обработать системная ошибка """
    http_code = 500
    error_code = 50001
    message = "sirena system error"


class SirenaEncryptionKeyError(BaseSirenaError):
    """Ошибки связанные с ключами шифрования"""
    http_code = 500
    error_code = 50080
    message = 'sirena encryption key error'


class SirenaClaimError(BaseSirenaError):
    """Ошибка при клейме"""
    http_code = 500
    error_code = 50004
    message = "some error in claim process"


# ~~~~~~~~~~~~~~~~~~~ 400 ~~~~~~~~~~~~~~~~~~~~~~~

class SirenaPnrBusyError(BaseSirenaError):
    """Pnr занята другим пульто"""
    http_code = 400
    error_code = 40001
    message = "Pnr is busy"


class SirenaPnrWaitingForPaymentConfirmationError(BaseSirenaError):
    """PNR ожидает подтверждение оплаты"""
    http_code = 400
    error_code = 40002
    message = "The PNR is waiting for payment confirmation"


class WrongDocumentPaymentDocumentType(BaseSirenaError):
    """Некорректный тип документа"""
    http_code = 400
    error_code = 40003
    message = "Wrong payment document type"


class SirenaMaxRetriesExceededError(BaseSirenaError):
    """Ошибка при использовании максимального кол-ва попыток запроса"""
    http_code = 500
    error_code = 50005
    message = "The request max count limit has been exceeded."


class SirenaWrongDocumentIssuedCountry(BaseSirenaError):
    """Документ не мог быть выпущен в предоставленной с ним стране"""
    http_code = 400
    error_code = 40004
    message = 'This document cannot have been issued in this country'


class SirenaDepartureDateInPast(BaseSirenaError):
    """В пункте отправления наступил новый день по местному времени
    Ошибка: {@code: '33235', text: 'Departure date in past'}
    """
    http_code = 400
    error_code = 40005
    message = "The departure date is in past"


class SirenaUnableToDerminateAirlineCode(BaseSirenaError):
    """Не удалось определить код авиакомпании"""
    http_code = 400
    error_code = 40006
    message = "Cannot determine ariline code"


class SirenaMoreThanOneSublassProvided(BaseSirenaError):
    """Указано больше одного подкласса"""
    http_code = 400
    error_code = 40007
    message = "More than one subclass provided"


class SirenaDateNotControl(BaseSirenaError):
    http_code = 400
    error_code = 40008
    message = "Date not control"


class SirenaInvalidNumberOfSSR(BaseSirenaError):
    """
    Неправильное кол-во SSR
    Пример: NUMBER OF SSR SEAT'S ON THE PASSENGER/SEGMENT IS MORE THAN PASSENGER NUMBER SEATS (S 1,P 1)
    """
    http_code = 400
    error_code = 40009
    message = "NUMBER OF SSR ON THE PASSENGER/SEGMENT IS MORE THAN PASSENGER NUMBER SEATS"


class SirenaUnableToCancelServices(BaseSirenaError):
    """
    Невозможно отменить услугу, emd выписан
    """
    http_code = 400
    error_code = 40010
    message = "Can't cancel selected services, emd issued"


class SirenaOperationCostOrCurrencyError(BaseSirenaError):
    """
    Цена или валюта операции не соотвествуют запросу
    """
    http_code = 400
    error_code = 40011
    message = "Operation cost or currency doesn't match query one"


class SirenaPNRWasChanded(BaseSirenaError):
    """PNR было изменено с момента последнего просмотра"""
    http_code = 400
    error_code = 40012
    message = "PNR was changed since last request"


class SirenaUnableToDeleteSegment(BaseSirenaError):
    """Не удалось удалить сегмент"""
    http_code = 400
    error_code = 40013
    message = "Unable to delete segment"

# ~~~~~~~~~~~~~~~~~~ 403 ~~~~~~~~~~~~~~~~~~~~~~~~


class SirenaPnrAndSurnameDontMatch(BaseSirenaError):
    """Не коректная пара pnr and last name"""
    http_code = 403
    error_code = 40304
    message = "PNR and surname do not match"


class SirenaDuplicateSvc(BaseSirenaError):
    """Услуга уже была добавлена"""
    http_code = 403
    error_code = 40305
    message = "svc already added in PNR"


class SirenaSeatMapIsTurnedOff(BaseSirenaError):
    """Не найдены цены на услуги """
    http_code = 403
    error_code = 40306
    message = "Seat map is turned off"


class SirenaInsuranceExists(BaseSirenaError):
    """Страховка с указанными параметрами уже присутствует в броне"""
    http_code = 403
    error_code = 40307
    message = 'Insurance already exists in order'


class SirenaPnrHasSvcError(BaseSirenaError):
    """ Действие запрещено пока у заказа есть услуги """
    http_code = 403
    error_code = 40308
    message = 'This action is prohibited while the pnr has services'


class SirenaUnusedSegmentsMustReturned(BaseSirenaError):
    """ Запрещено действие, все неиспользуемые сегменты должны быть возвращены  """
    http_code = 403
    error_code = 40309
    message = 'All unused segments must be returned'


class SirenaPnrAlreadyUnArchived(BaseSirenaError):
    """ Pnr существует / разархивация выполнена второй раз"""
    http_code = 403
    error_code = 40310
    message = 'PNR Already exists or was already unarchived'


class SirenaEmdCancelDenied(BaseSirenaError):
    """Срок возможности отмены emd истек. Возможнен только возврат"""
    http_code = 403
    error_code = 40311
    message = 'EMD cancel denied. Refund only'


class SirenaDuplicateSsr(BaseSirenaError):
    """ssr уже был добавлен"""
    http_code = 403
    error_code = 40312
    message = 'SSR already added in PNR'


class SirenaUnableToFindReceiptForPnr(BaseSirenaError):
    """Не удалось найти квитанцию для PNR"""
    http_code = 403
    error_code = 40313
    message = 'Could not find receipt for PNR'


class SirenaChangeIsNotPermitted(BaseSirenaError):
    """Изменения запрещены"""
    http_code = 403
    error_code = 40314
    message = 'Change is not permitted. Try cancellation'


class SirenaCantAddSSRToNotActiveSegment(BaseSirenaError):
    """Нельзя добавить SSR в не активный сегмент"""
    http_code = 403
    error_code = 40315
    message = 'Cant add ssr to not active segment'


class SirenaAccessToPnrDenied(BaseSirenaError):
    """Доступ к указанному PNR запрещен"""
    http_code = 403
    error_code = 40316
    message = 'Access to the specified PNR is denied'


class SirenaPnrNotBookedOnline(BaseSirenaError):
    """Этот PNR забронирован не через интернет"""
    http_code = 403
    error_code = 40317
    message = 'This PNR is not booked online'

# ~~~~~~~~~~~~~~~~~~ 404 ~~~~~~~~~~~~~~~~~~~~~~~~~


class SirenaOrderNotFound(BaseSirenaError):
    """Заказ не найден в сирене"""
    http_code = 404
    error_code = 40405
    message = "order in sirena not found"


class SirenaInvalidFlightNumber(BaseSirenaError):
    """Неправильный номер рейса"""
    http_code = 404
    error_code = 40406
    message = "invalid flight number in requst"


class ServicePriceNotFoundError(BaseSirenaError):
    """Не найдены цены на услуги """
    http_code = 404
    error_code = 40407
    message = "Price for service not found"


class SirenaParseRequestError(BaseSirenaError):
    """ Неправильный запрос  """
    http_code = 404
    error_code = 40408
    message = "Request parse error"


class SirenaTicketNotExistError(BaseSirenaError):
    """ Билет не существует в заказе  """
    http_code = 404
    error_code = 40409
    message = "Ticket not exist in pnr"


class SirenaPassengerNotFoundError(BaseSirenaError):
    """  Пассажир не был найден  """
    http_code = 404
    error_code = 40410
    message = "Passenger not found in pnr"


class SirenaTicketOrDocumentNumberNotFound(BaseSirenaError):
    """401 TICKET/DOCUMENT NUMBER NOT FOUND"""
    http_code = 404
    error_code = 40411
    message = "Ticket/Document number not found"


class SirenaSegmentNotFoundError(BaseSirenaError):
    """ Сегмент не найден в PNR"""
    http_code = 404
    error_code = 40412
    message = "No such segment in PNR"


class SirenaPassengersTitleNotFoundError(BaseSirenaError):
    """ Обращение к пассажиру не было найдено (Mr/Mrs/Ms/Miss) """
    http_code = 404
    error_code = 40411
    message = "Passenger's title not found in pnr"

# ~~~~~~~~~~~~~~~~~~ 408 ~~~~~~~~~~~~~~~~~~~~~~~~~


class SirenaMessageTimedOutError(BaseSirenaError):
    """
    Таймаут при получении сообщения

    "error": {
        "@code": "-1",
        "text": "ETS UT: EDIFACT MESSAGE TIMING OUT, PLEASE RETRY"
    }

    """
    http_code = 408
    error_code = 40501
    message = "Message timed out"


class SirenaInternalError(BaseSirenaError):
    http_code = 500
    error_code = 50001
    message = "Internal error"


class SirenaPultBusyError(BaseSirenaError):
    http_code = 500
    error_code = 50003
    message = "There is no free pult to work up query"


class SirenaFobiddenIpAddress(BaseSirenaError):
    http_code = 500
    error_code = 50002
    message = "Forbidden ip address"
