from .cart import Cart

def cart(request):
    """
    Returns the cart object to all templates.
    This allows us to use {{ cart }} in base.html
    """
    return {'cart': Cart(request)}

