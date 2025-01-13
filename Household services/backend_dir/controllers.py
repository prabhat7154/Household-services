from flask import Flask,render_template,request,url_for,redirect,session,flash
from flask import current_app as myApp
from datetime import datetime

from backend_dir.model import *


def register_admin():
    # Check if the email already exists in the database
    existing_user = clsUsers.query.filter_by(email_col="admin@gmail.com").first()
    if existing_user!=None:
        #do  nothing
        pass
    elif existing_user==None:
        new_admin_record = clsUsers(
            user_name_col="admin",
            email_col="admin@gmail.com",
            password_col="123",
            user_type_col="admin"
            
        )
        db.session.add(new_admin_record)
        db.session.commit() 

@myApp.route("/",methods=['GET'])
def home():
    register_admin()
    return render_template('customer_dir/customer_home.html')

@myApp.route('/register_customer_route', methods=['GET', 'POST'])
def fun_signup_customer():
    if request.method == 'POST':
        user_name = request.form['inpName']
        email = request.form['inpEmail']
        password = request.form['inpPassword']
        repeat_password = request.form['inpRepeatPassword']
        phone = request.form['inpPhone']
        location = request.form['inpLocation']
        pin_code = request.form['inpPin']
        user_type = 'customer'
        date_registered = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Check if the email already exists in the database
        existing_user = clsUsers.query.filter_by(email_col=email).first()
        if existing_user != None:#meqns the mail is already there in db
            error_msg = 'Email already exists. Try with a different email.'
            return render_template('customer_dir/register_customer_html.html', error_msg_data=error_msg)
        elif password != repeat_password:
            error_msg = 'Both passwords must be exactly the same. Try again...'
            return render_template('customer_dir/register_customer_html.html', error_msg_data=error_msg)
        else:

            new_user = clsUsers(user_name_col=user_name, email_col=email, password_col=password, user_type_col=user_type, date_registered_col=date_registered)
            db.session.add(new_user)
            db.session.commit()

            new_customer = clsCustomers(user_id_col=new_user.user_id_col, phone_col=phone, location_col=location,pin_col=pin_code)


            db.session.add(new_customer)
            db.session.commit()

            db.session.close()

            
            #after successful registeration we need to redirect the user to login and show success message
            return render_template('login.html', greeting_msg_after_successful_signup=f"{user_name} you were registered successfully. Now you can login...")

    elif request.method == 'GET':
        error_msg=None
        return render_template('customer_dir/register_customer_html.html',error_msg_data=error_msg)
    else:
        pass




@myApp.route('/register_serviceProfessional_route', methods=['GET', 'POST'])
def fun_signup_serviceProfessional():
    # Query the database to get all services
    all_services_rows = clsServices.query.all()
    
    if request.method == 'POST':
        user_name = request.form['inpName']
        email = request.form['inpEmail']
        password = request.form['inpPassword']
        repeat_password = request.form['inpRepeatPassword']
        phone = request.form['inpPhone']
        location = request.form['inpLocation']
        pin_code = request.form['inpPin']
        serv_id = request.form['ddlServiceType']
        serv_desc = request.form['inpServiceDescription']
        exp = request.form['ddlExperience']
        servicePro_document = request.files['inpFileUpload']
        user_type = 'service professional'
        date_registered = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Check if the email already exists in the database
        is_email_already_exist_in_db = clsUsers.query.filter_by(email_col=email).first()

        if is_email_already_exist_in_db !=None:
            error_msg = 'Email already exists. Try with a different email.'
            return render_template('serviceProfessional_dir/register_serviceProfessional_html.html', data=[error_msg, all_services_rows])
        
        elif password != repeat_password:
            error_msg = 'Both passwords must be exactly the same. Try again...'
            return render_template('serviceProfessional_dir/register_serviceProfessional_html.html', data=[error_msg, all_services_rows])
        
        elif(serv_id=="-1"):
            error_msg = 'Please select a proper service ...'
            return render_template('serviceProfessional_dir/register_serviceProfessional_html.html', data=[error_msg, all_services_rows])
        
        elif(does_selected_File_Has_Valid_Extension(servicePro_document.filename)==False):
            error_msg = 'You have selected an invalid file type.Please select a PDF/PNG/JPG/JPEG/DOC/DOCX Files only...'
            return render_template('serviceProfessional_dir/register_serviceProfessional_html.html', data=[error_msg, all_services_rows])

        else:#if everything is ok 
            
            #os.path.join() combines the path of directory (servicePro_document_Upload_Dir)
            #  and that of the servicePro_document to create the complete file path.
            import os

            project_current_dir = os.path.abspath(os.path.dirname(__file__))

            # Defining the path to your upload folder
            UPLOAD_FOLDER = os.path.join(project_current_dir, 'document_Upload_Dir')
 
            if os.path.exists(UPLOAD_FOLDER)==False:
                os.makedirs(UPLOAD_FOLDER)
             
            servicePro_document_filename = servicePro_document.filename
            from pathlib import Path
            file_extension = Path(servicePro_document_filename).suffix
         
            servicePro_document_filename_renamed = email + file_extension

            # Define the path to save the file
            servicePro_document_path = os.path.join(UPLOAD_FOLDER, servicePro_document_filename_renamed)

            # Save the servicePro_document to the specified path
            servicePro_document.save(servicePro_document_path)
            #lets us now create a record in tblUsers
            new_user = clsUsers(
                user_name_col=user_name,
                email_col=email,
                password_col=password,
                user_type_col=user_type,
                date_registered_col=date_registered
            )
            db.session.add(new_user)
            db.session.commit()
            #lets us now create a record in tblServiceProfessionals
            new_service_professional = clsServiceProfessionals(
                user_id_col=new_user.user_id_col,
                phone_col=phone,
                location_col=location,
                pin_col=pin_code,
                service_id_col=serv_id,
                service_description_col=serv_desc,
                experience_col=exp,
                uploaded_documents_path_col=servicePro_document_path,
                is_approved_col= False # because at the time of registration we want to make it False/pending which nedd to be approved by admin
            )
            db.session.add(new_service_professional)
            db.session.commit()
            
            success_msg="Dear Service Professional, Your Registration was successful. Please wait for approval until document verification."
            return render_template('serviceProfessional_dir/wait_for_document_verification.html', success_msg=success_msg)
        
    elif request.method=="GET":
        error_msg=None
        return render_template('serviceProfessional_dir/register_serviceProfessional_html.html', data=[error_msg, all_services_rows])
    else:
        pass


def does_selected_File_Has_Valid_Extension(name_of_file):
    lowered_case_file_name= name_of_file.lower()
    if lowered_case_file_name.endswith(('.pdf', '.png', '.jpg', '.jpeg','doc', 'docx'))==True:
        return True
    else:
        return False
    
def get_all_services():
    services = db.session.query(clsServices).all()
    return services

def get_all_service_professionals():
    services_professionals = db.session.query(clsServiceProfessionals).all()
    return services_professionals

def get_all_services_request():
    services_requests = db.session.query(clsServiceRequests).all()
    return services_requests

