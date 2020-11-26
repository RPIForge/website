from django.apps import AppConfig


class ForgeConfig(AppConfig):
    # ! function: home app that handles general site configuration and 
    # !           houses generic templates. also handles home pages

    name = 'forge'
    
    
class MachineUsageConfig(AppConfig):
    # ! function: App that handles any machine usage function
    # !           or view
    name = 'machine_usage'

class MachineManagementConfig(AppConfig):
    # ! function: App that handles all of the machine 
    # !           funcions or views. Also houses the model information for
    # !           all machines
    name = 'machine_management'

class MyForgeConfig(AppConfig):
    # ! function: App that handles all of the myforge elements
    name = 'myforge'

class UserManagementConfig(AppConfig):
    # ! function: App that handles all user functions and data storage
    name = 'user_management'

class APIConfig(AppConfig):
    # ! function: App that handles all interactions with non user requests
    name = 'apis'
    
class BusinessConfig(AppConfig):
    name = 'business'