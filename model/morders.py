from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Double
from config.config import Base

class Purchase(Base):
    __tablename__ = 'orders'

    id               = Column(Integer, primary_key=True, index=True)
    code             = Column(String(150), nullable=False)
    creationDate     = Column(DateTime, nullable=False)
    status           = Column(String(2), nullable=False)
    totalOrder       = Column(Double, default=0)
    guide            = Column(String(20), nullable=True)
    totalImport      = Column(Double, default=0)
    arrivalDate      = Column(DateTime, nullable=False)
    providerId       = Column(Integer, nullable=False)
    creationUserId   = Column(Integer, nullable=False)

    def __init__(self, code="", creationDate=None, status=None, totalOrder=None, guide=None, totalImport=None, arrivalDate=None, providerId=None, creationUserId=None):
        self.code            = code
        self.creationDate    = creationDate
        self.status          = status
        self.totalOrder      = totalOrder
        self.guide           = guide
        self.totalImport     = totalImport
        self.arrivalDate     = arrivalDate
        self.providerId      = providerId
        self.creationUserId  = creationUserId