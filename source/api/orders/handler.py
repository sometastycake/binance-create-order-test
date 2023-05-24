from source.api.orders.errors import NotFoundSymbolInExchangeInfo
from source.api.orders.schemas import CreateOrderRequest, CreateOrderResponse
from source.clients.binance.client import BinanceClient
from source.clients.binance.schemas.market.schemas import ExchangeInfoResponse
from source.enums import OrderType, SymbolStatus


async def create_order_handler(request: CreateOrderRequest) -> CreateOrderResponse:
    async with BinanceClient(raise_if_error=True) as client:
        exchange_info: ExchangeInfoResponse = await client.exchange_info(request.symbol)
        try:
            symbol = exchange_info.get_symbol(request.symbol.upper())
        except NotFoundSymbolInExchangeInfo:
            return CreateOrderResponse(
                success=False,
                error='Not found trading symbol',
            )
        if not symbol.isSpotTradingAllowed:
            return CreateOrderResponse(
                success=False,
                error='Spot trading disabled',
            )
        if symbol.status in (SymbolStatus.HALT, SymbolStatus.BREAK, SymbolStatus.AUCTION_MATCH):
            return CreateOrderResponse(
                success=False,
                error='Wrong trading symbol status',
            )
        if OrderType.LIMIT not in symbol.order_types:
            return CreateOrderResponse(
                success=False,
                error='Limit order disabled',
            )
    return CreateOrderResponse(success=True)