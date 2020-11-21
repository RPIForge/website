from django.apps import AppConfig


class ForgeConfig(AppConfig):
    name = 'forge'
    
    
class MachineUsageConfig(AppConfig):
    name = 'machine_usage'

class MachineManagementConfig(AppConfig):
    name = 'machine_management'

class MyForgeConfig(AppConfig):
    name = 'myforge'

class UserManagementConfig(AppConfig):
    name = 'user_management'

class APIConfig(AppConfig):
    name = 'apis'
    
class BusinessConfig(AppConfig):
    name = 'business'