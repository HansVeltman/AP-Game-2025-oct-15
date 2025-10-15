# ModelData_RectangelsLinesAndTriangles.py
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from protocol import LineType, Arrow, Rectangle, Triangle, Image

D_FontSize = 16
D_ArrowLength = 15


# ---------------------------------------------
# DIRECTE DATA (onderhoud hier je schema-items)
# ---------------------------------------------


RECTANGLES: List[Rectangle] = [
#	            name       text                     font        fonsize textcolor     x       y       w        h   L-Width     FillColor LineColor	LineType
    Rectangle("Background", " ",                    "Arial", D_FontSize, "#F0E9E9", 0.0,    0.0363, 0.8238, 0.9019, 0,    "#2C3A7A", "#F0E9E9", LineType.SOLID),
    Rectangle("Purchase", "Purchase",               "Arial", D_FontSize, "#F0E9E9", 0.0082, 0.0892, 0.1244, 0.0877, 3,    "#68A435", "#F0E9E9", LineType.SOLID),
    Rectangle("MakePlanning", "Make Planning",      "Arial", D_FontSize, "#F0E9E9", 0.3532, 0.0892, 0.1244, 0.0877, 3,    "#6193D5", "#F0E9E9", LineType.SOLID),
    Rectangle("MakeForecast", "Make forecast",      "Arial", D_FontSize, "#F0E9E9", 0.5457, 0.0892, 0.1244, 0.0877, 3,    "#EA7423", "#F0E9E9", LineType.SOLID),
    Rectangle("PromoteProds", "Promote products",   "Arial", D_FontSize, "#F0E9E9", 0.7186, 0.0892, 0.1244, 0.0877, 3,    "#EA7423", "#F0E9E9", LineType.SOLID),
    Rectangle("Distribute", "Distribute",           "Arial", D_FontSize, "#F0E9E9", 0.5457, 0.4481, 0.1244, 0.0877, 3,    "#6193D5", "#F0E9E9", LineType.SOLID),
    Rectangle("SellProducts", "Sell products",      "Arial", D_FontSize, "#F0E9E9", 0.5457, 0.2088, 0.1244, 0.0877, 3,    "#EA7423", "#F0E9E9", LineType.SOLID),
    Rectangle("Promise", "Promise sales orders",    "Arial", D_FontSize, "#F0E9E9", 0.5457, 0.3284, 0.1244, 0.0877, 3,    "#EA7423", "#F0E9E9", LineType.SOLID),
    Rectangle("ProduceWheels", "Produce wheels",    "Arial", D_FontSize, "#F0E9E9", 0.1607, 0.3284, 0.1244, 0.0877, 3,    "#6193D5", "#F0E9E9", LineType.SOLID),
    Rectangle("ProduceFrames", "Produce frames",    "Arial", D_FontSize, "#F0E9E9", 0.1607, 0.4481, 0.1244, 0.0877, 3,    "#6193D5", "#F0E9E9", LineType.SOLID),
    Rectangle("AssembleBike", "Assemble bicycles",  "Arial", D_FontSize, "#F0E9E9", 0.3532, 0.4481, 0.1244, 0.0877, 3,    "#6193D5", "#F0E9E9", LineType.SOLID),
    Rectangle("ManageMoney", "Manage money",        "Arial", D_FontSize, "#352D2D", 0.3532, 0.7047, 0.1244, 0.0877, 3,    "#EFD957", "#F0E9E9", LineType.SOLID),
    Rectangle("Market", " MARKET",                  "Arial", 30,         "#EA7423", 0.7186, 0.2500, 0.1244, 0.3300, 4,    "#DDC8A1", "#EA7423", LineType.SOLID),
    #Rectangle("TEST", "TESTTES",                    "Arial", 20, "#000000", 0.9,    0.9,    0.95,   0.95,   3,    "#E72B79", "#F0E9E9", LineType.SOLID),
]

