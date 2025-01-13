from flask import Flask
 
import os


project_current_dir=os.path.abspath(os.path.dirname(__file__))#__file__ is a special variable that holds the path of the current Python file. 
#If this code is inside a Python file, __file__ returns the file's relative path.os.path.dirname(__file__): This function gets the directory name of the file path. 
# For example, if __file__ is /path/to/project/file.py, then os.path.dirname(__file__) will return /path/to/project.Now the os.path.abspath(...): This function converts a relative path to an absolute path. 
# It ensures that the path is complete, making it useful when working with file paths in any environment.

myApp=Flask(__name__)#Flask() is a class,__name__: This is a special built-in variable in Python
#  that represents the name of the current module. When a Python script is 
# run, __name__ is set to "__main__" if the script is being executed 
# directly. If the script is being imported as a module in another script,
#  __name__ will be set to the name of the module.myApp: This is a variable that is 
# being assigned an instance of the Flask class. It represents the 
# Flask application itself. 


myApp.config['SQLALCHEMY_DATABASE_URI']="sqlite:///"+os.path.join(project_current_dir,'myDatabase.sqlite3')#it tells SQLAlchemy where to find or create the database file.
#myApp.config['SQLALCHEMY_DATABASE_URI']: This sets the configuration value for SQLALCHEMY_DATABASE_URI in myApp. SQLAlchemy uses this URI to connect to the specified database.
#"sqlite:///": This part specifies that the database is using SQLite.The three slashes (///) indicate an absolute path to the database file.
#os.path.join(project_current_dir, 'myDatabase.sqlite3'): This joins the project_current_dir (the absolute path to the directory containing your current file) with 'myDatabase.sqlite3', creating a path to where the SQLite database file will be stored within the project directory.

myApp.secret_key = 'any-arbitrary-secret-key'#this is needed for working of session

from backend_dir.model import db
db.init_app(myApp)#db.init_app(...): This method is used to link the db instance of SQLAlchemy, with the Flask app myApp. 

myApp.app_context().push()



from backend_dir.controllers import *
if(__name__=="__main__"):
   
    db.create_all() #db.create_all() checks each model you've defined and generates a corresponding table in the database, if it doesn’t already exist.
    # In the  models.py , classes  represent database tables
    
    myApp.run(debug=True,use_reloader=True)

  