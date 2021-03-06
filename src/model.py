# Imports Database class from the project to provide basic functionality for database access
from database import Database, AggregateReportParameterError
# Imports ObjectId to convert to the correct format before querying in the db
from bson.objectid import ObjectId
from datetime import datetime

# User document contains username, email, and role  fields
# Only admin users are authorized to access (r/w) this class
class UserModel:
    USER_COLLECTION = 'users'

    def __init__(self):
        self._db = Database()
        self._latest_error = ''
        self.username = ''
        self.emailid = ''
        self.role = ''
    
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

        if username == None or execusername == None:
            self.latest_error = "username or executing username can't be blank"

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

        if username == None or execusername == None:
            self._latest_error = "username or executing username can't be blank"
        
        execuserdoc = self.__find({'username': execusername})
        userdoc = self.__find({'username': username})
        
        if userdoc != None and execuserdoc != None:
            userrole = userdoc['role']
            return userrole
        else:
            self._latest_error = 'User {0} not found'.format(username)

    # Returns user role for the given username
    # No access rights is required
    def get_userrole_by_userdocument(self, userdocument):
        self._latest_error = ''
        if userdocument:
            return userdocument['role']
        else:
            self._latest_error = 'user document is blank'

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
            self._latest_error = "username or email or role or executing username can't be blank"
        
        userrole = self.get_userrole_by_username(execusername, execusername)

        if userrole == None or Authorization.isvalid_admin_operation(self.whoami, userrole, 'write') == False:
            self._latest_error = 'The user {0} is not authorized to insert user'.format(execusername)
            return 

        user_document = self.getuser_by_username(username, execusername)

        if (user_document != None):
            self._latest_error = f'Username {username} already exists'
            return
        
        user_data = {'username': username, 'email': email, 'role': role}
        user_obj_id = self._db.insert_single_data(UserModel.USER_COLLECTION, user_data)
        return self.getuser_by_object_id(user_obj_id, username, execusername)

# UserAccess document contains username and devices the user has access to
# only admin users are authorized to access this class
class UserAccessModel:
    USERACCESS_COLLECTION = 'useraccess'

    def __init__(self):
        self._db = Database()
        self._latest_error = ''
        self.username = ''
        self.device_id = ''
        self.access = ''

    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error

    # Returns name of the class
    @property
    def whoami(self):
        return (type(self).__name__)

    # Finds user document based on the unique auto-generated MongoDB object id
    def getuseraccess_by_object_id(self, obj_id, execusername):
        self._latest_error = ''

        if object_id == None or execusername == None:
            self._latest_error = "object_id or executing username can't be blank"
            return
        
        execuserrole = Utils.get_userrole(execusername, execusername)

        if execuserrole == None or Authorization.isvalid_admin_operation(self.whoami, execuserrole, 'read') == False:
            self._latest_error = "The user {0} is not authorized to access the method getuseraccess_by_object_id".format(execusername)
            return
        
        key = {'_id': ObjectId(obj_id)}
        return self.__find(key)

    # Find authorised devices by username
    def find_authorized_deviceids_by_username(self, username, execusername):
        self._latest_error = ''
        
        if username == None or execusername == None:
            self._latest_error = "Username or executing username can't be blank"
            return
        
        execuserrole = Utils().get_userrole(username, execusername)
        if execuserrole == None:
            self._latest_error = "The user {0} is not authorized to access the method find_authorized_deviceids_by_username".format(execusername)
            return

        query = {'username': username}
        documents = self._db.get_single_data_byquery(UserAccessModel.USERACCESS_COLLECTION, query)
        deviceids = []

        for doc in documents:
            deviceids.append(doc['device_id'])
        return deviceids;

    # The find user access method returns user access r/rw
    def get_user_access(self, username, deviceid, execusername):
        self._latest_error = ''

        if username == None or deviceid == None or execusername == None:
            self._latest_error = "Username or deviceid or executing username can't be blank"
            return

        execuserrole = Utils().get_userrole(execusername, execusername)

        if execuserrole == None:
            self._latest_error = "The user {0} is not authorized to access the method get_user_access".format(execusername)
            return

        query = {"username": username, "device_id": deviceid}
        useraccess_document = self._db.get_single_data_byquery(UserAccessModel.USERACCESS_COLLECTION, query)

        if useraccess_document.count() > 0:
            for doc in useraccess_document:
                return doc["access"]

    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key):
        user_document = self._db.get_single_data(UserAccessModel.USERACCESS_COLLECTION, key)
        return user_document

    # Private function (starting with __) to be used as the base for all find functions
    def __findmultiple(self, key):
        user_document = self._db.get_multiple_data(UserAccessModel.USERACCESS_COLLECTION, key)
        return user_document

    # This first checks if a user already exists with that username. If it does, it populates latest_error and returns -1
    # If a user doesn't already exist, it'll insert a new document and return the same to the caller
    def insert(self, username, device_id, access, execusername):
        self._latest_error = ''
        
        if username == None or device_id == None or access == None or execusername == None:
            self._latest_error = 'one or more of the parameter(s) are blank'
            return

        execuserrole = UserModel().get_userrole_by_username(execusername, execusername)
        userrole = UserModel().get_userrole_by_username(username, execusername)

        if execuserrole == None or Authorization.isvalid_admin_operation(self.whoami, execuserrole, 'write') == False:
            self._latest_error = 'The user {0} is not authorized to insert useraccess'.format(execusername)
            return

        useraccess_document = self.get_user_access(username, device_id, execusername)

        if (useraccess_document != None):
            self._latest_error = 'User access for user {0} on device {1} exists already'.format(username, device_id)
            return

        useraccess_data = {'username': username, 'device_id': device_id, 'access': access}
        useraccess_obj_id = self._db.insert_single_data(UserAccessModel.USERACCESS_COLLECTION, useraccess_data)
        return self.getuseraccess_by_object_id(useraccess_obj_id, execusername)