@myApp.route("/route_login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['inpEmail']
        password = request.form['inpPassword']
        user_detail = clsUsers.query.filter_by(email_col=email, password_col=password).first()
        
        if user_detail is not None:
            session['user_type_session'] = user_detail.user_type_col
            session['user_id_session'] = user_detail.user_id_col
            
            # Admin
            if user_detail.user_type_col == "admin":
                return render_template("admin_dir/admin_dashboard_overview_html.html", 
                                       services=get_all_services(),
                                       services_professionals=get_all_service_professionals(),
                                       services_requests=get_all_services_request())
            
            # Customer user
            elif user_detail.user_type_col == "customer":
                no_of_items_in_cart = len(session.get('cart_session', []))
                if no_of_items_in_cart == 0:  # Cart is empty
                    # No items in cart, redirect to home page
                    return render_template("customer_dir/customer_home.html", tblUsers_data=user_detail)
                elif no_of_items_in_cart > 0:  # Cart has items
                    # Transfer items from cart session to DB
                    for element in session['cart_session']:
                        service_id = element['service_id']
                        service_professional_id = element['service_professional_id']
                        service_date=element['service_date']
                        customer_remarks=element['customer_remarks']
                        
                        # Check if service already exists in cart
                        existing_service = db.session.query(clsCart).filter_by(
                            customer_id_col=user_detail.customer_table.customer_id_col,
                            service_id_col=service_id,
                            service_professional_id_col=service_professional_id,
                            service_required_on_date_col=service_date,
                            customers_remarks_instruction_col=customer_remarks
                        ).first()
                        
                        if not existing_service:
                            new_cart_item = clsCart(
                                customer_id_col=user_detail.customer_table.customer_id_col,
                                service_id_col=service_id,
                                service_professional_id_col=service_professional_id,
                                service_required_on_date_col=service_date,
                                customers_remarks_instruction_col=customer_remarks
                            )
                            db.session.add(new_cart_item)
                            db.session.commit()
                    
                    session.pop('cart_session', None)  # Clear the session cart
                    # Redirect to the view cart page if items were added
                    return redirect(url_for('view_cart'))  # Replace 'view_cart' with the appropriate function name for your cart page
            
            # Service Professional
            elif user_detail.user_type_col == "service professional":
                return render_template("serviceProfessional_dir/serviceProfessional_dashboard_overview_html.html", tblUsers_data=user_detail)
        else:  # If email and password did not match
            return render_template("login.html", error_msg_data="You entered an invalid email/password.") 
    else:
        return render_template("login.html", error_msg_data="Wrong HTTP request.")


@myApp.route('/logout_route', methods=['GET'])
def logout():
    session.clear()
    return render_template("customer_dir/customer_home.html", error_msg_data="You have been logged out successfully")




#to prevent Unauthorized access to admin dashboard
def is_user_is_Admin():
    if session.get('user_type_session') == 'admin':
        return True
    else:
        return False

@myApp.route('/adminDashboardOverview_route',methods=['GET'])
def fun_adminDashboardOverview():
    #lets us we allow only authorized user to access the admin dashboard in order toprevent url forging
    if(is_user_is_Admin()==True):

        return render_template('admin_dir/admin_dashboard_overview_html.html',
                               msg="",
                               services=get_all_services(),
                               services_professionals=get_all_service_professionals(),
                               services_requests=get_all_services_request())
    else:
        return render_template('login.html',error_msg_data="You are not authorized to access this page")

@myApp.route('/admin/create_service_route', methods=['POST'])
def fun_create_service():
    if is_user_is_Admin()==True:
        if request.method == 'POST':
            service_name = request.form['inpServiceName'].capitalize()
            base_price = float(request.form['inpBasePrice'])
            time_required = float(request.form['inpTimeRequired'])
            description = request.form['inpDescription']

            existing_service = clsServices.query.filter_by(service_name_col=service_name).first()
            if(existing_service !=None):
                msg = f"The service named {service_name} already exist in database, so it cannot be created."

                return render_template('admin_dir/admin_dashboard_overview_html.html', 
                                        msg=msg, 
                                        allServicesRows=get_all_services())
            elif(base_price<=0):
                msg = f"The base price must be Non zero positive number"

                return render_template('admin_dir/admin_dashboard_overview_html.html', 
                                        msg=msg, 
                                        allServicesRows=get_all_services())
            elif(time_required<=0):
                msg = f"The time required must be Non zero positive number"

                return render_template('admin_dir/admin_dashboard_overview_html.html', 
                                        msg=msg, 
                                        allServicesRows=get_all_services())
            else:
                new_service = clsServices(
                    service_name_col=service_name,
                    base_price_col=base_price,
                    time_required_col=time_required,
                    description_col=description
                )
                db.session.add(new_service)
                db.session.commit()

                msg = f"The new service named {service_name} was created successfully."

                return render_template('admin_dir/admin_dashboard_overview_html.html', 
                                   msg=msg, 
                                   allServicesRows=get_all_services())
    else:
        return render_template('login.html', error_msg_data="You are not authorized to access this page")

@myApp.route('/admin/update_service_route/<int:service_id>', methods=['POST'])
def update_service(service_id):
    if is_user_is_Admin():
        if request.method == "POST": 
            target_service = clsServices.query.get(service_id)

            if target_service == None:
                msg = f"Service ID {service_id} does not exist. It might have been deleted by another admin at the same time when you clicked the update button."
                return render_template('admin_dir/admin_dashboard_overview_html.html', msg=msg, allServicesRows=get_all_services())
            else:
                serv_name = request.form['inpServiceName'].capitalize()
                base_price = float(request.form['inpBasePrice'])
                time_reqd = float(request.form['inpTimeRequired'])
                serv_decr = request.form.get('inpDescription')

                if base_price <= 0:
                    msg = "Base price must be a positive number."
                    return render_template('admin_dir/admin_dashboard_overview_html.html', msg=msg, allServicesRows=get_all_services())
                elif time_reqd <= 0:
                    msg = "Time required must be a positive number."
                    return render_template('admin_dir/admin_dashboard_overview_html.html', msg=msg, allServicesRows=get_all_services())

                else:# If everything is OK, update the service
                    target_service.service_name_col = serv_name
                    target_service.base_price_col = base_price
                    target_service.time_required_col = time_reqd
                    target_service.description_col = serv_decr
                    db.session.commit()

                    msg = f"Service ID {service_id} updated successfully."
                    return render_template('admin_dir/admin_dashboard_overview_html.html', msg=msg, allServicesRows=get_all_services())
        else:
            msg = "Invalid request method."
            return render_template('admin_dir/admin_dashboard_overview_html.html', msg=msg, allServicesRows=get_all_services())

    else:
        return render_template('login.html', error_msg_data="You are not authorized to access this page.")






@myApp.route('/admin/delete_service_route/<int:service_id>', methods=['GET'])
def delete_service(service_id):
    if is_user_is_Admin():
        target_service = db.session.query(clsServices).filter(clsServices.service_id_col==service_id).first()
        if target_service== None:
            msg = f"Service ID {service_id} does not exist in db.It might have been deleted by another admin at the same time when you clicked update button."
            return render_template('admin_dir/admin_dashboard_overview_html.html', msg=msg, allServicesRows=get_all_services())
        else:
            db.session.delete(target_service)
            db.session.commit()
            
            related_block_histories = db.session.query(clsBlockHistory).filter(clsBlockHistory.user_id_col == service_id).all()
            for block_history in related_block_histories:
                db.session.delete(block_history)
                db.session.commit()
            #we also need to delete associated service professionals

            msg = f"Service ID {service_id} deleted successfully."
            return render_template('admin_dir/admin_dashboard_overview_html.html', msg=msg, allServicesRows=get_all_services())
    else:
        return render_template('login.html', error_msg_data="You are not authorized to access this page.")

@myApp.route('/admin/approvals_disapproval_route', methods=['GET'])
def waiting_approvals():
    if is_user_is_Admin()==True: 
        all_service_professionals_rows = getAllServiceProfessionals()
        
        return render_template('admin_dir/admin_dashboard_overview_html.html', all_service_professionals_rows=all_service_professionals_rows)
    else:
        return render_template('login.html', error_msg_data="You are not authorized to access this page.")





#perform approving
@myApp.route('/admin/approve_service_professional_route/<int:serviceProfessional_id>', methods=['GET'])
def approve_service_professional(serviceProfessional_id):
    if is_user_is_Admin()==True:
        that_service_professional = db.session.query(clsServiceProfessionals).filter_by(serviceProfessional_id_col=serviceProfessional_id).first()

        if that_service_professional != None:
            if that_service_professional.is_approved_col == False:
                # lets us Approve the service professional
                that_service_professional.is_approved_col = True
                db.session.commit()
                return render_template('admin_dir/admin_dashboard_overview_html.html',
                                    msg=f"Service Professional with service Professional id {serviceProfessional_id} was successfully approved.",
                                    services=get_all_services(),
                                    services_professionals=get_all_service_professionals(),
                                    services_requests=get_all_services_request())
            else:
                return render_template('admin_dir/admin_dashboard_overview_html.html',
                                    msg=f"Service Professional with service Professional id {serviceProfessional_id} is already approved.",
                                    services=get_all_services(),
                                    services_professionals=get_all_service_professionals(),
                                    services_requests=get_all_services_request())
        else:
            return render_template('admin_dir/admin_dashboard_overview_html.html', 
                                   msg=f"Service Professional with service Professional id {serviceProfessional_id} not found in database.It might be deleted by some other admin at the time you tried to approve him",
                                   services=get_all_services(),
                                   services_professionals=get_all_service_professionals(),
                                   services_requests=get_all_services_request())
    else:
        return render_template('login.html', error_msg_data="You are not authorized to access this page.")



#perform disapproving
@myApp.route('/admin/disapprove_service_professional_route/<int:serviceProfessional_id>', methods=['GET'])
def disapprove_service_professional(serviceProfessional_id):
    if is_user_is_Admin()==True:  # Ensure only admin can access this route
        that_service_professional = db.session.query(clsServiceProfessionals).filter_by(serviceProfessional_id_col=serviceProfessional_id).first()

        if that_service_professional !=None:
            # lets disapprove the service professional
            if(that_service_professional.is_approved_col==True):
                that_service_professional.is_approved_col = False 
                db.session.commit()
                return render_template('admin_dir/admin_dashboard_overview_html.html',
                                    msg=f"Service Professional with service Professional id {serviceProfessional_id} was successfully disapproved.",
                                    services=get_all_services(),
                                   services_professionals=get_all_service_professionals(),
                                   services_requests=get_all_services_request())
            else:
                return render_template('admin_dir/approve_disapprove_serviceProfessional.html',
                                    success_msg=f"Service Professional with service Professional id {serviceProfessional_id} is  already disapproved.",
                                    services=get_all_services(),
                                   services_professionals=get_all_service_professionals(),
                                   services_requests=get_all_services_request())
        else:
            return render_template('admin_dir/approve_disapprove_serviceProfessional.html', 
                                   error_msg=f"Service Professional with service Professional id {serviceProfessional_id} not found in database.It might be deleted by some other admin at the time you tried to approve him",
                                   services=get_all_services(),
                                   services_professionals=get_all_service_professionals(),
                                   services_requests=get_all_services_request())
    else:
        return render_template('login.html', error_msg_data="You are not authorized to access this page.")


@myApp.route('/admin/delete_service_professional_route/<int:serviceProfessional_id>', methods=['GET'])
def delete_service_professional(serviceProfessional_id):
    if is_user_is_Admin()==True:  # Ensure only admin can access this route
        that_service_professional = db.session.query(clsServiceProfessionals).filter_by(serviceProfessional_id_col=serviceProfessional_id).first()

        if that_service_professional !=None:
            # lets delete the service professional row
            db.session.delete(that_service_professional)
            db.session.commit()
            return render_template('admin_dir/admin_dashboard_overview_html.html',
                                msg=f"Service Professional with service Professional id {serviceProfessional_id} has been deleted from database.",
                                services=get_all_services(),
                                services_professionals=get_all_service_professionals(),
                                services_requests=get_all_services_request())
            
        else:
            return render_template('admin_dir/admin_dashboard_overview_html.html', 
                                   error_msg=f"Service Professional with service Professional id {serviceProfessional_id} not found in database.It might be deleted by some other admin at the time you tried to delete him",
                                   services=get_all_services(),
                                   services_professionals=get_all_service_professionals(),
                                   services_requests=get_all_services_request())
    else:
        return render_template('login.html', error_msg_data="You are not authorized to access this page.")
    


@myApp.route('/admin/service_request_associated_with_service_name_route/<int:service_id>', methods=['GET'])
def service_request_associated_with_service_name(service_id):
    if is_user_is_Admin()==True:  # Ensure only admin can access this route
        those_service_requests_associated_with_a_service_name = db.session.query(clsServiceRequests).filter(clsServiceRequests.service_id_col==service_id).all()
        
        if those_service_requests_associated_with_a_service_name !=None:
            
            return render_template('admin_dir/service_request_associated_with_service_name.html',
                                   service_name=db.session.query(clsServices.service_name_col).filter(clsServices.service_id_col==service_id).scalar(),
                                    those_service_requests_associated_with_a_service_name=those_service_requests_associated_with_a_service_name)
            
        else:
            return render_template('admin_dir/service_request_associated_with_service_name.html', 
                                   msg=f"No service request has been made with that service id.",
                                   service_name=db.session.query(clsServices.service_name_col).filter(clsServices.service_id_col==service_id).scalar(),
                                   those_service_requests_associated_with_a_service_name=those_service_requests_associated_with_a_service_name)
    else:
        return render_template('login.html', error_msg_data="You are not authorized to access this page.")



@myApp.route('/admin/service_requested_to_service_professional_route/<int:serviceProfessional_id>', methods=['GET'])
def service_requested_to_service_professional(serviceProfessional_id):
    if is_user_is_Admin()==True:  # Ensure only admin can access this route
        that_service_professional = db.session.query(clsServiceProfessionals).filter(clsServiceProfessionals.serviceProfessional_id_col==serviceProfessional_id).first()

        if that_service_professional !=None:
            service_requests_requested_to_that_service_professional=db.session.query(clsServiceRequests).filter(clsServiceRequests.service_professional_id_col==serviceProfessional_id).all()
            if service_requests_requested_to_that_service_professional !=None:
                return render_template('admin_dir/service_requested_to_service_professional.html',
                                       that_service_professional=that_service_professional,
                                    service_requests_requested_to_that_service_professional=service_requests_requested_to_that_service_professional)
            else:
                return render_template('admin_dir/service_requested_to_service_professional.html',
                                       that_service_professional=that_service_professional, 
                                   service_requests_requested_to_that_service_professional=service_requests_requested_to_that_service_professional)

            
        else:
            return render_template('admin_dir/service_requested_to_service_professional.html', 
                                   error_msg=f"Service Professional with service Professional id {serviceProfessional_id} not found in database.It might be deleted by some other admin at the time you tried to delete him"
                                   )
    else:
        return render_template('login.html', error_msg_data="You are not authorized to access this page.")

@myApp.route('/admin/search_by_route', methods=['GET', 'POST'])
def fun_search_by_admin():
    # Capture the selected search type and keyword
    if request.method == 'POST':
        search_by = request.form['ddlSearchBy']
        search_keyword = request.form['inpSearchKeyword']
        
        # Perform the search based on the 'search_by' value
        if search_by == 'Service_Name':
            services = db.session.query(clsServices).filter(clsServices.service_name_col.like(f"%{search_keyword}%")).all()
            return render_template('admin_dir/search.html', 
                                   search_results=services, 
                                   search_keyword=search_keyword, 
                                   search_by=search_by)
        
        elif search_by == 'Professional_Name':
            professionals = db.session.query(clsServiceProfessionals).join(clsUsers).filter(
                    clsUsers.user_name_col.like(f"%{search_keyword}%")
                ).all()
            return render_template('admin_dir/search.html', 
                                   search_results=professionals, 
                                   search_keyword=search_keyword, 
                                   search_by=search_by)
        
        elif search_by == 'Customer_Name':
            customers = db.session.query(clsCustomers).join(clsUsers).filter(
                    clsUsers.user_name_col.like(f"%{search_keyword}%")
                ).all()
            return render_template('admin_dir/search.html', 
                                   search_results=customers, 
                                   search_keyword=search_keyword, 
                                   search_by=search_by)
        
        elif search_by == 'customer_Location':
            from sqlalchemy import and_
            customers = db.session.query(clsCustomers).join(clsUsers).filter(and_(clsCustomers.location_col.like(f"%{search_keyword}%"),clsUsers.user_type_col=="customer")).all()
            return render_template('admin_dir/search.html', 
                                   search_results=customers, 
                                   search_keyword=search_keyword, 
                                   search_by=search_by) 
                                                            
        elif search_by == 'customer_PinCode':
            from sqlalchemy import and_
            customers = db.session.query(clsCustomers).join(clsUsers).filter(and_(clsCustomers.pin_col.like(f"%{search_keyword}%"),clsUsers.user_type_col=="customer")).all()
            return render_template('admin_dir/search.html', 
                                   search_results=customers, 
                                   search_keyword=search_keyword, 
                                   search_by=search_by)

        elif search_by == 'professional_Location':
                from sqlalchemy import and_
                professional= db.session.query(clsServiceProfessionals).join(clsUsers).filter(and_(clsServiceProfessionals.location_col.like(f"%{search_keyword}%"),clsUsers.user_type_col=="service professional")).all()
                return render_template('admin_dir/search.html', 
                                    search_results=professional, 
                                    search_keyword=search_keyword, 
                                    search_by=search_by)                          
        elif search_by == 'professional_PinCode':
            from sqlalchemy import and_
            professional = db.session.query(clsServiceProfessionals).join(clsUsers).filter(and_(clsServiceProfessionals.pin_col.like(f"%{search_keyword}%"),clsUsers.user_type_col=="service professional")).all()
            return render_template('admin_dir/search.html', 
                                search_results=professional, 
                                search_keyword=search_keyword, 
                                search_by=search_by)
        
        elif search_by == 'All_Accepted_Request':
            service_requests = db.session.query(clsServiceRequests).filter(clsServiceRequests.is_accepted_by_service_professional_col == True).all()
            return render_template('admin_dir/search.html', 
                                   search_results=service_requests, 
                                   search_keyword=search_keyword, 
                                   search_by=search_by)
        elif search_by == 'All_Denied_Request':
            service_requests = db.session.query(clsServiceRequests).filter(clsServiceRequests.is_accepted_by_service_professional_col == False).all()
            return render_template('admin_dir/search.html', 
                                   search_results=service_requests, 
                                   search_keyword=search_keyword, 
                                   search_by=search_by)
        elif search_by == 'All_Completed_Service':
            service_requests = db.session.query(clsServiceRequests).filter(clsServiceRequests.completion_status_col == 'completed').all()
            return render_template('admin_dir/search.html', 
                                   search_results=service_requests, 
                                   search_keyword=search_keyword, 
                                   search_by=search_by)
        elif search_by == 'All_Uncompleted_Service':
            service_requests = db.session.query(clsServiceRequests).filter(clsServiceRequests.completion_status_col == 'not completed').all()
            return render_template('admin_dir/search.html', 
                                   search_results=service_requests, 
                                   search_keyword=search_keyword, 
                                   search_by=search_by)
        else:
            search_results = []  # If no valid search type is selected
        
        # Return the results to the template
        return render_template('admin_dir/search.html', search_results=search_results, search_keyword=search_keyword, search_by=search_by)
    else:
        return render_template('admin_dir/search.html')


def getTotalNoOfUsers_Except_Admin():
    from sqlalchemy import func
    totalNoOfUsers = clsUsers.query.with_entities(func.count(clsUsers.user_id_col)).scalar()
    totalNoOfUsers_except_Admin =totalNoOfUsers-1
    return totalNoOfUsers_except_Admin

@myApp.route('/admin/block_unblock_route',methods=['GET'])
def fun_open_UserManagement():
    if(is_user_is_Admin()==True):
        #getting all users except admin
        allUsersRows_exceptAdmin=get_all_users_except_admin() 
        

        return render_template("admin_dir/block_unblock_Users_html.html",
                               allUsersRows_exceptAdmin_data=allUsersRows_exceptAdmin,
                               totalNoOfUsers_except_Admin_data=getTotalNoOfUsers_Except_Admin())
    else:
        return render_template('login.html',error_msg_data="You are not authorized to access this page")  



#perform blocking
# Block a Service Professional
@myApp.route('/block_service_professional_route/<int:user_id>', methods=['GET'])
def fun_block_service_professional(user_id):
    if is_user_is_Admin():
        target_user = db.session.query(clsUsers).filter(clsUsers.user_id_col==user_id).first()
        
        # lets check user exists and is a service professional
        if target_user and target_user.user_type_col == "service professional":
            target_user.block_status_col = 'blocked/inactive'
            db.session.commit()
            new_block_record = clsBlockHistory(
                                                user_id_col=user_id,
                                                block_status_col='blocked/inactive',
                                                reason_for_block_col='admin decision'
                                                )
            db.session.add(new_block_record)
            db.session.commit()

            all_users_rows_except_admin = get_all_users_except_admin()
            return render_template("admin_dir/block_unblock_Users_html.html",
                                    msg=f"Service Professional with User ID {user_id} has been successfully blocked .",
                                    allUsersRows_exceptAdmin_data=all_users_rows_except_admin,
                                    totalNoOfUsers_except_Admin_data=getTotalNoOfUsers_Except_Admin())
        
        else:
            all_users_rows_except_admin = get_all_users_except_admin()
            return render_template("admin_dir/block_unblock_Users_html.html",
                                   msg=f"Service Professional with ID {user_id} not found.",
                                   allUsersRows_exceptAdmin_data=all_users_rows_except_admin,
                                   totalNoOfUsers_except_Admin_data=getTotalNoOfUsers_Except_Admin())
    else:
        return render_template('login.html', error_msg_data="You are not authorized to access this page.")


@myApp.route('/block_customer_route/<int:user_id>', methods=['GET'])
def fun_block_customer(user_id):
    if is_user_is_Admin():
        target_user = db.session.query(clsUsers).filter(clsUsers.user_id_col==user_id).first()

        if target_user and target_user.user_type_col == "customer":
            
            target_user.block_status_col = 'blocked/inactive'
            new_block_record = clsBlockHistory(
                user_id_col=user_id,
                block_status_col='blocked/inactive',
                reason_for_block_col='admin decision'
            )
            db.session.add(new_block_record)
            db.session.commit()

            all_users_rows_except_admin = get_all_users_except_admin()
            return render_template("admin_dir/block_unblock_Users_html.html",
                msg=f"Customer with User ID {user_id} has been blocked successfully.",
                allUsersRows_exceptAdmin_data=all_users_rows_except_admin,
                totalNoOfUsers_except_Admin_data=getTotalNoOfUsers_Except_Admin())
            
        else:
            all_users_rows_except_admin = get_all_users_except_admin()
            return render_template("admin_dir/block_unblock_Users_html.html",
                msg=f"Customer with ID {user_id} not found.",
                allUsersRows_exceptAdmin_data=all_users_rows_except_admin,
                totalNoOfUsers_except_Admin_data=getTotalNoOfUsers_Except_Admin())
    else:
        return render_template('login.html', error_msg_data="You are not authorized to access this page.")

# Unblock a Service Professional
@myApp.route('/unblock_service_professional_route/<int:user_id>', methods=['GET'])
def fun_unblock_service_professional(user_id):
    if is_user_is_Admin():
        
        target_user = db.session.query(clsUsers).filter(clsUsers.user_id_col==user_id).first()
        # cols block_status_col of clsUsers and col service_complaints_count_col and review_score_col of clsServiceProfessionala gets affected
        if target_user and target_user.user_type_col == "service professional":
            if target_user.block_status_col == 'blocked/inactive':
                target_user.block_status_col = 'unblocked/active'               

                new_block_record = clsBlockHistory(
                    user_id_col=user_id,
                    block_status_col='unblocked/active',
                    reason_for_block_col=''
                )
                db.session.add(new_block_record)
                db.session.commit()

                all_users_rows_except_admin = get_all_users_except_admin()
                return render_template("admin_dir/block_unblock_Users_html.html",
                    msg=f"Service Professional with User ID {user_id} has been unblocked successfully.",
                    allUsersRows_exceptAdmin_data=all_users_rows_except_admin,
                    totalNoOfUsers_except_Admin_data=getTotalNoOfUsers_Except_Admin())
            else:
                all_users_rows_except_admin = get_all_users_except_admin()
                return render_template(
                    "admin_dir/block_unblock_Users_html.html",
                    msg=f"Service Professional with User ID {user_id} is already unblocked.",
                    allUsersRows_exceptAdmin_data=all_users_rows_except_admin,
                    totalNoOfUsers_except_Admin_data=getTotalNoOfUsers_Except_Admin())
        else:
            all_users_rows_except_admin = get_all_users_except_admin()
            return render_template("admin_dir/block_unblock_Users_html.html",
                msg=f"Service Professional with User ID {user_id} not found in database.",
                allUsersRows_exceptAdmin_data=all_users_rows_except_admin,
                totalNoOfUsers_except_Admin_data=getTotalNoOfUsers_Except_Admin()
            )
    else:
        return render_template('login.html', error_msg_data="You are not authorized to access this page.")



@myApp.route('/unblock_customer_route/<int:user_id>', methods=['GET'])
def fun_unblock_customer(user_id):
    if is_user_is_Admin():
        
        target_user = db.session.query(clsUsers).filter(clsUsers.user_id_col==user_id).first()
        # cols block_status_col of clsUsers and col wage_theft_count of clsCustomers gets affected
        if target_user and target_user.user_type_col == "customer":
            if target_user.block_status_col == 'blocked/inactive':
                target_user.block_status_col = 'unblocked/active'
                #since we are unblocking we also need to reset their block criteria wage_theft_count_col
                target_customer=db.session.query(clsCustomers).filter(clsCustomers.user_id_col==user_id).first()
                target_customer.wage_theft_count_col=0
                
                new_block_record = clsBlockHistory(
                    user_id_col=user_id,
                    block_status_col='unblocked/active',
                    reason_for_block_col=''
                )
                db.session.add(new_block_record)
                db.session.commit()

                all_users_rows_except_admin = get_all_users_except_admin()
                return render_template("admin_dir/block_unblock_Users_html.html",
                    msg=f"Customer with User ID {user_id} has been unblocked successfully.",
                    allUsersRows_exceptAdmin_data=all_users_rows_except_admin,
                    totalNoOfUsers_except_Admin_data=getTotalNoOfUsers_Except_Admin()
                )
            else:
                all_users_rows_except_admin = get_all_users_except_admin()
                return render_template("admin_dir/block_unblock_Users_html.html",
                    msg=f"Customer with User ID {user_id} is already unblocked.",
                    allUsersRows_exceptAdmin_data=all_users_rows_except_admin,
                    totalNoOfUsers_except_Admin_data=getTotalNoOfUsers_Except_Admin()
                )
        else:
            all_users_rows_except_admin = get_all_users_except_admin()
            return render_template("admin_dir/block_unblock_Users_html.html",
                msg=f"Customer with User ID {user_id} not found in database.",
                allUsersRows_exceptAdmin_data=all_users_rows_except_admin,
                totalNoOfUsers_except_Admin_data=getTotalNoOfUsers_Except_Admin()
            )
    else:
        return render_template('login.html', error_msg_data="You are not authorized to access this page.")


def get_all_users_except_admin():
    allUsersRows_exceptAdmin = clsUsers.query.filter(clsUsers.user_type_col !="admin").all()
    return allUsersRows_exceptAdmin


def getAllServiceProfessionals():
    all_service_professionals_rows = clsServiceProfessionals.query.all()
    return all_service_professionals_rows

# Defining the path where the image will be saved (ensure this folder exists)
import os
STATIC_FOLDER = os.path.join(os.getcwd(), 'static', 'graphs')

@myApp.route('/admin/summary_route', methods=['GET'])
def service_requests_graph():

    if not os.path.exists(STATIC_FOLDER):
        os.makedirs(STATIC_FOLDER)

    from sqlalchemy import func 
    status_counts = db.session.query(clsServiceRequests.completion_status_col, func.count(clsServiceRequests.service_request_id_col)).group_by(clsServiceRequests.completion_status_col).all()

    if len(status_counts) == 0:
        return render_template('admin_dir/admin_summary.html', error_msg="No service request data available.")

    statuses = []
    counts = []
    for status, count in status_counts:
        statuses.append(status)
        counts.append(count)


    img_file = os.path.join(STATIC_FOLDER, 'service_requests_graph.png')
    import matplotlib.pyplot as plt
    plt.bar(statuses, counts)
    plt.xlabel('Status')
    plt.ylabel('Requests')
    plt.title('Service Requests by Status')


    plt.savefig(img_file, format='png')
    plt.close()
    return render_template('admin_dir/admin_summary.html', graph_image='graphs/service_requests_graph.png')


 
def getProfessionalName(search_keyword):

    filteredrecords = (
        db.session.query(clsServiceProfessionals)
        .join(clsServices)
        .join(clsUsers)
        .filter(clsUsers.user_name_col.ilike(f"%{search_keyword}%"))
        .all()
    )
 
    return filteredrecords


def getTotalItemsInCart():
    
    return render_template("customer_dir/customer_layout.html",cartItemCount=clsCart().get_total_items_cart(session['user_id_session']))


@myApp.route('/professional/search_route', methods=['GET', 'POST'])
def fun_search_by_professional():
    if request.method == 'POST':
        search_by = request.form['ddlSearchBy']
        search_keyword = request.form['inpSearchKeyword']
        
        if search_by == 'Customer_Name':
            customers = db.session.query(clsCustomers).join(clsUsers).filter(
                    clsUsers.user_name_col.like(f"%{search_keyword}%")
                ).all()
            return render_template('serviceProfessional_dir/search.html', 
                                   search_results=customers, 
                                   search_keyword=search_keyword, 
                                   search_by=search_by)
        
        elif search_by == 'customer_Location':
            from sqlalchemy import and_
            customers = db.session.query(clsCustomers).join(clsUsers).filter(and_(clsCustomers.location_col.like(f"%{search_keyword}%"),clsUsers.user_type_col=="customer")).all()
            return render_template('serviceProfessional_dir/search.html', 
                                   search_results=customers, 
                                   search_keyword=search_keyword, 
                                   search_by=search_by) 
                                                            
        elif search_by == 'customer_PinCode':
            from sqlalchemy import and_
            customers = db.session.query(clsCustomers).join(clsUsers).filter(and_(clsCustomers.pin_col.like(f"%{search_keyword}%"),clsUsers.user_type_col=="customer")).all()
            return render_template('serviceProfessional_dir/search.html', 
                                   search_results=customers, 
                                   search_keyword=search_keyword, 
                                   search_by=search_by)

        
        else:
            search_results = []  # If no valid search type is selected
        
    
        return render_template('serviceProfessional_dir/search.html', search_results=search_results, search_keyword=search_keyword, search_by=search_by)
    else:
        return render_template('serviceProfessional_dir/search.html')
@myApp.route('/customer/my_profile_route', methods=['GET', 'POST'])
def fun_update_profile():
    if 'user_id_session' not in session or session['user_type_session'] != 'customer':
        message = "Please log in to proceed."
        return render_template('login.html', message=message)
    else:
        user_id = session['user_id_session']
        print(f"User ID from session: {user_id}")  # Check if the user ID is correctly fetched from the session

        that_customer = db.session.query(clsCustomers).filter(clsCustomers.user_id_col == user_id).first()
        that_users = db.session.query(clsUsers).filter(clsUsers.user_id_col == user_id).first()
        
        if not that_customer or not that_users:
            # If either customer or user data is not found in the database
            print(f"Customer: {that_customer}, User: {that_users}")  # Check if either is None
            return render_template('customer_dir/my_profile.html', 
                                   that_customer=that_customer, 
                                   that_users=that_users,
                                   msg="Profile data not found in database.")
        
        if request.method == 'POST':
            name = request.form['inpName'].strip()
            phone = request.form['inpPhone'].strip()
            location = request.form['inpLocation'].strip()
            pin = request.form['inpPin'].strip()

            if that_customer:
                that_customer.phone_col = phone
                that_customer.location_col = location
                that_customer.pin_col = pin
                that_users.user_name_col = name
                db.session.commit()
                return render_template('customer_dir/my_profile.html', 
                                       that_customer=that_customer, 
                                       that_users=that_users,
                                       msg="Profile updated successfully")
            else:
                return render_template('customer_dir/my_profile.html',
                                       that_customer=that_customer, 
                                       that_users=that_users,
                                       msg="Your profile not found in database")
        else:
            return render_template('customer_dir/my_profile.html', that_customer=that_customer, that_users=that_users)



@myApp.route('/customer/search_services_route', methods=['GET','POST'])
def fun_search_services():
    if request.method == "POST":
        search_keyword = request.form["inpSearch"].strip()

        filtered_services_records_by_service_name = getServicesBy_ServiceName(search_keyword)
        filtered_services_records_by_location = getServicesBy_Location(search_keyword)
        filtered_services_records_by_pin = getServicesBy_PinCode(search_keyword)
        filtered_services_records_by_service_professional_name = getServicesBy_ProfessionalName(search_keyword)

        # Combining all results lists into a set to avoid duplication
        all_results =  set(filtered_services_records_by_service_name + filtered_services_records_by_location + filtered_services_records_by_pin + filtered_services_records_by_service_professional_name)
        all_results= list(all_results)
        if all_results !=None:
            return render_template('customer_dir/service_search_results.html', 
                                   services=all_results, 
                                   search_keyword_data=search_keyword,
                                   search_result_count=len(all_results))

        else:
            return render_template('customer_dir/service_search_results.html',
                                   services=[],
                                   search_keyword_data=search_keyword,
                                   search_result_count=len(all_results))
    elif request.method=="GET":
        return render_template('customer_dir/customer_home.html')
     

def getServicesBy_ServiceName(search_keyword):
    #want to show only those professionals who has been approved by admin
    from sqlalchemy import and_


    filtered_services_records = (
        db.session.query(clsServices).join(clsServiceProfessionals)  # Joining with clsServiceProfessionals
        .filter(
            and_(
                clsServices.service_name_col.ilike(f"%{search_keyword}%"),  # Filter by service name
                clsServiceProfessionals.is_approved_col == True  # Filter by approval status
            )
        )
        .all()
    )

    return filtered_services_records

def getServicesBy_Location(search_keyword):
    #we need to join clsServices with clsServiceProfessionals to access location_col
   #want to show services by only those professionals who has been approved by admin
    from sqlalchemy import and_
    filtered_services_records = (
                                    db.session.query(clsServices)
                                    .join(clsServiceProfessionals)
                                    .filter(and_(clsServiceProfessionals.location_col.ilike(f"%{search_keyword}%"),clsServiceProfessionals.is_approved_col==True))
                                    .all()
                                )
    return filtered_services_records

def getServicesBy_PinCode(search_keyword):
 #want to show services by only those professionals who has been approved by admin
    from sqlalchemy import and_
    filtered_services_records = (
        db.session.query(clsServices)
        .join(clsServiceProfessionals)
        .filter(and_(clsServiceProfessionals.pin_col.ilike(f"%{search_keyword}%"),clsServiceProfessionals.is_approved_col==True))
        .all()
    )
    return filtered_services_records

def getServicesBy_ProfessionalName(search_keyword):
 
     #want to show services by only those professionals who has been approved by admin
    from sqlalchemy import and_

    filtered_services_records = (
        db.session.query(clsServices)
        .join(clsServiceProfessionals)
        .join(clsUsers)
        .filter(and_(clsUsers.user_name_col.ilike(f"%{search_keyword}%"),clsServiceProfessionals.is_approved_col==True))
        .all()
    )
 
    return filtered_services_records


@myApp.route('/customer/add_to_cart_route/<int:service_id>/<int:service_professional_id>/', methods=['GET', 'POST'])
def add_to_cart(service_id, service_professional_id):
    message = "" 
    customer_remarks = request.form['inpCustomer_Remark']
    service_required_on_date_str = request.form['inpServiceRequiredOnDate']
 
   

    if 'user_id_session' not in session:  # User is not logged in
        # Create a session-based cart if it doesn't exist
        if 'cart_session' not in session:
            session['cart_session'] = []
        
        # Adding the service to the session cart
        session['cart_session'].append({'service_id': service_id, 
                                        'service_professional_id': service_professional_id,
                                        'service_date':service_required_on_date_str,
                                        'customer_remarks':customer_remarks if customer_remarks !="" else 'No Remarks/instruction'})
        session.modified = True
        
     
        message = "Please log in to get your services added to your cart."
        
   
        return render_template('login.html', message=message)
    
    else:  # User is logged in
        user_id = session['user_id_session']
        buyer_customer = db.session.query(clsCustomers).filter_by(user_id_col=user_id).first()
        
        if buyer_customer is not None:
            # Check if the service is already in the user's cart
            existing_service = db.session.query(clsCart).filter_by(
                customer_id_col=buyer_customer.customer_id_col, 
                service_id_col=service_id
            ).first()
            
            if existing_service:
                # Service is already in the cart
                message = "This service is already in your cart."
            else:
                # Add a new service to the cart
                new_item = clsCart(
                    customer_id_col=buyer_customer.customer_id_col,
                    service_id_col=service_id,
                    service_professional_id_col=service_professional_id,
                    service_required_on_date_col=service_required_on_date_str,
                    customers_remarks_instruction_col=customer_remarks if customer_remarks !="" else 'No Remarks/instruction'
                )
                db.session.add(new_item)
                db.session.commit()
                message = "Service added to your cart."
        else:
            message = "Customer details not found."
        
        
        return render_template("customer_dir/customer_home.html", message=message)


@myApp.route('/customer/view_cart_route')
def view_cart():
    if 'user_id_session' not in session and session['user_type_session'] != 'customer':
        msg="You must be logged in to view your cart."
        return render_template('login.html', message=msg)
    else:
        user_id = session['user_id_session']
        customer = db.session.query(clsCustomers).filter_by(user_id_col=user_id).first()

        if customer !=None:
            carts_list_rows = db.session.query(clsCart).filter_by(customer_id_col=customer.customer_id_col).all()
            # lets us Calculate total price for all carts items
            totalPayableAmt = 0

            for cart in carts_list_rows:
                totalPayableAmt=totalPayableAmt + cart.fun_total_price

            
            return render_template('customer_dir/view_cart.html', 
                                carts_list_rows=carts_list_rows,
                                totalPayableAmt=totalPayableAmt,
                                customer_id_data=customer.customer_id_col)
        else:
            msg="Customer details not found."
            return render_template('login.html', message=msg)
        
@myApp.route('/customer/remove_item_from_cart_route/<int:service_id>', methods=['GET', 'POST'], strict_slashes=False)
def remove_item_from_cart(service_id):
    if 'user_id_session' not in session and session['user_type_session'] != 'customer':
        message = "Please log in to manage your cart."
        return render_template('login.html', message=message)

    user_id = session['user_id_session']

    # Find the customer linked to this user
    customer = db.session.query(clsCustomers).filter_by(user_id_col=user_id).first()
    if not customer:
        return render_template('customer_dir/view_cart.html', carts_list_rows=[], msg="Customer not found.")

  
    cart_item = db.session.query(clsCart).filter_by(
        customer_id_col=customer.customer_id_col,
        service_id_col=service_id
    ).first()

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
 
        updated_cart = db.session.query(clsCart).filter_by(customer_id_col=customer.customer_id_col).all()
        return render_template('customer_dir/view_cart.html', carts_list_rows=updated_cart, msg="Item removed from cart successfully.")
    else:
 
        updated_cart = db.session.query(clsCart).filter_by(customer_id_col=customer.customer_id_col).all()
        return render_template('customer_dir/view_cart.html', carts_list_rows=updated_cart, msg="Item not found in your cart.")

@myApp.route('/customer/clear_carts_route/<int:customer_id_data>', methods=['GET'], strict_slashes=False)
def clear_cart(customer_id_data):

    if 'user_id_session' not in session and session['user_type_session'] != 'customer':
        return render_template('login.html', message="Please log in to clear your cart.")
    
    user_id = session['user_id_session']
    customer = db.session.query(clsCustomers).filter_by(user_id_col=user_id, customer_id_col=customer_id_data).first()

    if not customer:
        return render_template('customer_dir/view_cart.html',message="customer not found.")

    # Delete all cart items for this customer
    db.session.query(clsCart).filter_by(customer_id_col=customer_id_data).delete()
    db.session.commit()


    return render_template('customer_dir/view_cart.html',message="All cart items have been cleared successfully.")


@myApp.route('/continue_shopping_route', strict_slashes=False)
def continue_shopping():
    return render_template('customer_dir/customer_home.html')



@myApp.route('/customer/create_service_request_route/<int:customer_id_data>', methods=['GET', 'POST'])
def create_service_request(customer_id_data):
    if 'user_id_session' not in session and session['user_type_session'] != 'customer':
        message = "Please log in to proceed."
        return render_template('login.html', message=message)

    user_id = session['user_id_session']

 
    customer = db.session.query(clsCustomers).filter_by(customer_id_col=customer_id_data,user_id_col=user_id).first()
    if not customer:
        return render_template('customer_dir/view_cart.html', carts_list_rows=[], msg="Customer not found.")
    else:
        
        list_of_records_cart = db.session.query(clsCart.customer_id_col,clsCart.service_id_col,
                                 clsCart.service_professional_id_col,clsCart.service_required_on_date_col,
                                 clsCart.customers_remarks_instruction_col).filter_by(customer_id_col=customer_id_data).all()
        
        for (customer_id,service_id,service_professional_id,service_required_on_date,customers_remarks_instruction) in list_of_records_cart:
            new_item = clsServiceRequests(
                    customer_id_col=customer_id,
                    service_id_col=service_id,
                    service_professional_id_col=service_professional_id,
                    date_of_service_wanted_col=service_required_on_date,
                    customers_remarks_instruction_col=customers_remarks_instruction,
                    completion_status_col="not completed"
                )
            db.session.add(new_item)
            db.session.commit()

        
        message = "You successfully created Service Request."
        #after this, delete cart items for that customer
        cart_items = clsCart.query.filter(clsCart.customer_id_col == customer_id).all()
        for cart_item in cart_items:
            db.session.delete(cart_item)
            db.session.commit() # Commit the session to apply the deletion

        
        return render_template('customer_dir/thankyou_for_shopping.html',  msg=message)


 
def get_accepted_denied_service_request(customer_id):
    list_of_all_accepted_denied_ServiceRequestsrecords = db.session.query(clsServiceRequests).filter(clsServiceRequests.customer_id_col==customer_id).all()
    return list_of_all_accepted_denied_ServiceRequestsrecords


@myApp.route('/my_services_route', methods=['GET'])
def open_my_services():
    if 'user_id_session' not in session and session['user_type_session'] != 'customer':
        message = "Please log in to proceed."
        return render_template('login.html', message=message)
    else:
        user_id = session['user_id_session']
        customer_id = db.session.query(clsCustomers.customer_id_col).filter(clsCustomers.user_id_col==user_id).scalar()
        #get all services requested by that customer
        #all open/pending,fulfilled/closed
        from sqlalchemy import and_,or_,not_
        list_of_all_Pendings_ServiceRequestsrecords = db.session.query(clsServiceRequests).filter(and_(clsServiceRequests.customer_id_col==customer_id,clsServiceRequests.completion_status_col=="not completed")).all()

        list_of_all_Finished_ServiceRequestsrecords = db.session.query(clsServiceRequests).filter(and_(clsServiceRequests.customer_id_col==customer_id,clsServiceRequests.completion_status_col=="completed")).all()
        return render_template('customer_dir/my_services.html', 
                               customer_id=customer_id,
                               Pending_service_request=list_of_all_Pendings_ServiceRequestsrecords,
                               Finished_service_request=list_of_all_Finished_ServiceRequestsrecords,
                               list_of_all_accepted_denied_ServiceRequestsrecords=get_accepted_denied_service_request(customer_id))
    
    
@myApp.route('/open_edit_service_request_route/<int:service_request_id>', methods=['GET'])
def open_edit_service_request(service_request_id):
    if 'user_id_session' not in session and session['user_type_session'] != 'customer':
        message = "Please log in to proceed."
        return render_template('login.html', message=message)
    else:
        user_id = session['user_id_session']
        customer_id = db.session.query(clsCustomers.customer_id_col).filter(clsCustomers.user_id_col==user_id).scalar()
        from sqlalchemy import and_
        service_request_obj=db.session.query(clsServiceRequests).filter(and_(clsServiceRequests.service_request_id_col==service_request_id,
                                                                             clsServiceRequests.completion_status_col=="not completed")).all()
        return render_template('customer_dir/edit_my_service.html', 
                               customer_id=customer_id,
                               service_request_obj=service_request_obj)
    
    
@myApp.route('/edit_and_save_service_request_route/<int:service_request_id>', methods=['GET','POST'])
def edit_and_save_service_request(service_request_id):
    if 'user_id_session' not in session and session['user_type_session'] != 'customer':
        message = "Please log in to proceed."
        return render_template('login.html', message=message)
    else:
        if request.method == 'POST':
            new_date = request.form['inpDateOfServiceWanted']
            customer_remarks = request.form['inpCustomerRemarks']
            old_date=db.session.query(clsServiceRequests.date_of_service_wanted_col).filter(clsServiceRequests.service_request_id_col==service_request_id).scalar()

            if new_date >=old_date:

                db.session.query(clsServiceRequests).filter(clsServiceRequests.service_request_id_col == service_request_id).update(
                                                                {clsServiceRequests.date_of_service_wanted_col: new_date,
                                                                clsServiceRequests.customers_remarks_instruction_col: customer_remarks},
                                                                synchronize_session='fetch' 
                                                            )
                db.session.commit()
            
                return render_template('customer_dir/edit_my_service.html', msg="Service Request updated successfully.")
            else:
                return render_template('customer_dir/edit_my_service.html', msg="You can not select older dates.The date should be future date.")
        else:
            return render_template('customer_dir/edit_my_service.html',msg="Bad request")





@myApp.route('/cancel_service_request_route_route/<int:service_request_id>', methods=['GET'])
def delete_service_request(service_request_id):
    if 'user_id_session' not in session and session['user_type_session'] != 'customer':
        message = "Please log in to proceed."
        return render_template('login.html', message=message)
    else:
        user_id = session['user_id_session']
        customer_id = db.session.query(clsCustomers.customer_id_col).filter(clsCustomers.user_id_col==user_id).scalar()
        
        db.session.query(clsServiceRequests).filter(clsServiceRequests.service_request_id_col==service_request_id,
                                                    clsServiceRequests.customer_id_col==customer_id).delete()
        db.session.commit()
            
        return render_template('customer_dir/edit_my_service.html', msg="Service Request deleted successfully.")




@myApp.route('/open_review_rating_route/<int:service_request_id>', methods=['GET'])
def open_review_rating(service_request_id):
    if 'user_id_session' not in session and session['user_type_session'] != 'customer':
        message = "Please log in to proceed."
        return render_template('login.html', message=message)
    else:
        user_id=session['user_id_session']
        customer_id=db.session.query(clsCustomers.customer_id_col).filter(clsCustomers.user_id_col==user_id).scalar()
        service_request=db.session.query(clsServiceRequests).filter(clsServiceRequests.service_request_id_col==service_request_id,
                                                                    clsServiceRequests.customer_id_col==customer_id).first()
        return render_template('customer_dir/review_rating.html', service_request_id=service_request_id,
                               service_request=service_request)
    




@myApp.route('/review_rating_route/<int:service_request_id>', methods=['GET', 'POST'])
def review_rating(service_request_id):
    if 'user_id_session' not in session and session['user_type_session'] != 'customer':
        message = "Please log in to proceed."
        return render_template('login.html', message=message)
    else:

        
        user_id=session['user_id_session']
        customer_id=db.session.query(clsCustomers.customer_id_col).filter(clsCustomers.user_id_col==user_id).scalar()

        service_request = db.session.query(clsServiceRequests).filter(clsServiceRequests.service_request_id_col == service_request_id,
                                                                    clsServiceRequests.customer_id_col==customer_id).first()

        if request.method == 'POST':
            
            rating = request.form['inpRating']
            review = request.form['inpReview']
            
            
            t
            existing_review_rating=db.session.query(clsReviewRating).filter_by(service_request_id_col=service_request_id).first()
            
            if existing_review_rating:# If the review already exists then update it
                
                existing_review_rating.rating_col = rating
                existing_review_rating.review_text_col = review
                db.session.commit()
                return render_template('customer_dir/customer_home.html', message="Your review and rating have been successfully submitted")
            else:#If the review does not  exists already then create a new review
                new_review_rating = clsReviewRating(
                    service_request_id_col=service_request_id,
                    customer_id_col=customer_id,
                    service_professional_id_col=service_request.service_professional_id_col,
                    rating_col=rating,
                    review_text_col=review
                )
                db.session.add(new_review_rating)
                db.session.commit()

                return render_template('customer_dir/customer_home.html', message="Your review and rating have been successfully submitted")


def fun_get_all_service_request_in_ascending_date(service_professional_id):
    from sqlalchemy import asc
    service_request_result_list = db.session.query(clsServiceRequests).filter(clsServiceRequests.service_professional_id_col==service_professional_id).order_by(asc(clsServiceRequests.date_of_service_wanted_col)).all()
    return service_request_result_list




@myApp.route('/professional/dashboard_route',methods=['GET'])
def professional_dashboard():
    if 'user_id_session' not in session and session['user_type_session'] != 'service professional':
        message = "Please log in to proceed."
        return render_template('login.html', message=message)
    else:
        #if service professional is approved by admin then only he can see the incoming service request
        # Fetch the service_request to access its details
        user_id=session['user_id_session']
        service_professional_id=db.session.query(clsServiceProfessionals.serviceProfessional_id_col).filter(clsServiceProfessionals.user_id_col==user_id).scalar()
        is_approved=db.session.query(clsServiceProfessionals.is_approved_col).filter(clsServiceProfessionals.serviceProfessional_id_col==service_professional_id).scalar()
        if is_approved==True:
            return render_template('serviceProfessional_dir/serviceProfessional_dashboard_overview_html.html', 
                                   service_request_result_list=fun_get_all_service_request_in_ascending_date(service_professional_id))
        else:
            return render_template('serviceProfessional_dir/serviceProfessional_dashboard_overview_html.html',
                                    message="You are not approved by admin yet to view your order") 




@myApp.route('/incoming_service_request_route')
def service_request_order():
    if 'user_id_session' not in session and session['user_type_session'] != 'service professional':
        message = "Please log in to proceed."
        return render_template('login.html', message=message)
    else:
        #if service professional is approved by admin then only he can see the incoming service request
        # Fetch the service_request to access its details
        user_id=session['user_id_session']
        service_professional_id=db.session.query(clsServiceProfessionals.serviceProfessional_id_col).filter(clsServiceProfessionals.user_id_col==user_id).scalar()
        is_approved=db.session.query(clsServiceProfessionals.is_approved_col).filter(clsServiceProfessionals.serviceProfessional_id_col==service_professional_id).scalar()
        if is_approved==True:
            return render_template('serviceProfessional_dir/serviceProfessional_dashboard_overview_html.html', service_request_result_list=fun_get_all_service_request_in_ascending_date(service_professional_id))
        else:
            return render_template('serviceProfessional_dir/serviceProfessional_dashboard_overview_html.html', message="You are not approved by admin yet to view your order")




@myApp.route('/accept_service_request_route/<int:service_request_id>',methods=['GET'])
def accept_order(service_request_id):
    if 'user_id_session' not in session and session['user_type_session'] != 'service professional':
        message = "Please log in to proceed."
        return render_template('login.html', message=message)
    else:
        target_service_request = db.session.query(clsServiceRequests).filter(clsServiceRequests.service_request_id_col==service_request_id).first()
        #let us update the is_accepted_by_service_professional_col so as to notify the customer
        if target_service_request:
            #update
            target_service_request.is_accepted_by_service_professional_col =True
            db.session.commit()
            user_id=session['user_id_session']
            service_professional_id=db.session.query(clsServiceProfessionals.serviceProfessional_id_col).filter(clsServiceProfessionals.user_id_col==user_id).scalar()
       
            message="Service Request has been accepted by you."
            return render_template('serviceProfessional_dir/orders.html', message=message,service_request_result_list=fun_get_all_service_request_in_ascending_date(service_professional_id))
        else:
            user_id=session['user_id_session']
            service_professional_id=db.session.query(clsServiceProfessionals.serviceProfessional_id_col).filter(clsServiceProfessionals.user_id_col==user_id).scalar()
       
            message = "Service request does not exist."
            return render_template('serviceProfessional_dir/orders.html', message=message,service_request_result_list=fun_get_all_service_request_in_ascending_date(service_professional_id))





@myApp.route('/deny_service_request_route/<int:service_request_id>',methods=['GET'])
def deny_order(service_request_id):
    if 'user_id_session' not in session and session['user_type_session'] != 'service professional':
        message = "Please log in to proceed."
        return render_template('login.html', message=message)
    else:
        target_service_request = db.session.query(clsServiceRequests).filter(clsServiceRequests.service_request_id_col==service_request_id).first()
        
       
        #let us update the is_accepted_by_service_professional_col so as to notify the customer
        if target_service_request:
            #update
            target_service_request.is_accepted_by_service_professional_col =False
            db.session.commit()
            message="Service Request has been denied by you."
            user_id=session['user_id_session']
            service_professional_id=db.session.query(clsServiceProfessionals.serviceProfessional_id_col).filter(clsServiceProfessionals.user_id_col==user_id).scalar()
        
            return render_template('serviceProfessional_dir/orders.html', message=message,service_request_result_list=fun_get_all_service_request_in_ascending_date(service_professional_id))
        else:
            message = "Service request does not exist."
            user_id=session['user_id_session']
            service_professional_id=db.session.query(clsServiceProfessionals.serviceProfessional_id_col).filter(clsServiceProfessionals.user_id_col==user_id).scalar()
        
            return render_template('serviceProfessional_dir/orders.html',  message=message,service_request_result_list=fun_get_all_service_request_in_ascending_date(service_professional_id))        


    
    




@myApp.route('/complete_service_request_route/<int:service_request_id>',methods=['GET'])
def close_order_with_no_wage_theft(service_request_id):
    if 'user_id_session' not in session and session['user_type_session'] != 'service professional':
        message = "Please log in to proceed."
        return render_template('login.html', message=message)
    else:
        
        
        #update completion_status_col from pending to completed and wage_theft_count_col by 1
        target_service_request = db.session.query(clsServiceRequests).filter(clsServiceRequests.service_request_id_col==service_request_id).first()
        if target_service_request:
            #update
            target_service_request.completion_status_col = "completed"
            
            db.session.commit()
            
            message="Order has been closed."
            service_professional_id = db.session.query(clsServiceRequests.service_professional_id_col).filter(clsServiceRequests.service_request_id_col==service_request_id).scalar()
            return render_template('serviceProfessional_dir/orders.html', 
                                   message=message,
                                   service_request_result_list=fun_get_all_service_request_in_ascending_date(service_professional_id))
        else:
            message = "Service request does not exist."
            service_professional_id = db.session.query(clsServiceRequests.service_professional_id_col).filter(clsServiceRequests.service_request_id_col==service_request_id).scalar()
            
            return render_template('serviceProfessional_dir/orders.html', 
                                   message=message,
                                   service_request_result_list=fun_get_all_service_request_in_ascending_date(service_professional_id))



@myApp.route('/make_wage_theft_route/<int:service_request_id>',methods=['GET'])
def make_wage_theft(service_request_id):
    if 'user_id_session' not in session and session['user_type_session'] != 'service professional':
        message = "Please log in to proceed."
        return render_template('login.html', message=message)
    else:
        
        
        #update completion_status_col from pending to completed and wage_theft_count_col by 1
        target_service_request = db.session.query(clsServiceRequests).filter(clsServiceRequests.service_request_id_col==service_request_id).first()
        if target_service_request:
            #update
            target_service_request.customers_table.wage_theft_count_col = target_service_request.customers_table.wage_theft_count_col +1
            db.session.commit()
            message="customer was marked as doing wage theft."
            service_professional_id = db.session.query(clsServiceRequests.service_professional_id_col).filter(clsServiceRequests.service_request_id_col==service_request_id).scalar()
            return render_template('serviceProfessional_dir/orders.html', 
                                   message=message,
                                   service_request_result_list=fun_get_all_service_request_in_ascending_date(service_professional_id))
        else:
            message = "Service request does not exist."
            service_professional_id = db.session.query(clsServiceRequests.service_professional_id_col).filter(clsServiceRequests.service_request_id_col==service_request_id).scalar()
        
            return render_template('serviceProfessional_dir/orders.html', 
                                   message=message,
                                   service_request_result_list=fun_get_all_service_request_in_ascending_date(service_professional_id))






@myApp.route('/donot_make_wage_theft_route/<int:service_request_id>',methods=['GET'])
def donot_make_wage_theft(service_request_id):
    if 'user_id_session' not in session and session['user_type_session'] != 'service professional':
        message = "Please log in to proceed."
        return render_template('login.html', message=message)
    else:
        
        
        #update completion_status_col from pending to completed and wage_theft_count_col by 1
        target_service_request = db.session.query(clsServiceRequests).filter(clsServiceRequests.service_request_id_col==service_request_id).first()
        if target_service_request:
            #update
            target_service_request.customers_table.wage_theft_count_col = target_service_request.customers_table.wage_theft_count_col +0
            db.session.commit()
            message="You marked customer as honest."
            service_professional_id = db.session.query(clsServiceRequests.service_professional_id_col).filter(clsServiceRequests.service_request_id_col==service_request_id).scalar()
            return render_template('serviceProfessional_dir/orders.html', 
                                   message=message,
                                   service_request_result_list=fun_get_all_service_request_in_ascending_date(service_professional_id))
        else:
            message = "Service request does not exist."
            service_professional_id = db.session.query(clsServiceRequests.service_professional_id_col).filter(clsServiceRequests.service_request_id_col==service_request_id).scalar()
        
            return render_template('serviceProfessional_dir/orders.html', 
                                   message=message,
                                   service_request_result_list=fun_get_all_service_request_in_ascending_date(service_professional_id))