TRIANGLES: List[Triangle] = [
#	            name       text                     font fonsize textcolor     x       y       w        h   L-Width FillColor   LineColor	   LineType
    Triangle("GRWheels",    " ",                   "Arial", 10, "#000000",  0.1052, 0.3284, 0.0416, 0.0877, 1,  "#7CAE3E", "#F0E9E9", LineType.SOLID),
    Triangle("GRFrames",    " ",                   "Arial", 10, "#000000",  0.1052, 0.4481, 0.0416, 0.0877, 1,  "#7CAE3E", "#F0E9E9", LineType.SOLID),
    Triangle("Wheels",    " ",                     "Arial", 10, "#000000",  0.297,  0.3284, 0.0416, 0.0877, 1,  "#7CAE3E", "#F0E9E9", LineType.SOLID),
    Triangle("Frames",    " ",                     "Arial", 10, "#000000",  0.297,  0.4481, 0.0416, 0.0877, 1,  "#7CAE3E", "#F0E9E9", LineType.SOLID),
    Triangle("FinProd",    " ",                    "Arial", 10, "#000000",  0.4895, 0.4481, 0.0416, 0.0877, 1,  "#7CAE3E", "#F0E9E9", LineType.SOLID),
    Triangle("Components",    " ",                 "Arial", 10, "#000000",  0.1052, 0.5678, 0.0416, 0.0877, 1,  "#7CAE3E", "#F0E9E9", LineType.SOLID),
]

