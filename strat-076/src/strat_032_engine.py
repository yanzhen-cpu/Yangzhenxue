"""0.7.6 状态机：在 0.7.4 基线上应用固定代码排畸门禁。"""
from .strat_030_engine import Engine as PreviousEngine
from .strat_032_data import FILTER_POLICY


class Engine(PreviousEngine):
    def __init__(self, inputs, params=None):
        if inputs.get("exchange_filter_policy") != FILTER_POLICY:
            raise ValueError("BLOCKED_INPUT: STRAT-032 requires the confirmed fixed product-code filter")
        super().__init__(inputs, params)
        self.product_filter_screened = set()
        self.product_excluded = set(inputs["exchange_filter_excluded_products"])
        self.invalid_product_codes = set(inputs.get("product_code_invalid_products", ()))
        self.diagnostics.update(fixed_code_excluded_products=len(self.product_excluded),
            invalid_product_codes=len(self.invalid_product_codes))

    def screen(self, product):
        key = product, self.date
        value = super().screen(product)
        if key in self.product_filter_screened:
            return self.screen_cache[key]
        self.product_filter_screened.add(key)
        exchange = self.inputs["exchange_by_product"].get(product, "")
        blocked = product in self.product_excluded
        invalid = product in self.invalid_product_codes
        updated = dict(value)
        if invalid:
            updated.update(normal=False, reason="invalid_product_code")
        elif blocked:
            updated.update(normal=False, reason="excluded_exchange_product")
        self.screen_cache[key] = updated
        screening_row = next(row for row in reversed(self.screening_daily)
            if row["trade_date"] == str(self.date) and row["product_code"] == product)
        screening_row.update(status="normal" if updated["normal"] else "abnormal", reason=updated["reason"],
            exchange_code=exchange, exchange_filter_blocked=int(blocked),
            product_code_filter_blocked=int(blocked), product_code_valid=int(not invalid))
        volume_row = next(row for row in reversed(self.delivery_volume_daily)
            if row["trade_date"] == str(self.date) and row["product_code"] == product)
        volume_row.update(status=screening_row["status"], reason=screening_row["reason"], exchange_code=exchange,
            exchange_filter_blocked=int(blocked), product_code_filter_blocked=int(blocked),
            product_code_valid=int(not invalid))
        return updated

    def scan(self, allow_create=True):
        # 普通原单每日复查；固定代码排畸或代码异常命中后立即撤单。换月单独立保存，不重新筛选。
        for product in sorted(self.product_excluded | self.invalid_product_codes):
            if product in self.pending:
                reason = "invalid_product_code" if product in self.invalid_product_codes else "excluded_exchange_product"
                self.cancel(product, reason, "close")
        return super().scan(allow_create)
