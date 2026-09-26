"""0.7.6 数据适配：继承 0.7.5，只把普通新建排畸改为固定品种代码。"""
from .strat_031_data import *  # noqa: F401,F403
from .strat_031_data import load_previous_inputs
from .strat_032_notice_resolution import resolve_reviewed_rules, validate_frozen_resolution


FIXED_EXCLUDED_PRODUCTS = frozenset({"LC", "PD", "PS", "PT", "SI", "MA", "SH", "UR", "AG"})
FILTER_POLICY = "fixed_product_codes_v076"


def product_excluded(product, exchange_code=None):
    """固定代码排畸；exchange_code 仅保留给统一审计接口。"""
    return product in FIXED_EXCLUDED_PRODUCTS


def attach_product_filter(inputs):
    products = tuple(inputs["products"])
    invalid = {product for product in products
        if not isinstance(product, str) or not product or product != product.upper()}
    for contract in inputs.get("contracts", {}).values():
        product = getattr(contract, "product_code", None)
        if product not in products:
            invalid.add(product)
    excluded = tuple(sorted(product for product in products if product_excluded(product)))
    included = tuple(product for product in products if product not in set(excluded) and product not in invalid)
    inputs["exchange_filter_policy"] = FILTER_POLICY
    inputs["exchange_filter_excluded_products"] = excluded
    inputs["exchange_filter_included_products"] = included
    inputs["product_code_filter_policy"] = FILTER_POLICY
    inputs["product_code_filter_excluded_products"] = excluded
    inputs["product_code_invalid_products"] = tuple(sorted(product for product in invalid if product is not None))
    return inputs


def load_inputs(start_date, end_date, **kwargs):
    if kwargs.get("source_snapshots") is None:
        kwargs["notice_rows_hook"] = resolve_reviewed_rules
    inputs = load_previous_inputs(start_date, end_date, **kwargs)
    validate_frozen_resolution(inputs)
    return attach_product_filter(inputs)
