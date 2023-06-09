from typing import Any, Optional

from source.clients.binance.connector import BinanceConnectorAbstract, DefaultBinanceConnector
from source.clients.binance.schemas.market.schemas import ExchangeInfoResponse, LatestPriceResponse
from source.clients.binance.schemas.order.schemas import NewOrderRequest, NewOrderResponse
from source.clients.binance.schemas.wallet.schemas import APITradingStatusResponse
from source.clients.binance.signature import BaseSignature


class BinanceClient:

    def __init__(self, connector: Optional[BinanceConnectorAbstract] = None, **kwargs: Any):
        self._connector = connector or DefaultBinanceConnector(**kwargs)

    async def __aenter__(self) -> 'BinanceClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._connector.close()

    @property
    def connector(self) -> BinanceConnectorAbstract:
        if self._connector is None:
            raise TypeError('Connector is not initialized')
        return self._connector

    async def exchange_info(self, symbol: str) -> ExchangeInfoResponse:
        return await self._connector.request(
            path='/api/v3/exchangeInfo',
            method='GET',
            params={
                'symbol': symbol.upper(),
            },
            response_model=ExchangeInfoResponse,
        )

    async def get_api_trading_status(self, params: Optional[BaseSignature] = None) -> APITradingStatusResponse:
        params = params or BaseSignature()
        params.sign()
        return await self._connector.request(
            path='/sapi/v1/account/apiTradingStatus',
            method='GET',
            params=params.dict(exclude_none=True),
            response_model=APITradingStatusResponse,
        )

    async def create_new_order(self, request: NewOrderRequest) -> NewOrderResponse:
        request.sign()
        return await self._connector.request(
            path='/api/v3/order',
            method='POST',
            body=request.to_query(),
            response_model=NewOrderResponse,
        )

    async def get_latest_price(self, symbol: str) -> LatestPriceResponse:
        return await self._connector.request(
            path='/api/v3/ticker/price',
            method='GET',
            params={
                'symbol': symbol.upper(),
            },
            response_model=LatestPriceResponse,
        )
