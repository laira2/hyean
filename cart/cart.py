from decimal import Decimal
from django.conf import settings

class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # 세션에 빈 카트 저장
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, artCd, price, image_url,art_name):
        """
        Add a product to the cart.
        """
        if artCd not in self.cart:
            self.cart[artCd] = {'artCd':str(artCd), 'art_name':str(art_name),'quantity':1,'price': str(price),'image_url':str(image_url)}
        self.save()

    def save(self):
        # 세션을 "modified"으로 표시하여 저장되도록 함
        self.session.modified = True

    def remove(self, artCd):
        """
        Remove a product from the cart.
        """
        if artCd in self.cart:
            del self.cart[artCd]
        self.save()

    def __len__(self):
        """
        Count all items in the cart.
        """
        return len(self.cart)

    def get_total_price(self):
        return sum(Decimal(item['price']) for item in self.cart.values())

    def clear(self):
        # 카트 세션 삭제
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def __iter__(self):
        """
        Iterate over items in the cart and yield each item's data.
        """
        for item in self.cart.values():
            item['price'] = Decimal(item['price'])  # 가격을 Decimal로 변환
            yield item
