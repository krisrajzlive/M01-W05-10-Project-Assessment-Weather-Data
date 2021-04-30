from model import UserModel, UserAccessModel, DeviceModel, WeatherDataModel,AppArgument, DailyReportsModel, Utils
import datetime
from datetime import datetime
import sys

"""
Assumption #1: pass existing username via commandline and hence no need to validate the login user exists
Assumption #2: login user credentials have been validated outside the application
How to run the application: 'python main.py admin' (without quotes) to run the application as admin user, 'python main.py user_1' (without quotes) to run the application as user_1
ADMIN Role: Are allowed to perform anything
DEFAULT Role: Are allowed to perform inserting device and weather data if they have access to, can also run reports for the devices they have access to
"""

appArgument = AppArgument(sys.argv)

print('Hi! ', appArgument.username)

util = Utils()

# Problem 1. access devices based on user access

userrole = util.get_userrole(appArgument.username, appArgument.username)
print('User Role: ', userrole)

# begin usermodel --------------------------------------------------------------------------------------------------------------------------
user = UserModel()
 
# only admin user should be able to access the method getuser_by_username
userdoc1 = user.getuser_by_username('user_1',appArgument.username)
if userdoc1:
    print('Got user_1 details successfully')
else:
    Utils.print_error(user.latest_error)

# default user can't access the method
userdoc2 = user.getuser_by_username('user_2','user_1')
if userdoc2:
    print('Got user_2 details successfully')
else:
    Utils.print_error(user.latest_error)

# only admin user should be able to access the method get_userrole_by_username
userrole1 = user.get_userrole_by_username('user_1',appArgument.username)
if userrole1:
    print('User_1s role is {0}'.format(userrole1))
else:
    Utils.print_error(user.latest_error)

userrole2 = user.get_userrole_by_username('user_1','user_2')
if userrole2:
    print('User_1s role is {0}'.format(userrole2))
else:
    Utils.print_error(user.latest_error)

# only admin user should be able to access the method insert
# inserting a new user
user.username = 'raj'
user.emailid = 'krisrajz@gmail.com'
user.role = 'default'

inserteduser1 = user.insert(user.username, user.emailid, user.role, appArgument.username)
if inserteduser1:
    print('inserted user {0} successfully'.format(user.username))
else:
    Utils.print_error(user.latest_error)

# Trying to insert the same user again should throw error message
user.username = 'raj'
user.emailid = 'krisrajz@gmail.com'
user.role = 'default'

inserteduser2 = user.insert(user.username, user.emailid, user.role, appArgument.username)
if inserteduser2:
    print('inserted user {0} successfully'.format(user.username))
else:
    Utils.print_error(user.latest_error)

# A default user user_1 is trying to insert user - should throw error message
user.username = 'krisraj'
user.emailid = 'krisrajz@gmail.com'
user.role = 'default'

inserteduser3 = user.insert(user.username, user.emailid, user.role, 'user_1')
if inserteduser3:
    print('inserted user {0} successfully'.format(user.username))
else:
    Utils.print_error(user.latest_error)

# end usermodel --------------------------------------------------------------------------------------------------------------------------------

# begin useraccess -----------------------------------------------------------------------------------------------------------------------------

#inserting useraccess - only admins can

useraccess = UserAccessModel()

useraccess.username = 'raj'
useraccess.device_id = 'DT003'
useraccess.access = "rw"

useraccess1 = useraccess.insert(useraccess.username, useraccess.device_id, useraccess.access, appArgument.username)
if useraccess1:
    print('Successfully created useraccess for user {0}'.format(useraccess.username))
else:
    Utils.print_error(useraccess.latest_error)

# insert duplicate
useraccess.username = 'raj'
useraccess.device_id = 'DT003'
useraccess.access = "rw"

useraccess2 = useraccess.insert(useraccess.username, useraccess.device_id, useraccess.access, appArgument.username)
if useraccess2:
    print('inserting useraccess user_2 DH002 rw')
else:
    Utils.print_error(useraccess.latest_error)

