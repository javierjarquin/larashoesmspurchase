import model.morders
import model.morderproduct
import controller.corder as corder
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, status
from config.config import engine, session
from sqlalchemy.orm import Session
import uvicorn
import os
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
def getOrderPById(orderId: int, db: Session):
    order =  db.query(model.morders.Purchase).filter(model.morders.Purchase.id == orderId).first()
    if not order:
        raise HTTPException(status_code=404, detail="órden de compra no encontrada")
    return order
def createOrder(code: str, creationDate: str, status: str, totalOrder: float, guide: str, totalImport: float, arrivalDate: datetime, providerId: int, creationUserId: int, db: Session):
    order = model.morders.Purchase(code=code, creationDate=creationDate, status=status, totalOrder=totalOrder, guide=guide, totalImport=totalImport, arrivalDate=arrivalDate, providerId=providerId, creationUserId=creationUserId)
    db.add(order)
    db.commit()
    return {"status": "se ha creado correctamente la orden de compra"}

def orderProduct(productId: int, orderId: int, quantity: int, unit: str, unitCost: float, db: Session):
    order = db.query(model.morders.Purchase).filter(model.morders.Purchase.id == orderId).first()
    print(f"order{order}")
    print(f"orderstatus {order.status}")
    if order.status != "PE":
        raise HTTPException(status_code=401, detail="No es posible agregar productos a una orden que no tienes estatus pendiente")

    order.totalOrder += (quantity * unitCost)

    oProduct = model.morderproduct.OrderProduct(productId=productId, orderId=orderId, quantity=quantity, unit=unit, unitCost=unitCost, totalCost=(quantity * unitCost), isShippet=0, isReceive=0, quoteCharge=0, isPayment=0, unitCostPlus=0, unitCostSalePercent=0, unitTotalSale=0)
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
def paymentOrder(orderId: int, db: Session):
    order = db.query(model.morders.Purchase).filter(model.morders.Purchase.id == orderId).first()
    if not order.status == "AT":
        raise HTTPException(status_code=451, detail="Solo se puede pagar la orden si está autorizada")
    order.status = "PA"
    order.isPayment = 1
    db.commit()
    return {"status": "Se ha pagado correctamente la orden de compra, favor de marcarlo como enviado"}

def getProductByOrder(orderId: int, db: Session):
    products = db.query(model.morderproduct.OrderProduct).filter(model.morderproduct.OrderProduct.orderId == orderId).all()
    return products

def getOrder(code: str, startDate: datetime, endDate: datetime, status: str, providerId: int, db: Session):
    orders = db.query(model.morders.Purchase)
    if code:
        orders = orders.filter(model.morders.Purchase.code.like(f"{code}"))
    if startDate and endDate:
        orders = orders.filter(model.morders.Purchase.creationDate.between(startDate, endDate))
    if status:
        orders = orders.filter(model.morders.Purchase.status == status)
    if providerId:
        orders = orders.filter(model.morders.Purchase.providerId == providerId)


    return orders.all()

def guideOrder(orderId: int, guide: str, totalImport: float, db: Session):
    order = db.query(model.morders.Purchase).filter(model.morders.Purchase.id == orderId).first()
    if not order.status == "PA":
        raise HTTPException(status_code=402, detail="No es posible marcar como enviado la orden si no se ha pagado")
    ## Actualiza la orden de compra
    order.status = "EN"
    order.arrivalDate = datetime.now()
    order.guide = guide
    order.totalImport = totalImport

    ### Se valida la cantidad de productos para asignar el costo de envio por modelo ###
    ### unitCostPlus es la division del total del envio entre la cantidad de modelos de la orden
    ### Nota: Al recibir las corridas se dividira por el total en otra función ###
    ### isShippet de enviado
    ### guide la guia del producto
    ### arrivalDate la fecha actual de cada producto
    products = db.query(model.morderproduct.OrderProduct).filter(model.morderproduct.OrderProduct.orderId == orderId).all()

    productcostplus = int(totalImport) / int(len(products))
    for product in products:
        product.guide = guide
        product.arrivalDate = datetime.now()
        product.isShippet = 1
        product.unitCostPlus = productcostplus

    db.commit()

def deleteP(orderProductId: int, db: Session):
    orderProduct = db.query(model.morderproduct.OrderProduct).filter(model.morderproduct.OrderProduct.id == orderProductId).first()
    order = db.query(model.morders.Purchase).filter(model.morders.Purchase.id == orderProduct.orderId).first()
    if order.status != "PE":
        raise HTTPException(status_code=401, detail="No es posible eliminar un producto si la orden de compra no está validada")

    if not orderProduct:
        raise HTTPException(status_code=401, detail="No existe el producto que quiere eliminar, contacte a sistemas")

    db.delete(orderProduct)
    db.commit()
    return {"status": "Se ha eliminado correctamente el producto de la orden de compra"}


### Fin Controlador
### Rutas
@app.post("/createOrder/")
async def newOrder(code: str, arrivalDate: datetime=datetime.now(), totalOrder: float=0.00, guide: str=None, totalImport: float=0.00, providerId: int=None, creationUserId: int=1, db: Session = db_dependency):
    return createOrder(code, datetime.now(), "PE", totalOrder, guide, totalImport, arrivalDate, providerId, creationUserId, db)

@app.post("/orderProduct/")
async def neworProduct(productId: int, orderId: int, quantity: int, unit: str, unitCost: float, db: Session = db_dependency):
    return orderProduct(productId, orderId, quantity, unit, unitCost, db)

@app.post("/cancelOrder/")
async def cancelOr(orderId: int, db: Session = db_dependency):
    return cancelOrder(orderId, db)

@app.post("/aprovedOrder/")
async def aprovedOrder(orderId: int, db: Session = db_dependency):
    return okOrder(orderId, db)

@app.post("/payOrder/")
async  def payOrder(orderId: int, db: Session = db_dependency):
    return paymentOrder(orderId, db)

@app.get("/orderProList/{orderId}")
async def orList(orderId: int, db: Session = db_dependency):
    return getProductByOrder(orderId, db)

@app.get("/orders/")
async def orderList(code: str=None, startDate: datetime=None, endDate: datetime=None, status: str=None, providerId: int=None,  db: Session = db_dependency):
    return getOrder(code, startDate, endDate, status, providerId, db)

@app.get("/orderById/{orderId}")
async def getOrderById(orderId: int, db: Session = db_dependency):
    return getOrderPById(orderId, db)

@app.post("/sendOrder/")
async def sendOrder(orderId: int, guide: str, totalImport, db: Session = db_dependency):
    return guideOrder(orderId, guide, totalImport, db)

@app.delete("/deleteProduct/{id}")
async def deleteProduct(id: int, db: Session = db_dependency):
    return deleteP(id, db)
### Fin Rutas

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))

    uvicorn.run(app, host="0.0.0.0", port=port)
    input("Presiona Enter para salir...")