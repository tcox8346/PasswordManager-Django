from django.test import TestCase
import requests
from .views import redirect
# Create your tests here.

TESTSTATUES = {0:"In progress", 1:"Failed", 2:"Success"}
#Test HomePage View
class TestSystemHomeView(TestCase):
    def __init__(self, methodName: str = "runHomeviewTest"):
        self.name = 'TestSystemHomeView'
        self.test_statues = TESTSTATUES[0]
        self.homeurl = '127.0.0.1'
        self.homeurl_response = 0
        
        # Create a webpage page request
        self.homeurl_response = requests.get(self.homeurl).status_code
       
        
        # Determine if request response is not 200
        if self.homeurl_response != 200:
            #set test to fail
            self.test_statues = TESTSTATUES[1]
            
        else:
            # if not set test to success
            self.test_statues = TESTSTATUES[2]
        # print and return test statues
        print(f'Testing of {self.name} resulted in : {self.test_statues}')
        return
#Test User Creation
class TestSystemUserCreation(TestCase):
     def __init__(self, methodName: str = "runUserCreationTest"):
     
        self.name = 'TestSystemUserCreation'
        self.test_statues_formurl = TESTSTATUES[0]
        self.test_statues_formurl_submission = TESTSTATUES[0]
        self.user_creation_url_lazy = 'signup'
        self.user_creation_url_response = 0
        
        # Create a webpage page request
        self.user_creation_page = requests.get(self.user_creation_url)
        self.homeurl_response = self.user_creation_page.status_code
       
        
        # Determine if request response is not 200
        if self.homeurl_response != 200:
            #set test to fail
            self.test_statues_formurl = TESTSTATUES[1]
        
            
        else:
            # if not set test to success and continue operations
            self.test_statues = TESTSTATUES[2]
            
            #load page form with test data - username: TestUSER_001, email:ThisisaTestemail@email.co
            self.client.post()
            
            # Test 
            
        # print and return test statues
        print(f'Testing of {self.name} resulted in : {self.test_statues}')
        return

# User Authentication
class TestSystemAuthenticationView(TestCase):
     def __init__(self, methodName: str = "runSystemAuthenticationTest"):
        self.name = 'TestSystemHomeView'
        self.test_statues = TESTSTATUES[0]
        self.homeurl = '127.0.0.1'
        self.homeurl_response = 0
        
        # Create a webpage page request
        self.homeurl_response = requests.get(self.homeurl).status_code
       
        
        # Determine if request response is not 200
        if self.homeurl_response != 200:
            #set test to fail
            self.test_statues = TESTSTATUES[1]
            
        else:
            # if not set test to success
            self.test_statues = TESTSTATUES[2]
        # print and return test statues
        print(f'Testing of {self.name} resulted in : {self.test_statues}')
        return

# Test Authenticated HomePage View
class TestSystemAuthenticatedHomeView(TestCase):
     def __init__(self, methodName: str = "runAuthenticatedHomeViewTest"):
        self.name = 'TestSystemHomeView'
        self.test_statues = TESTSTATUES[0]
        self.homeurl = '127.0.0.1'
        self.homeurl_response = 0
        
        # Create a webpage page request
        self.homeurl_response = requests.get(self.homeurl).status_code
       
        
        # Determine if request response is not 200
        if self.homeurl_response != 200:
            #set test to fail
            self.test_statues = TESTSTATUES[1]
            
        else:
            # if not set test to success
            self.test_statues = TESTSTATUES[2]
        # print and return test statues
        print(f'Testing of {self.name} resulted in : {self.test_statues}')
        return

#Test Established Navigational Links
class TestSystemLinks(TestCase):
     def __init__(self, methodName: str = "runHomeLinksTest"):
        self.name = 'TestSystemHomeView'
        self.test_statues = TESTSTATUES[0]
        self.homeurl = '127.0.0.1'
        self.homeurl_response = 0
        
        # Create a webpage page request
        self.homeurl_response = requests.get(self.homeurl).status_code
       
        
        # Determine if request response is not 200
        if self.homeurl_response != 200:
            #set test to fail
            self.test_statues = TESTSTATUES[1]
            
        else:
            # if not set test to success
            self.test_statues = TESTSTATUES[2]
        # print and return test statues
        print(f'Testing of {self.name} resulted in : {self.test_statues}')
        return

#Test profile Generation
class TestProfileCreation(TestCase):
    def __init__(self, methodName: str = "runProfileCreationTest"):
        pass

class TestFriendRequest(TestCase):
    def __init__(self, methodName: str = "runFriendRequestTest"):
        pass
    
class TestFriendRequestAcceptance(TestCase):
    def __init__(self, methodName: str = "runFriendRequestAcceptanceTest"):
        pass