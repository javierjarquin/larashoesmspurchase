import model.morders
import model.morderproduct
import controller.corder as corder
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, status
from config.config import engine, session
from sqlalchemy.orm import Session

app = FastAPI()
model.morders.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = session()
        yield db
    finally:
        db.close()

db_dependency = Depends(get_db)

### Controlador
def createOrder(code: str, creationDate: str, status: str, totalOrder: float, guide: str, totalImport: float, arrivalDate: datetime, providerId: int, creationUserId: int, db: Session):
    order = model.morders.Purchase(code=code, creationDate=creationDate, status=status, totalOrder=totalOrder, guide=guide, totalImport=totalImport, arrivalDate=arrivalDate, providerId=providerId, creationUserId=creationUserId)
    db.add(order)
    db.commit()
    return {"status": "se ha creado correctamente la orden de compra"}

def orderProduct(productId: int, orderId: int, creationUserId: int, quantity: int, unit: str, unitCost: float, totalCost: float, guide: str, arrivalDate: datetime, isShippet: int, isReceive: int, quoteCharge: int, isPayment: int, db: Session):
    oProduct = model.morderproduct.OrderProduct(productId=productId, orderId=orderId, creationUserId=creationUserId, quantity=quantity, unit=unit, unitCost=unitCost, totalCost=totalCost, guide=guide, arrivalDate=arrivalDate, isShippet=isShippet, isReceive=isReceive, quoteCharge=quoteCharge, isPayment=isPayment)
    db.add(oProduct)
    db.commit()
    return {"status": "se ha agregado un producto a la orden de compra."}

def cancelOrder(orderId: int, db: Session):
    order = db.query(model.morders.Purchase).filter(model.morders.Purchase.id == orderId).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"No existe la orden: {orderId}")

    if order.status == "AT":
        raise HTTPException(status_code=451, detail= "No se posible cancelar una orden de compra autorizada")

    order.status = "XX"
    db.commit()
    return {"status": "Se ha cancelado correctamente la orden de compra"}

def okOrder(orderId: int, db: Session):
    order = db.query(model.morders.Purchase).filter(model.morders.Purchase.id == orderId).first()
    if not order.status == "PE":
        raise HTTPException(status_code=451, detail="Solo es posible validar la orden si tiene el estatus pendiente")

    order.status = "AT"
    db.commit()
    return {"status": "Orden de compra autorizada, pedido enviado.. espere y recepcione la mercancia en el modulo correspondiente"}

def getProductByOrder(orderId: int, db: Session):
    products = db.query(model.morderproduct.OrderProduct).filter(model.morderproduct.OrderProduct.orderId == orderId).all()
    return products

def getOrder(db: Session):
    orders = db.query(model.morders.Purchase).all()
    return orders

### Fin Controlador
### Rutas
@app.post("/createOrder/")
async def newOrder(code: str, totalOrder: float=0.00, guide: str=None, totalImport: float=0.00, arrivalDate: datetime=None, providerId: int=None, creationUserId: int=None, db: Session = db_dependency):
    return createOrder(code, datetime.now(), "PE", totalOrder, guide, totalImport, arrivalDate, providerId, creationUserId, db)

@app.post("/orderProduct/")
async def neworProduct(productId: int, orderId: int, creationUserId: int, quantity: int, unit: str, unitCost: float, totalCost: float, guide: str=None, arrivalDate: datetime=None, isShippet: int=0, isReceive: int=0, quoteCharge: int=0, isPayment: int=0, db: Session = db_dependency):
    return orderProduct(productId, orderId, creationUserId, quantity, unit, unitCost, totalCost, guide, arrivalDate, isShippet, isReceive, quoteCharge, isPayment, db)

@app.post("/cancelOrder/")
async def cancelOr(orderId: int, db: Session = db_dependency):
    return cancelOrder(orderId, db)

@app.post("/aprovedOrder/")
async def aprovedOrder(orderId: int, db: Session = db_dependency):
    return okOrder(orderId, db)

@app.get("/orderProList/{orderId}")
async def orList(orderId: int, db: Session = db_dependency):
    return getProductByOrder(orderId, db)

@app.get("/orders/")
async def orderList(db: Session = db_dependency):
    return getOrder(db)
### Fin Rutas

