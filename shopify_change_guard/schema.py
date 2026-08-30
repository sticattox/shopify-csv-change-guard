"""Shopify product CSV column contract used by Change Guard.

Column names follow the classic Shopify product export headings that
merchants actually download and re-import. Official docs also use some
newer aliases (URL handle, Product image URL). Both families are
recognized and normalized to the classic names.
"""

from __future__ import annotations

CLASSIC_COLUMNS = [
    "Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Type", "Tags",
    "Published", "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value",
    "Option3 Name", "Option3 Value", "Variant SKU", "Variant Grams",
    "Variant Inventory Tracker", "Variant Inventory Qty", "Variant Inventory Policy",
    "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price",
    "Variant Requires Shipping", "Variant Taxable", "Variant Barcode", "Image Src",
    "Image Position", "Image Alt Text", "Gift Card", "SEO Title", "SEO Description",
    "Variant Image", "Variant Weight Unit", "Cost per item", "Status",
]

ALIASES = {
    "url handle": "Handle", "handle": "Handle", "title": "Title",
    "description": "Body (HTML)", "body (html)": "Body (HTML)", "vendor": "Vendor",
    "product category": "Product Category", "type": "Type", "tags": "Tags",
    "published": "Published", "published on online store": "Published",
    "option1 name": "Option1 Name", "option1 value": "Option1 Value",
    "option2 name": "Option2 Name", "option2 value": "Option2 Value",
    "option3 name": "Option3 Name", "option3 value": "Option3 Value",
    "sku": "Variant SKU", "variant sku": "Variant SKU",
    "barcode": "Variant Barcode", "variant barcode": "Variant Barcode",
    "price": "Variant Price", "variant price": "Variant Price",
    "compare-at price": "Variant Compare At Price",
    "variant compare at price": "Variant Compare At Price",
    "cost per item": "Cost per item",
    "inventory tracker": "Variant Inventory Tracker",
    "variant inventory tracker": "Variant Inventory Tracker",
    "inventory quantity": "Variant Inventory Qty",
    "variant inventory qty": "Variant Inventory Qty",
    "continue selling when out of stock": "Variant Inventory Policy",
    "variant inventory policy": "Variant Inventory Policy",
    "weight value (grams)": "Variant Grams", "variant grams": "Variant Grams",
    "weight unit for display": "Variant Weight Unit",
    "variant weight unit": "Variant Weight Unit",
    "requires shipping": "Variant Requires Shipping",
    "variant requires shipping": "Variant Requires Shipping",
    "fulfillment service": "Variant Fulfillment Service",
    "variant fulfillment service": "Variant Fulfillment Service",
    "product image url": "Image Src", "image src": "Image Src",
    "image position": "Image Position", "image alt text": "Image Alt Text",
    "variant image url": "Variant Image", "variant image": "Variant Image",
    "status": "Status", "seo title": "SEO Title", "seo description": "SEO Description",
    "gift card": "Gift Card",
}

PRODUCT_LEVEL = {
    "Title", "Body (HTML)", "Vendor", "Product Category", "Type", "Tags",
    "Published", "Gift Card", "SEO Title", "SEO Description", "Status",
}
VARIANT_IDENTITY = {
    "Handle", "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value",
    "Option3 Name", "Option3 Value",
}
VARIANT_FIELDS = {
    "Variant SKU", "Variant Grams", "Variant Inventory Tracker", "Variant Inventory Qty",
    "Variant Inventory Policy", "Variant Fulfillment Service", "Variant Price",
    "Variant Compare At Price", "Variant Requires Shipping", "Variant Taxable",
    "Variant Barcode", "Variant Image", "Variant Weight Unit", "Cost per item",
}
IMAGE_FIELDS = {"Image Src", "Image Position", "Image Alt Text"}
DESTRUCTIVE_IF_BLANKED = {
    "Handle", "Title", "Option1 Name", "Option1 Value", "Variant SKU",
    "Variant Price", "Variant Barcode", "Image Src", "Status",
}
NUMERIC_FIELDS = {
    "Variant Price", "Variant Compare At Price", "Cost per item",
    "Variant Grams", "Variant Inventory Qty", "Image Position",
}
FORBIDDEN_IMAGE_SUFFIXES = ("_thumb", "_small", "_medium")


def normalize_header(name: str) -> str:
    raw = (name or "").strip().lstrip("\ufeff")
    key = raw.lower()
    return ALIASES.get(key, raw)
