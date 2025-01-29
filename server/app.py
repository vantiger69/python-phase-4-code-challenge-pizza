#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


    ##API resources 
# API Resources
class RestaurantResource(Resource):
    def get(self):
        restaurants_data = [restaurant.to_dict() for restaurant in Restaurant.query.all()]

        response = make_response(jsonify(restaurants_data),200)

        response.headers["content-Type"] = "application/json"
        return response
    
class PizzaResource(Resource):
    def get(self):
        pizzas_data = [pizza.to_dict() for pizza in Pizza.query.all()]

        response = make_response(jsonify(pizzas_data),200)

        response.headers["content-Type"] = "application/json"

        return response
    
class RestaurantDetailsResource(Resource):
    def get(self, restaurant_id):

        ###checks if restaurant exist
        restaurant = Restaurant.query.get(restaurant_id)

        if not restaurant:
            return {"error":"Restaurant not found"},404
        
        ## if exist fetch the asociated restaurant_pizzas data
        pizza_map = {Pizza.id:pizza for pizza in Pizza.query.all()}
        restaurant_pizzas_data = [
    {
        "id": restaurant_pizza.id,
        "pizza": {
            "id": pizza_map.get(restaurant_pizza.pizza_id).id,
            "ingredients": pizza_map.get(restaurant_pizza.pizza_id).ingredients,
            "name": pizza_map.get(restaurant_pizza.pizza_id).name
        },
        "pizza_id": restaurant_pizza.pizza_id,
        "price": restaurant_pizza.price,
        "restaurant_id": restaurant_pizza.restaurant_id
    }
    for restaurant_pizza in restaurant.restaurant_pizzas
    if pizza_map.get(restaurant_pizza.pizza_id)
]

        ##prepare the response with the restaurant details and associated pizzas

        response_data = {
            "address":restaurant.address,
            "id":restaurant.id,
            "name":restaurant.name,
            "restaurant_pizzas":restaurant_pizzas_data
        }
        return make_response(jsonify(response_data),200)
    
      
    def delete(self,restaurant_id):
        restaurant = Restaurant.query.get(restaurant_id)

        if not restaurant:
            return {"error":"Restaurant not found"},404
        
        
        associated_pizzas = RestaurantPizza.query.filter_by(restaurant_id=restaurant.id).all()
        for pizza in associated_pizzas:
             db.session.delete(pizza)
        
        db.session.delete(restaurant)
        db.session.commit()

        return ('',204)
      
class RestaurantPizzaResource(Resource):
            def post(self):
                 data = request.get_json()
                 ###Validate existence of restaurant and pizza
                 restaurant = Restaurant.query.get(data.get("restaurant_id"))
                 pizza = Pizza.query.get(data.get("pizza_id"))
                 if not restaurant or not pizza:
                      return {"error":["Validation error: Restaurant or Pizza not found"]},400
                 try:
                      ###create the Restaurant instance
                      new_restaurant_pizza = RestaurantPizza(
                           restaurant_id = data["restaurant_id"],
                           pizza_id=data["pizza_id"],
                           price=data["price"]
                      )
                      db.session.add(new_restaurant_pizza)
                      db.session.commit()

                      return new_restaurant_pizza.to_dict(),201
                 except ValueError as e:
                      return {"error": f"Failed to create reatsurant pizza: {str(e)}"},400
                      
    

    
            
    
    
##Register API Resource with a URL
api.add_resource(RestaurantPizzaResource, "/restaurant_pizzas")
api.add_resource(PizzaResource, "/pizzas")
api.add_resource(RestaurantDetailsResource,"/restaurants/<int:restaurant_id>")
api.add_resource(RestaurantResource, "/restaurants")
if __name__ == "__main__":
    app.run(port=5555, debug=True)
