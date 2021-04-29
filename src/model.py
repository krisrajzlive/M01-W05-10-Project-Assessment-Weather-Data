# Imports Database class from the project to provide basic functionality for database access
from database import Database
# Imports ObjectId to convert to the correct format before querying in the db
from bson.objectid import ObjectId
from datetime import datetime

# User document contains username (String), email (String), and role (String) fields
# Only admin users are authorized to access (r/w) this class
class UserModel:
    USER_COLLECTION = 'users'

    def __init__(self):
        self._db = Database()
        self._latest_error = ''
    
    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error

   # Returns name of the class
    @property
    def whoami(self):
        return (type(self).__name__)
    
    # Since username should be unique in users collection, this provides a way to fetch the user document based on the username
    def getuser_by_username(self, username, execusername):
        self._latest_error = ''
        
        if username == None or execusername == None:
            self.latest_error = "username or executing username can't be blank"
        
        userrole = self.get_userrole_by_username(execusername, execusername)

        if userrole == None or Authorization.isvalid_admin_operation(self.whoami, userrole, 'read') == False:
            self._latest_error = 'The user {0} is not authorized to access the method getuser_by_username'.format(execusername)
            return 
        
        key = {'username': username}
        
        return self.__find(key)

    # Finds user document based on the unique auto-generated MongoDB object id
    def getuser_by_object_id(self, obj_id, username, execusername):
        self._latest_error = ''
        if username == None:
            self.latest_error = "username can't be blank"

        userrole = Utils().get_userrole(execusername, execusername)

        if userrole == None or Authorization.isvalid_admin_operation(self.whoami, userrole, 'read') == False:
            self._latest_error = 'The user {0} is not authorized to access the method getuser_by_object_id'.format(execusername)
            return 

        key = {'_id': ObjectId(obj_id)}
        return self.__find(key)

    # Returns user role for the given username
    # no access rights validation is required
    def get_userrole_by_username(self, username, execusername):
        self._latest_error = ''

        if username == None:
            self._latest_error = "username can't be blank"
        
        execuserdoc = self.__find({'username': execusername})
        userdoc = self.__find({'username': username})
        
        if userdoc != None and execuserdoc != None:
            userrole = userdoc['role']
            if Authorization.isvalid_admin_operation(self.whoami, execuserdoc['role'], 'read') == True:
                return userrole
            else:
                self._latest_error = 'The user {0} is not authorized to access the method insert'.format(execusername)
                return
        else:
            self._latest_error = 'User {0} not found '.format(username)

    # Returns user role for the given username
    # No access rights is required
    def get_userrole_by_userdocument(self, userdocument):
        return userdocument['role']

    # Private function (starting with __) to be used as the base for all find function
    # no access rights validation is required
    def __find(self, key):
        user_document = self._db.get_single_data(UserModel.USER_COLLECTION, key)
        return user_document

    # This first checks if a user already exists with that username. If it does, it populates latest_error and returns -1
    # If a user doesn't already exist, it'll insert a new document and return the same to the caller
    def insert(self, username, email, role, execusername):
        self._latest_error = ''
        if username == None or email == None or role == None or execusername == None:
            self.latest_error = "username or email or role or executing username can't be blank"
        
        userrole = self.get_userrole_by_username(execusername, execusername)

        if userrole == None or Authorization.isvalid_admin_operation(self.whoami, userrole, 'write') == False:
            self._latest_error = 'The user {0} is not authorized to access the method'.format(execusername)
            return 

        user_document = self.getuser_by_username(username, execusername)

        if (user_document != None):
            self._latest_error = f'Username {username} already exists'
            return -1
        
        user_data = {'username': username, 'email': email, 'role': role}
        user_obj_id = self._db.insert_single_data(UserModel.USER_COLLECTION, user_data)
        return self.getuser_by_object_id(user_obj_id, username, execusername)

