import json
import os
import bcrypt

class User:
    def __init__(self, username, password, role="user"):
        self.username = username
        self.password = password if password.startswith("$2b$") else self.hash_password(password)
        self.role = role

    def hash_password(self, password):
        '''Hash password using bcrypt'''
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def check_password(self, password):
        '''Verify entered password with stored hashed password'''
        return bcrypt.checkpw(password.encode(), self.password.encode())

class UserSystem:
    def __init__(self, filename="user.txt"):
        self.filename = filename
        self.users = self.load_users()
        self.logged_in_user = None

    def load_users(self):
        """Loads users from file."""
        try:
            with open(self.filename, "r") as file:
                data = json.load(file)
                return [User(**user) for user in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_users(self):
        '''Save users to file'''
        with open(self.filename, "w") as file:
            json.dump([user.__dict__ for user in self.users], file, indent=4)

    def register_user(self):
        """Register a new user."""
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()

        for user in self.users:
            if user.username == username:
                print(f"Username '{username}' already exists!")
                return

        # First user becomes admin
        if not self.users:
            role = "admin"
            print("First user registered as ADMIN.")
        else:
            while True:
                role = input("Register as 'user' or 'admin': ").strip().lower()
                if role in ["user", "admin"]:
                    break
                print("Invalid role! Please enter 'user' or 'admin'.")

        new_user = User(username, password, role)
        self.users.append(new_user)
        self.save_users()
        print(f"User '{username}' registered successfully as {role}.")

    def login(self):
        '''Login for the system'''
        username = input("Enter your username: ").strip()
        password = input("Enter your password: ").strip()
        
        for user in self.users:
            if user.username == username and user.check_password(password):
                self.logged_in_user = user
                print(f"Login successful! You are logged in as {user.role}.")
                return user
        
        print("Invalid username or password.")
        return None

    def logout(self):
        '''Logs out the current user'''
        if self.logged_in_user:
            print(f"Goodbye, {self.logged_in_user.username}")
            self.logged_in_user = None
        else:
            print("No user is logged in.")

class Product:
    def __init__(self, name, product_id, price,discount = 0):
        self.name = name
        self.product_id = product_id
        self.price = price
        self.discount = discount
    def apply_discount(self, quantity=1):
    # Ensure discount is valid (0 <= discount <= 100)
     if not (0 <= self.discount <= 100):
        raise ValueError("Discount must be between 0 and 100.")
    
    # Calculate discounted price
     discounted_price = self.price * (1 - self.discount / 100)
    
    # Round to 2 decimal places for currency
     return round(discounted_price * quantity, 2)
class Inventory:
    def __init__(self, filename="inventory.txt"):
        self.filename = filename
        self.stock = self.load_inventory()

    def load_inventory(self):
        '''Load inventory from a file'''
        if not os.path.exists(self.filename):
            return {}
        with open(self.filename, "r") as file:
            try:
                data = json.load(file)
                fixed_data = {}
                for pid, info in data.items():
                    product_data = info["product"]
                    product = Product(
                        name=product_data["name"],
                         product_id=int(product_data["product_id"]),
                         price=float(product_data["price"])
                         )
                    fixed_data[int(pid)] = {"product": product, "quantity": info["quantity"]}
                return fixed_data
            except json.JSONDecodeError:
                print("Error: Inventory file is corrupted.")
                return {}

    def save_inventory(self):
        '''Save inventory to file'''
        with open(self.filename, "w") as file:
            json.dump({pid: {"product": vars(info["product"]), "quantity": info["quantity"]} for pid, info in self.stock.items()}, file, indent=4)

    def add_stock(self, product, quantity, user):
        '''Only admin can add stock'''
        if user.role == "admin":
            if product.product_id in self.stock:
                self.stock[product.product_id]["quantity"] += quantity
                self.stock[product.product_id]["product"].discount = product.discount
            else:
                self.stock[product.product_id] = {"product": product, "quantity": quantity}
            self.save_inventory()
            print(f"Added {quantity} of {product.name} to inventory with a discount of {product.discount}%.")
        else:
            print("Only admin can add stock.")

    def show_stock(self):
        '''Show current inventory'''
        print("\nCurrent Inventory:")
        for product_id, data in self.stock.items():
            product = data["product"]
            quantity = data["quantity"]
            discounted_price = product.apply_discount(1)
            print(f"Product ID: {product_id}, Name: {product.name}, Price: {product.price}, Discount: {product.discount}%, Final Price: {discounted_price}, Quantity: {quantity}")
class Cart:
    def __init__(self):
        self.items = []

    def add_product(self, product, quantity):
        self.items.append((product, quantity))

    def checkout(self, inventory):
        if not self.items:
            print("Cart is empty.")
            return

        total_price = sum(product.price * quantity for product, quantity in self.items)
        print(f"Total bill: {total_price:.2f}")
        print("Payment successful!")

        for product, quantity in self.items:
            inventory.stock[product.product_id]["quantity"] -= quantity
        inventory.save_inventory()
        self.items.clear()
        print("ORDER PLACED SUCCESSFULLY.")

# Create system
user_system = UserSystem()
inventory = Inventory()
cart = Cart()

while True:
    print("\nMain Menu:")
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    choice = input("Choose an action: ").strip()

    if choice == "1":
        user_system.register_user()
    elif choice == "2":
        user = user_system.login()
        if user:
            if user.role == "admin":
                while True:
                    print("\nAdmin Menu:")
                    print("1. Add Stock")
                    print("2. View Inventory")
                    print("3. Logout")
                    choice = input("Choose an action: ").strip()

                    if choice == "1":
                        product_name = input("Enter product name: ").strip()
                        product_id = int(input("Enter product ID: ").strip())
                        price = float(input("Enter product price: ").strip())
                        discount = float(input("Enter product discount (0 if none): ").strip())
                        quantity = int(input("Enter quantity to add: ").strip())
                        product = Product(product_name, product_id, price,discount)
                        inventory.add_stock(product, quantity, user)
                    elif choice == "2":
                        inventory.show_stock()
                    elif choice == "3":
                        user_system.logout()
                        break
                    else:
                        print("Invalid choice.")

            elif user.role == "user":
                while True:
                    print("\nUser Menu:")
                    print("1. View Inventory")
                    print("2. Add to Cart")
                    print("3. Checkout")
                    print("4. Logout")
                    choice = input("Choose an action: ").strip()

                    if choice == "1":
                        inventory.show_stock()
                    elif choice == "2":
                        product_id = int(input("Enter product ID to add to cart: ").strip())
                        quantity = int(input("Enter quantity: ").strip())
                        if product_id in inventory.stock:
                            product = inventory.stock[product_id]["product"]
                            cart.add_product(product, quantity)
                            print(f"Added {quantity} of {product.name} to cart.")
                        else:
                            print("Product not available.")
                    elif choice == "3":
                        cart.checkout(inventory)
                    elif choice == "4":
                        user_system.logout()
                        break
                    else:
                        print("Invalid choice.")
    elif choice == "3":
        print("Exiting system.")
        break
    else:
        print("Invalid choice. Please try again.")
