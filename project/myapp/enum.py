from enum import Enum


class PriceChoice(Enum):
    HIGH = "high"
    MEDIUM = 'medium'
    LOW = "low"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]



class OrderStatus(Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]



class PaymentStatus(Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    REFUNDED = "refunded"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class PaymentMethod(Enum):
    CREDIT_CARD = "credit card"
    PAYPAL = "PayPal"
    VISA = "Visa"
    MASTERCARD = "MasterCard"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]