# end useraccess -------------------------------------------------------------------------------------------------------------------------------

# begin device ---------------------------------------------------------------------------------------------------------------------------------

#inserting device

    device = DeviceModel()

    device.device_id = 'DT0010'
    device.desc = 'Temperature Sensor'
    device.manufacturer = 'Acme'
    device.type = 'Temperature'

    device.insert(device.device_id, device.desc, device.type, device.manufacturer, appArgument.username)

    if len(device.latest_error) == 0:
        print('created new device {0}'.format(device.device_id))
    Utils.print_error(device.latest_error)

    device.device_id = 'DT001'
    device.desc = 'Temperature Sensor'
    device.manufacturer = 'Acme'
    device.type = 'Temperature'

    #default user inserting duplicate device
    device.insert(device.device_id, device.desc, device.type, device.manufacturer, appArgument.username)

    if len(device.latest_error) == 0:
        print('created new device {0}'.format(device.device_id))
    Utils.print_error(device.latest_error)
    
    device.device_id = 'DH004'
    device.desc = 'Humidity Sensor'
    device.manufacturer = 'Krab'
    device.type = 'Humidity'

    device.insert(device.device_id, device.desc, device.type, device.manufacturer, 'user_2')

    if len(device.latest_error) == 0:
        print('created new device {0}'.format(device.device_id))
    Utils.print_error(device.latest_error)

# end device ----------------------------------------------------------------------------------------------------------------------------------

# begin weather data --------------------------------------------------------------------------------------------------------------------------

    weather = WeatherDataModel()

    weather.device_id = 'DH0011'
    weather.value = 39
    weather.timestamp = datetime.now()

    #weather.insert('DEV01',41,datetime.datetime.now,appArgument.username)
    weather.insert(weather.device_id, weather.value, weather.timestamp, appArgument.username)
    
    if len(weather.latest_error) == 0:
        print('inserted weather data for device {0}'.format(weather.device_id))
    
    Utils.print_error(weather.latest_error)
    
    # inserting duplicate
    weather.insert(weather.device_id, weather.value, weather.timestamp, appArgument.username)
    
    if len(weather.latest_error) == 0:
        print('inserted weather data for device {0}'.format(weather.device_id))
    
    Utils.print_error(weather.latest_error)

    #default user with access rights
    weather.device_id = 'DH002'
    weather.value = 39
    weather.timestamp = datetime.now()
    weather.insert(weather.device_id, weather.value, weather.timestamp, 'user_2')
    
    if len(weather.latest_error) == 0:
        print('inserted weather data for device {0}'.format(weather.device_id))
    
    Utils.print_error(weather.latest_error)

    #default user without access rights
    weather.insert(weather.device_id, weather.value, weather.timestamp, 'user_1')
    
    if len(weather.latest_error) == 0:
        print('inserted weather data for device {0}'.format(weather.device_id))
    
    Utils.print_error(weather.latest_error)


# end weather data ----------------------------------------------------------------------------------------------------------------------------

#Problem #2: Aggregate Report : begins ------------------------------------------------------------------------------------------------------------------------

dailyreport = DailyReportsModel()
startDate = datetime.strptime("20/12/01 01:00:00", "%y/%m/%d %H:%M:%S") # date should be in YY/MM/DD format
endDate = datetime.strptime("20/12/03 23:59:59", "%y/%m/%d %H:%M:%S")

#run report for all the devices for the login user
dailyreport.print_aggregate_report(startDate, endDate, appArgument.username)
Utils.print_error(dailyreport.latest_error)

#run report for specific devices and the reports runs only for authorized devices
deviceids = ["DH001","DH002","DT002","DT003"]
dailyreport.print_aggregate_report(startDate, endDate, appArgument.username, deviceids)
Utils.print_error(dailyreport.latest_error)

#non-existent user
dailyreport.print_aggregate_report(startDate,endDate, 'john')
Utils.print_error(dailyreport.latest_error)

#aggregate report ends -------------------------------------------------------------------------------------------------------------------------