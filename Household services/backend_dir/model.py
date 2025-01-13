from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class clsUsers(db.Model):
    __tablename__ = 'tblUsers'
    user_id_col = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name_col = db.Column(db.String, nullable=False)
    email_col = db.Column(db.String, unique=True, nullable=False)
    password_col = db.Column(db.String, nullable=False)
    user_type_col = db.Column(db.String, nullable=False)  # e.g., 'admin', 'customer', 'service_professional'
    date_registered_col = db.Column(db.String)
    #approval_status_col = db.Column(db.String, default='pending') #only specific to service professional so moving to that table
    block_status_col = db.Column(db.String(50), nullable=False, default='unblocked/active')
    #service_complaints_count_col = db.Column(db.Integer, default=0)  #only specific to service professional so moving to that table
    #wage_theft_count_col = db.Column(db.Integer, default=0)  #only specific to customers so moving to that table
    #review_score_col = db.Column(db.Float, default=5.0)  # Review score from 1 to 5 #only specific to service professional so moving to that table

    # One-to-One relationship with clsCustomers and clsServiceProfessionals
    customer_table = db.relationship(
                                        "clsCustomers", 
                                        cascade="all", #If a  record of clsUsers is deleted, the associated  record in clsCustomers will also be deleted automatically,
                                        #that if a clsUsers entry is deleted, the related clsCustomers entry should also be deleted automatically.
                                        back_populates="users_table",   # if you have a clsCustomers object, you can access the associated clsUsers object using customer.users_table).
                                        uselist=False, #one-to-one relationship a record in clsUsers can have only 1 record in clsCustomers
                                        lazy=True
                                    )
    
    service_professional_table = db.relationship(
                                                    "clsServiceProfessionals", 
                                                    cascade="all", 
                                                    back_populates="users_table",   # Enables access to the associated clsUsers record as service_professional.user
                                                    uselist=False, 
                                                    lazy=True
                                                )

    
    # Relationship with block history (one-to-many)
    block_history_table = db.relationship('clsBlockHistory', backref='users_table', lazy=True)


class clsCustomers(db.Model):
    __tablename__ = 'tblCustomers'
    customer_id_col = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id_col = db.Column(db.Integer, db.ForeignKey('tblUsers.user_id_col'), unique=True)
    phone_col = db.Column(db.String, nullable=False)  # Phone stored as a string to include country codes or leading zeros
    location_col = db.Column(db.String(150))
    pin_col = db.Column(db.Integer)
    wage_theft_count_col = db.Column(db.Integer, default=0)

    # Relationship back to clsUsers
    users_table = db.relationship(
                                    "clsUsers", 
                                    back_populates="customer_table", 
                                    lazy=True,
                                    cascade="save-update",
                                    uselist=False
                                )
    
    
    cart_table = db.relationship(
                                    "clsCart", 
                                    back_populates="customers_table",  # back_populates used here to link to cart_items_table in clsCart
                                    lazy=True,
                                    cascade="save-update"
                                )
    
    service_requests_table = db.relationship(
                                        "clsServiceRequests", 
                                        back_populates="customers_table", 
                                        uselist=False,
                                        cascade="save-update",
                                        lazy=True
                                    )
    review_rating_table = db.relationship(
        'clsReviewRating',
        back_populates='customer_table',
        lazy=True,
        uselist=True  # Allow multiple reviews from the same customer
    )

    