# UserAccess document contains username and devices the user has access to
class UserAccessModel:
    USERACCESS_COLLECTION = 'useraccess'

    def __init__(self):
        self._db = Database()
        self._latest_error = ''

    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error

    # Returns name of the class
    @property
    def whoami(self):
        return (type(self).__name__)

    # Finds user document based on the unique auto-generated MongoDB object id
    def getuseraccess_by_object_id(self, obj_id, userrole):
        Authorization.isvalid_admin_operation(self.whoami, userrole, 'read')
        key = {'_id': ObjectId(obj_id)}
        return self.__find(key, userrole)

    # Find authorised devices by username
    def find_authorized_deviceids_by_username(self, username):
        #Authorization.isvalid(self.whoami, role, 'read')
        query = {'username': username}
        documents = self._db.get_single_data_byquery(UserAccessModel.USERACCESS_COLLECTION, query)
        deviceids = []
        for doc in documents:
            deviceids.append(doc['device_id'])
        return deviceids;

    # The find user access method returns user access r/rw
    def get_user_access(self, username, deviceid):
        if len(username) == 0 or len(deviceid) == 0:
            raise Exception("username or deviceid can't be blank")

        query = {"username": username, "device_id": deviceid}
        useraccess_document = self._db.get_single_data_byquery(UserAccessModel.USERACCESS_COLLECTION, query)

        if useraccess_document.count() > 0:
            for doc in useraccess_document:
                return doc["access"]
        #else:
           #raise Exception("Can't find user's role")

    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key, userrole):
        # Authorization.isvalid(self.whoami, userrole)
        user_document = self._db.get_single_data(UserAccessModel.USERACCESS_COLLECTION, key)
        return user_document

    # Private function (starting with __) to be used as the base for all find functions
    def __findmultiple(self, key, userrole):
        # Authorization.isvalid(self.whoami, userrole)
        user_document = self._db.get_multiple_data(UserAccessModel.USERACCESS_COLLECTION, key)
        return user_document

    # This first checks if a user already exists with that username. If it does, it populates latest_error and returns -1
    # If a user doesn't already exist, it'll insert a new document and return the same to the caller
    def insert(self, username, device_id, access, userrole):
        Authorization.isvalid_admin_operation(self.whoami, userrole, 'write')
        self._latest_error = ''
        #user_document = self.getuser_by_username(username, userrole)
        #if (user_document):
        #    self._latest_error = f'Username {username} already exists'
        #    return -1

        useraccess_data = {'username': username, 'device_id': device_id, 'access': access}
        useraccess_obj_id = self._db.insert_single_data(UserAccessModel.USERACCESS_COLLECTION, useraccess_data)
        return self.getuseraccess_by_object_id(useraccess_obj_id, userrole)

# Device document contains device_id (String), desc (String), type (String - temperature/humidity) and manufacturer (String) fields
# Any users who has been granted access can perform the allowed operation (read or read/write)
class DeviceModel:
    DEVICE_COLLECTION = 'devices'

    def __init__(self):
        self._db = Database()
        self._latest_error = ''

    # Returns name of the class
    @property
    def whoami(self):
        return (type(self).__name__)
    
    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error
    
    # Since device id should be unique in devices collection, this provides a way to fetch the device document based on the device id
    #def find_by_device_id(self, device_id, role):
    def find_by_device_id(self, username, role, device_id):
        #Authorization.isvalid_admin_operation(self.whoami, role, 'read')
        Authorization.isvalidoperation(username, device_id, 'read')
        key = {'device_id': device_id}
        return self.__find(key, role)
 
    # Finds a document based on the unique auto-generated MongoDB object id 
    def find_by_object_id(self, obj_id, role):
        Authorization.isvalid_admin_operation(self.whoami, role, 'read')
        key = {'_id': ObjectId(obj_id)}
        return self.__find(key, role)
    
    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key, role):
        Authorization.isvalid_admin_operation(self.whoami, role, 'read')
        device_document = self._db.get_single_data(DeviceModel.DEVICE_COLLECTION, key)
        return device_document
    
    # This first checks if a device already exists with that device id. If it does, it populates latest_error and returns -1
    # If a device doesn't already exist, it'll insert a new document and return the same to the caller
    def insert(self, device_id, desc, type, manufacturer, username):
        #Authorization.isvalid_admin_operation(self.whoami, role, 'write')
        Authorization.isvalidoperation(username, device_id,"RW")
        self._latest_error = ''
        role = Utils().get_userrole(username, username)
        device_document = self.find_by_device_id(username, role, device_id)
        if (device_document):
            self._latest_error = f'Device id {0} already exists'.format(device_id)
            return 
        
        device_data = {'device_id': device_id, 'desc': desc, 'type': type, 'manufacturer': manufacturer}
        device_obj_id = self._db.insert_single_data(DeviceModel.DEVICE_COLLECTION, device_data)
        return self.find_by_object_id(device_obj_id, role)

