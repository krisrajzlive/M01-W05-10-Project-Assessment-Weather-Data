from model import UserModel, UserAccessModel, DeviceModel, WeatherDataModel,AppArgument, DailyReportsModel, Utils
import datetime
from datetime import datetime
import sys

"""
Assumption #1: pass existing username via commandline and hence no need to validate the login user exists
Assumption #2: login user credentials have been validated outside the application
How to run the application: 'python main.py admin' (without quotes) to run the application as admin user, 'python main.py user_1' (without quotes) to run the application as user_1
"""

appArgument = AppArgument(sys.argv)

print('Hi! ', appArgument.username)

util = Utils()

# Problem 1a. determine user role before performing any operation
userrole = util.get_userrole(appArgument.username, appArgument.username)
print('User Role: ', userrole)

#inserting user - only admins can
#try:
user = UserModel()

# only admin user should be able to access
userdoc1 = user.getuser_by_username('user_1',appArgument.username)
if userdoc1:
    print('getuser_by_username called successfully')
else:
    Utils.print_error(user.latest_error)

# default user can't access the method
userdoc2 = user.getuser_by_username('user_2','user_1')
if userdoc2 == None:
    Utils.print_error(user.latest_error)

# if you run the application admin and if the user does not exist already, this should go
user.insert('raj', 'krisrajz@gmail.com', 'default', appArgument.username)
print('inserting raj firsttime')
util.print_error(user.latest_error)
# Trying to insert an existing user name - should throw error message
user.insert('raj', 'krisrajz@gmail.com', 'default', appArgument.username)
util.print_error(user.latest_error)
# A default user user_1 is trying to insert user - should throw error message
user.insert('raj1','krisrajz@gmail.com','default','user_1')
util.print_error(user.latest_error)
print('Inserted user successfully')
#except:
    #print(sys.exc_info()[1])

#inserting useraccess - only admins can
try:
    useraccess = UserAccessModel()
    print('inserting useraccess user_1 dt003 r')
    useraccess.insert('user_1', 'DT003', 'r', userrole)
    print('inserting useraccess user_2 DH002 rw')
    useraccess.insert('user_2', 'DH002', 'rw', userrole)
    print('Inserted user access successfully')
except:
    print(sys.exc_info()[1])

#inserting device
try:
    device = DeviceModel()
    #admin
    #device.insert('DT001', 'Temperature Sensor', 'Temperature', 'Acme', appArgument.username)
    #user without rights
    #device.insert('DT001', 'Temperature Sensor', 'Temperature', 'Acme', 'user_1')
    #user with rights
    print('inserting device DH002 Humidity Sensor Humidity Krab user_2')
    device.insert('DH002', 'Humidity Sensor', 'Humidity', 'Krab', 'user_2')
    print('Inserted device successfully')
except:
    print(sys.exc_info()[1])

#inserting weather data both admin and default users can perform
try:
    weather = WeatherDataModel()
    #admin
    #weather.insert('DEV01',41,datetime.datetime.now,appArgument.username)
    #default user
    weather.insert('DH002',41,datetime.now(),'user_2')
    weather.insert('DH001',41,datetime.now(),'user_1')
    print('Inserted weather data successfully')
except:
    print(sys.exc_info()[1])

#aggregate report
dailyreport = DailyReportsModel()
startDate = datetime.strptime("20/12/01 01:00:00", "%y/%m/%d %H:%M:%S") # date should be in YY/MM/DD format
endDate = datetime.strptime("20/12/03 23:59:59", "%y/%m/%d %H:%M:%S")

#run report for all the devices
dailyreport.print_aggregate_report(startDate, endDate, appArgument.username)

#run report for specific devices
deviceids = ["DH001","DH002","DT001","DT002"]
dailyreport.print_aggregate_report(startDate, endDate, appArgument.username, userrole, deviceids)


"""2

useraccesstype = useraccess.get_user_access('user_1', 'DT003')
print('User access type: ', useraccesstype)

deviceid = "DT001"
startDate = datetime.strptime("20/12/01 01:00:00", "%y/%m/%d %H:%M:%S")
endDate = datetime.strptime("20/12/03 23:59:59", "%y/%m/%d %H:%M:%S")

print('start date ', startDate)
print('end date ', endDate)

dailyreportmodel = DailyReportsModel()
#
#for doc in dailyreportmodel.aggregate_report(deviceid, startDate, endDate):
#    print(doc)

# Shows how to initiate and search in the users collection based on a username
user_coll = UserModel()
user_document = user_coll.getuser_by_username(appArgument.username, 'default')
print('Login user role by username', user_coll.get_userrole_by_username(appArgument.username));
print('Login user role by document:', user_coll.get_userrole_by_userdocument(user_document))

user_document = user_coll.getuser_by_username('admin', 'admin')
if user_document:
    print(user_document)

# Shows a successful attempt on how to insert a user
user_document = user_coll.insert('test_3', 'test_3@example.com', 'default', userrole)
if user_document == -1:
    print(user_coll.latest_error)
else:
    print(user_document)

# Shows how to initiate and search in the devices collection based on a device id
device_coll = DeviceModel()
device_document = device_coll.find_by_device_id('DT002', 'admin')

if device_document:
    print(device_document)

# Shows a successful attempt on how to insert a new device
device_document = device_coll.insert('DT201', 'Temperature Sensor', 'Temperature', 'Acme', userrole)
if device_document == -1:
    print(device_coll.latest_error)
else:
    print(device_document)

# Shows how to initiate and search in the weather_data collection based on a device_id and timestamp
wdata_coll = WeatherDataModel()
wdata_document = wdata_coll.find_by_device_id_and_timestamp('DT002', datetime(2020, 12, 2, 13, 30, 0), userrole)
if wdata_document:
    print(wdata_document)

# Shows a failed attempt on how to insert a new data point
wdata_document = wdata_coll.insert('DT002', 12, datetime(2020, 12, 2, 13, 30, 0), userrole)
if wdata_document == -1:
    print(wdata_coll.latest_error)
else:
    print(wdata_document)
"""