class clsServiceProfessionals(db.Model):
    __tablename__ = 'tblServiceProfessionals'
    serviceProfessional_id_col = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id_col = db.Column(db.Integer, db.ForeignKey('tblUsers.user_id_col'), unique=True)
    phone_col = db.Column(db.String, nullable=False)
    location_col = db.Column(db.String(150))
    pin_col = db.Column(db.Integer)
    service_description_col = db.Column(db.Text)
    experience_col = db.Column(db.Integer)
    uploaded_documents_path_col = db.Column(db.String, nullable=True)
    is_approved_col = db.Column(db.Boolean)
    service_complaints_count_col = db.Column(db.Integer, default=0)#excellent service,good service,avg service,bad service,very poor service

    
    service_id_col = db.Column(
                                db.Integer, 
                                db.ForeignKey('tblServices.service_id_col'), 
                                nullable=False
                                )
    income_col=db.Column(db.Float)

    # Relationship with clsUsers
    users_table = db.relationship(
                                    "clsUsers", 
                                    back_populates="service_professional_table", 
                                    lazy=True,
                                    cascade="all,delete"
                                )

    # One service professional offers at most one service
    services_table = db.relationship(
                                        "clsServices", 
                                        back_populates="service_professional_table", 
                                        cascade="save-update", 
                                        uselist=False,  # Setting uselist=False in the relationship and adding 
                                        #unique=True to the foreign key ensures that each service professional can only offer one service.
                                        lazy=True
                                    )
    cart_table = db.relationship(
                                    "clsCart", 
                                    back_populates="service_professionals_table", 
                                    lazy=True,
                                    cascade="save-update",
                                    uselist=False
                                )
    service_requests_table= db.relationship(
                                    "clsServiceRequests", 
                                    back_populates="service_professionals_table", 
                                    lazy=True,
                                    cascade="save-update",
                                    uselist=False
                                )
    #A service professional can receive multiple reviews from different customers.
    review_rating_table = db.relationship(
                                            'clsReviewRating',
                                            back_populates='service_professional_table',
                                            lazy=True,
                                            uselist=True  # Allow multiple reviews from different customers
                                        )

class clsServices(db.Model):
    __tablename__ = 'tblServices'
    service_id_col = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_name_col = db.Column(db.String(150), nullable=False, unique=True)
    base_price_col = db.Column(db.Float, nullable=False)
    time_required_col = db.Column(db.Integer)
    description_col = db.Column(db.Text)


    # # One service can be offered by multiple service professional
    service_professional_table = db.relationship(
                                                    "clsServiceProfessionals", 
                                                    back_populates="services_table", 
                                                    uselist=False, # forces 1-to-1
                                                    lazy=True,
                                                    cascade="all"
                                                )
    cart_table = db.relationship(
                                    "clsCart", 
                                    back_populates="services_table",  # Link to the services_table in clsCart
                                    lazy=True,
                                    uselist=True,
                                    cascade="all"
                                )
    service_requests_table = db.relationship(
                                                "clsServiceRequests", 
                                                back_populates="services_table", 
                                                uselist=False,
                                                cascade="all",
                                                lazy=True
                                            )






class clsBlockHistory(db.Model):
    __tablename__ = 'tblBlockHistory'
    block_id_col = db.Column(db.Integer, primary_key=True,autoincrement=True)
    user_id_col = db.Column(db.Integer, db.ForeignKey('tblUsers.user_id_col'), nullable=False)
    block_status_col = db.Column(db.String(50), nullable=False) 
    reason_for_block_col = db.Column(db.String(255), nullable=False) 


class clsServiceRequests(db.Model):
    __tablename__ = 'tblServiceRequests'
    service_request_id_col = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id_col = db.Column(db.Integer, db.ForeignKey('tblCustomers.customer_id_col'), nullable=False)
    service_professional_id_col=db.Column(db.Integer, db.ForeignKey('tblServiceProfessionals.serviceProfessional_id_col'), nullable=False)
    service_id_col = db.Column(db.Integer, db.ForeignKey('tblServices.service_id_col'), nullable=False)
    date_of_service_wanted_col = db.Column(db.String, nullable=False)
    completion_status_col = db.Column(db.String(50), default='not completed')  # Pending, In Progress, Completed
    customers_remarks_instruction_col = db.Column(db.Text, nullable=True)
    is_accepted_by_service_professional_col=db.Column(db.Boolean)

    customers_table = db.relationship(
                                        "clsCustomers", 
                                        back_populates="service_requests_table", 
                                        uselist=False,
                                        lazy=True,
                                        cascade="all"
                                    )
    services_table = db.relationship(
                                        "clsServices", 
                                        back_populates="service_requests_table", 
                                        uselist=False,
                                        lazy=True,
                                        cascade="all"
                                    )
    service_professionals_table = db.relationship(
                                        "clsServiceProfessionals", 
                                        back_populates="service_requests_table", 
                                        uselist=False,
                                        lazy=True,
                                        cascade="all"
                                    )
    review_rating_table = db.relationship(
                                            'clsReviewRating',
                                            back_populates='service_request_table',
                                            lazy=True,
                                            uselist=True  # Allow multiple reviews for each service request
                                        )