# Weather data document contains device_id (String), value (Integer), and timestamp (Date) fields
class WeatherDataModel:
    WEATHER_DATA_COLLECTION = 'weather_data'

    def __init__(self):
        self._db = Database()
        self._latest_error = ''

    # Returns name of the class
    @property
    def whoami(self):
        return (type(self).__name__)
    
    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error
    
    # Since device id and timestamp should be unique in weather_data collection, this provides a way to fetch the data document based on the device id and timestamp
    def find_by_device_id_and_timestamp(self, device_id, timestamp, role):
        #Authorization.isvalid(self.whoami, role)
        key = {'device_id': device_id, 'timestamp': timestamp}
        return self.__find(key, role)
    
    # Finds a document based on the unique auto-generated MongoDB object id 
    def find_by_object_id(self, obj_id, role):
        #Authorization.isvalid(self.whoami, role)
        key = {'_id': ObjectId(obj_id)}
        return self.__find(key, role)
    
    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key, role):
        #Authorization.isvalid(self.whoami, role)
        wdata_document = self._db.get_single_data(WeatherDataModel.WEATHER_DATA_COLLECTION, key)
        return wdata_document
    
    # This first checks if a data item already exists at a particular timestamp for a device id. If it does, it populates latest_error and returns -1.
    # If it doesn't already exist, it'll insert a new document and return the same to the caller
    def insert(self, device_id, value, timestamp, username):
        #Authorization.isvalidweatherinsert(username, device_id)
        Authorization.isvalidoperation(username, device_id,"RW")
        self._latest_error = ''
        role = Utils().get_userrole(username, username)

        wdata_document = self.find_by_device_id_and_timestamp(device_id, timestamp, role)
        
        if (wdata_document):
            self._latest_error = f'Data for timestamp {timestamp} for device id {device_id} already exists'
            return -1
        
        weather_data = {'device_id': device_id, 'value': value, 'timestamp': timestamp}
        wdata_obj_id = self._db.insert_single_data(WeatherDataModel.WEATHER_DATA_COLLECTION, weather_data)
        return self.find_by_object_id(wdata_obj_id, role)

# DailyReportsModel document contains average, minimum, maximum deviceid and date fields
class DailyReportsModel:
    DAILYREPORTS_COLLECTION = 'dailyreports'

    def __init__(self):
        self._db = Database()
        self._last_error = ''

    # Returns name of the class
    @property
    def whoami(self):
        return (type(self).__name__)

    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error

    def __default_aggregate_report(self, startdate, enddate, role, deviceids = None):
        return(self._db.get_aggregate_weather_data(startdate, enddate, role, deviceids))

    def __admin_aggregate_report(self, startdate, enddate, role, deviceids = None):
        return(self._db.get_admin_aggregate_weather_data(startdate, enddate, role, deviceids))
    
    def donotuse1print_default_aggregate_report(self, startdate, enddate, userid, deviceids = None):
        Authorization.isvalid(self.whoami, role, 'read')

        print('Printing report from {0} to {1}'.format(startdate.strftime("%d-%m-%Y"), enddate.strftime("%d-%m-%Y")))
        
        for doc in self.__default_aggregate_report(startdate, enddate, role, deviceids):
            print('Device ID: {0}, Day: {1}, Average: {2}, Minimum: {3}, Maximum: {4}'.format(doc['deviceid'], self.__formatdate(doc['day']), round(doc['Average']), round(doc['Minimum']), round(doc['Maximum'])))

    def donotuse2print_admin_aggregate_report(self, startdate, enddate, role, deviceids = None):
        Authorization.isvalid(self.whoami, role, 'read')

        print('Printing report from {0} to {1}'.format(startdate.strftime("%d-%m-%Y"), enddate.strftime("%d-%m-%Y")))
        
        for doc in self.__admin_aggregate_report(startdate, enddate, role, deviceids):
            print('Device ID: {0}, Day: {1}, Average: {2}, Minimum: {3}, Maximum: {4}'.format(doc['deviceid'], self.__formatdate(doc['day']), round(doc['Average']), round(doc['Minimum']), round(doc['Maximum'])))
    
    # the report prints aggredate weather data of the given user for the devices they have access to
    # admin can see the report for all the devices hence deviceids are optional
    def print_aggregate_report(self, startdate, enddate, username, role = None, deviceids = None):
        
        utils = Utils()

        if len(username) == 0:
            raise Exception("Aggregate Report: username can't be blank")
        
        if startdate == None or enddate == None:
            raise Exception("Aggregate Report: Date range is required to run the report")

        # determine the role, admin has access to all the device data
        # default users have access only specific device data
        if role == None and len(username) > 0:
            role =  utils.get_userrole(username, username)

        if utils.truncateandcapitalize(role) == 'ADMIN':
             print('Printing report from {0} to {1}'.format(startdate.strftime("%d-%m-%Y"), enddate.strftime("%d-%m-%Y")))
             for doc in self.__admin_aggregate_report(startdate, enddate, role, deviceids):
                 print('Device ID: {0}, Day: {1}, Average: {2}, Minimum: {3}, Maximum: {4}'.format(doc['deviceid'], self.__formatdate(doc['day']), round(doc['Average']), round(doc['Minimum']), round(doc['Maximum'])))
            
        if deviceids == None:
            deviceids = utils.get_authorized_deviceids(username)
  
    def __formatdate(self, datelist):
        tempdate = datetime(datelist[0], datelist[1], datelist[2])
        return str(tempdate.strftime("%d-%m-%Y"))