# Device document contains device_id (String), desc (String), type (String - temperature/humidity) and manufacturer (String) fields
# Any users who has been granted access to the device can perform the allowed operation (read or read/write)
class DeviceModel:
    DEVICE_COLLECTION = 'devices'

    def __init__(self):
        self._db = Database()
        self._latest_error = ''
        #self.device_id = ''
        #self.desc = ''
        #self.type = ''
        #self.manufacturer = ''

    # Returns name of the class
    @property
    def whoami(self):
        return (type(self).__name__)
    
    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error
    
    # Since device id should be unique in devices collection, this provides a way to fetch the device document based on the device id
    def find_by_device_id(self, username, role, device_id):
        self._latest_error = ''
        key = {'device_id': device_id}
        return self.__find(key, role)
 
    # Finds a document based on the unique auto-generated MongoDB object id 
    def find_by_object_id(self, obj_id, role):
        self._latest_error = ''
        key = {'_id': ObjectId(obj_id)}
        return self.__find(key, role)
    
    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key, role):
        device_document = self._db.get_single_data(DeviceModel.DEVICE_COLLECTION, key)
        return device_document
    
    # This first checks if a device already exists with that device id. If it does, it populates latest_error and returns -1
    # If a device doesn't already exist, it'll insert a new document and return the same to the caller
    def insert(self, device_id, desc, devicetype, manufacturer, execusername):
        self._latest_error = ''
        
        if device_id == None or desc == None or devicetype == None or manufacturer == None or execusername == None:
            self._latest_error = "One or more paramters can't be blank"
            return
        
        execuserrole = Utils().get_userrole(execusername, execusername)
       
        if execuserrole == None:
            self._latest_error = "The user {0} can't create the device".format(execusername)
            return

        if Authorization().isvalidinsert(execusername, execuserrole, device_id, "RW", "create device data") == False:
            self._latest_error = "The user {0} can't create the device".format(execusername)
            return

        device_document = self.find_by_device_id(execusername, execuserrole, device_id)
        if (device_document):
            self._latest_error = 'Device id {0} already exists'.format(device_id)
            return 
        
        device_data = {'device_id': device_id, 'desc': desc, 'type': devicetype, 'manufacturer': manufacturer}
        device_obj_id = self._db.insert_single_data(DeviceModel.DEVICE_COLLECTION, device_data)
        return self.find_by_object_id(device_obj_id, execuserrole)

# Weather data document contains device_id (String), value (Integer), and timestamp (Date) fields
class WeatherDataModel:
    WEATHER_DATA_COLLECTION = 'weather_data'

    def __init__(self):
        self._db = Database()
        self._latest_error = ''
        self.device_id = ''
        self.value = 0
        self.timestamp = ''

    # Returns name of the class
    @property
    def whoami(self):
        return (type(self).__name__)
    
    # Latest error is used to store the error string in case an issue. It's reset at the beginning of a new function call
    @property
    def latest_error(self):
        return self._latest_error
    
    # Since device id and timestamp should be unique in weather_data collection, this provides a way to fetch the data document based on the device id and timestamp
    def find_by_device_id_and_timestamp(self, device_id, timestamp):
        #Authorization.isvalid(self.whoami, role)
        key = {'device_id': device_id, 'timestamp': timestamp}
        return self.__find(key)
    
    # Finds a document based on the unique auto-generated MongoDB object id 
    def find_by_object_id(self, obj_id):
        #Authorization.isvalid(self.whoami, role)
        key = {'_id': ObjectId(obj_id)}
        return self.__find(key)
    
    # Private function (starting with __) to be used as the base for all find functions
    def __find(self, key):
        #Authorization.isvalid(self.whoami, role)
        wdata_document = self._db.get_single_data(WeatherDataModel.WEATHER_DATA_COLLECTION, key)
        return wdata_document
    
    # This first checks if a data item already exists. If it does, it populates latest_error and returns -1.
    # If it doesn't already exist, it'll insert a new document and return the same to the caller
    def insert(self, device_id, value, timestamp, execusername):
        self._latest_error = ''

        if device_id == None or value == None or timestamp == None or execusername == None:
            self._latest_error = "One or more parameters are blank"
            return
        
        execuserrole = Utils().get_userrole(execusername, execusername)
        
        if Authorization().isvalidinsert(execusername, execuserrole, device_id, "RW", "insert weather data") == False:
            self._latest_error = "The user {0} can't insert weather data".format(execusername)
            return

        wdata_document = self.find_by_device_id_and_timestamp(device_id, timestamp)
        
        if (wdata_document):
            self._latest_error = f'Weather Data for for device id {device_id} already exists'
            return
        
        weather_data = {'device_id': device_id, 'value': value, 'timestamp': timestamp}
        wdata_obj_id = self._db.insert_single_data(WeatherDataModel.WEATHER_DATA_COLLECTION, weather_data)
        return self.find_by_object_id(wdata_obj_id)