class clsReviewRating(db.Model):
    __tablename__ = 'tblReviewRating'

    review_rating_id_col = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_request_id_col = db.Column(db.Integer, db.ForeignKey('tblServiceRequests.service_request_id_col'), nullable=False)
    service_professional_id_col = db.Column( db.Integer, db.ForeignKey('tblServiceProfessionals.serviceProfessional_id_col'), nullable=False)
    customer_id_col = db.Column(db.Integer, db.ForeignKey('tblCustomers.customer_id_col'), nullable=False)
    
    review_text_col = db.Column(db.Text, nullable=True)  # Customer's review text
    rating_col = db.Column(db.Float, nullable=True)  # Rating (e.g., from 1.0 to 5.0)

#UniqueConstraint enforces that the combination of values in customer_id_col,service_professional_id_col,service_request_id_col'', 
# must be unique across all rows in the table. that means no two rows in the table can have the same combination of values for the specified columns.
    unique_constraint = db.UniqueConstraint(
                                                'customer_id_col', 
                                                'service_professional_id_col', 
                                                'service_request_id_col', 
                                                name='uunique_customer_professional_request_combination_for_review_ratingtion'  
                                            )
    


    service_request_table = db.relationship(
                                                "clsServiceRequests", 
                                                back_populates="review_rating_table", 
                                                lazy=True,
                                                uselist=False  # Each review is tied to a single service request
                                            )
    service_professional_table = db.relationship(
                                                    "clsServiceProfessionals", 
                                                    lazy=True,
                                                    back_populates="review_rating_table",
                                                    uselist=False  # Each review relates to a single service professional
                                                )
    customer_table = db.relationship(
                                        "clsCustomers", 
                                        lazy=True,
                                        uselist=False  # Each review relates to a single customer
                                    )



class clsCart(db.Model):
    __tablename__ = 'tblCart'

    cart_id_col = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id_col = db.Column(db.Integer, db.ForeignKey('tblCustomers.customer_id_col'), nullable=False)
    service_id_col = db.Column(db.Integer, db.ForeignKey('tblServices.service_id_col'), nullable=False)
    service_professional_id_col = db.Column(db.Integer, db.ForeignKey('tblServiceProfessionals.serviceProfessional_id_col'), nullable=False)
    service_required_on_date_col=db.Column(db.String,nullable=False)
    customers_remarks_instruction_col=db.Column(db.String(120))
#If you do not want the related clsServices, clsCustomers, and 
# clsServiceProfessionals objects to be deleted when the clsCart object is deleted, THEN JUST WRITE CASCADE="ALL" in both related tables
    customers_table = db.relationship(
        "clsCustomers", 
        back_populates="cart_table",  
        uselist=True, #a customer can have add multiple items in carts 
        lazy="joined",# Ensures related data is loaded immediately when querying
        cascade="save-update"  # do not Automatically delete related customer if cart is deleted only do cascade CRU of CRUD excluding
         # delete and also in cart_table of clsCustomers write cascade="all"
    )

    services_table = db.relationship(
        "clsServices", 
        back_populates="cart_table",
        lazy="joined",
        cascade="save-update",
        uselist=True# This will allow us to get multiple services in a cart (many-to-many)
    )
    service_professionals_table = db.relationship(
        "clsServiceProfessionals", 
        back_populates="cart_table", 
        lazy="joined",
        cascade="save-update",
        uselist=False#if one service professional provides only one service per cart item.
    )
    @property#the below function becomes attribute
    def fun_total_price(self):#this function behave as property of clsCart class and we can call it like an attribute like cart_obj.total_price 
        # This is a property method that calculates the total price on the fly
        totalPrice = 0
        for service in self.services_table:
            if service.base_price_col:
                totalPrice += service.base_price_col
        return totalPrice
    


        

   