# AppArgument represents commandline arguments
class AppArgument:
    def __init__(self,args):
        self.__latest_error = ''
        self.appArgs = args

    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self.__latest_error

    #first command line parameter
    @property
    def username(self):
        if len(self.appArgs) == 2:
            return self.appArgs[1]
        else:
            self.__latest_error = "username parameter can't be blank"
            print(self.latest_error)
            return

    @property
    def arglength(self):
        return len(self.appArgs)

#Authorization represents whether an user is authorized to perform certain operation
class Authorization:
    def __init__(self):
        self._latest_error = ''

    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error

    # This method validates whether a specific user is authorized to perform a specific operation such as read /write operation on a specific model
    @staticmethod
    def isvalid_admin_operation(model, role, operation):

        if model == None or len(model) == 0:
            raise Exception("Model can't be blank")
        else:
            model = Utils.truncateandcapitalize(model)

        if role == None or len(role) == 0:
            raise Exception("Role can't be blank")
        else:
            role = Utils.truncateandcapitalize(role)

        if operation == None or len(operation) == 0:
            raise Exception("Operation can't be blank")
        else:
            operation = Utils.truncateandcapitalize(operation)

        # Only admin can perform any operation in USERMODEL
        if model == 'USERMODEL' and role != 'ADMIN':
            return False
        # Only admin can perform any operation in USERACCESSMODEL
        elif model == 'USERACCESSMODEL' and role != 'ADMIN':
            raise Exception('Usertype ' + role + ' is not authorized to perform ' + operation + ' on ' + model)
        elif model == 'DEVICEMODEL' and role == 'ADMIN':
            raise Exception('Usertype ' + role + ' is not authorized to perform ' + operation + ' on ' + model)
      
        if role == 'ADMIN':
            return True
        else:
            return False

    # isvalidoperation metho is used to determine whether users have appropriate access to the device
    @staticmethod
    def isvalidweatherinsert(username, deviceid):

        if len(username) == 0 or len(deviceid) == 0:
            raise Exception("Username or deviceid can't be blank")
        
        role = Utils().get_userrole(username, username)

        if Utils.truncateandcapitalize(role) == 'ADMIN':
            return True
        
        useraccess = UserAccessModel().get_user_access(username, deviceid)

        if useraccess != None and Utils.truncateandcapitalize(useraccess) == 'RW':
            return True
        else:
            raise Exception('The user {0} is not authorised to insert data for the device {1}'.format(username, deviceid))

    @staticmethod
    def isvaliddeviceinsert(username, deviceid):
        if len(username) == 0 or len(deviceid) == 0:
            raise Exception("Username or deviceid can't be blank")
        
        role = Utils().get_userrole(username, username)

        if Utils.truncateandcapitalize(role) == 'ADMIN':
            return True
        
        useraccess = UserAccessModel().get_user_access(username, deviceid)

        if useraccess != None and Utils.truncateandcapitalize(useraccess) == 'RW':
            return True
        else:
            raise Exception('The user {0} is not authorised to insert data for the device {1}'.format(username, deviceid))

    # isvalidoperation metho is used to determine whether users have appropriate access to the device
    @staticmethod
    def isvalidoperation(username, deviceid, accesstype):

        if len(username) == 0 or len(deviceid) == 0:
            raise Exception("Username or deviceid can't be blank")
        
        role = Utils().get_userrole(username, username)

        if Utils.truncateandcapitalize(role) == 'ADMIN':
            return True
        
        useraccess = UserAccessModel().get_user_access(username, deviceid)

        if useraccess != None and Utils.truncateandcapitalize(useraccess) == accesstype:
            return True
        else:
            raise Exception('The user {0} is not authorised to perform the operation for the device {1}'.format(username, deviceid))

# This class contains methods redundantly used
class Utils:
    def __init__(self):
        self._latest_error = ''

    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error

    # Function truncateandcapitalize to remove leading and trailing spaces and convert parameter to uppercase
    @staticmethod
    def truncateandcapitalize(arg):
        if arg != None:
            return arg.strip().upper()

    # Function get_userrole returns role for the given username
    def get_userrole(self, username, execusername):
        user = UserModel()
        return user.get_userrole_by_username(username, execusername)

    # Function get_authorized_deviceids returns device ids as list for the given username
    def get_authorized_deviceids(self, username):
        useraccess = UserAccessModel()
        return useraccess.find_authorized_deviceids_by_username(username)
    
    # The method print_error is used to print error messages if any
    @staticmethod
    def print_error(errormessage):
        if errormessage != None:
            print(errormessage)
