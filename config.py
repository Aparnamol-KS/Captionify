import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "gh543548fyt6hjg98uh")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'site.db') 
    SQLALCHEMY_TRACK_MODIFICATIONS = False  