# DailyReportsModel document contains average, minimum, maximum deviceid and date fields
class DailyReportsModel:
    DAILYREPORTS_COLLECTION = 'dailyreports'

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

    # called when the application is run as default user, deviceids are authorized device ids that the default users has access to
    def __default_aggregate_report(self, startdate, enddate, role, deviceids = None):
        try:
            return(self._db.get_aggregate_weather_data(startdate, enddate, role, deviceids))
        except AggregateReportParameterError:
            self._latest_error = 'Invalid parameter passed to the report'
            Utils.print_error(self.latest_error)

    # called when the application is run as admin
    def __admin_aggregate_report(self, startdate, enddate, role, deviceids = None):
        try:
            return(self._db.get_admin_aggregate_weather_data(startdate, enddate, role, deviceids))
        except AggregateReportParameterError:
            self._latest_error = 'Invalid parameter passed to the report'
            Utils.print_error(self.latest_error)
    
    # the report prints aggredate weather data of the given user for the devices they have access to
    # admin can see the report for all the devices hence deviceids are optional but it is required for default users though being initialized as None
    def print_aggregate_report(self, startdate, enddate, execusername, deviceids = None):
        self._latest_error = ''
        utils = Utils()

        if execusername == None:
            self._latest_error = "Aggregate Report: username can't be blank"
            return

        if startdate == None or enddate == None:
            self._latest_error = "Aggregate Report: Date range is required to run the report"
            return

        # determine the role, admin has access to all the device data
        # default users have access only specific device data
        role = utils.get_userrole(execusername, execusername)

        if role == None:
            self._latest_error = "The non-existent user {0} can't access the method print_aggregate_report".format(execusername)
            return

        if utils.truncateandcapitalize(role) == 'ADMIN':
            #admin has access to all devices
            reportdocs = self.__admin_aggregate_report(startdate, enddate, role, deviceids)
        else: 
            # determine default user's devices
            authdeviceids = utils.get_authorized_deviceids(execusername, execusername)
            devlist = []

            if deviceids != None and authdeviceids != None:
                devs = set(deviceids)
                authdevs = set(authdeviceids)
                devlist = list(devs.intersection(authdevs))

                if devlist == None:
                    self._latest_error = "Can't find authorized devices for user {0}".format(execusername)
                    return
            elif deviceids == None and authdeviceids != None:
                devlist = authdeviceids
            else:
                self._latest_error = "Can't find authorized devices for user {0}".format(execusername)
                return
            
            reportdocs = self.__default_aggregate_report(startdate, enddate, role, devlist)

        if reportdocs:
            print('Printing report from {0} to {1}'.format(startdate.strftime("%d-%m-%Y"), enddate.strftime("%d-%m-%Y")))
            print('Device ID \t Day \t\t Average \t Minimum \tMaximum')
            for doc in reportdocs:
                print('{0} \t\t {1} \t {2} \t\t {3} \t\t {4}'.format(doc['deviceid'], self.__formatdate(doc['day']), round(doc['Average']), round(doc['Minimum']), round(doc['Maximum'])))

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
            return False
      
        if role == 'ADMIN':
            return True
        else:
            return False

    # The method isvaliddeviceinsert is used to perform whether an user is authorized to insert device data
    def isvalidinsert(self, username, userrole, deviceid, access, operation):
        self._latest_error = ''

        if username == None or userrole == None or deviceid == None or access == None or operation == None:
            self._latest_error = "One or more parameters can't be blank"
            return False

        if Utils.truncateandcapitalize(userrole) == 'ADMIN':
           return True
        
        useraccess = UserAccessModel().get_user_access(username, deviceid, username)
       
        if useraccess == None:
            self._latest_error = "The User {0} do not have access to the device {1} to {2} ".format(username, deviceid, operation)
            return False
        elif Utils.truncateandcapitalize(useraccess) != access:
            self._latest_error = "The User {0} do not have appropriate access to the device {1} to {2} ".format(username, deviceid, operation)
            return False
        else:
            return True

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
    def get_authorized_deviceids(self, username, execusername):
        useraccess = UserAccessModel()
        return useraccess.find_authorized_deviceids_by_username(username, execusername)
    
    # The method print_error is used to print error messages if any
    @staticmethod
    def print_error(errormessage):
        if errormessage != None and len(errormessage)>0:
            print("Error: {0}".format(errormessage))