LINES: List[Arrow] = [
#	         name       text                     font fonsize textcolor     x1       y1       x2     y2   L-Width  LineColor	   LineType       Aroowlength

    Arrow("PlanToPurch", " ",                   "Arial", 10, "#000000",  0.3532, 0.1330, 0.1325, 0.1330,   2,     "#F0E9E9", LineType.SOLID, arrow=D_ArrowLength), 
    Arrow("ForecstToPlan", " ",                 "Arial", 10, "#000000",  0.5457, 0.1330, 0.4776, 0.1330,   2,     "#F0E9E9", LineType.SOLID, arrow=D_ArrowLength), 
    Arrow("PlanToProdWheels", " ",              "Arial", 10, "#000000",  0.3843, 0.1769, 0.2540, 0.3284,   2,     "#F0E9E9", LineType.SOLID, arrow=D_ArrowLength), 
    Arrow("PlanToAssemble", " ",                "Arial", 10, "#000000",  0.4154, 0.1769, 0.4154, 0.4481,   2,     "#F0E9E9", LineType.SOLID, arrow=D_ArrowLength), 
    Arrow("PromiseToPlanning", " ",             "Arial", 10, "#000000",  0.5457, 0.3503, 0.4465, 0.1769,   2,     "#F0E9E9", LineType.SOLID, arrow=D_ArrowLength), 
    Arrow("PurchaseToVendor", " ",              "Arial", 10, "#000000",  0.0651, 0.1769, 0.0651, 0.3284,   2,     "#F0E9E9", LineType.SOLID, arrow=D_ArrowLength), 
    Arrow("PromoteToMarket", " ",               "Arial", 10, "#000000",  0.7808, 0.1769, 0.7808, 0.2500,   2,     "#F0E9E9", LineType.SOLID, arrow=D_ArrowLength), 
    Arrow("CustomerToPromise", " ",             "Arial", 10, "#000000",  0.7790, 0.4866, 0.6701, 0.3941,   2,     "#F0E9E9", LineType.SOLID, arrow=D_ArrowLength), 
    Arrow("MarketToMakeForecast", " ",          "Arial", 10, "#000000",  0.7400, 0.2500, 0.6701, 0.1550,   2,     "#F0E9E9", LineType.SOLID, arrow=D_ArrowLength), 
    Arrow("SellToCustomer", " ",                "Arial", 10, "#000000",  0.6701, 0.2746, 0.7600, 0.4381,   2,     "#F0E9E9", LineType.SOLID, arrow=D_ArrowLength), 
    
    #Cashflows
    Arrow("CustomerToCash1", " ",               "Arial", 10, "#000000",  0.7800, 0.5450, 0.7800, 0.7486,   4,     "#EFD957", LineType.SOLID, arrow=0),
    Arrow("CustomerToCash2", " ",               "Arial", 10, "#000000",  0.7800, 0.7486, 0.4778, 0.7486,   4,     "#EFD957", LineType.SOLID, arrow=15),
    Arrow("CashToVendor1", " ",                 "Arial", 10, "#000000",  0.3532, 0.7486, 0.0647, 0.7486,   4,     "#EFD957", LineType.SOLID, arrow=0),
    Arrow("CashToVendor2", " ",                 "Arial", 10, "#000000",  0.0651, 0.7486, 0.0651, 0.6554,   4,     "#EFD957", LineType.SOLID, arrow=15),
    Arrow("CashToOther1", " ",                  "Arial", 10, "#000000",  0.3532, 0.7705, 0.3200, 0.7705,   4,     "#EFD957", LineType.SOLID, arrow=0),
    Arrow("CashToOther2", " ",                  "Arial", 10, "#000000",  0.3209, 0.7705, 0.3209, 0.8760,   4,     "#EFD957", LineType.SOLID, arrow=15),
    


    # materialflows from Vendors: double lines
    Arrow("VendorToWheels", " ",                "Arial", 10, "#000000",  0.0897, 0.3723, 0.1146, 0.3723,   7,     "#F0E9E9", LineType.SOLID, arrow=13.0),
    Arrow("VendorToWheels_", " ",               "Arial", 10, "#000000",  0.0897, 0.3723, 0.1146, 0.3723,   3,     "#2C3A7A", LineType.SOLID, arrow=11),
    Arrow("VendorToFrames", " ",                "Arial", 10, "#000000",  0.0897, 0.4920, 0.1146, 0.4920,   7,     "#F0E9E9", LineType.SOLID, arrow=13.0),
    Arrow("VendorToFrames_", " ",               "Arial", 10, "#000000",  0.0897, 0.4920, 0.1146, 0.4920,   3,     "#2C3A7A", LineType.SOLID, arrow=11),
    Arrow("VendorToComponents", " ",            "Arial", 10, "#000000",  0.0897, 0.6116, 0.1146, 0.6116,   7,     "#F0E9E9", LineType.SOLID, arrow=13.0),
    Arrow("VendorToComponents_", " ",           "Arial", 10, "#000000",  0.0897, 0.6116, 0.1146, 0.6116,   3,     "#2C3A7A", LineType.SOLID, arrow=11),
  
    Arrow("CompsToAssemble1", "Components",     "Arial", D_FontSize, "#F0E9E9",  0.1358, 0.6116, 0.3280, 0.6116,   7,     "#F0E9E9", LineType.SOLID, arrow=0),
    Arrow("CompsToAssemble1_", " ",             "Arial", 10, "#000000",  0.1358, 0.6116, 0.3280, 0.6116,   3,     "#2C3A7A", LineType.SOLID, arrow=0),
    Arrow("CompsToAssemble2", " ",              "Arial", 10, "#000000",  0.3280, 0.6116, 0.3688, 0.5358,   7,     "#F0E9E9", LineType.SOLID, arrow=13),
    Arrow("CompsToAssemble2_", " ",             "Arial", 10, "#000000",  0.3280, 0.6116, 0.3688, 0.5358,   3,     "#2C3A7A", LineType.SOLID, arrow=11),
  
    Arrow("CompsToProdWheels", " ",             "Arial", 10, "#000000",  0.1358, 0.3723, 0.1607, 0.3723,   7,     "#F0E9E9", LineType.SOLID, arrow=13.0),
    Arrow("CompsToProdWheels_", " ",            "Arial", 10, "#000000",  0.1358, 0.3723, 0.1605, 0.3723,   3,     "#2C3A7A", LineType.SOLID, arrow=11),
    Arrow("ProdWheelsToWheels", " ",            "Arial", 10, "#000000",  0.2851, 0.3723, 0.3094, 0.3723,   7,     "#F0E9E9", LineType.SOLID, arrow=13.0),
    Arrow("ProdWheelsToWheels_", " ",           "Arial", 10, "#000000",  0.2851, 0.3723, 0.3092, 0.3723,   3,     "#2C3A7A", LineType.SOLID, arrow=11),
    
    Arrow("WheelsToAssemble", " ",              "Arial", 10, "#000000",  0.3280, 0.3723, 0.3688, 0.4450,   7,     "#F0E9E9", LineType.SOLID, arrow=13.0),
    Arrow("WheelsToAssemble_", " ",             "Arial", 10, "#000000",  0.3280, 0.3723, 0.3688, 0.4450,   3,     "#2C3A7A", LineType.SOLID, arrow=11),
    
    Arrow("CompsToProdFrames", " ",             "Arial", 10, "#000000",  0.1358, 0.4920, 0.1607, 0.4920,   7,     "#F0E9E9", LineType.SOLID, arrow=13.0),
    Arrow("CompsToProdFrames_", " ",            "Arial", 10, "#000000",  0.1358, 0.4920, 0.1605, 0.4920,   3,     "#2C3A7A", LineType.SOLID, arrow=11),
    Arrow("ProdFramesToFrames", " ",            "Arial", 10, "#000000",  0.2851, 0.4920, 0.3094, 0.4920,   7,     "#F0E9E9", LineType.SOLID, arrow=13.0),
    Arrow("ProdFramesToFrames_", " ",           "Arial", 10, "#000000",  0.2851, 0.4920, 0.3092, 0.4920,   3,     "#2C3A7A", LineType.SOLID, arrow=11),

    Arrow("CompsToProdFrames", " ",             "Arial", 10, "#000000",  0.3283, 0.4920, 0.3532, 0.4920,   7,     "#F0E9E9", LineType.SOLID, arrow=13.0),
    Arrow("CompsToProdFrames_", " ",            "Arial", 10, "#000000",  0.3283, 0.4920, 0.3530, 0.4920,   3,     "#2C3A7A", LineType.SOLID, arrow=11),
    Arrow("ProdFramesToFrames", " ",            "Arial", 10, "#000000",  0.4776, 0.4920, 0.5019, 0.4920,   7,     "#F0E9E9", LineType.SOLID, arrow=13.0),
    Arrow("ProdFramesToFrames_", " ",           "Arial", 10, "#000000",  0.4776, 0.4920, 0.5017, 0.4920,   3,     "#2C3A7A", LineType.SOLID, arrow=11),
    
    Arrow("FinProdToDistribute", " ",           "Arial", 10, "#000000",  0.5208, 0.4920, 0.5457, 0.4920,   7,     "#F0E9E9", LineType.SOLID, arrow=13.0),
    Arrow("FinProdToDistribute_", " ",          "Arial", 10, "#000000",  0.5208, 0.4920, 0.5455, 0.4920,   3,     "#2C3A7A", LineType.SOLID, arrow=11),
    Arrow("DistributeToCustomer", " ",          "Arial", 10, "#000000",  0.6701, 0.4920, 0.7458, 0.4920,   7,     "#F0E9E9", LineType.SOLID, arrow=13.0),
    Arrow("DistributeToCustomer_", " ",         "Arial", 10, "#000000",  0.6701, 0.4920, 0.7456, 0.4920,   3,     "#2C3A7A", LineType.SOLID, arrow=11),
]


IMAGES: List[Image] = [
#	         name       text       font fonsize textcolor     x       y       w        h       filename
    Image("VendorWheels", " ",      "Arial", 10, "#000000", 0.0404, 0.3284, 0.0493, 0.09, "Vendor.png"),	
    Image("VendorFrames", " ",      "Arial", 10, "#000000", 0.0404, 0.4481, 0.0493, 0.09, "Vendor.png"),
    Image("VendorComponents", " ",  "Arial", 10, "#000000", 0.0404, 0.5677, 0.0493, 0.09, "Vendor.png"), 
    Image("Customer", " ",          "Arial", 10, "#000000", 0.7461, 0.4280, 0.0657, 0.12, "Customer.png"),
    Image("Counter", " ",           "Arial", 10, "#000000", 0.3900, 0.7300, 0.0734, 0.09, "Counter.png"),
]