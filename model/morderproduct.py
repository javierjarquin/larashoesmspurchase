from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Double
from config.config import Base

class OrderProduct(Base):
    __tablename__ = 'orderproduct'

    id              = Column(Integer, primary_key=True, index=True)
    productId      = Column(Integer, nullable=False)
    orderId         = Column(Integer, ForeignKey('orders.id'), nullable=False)
    creationUserId  = Column(Integer, default=1)
    quantity        = Column(Double, default=0)
    unit            = Column(String(2), nullable=False)
    unitCost        = Column(Double, default=0)
    totalCost       = Column(Double, default=0)
    guide           = Column(String(20), nullable=True)
    arrivalDate     = Column(DateTime, nullable=True)
    isShippet       = Column(Integer, default=0)
    isReceive       = Column(Integer, default=0)
    quoteCharge     = Column(Integer, default=0)
    isPayment       = Column(Integer, default=0)
    unitCostPlus    = Column(Double, default=0)
    unitCostSalePercent = Column(Double, default=0)
    unitTotalSale   = Column(Double, default=0)

    def __init__(self, productId=None, orderId=None, creationUserId=None, quantity=None, unit=None, unitCost=None, totalCost=None, guide=None, arrivalDate=None, isShippet=None, isReceive=None, quoteCharge=None, isPayment=None, unitCostPlus=None, unitCostSalePercent=None, unitTotalSale=None):
        self.productId     = productId
        self.orderId        = orderId
        self.creationUserId = creationUserId
        self.quantity       = quantity
        self.unit           = unit
        self.unitCost       = unitCost
        self.totalCost      = totalCost
        self.guide          = guide
        self.arrivalDate    = arrivalDate
        self.isShippet      = isShippet
        self.isReceive      = isReceive
        self.quoteCharge    = quoteCharge
        self.isPayment      = isPayment
        self.unitCostPlus   = unitCostPlus
        self.unitCostSalePercent = unitCostSalePercent
        self.unitTotalSale  = unitTotalSale