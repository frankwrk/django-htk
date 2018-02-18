HTK_SHOPIFY_SHOP_NAME = None
HTK_SHOPIFY_API_KEY = None
HTK_SHOPIFY_API_SECRET = None
HTK_SHOPIFY_SHARED_SECRET = None

HTK_SHOPIFY_MONGODB_COLLECTIONS = {
    'product' : 'product',
    'product_tag' : 'product_tag',
    'product_image' : 'product_image',
    'product_variant' : 'product_variant',
    'order' : 'order',
    'customer' : 'customer',
    'customer_address' : 'customer_address',
}

HTK_SHOPIFY_MONGODB_ITEM_PK = lambda item_type, item_json: item_json['id']
